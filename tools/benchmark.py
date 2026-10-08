#!/usr/bin/env python3
"""Known expected diagnoses; results describe synthetic fixtures, not field accuracy."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "free/github-ci-fixer/scripts"))
from cifixer.diagnose import analyze


def main():
    cases = json.loads((ROOT / "fixtures/expectations.json").read_text())
    results = []
    for case in cases:
        report = analyze((ROOT / "fixtures" / case["fixture"]).read_text())
        actual = report["findings"][0]["code"] if report["findings"] else None
        results.append({**case, "actual": actual, "passed": actual == case["first_code"]})
    print(
        json.dumps(
            {
                "dataset": "controlled-synthetic-v1",
                "cases": len(results),
                "passed": sum(r["passed"] for r in results),
                "results": results,
                "limitations": [
                    "Hand-curated signature examples; not an estimate of real-world diagnosis accuracy",
                    "Unknown errors intentionally return insufficient evidence",
                    "No repair success rate measured",
                ],
            },
            indent=2,
        )
    )
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
