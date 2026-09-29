"""Boundary validation and state-machine behavior, without network access."""

import json
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from ai_quant_trade.domain.accounting import CashBalance
from ai_quant_trade.domain.market import Bar, Quote, Signal, TargetPosition
from ai_quant_trade.domain.orders import Fill, Order, OrderIntent
from ai_quant_trade.domain.positions import PositionLot
from ai_quant_trade.domain.serialization import from_json, to_json
from ai_quant_trade.domain.types import (
    Board,
    DomainError,
    Exchange,
    OrderStatus,
    PriceBasis,
    RejectReason,
    Side,
    Symbol,
)

TZ = ZoneInfo("Asia/Shanghai")
T = datetime(2026, 1, 2, 10, tzinfo=TZ)
S = Symbol("600000", Exchange.SSE, Board.MAIN)
D = Decimal


def intent(side: Side = Side.BUY, quantity: int = 5) -> OrderIntent:
    """Create one valid, explicitly ticked order intent."""
    return OrderIntent("i1", "key1", S, side, quantity, D("10.00"), D("0.01"), T, T)


def fill(quantity: int = 2, observed_at: datetime = T + timedelta(minutes=2)) -> Fill:
    """Create a buy fill with caller-supplied lot release date."""
    return Fill(
        "f1",
        "o1",
        S,
        Side.BUY,
        quantity,
        D("10.00"),
        D("0.005"),
        observed_at,
        observed_at,
        date(2026, 1, 3),
    )


@pytest.mark.parametrize("bad", [0, -1, 1.5, True])
def test_share_quantity_rejects_non_positive_and_noninteger(bad: object) -> None:
    with pytest.raises(DomainError):
        OrderIntent("i1", "k1", S, Side.BUY, bad, D("10"), D("0.01"), T, T)  # type: ignore[arg-type]


def test_money_float_tick_and_nonfinite_rejected() -> None:
    with pytest.raises(DomainError, match="Decimal"):
        OrderIntent("i1", "k1", S, Side.BUY, 1, 10.0, D("0.01"), T, T)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="tick"):
        OrderIntent("i1", "k1", S, Side.BUY, 1, D("10.001"), D("0.01"), T, T)
    with pytest.raises(DomainError):
        CashBalance(D("NaN"), D("0"), T)
    assert fill().fee == D("0.01")  # half-up fee rounding


@pytest.mark.parametrize(
    "kind", ["intent", "fill", "lot", "bar", "quote", "signal", "target", "cash"]
)
def test_naive_time_rejected(kind: str) -> None:
    naive = T.replace(tzinfo=None)
    with pytest.raises(DomainError, match="timezone-aware"):
        if kind == "intent":
            OrderIntent("i", "k", S, Side.BUY, 1, D("10"), D(".01"), naive, T)
        elif kind == "fill":
            Fill("f", "o", S, Side.BUY, 1, D("10"), D("0"), naive, T, date(2026, 1, 3))
        elif kind == "lot":
            PositionLot("l", S, 1, D("10"), D("10.00"), naive, date(2026, 1, 3))
        elif kind == "bar":
            Bar(S, naive, T, D("10"), D("11"), D("9"), D("10"), 100, PriceBasis.RAW)
        elif kind == "quote":
            Quote(S, naive, T, D("9"), D("10"))
        elif kind == "signal":
            Signal("sig", S, D("1"), naive, T, T)
        elif kind == "target":
            TargetPosition(S, D(".1"), naive, T)
        else:
            CashBalance(D("0"), D("0"), naive)


def test_research_time_and_price_boundaries() -> None:
    with pytest.raises(DomainError, match="look ahead"):
        Signal("s", S, D("1"), T, T + timedelta(minutes=1), T)
    with pytest.raises(DomainError, match="weight"):
        TargetPosition(S, D("1.1"), T, T)
    with pytest.raises(DomainError, match="OHLC"):
        Bar(S, T, T, D("10"), D("9"), D("8"), D("10"), 1, PriceBasis.RAW)
    with pytest.raises(DomainError, match="bid"):
        Quote(S, T, T, D("11"), D("10"))


def test_order_transitions_unknown_partial_and_terminal() -> None:
    order = Order("o1", intent())
    with pytest.raises(DomainError, match="unsubmitted"):
        order.apply_fill(fill())
    with pytest.raises(DomainError, match="illegal"):
        order.transition(OrderStatus.FILLED, T)
    order = order.transition(OrderStatus.SUBMITTED, T)
    order = order.transition(OrderStatus.UNKNOWN, T + timedelta(minutes=1))
    assert order.is_open  # no inference of rejection or permission to retry
    order = order.apply_fill(fill())
    assert order.status is OrderStatus.PARTIALLY_FILLED and order.filled_quantity == 2
    with pytest.raises(DomainError, match="remaining"):
        order.apply_fill(
            Fill(
                "f2",
                "o1",
                S,
                Side.BUY,
                4,
                D("10"),
                D("0"),
                T + timedelta(minutes=3),
                T + timedelta(minutes=3),
                date(2026, 1, 3),
            )
        )
    order = order.transition(OrderStatus.CANCELLED, T + timedelta(minutes=3))
    assert not order.is_open
    with pytest.raises(DomainError, match="terminal"):
        order.apply_fill(
            Fill(
                "f3",
                "o1",
                S,
                Side.BUY,
                1,
                D("10"),
                D("0"),
                T + timedelta(minutes=4),
                T + timedelta(minutes=4),
                date(2026, 1, 3),
            )
        )


def test_rejection_requires_reason() -> None:
    order = Order("o1", intent())
    with pytest.raises(DomainError, match="reason"):
        order.transition(OrderStatus.REJECTED, T)
    assert (
        order.transition(OrderStatus.REJECTED, T, RejectReason.RISK_REJECTED).status
        is OrderStatus.REJECTED
    )


def test_serialization_round_trip_and_version_fail_closed() -> None:
    objects = [
        S,
        intent(),
        fill(),
        Order("o1", intent()),
        PositionLot("l", S, 2, D("10"), D("20.00"), T, date(2026, 1, 3)),
    ]
    for obj in objects:
        assert from_json(to_json(obj)) == obj
    data = json.loads(to_json(intent()))
    data["version"] = 2
    with pytest.raises(DomainError, match="version"):
        from_json(json.dumps(data))
    data["version"] = 1
    data["payload"]["$type"] = "Untrusted"
    with pytest.raises(DomainError, match="unknown object"):
        from_json(json.dumps(data))


def test_order_constructor_and_fill_negative_boundaries() -> None:
    base = intent()
    for intent_changes in (
        {"effective_at": T - timedelta(seconds=1)},
        {"side": "BUY"},
        {"currency": "USD"},
        {"time_in_force": "DAY"},
    ):
        with pytest.raises(DomainError):
            replace(base, **intent_changes)
    for fill_changes in (
        {"sellable_from": None},
        {"sellable_from": date(2026, 1, 1)},
        {"observed_at": T},
        {"side": "BUY"},
    ):
        with pytest.raises(DomainError):
            replace(fill(), **fill_changes)
    with pytest.raises(DomainError, match="sell fill"):
        replace(fill(), side=Side.SELL)
    for order_changes in (
        {"intent": "bad"},
        {"status": "NEW"},
        {"filled_quantity": 6},
        {"status": OrderStatus.FILLED},
        {"status": OrderStatus.ACK, "filled_quantity": 1},
        {"status": OrderStatus.PARTIALLY_FILLED},
        {"reject_reason": RejectReason.UNKNOWN},
        {"last_observed_at": T.replace(tzinfo=None)},
    ):
        with pytest.raises(DomainError):
            replace(Order("o1", base), **order_changes)


def test_fill_validation_and_report_order() -> None:
    order = Order("o1", intent()).transition(OrderStatus.SUBMITTED, T)
    at = T + timedelta(minutes=2)
    for changes in (
        {"order_id": "other"},
        {"price": D("10.001")},
        {"price": D("10.01")},
        {"quantity": 6},
        {"executed_at": T - timedelta(seconds=1)},
    ):
        with pytest.raises(DomainError):
            order.apply_fill(replace(fill(), **changes))
    sell_order = Order("o1", intent(Side.SELL)).transition(OrderStatus.SUBMITTED, T)
    with pytest.raises(DomainError, match="below limit"):
        sell_order.apply_fill(Fill("fs", "o1", S, Side.SELL, 1, D("9.99"), D("0"), at, at))
    with pytest.raises(DomainError, match="out-of-order"):
        order.transition(OrderStatus.ACK, T - timedelta(seconds=1))
    with pytest.raises(DomainError, match="reason"):
        order.transition(OrderStatus.ACK, at, RejectReason.UNKNOWN)
    with pytest.raises(DomainError, match="out-of-order"):
        order.transition(OrderStatus.ACK, at).apply_fill(
            replace(
                fill(), observed_at=T + timedelta(minutes=1), executed_at=T + timedelta(minutes=1)
            )
        )


def test_rejected_reason_and_nested_types_cannot_bypass_decoding() -> None:
    with pytest.raises(DomainError, match="reason"):
        Order("o", intent(), status=OrderStatus.REJECTED)
    with pytest.raises(DomainError, match="reason"):
        Order("o", intent(), status=OrderStatus.REJECTED, reject_reason="arbitrary")  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="symbol"):
        Quote("bad", T, T, D("9"), D("10"))  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="symbol"):
        Bar("bad", T, T, D("10"), D("11"), D("9"), D("10"), 1, PriceBasis.RAW)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="symbol"):
        Signal("sig", "bad", D("1"), T, T, T)  # type: ignore[arg-type]
    with pytest.raises(DomainError, match="symbol"):
        TargetPosition("bad", D(".1"), T, T)  # type: ignore[arg-type]


def test_lot_and_position_validation_and_rounding() -> None:
    from ai_quant_trade.domain.positions import Position

    lot = PositionLot("l", S, 2, D("10"), D("20.00"), T, date(2026, 1, 3))
    assert lot.sellable_on(date(2026, 1, 2)) == 0
    assert lot.sellable_on(date(2026, 1, 3)) == 2
    with pytest.raises(DomainError):
        replace(lot, sellable_from=date(2026, 1, 1))
    with pytest.raises(DomainError):
        replace(lot, cost_basis=D("20.001"))
    with pytest.raises(DomainError):
        lot.sellable_on("2026-01-03")  # type: ignore[arg-type]
    with pytest.raises(DomainError):
        Position(S, (lot,), 3, T)
    other = Symbol("000001", Exchange.SZSE, Board.MAIN)
    with pytest.raises(DomainError):
        Position(other, (lot,), 0, T)


def test_serialization_rejects_malformed_payloads() -> None:
    with pytest.raises(DomainError, match="top-level"):
        to_json("not a domain object")
    with pytest.raises(DomainError, match="invalid JSON"):
        from_json("{")
    data = json.loads(to_json(intent()))
    for value in (True, "1", 0):
        changed = {**data, "version": value}
        with pytest.raises(DomainError, match="version"):
            from_json(json.dumps(changed))
    payload = data["payload"]
    assert isinstance(payload, dict)
    for field, changed_value in (
        ("limit_price", {"$decimal": "NaN"}),
        ("limit_price", {"$decimal": "not-decimal"}),
        ("as_of", {"$datetime": "2026-01-01T00:00:00"}),
        ("as_of", {"$datetime": "broken"}),
        ("side", {"$enum": "Unknown", "value": "BUY"}),
        ("side", {"$enum": "Side", "value": "OTHER"}),
        ("symbol", {"$type": "Symbol", "code": "600000"}),
    ):
        changed = {**data, "payload": {**payload, field: changed_value}}
        with pytest.raises(DomainError):
            from_json(json.dumps(changed))


def test_json_decimal_tag_requires_text_not_json_number() -> None:
    original = fill()
    encoded = json.loads(to_json(original))
    for raw_amount in (1.005, 1, True):
        changed = {**encoded, "payload": {**encoded["payload"], "fee": {"$decimal": raw_amount}}}
        with pytest.raises(DomainError, match="string"):
            from_json(json.dumps(changed))
