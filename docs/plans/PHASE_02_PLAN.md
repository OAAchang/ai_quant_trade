# Phase 02 plan — pure domain, ledger and order invariants

- Date/base: 2026-09-28; `phase-02-domain-ledger` from user-merged `origin/Main` at `8864452` (tree `16c200a9`); clean checkout.
- Gate evidence: Phase 01 independent GO and PR #2 merged by user; fetched Main tree matches the reviewed Phase 01 final tree.

## Facts, assumptions, unknowns

- Facts: Python 3.11/uv package has no production dependencies; domain is empty; tests run offline with socket denial; live mode has no implementation and fails closed.
- Assumption for this phase: one CNY cash-equity account, long-only integer shares, no margin or cross-currency accounting. A fill is authoritative only when supplied as an explicit, uniquely identified event; an order submission/ACK is not a fill.
- Unknown: provider/broker identifiers and reports, historical exchange rule tables, settlement calendar, actual tick sizes and fees. Do not infer these. Callers supply validated execution price, fee amount and lot sellable-from date; these do not become a broker adapter or trading rule.

## Scope and non-goals

- Add immutable value objects and market/research boundaries, explicit aware timestamps and versioned serialization.
- Add controlled order transitions including UNKNOWN, idempotent event/fill handling, and terminal-state rejection.
- Add an append-only in-memory event log with balanced journal entries, deterministic replay and derived snapshots. Enforce cash and sellable-lot limits; track acquisition/sellable dates and open-sell reservations.
- No provider, database, backtest engine, dated A-share rule implementation, OMS transport or live adapter. Historical reference directories remain unchanged.

## Planned changes and migration

- New modules only below `src/ai_quant_trade/domain/{accounting,orders,positions}` plus focused tests; new domain docs and ADRs. Existing Phase 01 public behavior stays intact.
- No persisted data or schema exists to migrate. Introduce schema v1 and reject other versions; future migration must be explicit. No production dependency is planned. Update quality-gate/roadmap status after verification.

## Risks and controls

- Ledger error or duplicate fill: balanced journal invariant, event/fill IDs, replay/property tests, independent review. No live path.
- Ambiguous settlement/fee/tick rule: require caller-provided values and effective dates or fail closed; never hard-code today's exchange rules.
- UNKNOWN/late reports: no blind retry or inferred fill; explicit reconciliation remains later-phase work.
- Large domain diff: split modules by accounting/orders/positions, typed APIs and behavioral tests; avoid touching upstream examples.

## Verification matrix

- Constructor and timestamp validation, decimal/quantity constraints, price and fee precision, v1 round-trip/version rejection.
- Order valid/invalid transitions, partial fill, terminal/UNKNOWN behavior, duplicate report and overfill.
- Funding, buy/sell, fee, insufficient cash, oversell, same-day unsellable, reservation/frozen amount, cancellation/rejection.
- Seeded property-style loops over cash/quantity, replay equivalence and duplicate fill idempotence; deterministic integration/minimal example.
- `make all`, `make audit` if network available, focused pytest, boundary/secret checks, diff/whitespace review and independent read-only Review.

## Rollback

- Revert the Phase 02 branch/PR only. The parent `Main` contains no domain behavior or persisted state. Never reset user changes; no live orders or external data writes are involved.
