#!/usr/bin/env python3
"""Exercise a reviewed distribution in a fresh pip-free environment.

Only built local trusted source, or an explicitly approved archive digest, is executed.
Online collection is separate, opt-in and read-only. No agent host is invoked here.
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import venv
import zipfile
from pathlib import Path

from build_release import _read_source, build, validate


def execute(argv: list[str], cwd: Path, env: dict[str, str], timeout: int = 30) -> dict:
    result = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        capture_output=True,
        encoding="utf-8",
        timeout=timeout,
        shell=False,
        stdin=subprocess.DEVNULL,
    )
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def trusted_git_fixture(root: Path, cwd: Path, env: dict[str, str]) -> tuple[Path, dict[str, str]]:
    """Create only our fixture; user signing, templates and hooks cannot execute here."""
    executable = shutil.which("git", path=env.get("PATH"))
    require(executable is not None, "Git is required for the trusted Pro fixture")
    fixture = root / "trusted-fixture"
    (fixture / "tests").mkdir(parents=True)
    (fixture / "tests/test_value.py").write_text(
        "import unittest\nclass Demo(unittest.TestCase):\n"
        " def test_value(self): self.assertEqual(2+2,4)\n",
        encoding="utf-8",
    )
    empty = root / "empty-git-configuration"
    empty.mkdir()
    git_env = {key: value for key, value in env.items() if not key.upper().startswith("GIT_")}
    git_env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_TEMPLATE_DIR": str(empty),
        }
    )
    git_prefix = [
        str(executable),
        "-c",
        f"core.hooksPath={empty}",
        "-c",
        "commit.gpgSign=false",
        "-c",
        "tag.gpgSign=false",
        "-c",
        "core.autocrlf=false",
        "-c",
        "core.fsmonitor=false",
        "-c",
        f"core.attributesFile={os.devnull}",
        "-C",
        str(fixture),
    ]
    for arguments in (
        ["init", "-b", "main"],
        ["add", "."],
        [
            "-c",
            "user.name=BuyerSmoke",
            "-c",
            "user.email=smoke@example.invalid",
            "commit",
            "-m",
            "controlled fixture",
        ],
    ):
        outcome = execute(git_prefix + arguments, cwd, git_env)
        require(outcome["returncode"] == 0, "Could not prepare trusted Git fixture")
    return fixture, git_env


def smoke(archive: Path, digest: str, online_repo: str | None, online_run: str | None) -> dict:
    report = validate(archive, layout="skill-folder")
    require(report["sha256"] == digest, "Archive differs from approved SHA-256")
    # Use one immutable byte sequence for digest approval and subsequent extraction.
    data = _read_source(archive)
    require(hashlib.sha256(data).hexdigest() == digest, "Archive changed before buyer extraction")

    with tempfile.TemporaryDirectory(prefix="cifixer-buyer-") as temporary:
        root = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            package.extractall(root / "installed")
        skill = root / "installed" / report["skill"]
        environment = root / "clean-python"
        venv.EnvBuilder(with_pip=False, system_site_packages=False).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.upper().startswith("PYTHON") and key.upper() != "VIRTUAL_ENV"
        }
        env["PYTHONNOUSERSITE"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        cli = [str(python), str(skill / "scripts/ci_fixer.py")]
        unrelated = root / "outside-installation"
        unrelated.mkdir()
        log = unrelated / "failure.log"
        log.write_bytes(
            "runner café 工具\r\nModuleNotFoundError: No module named 'buyer_example'\r\n".encode()
        )
        offline = execute(cli + [str(log)], unrelated, env)
        require(
            offline["returncode"] == 0
            and "Python import failed" in offline["stdout"]
            and "not-run" in offline["stdout"]
            and "工具" in offline["stdout"],
            "Fresh offline CLI failed",
        )
        empty_environment = execute(
            [
                str(python),
                "-c",
                "import importlib.util; assert importlib.util.find_spec('pytest') is None; assert importlib.util.find_spec('yaml') is None; assert importlib.util.find_spec('pip') is None",
            ],
            unrelated,
            env,
        )
        require(
            empty_environment["returncode"] == 0,
            "Buyer environment unexpectedly contains development dependencies",
        )
        result = {
            "archive": report["archive"],
            "sha256": digest,
            "layout": report["layout"],
            "edition": "pro" if report["skill"].endswith("-pro") else "free",
            "environment": "fresh venv, no pip or third-party packages",
            "offline_markdown": "passed",
            "unrelated_cwd_utf8_crlf": "passed",
            "agent_host": "not-tested-by-this-tool",
            "marketplace_acceptance": "unverified",
            "trusted_fixture_execution": "not-run",
            "online_collection": "not-run",
        }
        if result["edition"] == "pro":
            analysis = execute(cli + ["analyze", str(log), "--format", "json"], unrelated, env)
            require(analysis["returncode"] == 0, "Pro offline JSON failed")
            parsed = json.loads(analysis["stdout"])
            require(
                parsed["schema_version"] == "1.0" and parsed["verification"]["status"] == "not-run",
                "Pro analysis schema/status differs",
            )
            result["offline_json"] = "passed"
            fixture, fixture_env = trusted_git_fixture(root, unrelated, env)
            planned = execute(
                cli + ["plan", "--repo-path", str(fixture), "--kind", "python-unittest"],
                unrelated,
                fixture_env,
            )
            require(planned["returncode"] == 0, "Extracted Pro plan failed")
            plan = unrelated / "reviewed-plan.json"
            plan.write_bytes(planned["stdout"].encode())
            approved = hashlib.sha256(plan.read_bytes()).hexdigest()
            declined = execute(
                cli
                + [
                    "verify",
                    "--repo-path",
                    str(fixture),
                    "--plan",
                    str(plan),
                    "--approve-plan-sha256",
                    approved,
                ],
                unrelated,
                fixture_env,
            )
            require(
                declined["returncode"] == 2,
                "Verification did not decline missing isolation acknowledgement",
            )
            verified = execute(
                cli
                + [
                    "verify",
                    "--repo-path",
                    str(fixture),
                    "--plan",
                    str(plan),
                    "--approve-plan-sha256",
                    approved,
                    "--isolation-acknowledged",
                ],
                unrelated,
                fixture_env,
            )
            require(verified["returncode"] == 0, "Extracted Pro trusted verification failed")
            check = json.loads(verified["stdout"])
            require(
                check["status"] == "passed" and not check["changes_during_check"],
                "Trusted verification status differs",
            )
            result["trusted_fixture_execution"] = "passed"
            result["missing_acknowledgement"] = "refused"
            result["verification_schema"] = check["schema_version"]
            if online_repo is not None:
                collected = execute(
                    cli
                    + [
                        "collect",
                        "--repo",
                        online_repo,
                        "--run",
                        str(online_run),
                        "--format",
                        "json",
                    ],
                    unrelated,
                    env,
                    timeout=180,
                )
                require(
                    collected["returncode"] == 0,
                    "Authorized public collection failed; inspect authentication/log availability locally",
                )
                payload = json.loads(collected["stdout"])
                require(
                    payload["context"]["repository"] == online_repo
                    and payload["context"]["run_id"] == online_run
                    and payload["verification"]["status"] == "not-run",
                    "Collection context/status differs",
                )
                result["online_collection"] = {
                    "status": "passed",
                    "repository": online_repo,
                    "run_id": online_run,
                    "commit": payload["context"]["commit"],
                    "codes": [finding["code"] for finding in payload["findings"]],
                    "workflow_count": len(payload["workflow_inspection"]),
                    "verification": "not-run",
                }
        elif online_repo is not None:
            raise ValueError("Free has no online collection")
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--archive", type=Path)
    inputs.add_argument(
        "--package-root",
        type=Path,
        help="Reviewed local source only; building executes its runtime smoke",
    )
    parser.add_argument("--approved-sha256")
    parser.add_argument("--online-repo")
    parser.add_argument("--online-run")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if (args.online_repo is None) != (args.online_run is None):
        parser.error("Online smoke requires both an authorized repository and run")
    with tempfile.TemporaryDirectory(prefix="cifixer-buyer-build-") as temporary:
        archive = args.archive
        digest = args.approved_sha256
        if args.package_root is not None:
            archive = Path(temporary) / "reviewed-distribution.zip"
            digest = build(args.package_root, archive)
        if archive is None or digest is None:
            parser.error("An existing archive requires its explicit approved SHA-256")
        result = smoke(archive, digest, args.online_repo, args.online_run)
        serialized = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
