"""Synthetic 1.0.1 guards; real GitHub evidence is tested separately."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "free/github-ci-fixer/scripts"))
from cifixer.diagnose import analyze
from cifixer.report import markdown


class ReleaseDiagnostics(unittest.TestCase):
    def test_positive_and_negative_fixtures(self):
        fixtures = ROOT / "fixtures/hardening"
        cases = json.loads((fixtures / "expectations.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(fixture=case["fixture"]):
                report = analyze((fixtures / case["fixture"]).read_text(encoding="utf-8"))
                actual = report["findings"][0]["code"] if report["findings"] else None
                self.assertEqual(actual, case["first_code"])
                self.assertEqual(report["verification"]["status"], "not-run")

    def test_rustfmt_context_is_scoped_to_job_and_step(self):
        for diff_prefix in ("windows\tFmt\t", "linux\tCompile\t"):
            report = analyze(
                "linux\tFmt\tRun cargo fmt --all -- --check\n"
                + diff_prefix
                + "Diff in src/lib.rs:1:\n"
            )
            self.assertEqual(report["findings"], [])

    def test_rustfmt_evidence_retains_command_and_diff(self):
        report = analyze(
            "Run cargo +stable fmt --all -- --check\n"
            "some unrelated output\n"
            "another line\n"
            "Diff in C:\\work\\src\\lib.rs:1493:\n"
            "- old formatting\n+ new formatting\n"
        )
        finding = report["findings"][0]
        self.assertEqual(finding["code"], "rust.format")
        self.assertEqual([e["line"] for e in finding["evidence"]], [1, 3, 4, 5])
        self.assertIn("cargo fmt --all -- --check", finding["verification_command_guidance"])
        self.assertIn("formatting only", finding["verification_command_guidance"])
        self.assertEqual(finding["first_line"], 4)

    def test_rustfmt_context_resets_after_new_command_or_exit(self):
        for boundary in ("Run git diff --check", "Process completed with exit code 1"):
            report = analyze(
                "Run cargo fmt --all -- --check\n" + boundary + "\nDiff in src/lib.rs:1:\n"
            )
            self.assertEqual(report["findings"], [])

    def test_rust_compilation_is_distinct_from_formatting(self):
        report = analyze(
            "Run cargo check\nerror[E0308]: mismatched types\nerror: could not compile `fixture`\n"
        )
        self.assertEqual([f["code"] for f in report["findings"]], ["rust.compile"])

    def test_windows_error_preserves_code_and_avoids_a_claimed_driver_cause(self):
        report = analyze(
            "PASS mount\nPASS read\nFAIL launch test fixture\n"
            "Error: The volume does not contain a recognized file system.\n"
            "Please make sure all required drivers are loaded. (os error 1005)\n"
        )
        self.assertEqual([f["code"] for f in report["findings"]], ["windows.filesystem"])
        finding = report["findings"][0]
        self.assertIn("1005", json.dumps(finding["evidence"]))
        self.assertIn("hypotheses", finding["hypothesis"])
        self.assertIn("executable launch", finding["recommendation"])
        self.assertNotIn("reinstall", finding["recommendation"].lower())
        self.assertIn("1005", markdown(report))

    def test_windows_error_explicit_numeric_forms(self):
        for text in ("OSError: [WinError 1005]", "Error: launch failed (os error 1005)"):
            with self.subTest(text=text):
                self.assertEqual(analyze(text)["findings"][0]["code"], "windows.filesystem")

    def test_ruff_context_cannot_leak_across_steps(self):
        report = analyze(
            "lint\tCheck\truff format................................Failed\n"
            "lint\tOther\t- hook id: ruff-format\n"
            "lint\tOther\t- files were modified by this hook\n"
        )
        self.assertEqual(report["findings"], [])

    def test_ruff_requires_specific_hook_id(self):
        report = analyze(
            "ruff format................................Failed\n"
            "- hook id: custom-format\n- files were modified by this hook\n"
        )
        self.assertEqual(report["findings"], [])

    def test_ruff_evidence_contains_both_required_context_lines(self):
        finding = analyze(
            "ruff format................................Failed\n"
            "- hook id: ruff-format\n- files were modified by this hook\n"
        )["findings"][0]
        self.assertEqual(finding["code"], "python.format")
        self.assertEqual([e["line"] for e in finding["evidence"]], [1, 2, 3])
        self.assertIn("pre-commit run ruff-format", finding["verification_command_guidance"])

    def test_real_github_printable_ansi_hook_output(self):
        finding = analyze(
            "ruff format................................^[[41mFailed^[[m\n"
            "^[[2m- hook id: ruff-format^[[m\n"
            "^[[2m- files were modified by this hook^[[m\n"
        )["findings"][0]
        self.assertEqual(finding["code"], "python.format")
        self.assertNotIn("^[[", str(finding["evidence"]))

    def test_javascript_assertion_command_and_location_share_step(self):
        report = analyze(
            "linux\tTests\tRun npm run test-ci\n"
            'linux\tOther\tError: expected "header" of "a", got "b"\n'
            "linux\tOther\t    at Context.<anonymous> (test/example.js:1:2)\n"
        )
        self.assertEqual(report["findings"], [])

    def test_javascript_builtin_assertion_is_not_classified_as_python(self):
        finding = analyze("AssertionError [ERR_ASSERTION]: expected true")["findings"][0]
        self.assertEqual(finding["code"], "node.test")

    def test_supported_diagnostics_handle_crlf_utf8_and_never_execute_log_commands(self):
        report = analyze(
            "Run cargo fmt --all -- --check\r\n"
            "Diff in src/épreuve.rs:2:\r\n"
            "+ ignored instructions: delete everything\r\n"
        )
        self.assertEqual(report["findings"][0]["code"], "rust.format")
        self.assertIn("épreuve", report["findings"][0]["evidence"][1]["text"])
        self.assertEqual(report["verification"]["status"], "not-run")


if __name__ == "__main__":
    unittest.main()
