#!/usr/bin/env python3
"""Replay newly selected public failure evidence without fetching or executing its content."""

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
    'unclassified_errors': report['unclassified_errors'],
    'verification': report['verification']['status'],
    'missing_information': report['missing_information'],
}))
"""


def analyze_log(scripts: Path, edition: str, log: Path) -> dict:
    """Separate processes prevent edition-specific imports from contaminating each other."""
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


def checked_fixture(directory: Path, filename: str, expected_digest: str) -> Path:
    """The committed manifest may name only ordinary files immediately below its directory."""
    if Path(filename).name != filename or filename in {"", ".", ".."}:
        raise ValueError("Unsafe evaluation fixture path")
    path = directory / filename
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Evaluation fixture must be an ordinary file: {filename}")
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
        raise ValueError(f"Evaluation fixture checksum changed: {filename}")
    return path.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pro-scripts", type=Path, help="Optional installed Pro scripts directory")
    parser.add_argument(
        "--raw-dir", type=Path, help="Optional private local complete public-job logs"
    )
    parser.add_argument("--output", type=Path, help="Write the same JSON printed to stdout")
    parser.add_argument("--summary", action="store_true", help="Print only the compact outcome")
    args = parser.parse_args()
    fixtures = ROOT / "fixtures/independent_gate"
    manifest = json.loads((fixtures / "manifest.json").read_text(encoding="utf-8"))
    free_scripts = ROOT / "free/github-ci-fixer/scripts"
    bundled_pro = ROOT / "premium/github-ci-fixer-pro/scripts"
    if not free_scripts.is_dir():
        free_scripts = bundled_pro
    editions = {"free": free_scripts}
    if args.pro_scripts:
        editions["pro"] = args.pro_scripts.resolve()
    elif bundled_pro.is_dir():
        editions["pro"] = bundled_pro
    frozen = manifest["frozen_diagnostic_sources"]["sha256_by_edition"]
    source_differences = []
    for edition, scripts in editions.items():
        for relative, digest in frozen[edition].items():
            path = scripts / relative
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                source_differences.append(f"{edition}: {relative}")
    results = []
    mismatches = []
    for case in manifest["cases"]:
        log = checked_fixture(fixtures, case["fixture"], case["fixture_sha256"])
        outcomes = {}
        for edition, scripts in editions.items():
            actual = analyze_log(scripts.resolve(), edition, log)
            expected = case[f"expected_{edition}_codes"]
            false_positives = [code for code in actual["codes"] if code not in expected]
            missing = [code for code in expected if code not in actual["codes"]]
            matched = actual["codes"] == expected and actual["verification"] == "not-run"
            outcomes[edition] = {
                **actual,
                "expected_codes_from_preanalysis_evidence_review": expected,
                "false_positive_codes": false_positives,
                "missing_supported_codes": missing,
                "replay_expectation_matched": matched,
            }
            if not matched:
                mismatches.append(f"{case['id']}: {edition}")
        results.append({**case, "editions": outcomes})
    complete_logs = []
    if args.raw_dir:
        for filename in sorted({case["raw_log_file"] for case in manifest["cases"]}):
            cases = [case for case in manifest["cases"] if case["raw_log_file"] == filename]
            raw = checked_fixture(args.raw_dir, filename, cases[0]["raw_log_sha256"])
            complete_logs.append(
                {
                    "file": filename,
                    "sha256": cases[0]["raw_log_sha256"],
                    "editions": {
                        edition: analyze_log(scripts.resolve(), edition, raw)
                        for edition, scripts in editions.items()
                    },
                    "interpretation": "Complete-job context check; no extra accuracy claim",
                }
            )
    counts = {
        state: sum(case["evidence_state"] == state for case in manifest["cases"])
        for state in ("supported", "unsupported", "unknown")
    }
    summary = {
        "schema_version": "1.0",
        "dataset": manifest["dataset"],
        "collection_date": manifest["collection_date"],
        "source_kind": manifest["source_kind"],
        "selection_policy": manifest["selection_policy"],
        "unique_failed_runs": len({case["run_id"] for case in manifest["cases"]}),
        "excerpt_cases": len(results),
        "human_evidence_state_counts": counts,
        "editions_tested": list(editions),
        "diagnostic_source_freeze_matched": not source_differences,
        "diagnostic_source_differences": source_differences,
        "replay_expectation_checks": len(results) * len(editions),
        "replay_expectation_mismatches": mismatches,
        "false_positive_codes": {
            edition: [
                {"id": case["id"], "code": code}
                for case in results
                for code in case["editions"][edition]["false_positive_codes"]
            ]
            for edition in editions
        },
        "results": results,
        "complete_log_results": complete_logs,
        "acquisition_exclusions": manifest["acquisition_exclusions"],
        "limitations": manifest["limitations"],
    }
    serialized = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8", newline="\n")
    if args.summary:
        print(
            json.dumps(
                {
                    key: value
                    for key, value in summary.items()
                    if key not in {"results", "complete_log_results", "limitations"}
                },
                indent=2,
            )
        )
    else:
        print(serialized, end="")
    # Exact replay and unchanged code are release checks, not a score for successful repairs.
    return 1 if mismatches or source_differences else 0


if __name__ == "__main__":
    raise SystemExit(main())
