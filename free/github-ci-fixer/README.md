# GitHub CI Fixer Free 1.0.1

Extract the ZIP into a parent directory. It creates the `github-ci-fixer/` skill
folder with `SKILL.md`, scripts, references and the MIT license.

With Python 3.11 or newer, run the following from this folder:

```sh
python scripts/ci_fixer.py /path/to/job.log
```

On hosts using `python3`, replace `python` accordingly. An absolute script path
also works from another working directory. Input must be a saved UTF-8 text log.
No account, dependencies or network access are needed for offline analysis.

Exit 0 means analysis completed. Findings describe supported signatures and
observed evidence; they do not establish every root cause or repair CI.
Verification remains `not-run`. Unknown causes require more evidence.

For an Agent Skills host, place this entire folder in that host's documented
skills directory. Host discovery and marketplace approval are separate checks.
See [SKILL.md](SKILL.md), [security](references/security.md),
[troubleshooting](references/troubleshooting.md) and [license](LICENSE.txt).
