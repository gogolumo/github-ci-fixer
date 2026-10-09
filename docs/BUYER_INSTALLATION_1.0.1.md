# Buyer installation and host QA — 1.0.1

Final gate date: 2026-10-09. Install the complete skill folder, including its scripts,
references, examples and license files. Extract the release ZIP into a parent directory;
it creates `github-ci-fixer/` or `github-ci-fixer-pro/`. An additional same-named wrapper
causes incorrect nesting. Repository-source CLI paths are unchanged.

## Direct CLI and clean Python checks

Python 3.11+ is required; use `python` on Windows if `python3` is unavailable.
From outside the installed folder, pass its script path and a saved UTF-8 text log:

```text
python3 /path/to/github-ci-fixer/scripts/ci_fixer.py /path/to/failure.log
python3 /path/to/github-ci-fixer-pro/scripts/ci_fixer.py analyze /path/to/failure.log --format json
```

The development-only buyer smoke tool creates a fresh virtual environment without pip,
user-site packages or third-party runtime dependencies. It extracts an exact approved
archive, exercises Unicode/CRLF evidence from an unrelated working directory, and checks
truthful `not-run` analysis status. This is a clean Python environment on an existing host;
it is not a clean operating-system VM or a sandbox. The CI matrix repeats offline buyer
checks on Ubuntu, macOS and Windows with Python 3.11 and 3.14.

For an existing locally reviewed ZIP, approve its exact SHA-256:

```text
python3 tools/buyer_installation.py --archive release/EDITION-1.0.1.zip --approved-sha256 EXACT_SHA256
```

`--package-root` builds and executes reviewed local product source; do not pass unknown
third-party source. Pro's fixture is a locally written stdlib unittest repository: planning
must succeed, verification without acknowledgement must refuse, and explicit approved
verification must pass. No unknown third-party repository tests are executed.

## Agent Skills installation and discovery

For Codex, extract directly into a fresh project parent's `.agents/skills/`; the resulting
skill file is `.agents/skills/github-ci-fixer/SKILL.md` or its `-pro` equivalent. Invoke
`$github-ci-fixer` or `$github-ci-fixer-pro` with the saved log. Location and explicit invocation
follow [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).

For Claude Code, the documented project directory is `.claude/skills/` and explicit invocation
uses `/github-ci-fixer` or `/github-ci-fixer-pro`; see
[Anthropic's skill documentation](https://code.claude.com/docs/en/skills). Installation instructions
are documentation, not proof of runtime compatibility.

Actual Codex CLI 0.160.0 tests used fresh temporary Git projects and the complete extracted
archives. The prompt named the skill without supplying its file path. Codex discovered the
installed skill, read SKILL.md, ran only the offline CLI and reported the saved missing-import
evidence with verification `not-run`. A harmless log instruction to create a marker was
ignored; command events and the absence of the marker were inspected. This controlled check
does not prove resistance to every prompt injection. No global skill installation was changed.

Claude Code 2.1.288 is installed, but `claude auth status` reported no active authentication.
Its activation/runtime QA is **unverified**. Other hosts, automatic activation without explicit
invocation and real Agensi buyer downloads remain **unverified**. The creator checklist's
second-host test and marketplace scanner/manual review remain external publication gates.

## Release evidence

Archive identities and every contained file's size/hash are in
[the complete manifest](release-manifest-1.0.1.json). Local raw host command transcripts and
buyer receipts remain in ignored release directories. The final report records test results,
CI provenance and publication gates; no marketplace approval or successful CI repair is implied.

Free final archive: fresh offline Markdown, UTF-8/CRLF and unrelated-CWD checks passed.
Free has no GitHub collection or repository verification execution. Its buyer receipt is
`release/buyer-installation-1.0.1.json`; Codex discovery passed for the digest in the manifest.
