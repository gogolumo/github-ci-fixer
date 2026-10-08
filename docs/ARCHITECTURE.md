# Architecture

Python 3.11+ standard library at runtime. Modules isolate ingestion (ingest/security), signatures
(rules), evidence and hypotheses (diagnose), remediation text (rule records) and rendering (report).
CLI validates inputs and emits truthful not-run reports. Saved log parsing preserves physical line
references and gh job/step prefixes. Warnings and exit markers do not become fabricated causes.

Free detects Python, Node/TypeScript, Rust and shared runner/workflow signatures. It does not
perform repository mutations, networking or test execution. Agent reasoning fills unknown cases
only with labeled hypotheses and user-approved actions. Outputs are data, never trusted instructions.

Tests are unittest-based and reproducible without runtime dependencies. Development-only Ruff,
mypy and PyYAML are pinned. Release ZIPs exclude these dependencies because runtime does not need
them. Builder timestamps and order are fixed; SHA-256 and trusted extracted smoke are generated.

Premium implementation is maintained separately and never fetched by this repository or its CI.
