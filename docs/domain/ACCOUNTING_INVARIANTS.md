# Phase 02 accounting invariants

All money is `Decimal`; floats are rejected at the accounting and JSON-decoding boundaries. Shares are nonnegative integers (not bool). CNY posting amounts and fees are rounded to cents with `ROUND_HALF_UP`; fee input is rounded once at `Fill` construction. Price must be a positive Decimal aligned to the caller-supplied tick. Price × shares, cost allocation and signed sums use a fixed precision-50 context; sign/magnitude operations use context-independent Decimal copies. A buy lot tracks its *remaining* rounded cost basis; on a partial disposal, allocated basis is rounded, while final disposal takes the exact remainder. This avoids accumulating a phantom cent.

Journal convention: debit positive, credit negative. Each funding/fill event creates one entry whose postings sum to zero. No entry is created for merely placing or acknowledging an order.

| Event | Signed postings |
|---|---|
| Funding `F` | Cash `+F`, External equity `-F` |
| Buy at rounded notional `N`, fee `C` | Cash `-(N+C)`, Inventory `+N`, Fees `+C` |
| Sell at rounded notional `N`, fee `C`, allocated basis `B` | Cash `+(N-C)`, Inventory `-B`, Fees `+C`, Realized P&L `+(B-N)` |

The aggregate refuses a buy that would make cash negative, a sell exceeding eligible lots, a sell fee exceeding proceeds, an overfill, a duplicate conflicting fill, and any event that would break a journal. A failed append leaves events, orders, lots, cash and journals unchanged. An open sell freezes its remaining quantity; UNKNOWN remains open until explicit reconciliation/status resolution. Eligible quantity comes from each lot's `sellable_from` date; the date is supplied by a separately dated execution rule, **not** calculated as a hard-coded permanent T+1 exchange rule.

The in-memory aggregate is a semantic reference, not a durable OMS or a reconciled broker account. There is no withdrawal, cash reservation for buy orders, corporate action, dividend, tax-lot election, multi-currency balance, margin, DB migration or real broker path in this phase. Before any real-order capability, later phases must add durable atomic event storage, crash recovery, broker reconciliation, dated rule/fee tables, pre-trade cash reservation and risk veto.
