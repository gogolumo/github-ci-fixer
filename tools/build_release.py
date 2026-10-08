#!/usr/bin/env python3
"""Deterministic package builder and hostile-archive validator.

Archive code runs only with an explicit caller-approved SHA-256 digest.
"""

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

MAX_SIZE = 50_000_000
FORBIDDEN = {".git", ".env", ".venv", "__pycache__", "__MACOSX", ".DS_Store", "node_modules"}
SUFFIXES = {".py", ".md", ".txt", ".json", ".log", ".yaml", ".yml"}
DEVICE = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.I)
SECRET = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|-----BEGIN [^-]*PRIVATE KEY-----"
)


def metadata(text: str) -> dict:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("Missing SKILL.md YAML frontmatter")
    # This deliberately validates the shipped flat scalar subset, not arbitrary YAML.
    fields = {}
    for line in match[1].splitlines():
        if not line or line.startswith("#"):
            continue
        if ": " not in line or line[0].isspace():
            raise ValueError("Frontmatter must use the supported flat scalar subset")
        key, value = line.split(": ", 1)
        if key in fields or key not in {"name", "description", "license", "compatibility"}:
            raise ValueError("Duplicate or unsupported metadata field")
        if any(c in value for c in "\n{}[]&*!#") or value.startswith(("|", ">")):
            raise ValueError("Unsupported YAML scalar")
        fields[key] = value.strip("\"'")
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("Invalid skill name")
    if not 1 <= len(fields.get("description", "")) <= 1024:
        raise ValueError("Invalid description")
    if len(fields.get("compatibility", "")) > 500:
        raise ValueError("Compatibility too long")
    return fields


def portable_name(name: str) -> None:
    parts = PurePosixPath(name).parts
    if (
        not parts
        or name != PurePosixPath(name).as_posix()
        or name.startswith("/")
        or "\\" in name
        or any(
            p.startswith(".")
            or p.endswith((".", " "))
            or DEVICE.fullmatch(p)
            or any(ord(c) < 32 or c in '<>:"|?*' for c in p)
            for p in parts
        )
        or any(p in FORBIDDEN for p in parts)
        or PurePosixPath(name).suffix not in SUFFIXES
    ):
        raise ValueError("Unsafe or nonportable package filename")


def build(root: Path, output: Path) -> str:
    if root.is_symlink():
        raise ValueError("Package root cannot be a symlink")
    files = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in FORBIDDEN for part in relative.parts) or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError("Package symlinks are forbidden")
        if not path.is_dir() and not stat.S_ISREG(path.stat().st_mode):
            raise ValueError("Package contains a special file")
        if path.is_file():
            if path.suffix not in SUFFIXES or path.stat().st_size > MAX_SIZE:
                raise ValueError("Unsupported or oversized package file")
            portable_name(relative.as_posix())
            files.append((path, relative.as_posix()))
    if len(files) > 1000 or sum(p.stat().st_size for p, _ in files) >= MAX_SIZE:
        raise ValueError("Expanded package exceeds limits")
    if len({n.casefold() for _, n in files}) != len(files):
        raise ValueError("Case-insensitive package filename collision")
    if metadata((root / "SKILL.md").read_text(encoding="utf-8"))["name"] != root.name:
        raise ValueError("Skill name must match directory name")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, name in files:
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3  # Normalize ZIP platform metadata on Windows too.
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            with path.open("rb") as source:
                data = source.read(MAX_SIZE + 1)
            if len(data) >= MAX_SIZE:
                raise ValueError("Package file grew beyond limits")
            archive.writestr(info, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return digest


def validate(path: Path, smoke_digest: str | None = None) -> dict:
    if (
        path.is_symlink()
        or not stat.S_ISREG(path.stat().st_mode)
        or path.stat().st_size >= MAX_SIZE
    ):
        raise ValueError("Archive must be a regular file smaller than 50 MB")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with (
        zipfile.ZipFile(path) as archive,
        tempfile.TemporaryDirectory(prefix="ci-fixer-release-") as temp,
    ):
        members = archive.infolist()
        if len(members) > 1000 or sum(i.file_size for i in members) >= MAX_SIZE:
            raise ValueError("Expanded package exceeds limits")
        names = set()
        folded = set()
        texts = {}
        root = Path(temp).resolve()
        for info in members:
            name = info.filename
            parts = PurePosixPath(name).parts
            portable_name(name)
            mode = stat.S_IFMT(info.external_attr >> 16)
            if (
                not name
                or info.is_dir()
                or name in names
                or name.casefold() in folded
                or name.startswith("/")
                or "\\" in name
                or ":" in name
                or any(p in {"..", "."} | FORBIDDEN for p in parts)
                or name != PurePosixPath(name).as_posix()
                or mode not in {0, stat.S_IFREG}
                or PurePosixPath(name).suffix not in SUFFIXES
            ):
                raise ValueError("Unsafe, duplicate or unsupported archive member")
            names.add(name)
            folded.add(name.casefold())
            data = archive.read(info)
            text = data.decode("utf-8")
            if SECRET.search(text):
                raise ValueError("Potential secret in package")
            texts[name] = text
            target = root.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if "SKILL.md" not in names or "scripts/ci_fixer.py" not in names:
            raise ValueError("Root SKILL.md and runtime entrypoint required")
        fields = metadata(texts["SKILL.md"])
        for name, text in texts.items():
            if not name.endswith(".md"):
                continue
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if link.startswith(("https://", "http://", "#")):
                    continue
                link = link.split("#", 1)[0]
                resolved = root.joinpath(*PurePosixPath(name).parent.parts, link).resolve()
                if not resolved.is_relative_to(root) or not resolved.is_file():
                    raise ValueError(f"Broken or unsafe relative reference in {name}")
        smoke = "not-run"
        if smoke_digest is not None:
            if smoke_digest != digest:
                raise ValueError("Smoke approval digest does not match archive")
            # The caller approves executing this exact archive, not all arbitrary uploads.
            log = root / "smoke.log"
            log.write_text(
                "ModuleNotFoundError: No module named 'example_dependency'\n", encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, str(root / "scripts/ci_fixer.py"), str(log)],
                capture_output=True,
                text=True,
                timeout=20,
                shell=False,
                cwd=Path(temp).parent,
            )
            if (
                result.returncode
                or "Python import failed" not in result.stdout
                or "not-run" not in result.stdout
            ):
                raise ValueError("Extracted package smoke test failed")
            smoke = "passed"
        return {
            "archive": path.name,
            "bytes": path.stat().st_size,
            "sha256": digest,
            "skill": fields["name"],
            "files": len(names),
            "structural_validation": "passed",
            "smoke": smoke,
            "ready_for_submission_review": smoke == "passed",
            "marketplace_approval": "not-requested",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build")
    make.add_argument("root", type=Path)
    make.add_argument("output", type=Path)
    check = sub.add_parser("validate")
    check.add_argument("archive", type=Path)
    check.add_argument(
        "--smoke-approved-sha256", help="Approve local execution of this exact trusted package"
    )
    meta = sub.add_parser("metadata")
    meta.add_argument("skill", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "metadata":
            report = metadata(args.skill.read_text(encoding="utf-8"))
        elif args.command == "build":
            digest = build(args.root, args.output)
            report = validate(args.output, digest)
        else:
            report = validate(args.archive, args.smoke_approved_sha256)
        print(json.dumps(report, indent=2))
        return 0
    except (
        OSError,
        ValueError,
        UnicodeError,
        zipfile.BadZipFile,
        subprocess.SubprocessError,
    ) as exc:
        print(f"Release validation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
