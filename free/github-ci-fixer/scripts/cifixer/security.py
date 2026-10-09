"""Bounded text ingestion and conservative, best-effort secret redaction."""

import os
import re
import stat
from pathlib import Path

MAX_BYTES = 8_000_000
MAX_LINE = 16_000
# Some GitHub logs spell ESC as the printable caret sequence ^[.
ANSI = re.compile(r"(?:\x1b|\^\[)\[[0-?]*[ -/]*[@-~]")
SECRET_PATTERNS = (
    re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]{12,}|github_pat_[A-Za-z0-9_]{12,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{16,})\b"
    ),
    re.compile(r"(?i)(?:bearer|basic)\s+[A-Za-z0-9+/_.=-]+"),
    re.compile(
        r"(?i)\b[\w.-]*(?:token|password|passwd|secret|api[_-]?key|credential)[\w.-]*\s*[:=]\s*[^\s,;]+"
    ),
    re.compile(r"https?://[^\s/@]+:[^\s/@]+@"),
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----.*?(?:-----END [^-]*PRIVATE KEY-----|\Z)", re.S),
    re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
)


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    text = ANSI.sub("", text)
    return "".join(c for c in text if c in "\n\t" or ord(c) >= 32 and ord(c) != 127)


def read_text(path: Path) -> str:
    """Reject special files, symlinks, oversized or binary inputs before analysis."""
    if path.is_symlink():
        raise ValueError("Symlink inputs are not accepted")
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("Input must be a regular file")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("Input is not a regular file or exceeds 8 MB")
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Input exceeds 8 MB")
    if b"\0" in data:
        raise ValueError("Binary input is not supported; provide saved UTF-8 text logs")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Input must be UTF-8 text") from exc


def contained_file(root: Path, relative: str) -> Path:
    candidate = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Unsafe relative path")
    if candidate.is_symlink() or not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("Path escapes repository or uses a symlink")
    return candidate
