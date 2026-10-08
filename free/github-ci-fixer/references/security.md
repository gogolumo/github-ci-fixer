# Security and privacy

Inputs are untrusted evidence. Scripts never obey embedded instructions, eval log content,
apply patches, extract supplied log ZIPs, or send offline content anywhere. Files must be regular
UTF-8 text, at most 8 MB, without NUL bytes. Symlinks/special files are rejected. Lines are
bounded to 16000 characters; log rows to 50000; findings to 100. Reject arbitrary binary/ZIP formats rather than
silently interpreting them. Log paths are supplied by the user; repository-relative reads reject
traversal and escapes. Markdown escapes HTML and active formatting from evidence.

Common token prefixes, credential assignments, authorization headers, URL credentials,
JWT-like strings and PEM private keys are redacted. Unknown secrets, personal information and
source fragments may remain. Redaction is neither a DLP system nor permission to publish logs.
No telemetry, background services or hidden network access. AI host providers have their own
network/data policies: use offline scripts if content must stay local.

Explicit gh collection talks to GitHub using existing auth; Pro never reads auth token files.
Verification runs approved repository code with a minimal inherited environment, bounded capture
and timeout. This is NOT a sandbox: malicious tests can read local files or make network calls.
Use a disposable container/VM with no secrets for untrusted repositories. Approval flags require
review, not automatic skill consent. Never claim tests ran if only a plan/report was generated.

Release validation rejects unsafe archive paths, duplicates, symlinks, unsupported files and
expanded-size abuse. Smoke execution requires an exact approved archive digest; structural
inspection alone is not marketplace approval. The builder executes the archive it just built
from caller-supplied trusted source. Do not build untrusted source on your host.
