"""Marketplace layout and adversarial archive regressions, using real shipped code."""

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = (
    ROOT / "free/github-ci-fixer"
    if (ROOT / "free/github-ci-fixer").is_dir()
    else ROOT / "premium/github-ci-fixer-pro"
)
spec = importlib.util.spec_from_file_location("package_gate", ROOT / "tools/build_release.py")
assert spec is not None and spec.loader is not None
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

FRONTMATTER = (
    "---\nname: example-skill\ndescription: Diagnose saved CI logs.\n---\n\n# Instructions\n"
)


class MarketplacePackaging(unittest.TestCase):
    def test_portable_path_baseline(self):
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

    def write_archive(self, directory, members):
        archive = Path(directory) / "fixture.zip"
        with warnings.catch_warnings(), zipfile.ZipFile(archive, "w") as target:
            warnings.filterwarnings("ignore", message="Duplicate name:", category=UserWarning)
            for name, data in members:
                target.writestr(name, data)
        return archive

    def valid_members(self):
        return [
            ("example-skill/SKILL.md", FRONTMATTER),
            ("example-skill/scripts/ci_fixer.py", "# Fixture: structural validation only.\n"),
        ]

    def test_final_layout_manifest_and_real_extracted_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            one, two = Path(directory) / "one.zip", Path(directory) / "two.zip"
            digest = release.build(SKILL, one)
            self.assertEqual(digest, release.build(SKILL, two))
            report = release.validate(one, digest)
            self.assertEqual(report["layout"], "skill-folder")
            self.assertEqual(report["skill_directory"], SKILL.name)
            self.assertEqual(report["marketplace_approval"], "not-requested")
            self.assertEqual(report["smoke"], "passed")
            with zipfile.ZipFile(one) as archive:
                self.assertNotIn("SKILL.md", archive.namelist())
                self.assertEqual({name.split("/")[0] for name in archive.namelist()}, {SKILL.name})
                self.assertIn(f"{SKILL.name}/SKILL.md", archive.namelist())
                self.assertEqual(report["files"], len(archive.infolist()))
                for member in report["file_manifest"]:
                    contents = archive.read(member["path"])
                    self.assertEqual(member["bytes"], len(contents))
                    self.assertEqual(member["sha256"], hashlib.sha256(contents).hexdigest())
                extracted = Path(directory) / "extracted"
                archive.extractall(extracted)
            outside = Path(directory) / "unrelated-cwd"
            outside.mkdir()
            log = outside / "unicode.log"
            log.write_bytes(
                "runner café 工具\r\nModuleNotFoundError: No module named 'buyer_dependency'\r\n".encode(
                    "utf-8"
                )
            )
            env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
            env["PYTHONIOENCODING"] = "ascii"
            cli = [sys.executable, str(extracted / SKILL.name / "scripts/ci_fixer.py")]
            result = subprocess.run(
                cli + [str(log)],
                cwd=outside,
                env=env,
                capture_output=True,
                encoding="utf-8",
                timeout=20,
                shell=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Python import failed", result.stdout)
            self.assertIn("not-run", result.stdout)
            self.assertIn("unicode.log:2", result.stdout)
            self.assertIn("工具", result.stdout)
            if SKILL.name.endswith("-pro"):
                result = subprocess.run(
                    cli + ["analyze", str(log), "--format", "json"],
                    cwd=outside,
                    env=env,
                    capture_output=True,
                    encoding="utf-8",
                    timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                analysis = json.loads(result.stdout)
                self.assertEqual(analysis["schema_version"], "1.0")
                self.assertEqual(analysis["verification"]["status"], "not-run")
                core = extracted / SKILL.name / "scripts"
                manifest = json.loads((core / "cifixer-manifest.json").read_text("utf-8"))
                for name, expected in manifest["sha256"].items():
                    self.assertEqual(
                        hashlib.sha256((core / "cifixer" / name).read_bytes()).hexdigest(),
                        expected,
                    )

    def test_flat_requires_explicit_legacy_mode_and_is_not_marketplace_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "legacy.zip"
            digest = release.build(SKILL, archive, layout="flat")
            with self.assertRaises(ValueError):
                release.validate(archive)
            report = release.validate(archive, digest, layout="flat")
            self.assertEqual(report["smoke"], "passed")
            self.assertEqual(report["marketplace_packaging"], "legacy")
            self.assertFalse(report["ready_for_submission_review"])

    def test_approval_digest_and_extraction_use_the_same_archive_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = self.write_archive(directory, self.valid_members())
            original = archive.read_bytes()
            reader = release._read_source

            def replace_after_read(path):
                contents = reader(path)
                path.write_bytes(b"Archive replaced after the approved bytes were read")
                return contents

            with patch.object(release, "_read_source", side_effect=replace_after_read):
                report = release.validate(archive)
            self.assertEqual(report["sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual(report["bytes"], len(original))
            self.assertEqual(report["structural_validation"], "passed")

    def test_wrong_folder_extra_root_file_and_double_nesting(self):
        fixtures = [
            [
                (name.replace("example-skill/", "wrong-name/"), text)
                for name, text in self.valid_members()
            ],
            self.valid_members() + [("another-skill/readme.md", "Extra skill")],
            self.valid_members() + [("README.md", "Unexpected top-level file")],
            [("outer/" + name, text) for name, text in self.valid_members()],
            self.valid_members() + [("example-skill/extra/SKILL.md", FRONTMATTER)],
        ]
        for members in fixtures:
            with self.subTest(members=members), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(ValueError):
                    release.validate(self.write_archive(directory, members))

    def test_explicit_directory_entries_are_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = self.write_archive(
                directory,
                [("example-skill/", ""), ("example-skill/scripts/", "")] + self.valid_members(),
            )
            self.assertEqual(release.validate(archive)["files"], 2)

    def test_collisions_device_names_traversal_and_special_members(self):
        additions = [
            [("example-skill/scripts/CI_FIXER.py", "Collision")],
            [("example-skill/Scripts/other.py", "Directory collision")],
            [("example-skill/CON.txt", "Windows device")],
            [("example-skill/COM¹.txt", "Windows device")],
            [("example-skill/trailing .txt ", "Nonportable")],
            [("example-skill/../escape.py", "Traversal")],
            [("example-skill/scripts//other.py", "Noncanonical")],
            [("example-skill/x.py", "File"), ("example-skill/x.py/inside.py", "Child")],
            [("example-skill/x.py/inside.py", "Child"), ("example-skill/x.py", "File")],
            [("example-skill/caf\u00e9.txt", "One"), ("example-skill/cafe\u0301.txt", "Two")],
        ]
        for extra in additions:
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(ValueError):
                    release.validate(self.write_archive(directory, self.valid_members() + extra))
        for mode in (stat.S_IFLNK, stat.S_IFIFO):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                info = zipfile.ZipInfo("example-skill/link.txt")
                info.external_attr = (mode | 0o644) << 16
                with self.assertRaises(ValueError):
                    release.validate(
                        self.write_archive(directory, self.valid_members() + [(info, "target")])
                    )

    def test_duplicate_nul_invalid_utf8_and_secret_contents(self):
        for extra in [
            [("example-skill/SKILL.md", FRONTMATTER)],
            [("example-skill/binary.txt", b"nul\0data")],
            [("example-skill/invalid.txt", b"\xff")],
            [("example-skill/token.txt", "ghp_" + "a" * 36)],
        ]:
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as directory:
                with self.assertRaises((ValueError, UnicodeError)):
                    release.validate(self.write_archive(directory, self.valid_members() + extra))

    def test_body_and_supported_yaml_scalar_validation(self):
        invalid = [
            "---\nname: example-skill\ndescription: Diagnostic\n---\n",
            FRONTMATTER.replace("Diagnose saved CI logs.", "'unterminated"),
            FRONTMATTER.replace("Diagnose saved CI logs.", '"bad\\qescape"'),
            FRONTMATTER.replace("Diagnose saved CI logs.", "plain: invalid mapping"),
            FRONTMATTER.replace("Diagnose saved CI logs.", "true"),
            FRONTMATTER.replace("Diagnose saved CI logs.", "12"),
        ]
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ValueError):
                release.metadata(text)
        quoted = FRONTMATTER.replace("Diagnose saved CI logs.", json.dumps("CI: inspect evidence."))
        self.assertEqual(release.metadata(quoted)["description"], "CI: inspect evidence.")
        single = FRONTMATTER.replace("Diagnose saved CI logs.", "'Buyer''s CI evidence.'")
        self.assertEqual(release.metadata(single)["description"], "Buyer's CI evidence.")

    def test_relative_links_cannot_escape_the_skill_folder(self):
        members = self.valid_members()
        members[0] = (members[0][0], FRONTMATTER + "[escape](../outside.md)\n")
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            release.validate(self.write_archive(directory, members))


if __name__ == "__main__":
    unittest.main()
