# Security policy and threat model

Assets: local files, credentials, private source/logs, approved execution authority and premium IP.
Adversaries can control CI log text, repository files, paths and supplied archives. Trust is never
inherited from a log message. Deterministic parsing is read-only; proposals do not execute.

Controls: bounded regular UTF-8 files; no symlink/special-file input; path containment for repository
reads; inert Markdown rendering; best-effort credential redaction; argument-vector subprocesses;
explicit collection; separate consent-bound verification; deterministic archive layout validation.
No eval, exec of log text, shell=True, credential harvesting or telemetry. Package validation does
not safely execute arbitrary archive contents: smoke requires a specific approved digest.

Residual risks: secret formats not recognized by redaction, personal/source fragments in evidence,
AI host data policies, ignored Git files not bound by snapshots, and arbitrary behavior of approved
repository tests. Verification environment filtering is not a sandbox. Use a disposable VM/container
without secrets for untrusted code. Timeout/output limits mitigate accidents, not hostile OS escape.

Report vulnerabilities through GitHub private vulnerability reporting if enabled; otherwise contact
the author via https://github.com/gogolumo to arrange private disclosure. Do not open public issues
with credentials or premium source. No response-time SLA is promised. Review marketplace listings
and packages locally before submitting; no Agensi security approval is claimed.
