# Release hardening audit — 1.0.1

Audit date: 2026-10-08. Both working trees were clean before branching from fetched origin/main.
Free baseline: `b48c46d73ba11c6c6ccf3bf822f1a68656803f89`. PR #1 is merged. Baseline main run [37806423583](https://github.com/gogolumo/github-ci-fixer/actions/runs/37806423583) completed successfully with six OS/Python checks. These are baseline results, not acceptance evidence for 1.0.1.

## Findings before changes

- Verification approval in Pro binds HEAD, diff and untracked text, but ignores other Git-ignored inputs, symlinks, submodules and runtime dependencies. Tests run in the original directory. Approval is incomplete; ordinary host execution provides no isolation.
- Process capture uses temporary files and polling; descendant cleanup after a parent exits needs stronger handling on all three platforms.
- Rust formatting and Windows filesystem error 1005 require evidence-backed diagnosis and negative tests.
- Existing benchmarks use synthetic fixtures. Five historical failed runs must be evaluated separately, including unknown and additional failures.
- Free README still switches to the already merged feature branch.
- Packaging has deterministic timestamps and a trusted extraction smoke, but needs portable filename/collision checks, explicit metadata validation and execution from an unrelated working directory.
- Shared Free modules are bundled in Pro with MIT notices, but automated content identity checks are missing.
- Pro collection pins github.com and reads only requested runs/workflows; malformed metadata and cancelled/skipped/API failures need additional regression coverage.
- Existing archives are 1.0.0 preparation artifacts. They are excluded from Git. Commercial licensing and $24.99 personal-license terms remain in force.

## Scope and governance

Separate 1.0.1 branches and PRs target main. No merge or Agensi publication is authorized. Pro source stays private; commercial ZIPs stay local. PlaySparse, Wheel and ATELIER are read-only targets. Actual release evidence and remaining limitations will be recorded in FINAL_RELEASE_REPORT_1.0.1.md.
