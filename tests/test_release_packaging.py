"""Portable archives and extracted, unrelated-directory runtime checks."""

import hashlib
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
SKILL = next(
    p for p in (ROOT / "free/github-ci-fixer", ROOT / "premium/github-ci-fixer-pro") if p.is_dir()
)
SPEC = importlib.util.spec_from_file_location("package_validation", ROOT / "tools/build_release.py")
assert SPEC is not None and SPEC.loader is not None
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleasePackaging(unittest.TestCase):
    def test_portable_paths_and_case_collisions(self):
        for name in [
            "../x.py",
            "/x.py",
            "x\\y.py",
            "CON.txt",
            "aux.log",
            "x./a.py",
            ".hidden/a.py",
            "x:a.py",
            "x /a.py",
        ]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                release.portable_name(name)
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "collision.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("A.py", "pass")
                z.writestr("a.py", "pass")
            with self.assertRaises(ValueError):
                release.validate(archive)

    def test_reproducible_extraction_crlf_utf8_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, second = root / "first.zip", root / "second.zip"
            digest = release.build(SKILL, first)
            self.assertEqual(digest, release.build(SKILL, second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(release.metadata((SKILL / "SKILL.md").read_text())["name"], SKILL.name)
            self.assertEqual(release.validate(first, digest)["smoke"], "passed")
            extracted, elsewhere = root / "installed", root / "elsewhere"
            extracted.mkdir()
            elsewhere.mkdir()
            with zipfile.ZipFile(first) as z:
                z.extractall(extracted)
            log = elsewhere / "unicode.log"
            log.write_bytes(
                "runner café 工具\r\nModuleNotFoundError: No module named 'example_dependency'\r\n".encode()
            )
            cli = [sys.executable, str(extracted / "scripts/ci_fixer.py")]
            env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
            env["PYTHONIOENCODING"] = "ascii"
            result = subprocess.run(
                cli + [str(log)], cwd=elsewhere, env=env, capture_output=True, text=True, timeout=20
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Python import failed", result.stdout)
            self.assertIn("not-run", result.stdout)
            self.assertIn("unicode.log:2", result.stdout)
            self.assertIn("工具", result.stdout)
            if SKILL.name.endswith("-pro"):
                result = subprocess.run(
                    cli + ["analyze", str(log), "--format", "json"],
                    cwd=elsewhere,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["schema_version"], "1.0")
                self.assertEqual(report["verification"]["status"], "not-run")
                manifest = json.loads((extracted / "scripts/cifixer-manifest.json").read_text())
                for name, expected in manifest["sha256"].items():
                    self.assertEqual(
                        hashlib.sha256(
                            (extracted / "scripts/cifixer" / name).read_bytes()
                        ).hexdigest(),
                        expected,
                    )


if __name__ == "__main__":
    unittest.main()
