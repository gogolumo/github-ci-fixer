# Manual Agensi publication — 1.0.1

No upload or publication has been performed. Product links remain pending.

1. Review the two hardening PRs, release report and limitations. Approve and merge each PR only after its six checks pass; merging is a separate owner action.
2. Rebuild from the approved source if any runtime/package file changes. Compare SHA-256 and file sizes with the report. Use only the versioned local ZIP; never a source-tree ZIP.
3. Sign in to Agensi and confirm creator eligibility, payout setup, current dashboard limits and purchase terms.
4. Create Free and Pro as separate submissions: Free $0; Pro $24.99 one-time, personal license. Use the corresponding English listing and comparison. Keep the premium ZIP private except for the intended Agensi submission.
5. Upload the correct ZIP with SKILL.md at root, scripts, referenced guides and licenses. Paste requirements, limitations, support contact and real generated example; do not claim autonomous repair or universal agent compatibility.
6. Review the automated scan results and complete the marketplace's manual review. Supply clarification about explicit GitHub reads and reviewed code execution if requested. Local package validation is not marketplace approval.
7. Review the buyer download in a clean directory: read metadata/licenses, run offline analysis, and confirm all runtime files are present. Do not run untrusted repository tests on your personal host.
8. Once Agensi approves and supplies actual product URLs, add those URLs to the matching public/private descriptions. Do not invent links, ratings or sales statistics.

Official requirements checked 2026-10-08: [seller guide](https://www.agensi.io/learn/how-to-sell-skills-on-agensi) requires a ZIP containing valid SKILL.md and supporting files, followed by automated and manual review. [Agent Skills specification](https://agentskills.io/specification) defines name/description and directory conventions. This builder validates the shipped flat frontmatter subset, not arbitrary third-party YAML. Its 50,000,000-byte ceiling is a conservative local policy; the public guide does not state an upload ceiling. The dashboard remains authoritative for submission limits. Agensi terms page could not be fetched during this audit; review current terms before submission. Existing licenses were preserved.
