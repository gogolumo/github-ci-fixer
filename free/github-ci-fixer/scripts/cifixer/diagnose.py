"""Evidence extraction and cautious ordering; no inferred numerical certainty."""

import re

from .ingest import ingest
from .rules import COMMAND, COMPILED, EXIT, WARNING

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
    unclassified: list[dict] = []
    seen = set()
    commands: dict[tuple[str, str], dict] = {}
    for index, row in enumerate(rows):
        message = row["text"]
        context_key = (row["job"], row["step"])
        command = COMMAND.match(message)
        if command:
            commands[context_key] = {
                "row": row,
                "command": (command.group(1) or command.group(2)).removeprefix("$ "),
            }
        if WARNING.search(message) and not message.startswith("##[error]"):
            if len(warnings) < 20:
                warnings.append(row)
            continue
        if EXIT.search(message):
            commands.pop(context_key, None)
            if len(secondary) < 20:
                secondary.append(row)
            continue
        matched = False
        for rule, pattern in COMPILED:
            if not pattern.search(message):
                continue
            command_context = commands.get(context_key)
            if rule.command_pattern and (
                command_context is None
                or not re.search(rule.command_pattern, command_context["command"])
            ):
                continue
            following = [
                r
                for r in rows[index + 1 : index + 4]
                if r["job"] == row["job"] and r["step"] == row["step"]
            ]
            if any(
                not any(re.search(required, r["text"]) for r in following)
                for required in rule.following_patterns
            ):
                continue
            matched = True
            identity = (rule.code, row["job"], row["step"])
            if identity in seen:
                continue
            seen.add(identity)
            evidence = [
                r
                for r in rows[max(0, index - 1) : index + (4 if rule.following_patterns else 2)]
                if r["job"] == row["job"] and r["step"] == row["step"]
            ]
            if rule.command_pattern and command_context is not None:
                command_row = command_context["row"]
                if command_row not in evidence:
                    evidence.insert(0, command_row)
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
        if (
            not matched
            and re.search(r"(?i)\b(?:error|fatal|failed|failure)\b", message)
            and len(unclassified) < 20
        ):
            unclassified.append(row)
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
        "product_version": "1.0.1",
        "edition": edition,
        "context": {},
        "assessment": "signature-supported" if findings else "insufficient",
        "first_meaningful_error": findings[0]["id"] if findings else None,
        "findings": findings,
        "unclassified_errors": unclassified,
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
