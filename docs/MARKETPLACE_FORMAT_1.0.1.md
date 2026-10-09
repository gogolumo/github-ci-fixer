# Marketplace archive format — final gate 1.0.1

The previous flat-ZIP recommendation is superseded by the
[packaging gate report](MARKETPLACE_PACKAGING_GATE.md).
The [creator checklist](https://www.agensi.io/learn/skill-md-creator-checklist)
(April 28, 2026) and
[security-scan guide](https://www.agensi.io/learn/how-agensi-security-scan-works)
(April 27, 2026) explicitly describe one named top-level skill folder with
SKILL.md directly inside it. The older
[seller guide](https://www.agensi.io/learn/how-to-sell-skills-on-agensi)
(March 30, 2026) requires a ZIP containing SKILL.md and supporting files without
specifying its directory level. It does not explicitly mandate a flat ZIP.
Our earlier interpretation conflicted with the more specific guidance.

Default release archives contain exactly one `github-ci-fixer/` or
`github-ci-fixer-pro/` folder, with SKILL.md, scripts, references, examples and
licenses inside. Source CLI paths remain unchanged. Extract into a parent
directory and enter the generated folder; avoid an additional wrapper.
Legacy flat archives require an explicit developer-only option and are not
eligible for the validator's submission-review status.

The 50,000,000-byte decimal size ceiling is a conservative local policy;
creator-dashboard limits remain unverified. Actual Agensi submission, scanner
acceptance, buyer-download handling and manual approval have not been tested.
Local validation prepares an archive for review and cannot certify marketplace
acceptance. See the packaging report for full manifests, extraction tests and
reproducibility limits.
