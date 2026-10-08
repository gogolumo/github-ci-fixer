"""Preserve physical line references and gh job/step prefixes."""

import io
import re

from .security import MAX_BYTES, MAX_LINE, redact

STAMP = re.compile(r"^\d{4}-\d\d-\d\dT[0-9:.]+Z\s*")


def ingest(text: str, source: str) -> tuple[list[dict], list[str]]:
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Input exceeds 8 MB")
    if "\0" in text:
        raise ValueError("Binary input is not supported")
    notes = []
    rows = []
    # Redact the whole document first to cover multiline keys.
    # Replacement preserves line count so evidence still points at input lines.
    from .security import SECRET_PATTERNS

    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: "[REDACTED]" + "\n" * m.group().count("\n"), text)
    for number, raw in enumerate(io.StringIO(text), 1):
        if number > 50_000:
            notes.append("Input exceeds 50000 lines; analysis incomplete")
            break
        raw = raw.rstrip("\r\n")
        if len(raw) > MAX_LINE:
            notes.append(f"Line {number} exceeds 16000 characters; evidence incomplete")
            raw = raw[:MAX_LINE]
        clean = redact(raw)
        pieces = clean.split("\t", 2)
        job, step, message = pieces if len(pieces) == 3 else ("saved-log", "unknown", clean)
        message = STAMP.sub("", message)
        rows.append(
            {"source": redact(source), "line": number, "job": job, "step": step, "text": message}
        )
    if not rows:
        notes.append("No log lines supplied")
    if text.rstrip().endswith(("...", "[truncated]")):
        notes.append("Log explicitly indicates truncation")
    return rows, list(dict.fromkeys(notes))
