# Risk Register

Severity uses the project P0–P3 scale. `OPEN` means mitigation is planned; `BLOCKED` means an external decision/document/environment is required; `MONITOR` means a control exists but must be rechecked. These entries describe legacy or future-phase risks, not automatically unresolved findings in the current Phase 00 change. Deferral is allowed only while the trigger is kept out of the new core, CI and live path, the owner phase and control/gate remain recorded, and the current phase's acceptance criteria are met. If current work exposes a trigger, it becomes a blocking current-phase finding. Phase 14 cannot release with unresolved P0/P1 risks.

| ID | Severity | Risk / trigger | Impact | Current evidence | Required control / gate | Owner phase | Status |
|---|---|---|---|---|---|---|---|
| R-DATA-001 | P0 | Future announcements, adjusted values or future states enter earlier queries | Lookahead and false strategy results | No shared `as_of`/availability model | PIT schemas, availability timestamps, mutation tests | 03 | OPEN |
| R-DATA-002 | P1 | Current-only listed universe is used historically | Survivorship-biased performance | Tushare selection uses `list_status="L"` | Historical symbol/status/index membership service | 03 | OPEN |
| R-DATA-003 | P1 | Mutable CSV cache is treated as authoritative without version/checksum | Non-reproducible or silently changed research | Provider example overwrites/reuses CSV by existence | Immutable raw layer, manifests, quality reports | 03 | OPEN |
| R-DATA-004 | P1 | Adjusted research price is used as executable price | Impossible fills and incorrect PnL | No shared distinction exists | Separate raw/adjusted/executable fields and golden tests | 03/05 | OPEN |
| R-METRIC-001 | P1 | Incorrect fee formulas or undated A-share fees | Materially overstated/understated net results | Legacy commission multiplies shares, not trade value | Decimal effective-dated fee engine and official-source golden tests | 05 | OPEN |
| R-METRIC-002 | P1 | Incorrect benchmark/beta/alpha/frequency conventions | Misleading risk attribution | Legacy beta denominator repeats covariance | Independent formulas, benchmark alignment and golden cases | 06 | OPEN |
| R-EXEC-001 | P0 | Duplicate submit after timeout/restart/message replay | Duplicate real orders and capital loss | Wind example calls `torder` directly; no idempotency | Durable intent, idempotency key, query-before-retry, replay tests | 10–12 | OPEN |
| R-LEDGER-001 | P0 | Local cash/position ledger drifts from broker | Incorrect exposure and unsafe subsequent orders | No append-only ledger or reconciliation gate | Event store, conservation properties, reconciliation halt | 02/10 | OPEN |
| R-RULE-001 | P0 | T+1, lot, suspension or price-limit rule omitted/wrong for date/board | Invalid fills/orders | Examples use static lot/fee assumptions and idealized open fills | Effective-dated sourced rule engine and golden tests | 05 | OPEN |
| R-RISK-001 | P0 | Strategy bypasses final risk authority or kill switch resets | Trading continues beyond limits | No common risk state machine or persistent kill switch | Central risk port, external persistent halt, negative tests | 08/10/11 | OPEN |
| R-SECRET-001 | P0 | Credentials/account identifiers are committed or logged | Account compromise | Placeholder/env patterns exist; no automated scanner/redaction | Secret manager, scanning, redaction tests, history audit | 01/13 | OPEN |
| R-BROKER-001 | P0 | Broker API/status/retry behavior is guessed | Wrong/repeated orders or unrecoverable unknown state | Broker and official docs are UNDECIDED | Fail closed; official versioned docs + authorized sandbox | 12 | BLOCKED |
| R-BROKER-002 | P0 | Existing Wind example is run as production code | Direct unguarded simulated/possible account actions | Direct login/query/order/cancel calls | Exclude from CI/runtime; replace through broker port | 10–12 | OPEN |
| R-TIME-001 | P1 | Naive/local wall-clock semantics differ across research/runtime | Session and availability errors | Existing examples use naive pandas/datetime values | Zoned clock/calendar ports and boundary tests | 02–05 | OPEN |
| R-DEP-001 | P1 | Root dependency stack cannot install or resolve consistently | Development/CI unreproducible | Root install failed on audited host | Python 3.11 compatibility ADR, `pyproject`, lock, clean CI | 01 | OPEN |
| R-PROV-001 | P1 | Third-party notebooks/data/media/snippets lack verified redistribution terms | License/compliance exposure | Only one root LICENSE; many heterogeneous assets | Per-asset provenance before migration/distribution | 00 onward | OPEN |
| R-TEST-001 | P1 | Eight example tests are mistaken for system validation | Critical defects escape to research/live | Most domains have no automated tests | Layered unit/property/golden/integration/replay/contract suite | 01 onward | OPEN |
| R-ML-001 | P1 | Test set drives parameter/model selection | Inflated OOS performance | Momentum leaderboard sorts test CAGR | Frozen OOS/walk-forward protocol and trial ledger | 07/09 | OPEN |
| R-SUPPLY-001 | P1 | Old/unpinned/inconsistent dependencies or binary assets are compromised | Build/runtime compromise | Multiple incompatible manifests; no audit/SBOM | Locked minimal groups, dependency audit, SBOM, artifact policy | 01/13 | OPEN |
| R-OPS-001 | P1 | Stale data, DB failure, disconnect or clock skew is not observable | Silent unsafe operation | No structured metrics/alerts/readiness | Observability, chaos tests and runbooks | 13/14 | OPEN |
| R-SCALE-001 | P2 | Large committed datasets/media grow clone and review cost | Slow CI/clones and provenance burden | 86.59 MiB Git pack; two CSVs near 49 MiB combined | Artifact retention/storage policy; no history rewrite without ADR | 01/13 | MONITOR |
| R-BRANCH-001 | P2 | Workflow and docs still target `master` after fork default changed to `Main` | CI/document deployment does not trigger | Docs workflow explicitly watches `master` | Align CI/default branch during Phase 01 | 01 | OPEN |

## Immediate policy

- Existing provider and broker examples are never executed by default.
- Legacy examples remain reference-only; they are not imported into the new runtime, run by CI, connected to real accounts, or presented as live-ready. A later phase must add the specified control and tests before reusing their behavior.
- Any missing broker/rule/data fact is `BLOCKED/UNRESOLVED` and fails closed.
- No current backtest or example output may be presented as investment advice, profitability evidence, or proof of live readiness.
