#!/usr/bin/env python3
"""Deterministic package builder and hostile-archive validator.

Archive code runs only with an explicit caller-approved SHA-256 digest.
"""

import argparse
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

MAX_SIZE = 50_000_000
FORBIDDEN = {".git", ".env", ".venv", "__pycache__", "__MACOSX", ".DS_Store", "node_modules"}
SUFFIXES = {".py", ".md", ".txt", ".json", ".log", ".yaml", ".yml"}
LAYOUTS = ("skill-folder", "flat")
DEVICE = re.compile(r"(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?\Z", re.I)
SECRET = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|-----BEGIN [^-]*PRIVATE KEY-----"
)


def metadata(text: str) -> dict:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("Missing SKILL.md YAML frontmatter")
    if not text[match.end() :].strip():
        raise ValueError("SKILL.md must contain a nonempty instruction body")
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
        if value.startswith('"'):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid quoted YAML scalar") from exc
            if not isinstance(parsed, str):
                raise ValueError("Metadata values must be strings")
        elif value.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                raise ValueError("Invalid quoted YAML scalar")
            parsed = value[1:-1].replace("''", "'")
        else:
            if (
                not value
                or value[0] in "|>-?:,@`{}[]&*!#%"
                or ": " in value
                or any(c in value for c in "\n#")
                or value.lower() in {"null", "~", "true", "false", "yes", "no", "on", "off"}
                or re.match(r"[+-]?(?:\d|\.\d)", value)
            ):
                raise ValueError("Unsupported YAML scalar; use a quoted string")
            parsed = value
        if any(ord(c) < 32 for c in parsed):
            raise ValueError("Control characters are forbidden in metadata")
        fields[key] = parsed
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("Invalid skill name")
    if not 1 <= len(fields.get("description", "")) <= 1024:
        raise ValueError("Invalid description")
    if len(fields.get("compatibility", "")) > 500:
        raise ValueError("Compatibility too long")
    return fields


def portable_name(name: str, directory: bool = False) -> None:
    normalized = name[:-1] if directory and name.endswith("/") else name
    parts = PurePosixPath(normalized).parts
    if (
        not parts
        or normalized != PurePosixPath(normalized).as_posix()
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
        or (not directory and PurePosixPath(name).suffix not in SUFFIXES)
    ):
        raise ValueError("Unsafe or nonportable package filename")


def _layout(layout: str) -> None:
    if layout not in LAYOUTS:
        raise ValueError("Unknown archive layout")


def _register_name(
    name: str, directory: bool, components: dict[str, str], kinds: dict[str, bool]
) -> None:
    parts = PurePosixPath(name).parts
    for depth in range(1, len(parts) + 1):
        component = "/".join(parts[:depth])
        folded = unicodedata.normalize("NFC", component).casefold()
        previous = components.setdefault(folded, component)
        if previous != component:
            raise ValueError("Case-insensitive package directory collision")
        is_directory = directory or depth < len(parts)
        if folded in kinds and kinds[folded] != is_directory:
            raise ValueError("Package file and directory paths overlap")
        kinds[folded] = is_directory


def _read_source(path: Path) -> bytes:
    """Bound reads and reject changed files; this is not a hostile filesystem sandbox."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("Package source must be a regular file")
    fd = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
    )
    with os.fdopen(fd, "rb") as source:
        opened = os.fstat(source.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (
            opened.st_dev,
            opened.st_ino,
        ):
            raise ValueError("Package source changed while opening")
        data = source.read(MAX_SIZE + 1)
        after = os.fstat(source.fileno())
    if (
        len(data) >= MAX_SIZE
        or not stat.S_ISREG(opened.st_mode)
        or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns)
        != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    ):
        raise ValueError("Package source changed or exceeds limits")
    return data


def build(root: Path, output: Path, layout: str = "skill-folder") -> str:
    _layout(layout)
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
    components: dict[str, str] = {}
    kinds: dict[str, bool] = {}
    for _, name in files:
        _register_name(name, False, components, kinds)
    if metadata((root / "SKILL.md").read_text(encoding="utf-8"))["name"] != root.name:
        raise ValueError("Skill name must match directory name")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        expanded = 0
        for path, name in files:
            if layout == "skill-folder":
                name = f"{root.name}/{name}"
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3  # Normalize ZIP platform metadata on Windows too.
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            data = _read_source(path)
            expanded += len(data)
            if expanded >= MAX_SIZE:
                raise ValueError("Expanded package exceeds limits")
            archive.writestr(info, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="utf-8"
    )
    return digest


def validate(path: Path, smoke_digest: str | None = None, layout: str = "skill-folder") -> dict:
    _layout(layout)
    if (
        path.is_symlink()
        or not stat.S_ISREG(path.stat().st_mode)
        or path.stat().st_size >= MAX_SIZE
    ):
        raise ValueError("Archive must be a regular file smaller than 50 MB")
    archive_bytes = _read_source(path)
    digest = hashlib.sha256(archive_bytes).hexdigest()
    with (
        zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive,
        tempfile.TemporaryDirectory(prefix="ci-fixer-release-") as temp,
    ):
        members = archive.infolist()
        if len(members) > 1000 or sum(i.file_size for i in members) >= MAX_SIZE:
            raise ValueError("Expanded package exceeds limits")
        names = set()
        folded = set()
        components: dict[str, str] = {}
        kinds: dict[str, bool] = {}
        texts = {}
        manifest = []
        root = Path(temp).resolve()
        for info in members:
            name = info.filename
            parts = PurePosixPath(name).parts
            directory = info.is_dir()
            portable_name(name, directory)
            mode = stat.S_IFMT(info.external_attr >> 16)
            member_name = name.rstrip("/")
            if (
                not name
                or member_name in names
                or member_name.casefold() in folded
                or name.startswith("/")
                or "\\" in name
                or ":" in name
                or any(p in {"..", "."} | FORBIDDEN for p in parts)
                or member_name != PurePosixPath(name).as_posix()
                or mode not in ({0, stat.S_IFDIR} if directory else {0, stat.S_IFREG})
                or info.flag_bits & 1
                or "\0" in info.orig_filename
                or info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
                or (directory and info.file_size)
            ):
                raise ValueError("Unsafe, duplicate or unsupported archive member")
            _register_name(name, directory, components, kinds)
            names.add(member_name)
            folded.add(member_name.casefold())
            if directory:
                continue
            data = archive.read(info)
            if len(data) != info.file_size or b"\0" in data:
                raise ValueError("Invalid package file contents")
            text = data.decode("utf-8")
            if SECRET.search(text):
                raise ValueError("Potential secret in package")
            texts[name] = text
            manifest.append(
                {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            )
            target = root.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if layout == "skill-folder":
            top = {PurePosixPath(name).parts[0] for name in names}
            if len(top) != 1 or any(len(PurePosixPath(name).parts) == 1 for name in texts):
                raise ValueError("Exactly one top-level skill folder is required")
            prefix = next(iter(top))
            skill_root = root / prefix
            skill_file = f"{prefix}/SKILL.md"
            entry_file = f"{prefix}/scripts/ci_fixer.py"
        else:
            prefix = "."
            skill_root = root
            skill_file = "SKILL.md"
            entry_file = "scripts/ci_fixer.py"
        if skill_file not in texts or entry_file not in texts:
            raise ValueError("SKILL.md and runtime entrypoint must be at the skill folder root")
        if sum(PurePosixPath(name).name == "SKILL.md" for name in texts) != 1:
            raise ValueError("Exactly one SKILL.md is required")
        fields = metadata(texts[skill_file])
        if layout == "skill-folder" and fields["name"] != prefix:
            raise ValueError("Skill folder name must match frontmatter name")
        for name, text in texts.items():
            if not name.endswith(".md"):
                continue
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if link.startswith(("https://", "http://", "#")):
                    continue
                link = link.split("#", 1)[0]
                resolved = root.joinpath(*PurePosixPath(name).parent.parts, link).resolve()
                if not resolved.is_relative_to(skill_root) or not resolved.is_file():
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
                [sys.executable, "-E", "-s", str(root / entry_file), str(log)],
                capture_output=True,
                text=True,
                encoding="utf-8",
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
            "bytes": len(archive_bytes),
            "sha256": digest,
            "skill": fields["name"],
            "layout": layout,
            "skill_directory": prefix,
            "files": len(texts),
            "file_manifest": sorted(manifest, key=lambda item: str(item["path"])),
            "structural_validation": "passed",
            "smoke": smoke,
            "ready_for_submission_review": smoke == "passed" and layout == "skill-folder",
            "marketplace_packaging": "locally-validated" if layout == "skill-folder" else "legacy",
            "marketplace_approval": "not-requested",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build")
    make.add_argument("root", type=Path)
    make.add_argument("output", type=Path)
    make.add_argument("--layout", choices=LAYOUTS, default="skill-folder")
    check = sub.add_parser("validate")
    check.add_argument("archive", type=Path)
    check.add_argument("--layout", choices=LAYOUTS, default="skill-folder")
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
            digest = build(args.root, args.output, args.layout)
            report = validate(args.output, digest, args.layout)
        else:
            report = validate(args.archive, args.smoke_approved_sha256, args.layout)
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
