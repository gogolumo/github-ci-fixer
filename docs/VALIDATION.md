# Validation status — release candidate

Local host: macOS arm64, Python 3.14.6. Free: 13 unittest methods including 37 known diagnostic
scenarios passed. Pro (separate private tree): 15 unittest methods including 12 premium signatures
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

Agent CLIs are available; runtime behavior checks and real GitHub integration validation are
recorded in the final release report. Metadata validity alone does not prove agent behavior.
Marketplace acceptance and fingerprinted buyer downloads require manual submission/review.
