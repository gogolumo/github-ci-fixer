# Contributing

Use Python 3.11+. Create a virtual environment, install requirements-dev.txt, and run:

```text
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m unittest discover -s tests -v
python tools/benchmark.py
python tools/real_world_benchmark.py
python tools/independent_evaluation.py --summary
python tools/buyer_installation.py --package-root free/github-ci-fixer
python tools/audit_public.py
python tools/build_release.py build free/github-ci-fixer release/github-ci-fixer-free-1.0.1.zip
```

Add realistic positive and negative fixtures when changing a rule; do not hardcode fixture names
in the engine or treat unknown logs as success. Preserve line references and not-run semantics.
Do not add premium modules/archives, real user logs, secrets or personal details to this public tree.
Keep feature branches reviewable; never bypass CI or automatically merge. Matrix CI covers
Ubuntu/macOS/Windows with Python 3.11 and 3.14. Test outputs document actual execution only.
