# Marketplace format check — 1.0.1

Checked 2026-10-08 against the [Agensi creator guide](https://www.agensi.io/learn/how-to-sell-skills-on-agensi) and [Agent Skills specification](https://agentskills.io/specification). Submission is a ZIP with valid SKILL.md plus supporting scripts/references. Our archives put SKILL.md directly at archive root and are extracted into a directory matching the skill name. Required name and description, optional license, valid UTF-8 and all relative Markdown references are checked. Runtime modules use Python's standard library.

Local validation rejects traversal, absolute paths, Windows device names, case collisions, hidden files, special files, symlinks, unsupported extensions, known credential signatures and oversized expanded archives. Deterministic ordering, timestamps and permissions produce stable hashes. Trusted extraction smoke runs from an unrelated directory; hostile arbitrary uploads require explicit digest approval for execution.

The 50 MB decimal package limit is our conservative policy, not a verified marketplace limit. Creator-dashboard requirements and automated/manual review may introduce additional checks. Terms page fetch timed out; existing licenses remain unchanged. No product listing has been submitted or approved.
