# Target Architecture

All paths in this document marked **TARGET** are planned paths and do not exist in the audited upstream snapshot unless separately noted.

## Dependency rule

Adopt ports-and-adapters/hexagonal architecture. Dependencies point inward only:

```text
adapters / research / runtime / cli
                 │
                 ▼
             application
                 │
                 ▼
          ports + pure domain
```

- `domain` never imports pandas, database clients, networking, vendor SDKs, UI frameworks or wall-clock globals.
- `application` orchestrates use cases through ports and cannot import concrete adapters.
- `research` produces versioned signals/predictions and cannot submit or cancel broker orders.
- `runtime` invokes the same portfolio, risk, OMS and ledger semantics used by backtest and paper.
- Broker and provider SDKs exist only in adapters.

## Target package map

| Path | Responsibility | Forbidden dependencies |
|---|---|---|
| **TARGET** `src/ai_quant_trade/domain/` | Symbols, money, timestamps, signals, orders, fills, positions, ledger events and invariants | pandas, I/O, database, broker SDK |
| **TARGET** `src/ai_quant_trade/application/` | Backtest, rebalance, order-intent, reconciliation and recovery use cases | concrete adapters |
| **TARGET** `src/ai_quant_trade/ports/` | Data, calendar, clock, storage, event, broker and notification protocols | concrete providers |
| **TARGET** `src/ai_quant_trade/adapters/` | Parquet/DuckDB, database, provider, paper and eventual broker implementations | reverse imports from domain into vendor code are allowed; vendor code into domain is not |
| **TARGET** `src/ai_quant_trade/research/` | Factor, model and experiment pipelines | broker submit/cancel APIs |
| **TARGET** `src/ai_quant_trade/runtime/` | disabled/paper/shadow/live scheduling, OMS, risk and observability composition | implicit live activation |
| **TARGET** `src/ai_quant_trade/cli/` | Explicit operator commands | business rules embedded in command handlers |
| **TARGET** `tests/` | unit, property, golden, integration, replay, no-lookahead and contract tests | public data or real broker in CI |

## Canonical event flow

```text
versioned PIT data + calendar + injected clock
                    │
                    ▼
               strategy signal
                    │
                    ▼
          portfolio construction target
                    │
                    ▼
              pre-trade risk
              │ approve/reduce/reject
              ▼
           durable order intent
                    │
                    ▼
             OMS + outbox/inbox
                    │
        paper/shadow/broker adapter
                    │
                    ▼
         ack/fill/reject/unknown events
                    │
                    ▼
       append-only ledger + reconciliation
                    │
                    ▼
     positions, cash, risk, reports, alerts
```

## Core semantic boundaries

- Money/fees/ledger values use `Decimal` with explicit quantization and rounding; share quantities are integers.
- All timestamps are timezone-aware. A-share sessions use `Asia/Shanghai`; data values carry `as_of`, `effective_at`, `observed_at` or equivalent semantics.
- Research-adjusted prices and executable prices are separate types/fields.
- Rules and fees are effective-dated and source-attributed.
- Orders, broker requests and broker events have stable IDs and idempotency keys.
- Local state is reconstructable from append-only versioned events; snapshots are derived.
- Reconciliation failure, unknown order state, stale data, unhealthy broker or persistent kill switch prevents new orders.

## Storage targets

- **TARGET** immutable raw provider captures with provider/endpoint/fetched-at/checksum metadata.
- **TARGET** normalized and curated Parquet datasets queried through DuckDB for local research.
- **TARGET** SQLite for development event/state persistence and PostgreSQL-compatible migrations for runtime.
- **TARGET** manifests bind code commit, config, data versions, seed, calendar/rule versions and output checksums.

## Migration sequence

1. Phase 01 creates only the installable skeleton and enforceable dependency boundary.
2. Phase 02 establishes domain/ledger invariants independently of legacy pandas classes.
3. Phase 03 introduces PIT ports/storage before any legacy provider is accepted.
4. Phase 04 creates deterministic orchestration before A-share execution rules are attached.
5. Later phases adapt selected reference behavior behind ports and contract tests.
6. Broker-specific code remains blocked until official documentation and authorized sandbox information are supplied.

The legacy tree remains available for comparison until the new behavior is independently verified and an ADR authorizes deprecation/removal.
