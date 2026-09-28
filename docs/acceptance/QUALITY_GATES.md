# Quality Gates

## Gate policy

- A command is PASS only when it was actually run with exit code 0 and its scope is stated.
- An unavailable tool or missing external prerequisite is BLOCKED/NOT CONFIGURED, never silently PASS.
- Any unresolved P0/P1 **finding in the current phase**, or a BLOCKED critical criterion for that phase, produces NO-GO. A registered legacy/future-phase risk may be deferred only while its trigger remains isolated from the new core, CI, and live path; the risk register must name its owner phase, required control, and gate. Exposure by current work makes it a blocking finding. No unresolved P0/P1 may pass the Phase 14 release gate.
- Tests use deterministic fixtures; CI cannot contact public providers or any broker.
- Real-order capability remains disabled until the Phase 14 controlled-release gate.

## Global gates

| ID | Capability | Criterion | Required evidence | Current baseline |
|---|---|---|---|---|
| G-01 | Repository safety | Work occurs in personal fork; canonical upstream is fetch-only/no-push | remotes, branch and SHA | PASS |
| G-02 | Reproducible install | Python 3.11 environment installs from committed lock | clean install command | PASS for Phase 01 target package; legacy tree excluded |
| G-03 | Formatting/lint | Formatter check and lint finish without modifying files | CI logs | PASS locally for Phase 01 paths; GitHub run pending |
| G-04 | Types | Public/core API type check passes | mypy/pyright logs | PASS locally for Phase 01 paths; later core unimplemented |
| G-05 | Unit behavior | Domain/metrics/rules unit and golden tests pass | pytest report | PARTIAL: Phase 01 settings/logging/tooling tests pass; domain/metrics/rules absent |
| G-06 | Invariants | Property tests prove cash/position conservation, idempotency and replay | seeded test report | NOT CONFIGURED |
| G-07 | PIT/no-lookahead | Future-data mutation cannot alter earlier signals/orders/fills | mutation test report | NOT CONFIGURED |
| G-08 | Integration | data → strategy → risk → order → fill → ledger deterministic path | fixture artifact checksums | NOT CONFIGURED |
| G-09 | Broker contract | All adapters satisfy states, duplicate/late/unknown and recovery cases | offline contract suite | NOT CONFIGURED |
| G-10 | Secrets/supply chain | Secret scan, dependency audit, licenses and SBOM pass/are reviewed | CI artifacts | PARTIAL: Phase 01 pattern scan and locked audit pass; history/binary/SBOM not covered |
| G-11 | Documentation | Context, ADR, schema, migration, commands and implementation agree | path/link validation + review | Phase 00 reviewed GO; Phase 01 local docs complete, independent Review pending |
| G-12 | Live fail-closed | Missing any explicit mode/account/session/data/broker/reconciliation/approval gate prevents submit | negative tests | PARTIAL: Phase 01 rejects live and has no submit path; later system gate not implemented |

## Phase 00 acceptance

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| P00-01 | Major upstream code domains have a disposition | `docs/audit/UPSTREAM_INVENTORY.md`, `REUSE_DECISIONS.md` | PASS |
| P00-02 | Current and target architecture are factual and paths are distinguished | `docs/architecture/CURRENT_STATE.md`, `TARGET_ARCHITECTURE.md` | PASS |
| P00-03 | Migration is incremental and reversible | ADR-0001 and plan rollback section | PASS |
| P00-04 | Apache-2.0 obligations and copied-material provenance are recorded | `docs/audit/LICENSE_AND_PROVENANCE.md` | PASS |
| P00-05 | Existing tests/install/static checks have honest outcomes | `docs/audit/BASELINE_RESULTS.md` | PASS |
| P00-06 | Required risk classes are registered | `docs/risks/RISK_REGISTER.md` | PASS |
| P00-07 | No new trading behavior or directory rewrite occurred | Git diff review | PASS |
| P00-08 | No unsupported production/live claim is made | Fork-specific warnings and qualified claims in README, README_EN and docs/index; third reviewer verified | PASS |
| P00-09 | Required files exist and Markdown paths are validated or marked TARGET | Phase validation command | PASS |
| P00-10 | Independent reviewer gives GO with no current-phase P0/P1 findings | Independent Review Result in Codex task `01a0e767-887a-7e83-8ed5-3c568fd98652`; first and second reviews were NO-GO | PASS — third independent Review GO |

Phase 00 implementation can be COMPLETE while the project-wide baseline remains red. Phase 01 cannot start until P00-10 is satisfied **and** the user merges the Phase 00 PR into the personal Fork's `Main`.

## Phase 01 acceptance

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| P01-01 | Python 3.11 target package editable-installs from the committed lock in a clean environment | `uv sync --frozen --offline --group dev` into disposable environment; import and CLI smoke outside repo | PASS locally |
| P01-02 | Empty layer skeleton and documented dependency direction exist | `src/ai_quant_trade/`, `docs/architecture/DEPENDENCY_RULES.md`, `make security` | PASS locally |
| P01-03 | One documented command surface covers format, lint, typecheck, unit, integration and all | `Makefile`, `docs/development/SETUP.md`, `make all` | PASS locally |
| P01-04 | CI runs scoped checks without provider/broker tests or credentials | `.github/workflows/ci.yml`, `make workflow-check`, pytest socket denial | PASS for local structure; GitHub runner execution pending |
| P01-05 | Trading mode defaults disabled; invalid and live requests fail closed | `tests/unit/test_settings.py`, no submit path | PASS locally |
| P01-06 | Package import and CLI help work outside the repository | disposable-environment smoke and `make import-smoke` | PASS locally |
| P01-07 | Locked dependency audit and secret scan run | `make audit`, `make security` | PASS locally; scan is high-confidence/pattern-only |
| P01-08 | No trading business code or legacy migration | scoped diff review | PASS locally |
| P01-09 | Independent reviewer gives GO with no current-phase P0/P1 findings | Separate Phase 01 review task | PENDING |

Phase 01 must not progress to Phase 02 until P01-09 is PASS and the user merges its PR into the personal Fork's `Main`. The local CI-structure check is not evidence that a GitHub-hosted workflow has executed.
