#!/usr/bin/env python3
"""Replay authenticated public-log excerpts; never execute their contents or fetch logs."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = """
import importlib, json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from cifixer.security import read_text
module = importlib.import_module('pro.analysis' if sys.argv[2] == 'pro' else 'cifixer.diagnose')
analyzer = module.enrich if sys.argv[2] == 'pro' else module.analyze
report = analyzer(read_text(Path(sys.argv[3])), Path(sys.argv[3]).name)
print(json.dumps({
    'assessment': report['assessment'],
    'codes': [finding['code'] for finding in report['findings']],
    'findings': [{'code': finding['code'], 'line': finding['first_line'],
                  'job': finding['job'], 'step': finding['step']}
                 for finding in report['findings']],
    'unclassified_errors': len(report['unclassified_errors']),
    'verification': report['verification']['status'],
    'missing_information': report['missing_information'],
}))
"""


def analyze_log(scripts: Path, edition: str, log: Path) -> dict:
    """Separate imports prevent one edition from accidentally loading the other's core."""
    result = subprocess.run(
        [sys.executable, "-c", WORKER, str(scripts), edition, str(log)],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=ROOT,
    )
    if result.returncode:
        raise ValueError(f"{edition} analysis failed for {log.name}: {result.stderr[:1000]}")
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pro-scripts", type=Path, help="Optional installed Pro scripts directory")
    parser.add_argument(
        "--raw-dir", type=Path, help="Optional locally collected complete failed-job logs"
    )
    parser.add_argument("--output", type=Path, help="Write the same JSON printed to stdout")
    args = parser.parse_args()
    fixture_root = ROOT / "fixtures/real_world"
    manifest = json.loads((fixture_root / "manifest.json").read_text(encoding="utf-8"))
    free_scripts = ROOT / "free/github-ci-fixer/scripts"
    bundled_pro = ROOT / "premium/github-ci-fixer-pro/scripts"
    if not free_scripts.is_dir():
        # The private repository checks its MIT-licensed bundled Free core independently.
        free_scripts = bundled_pro
    editions = {"free": free_scripts}
    if args.pro_scripts is not None:
        editions["pro"] = args.pro_scripts.resolve()
    elif bundled_pro.is_dir():
        editions["pro"] = bundled_pro
    results = []
    failures = []
    for case in manifest["cases"]:
        fixture = fixture_root / case["fixture"]
        if hashlib.sha256(fixture.read_bytes()).hexdigest() != case["fixture_sha256"]:
            raise ValueError(f"Fixture checksum changed: {case['id']}")
        actual = {}
        for edition, scripts in editions.items():
            report = analyze_log(scripts.resolve(), edition, fixture.resolve())
            expected = case[f"expected_{edition}_codes"]
            matched = report["codes"] == expected and report["verification"] == "not-run"
            actual[edition] = {
                **report,
                "expected_codes": expected,
                "regression_matched": matched,
                "supported_observation": bool(report["codes"]),
                "false_positive_codes": [code for code in report["codes"] if code not in expected],
            }
            if not matched:
                failures.append(f"{case['id']}: {edition} excerpt regression mismatch")
        results.append(
            {
                "id": case["id"],
                "repository": case["repository"],
                "run_id": case["run_id"],
                "run_url": case["run_url"],
                "job": case["job"],
                "step": case["step"],
                "commit": case["commit"],
                "source_kind": manifest["source_kind"],
                "expected_observed_category": case["expected_observed_category"],
                "evidence_assessment": case["evidence_assessment"],
                "editions": actual,
            }
        )
    complete_logs = []
    if args.raw_dir is not None:
        for filename in sorted({case["raw_log_file"] for case in manifest["cases"]}):
            cases = [case for case in manifest["cases"] if case["raw_log_file"] == filename]
            raw = args.raw_dir / filename
            if hashlib.sha256(raw.read_bytes()).hexdigest() != cases[0]["raw_log_sha256"]:
                raise ValueError(f"Complete log checksum changed: {filename}")
            outcomes = {}
            for edition, scripts in editions.items():
                report = analyze_log(scripts.resolve(), edition, raw.resolve())
                expected = sorted(
                    {code for case in cases for code in case[f"expected_{edition}_codes"]}
                )
                observed = sorted(set(report["codes"]))
                matched = observed == expected and report["verification"] == "not-run"
                outcomes[edition] = {
                    **report,
                    "expected_unique_codes": expected,
                    "regression_matched": matched,
                    "false_positive_codes": [code for code in observed if code not in expected],
                }
                if not matched:
                    failures.append(f"{filename}: {edition} complete-log regression mismatch")
            complete_logs.append(
                {"file": filename, "sha256": cases[0]["raw_log_sha256"], "editions": outcomes}
            )
    summary = {
        "schema_version": "1.0",
        "dataset": manifest["dataset"],
        "source_kind": manifest["source_kind"],
        "unique_failed_runs": len({case["run_id"] for case in manifest["cases"]}),
        "job_step_cases": len(results),
        "editions_tested": list(editions),
        "regression_checks": len(results) * len(editions) + len(complete_logs) * len(editions),
        "regression_failures": failures,
        "results": results,
        "complete_log_results": complete_logs,
        "limitations": manifest["limitations"]
        + [
            "Regression matches include intentionally unsupported outcomes; they are not diagnosis accuracy",
            "No target checkout, repair, test execution, workflow rerun or success-rate measurement",
        ],
    }
    serialized = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8", newline="\n")
    print(serialized, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
