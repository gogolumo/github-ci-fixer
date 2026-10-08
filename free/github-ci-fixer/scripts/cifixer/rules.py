"""Signatures describe observed failures, never assert an unproved repair."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    code: str
    pattern: str
    title: str
    cause: str
    recommendation: str
    verify: str


RULES = (
    Rule(
        "python.missing-module",
        r"(?:ModuleNotFoundError: No module named|ImportError: cannot import name)",
        "Python import failed",
        "The runner cannot resolve an import; dependency, import path or version may differ.",
        "Locate the import and compare the locked dependency install and interpreter used by the failing step. Add the declared dependency only if absent; do not infer a PyPI name from an import name.",
        "Run the same interpreter's dependency installation and the failing pytest target; then rerun the affected CI job.",
    ),
    Rule(
        "python.test",
        r"(?:^FAILED\s+\S+|AssertionError\b|E\s+assert\b)",
        "Python assertion or test failed",
        "An assertion differs from expected behavior; the assertion alone does not establish which code is wrong.",
        "Inspect the failing assertion, input and expected/actual values. Reproduce the named test before changing production code or expectations.",
        "Run the named pytest test, then the affected test suite.",
    ),
    Rule(
        "node.resolve",
        r"(?:Cannot find module|Module not found:|Cannot resolve module|ERR_MODULE_NOT_FOUND)",
        "JavaScript module resolution failed",
        "A dependency or local module is absent, mis-cased or incompatible with the resolver.",
        "Determine whether the target is a package or local path. Compare package.json, lockfile, install step and filename case; use the lockfile's package manager.",
        "Run the locked install and original build/test command on the runner's OS.",
    ),
    Rule(
        "node.peer",
        r"(?:\bERESOLVE\b|unable to resolve dependency tree)",
        "npm dependency resolution failed",
        "The requested dependency versions have incompatible peer constraints.",
        "Read the conflicting peer ranges near ERESOLVE and choose mutually compatible versions. Do not disable peer checks as a blanket repair.",
        "Run npm ci from a reviewed lockfile, then the failing build/test command.",
    ),
    Rule(
        "node.lock",
        r"(?:npm ci.*(?:in sync|package-lock)|npm ERR!.*EUSAGE|Missing: .+ from lock file)",
        "npm lockfile or command mismatch",
        "npm ci requires a matching package manifest and lockfile; EUSAGE also needs its surrounding usage detail.",
        "Compare package.json with package-lock.json and the npm version. Regenerate the lockfile intentionally if stale; inspect CLI arguments for EUSAGE.",
        "Run npm ci in a clean approved environment and the failing build.",
    ),
    Rule(
        "node.typescript",
        r"(?:\berror TS\d+:|TS\d+: error)",
        "TypeScript compilation failed",
        "The compiler reports a type or configuration error at the referenced location.",
        "Inspect the TS diagnostic and referenced source line with the CI tsconfig and TypeScript version. Correct the smallest demonstrated mismatch.",
        "Run the project's typecheck/build command using the same tsconfig.",
    ),
    Rule(
        "node.test",
        r"(?:^FAIL\s+\S+|Expected:.*Received:|AssertionError \[ERR_ASSERTION\])",
        "JavaScript test failed",
        "The test runner reported an assertion or suite failure; preceding context is required.",
        "Reproduce the named test and compare its assertion output; inspect mocks, fixtures and runtime version before editing expectations.",
        "Run the selected test and affected npm test suite.",
    ),
    Rule(
        "rust.compile",
        r"(?:^error\[E\d+\]:|^error: could not compile)",
        "Rust compilation failed",
        "Cargo/rustc reports a compilation or symbol/type error.",
        "Inspect the first rustc diagnostic, source span and compiler version. Apply the smallest type/import correction supported by that diagnostic.",
        "Run cargo check and the affected cargo test target with CI's toolchain.",
    ),
    Rule(
        "dependency.install",
        r"(?:No matching distribution found|Could not find a version that satisfies|npm (?:ERR!|error) (?:E404|ETARGET)|failed to select a version for|Could not resolve dependencies)",
        "Dependency installation failed",
        "The requested package/version cannot be resolved from the configured source or constraints.",
        "Compare package/version constraints, supported runtime and configured registry. Check preceding resolver output; do not expose registry credentials.",
        "Repeat the reviewed dependency install using the same runtime and registry; then rerun the failing job.",
    ),
    Rule(
        "environment.missing",
        r"(?i)(?:(?:environment variable|env var).{0,100}(?:not set|missing|required|undefined)|(?:missing|required).{0,60}(?:environment variable|env var)|KeyError: ['\"][A-Z][A-Z0-9_]+['\"])",
        "Environment input may be missing",
        "An environment lookup failed; KeyError alone may also be an ordinary dictionary access.",
        "Inspect the named lookup and workflow env/secret binding. For fork PRs, check whether secrets are intentionally unavailable; never print values or weaken trust restrictions.",
        "Confirm presence only in an authorized context, then rerun the specific step.",
    ),
    Rule(
        "filesystem.missing",
        r"(?:FileNotFoundError|ENOENT|No such file or directory|The system cannot find the (?:file|path) specified)",
        "Required file or command path is missing",
        "The runner cannot find a requested path; checkout, working directory, casing or generated output may differ.",
        "Inspect the referenced path and step working-directory. Check checkout, generation order and exact filename case on the runner OS.",
        "Check the path exists after its producer step, then rerun the failing consumer.",
    ),
    Rule(
        "permission.denied",
        r"(?:PermissionError|Permission denied|EACCES|Access is denied|Resource not accessible by integration|HTTP 403)",
        "Access was denied",
        "Filesystem permissions or token authorization prevented the operation; surrounding context distinguishes them.",
        "For local files inspect ownership and executable bits. For GitHub access inspect event trust and the minimum required token permissions; do not grant broad write access blindly.",
        "Repeat only the denied operation with reviewed least-privilege access.",
    ),
    Rule(
        "workflow.invalid",
        r"(?:Invalid workflow file|Unrecognized named-value|Unexpected value|workflow is not valid|YAMLException|mapping values are not allowed)",
        "Workflow configuration was rejected",
        "GitHub or a YAML parser rejected a workflow value, expression or structure.",
        "Inspect the workflow file and line reported by the parser. Validate event/expression context and indentation with actionlint when installed.",
        "Run actionlint if available and validate the revised workflow with GitHub on a review branch.",
    ),
    Rule(
        "runner.command",
        r"(?:command not found|is not recognized as an internal or external command|The term .+ is not recognized)",
        "Runner command is unavailable",
        "The command is not installed/on PATH or uses syntax for a different shell.",
        "Check runs-on, step shell and setup steps. Install the intended tool through a trusted setup action or use the correct shell syntax.",
        "Check the tool's version in the intended shell, then rerun the failed command.",
    ),
)

COMPILED = tuple((rule, re.compile(rule.pattern)) for rule in RULES)
WARNING = re.compile(r"(?i)(?:^|\s)(?:warning[: ]|##\[warning\]|deprecated\b)")
EXIT = re.compile(
    r"(?:Process completed with exit code [1-9]|##\[error\].*exit code|Error: Process completed)"
)
