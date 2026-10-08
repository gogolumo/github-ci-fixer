# Real-world validation — 1.0.1

Collected 2026-10-08 using read-only GitHub CLI metadata and failed-job logs. All five repositories/runs are public. No target files, tests or workflows were changed or rerun. Six job/step cases from five unique failed runs were retained, including an unexplained macOS failure.

The committed fixtures are sanitized authentic excerpts, not fabricated reproductions. Provenance, job/step IDs, failed source SHA, physical raw-log ranges and full/excerpt SHA-256 are in [manifest](../fixtures/real_world/manifest.json). Known secrets/control sequences are redacted during analysis; printable caret ANSI sequences required an additional regression fix. GitHub returned UNKNOWN STEP in the log prefixes; actual step names below come from job metadata. Sanitized excerpts omit setup output. Complete collected logs were also evaluated locally and remain outside Git in the private checkout's ignored release/qa/raw directory. Root causes beyond the observed diagnostic signatures were not independently established.

| Case / actual run | Failing job and step | Observed evidence / expected category | Free actual | Pro actual |
| --- | --- | --- | --- | --- |
| [playsparse-rustfmt](https://github.com/gogolumo/PlaySparse/actions/runs/37612144554) | linux / Run cargo fmt --all -- --check | rustfmt showed formatting-only source changes under cargo fmt --all -- --check; compiler correctness was not tested. | rust.format | rust.format |
| [playsparse-windows-filesystem](https://github.com/gogolumo/PlaySparse/actions/runs/37612038222) | native (windows-latest, windows-x64, nsis) / Hosted Windows generated mount and descendant acceptance (GUI and physical proof excluded) | Error 1005 occurred when launching a fixture after mount, read and overlay write succeeded. The underlying driver/volume/application cause remains unproven. | windows.filesystem | windows.filesystem |
| [flask-mypy](https://github.com/pallets/flask/actions/runs/37633292268) | typing / Run uv run --locked --no-default-groups --group dev tox run -e typing | mypy rejected Mapping[str, Any] overriding an App base attribute typed dict[str, Any]. Root design intent and the right source/dependency repair were not independently established. | insufficient | python.typecheck |
| [requests-ruff-format](https://github.com/psf/requests/actions/runs/36454554828) | lint / Run pre-commit | The ruff-format hook failed because it modified two files; the preceding ruff check passed. No target files were changed by this evaluation. | python.format | python.format |
| [express-cookie-assertion](https://github.com/expressjs/express/actions/runs/37533322411) | Run tests (windows-latest, 24) / Run tests | The clearCookie assertion expected an Expires timestamp one second earlier than received. This is an observed assertion mismatch; timing flakiness and application defects remain hypotheses. | node.test | node.test |
| [playsparse-macos-unknown](https://github.com/gogolumo/PlaySparse/actions/runs/37612144554) | macos-sdk / Verified macFUSE SDK compile, link and tests without driver installation | The wrapper logged status FAIL, mount_validation NOT RUN and exit 1, without the underlying compiler/test diagnostics. No missing SDK or driver cause can be established. | insufficient | insufficient |

## Actual results and unsuccessful cases

Free supports four of six excerpt observations; Pro supports five. Free intentionally lacks the Flask mypy rule. Both leave the macOS SDK wrapper insufficient: status FAIL, NOT RUN and exit 1 contain no underlying compiler/test cause. PlaySparse formatting jobs are diagnosed, but the additional macOS failure in that same run is unresolved. No SDK/driver cause is invented.

All 12 excerpt edition checks and 10 complete-log edition checks matched their declared expectations. These 22 regression matches include expected unknown outcomes and are not an accuracy/success percentage. No additional diagnostic categories outside expectations appeared in this sample. Initially, Windows native FAIL was misclassified as Node and the Requests printable ANSI formatter output was missed; both were fixed with regression/negative tests. The same sample guided implementation, so this is an integration validation dataset, not an independent held-out accuracy benchmark. Convenience sampling from three public projects provides limited coverage. No real-world repair was attempted or verified; every analysis reports not-run.

## GitHub integration

Actual Pro collect executed against Flask run37633292268 and Express run37533322411. Both preserved failed headSHA and retrieved one workflow at that SHA. Flask type-check evidence was classified; Express required the new contextual assertion rule, then offline replay classified its observed expected/got mismatch. Collection does not establish timing flakiness or a code defect. Missing/expired logs, API errors, rate limits, malformed metadata, cancelled/skipped jobs and invalid repository/run inputs are separate mocked regression tests, not live demonstrations of every error condition.

## Reproduce

```text
python3 tools/real_world_benchmark.py
```

Free runs six excerpt checks without Pro or authentication. The private checkout runs both editions' analyzers against its own bundled core. For a local cross-edition comparison, pass `--pro-scripts PATH_TO_INSTALLED_PRO_SCRIPTS`; no remote checkout is needed at runtime. Optional `--raw-dir` replays the five locally collected complete logs only when their recorded hashes match. [Machine-readable final summary](real-world-benchmark-1.0.1.json) records findings, unknowns, false positives, source commits and complete-log outcomes. Synthetic positive/negative fixtures, mocked gh responses and controlled verification repositories remain separate tests; their counts are not real-world accuracy.
