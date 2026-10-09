# Marketplace packaging gate — 1.0.1

Reviewed on 2026-10-08. The local release format is `skill-folder`; real Agensi
submission, scanner results and manual approval remain **unverified**.

## Official guidance and the apparent contradiction

The [creator checklist](https://www.agensi.io/learn/skill-md-creator-checklist)
(2026-04-28) gives the most explicit ZIP layout rule: include one folder named
for the skill and place `SKILL.md` directly inside that folder.

It rejects a flat ZIP and a second nesting level. The
[security scan guide](https://www.agensi.io/learn/how-agensi-security-scan-works)
(2026-04-27) describes the same single-folder structure. The older
[seller guide](https://www.agensi.io/learn/how-to-sell-skills-on-agensi)
(2026-03-30) says to include a valid `SKILL.md` and supporting files but does not
explicitly require the file at ZIP root. Thus the seller guide is ambiguous,
while the two more specific guides agree. Our earlier flat-layout interpretation
and release report conflict with that explicit guidance; this gate corrects them.
The [Agent Skills specification](https://agentskills.io/specification) describes
a skill directory, independently of the marketplace ZIP container.

## Chosen format and buyer usage

Free has exactly one top-level folder, `github-ci-fixer/`; Pro has
`github-ci-fixer-pro/`. In each ZIP that folder contains `SKILL.md`, `README.md`,
licenses, scripts and references. The folder name must equal frontmatter `name`.
ZIP-root files, multiple skill folders, double nesting and extra `SKILL.md` files
are rejected. Conventional explicit directory entries are accepted; our builder
emits sorted file entries only.

Extract into a parent directory, then run the existing script inside the
generated skill folder. Do not first create another same-named skill folder:
that would cause double nesting. Repository-source CLI paths are unchanged.

```sh
# Free: from the repository root
python tools/build_release.py build free/github-ci-fixer release/github-ci-fixer-free-1.0.1.zip

# Pro: from the private repository root
python tools/build_release.py build premium/github-ci-fixer-pro release/github-ci-fixer-pro-1.0.1.zip
```

For legacy developer archives, both `build` and `validate` accept an explicit
`--layout flat`. Default validation rejects that layout, and flat archives never
receive `ready_for_submission_review: true`. It is not the marketplace release.

## Local validation and reproducibility

Validation bounds compressed and expanded sizes, reads regular files, rejects
unsafe or nonportable names, traversal, symlinks, special members, duplicate
members, file/directory overlaps and case or Unicode-normalization collisions.
It checks UTF-8 text, selected secret signatures, valid shipped scalar YAML
frontmatter, a nonempty instruction body, matching skill name, runtime entrypoint
and contained relative Markdown references. This is a constrained packaging
validator, not the Agensi scanner or a complete secret detector.

ZIP entries have fixed timestamps, permissions, platform metadata and sorted
ordering. Each JSON result includes archive size/SHA-256 and a complete
`file_manifest` with every file's path, byte count and SHA-256. Cross-platform
compressor implementation identity is not promised; repeat builds in the same
release environment must match exactly.

Smoke execution requires explicit approval of that exact archive digest. Hashing,
parsing and extraction use the same bounded byte snapshot, so replacing the ZIP
pathname after reading cannot substitute unapproved executable content. This
approval does not prove arbitrary code safe. The validator creates a private
temporary extraction and executes the trusted packaged CLI from an unrelated
working directory with Python environment overrides and user-site imports disabled.

Ten focused packaging tests per edition cover the chosen layout, legacy mode,
wrong nesting/name, extra folders/files, conventional directory entries, hostile
members, metadata, contained references, immutable archive approval, complete
manifests, determinism and actual extracted UTF-8/CRLF offline execution, including
Pro JSON/schema and bundled Free-core hash checks. They passed locally
on macOS with Python 3.14. CI checks the same tests in its configured OS/Python
matrix; the final release report records current-head results.

## Remaining external gate

Local structure and execution checks justify submission review only. They cannot
confirm undocumented marketplace enforcement, dangerous-command screening,
buyer fingerprinting, host discovery or manual acceptance. After owner approval,
submit these exact digest-identified archives to the real Agensi scanner and
record its result. Review scanner findings before publication. Keep Pro source,
the commercial ZIP and its submission access private.
