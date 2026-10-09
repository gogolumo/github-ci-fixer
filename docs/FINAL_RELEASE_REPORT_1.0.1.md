# Final release gate — GitHub CI Fixer Free 1.0.1

Release review date: 2026-10-09. **Engineering decision: GO for owner review.**
Validated code, packaging and clean-installation checks passed, including six OS/Python CI jobs.
**Marketplace publication: NO-GO** until the external gates below are complete.
Neither PR has been merged; no Agensi submission/publication has occurred.

## Final distribution and reproducibility

- Local archive: `release/github-ci-fixer-free-1.0.1.zip`
- Exact size: **19295 bytes**; **16 regular files**.
- SHA-256: `1976d03aa094eee7c65c741c2b84e03a4487e17cfc3d707bc45c68bf9defadac`
- Exactly one named top-level folder, `github-ci-fixer/`, with SKILL.md directly inside.
- Repeat build on the release host produced byte-identical output. Timestamps, order, permissions
  and ZIP platform metadata are fixed; identity across other compressor implementations is not promised.
- [Complete file manifest](release-manifest-1.0.1.json): every contained path, size and SHA-256.

The [packaging report](MARKETPLACE_PACKAGING_GATE.md) explains the correction from the previous
flat layout: the creator checklist and scanner guide explicitly require a skill folder; the older
seller guide is ambiguous and never explicitly mandates flat layout. Unsafe paths, duplicate/colliding
names, symlinks, special files, malformed metadata and wrong nesting are rejected. Digest approval,
parsing and extraction use the same immutable bounded bytes. Actual extracted CLI execution passed.
This validator is not the real marketplace scanner or a complete secret detector.

## Test and installation evidence

- Local macOS arm64 / Python 3.14.6: **38 unittest methods**; 38 passed, none skipped.
- Ruff lint/format, mypy, compileall, skill metadata and deterministic packaging checks passed.
- Ten focused packaging methods per edition include real extraction, Unicode/CRLF, unrelated-CWD
  CLI execution, hostile archive paths, explicit legacy layout and immutable digest approval.
- [Buyer/host QA](BUYER_INSTALLATION_1.0.1.md): final exact-digest archive passed in a fresh Python
  environment without pip or third-party packages; Codex CLI 0.160.0 discovered the installed skill
  in a fresh project's `.agents/skills` and ran only offline analysis, preserving `not-run` status.
- Claude Code 2.1.288 has no active authentication; its discovery/runtime test is **unverified**.
  Other hosts and real Agensi buyer downloads are **unverified**.
- CI matrix: Ubuntu/macOS/Windows × Python 3.11/3.14, including offline fresh buyer smoke and
  independent-case replay: **6/6 successful** in [run 37895364969](https://github.com/gogolumo/github-ci-fixer/actions/runs/37895364969) at
  source head `7a8991f17e83b5e876f20042f36c98b832ffd374`. [Machine receipt](ci-evidence-1.0.1.json) records all jobs/steps.
  This receipt precedes the documentation commit recording it. That final documentation head is
  checked again before delivery; live status is [PR #2 checks](https://github.com/gogolumo/github-ci-fixer/pull/2/checks),
  and its exact receipt is local at `release/qa/ci-current-head-1.0.1.json`.

The original 37 controlled synthetic cases matched; this is regression matching, not field accuracy.
Public-boundary audit passed. Free analysis performs no repository execution or network access.

## Independent diagnostic evidence

[Seven new cases from six failed runs](INDEPENDENT_EVALUATION_1.0.1.md) were recorded against frozen
diagnostic sources before invoking the analyzers. Both editions classified only the supported
pytest assertion as `python.test`; five identifiable failures remained unsupported and one aggregate-only
input remained unknown. No false-positive category appeared in these excerpts or complete logs.
Fourteen two-edition replay checks matched, including deliberately empty outcomes; this is neither
an accuracy percentage nor successful CI repair evidence. Unsupported signatures may still receive
generic advice asking for complete logs, and one policy failure is not retained as an error row.
The earlier real-world dataset informed rules and remains design/regression evidence.

## Limits and privacy

Supported signatures identify observed errors, not unique proven root causes. Analysis does not apply
changes, run tests or prove a repair. Unknown/truncated logs need evidence; unsupported complete logs
may need manual reasoning. Output redaction is best effort and personal/source fragments may remain.
The AI host has separate data/network policies. Review reports before sharing. Pro's separate
execution capability remains opt-in and is not a sandbox or complete environment-integrity proof.
No commercial source or archive is included in this public repository or its Actions artifacts.

## External publication gates and owner actions

1. Confirm both PR #2 current-head matrices are green, then obtain explicit owner approval for each
   merge. This task does not merge them or authorize publication.
2. Complete the real Agensi automated scanner and manual review for these exact archive digests.
   No marketplace acceptance or security certification is claimed.
3. Complete a second Agent Skills host test and actual marketplace buyer-download QA; Claude is
   presently unverified because authentication is absent. Universal host compatibility is unclaimed.
4. Recheck creator-dashboard limits/current terms and clarify MIT distribution of the Free edition
   with Agensi. [Terms alignment](TERMS_ALIGNMENT_1.0.1.md) preserves Pro marketplace/statutory
   refunds and access to published updates; it does not promise future development or a support SLA.
5. Follow the [manual launch checklist](../marketing/LAUNCH_CHECKLIST.md). Keep Pro private and upload
   it only to the intended marketplace after authorization. Product links, sales and ratings remain pending.

The local 50,000,000-byte limit is a conservative packaging policy, not a confirmed Agensi limit.
Listings avoid universal root-cause and automatic-repair claims. Remaining coverage, isolation,
redaction, host and marketplace limits are explicit; no real CI repair was attempted.
