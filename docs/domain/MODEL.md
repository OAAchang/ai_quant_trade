# Phase 02 domain model

The new package remains a pure Python domain. It does not read a provider, call a broker, persist a database, run a backtest or submit an order. Historical examples remain reference-only.

## Objects and time

| Group | Objects | Boundary |
|---|---|---|
| Identity | `Symbol`, `Exchange`, `Board`, `Currency`, `Side` | Explicit values; no ticker-to-board inference |
| Market/research | `Bar`, `Quote`, `Signal`, `TargetPosition` | `Bar` declares RAW versus RESEARCH_ADJUSTED; `Quote` is raw; signal `effective_at >= observed_at >= as_of` |
| Orders | `OrderIntent`, `Order`, `Fill` | Intent is not broker submission; ACK is not execution; fill is an explicit report |
| Position | `PositionLot`, `Position` | Acquisition instant and caller-provided `sellable_from` date; integer shares; open sells reserve remaining shares |
| Account | `CashBalance`, `AccountSnapshot`, `PortfolioSnapshot` | Derived from events; no inferred market value or broker balance |

All datetime fields require a real UTC offset. The account event log is ordered by `observed_at`; snapshots cannot claim an `as_of` earlier than the latest event. Execution instants are additionally monotonic. `Asia/Shanghai` is used only to interpret session dates. The domain does **not** calculate trading days or assert that an observed/executed instant falls inside a session. A delayed or contradictory report fails closed for reconciliation rather than being silently reordered.

`OrderIntent` requires an explicit tick size and limit price. `Fill` requires a Decimal price and fee, integer quantity, stable fill/order IDs and distinct execution/observation times. A buy fill requires a caller-supplied `sellable_from` date; the actual historical settlement rule belongs to a later dated-rules phase. This date may not precede the acquisition date in Shanghai time. No share-lot size, tick table or fee rate is invented here.

`OrderPlaced.observed_at` is the **local placement instant**. `OrderStatusRecorded` with `SUBMITTED` is the **local request-dispatch event**; its `observed_at` is dispatch time, not a delayed broker ACK. Other status events carry their observed report time. The aggregate stamps `Order.placed_at` and `submitted_at` and refuses a fill executed before either. A late ACK observation is not used as the execution lower bound. If a later adapter cannot prove local dispatch time, it must fail closed rather than fabricate one.

## State and replay

`Account.append` atomically accepts `FundingRecorded`, `OrderPlaced`, `OrderStatusRecorded` and `FillRecorded`. Event IDs and fill IDs are idempotency keys. Identical replay is a no-op; an ID collision with different payload is rejected. A repeated status with a *new* event ID is treated as a distinct report and must obey the state machine. A network timeout or UNKNOWN status does not authorize resubmission; open UNKNOWN sells retain reservations. Terminal orders cannot be resurrected by a later fill. Late fills after terminal status require external reconciliation in a future phase.

`Account.replay(account.events)` reconstructs orders, cash, lots and journals. `snapshot(as_of)` derives positions and frozen sell shares; it is not an authoritative ledger. Buy cash is checked on fill but **not** reserved at order placement. Two pending buy intents can therefore exceed available cash; the later fill fails closed. This domain behavior is not an OMS pre-trade risk control, and no live path exists.

## Schema and compatibility

`to_json` / `from_json` encode whitelisted domain objects using `schema = "ai_quant_trade.domain"` and integer `version = 1`. Decimal values are strings, dates/datetimes are ISO-8601, and controlled enums are tagged. Unknown versions/types/fields fail closed. There is no persisted v0 state or automatic migration. Event streams can be serialized event-by-event and replayed after decoding; durable storage and crash recovery are later-phase responsibilities.

## Minimal deterministic use

`tests/unit/test_domain_ledger.py::test_buy_sell_fee_journals_and_replay` is the offline minimal example: explicit funding → buy order/report/fill → same-day sell denial → next-day sell/report/fill → balanced journals → same snapshot from replay. It uses invented fixtures, not historical market data or trading-rule claims.
