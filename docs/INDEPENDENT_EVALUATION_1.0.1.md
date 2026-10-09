# New-case diagnostic evaluation — final release gate 1.0.1

Evaluation date: 2026-10-08. The dataset contains seven evidence cases from six
newly reviewed public failed GitHub Actions runs. No diagnostic rules were changed
for these cases. Both editions classified one Python assertion observation and
left five unsupported observations and one aggregate-only unknown case
unclassified. No false-positive category was emitted in the reviewed excerpts or
complete failed-job logs. This limited convenience sample does not establish
general diagnosis accuracy, root-cause accuracy or successful repair rates.

## Method and source freeze

Before running either analyzer, the reviewer saved SHA-256 values for the Free
diagnostic modules and Pro enrichment module, then recorded case evidence and
expected category codes in [the dataset manifest](../fixtures/independent_gate/manifest.json).
The initial source revisions were Free
`0d58a43af4cbe5a5437e168ffa7a6b11e424e01b` and Pro
`7e9e92c53deb9f19728f6f6984a19334ea5e7c05`. The replay tool checks the actual
diagnostic file bytes against this freeze; later security or packaging changes
outside those modules do not change this diagnostic evaluation.

Case selection used recent public failures in pytest, Pydantic, Black and
ripgrep, which were absent from the previous design dataset. The previous
PlaySparse, Flask, Requests, Express and actionlint runs were explicitly excluded.
Selection intentionally retained identifiable unsupported failures and a
downstream aggregate-only input. It was not random, blinded selection, a broad
held-out benchmark or a balanced language/platform sample. Expected codes were
chosen from the observed diagnostics and the already frozen supported categories
before invoking an analyzer.

Only read-only run metadata and failed-job logs were retrieved with `gh`.
Repository contents and commands printed in logs were never executed. Minimal
public excerpts preserve timestamps and job/step prefixes, with ANSI sequences
removed and secret redaction applied. The full raw public logs are retained only
in the private checkout's ignored `release/qa/final-gate/raw` directory. The
committed manifest includes full source commit SHA, run/job IDs, API failed step,
raw-log digest, exact source line ranges and fixture digest for every case.

Five runs' `gh --log-failed` output uses `UNKNOWN STEP`. The failed-step names
below come from separate API metadata; they were not inserted into fixture text.
Two `cli/cli` acquisition candidates returned no jobs and `log not found`; they
are recorded as acquisition exclusions and are not counted as analysis results.

## Exact results

The columns below apply to both editions; their outputs were identical for this
dataset. `supported`, `unsupported` and `unknown` are the reviewer's evidence
states. The product itself reports `signature-supported` or `insufficient`; it
does not emit a distinct unsupported category.

| Evidence case and source | API job / failed step | Reviewed state and observed diagnostic | Actual codes / assessment | Retained unclassified error rows |
| --- | --- | --- | --- | --- |
| [pytest 37653997861](https://github.com/pytest-dev/pytest/actions/runs/37653997861), timing assertion | `build (windows-py311)` / `Test without coverage` | Supported: measured `0.19469999999999998` fails `< 0.1` in the named terminal-output test | `python.test` / `signature-supported` | 2 |
| [pytest 37653997861](https://github.com/pytest-dev/pytest/actions/runs/37653997861), aggregate-only input | `check` / `Decide whether the needed jobs succeeded or failed` | Unknown for this input: the required `build` job failed; its originating diagnostic is absent from the aggregate excerpt | none / `insufficient` | 3 |
| [Pydantic 37818576440](https://github.com/pydantic/pydantic/actions/runs/37818576440) | `upload-previews` / `Run dawidd6/action-download-artifact@d63b86af1b34672e53c440b1b83979861906bad7` | Unsupported: artifact lookup found no matching eligible workflow run; a fork was skipped with `allow forks: false` | none / `insufficient` | 1 |
| [Pydantic 37784817707](https://github.com/pydantic/pydantic/actions/runs/37784817707) | `Send tweet` / `Run uv sync --only-group tweet` | Unsupported signature form: uv reports no `pyproject.toml` in the current directory or any ancestor | none / `insufficient` | 1 |
| [Black 37824955673](https://github.com/psf/black/actions/runs/37824955673) | `lint` / `Run pre-commit hooks` | Unsupported: the **Prettier** hook failed and modified files; isort, flake8 and mypy passed | none / `insufficient` | 4 |
| [Black 37773541121](https://github.com/psf/black/actions/runs/37773541121) | `check` / `Grep CHANGES.md for PR number` | Unsupported: repository policy requests the PR entry in `CHANGES.md` or a reviewed skip-news label | none / `insufficient` | 0 |
| [ripgrep 37085789735](https://github.com/BurntSushi/ripgrep/actions/runs/37085789735) | `test (pinned, ubuntu-latest, 1.96.0)` / `Build ripgrep and all crates` | Unsupported: Cargo dependency download fails with curl HTTP2 framing error 16 | none / `insufficient` | 5 |

Every output reported verification `not-run`. Both editions emitted only
`python.test` for the complete pytest failed-job log and no category for each of
the other five complete failed-job logs. Complete-context analysis therefore did
not introduce an extra category or hide an excerpt-only false positive.

The near-match cases produced no Ruff-format diagnosis for a failed Prettier
hook, no type-check diagnosis for a passing mypy hook, no rustc compilation
diagnosis for Cargo's HTTP2 download failure, and no dependency diagnosis for an
artifact search failure. These observations cover only the recorded inputs;
they do not establish an absence of false positives across other logs.

## Missing evidence and limitations

- The timing assertion proves an observed threshold mismatch. It does not
  establish whether scheduling variance, implementation behavior or the threshold
  caused the failure. No repair was attempted.
- The artifact log shows a skipped fork and a failed lookup. It does not prove
  that the fork filter was the only reason no eligible artifacts matched.
- The uv diagnostic identifies a missing project file, but does not establish the
  intended working directory, checkout contents or why the file was absent.
- Prettier's full diff and the project's formatter policy were not evaluated.
  Cargo's HTTP2 error does not establish a persistent network, proxy or registry
  defect.
- The aggregate-only unknown case intentionally excludes its predecessor's
  diagnostic. The separate pytest case and complete log do contain that
  diagnostic; the entire pytest run is not described as unknowable.
- The product's generic `missing_information` advice requests complete logs for
  unsupported signatures even when complete logs were supplied. This is a
  coverage limitation, not proof that the original evidence was missing.
- Black's changelog policy message is not retained as an unclassified error row;
  the output retains its exit marker and insufficient assessment, while the
  fixture and independent report preserve the policy evidence.
- Five identifiable observations remain unsupported by the current rules.
  Pro adds no category coverage over Free on this selected set. This report does
  not replace the earlier design-set regression report or claim a numerical
  accuracy improvement.

## Reproduction and release interpretation

From a Free checkout, replay the committed excerpts offline:

```sh
python3 tools/independent_evaluation.py
```

With an authorized local Pro installation, include its scripts directory:

```sh
python3 tools/independent_evaluation.py --pro-scripts /path/to/github-ci-fixer-pro/scripts
```

The private checkout auto-selects its bundled Free core and Pro enrichment. An
optional `--raw-dir` replays locally retained complete logs after checking their
committed digests. The tool never fetches new logs or executes repository tests.
It uses separate Python processes for each edition to prevent import leakage.

The recorded two-edition run performed **14 excerpt replay expectation checks**,
with zero mismatches and zero diagnostic-source hash differences. These equality
checks include intentionally empty outcomes and become ordinary regression
checks after this evaluation; they are not 14 successful diagnoses or repairs.
Exact findings, missing-information text and complete-log outcomes are in
[the machine report](independent-evaluation-1.0.1.json).

The evaluated category behavior is acceptable for review with the documented
coverage limits and truthful marketing. It provides no marketplace acceptance
evidence and no permission to publish or merge.
