# Diagnostic hardening fixtures

These are handcrafted synthetic reproductions and negative controls. They test
specific guards; they are not raw real-run logs or a measure of field accuracy.
The separately documented real-world fixtures retain actual failed-run evidence.

The 14 cases cover Rust formatting, Windows volume errors, Ruff formatting hooks,
JavaScript assertions and incomplete/unrelated/successful alternatives. A
formatting diff requires an active `cargo fmt --check` command in the same job
and step. Ruff requires its failed formatter hook and modified-files details.
The new expected/actual assertion form requires a JavaScript test command and
JavaScript source location. A generic `FAIL launch test fixture` is not a
JavaScript suite diagnosis.
