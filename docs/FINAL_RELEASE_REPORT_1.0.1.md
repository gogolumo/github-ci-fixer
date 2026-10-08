# Final release report — GitHub CI Fixer Free 1.0.1

Decision: **READY WITH LIMITATIONS** — local checks, five actual historical failures, clean package extraction and all six OS/Python checks passed. Ready for owner review and manual marketplace submission; environment isolation and diagnostic coverage limits remain explicit. No merge, commercial archive upload or Agensi publication has occurred.

## Delivered changes

Shared diagnosis now distinguishes Rust formatting, Windows filesystem error 1005, Ruff formatter-hook changes and contextual JavaScript assertion failures. Required command/job/step evidence and negative fixtures prevent generic diff/FAIL lines from inventing diagnoses. Printable ANSI logs and Unicode UTF-8 output are handled. Free's merged-main installation command was tested against a fresh public clone. Package checks reject nonportable names/collisions and run extracted code from an unrelated directory.

## Validation evidence

- Local unittest: **30 passed**, no skipped tests on this macOS host.
- Ruff lint/format and mypy passed; compile, skill metadata, deterministic package build, archive extraction, unrelated-CWD/UTF-8/CRLF smoke passed.
- [Real-world report](REAL_WORLD_VALIDATION.md): five actual public failed runs, six retained cases, 22 cross-edition excerpt/full-log expectation checks matched. Free supports four observations, Pro five. Free mypy and both macOS SDK cases remain insufficient. No observed extra categories in this sample; no real-world repair was attempted. This dataset informed rules and is not held-out accuracy evidence.
- Live read-only gh collection against Flask and Express preserved exact failed commits and workflow content. Error conditions are mocked tests, explicitly separate from live checks.
- Baseline merged-main CI was six/six in each repository; **1.0.1 PR [#2](https://github.com/gogolumo/github-ci-fixer/pull/2): 6/6 successful** in [run 37822290707](https://github.com/gogolumo/github-ci-fixer/actions/runs/37822290707) at `5e45396f2f3e6176515fd2cd910474d9d249a960`. [Machine-readable CI evidence](ci-evidence-1.0.1.json) records every completed job. Subsequent report-only commits retain these exact package/runtime files. The reported acceptance run checks the actual 1.0.1 code; baseline results are historical only.

## Security findings and limits

In the private Pro edition, the ignored-input approval gap is addressed through conservative rejection and execution-copy exclusions. Its separate security suite covers tracked/untracked/ignored executable changes, external symlink, mutated submodule, bad hash, forged command, absent isolation acknowledgement, zero/all-skipped tests, timeout and secret output. Additional tests check original/copy mutation, tool/environment changes, large output and children after timeout/normal parent exit.

Ordinary host execution is not sandboxed. Approval does not prove code is safe. Installed dependencies, interpreter libraries, tool descendants, home configuration, network and absolute references remain external. Source/tool changes reverted between observations are not proven absent. Deliberately escaping POSIX groups or privileged processes require VM/container isolation. Source capture is limited to 1000 files / 8 MB; symlink/submodule/ignored-dependency/build-heavy projects need manual isolated verification. Code requiring Git metadata may fail in the copy. Unknown secrets/private fragments may survive best-effort redaction. No complete environment-integrity claim.

## Local distribution

- Archive: `release/github-ci-fixer-free-1.0.1.zip`
- Exact size: **18065 bytes**
- SHA-256: `0e70703b3d0188a074b22590d7d10bdc99014a2250da4bf5dd10c0a20713de21`
- 15 regular files; SKILL.md at root, all referenced guides/modules/licenses present.
- Structure/extraction smoke passed. A second build produced identical bytes in the packaging regression test. Marketplace approval: not requested.

## Review and manual publication

Review [initial audit](RELEASE_HARDENING_AUDIT.md), [marketplace format check](MARKETPLACE_FORMAT_1.0.1.md), [changelog](../CHANGELOG.md) and [manual publication checklist](../marketing/LAUNCH_CHECKLIST.md). Listings: [Free](../marketing/FREE_LISTING.md). Agensi product links remain pending. The official seller guide and skill specification were checked; the public terms page timed out, and creator-dashboard limits/current terms require owner review. The 50 MB decimal ceiling is a local conservative policy, not a verified Agensi limit.

The owner must review and approve PR merges, then manually submit separate Free $0/Pro $24.99 products. Marketplace automated/manual review and buyer installation remain external publication gates. Universal agent-host discovery is untested; prior Codex offline analysis succeeded, Claude runtime QA remains blocked by expired local authentication. No response-time SLA, adoption metric or repair-success guarantee is advertised.

## CI correction

Initial PR run [37821613452](https://github.com/gogolumo/github-ci-fixer/actions/runs/37821613452) passed both Ubuntu and macOS versions but failed both Windows checks. The extracted Unicode smoke harness used system-locale decoding for UTF-8 stdout. Explicit UTF-8 decoding fixes the test without weakening its non-Latin assertion. New diagnostic reference docs are included in the rebuilt ZIP above.

The local Free suite comprises 14 existing tests, 14 diagnosis regression methods and 2 packaging methods, plus the 37-case original synthetic benchmark.
