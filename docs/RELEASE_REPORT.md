# Release report — 2026-10-08

Status: validated release candidate, prepared for manual submission review. Marketplace approval
has not been requested. Do not infer production readiness from package-validation success alone.

## Implemented and measured

Free: standalone offline log diagnosis for tested Python/pytest, npm/JS/TypeScript, Rust and shared
workflow/environment/file/permission/runner categories. Redacted physical-line evidence,
warning/exit separation, unclassified candidates, cautious recommendations and Markdown.
No network, code changes or test execution in Free runtime.

Pro (separate private project): explicit authenticated gh reads; failed run/job/commit metadata,
failed-step logs and workflow inspection at headSha; same-workflow metadata comparison;
related-signature groups; tested Java/macOS/Windows/Ubuntu signatures; JSON schema; guarded
single-job Python install-step diff proposal; hash/snapshot-bound approved check execution and
JSON/Markdown verification records. No automatic changes/push/merge/deploy.

Local host: macOS arm64, Python 3.14.6. Ruff check and format, mypy, compileall and skill-validator
metadata checks passed. Free: 14 unittest methods and 37/37 controlled benchmark cases. Pro:
18 unittest methods with 14 premium signature scenarios. These synthetic results are not
real-world accuracy, repair rates or measured time savings.

Actual Pro verification in disposable task-authored code recorded an assertion failure before a
manual arithmetic correction and a passing check afterward. A generated workflow diff passed
`git apply --check` and was applied in a disposable fixture; its install step/CI execution was
not run. No automatic source repair is claimed. Python bytecode cache isolation now avoids
same-size/same-timestamp stale imports; regression test passed. Zero/all-skipped unittest checks
are inconclusive, not verified success.

Codex runtime QA for Free passed: it ran the analyzer, ignored malicious log instructions and
kept repair verification not-run. Claude runtime QA was blocked: OAuth session expired and could
not be refreshed. Codex runtime QA for Pro also passed on synthetic multi-job evidence, preserving not-run and
ignoring the embedded instruction. Automatic discovery on all agents is not certified.
To retry Claude, authenticate locally with `claude auth login`, then run the bundled synthetic
skill example in a restricted test directory. Never paste credentials into chat.

Real Pro gh integration succeeded on public rhysd/actionlint run 37087088134: failed logs, commit
011a6d15e749bb3f2d771eed9c7aa0e7e3e10ee7 and workflow were retrieved. Logs supplied only an exit
marker usable by our rules; diagnosis correctly remains insufficient. Comparison path is
controlled-response tested, not certified against every GitHub event/job pattern.

## Security and distribution

Input, traversal, symlink/special-file, binary/oversize/line limits, secret-redaction, Markdown
injection, hostile ZIP, metadata, forged-plan, changed-snapshot, environment filtering, timeout,
output limit, archive independence and reproducibility checks passed. Redaction is best effort;
verification runs approved repository code and is not a sandbox. Git-ignored state is not fully
bound by snapshots. Windows batch wrappers are declined. CRLF workflow proposals preserve original line endings
and passed an actual git apply regression check. Workflow inspection is not full YAML
validation, matrix evaluation or arbitrary patch generation.

Public Free history paths and runtime imports were audited: no premium source/archive present.
Bundled Pro MIT core is byte-identical to Free. Pro GitHub source repository is PRIVATE and was
created/pushed only after explicit user approval. Commercial ZIP stays local outside Git.
No Agensi upload, release publication, automatic merge or deployment occurred. ATELIER was not modified.

## GitHub and CI

Public PR: https://github.com/gogolumo/github-ci-fixer/pull/1 (open, not merged).
Free branch: feat/github-ci-fixer-free. Pro branch: feat/github-ci-fixer-pro.
Implementation/source commits at package validation: Free `636f69bb4e7242c216504ecd429046127c5e4407`.
The report commit may follow; exact final hashes and live CI snapshots are recorded in local
release/release-manifest.json after the final push.

The matrix targets Ubuntu/macOS/Windows × Python 3.11/3.14. Read the actual latest job states
below or the live Actions page; queued/cancelled jobs are never described as passing. Superseded
runs were cancelled to avoid duplicate matrices. Local macOS checks passed independently.
An initial private Windows matrix failed mypy on os.killpg/SIGKILL narrowing; fixed by explicit
sys.platform branches. The fix also passed local mypy --platform win32. A subsequent Windows runtime failure
exposed CRLF proposal filtering, which was fixed and regression-tested. These initial failures
are retained as evidence; final matrix must validate the revised source.

## Packages

- github-ci-fixer-free.zip: 14646 bytes; SHA-256 `149b16daa66888d5f260c7b8c28debebbb64246089e5f2654ed338f524ffe7da`. Structure and extracted trusted smoke passed; marketplace approval not requested.

Both archives place SKILL.md at ZIP root, include all references/runtime/example files, have no
runtime pip dependency, and are far below the conservative 50 MB task limit. Timestamp/order
are fixed. Local validation is not Agensi security certification. Free release ZIP is local until
review; Pro ZIP must not be attached to the public PR or workflow artifacts.

## Remaining manual launch steps

1. Complete/review all required matrix and agent-runtime checks; resolve actual failures. Any
   still-queued Free hosted-runner checks must finish. Claude auth is a user-local step.
2. Review author-retained licenses and listings. MIT Free allows reuse/resale with attribution;
   premium personal-use terms prohibit redistribution and remain subject to marketplace terms.
3. Sign in to Agensi creator dashboard and complete enabled payout onboarding per current Terms.
4. Recheck current submission size/layout/security requirements; review ZIPs and SHA-256 locally.
5. Paste complete listings, choose truthful categories/tags, set Free $0 and Pro $24.99; upload manually.
6. Wait for automated scanning and human approval. Validate fingerprinted purchaser download and
   actual host installation. Add real marketplace URLs only once they exist.
7. Review public PR and merge only with explicit user approval. No merge has been performed.

Marketplace material: marketing/FREE_LISTING.md, separately private marketing/PRO_LISTING.md,
COMPARISON.md and LAUNCH_CHECKLIST.md. Author Bohdan Dron; no sales, reviews, adoption or universal
success claims. Remaining unsupported categories require agent reasoning with labeled hypotheses.

## Observed platform verification

Pro source commit 91411435d7b7de829bc4f0e1d4a0b56ee0c119b4 passed all six matrix jobs
(Ubuntu/macOS/Windows × Python 3.11/3.14) in its authorized PRIVATE repository.
Free source ec72a7b51312a8001dda8b37aa7822bd7b4ea2fd has five successful jobs and
one queued macOS/Python 3.11 job at this snapshot. Final live states are in the local manifest.
