# Current-State Architecture

## Summary

The audited repository is a broad learning/example collection, not one installable trading application. Its executable paths are organized by topic and vendor rather than by stable domain/application/port boundaries.

```text
README/tutorials
  ├── egs_data/* ───────────────► public/vendor APIs ─► CSV/console
  ├── egs_trade/vanilla/* ──────► pandas backtests ───► CSV/PNG reports
  ├── egs_trade/ms_qlib/* ──────► Qlib tutorials
  ├── egs_trade/rl/* ───────────► Gym/FinRL examples + bundled CSV
  └── egs_trade/paper_trade/wind
          └─────────────────────► WindPy account/order APIs

quant_brain/* and tools/* are imported directly by selected examples.
There is no shared event ledger, OMS, risk authority, provider contract,
broker contract, configuration boundary, or installable application runtime.
```

## Packaging and dependency state

- No `pyproject.toml`, package metadata, lock file or standard build command exists.
- Both `quant_brain/` and `tools/` are importable only because the repository root is placed on `sys.path` or the process starts in a specific directory.
- `src/tools/` overlaps the root `tools/` namespace without a documented ownership boundary.
- Root dependencies target Python 3.8-era libraries; example-specific requirements include incompatible modern and GPU stacks.
- The only CI workflow builds MkDocs and still triggers on `master`, while the fork default is `Main`.

## Data flow

- Provider clients return pandas frames directly to scripts.
- Local caches are mutable CSV files, often selected merely because a path exists.
- Dataset provenance, schema version, fetch time, field mapping and quality result are not recorded in a run manifest.
- Tushare universe construction requests currently listed securities only.
- Corporate actions, fundamental announcement availability, revisions, historical index membership and point-in-time queries have no shared model.

## Research and backtest flow

- The legacy double-MA path combines data preparation, signal, portfolio sizing, accounting, fees, metrics and reporting through mutable objects/dataframes.
- The newer momentum example uses previous-day target selection and next-open execution, but current-open order sizing reads that same day's final close through `_mark_to_market()` / `_position_value()`. This is a lookahead defect, despite eight local-fixture tests. It remains a monolithic example with float accounting and idealized fills.
- Multiple metric implementations exist with different conventions. The legacy beta implementation is demonstrably incorrect, and no golden formula suite establishes authoritative behavior.
- Parameter ranking uses test-period CAGR in the current example flow, so it is not an unbiased final out-of-sample protocol.

## Execution and reliability flow

- Wind paper scripts import `WindPy` directly and issue account/order/cancel calls from the strategy/runtime script.
- Orders are treated as API call responses rather than persistent intents and broker event state machines.
- There is no idempotency, event replay, restart recovery, reconciliation gate, account whitelist, persistent kill switch or explicit disabled/paper/live settings model.
- Logging is plaintext/config-file based rather than structured, correlated and redacted.

## Test and delivery state

- The selected baseline covers the momentum example with eight local-fixture tests; they do not cover the same-day-close order-sizing leak.
- Separate test trees exist under `egs_aide/看盘神器/v2/tests/` (11 modules, 156 test functions) and `egs_skill/broker-research-analyst/tests/` (four test functions). They were not run in the Phase 00 baseline; the broker-research tree contains an unguarded pytest-collected Eastmoney network test. Default CI must use an explicit offline test scope.
- No behavioral tests cover legacy accounting, fee rules, metrics, T+1, suspensions, limits, partial fills, duplicate messages, reconciliation, or recovery.
- Static analysis currently reports 24 findings in the selected core/example/test paths.
- No type checker, coverage threshold, migration framework, secret scanner, dependency audit or software bill of materials is configured.

## Trust boundary

Everything in the upstream snapshot is reference material unless explicitly accepted through a later Phase gate. In particular, examples named “paper,” “real,” “risk,” or “backtest” are not production-trust signals.
