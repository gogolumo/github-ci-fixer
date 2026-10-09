# Manual Agensi publication — 1.0.1

No upload or publication has been performed. Product links remain pending.

1. Review the two hardening PRs, release report and limitations. Approve and merge each PR only after its six checks pass; merging is a separate owner action.
2. Rebuild from the approved source if any runtime/package file changes. Compare SHA-256 and file sizes with the report. Use only the versioned local ZIP; never a source-tree ZIP.
3. Sign in to Agensi and confirm creator eligibility, payout setup, current dashboard limits and purchase terms. Clarify MIT distribution of the Free edition with Agensi before listing it.
4. Create Free and Pro as separate submissions: Free $0; Pro $24.99 one-time, personal license. Use the corresponding English listing and comparison. Keep the premium ZIP private except for the intended Agensi submission.
5. Upload the correct ZIP with one named top-level skill folder and SKILL.md at that folder's root, scripts, referenced guides and licenses. Paste requirements, limitations, support contact and real generated example; do not claim autonomous repair or universal agent compatibility.
6. Review the automated scan results and complete the marketplace's manual review. Supply clarification about explicit GitHub reads and reviewed code execution if requested. Local package validation is not marketplace approval.
7. Review the buyer download in a clean directory: read metadata/licenses, run offline analysis, and confirm all runtime files are present. Do not run untrusted repository tests on your personal host.
8. Once Agensi approves and supplies actual product URLs, add those URLs to the matching public/private descriptions. Do not invent links, ratings or sales statistics.

Official guidance reviewed 2026-10-08: the
[creator checklist](https://www.agensi.io/learn/skill-md-creator-checklist) and
[scanner guide](https://www.agensi.io/learn/how-agensi-security-scan-works) require
the single named-folder layout. The older
[seller guide](https://www.agensi.io/learn/how-to-sell-skills-on-agensi) describes
submission and review without specifying SKILL.md's directory level. See the
[packaging report](../docs/MARKETPLACE_PACKAGING_GATE.md) for this correction and
local evidence, and [terms review](../docs/TERMS_ALIGNMENT_1.0.1.md) for current
buyer rights and the unresolved Free-distribution gate.

This builder validates the shipped scalar frontmatter subset, not arbitrary
third-party YAML or the marketplace scanner's undocumented behavior. Its
50,000,000-byte ceiling is a conservative local policy; the dashboard remains
authoritative for submission limits. Extract into a parent directory and enter
the generated skill folder. Actual scanner/manual review and buyer-download or
host QA remain separate from local validation; record only tests actually run.

Final gate evidence: [release decision](../docs/FINAL_RELEASE_REPORT_1.0.1.md),
[complete archive manifest](../docs/release-manifest-1.0.1.json), and
[buyer/host QA](../docs/BUYER_INSTALLATION_1.0.1.md). Local engineering checks are complete;
publication remains NO-GO until the listed external gates are cleared. Codex explicit discovery
passed; complete a second host's activation/runtime QA before marketplace release. Claude is
presently unauthenticated and unverified. Record actual scanner/manual review and buyer downloads,
then obtain owner authorization for publication. Keep the exact submitted digest in the release record.
