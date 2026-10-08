# Product research — 2026-10-08

## Sources and findings
- [Agensi creator guide](https://www.agensi.io/learn/how-to-sell-skills-on-agensi): ZIP delivery with SKILL.md and supporting resources; automated eight-part security screening followed by manual review. Account/payout onboarding is a publication step. Local validation cannot certify marketplace acceptance.
- [Agensi Terms](https://www.agensi.io/terms), sections 5–6: permanent personal non-transferable purchase license, creator retains IP; paid listing requires an enabled payout method. $24.99 exceeds the $5 minimum. Terms govern purchases; no claim of a team redistribution license.
- [Agent Skills specification](https://agentskills.io/specification): name/description YAML metadata, names matching directories, concise entrypoints and progressive disclosure.
- [GitHub Actions docs](https://docs.github.com/en/actions) and [secure use](https://docs.github.com/en/actions/reference/security/secure-use): workflows have job/step context; logs and repository content are untrusted. Credential permissions and runner isolation matter.
- [GitHub CLI manual](https://cli.github.com/manual/) and [run view](https://cli.github.com/manual/gh_run_view): JSON run/job metadata and failed-step logs are available; unavailable logs and UNKNOWN STEP are real limitations.
- [Author account](https://github.com/gogolumo): target owner. Authenticated CLI inspection found no github-ci-fixer repository before development.

## Existing solutions
[OpenAI gh-fix-ci](https://github.com/openai/skills/tree/main/skills/.curated/gh-fix-ci) already collects failed check evidence and guides agent fixes. [actionlint](https://github.com/rhysd/actionlint) statically checks workflow syntax, expressions and shell-related issues. [SWE-agent](https://github.com/SWE-agent/SWE-agent) attempts repository repairs using language models and an execution environment. These are useful alternatives; this project does not replace their broader capabilities or copy their skill text.

## Practical scope and value
Free: deterministic saved-text log diagnostics, redacted evidence, actionable Markdown, no GitHub or paid API requirement. Pro: explicit gh collection, job-aware grouping, conservative workflow inspection, repository-grounded proposal previews, structured reports and consent-bound verification records. Full autonomous repair, full YAML interpretation, arbitrary patch generation and universal success guarantees are excluded.

The $24.99 value hypothesis is a self-contained repeatable triage and verification workflow rather than a longer prompt. Willingness to pay is unvalidated; no demand, adoption or time-saving metrics were measured. Market testing remains a launch task.

## Packaging and IP
Use SKILL.md at ZIP root, all resources bundled, deterministic archives, no symlinks/caches/secrets. Enforce a conservative 50,000,000-byte local size ceiling from the task; the researched guide/Terms do not independently state this limit. Agensi acceptance and current dashboard limits must be checked at submission.

Free and Pro live in separate source repositories. Public CI builds only Free. Pro includes a licensed copy of the Free core, not a runtime checkout dependency. Premium source, tests, packages and listing stay outside public Git history.

## License decision and trade-offs
MIT is selected for original Free code: permits redistribution and commercial reuse with attribution, maximizing usefulness but not preventing third-party paid repackaging. Apache-2.0 would add explicit patent terms and more obligations; copyleft would constrain derivative distribution. Pro uses author-retained copyright and a personal-use commercial grant aligned with Agensi purchase terms; no redistribution of premium modules. MIT notices remain for bundled Free modules. Author should review commercial terms before submission; marketplace terms prevail for purchases. These choices preserve author copyright and document the distribution trade-off before publication.
