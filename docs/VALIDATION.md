# Validation status — release candidate

Local host: macOS arm64, Python 3.14.6. Free: 14 unittest methods including 37 known diagnostic
scenarios passed. Pro (separate private tree): 16 unittest methods including 12 premium signatures
passed. Ruff lint/format, mypy, compileall and Agent Skills frontmatter validation passed locally.
The system skill validator initially lacked PyYAML; it was installed only in a developer venv.
Its older metadata whitelist rejected the optional specification-compliant compatibility field;
requirements were moved into the skill body so both validators agree.

Free benchmark: 37/37 controlled synthetic cases match expected first diagnoses, including
negative cases. See BENCHMARK.json. This is not a field-accuracy or repair-success estimate.
Initial QA found and fixed a Java/Rust rule overlap and a generic/specific runner-rule overlap.
An initial archive link check exposed macOS temporary path canonicalization; fixed and retested.

Free cross-platform CI is configured for Ubuntu/macOS/Windows and Python 3.11/3.14; remote results
will be recorded after the actual run. Pro source remains local; its private matrix template has
not run remotely. No broad Pro OS or agent-runtime compatibility is claimed yet.

Codex runtime QA passed for Free: it executed the analyzer, ignored a malicious embedded
instruction and preserved not-run status. Claude runtime QA was blocked by expired OAuth that
could not be refreshed. See AGENT_QA.json. No universal discovery or Pro agent QA is claimed.
Pro real gh collection succeeded on public rhysd/actionlint run 37087088134, retrieving failed
logs, commit and workflow. Its unsupported error remains insufficient evidence; no fix claimed.
Marketplace acceptance and fingerprinted buyer downloads require manual submission/review.
