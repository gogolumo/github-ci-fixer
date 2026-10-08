#!/usr/bin/env python3
"""Saved-text analysis. Exit 0 means analysis completed, not CI passed."""

import argparse
import sys
from pathlib import Path

from cifixer.diagnose import analyze
from cifixer.report import markdown
from cifixer.security import read_text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Diagnose saved GitHub Actions UTF-8 text logs offline"
    )
    parser.add_argument("log", type=Path)
    parser.add_argument("--version", action="version", version="GitHub CI Fixer Free 1.0.0")
    args = parser.parse_args(argv)
    try:
        report = analyze(read_text(args.log), args.log.name)
        sys.stdout.write(markdown(report))
        return 0
    except (OSError, ValueError) as exc:
        # Do not print OS exception details containing arbitrary input paths.
        message = (
            str(exc)
            if isinstance(exc, ValueError)
            else "Input could not be read; check regular-file path and permissions"
        )
        print(f"ci-fixer: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
