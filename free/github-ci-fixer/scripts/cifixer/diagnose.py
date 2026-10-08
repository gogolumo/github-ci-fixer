"""Evidence extraction and cautious ordering; no inferred numerical certainty."""

from .ingest import ingest
from .rules import COMPILED, EXIT, WARNING

LIMITATIONS = [
    "Signatures identify observed errors, not proof of a unique root cause.",
    "Text logs may omit earlier failures; first observed error need not be first actual error.",
    "Secret redaction is best effort; review reports before sharing.",
    "No code changes or tests have been executed by analysis.",
]


def analyze(text: str, source: str = "saved-log", edition: str = "free") -> dict:
    rows, notes = ingest(text, source)
    findings: list[dict] = []
    warnings: list[dict] = []
    secondary: list[dict] = []
    seen = set()
    for index, row in enumerate(rows):
        message = row["text"]
        if WARNING.search(message) and not message.startswith("##[error]"):
            if len(warnings) < 20:
                warnings.append(row)
            continue
        if EXIT.search(message):
            if len(secondary) < 20:
                secondary.append(row)
            continue
        for rule, pattern in COMPILED:
            if not pattern.search(message):
                continue
            identity = (rule.code, row["job"], row["step"])
            if identity in seen:
                continue
            seen.add(identity)
            evidence = [
                r
                for r in rows[max(0, index - 1) : index + 2]
                if r["job"] == row["job"] and r["step"] == row["step"]
            ]
            findings.append(
                {
                    "id": f"F{len(findings) + 1}",
                    "code": rule.code,
                    "title": rule.title,
                    "job": row["job"],
                    "step": row["step"],
                    "first_line": row["line"],
                    "assessment": "signature-supported",
                    "hypothesis": rule.cause,
                    "evidence": evidence,
                    "recommendation": rule.recommendation,
                    "verification_command_guidance": rule.verify,
                    "verification": {"status": "not-run"},
                }
            )
            break
        if len(findings) >= 100:
            notes.append("Finding limit reached; analysis incomplete")
            break
    if not findings:
        notes.append(
            "Insufficient evidence: no supported error signature; obtain complete failed-step logs and command context"
        )
    if secondary and not findings:
        notes.append("Exit status alone does not explain why the command failed")
    return {
        "schema_version": "1.0",
        "product_version": "1.0.0",
        "edition": edition,
        "context": {},
        "assessment": "signature-supported" if findings else "insufficient",
        "first_meaningful_error": findings[0]["id"] if findings else None,
        "findings": findings,
        "secondary_exit_markers": secondary,
        "warnings": warnings,
        "missing_information": notes,
        "limitations": LIMITATIONS.copy(),
        "verification": {"status": "not-run"},
        "next_actions": [
            "Review evidence and obtain missing context",
            "Approve a minimal proposal before changes",
            "Run appropriate checks before claiming a verified fix",
        ],
    }
