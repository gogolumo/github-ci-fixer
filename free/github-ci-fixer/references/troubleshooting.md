# Supported failure signatures

Python: missing imports, pytest failures/assertions and resolver failures. Node: module resolution,
ERESOLVE, stale npm lockfile/usage errors, TypeScript diagnostics and Jest/assertion failures.
Rust: rustc E-codes and Cargo dependency selection. Shared: environment lookups, missing paths,
filesystem/API permissions, rejected workflows and unavailable runner commands.

An import name is not necessarily a package distribution name. EUSAGE needs its surrounding
usage error. KeyError can be ordinary dictionary access. A test failure does not tell you whether
the test or production code is wrong. The first *observed* meaningful error may follow omitted
causes. Unknown/empty/truncated logs must not yield a confident root cause. Full YAML parsing,
network outage diagnosis and arbitrary compiler languages are outside Free's tested rules.

Use the report's specific recommendation and verification guidance. Keep warnings separate;
exit markers only describe command failure. Obtain the preceding command and complete failed-step
output when evidence is insufficient. No code or repository test is executed by analysis.
