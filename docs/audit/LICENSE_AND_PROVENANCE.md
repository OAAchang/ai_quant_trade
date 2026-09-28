# License and Provenance

## Upstream baseline

- Canonical source: `https://github.com/charliedream1/ai_quant_trade`.
- Audited source commit: `4e4cb796fab4fe59d7260a7654a6b902ef4d85a9`.
- Earliest repository commit observed: `d89b35000192057cc869e22d177a3afaadbbbdf6` dated 2022-06-10.
- Root license: Apache License 2.0 in `LICENSE`.
- The fork preserves Git history and the root license.
- 87 of 180 tracked Python files contain an Apache license header in their leading text. Absence of a per-file header does not by itself override the root license, but third-party origins still require verification.
- Only one tracked file named `LICENSE`, `NOTICE` or `COPYING` was found. Numerous tutorials, notebooks, datasets, images, PDFs and snippets may have separate upstream terms that are not represented by a colocated license file.

## Apache-2.0 handling

For copied or modified Apache-2.0 material:

- retain the root license and applicable copyright/attribution notices;
- mark materially modified files;
- include a copy of the license in redistributed source/object forms;
- preserve any future NOTICE contents required by upstream;
- do not imply trademark rights, warranty, profitability, or upstream endorsement.

This document is engineering provenance guidance, not legal advice. Ambiguous third-party material remains reference-only until its license is confirmed.

## Phase 00 material ledger

| Target | Source | Source identity | Modification | License/provenance status |
|---|---|---|---|---|
| `AGENTS.md` | `codex_quant_system_prompt_pack/AGENTS.md` | User-provided `codex_quant_system_prompt_pack.zip`, received 2026-09-10 | Exact copy | Source recorded; no license file present in pack; internal project use explicitly requested by repository owner |
| `docs/PROJECT_CHARTER.md` | `codex_quant_system_prompt_pack/PROJECT_CHARTER.md` | Same local prompt pack | Original copy; Phase 00 review remediation clarifies current-phase findings versus isolated legacy risks in the release principle | Same limitation as above; modification documented |
| `docs/PROJECT_CONTEXT.md` | `codex_quant_system_prompt_pack/PROJECT_CONTEXT_TEMPLATE.md` | Same local prompt pack | Filled repository, branch, OS and target-stack fields | Same limitation as above; modifications documented |
| `docs/templates/*` | `codex_quant_system_prompt_pack/templates/*` | Same local prompt pack | Exact copies | Same limitation as above |
| Phase 00 audit/architecture/risk/status documents | Generated for this fork from observed repository facts | Branch `phase-00-audit-governance` | New project documentation | Project-authored; factual sources cited by path/commit |
| `README.md`, `README_EN.md`, `docs/index.md` | Upstream files at audited commit `4e4cb796fab4fe59d7260a7654a6b902ef4d85a9` | Apache-2.0 fork history | Phase 00 review remediation adds prominent fork-specific safety status and qualifies historical claims; tutorials remain as upstream reference | Root license and upstream history retained |

Before public redistribution of prompt-pack text outside this repository workflow, the owner should confirm its license. No assumption is made that the prompt pack is covered by the upstream repository's Apache-2.0 license.

## Future provenance record

Use this table in the responsible ADR or status report for each migrated unit:

| Field | Required value |
|---|---|
| Source repository | Canonical URL |
| Source commit | Immutable full SHA |
| Source path | Exact path(s) |
| Source license | SPDX identifier and notice path |
| Target path | Exact repository path |
| Modification summary | Behavioral and structural changes |
| Correctness impact | PIT/time/money/rule/execution implications |
| Verification | Deterministic command and artifact |
| Responsible Phase/ADR | Identifier |
| Rollback | Revert/removal method |

## Current disposition

- Existing upstream tree remains intact and attributed by history.
- Phase 00 copies no upstream runtime source into `src/ai_quant_trade/`.
- Candidate behavior is classified in `docs/audit/REUSE_DECISIONS.md`.
- Third-party-origin uncertainty is tracked as `R-PROV-001` in the risk register and fails closed for migration.
