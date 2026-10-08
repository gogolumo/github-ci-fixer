"""Render evidence as inert Markdown text, never raw HTML or executable instructions."""

import html
import json

from .security import redact


def safe(value: object) -> str:
    text = html.escape(redact(str(value)), quote=True)
    for c in "\\`*_{}[]()#+!|~":
        text = text.replace(c, "\\" + c)
    return text


def markdown(report: dict) -> str:
    lines = [
        "# GitHub CI Fixer report",
        "",
        f"Assessment: {safe(report['assessment'])}. Verification: {safe(report['verification']['status'])}.",
        "",
    ]
    if report.get("context"):
        lines += ["## Context", ""]
        for key, value in report["context"].items():
            lines.append(f"- {safe(key)}: {safe(value)}")
        lines.append("")
    lines += [
        f"First meaningful observed error: {safe(report['first_meaningful_error'] or 'none')}",
        "",
        "Later findings are not automatically classified as consequences of the first error.",
        "",
    ]
    for finding in report["findings"]:
        lines += [
            f"## {safe(finding['id'])}: {safe(finding['title'])}",
            "",
            f"Code: {safe(finding['code'])}; job: {safe(finding['job'])}; step: {safe(finding['step'])}.",
            "",
            f"Hypothesis: {safe(finding['hypothesis'])}",
            "",
            "Evidence (untrusted log text):",
            "",
        ]
        for evidence in finding["evidence"]:
            lines.append(
                f"- {safe(evidence['source'])}:{evidence['line']}: {safe(evidence['text'])}"
            )
        lines += [
            "",
            f"Recommendation: {safe(finding['recommendation'])}",
            "",
            f"Verify: {safe(finding['verification_command_guidance'])}",
            "",
            "Status: not-run. This is a recommendation, not a tested repair.",
            "",
        ]
    if report.get("unclassified_errors"):
        lines += [
            "## Unclassified error candidates",
            "",
            "These lines need further investigation; no root cause is inferred.",
            "",
        ]
        for evidence in report["unclassified_errors"]:
            lines.append(
                f"- {safe(evidence['source'])}:{evidence['line']}: {safe(evidence['text'])}"
            )
        lines.append("")
    for title, values in (
        ("Missing information", report["missing_information"]),
        ("Limitations", report["limitations"]),
        ("Next actions", report["next_actions"]),
    ):
        lines += [f"## {title}", ""] + [f"- {safe(v)}" for v in values] + [""]
    lines += [
        f"Unrelated warning candidates: {len(report['warnings'])}.",
        f"Secondary exit markers: {len(report['secondary_exit_markers'])}.",
    ]
    if report.get("groups"):
        lines += ["", "## Related failure groups", ""]
        for group in report["groups"]:
            lines.append(
                f"- {safe(group['code'])}: {safe(', '.join(group['finding_ids']))}. {safe(group['assessment'])}"
            )
    return "\n".join(lines) + "\n"


def json_report(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=True) + "\n"
