# ADR-0001: Incremental migration into a new hexagonal core

## Status

Accepted for Phase 00; implementation begins only after Phase 00 independent Review GO.

## Context

The fork contains valuable learning material and examples but no single installable, testable or production-safe application boundary. Legacy dataframes, strategy code, accounting, vendor APIs and reporting are often directly coupled. A wholesale rewrite would discard useful evidence and make behavioral regressions difficult to identify; treating existing examples as production-ready would preserve known correctness and safety defects.

## Decision

Use an incremental strangler-style migration:

- preserve the upstream tree and Git history as reference;
- create a new **TARGET** package at `src/ai_quant_trade/`;
- implement pure domain semantics first, followed by application ports and adapters;
- migrate only selected behavior after source/commit/license recording and deterministic characterization tests;
- require backtest, paper and eventual live paths to share domain, portfolio, risk, OMS and ledger semantics;
- keep research unable to invoke broker submit/cancel operations;
- default runtime to `disabled`, then graduate through paper and shadow gates;
- deprecate legacy paths through explicit ADRs only after consumers and rollback are known.

## Alternatives considered

### Continue extending `quant_brain` in place

Rejected because current modules expose mutable pandas/global-I/O coupling and do not provide the dependency boundaries required for safe reuse.

### Rewrite the entire repository at once

Rejected because it creates an unreviewable change, loses traceability, and increases the chance of unnoticed quantitative regressions.

### Adopt Qlib or a broker SDK as the system core

Rejected because vendor/framework semantics would leak into domain and execution. They may be replaceable adapters in later phases.

## Quant/data correctness impact

The migration can establish PIT, timestamp, historical-universe, fee/rule-version and no-lookahead semantics before accepting old behavior. Existing results are not treated as comparable until a manifest and golden tests define the inputs and formulas.

## Reliability/safety impact

Direct Wind order paths stay outside the target runtime. Live submission remains fail-closed until OMS idempotency, persistence, recovery, reconciliation, risk authority, approval and kill-switch gates exist.

## Migration and rollback

- Each migrated unit records source commit/path/license, target path, semantic differences and tests.
- Legacy paths remain untouched during early migration.
- A phase can be rolled back by reverting only its new package/doc/config changes.
- No data format becomes authoritative without a versioned migration and reverse/restore procedure.

## Verification

- Dependency-boundary tests in Phase 01.
- Domain invariant/property/replay tests in Phase 02.
- PIT/no-lookahead tests in Phase 03 onward.
- Broker contract, duplicate/unknown event and reconciliation tests before any live adapter.
- Independent Review gate after every Phase.

## Consequences

- Delivery is slower than directly patching examples, but changes are smaller, attributable and reversible.
- Some functionality will temporarily exist twice as reference and target implementations.
- Existing example results are educational evidence only until revalidated through target semantics.
