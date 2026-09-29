"""Deterministic ledger properties, negative paths and replay."""

import json
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from random import Random
from zoneinfo import ZoneInfo

import pytest

from ai_quant_trade.domain.accounting import (
    Account,
    AccountSnapshot,
    CashBalance,
    FillRecorded,
    FundingRecorded,
    JournalEntry,
    OrderPlaced,
    OrderStatusRecorded,
    PortfolioSnapshot,
    Posting,
)
from ai_quant_trade.domain.accounting.ledger import LedgerAccount
from ai_quant_trade.domain.orders import Fill, Order, OrderIntent
from ai_quant_trade.domain.serialization import from_json, to_json
from ai_quant_trade.domain.types import (
    Board,
    DomainError,
    Exchange,
    OrderStatus,
    RejectReason,
    Side,
    Symbol,
)

TZ = ZoneInfo("Asia/Shanghai")
DAY1 = datetime(2026, 1, 2, 10, tzinfo=TZ)
DAY2 = datetime(2026, 1, 3, 10, tzinfo=TZ)
S = Symbol("600000", Exchange.SSE, Board.MAIN)
D = Decimal
DEFAULT_FUNDING = D("1000.00")
DEFAULT_BUY_PRICE = D("10.00")
DEFAULT_BUY_FEE = D("1.00")
DEFAULT_SELL_PRICE = D("12.00")
DEFAULT_SELL_FEE = D("0.50")


def order(order_id: str, side: Side, qty: int, price: Decimal, at: datetime) -> Order:
    """Produce one unique order, with explicit tick and timestamps."""
    return Order(
        order_id,
        OrderIntent(
            order_id + "-intent", order_id + "-key", S, side, qty, price, D("0.01"), at, at
        ),
    )


def funded_account(amount: Decimal = DEFAULT_FUNDING) -> Account:
    """Create an account whose cash provenance is an explicit funding event."""
    account = Account()
    account.append(FundingRecorded("fund", amount, DAY1))
    return account


def buy(
    account: Account,
    qty: int = 5,
    price: Decimal = DEFAULT_BUY_PRICE,
    fee: Decimal = DEFAULT_BUY_FEE,
) -> FillRecorded:
    """Place, submit and fill an order on day one."""
    account.append(OrderPlaced("place-buy", order("buy", Side.BUY, qty, price, DAY1), DAY1))
    account.append(
        OrderStatusRecorded("submit-buy", "buy", OrderStatus.SUBMITTED, DAY1 + timedelta(minutes=1))
    )
    at = DAY1 + timedelta(minutes=2)
    event = FillRecorded(
        "fill-buy", Fill("fb", "buy", S, Side.BUY, qty, price, fee, at, at, date(2026, 1, 3)), at
    )
    account.append(event)
    return event


def sell(
    account: Account,
    qty: int = 2,
    price: Decimal = DEFAULT_SELL_PRICE,
    fee: Decimal = DEFAULT_SELL_FEE,
) -> FillRecorded:
    """Place, submit and fill a sell order after explicit lot release date."""
    account.append(OrderPlaced("place-sell", order("sell", Side.SELL, qty, price, DAY2), DAY2))
    account.append(
        OrderStatusRecorded(
            "submit-sell", "sell", OrderStatus.SUBMITTED, DAY2 + timedelta(minutes=1)
        )
    )
    at = DAY2 + timedelta(minutes=2)
    event = FillRecorded("fill-sell", Fill("fs", "sell", S, Side.SELL, qty, price, fee, at, at), at)
    account.append(event)
    return event


def test_buy_sell_fee_journals_and_replay() -> None:
    account = funded_account()
    buy_event = buy(account)
    assert account.snapshot(DAY1 + timedelta(minutes=2)).cash.total == D("949.00")
    assert account.snapshot(DAY1 + timedelta(minutes=2)).positions[0].quantity == 5
    with pytest.raises(DomainError, match="sellable"):
        account.append(
            OrderPlaced(
                "bad-same-day",
                order("same", Side.SELL, 1, D("12"), DAY1 + timedelta(minutes=3)),
                DAY1 + timedelta(minutes=3),
            )
        )
    assert account.events[-1] == buy_event  # failed append is atomic
    sell(account)
    snap = account.snapshot(DAY2 + timedelta(minutes=2))
    assert snap.cash.total == D("972.50")
    assert snap.positions[0].quantity == 3
    assert snap.positions[0].lots[0].cost_basis == D("30.00")
    assert snap.orders[-1].status is OrderStatus.FILLED
    assert Account.replay(account.events).snapshot(snap.as_of) == snap
    assert all(sum((p.amount for p in j.postings), D("0")) == 0 for j in account.journals)
    assert all(from_json(to_json(event)) == event for event in account.events)
    assert from_json(to_json(snap)) == snap


def test_duplicate_event_and_fill_idempotent_but_collision_rejected() -> None:
    account = funded_account()
    event = buy(account)
    before = account.snapshot(DAY1 + timedelta(minutes=2))
    assert account.append(event) is False
    duplicate_report = FillRecorded("another-report", event.fill, event.observed_at)
    assert account.append(duplicate_report) is False
    assert account.snapshot(before.as_of) == before
    assert len(account.journals) == 2
    conflicting = FillRecorded(
        "another-report",
        Fill(
            "fb",
            "buy",
            S,
            Side.BUY,
            1,
            D("10"),
            D("0"),
            event.observed_at,
            event.observed_at,
            date(2026, 1, 3),
        ),
        event.observed_at,
    )
    with pytest.raises(DomainError, match="fill ID collision"):
        account.append(conflicting)


def test_cash_shortage_oversell_and_reservation() -> None:
    account = funded_account(D("10.00"))
    account.append(OrderPlaced("p", order("b", Side.BUY, 2, D("10"), DAY1), DAY1))
    account.append(
        OrderStatusRecorded("s", "b", OrderStatus.SUBMITTED, DAY1 + timedelta(minutes=1))
    )
    at = DAY1 + timedelta(minutes=2)
    with pytest.raises(DomainError, match="cash"):
        account.append(
            FillRecorded(
                "f", Fill("f", "b", S, Side.BUY, 2, D("10"), D("0"), at, at, date(2026, 1, 3)), at
            )
        )
    assert account.snapshot(at).cash.total == D("10.00")
    rich = funded_account()
    buy(rich)
    rich.append(OrderPlaced("p1", order("s1", Side.SELL, 4, D("10"), DAY2), DAY2))
    snap = rich.snapshot(DAY2)
    assert snap.positions[0].frozen_quantity == 4
    assert snap.positions[0].sellable_quantity(DAY2.date()) == 1
    with pytest.raises(DomainError, match="sellable"):
        rich.append(OrderPlaced("p2", order("s2", Side.SELL, 2, D("10"), DAY2), DAY2))
    rich.append(
        OrderStatusRecorded("cancel", "s1", OrderStatus.CANCELLED, DAY2 + timedelta(minutes=1))
    )
    assert rich.snapshot(DAY2 + timedelta(minutes=1)).positions[0].frozen_quantity == 0
    with pytest.raises(DomainError, match="sellable"):
        rich.append(
            OrderPlaced(
                "p3",
                order("s3", Side.SELL, 6, D("10"), DAY2 + timedelta(minutes=2)),
                DAY2 + timedelta(minutes=2),
            )
        )


def test_rejection_releases_sell_reservation_and_unknown_holds_it() -> None:
    account = funded_account()
    buy(account)
    account.append(OrderPlaced("p", order("s1", Side.SELL, 5, D("10"), DAY2), DAY2))
    account.append(
        OrderStatusRecorded("submit", "s1", OrderStatus.SUBMITTED, DAY2 + timedelta(minutes=1))
    )
    account.append(
        OrderStatusRecorded("unknown", "s1", OrderStatus.UNKNOWN, DAY2 + timedelta(minutes=2))
    )
    assert account.snapshot(DAY2 + timedelta(minutes=2)).positions[0].frozen_quantity == 5
    account.append(
        OrderStatusRecorded(
            "reject",
            "s1",
            OrderStatus.REJECTED,
            DAY2 + timedelta(minutes=3),
            RejectReason.BROKER_REJECTED,
        )
    )
    assert account.snapshot(DAY2 + timedelta(minutes=3)).positions[0].frozen_quantity == 0


def test_seeded_conservation_replay_and_duplicate_properties() -> None:
    """Generated deterministic prices/quantities exercise conservation over many cases."""
    rng = Random(20260928)
    for _ in range(80):
        qty = rng.randint(1, 100)
        buy_price = D(rng.randint(100, 10000)) / 100
        sell_price = D(rng.randint(100, 10000)) / 100
        buy_fee = D(rng.randint(0, 100)) / 100
        sell_fee = D(rng.randint(0, 100)) / 100
        account = funded_account(D("20000.00"))
        buy_event = buy(account, qty, buy_price, buy_fee)
        mid = account.snapshot(DAY1 + timedelta(minutes=2))
        assert mid.cash.total + mid.positions[0].lots[0].cost_basis + buy_fee == D("20000.00")
        assert account.append(buy_event) is False
        sell_event = sell(account, qty, sell_price, sell_fee)
        final = account.snapshot(DAY2 + timedelta(minutes=2))
        assert final.positions == ()
        expected = D("20000.00") - buy_price * qty - buy_fee + sell_price * qty - sell_fee
        assert final.cash.total == expected
        assert account.append(sell_event) is False
        assert Account.replay(account.events).snapshot(final.as_of) == final
        assert all(sum((p.amount for p in j.postings), D("0")) == 0 for j in account.journals)


def test_journal_snapshot_and_event_constructor_rejections() -> None:
    with pytest.raises(DomainError, match="posting"):
        Posting("CASH", D("1"))  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="cents"):
        Posting(LedgerAccount.CASH, D("0.001"))
    with pytest.raises(DomainError, match="balance"):
        JournalEntry("bad", (Posting(LedgerAccount.CASH, D("1")),))
    entries = [Posting(LedgerAccount.CASH, D("1")), Posting(LedgerAccount.EXTERNAL_EQUITY, D("-1"))]
    with pytest.raises(DomainError, match="balance"):
        JournalEntry("mutable", entries)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="positive"):
        FundingRecorded("bad", D("0"), DAY1)
    with pytest.raises(DomainError, match="NEW"):
        OrderPlaced(
            "bad",
            order("o", Side.BUY, 1, D("10"), DAY1).transition(OrderStatus.SUBMITTED, DAY1),
            DAY1,
        )
    with pytest.raises(DomainError, match="controlled"):
        OrderStatusRecorded("bad", "o", "ACK", DAY1)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="controlled reason"):
        OrderStatusRecorded("bad-reason", "o", OrderStatus.REJECTED, DAY1, "arbitrary")  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="controlled reason"):
        OrderStatusRecorded("missing-reason", "o", OrderStatus.REJECTED, DAY1)
    with pytest.raises(DomainError, match="cannot include reason"):
        OrderStatusRecorded("extra-reason", "o", OrderStatus.ACK, DAY1, RejectReason.UNKNOWN)
    with pytest.raises(DomainError, match="observation"):
        FillRecorded(
            "bad",
            Fill("f", "o", S, Side.SELL, 1, D("10"), D("0"), DAY1, DAY1),
            DAY1 + timedelta(seconds=1),
        )
    with pytest.raises(DomainError, match="frozen"):
        CashBalance(D("1"), D("2"), DAY1)
    cash = CashBalance(D("2"), D("1"), DAY1)
    assert cash.available == D("1")
    with pytest.raises(DomainError, match="timestamps"):
        AccountSnapshot(cash, (), (), 0, DAY2)
    snapshot = AccountSnapshot(cash, (), (), 0, DAY1)
    with pytest.raises(DomainError, match="immutable"):
        AccountSnapshot(cash, [], (), 0, DAY1)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="immutable"):
        AccountSnapshot(cash, (), ("not an order",), 0, DAY1)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="timestamps"):
        PortfolioSnapshot(snapshot, DAY2)
    assert PortfolioSnapshot(snapshot, DAY1).account == snapshot


def test_rejection_status_json_reason_is_controlled() -> None:
    valid = OrderStatusRecorded(
        "reject", "o", OrderStatus.REJECTED, DAY1, RejectReason.RISK_REJECTED
    )
    assert from_json(to_json(valid)) == valid
    encoded = json.loads(to_json(valid))
    encoded["payload"]["reason"] = "arbitrary"
    with pytest.raises(DomainError, match="controlled reason"):
        from_json(json.dumps(encoded))


def test_aggregate_id_time_and_missing_order_fail_closed() -> None:
    account = funded_account()
    with pytest.raises(DomainError, match="unsupported"):
        account.append("bad")  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="collision"):
        account.append(FundingRecorded("fund", D("1"), DAY1))
    with pytest.raises(DomainError, match="out of order"):
        account.append(FundingRecorded("late", D("1"), DAY1 - timedelta(seconds=1)))
    with pytest.raises(DomainError, match="latest"):
        account.snapshot(DAY1 - timedelta(seconds=1))
    with pytest.raises(DomainError, match="unknown order"):
        account.append(OrderStatusRecorded("status", "missing", OrderStatus.ACK, DAY1))
    at = DAY1 + timedelta(seconds=1)
    with pytest.raises(DomainError, match="unknown order"):
        account.append(
            FillRecorded(
                "missing", Fill("fm", "missing", S, Side.SELL, 1, D("10"), D("0"), at, at), at
            )
        )
    with pytest.raises(DomainError, match="before effective"):
        account.append(OrderPlaced("too-early", order("later", Side.BUY, 1, D("10"), DAY2), DAY1))
    first = order("one", Side.BUY, 1, D("10"), DAY1)
    account.append(OrderPlaced("placed", first, DAY1))
    with pytest.raises(DomainError, match="duplicate"):
        account.append(OrderPlaced("placed-again", first, DAY1))
    same_key = replace(
        order("two", Side.BUY, 1, D("10"), DAY1),
        intent=replace(
            order("two", Side.BUY, 1, D("10"), DAY1).intent,
            idempotency_key=first.intent.idempotency_key,
        ),
    )
    with pytest.raises(DomainError, match="duplicate"):
        account.append(OrderPlaced("same-key", same_key, DAY1))


def test_execution_order_fee_and_rounding_edge_cases() -> None:
    account = funded_account()
    buy(account)
    account.append(OrderPlaced("p-s", order("s", Side.SELL, 2, D("0.01"), DAY2), DAY2))
    account.append(OrderStatusRecorded("submit-s", "s", OrderStatus.SUBMITTED, DAY2))
    at = DAY2 + timedelta(minutes=1)
    with pytest.raises(DomainError, match="fee exceeds"):
        account.append(
            FillRecorded(
                "too-expensive", Fill("se", "s", S, Side.SELL, 2, D("0.01"), D("1"), at, at), at
            )
        )
    assert account.snapshot(at).positions[0].quantity == 5
    account.append(
        FillRecorded("fine", Fill("sf", "s", S, Side.SELL, 2, D("0.01"), D("0"), at, at), at)
    )
    account.append(
        OrderPlaced("p-b2", order("b2", Side.BUY, 1, D("10"), DAY2), DAY2 + timedelta(minutes=2))
    )
    account.append(
        OrderStatusRecorded("submit-b2", "b2", OrderStatus.SUBMITTED, DAY2 + timedelta(minutes=2))
    )
    with pytest.raises(DomainError, match="out-of-order execution"):
        account.append(
            FillRecorded(
                "old-exec",
                Fill(
                    "old",
                    "b2",
                    S,
                    Side.BUY,
                    1,
                    D("10"),
                    D("0"),
                    DAY2,
                    DAY2 + timedelta(minutes=3),
                    date(2026, 1, 4),
                ),
                DAY2 + timedelta(minutes=3),
            )
        )


def test_partial_fill_cent_allocation_conserves_basis() -> None:
    account = funded_account()
    buy_intent = OrderIntent(
        "cheap-i", "cheap-k", S, Side.BUY, 3, D("0.333"), D("0.001"), DAY1, DAY1
    )
    account.append(OrderPlaced("cheap-p", Order("cheap", buy_intent), DAY1))
    account.append(
        OrderStatusRecorded("cheap-s", "cheap", OrderStatus.SUBMITTED, DAY1 + timedelta(minutes=1))
    )
    at = DAY1 + timedelta(minutes=2)
    account.append(
        FillRecorded(
            "cheap-f",
            Fill("cheap-f", "cheap", S, Side.BUY, 3, D("0.333"), D("0"), at, at, date(2026, 1, 3)),
            at,
        )
    )
    assert account.snapshot(at).positions[0].lots[0].cost_basis == D("1.00")
    sell_intent = OrderIntent(
        "cheap-si", "cheap-sk", S, Side.SELL, 3, D("0.333"), D("0.001"), DAY2, DAY2
    )
    account.append(OrderPlaced("cheap-sp", Order("cheap-s", sell_intent), DAY2))
    account.append(
        OrderStatusRecorded(
            "cheap-ss", "cheap-s", OrderStatus.SUBMITTED, DAY2 + timedelta(minutes=1)
        )
    )
    at1 = DAY2 + timedelta(minutes=2)
    account.append(
        FillRecorded(
            "cheap-sf1",
            Fill("cheap-sf1", "cheap-s", S, Side.SELL, 1, D("0.333"), D("0"), at1, at1),
            at1,
        )
    )
    lot = account.snapshot(at1).positions[0].lots[0]
    assert (lot.quantity, lot.cost_basis) == (2, D("0.67"))
    at2 = DAY2 + timedelta(minutes=3)
    account.append(
        FillRecorded(
            "cheap-sf2",
            Fill("cheap-sf2", "cheap-s", S, Side.SELL, 2, D("0.333"), D("0"), at2, at2),
            at2,
        )
    )
    assert account.snapshot(at2).cash.total == D("1000.00")
    assert account.snapshot(at2).positions == ()


def test_account_arithmetic_ignores_ambient_decimal_precision() -> None:
    with localcontext() as context:
        context.prec = 4
        account = funded_account(D("1000.00"))
        buy(account, 5, D("10.00"), D("1.00"))
        sell(account, 2, D("12.00"), D("0.50"))
        assert account.snapshot(DAY2 + timedelta(minutes=2)).cash.total == D("972.50")
        assert all(sum((p.amount for p in j.postings), D("0")) == 0 for j in account.journals)


def test_review_regression_signed_amounts_and_replay_journals() -> None:
    account = funded_account()
    buy(account, 1, D("123.45"), D("0"))
    before = account.events
    with localcontext() as context:
        context.prec = 4
        assert CashBalance(D("1000.00"), D("123.45"), DAY1).available == D("876.55")
        sell(account, 1, D("123.55"), D("0"))
        journal = account.journals[-1]
        inventory = next(p.amount for p in journal.postings if p.account is LedgerAccount.INVENTORY)
        realized = next(
            p.amount for p in journal.postings if p.account is LedgerAccount.REALIZED_PNL
        )
        assert inventory == D("-123.45")
        assert realized == D("-0.10")
        with pytest.raises(DomainError, match="cents"):
            Posting(LedgerAccount.CASH, D("123.456"))
    assert before != account.events
    assert Account.replay(account.events).journals == account.journals
    assert account.snapshot(DAY2 + timedelta(minutes=2)).positions == ()


def test_review_regression_fill_before_placement_or_submission_rejected() -> None:
    account = Account()
    placed = DAY1 + timedelta(minutes=10)
    submitted = DAY1 + timedelta(minutes=11)
    observed = DAY1 + timedelta(minutes=12)
    account.append(FundingRecorded("fund", D("100"), placed))
    early_intent = OrderIntent(
        "early-i", "early-key", S, Side.BUY, 1, D("10"), D("0.01"), DAY1, DAY1
    )
    account.append(OrderPlaced("place", Order("early", early_intent), placed))
    account.append(OrderStatusRecorded("submit", "early", OrderStatus.SUBMITTED, submitted))
    for executed in (DAY1 + timedelta(minutes=5), placed + timedelta(seconds=30)):
        early_fill = Fill(
            "early-f",
            "early",
            S,
            Side.BUY,
            1,
            D("10"),
            D("0"),
            executed,
            observed,
            date(2026, 1, 3),
        )
        with pytest.raises(DomainError, match="before local"):
            account.append(FillRecorded("early-event", early_fill, observed))
    assert account.snapshot(observed).cash.total == D("100")
    assert account.snapshot(observed).positions == ()


def test_cross_lot_partial_sale_matches_inventory_journal() -> None:
    account = funded_account()
    for index, (qty, price) in enumerate(((2, D("10.00")), (3, D("20.00")))):
        at = DAY1 + timedelta(minutes=10 * index)
        order_id = f"b{index}"
        account.append(OrderPlaced(f"p{index}", order(order_id, Side.BUY, qty, price, at), at))
        submitted = at + timedelta(minutes=1)
        account.append(OrderStatusRecorded(f"s{index}", order_id, OrderStatus.SUBMITTED, submitted))
        executed = at + timedelta(minutes=2)
        account.append(
            FillRecorded(
                f"f{index}",
                Fill(
                    f"f{index}",
                    order_id,
                    S,
                    Side.BUY,
                    qty,
                    price,
                    D("0"),
                    executed,
                    executed,
                    date(2026, 1, 3),
                ),
                executed,
            )
        )
    account.append(OrderPlaced("ps", order("sale", Side.SELL, 4, D("30"), DAY2), DAY2))
    account.append(
        OrderStatusRecorded("ss", "sale", OrderStatus.SUBMITTED, DAY2 + timedelta(minutes=1))
    )
    at = DAY2 + timedelta(minutes=2)
    account.append(
        FillRecorded("fs", Fill("fs", "sale", S, Side.SELL, 4, D("30"), D("0"), at, at), at)
    )
    snap = account.snapshot(at)
    assert snap.positions[0].quantity == 1
    assert snap.positions[0].lots[0].cost_basis == D("20.00")
    inventory = next(
        p.amount for p in account.journals[-1].postings if p.account is LedgerAccount.INVENTORY
    )
    assert inventory == D("-60.00")
    assert sum(
        (
            p.amount
            for journal in account.journals
            for p in journal.postings
            if p.account is LedgerAccount.INVENTORY
        ),
        D("0"),
    ) == D("20.00")
    rebuilt = Account.replay(account.events)
    assert rebuilt.journals == account.journals
    assert rebuilt.snapshot(at) == snap
