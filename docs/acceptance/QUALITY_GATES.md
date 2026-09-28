# Quality Gates

## Gate policy

- A command is PASS only when it was actually run with exit code 0 and its scope is stated.
- An unavailable tool or missing external prerequisite is BLOCKED/NOT CONFIGURED, never silently PASS.
- Any unresolved P0/P1 or BLOCKED critical criterion produces NO-GO.
- Tests use deterministic fixtures; CI cannot contact public providers or any broker.
- Real-order capability remains disabled until the Phase 14 controlled-release gate.

## Global gates

| ID | Capability | Criterion | Required evidence | Current baseline |
|---|---|---|---|---|
| G-01 | Repository safety | Work occurs in personal fork; canonical upstream is fetch-only/no-push | remotes, branch and SHA | PASS |
| G-02 | Reproducible install | Python 3.11 environment installs from committed lock | clean install command | FAIL |
| G-03 | Formatting/lint | Formatter check and lint finish without modifying files | CI logs | FAIL |
| G-04 | Types | Public/core API type check passes | mypy/pyright logs | NOT CONFIGURED |
| G-05 | Unit behavior | Domain/metrics/rules unit and golden tests pass | pytest report | PARTIAL: momentum only |
| G-06 | Invariants | Property tests prove cash/position conservation, idempotency and replay | seeded test report | NOT CONFIGURED |
| G-07 | PIT/no-lookahead | Future-data mutation cannot alter earlier signals/orders/fills | mutation test report | NOT CONFIGURED |
| G-08 | Integration | data → strategy → risk → order → fill → ledger deterministic path | fixture artifact checksums | NOT CONFIGURED |
| G-09 | Broker contract | All adapters satisfy states, duplicate/late/unknown and recovery cases | offline contract suite | NOT CONFIGURED |
| G-10 | Secrets/supply chain | Secret scan, dependency audit, licenses and SBOM pass/are reviewed | CI artifacts | PARTIAL |
| G-11 | Documentation | Context, ADR, schema, migration, commands and implementation agree | path/link validation + review | PASS for Phase 00 docs |
| G-12 | Live fail-closed | Missing any explicit mode/account/session/data/broker/reconciliation/approval gate prevents submit | negative tests | NOT IMPLEMENTED |

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
| P00-08 | No unsupported production/live claim is made | All Phase 00 docs | PASS |
| P00-09 | Required files exist and Markdown paths are validated or marked TARGET | Phase validation command | PASS |
| P00-10 | Independent reviewer gives GO with no P0/P1 | Independent Review Result | BLOCKED pending review |

Phase 00 implementation can be COMPLETE while the project-wide baseline remains red. Phase 01 cannot start until P00-10 is satisfied.
