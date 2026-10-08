"""Observable diagnostic, CLI and adversarial-input behavior."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "free/github-ci-fixer"
sys.path.insert(0, str(SKILL / "scripts"))
from cifixer.diagnose import analyze
from cifixer.report import markdown
from cifixer.security import MAX_BYTES, contained_file, read_text

spec = importlib.util.spec_from_file_location("release", ROOT / "tools/build_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class Diagnostics(unittest.TestCase):
    def test_benchmark(self):
        expected = json.loads((ROOT / "fixtures/expectations.json").read_text())
        for case in expected:
            with self.subTest(case=case["fixture"]):
                report = analyze((ROOT / "fixtures" / case["fixture"]).read_text())
                actual = report["findings"][0]["code"] if report["findings"] else None
                self.assertEqual(actual, case["first_code"])
                self.assertEqual(report["verification"]["status"], "not-run")
                if actual is None:
                    self.assertEqual(report["assessment"], "insufficient")

    def test_evidence_job_and_line(self):
        text = "build\tInstall\t2026-10-08T12:34:56.001Z installing\nbuild\tTest\t2026-10-08T12:34:57Z ModuleNotFoundError: No module named 'x'\n"
        finding = analyze(text)["findings"][0]
        self.assertEqual(
            (finding["job"], finding["step"], finding["first_line"]), ("build", "Test", 2)
        )
        self.assertTrue(all(e["step"] == "Test" for e in finding["evidence"]))

    def test_exit_not_root_cause(self):
        report = analyze(
            "warning: old API\nModuleNotFoundError: No module named 'x'\n##[error]Process completed with exit code 1\n"
        )
        self.assertEqual(len(report["findings"]), 1)
        self.assertEqual(len(report["warnings"]), 1)
        self.assertEqual(len(report["secondary_exit_markers"]), 1)

    def test_multiple_independent_errors_are_not_false_cascades(self):
        report = analyze("ModuleNotFoundError: No module named 'x'\nPermission denied\n")
        self.assertEqual(
            [f["code"] for f in report["findings"]], ["python.missing-module", "permission.denied"]
        )
        self.assertNotIn("caused_by", report["findings"][1])

    def test_secret_redaction_and_line_preservation(self):
        token = "ghp_" + "a" * 36
        log = f"TOKEN={token}\n-----BEGIN RSA PRIVATE KEY-----\nprivatebody\n-----END RSA PRIVATE KEY-----\nModuleNotFoundError: No module named 'x'\nAuthorization: Bearer example-private-value\n"
        report = analyze(log)
        dumped = json.dumps(report) + markdown(report)
        self.assertNotIn(token, dumped)
        self.assertNotIn("privatebody", dumped)
        self.assertNotIn("example-private-value", dumped)
        self.assertEqual(report["findings"][0]["first_line"], 5)

    def test_markdown_injection_is_inert(self):
        report = analyze(
            "ModuleNotFoundError: No module named '<script>alert(1)</script>' ``` [click](https://evil.test)\n"
        )
        rendered = markdown(report)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("```", rendered)
        self.assertNotIn("[click](", rendered)

    def test_oversize_and_binary(self):
        with self.assertRaises(ValueError):
            analyze("x" * (MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            analyze("abc\0def")
        report = analyze("x" * 16001)
        self.assertTrue(any("incomplete" in n for n in report["missing_information"]))
        lines = analyze("\n" * 50_001)
        self.assertTrue(any("50000 lines" in n for n in lines["missing_information"]))

    def test_filesystem_guards(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "binary.log"
            binary.write_bytes(b"abc\0def")
            with self.assertRaises(ValueError):
                read_text(binary)
            bad = root / "encoding.log"
            bad.write_bytes(b"\xff\xfe")
            with self.assertRaises(ValueError):
                read_text(bad)
            with self.assertRaises(ValueError):
                read_text(root)
            with self.assertRaises(ValueError):
                contained_file(root, "../outside")
            if os.name != "nt":
                link = root / "link.log"
                link.symlink_to(binary)
                with self.assertRaises(ValueError):
                    read_text(link)
                fifo = root / "fifo"
                os.mkfifo(fifo)
                with self.assertRaises(ValueError):
                    read_text(fifo)

    def test_cli(self):
        cli = [sys.executable, str(SKILL / "scripts/ci_fixer.py")]
        completed = subprocess.run(
            cli + [str(ROOT / "fixtures/python_missing.log")],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("Python import failed", completed.stdout)
        self.assertIn("not-run", completed.stdout)
        missing = subprocess.run(
            cli + ["/nonexistent/log"], capture_output=True, text=True, timeout=10
        )
        self.assertEqual(missing.returncode, 2)
        self.assertNotIn("Traceback", missing.stderr)


class Packaging(unittest.TestCase):
    def test_metadata_and_deterministic_archive(self):
        self.assertEqual(release.metadata((SKILL / "SKILL.md").read_text())["name"], SKILL.name)
        with tempfile.TemporaryDirectory() as temp:
            one, two = Path(temp) / "one.zip", Path(temp) / "two.zip"
            digest = release.build(SKILL, one)
            self.assertEqual(digest, release.build(SKILL, two))
            self.assertTrue(release.validate(one, digest)["ready_for_submission_review"])
            self.assertFalse(release.validate(one)["ready_for_submission_review"])
            with self.assertRaises(ValueError):
                release.validate(one, "0" * 64)
            with zipfile.ZipFile(one) as archive:
                self.assertFalse(any("pro/" in n or "premium" in n for n in archive.namelist()))

    def test_reject_hostile_archives(self):
        for member in [
            "../escape.py",
            "/absolute.py",
            "C:/evil.py",
            "x\\evil.py",
            ".env",
            "x/../../evil.py",
            "__MACOSX/file.txt",
            "a//b.py",
        ]:
            with self.subTest(member=member), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "bad.zip"
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr(member, "evil")
                with self.assertRaises(ValueError):
                    release.validate(path)

    def test_symlink_and_secret_archive(self):
        for symlink in (True, False):
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "bad.zip"
                with zipfile.ZipFile(path, "w") as archive:
                    info = zipfile.ZipInfo("file.txt")
                    if symlink:
                        info.external_attr = 0o120777 << 16
                    archive.writestr(info, "../escape" if symlink else "ghp_" + "b" * 36)
                with self.assertRaises(ValueError):
                    release.validate(path)

    def test_invalid_metadata(self):
        for text in [
            "no frontmatter",
            "---\nname: Invalid\ndescription: hi\n---\n",
            "---\nname: a--b\ndescription: hi\n---\n",
            "---\nname: valid\nname: duplicate\ndescription: hi\n---\n",
        ]:
            with self.assertRaises(ValueError):
                release.metadata(text)


if __name__ == "__main__":
    unittest.main()
