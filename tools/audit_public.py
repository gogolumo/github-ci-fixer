#!/usr/bin/env python3
"""Audit public distribution boundaries; premium source is never imported."""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "free/github-ci-fixer"
ALLOWED_MODULES = {"__init__", "security", "ingest", "rules", "diagnose", "report"}
SECRET = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b"
)


def main():
    failures = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(
            p in {".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache", "release"}
            for p in relative.parts
        ):
            continue
        if path.is_symlink():
            failures.append(f"Unexpected symlink: {relative}")
        if any(p in {"premium", "github-ci-fixer-pro", "pro"} for p in relative.parts):
            failures.append(f"Premium source path: {relative}")
        if path.is_file():
            if path.suffix == ".zip":
                failures.append(
                    f"Unexpected archive outside excluded release directory: {relative}"
                )
            if path.suffix in {".py", ".md", ".json", ".yml", ".yaml", ".txt", ".log"}:
                if SECRET.search(path.read_text(encoding="utf-8")):
                    failures.append(f"Potential credential: {relative}")
    for path in (PACKAGE / "scripts").rglob("*.py"):
        relative = path.relative_to(PACKAGE / "scripts")
        if relative.as_posix() != "ci_fixer.py" and (
            relative.parent.as_posix() != "cifixer" or path.stem not in ALLOWED_MODULES
        ):
            failures.append(f"Unexpected public runtime module: {relative}")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ]
        imports += [
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        ]
        if any(
            name.split(".")[0] in {"pro", "requests", "urllib", "subprocess", "socket"}
            for name in imports
        ):
            failures.append(
                f"Network, execution or premium dependency in public runtime: {relative}"
            )
    print(
        json.dumps(
            {"public_boundary": "failed" if failures else "passed", "failures": failures}, indent=2
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
