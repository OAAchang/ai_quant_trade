# Phase 02 status — domain, ledger and state invariants

## Status

COMPLETE for implementation and independent Review — first Review returned NO-GO (F-01/F-02 P0, F-03 P1, F-04/F-05 P2); follow-up Review closed F-01–F-05 and returned GO; final narrow Review closed F-06 P2 and confirmed GO. No Phase 03 work, commit, push, PR or merge has occurred in this phase. Publication and user merge remain separate gates.

## Scope completed

- Pure domain identity, timestamped market/research records, order intent/report/state, lot/position and account snapshots.
- Controlled order transitions including UNKNOWN, partial fills, terminal rejection, conservative sell reservations, explicit rejection reasons and placement/dispatch execution-causality checks.
- Append-only in-memory account events, balanced journals, atomic append, event/fill ID deduplication, deterministic replay and schema-v1 JSON round trips.
- Decimal/CNY cents and integer-share boundaries, caller-supplied tick/fee/sellable date, fixed arithmetic context and partial-lot cost-basis remainder handling.
- Model/accounting docs and ADR-0003/0004/0005. No broker, external market data or live path.

## Files changed

- Added: `src/ai_quant_trade/domain/types.py`, `market.py`, `orders/`, `positions/`, `accounting/`, `serialization.py`; `tests/unit/test_domain_models.py`, `test_domain_ledger.py`; `docs/domain/MODEL.md`, `ACCOUNTING_INVARIANTS.md`; ADR-0003/0004/0005; `docs/plans/PHASE_02_PLAN.md`; this report.
- Modified: roadmap and quality-gate tracking (`PLANS.md`, `docs/acceptance/QUALITY_GATES.md`).
- Deleted: none. Legacy/upstream reference tree unchanged.

## Design decisions

- ADR-0003: Decimal, half-up CNY-cent postings, explicit tick/fee and deterministic arithmetic.
- ADR-0004: event source of truth with balanced derived journals and replay; no durability claim.
- ADR-0005: ACK is not fill, UNKNOWN retains uncertainty and sell reservation, terminal/late contradictions fail closed.
- No dependency or lock change. No persisted schema exists to migrate. v1 decoder rejects unknown versions.

## Commands actually run

| Command | Exit | Result |
|---|---:|---|
| `git fetch origin Main` and tree comparison | 0 | User-merged PR #2 Main tree `16c200a9` equals Phase 01 final local tree. |
| `uv run --frozen --offline --group dev pytest tests/unit/test_domain_models.py tests/unit/test_domain_ledger.py -q` | 0 | 30 focused tests passed at the time run. |
| First `make all` | 2 | Ruff import order check failed; sorted imports. |
| Second `make all` | 2 | Existing boundary checker rejected `__future__` imports in new domain code; removed those imports. |
| Third `make all` | 2 | 53 tests passed but branch coverage 83.00% below 90%; expanded negative/property tests. |
| Pre-review `make all` | 0 | Unit 60/60, integration 2/2, branch coverage 94.27%; independent reviewer reran and reproduced five findings outside existing tests. |
| Post-repair `make all` | 0 | Formatter/lint/mypy pass (34 files); unit 65/65, integration 2/2, combined 67/67, branch coverage 93.44%; import/CLI, workflow, lock, secret, boundary and distribution checks passed. |
| `make audit` before and after repair | 0 both | No known vulnerabilities reported for locked dev dependencies at check time. |
| Post-F-06 `make all` | 0 | Unit 66/66, integration 2/2, combined 68/68, branch coverage 93.51%; all other checks passed. |
| Post-F-06 `make audit` | 0 | No known vulnerabilities reported at check time. |
| Independent full re-review and narrow F-06 re-review | GO both | Reviewer independently reran `make all`/`make audit`, original F-01–F-06 cases and 40 additional generated multi-lot cases; no open finding. |

The expected `pytest-socket` warning comes from the negative test that verifies sockets are blocked. It is not a successful network call.

## Acceptance matrix

| Criterion | Result | Evidence |
|---|---|---|
| Pure domain boundary; no pandas/DB/network/broker/UI imports | PASS locally | `make security`, import-boundary AST check and package diff |
| Required identity, market, order, lot, cash and snapshot objects | PASS locally | `src/ai_quant_trade/domain/`, constructor and behavior tests |
| Aware time, PIT/observation/effect semantics | PASS locally | timestamp validation tests; `docs/domain/MODEL.md` |
| Decimal, integer shares, explicit tick/fee rounding | PASS locally after repair | JSON-number rejection, low-precision signed-posting and cent-allocation tests |
| Append-only event/journal, balanced accounting and replay | PASS locally after repair | generated conservation/replay, cross-lot and replay-journal tests |
| UNKNOWN/timeout uncertainty and legal order transitions | PASS locally | transition, duplicate/partial/terminal tests and ADR-0005 |
| T+1-relevant acquisition/sellable/frozen quantities | PASS locally | same-day denial, next-day sale and reservation tests; no hard-coded calendar |
| Duplicate fill prevention, cash/position fail-closed | PASS locally | duplicate/collision, insufficient cash, oversell tests |
| Schema/versioned serialization and rejection | PASS locally after repair | round-trip, malformed, numeric Decimal tag and version tests |
| Minimum reproducible example | PASS locally | `test_buy_sell_fee_journals_and_replay` within offline pytest |
| Independent no-P0/P1 Review GO | PASS | Independent follow-up GO closed F-01–F-05; final narrow GO closed F-06; no open finding |

## Risks and limitations

- The aggregate is in-memory only. There is no durable event store, process crash recovery, broker reconciliation, pre-trade buy-cash reservation or account white-list. It cannot be used for real orders; Phase 10+ owns those controls.
- Fee/tick/sellable date are supplied, not verified against historical exchange rules. Phase 05 must provide dated rules and golden fixtures. A syntactically valid but historically wrong input would remain wrong.
- The deterministic generated property suite uses a fixed-seed Python generator (80 cases) without a shrinking engine. Cross-lot, low-precision, decoding and causal-time regression tests supplement it; this is not exhaustive proof.
- Unknown/late/contradictory execution reports fail closed; reconciliation handling is deferred. No promise of profitability or real-trading readiness is made.

## Review findings disposition

Independent Review task `01a0e89c-77af-7c11-adb3-a5e249ef445b` first returned NO-GO with F-01/F-02 P0, F-03 P1, F-04/F-05 P2. F-01 repaired by context-independent sign/magnitude operations and replay-journal regression; F-02 by strict string-only Decimal tags; F-03 by stamped placement/local-dispatch instants and pre-dispatch fill rejection; F-04 by nested type/rejection constructor checks; F-05 by tuple-only immutable container checks. Follow-up Review returned GO, closed all five, and independently ran 40 additional seeded multi-lot/partial-sale cases across Decimal precisions 2/4/7/28. It found F-06 P2: `OrderStatusRecorded` accepted an invalid rejection reason at construction/decoding, though the aggregate rejected it. Constructor checks and a JSON negative test repaired F-06; final narrow read-only Review independently reproduced the original case, reran checks and confirmed **F-06 CLOSED / GO**. All six reported findings are closed; no current P0/P1 remains.

## Out-of-scope confirmed

No行情下载、回测事件循环、具体涨跌停/费用历史规则、数据库、真实 broker adapter、Phase 03 or live trading behavior.

## Next action

The user authorized committing, pushing and opening a Phase 02 PR on 2026-09-29. Publish the reviewed branch against the personal Fork's `Main`; do not auto-merge. After any user merge, verify the actual Main tree before Phase 03.
