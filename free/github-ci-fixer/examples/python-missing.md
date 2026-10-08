# Python import example

Controlled synthetic input: [python-missing.log](python-missing.log).
Run `python3 scripts/ci_fixer.py examples/python-missing.log` from the installed skill directory.
The [actual generated report](python-missing.report.md) records the input line and not-run status.
Compare the dependency manifest, installation step and interpreter. Do not blindly install a
package named after an import. Verification requires a reviewed install plus the failing test in
an authorized environment, and ultimately the matching CI job. No successful repair is claimed.
