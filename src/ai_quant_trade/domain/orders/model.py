"""Immutable order state; only explicit reports or fills advance it."""

from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal

from ai_quant_trade.domain.types import (
    SHANGHAI,
    Currency,
    DomainError,
    OrderStatus,
    OrderType,
    RejectReason,
    Side,
    Symbol,
    TimeInForce,
    aware,
    decimal_value,
    identifier,
    money,
    shares,
    tick_aligned,
)

_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.NEW: frozenset(
        {OrderStatus.SUBMITTED, OrderStatus.REJECTED, OrderStatus.CANCELLED}
    ),
    OrderStatus.SUBMITTED: frozenset(
        {
            OrderStatus.ACK,
            OrderStatus.REJECTED,
            OrderStatus.CANCELLED,
            OrderStatus.EXPIRED,
            OrderStatus.UNKNOWN,
        }
    ),
    OrderStatus.ACK: frozenset(
        {OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED, OrderStatus.UNKNOWN}
    ),
    OrderStatus.PARTIALLY_FILLED: frozenset(
        {OrderStatus.CANCELLED, OrderStatus.EXPIRED, OrderStatus.UNKNOWN}
    ),
    OrderStatus.UNKNOWN: frozenset(
        {OrderStatus.ACK, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED}
    ),
    OrderStatus.FILLED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
    OrderStatus.REJECTED: frozenset(),
    OrderStatus.EXPIRED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class OrderIntent:
    """Long-only cash-equity request with caller-supplied effective tick."""

    intent_id: str
    idempotency_key: str
    symbol: Symbol
    side: Side
    quantity: int
    limit_price: Decimal
    tick_size: Decimal
    as_of: datetime
    effective_at: datetime
    order_type: OrderType = OrderType.LIMIT
    time_in_force: TimeInForce = TimeInForce.DAY
    currency: Currency = Currency.CNY

    def __post_init__(self) -> None:
        identifier(self.intent_id, "intent_id")
        identifier(self.idempotency_key, "idempotency_key")
        if not isinstance(self.symbol, Symbol) or not isinstance(self.side, Side):
            raise DomainError("symbol/side must be controlled")
        shares(self.quantity, "quantity", positive=True)
        decimal_value(self.limit_price, "limit_price", positive=True)
        decimal_value(self.tick_size, "tick_size", positive=True)
        if not tick_aligned(self.limit_price, self.tick_size):
            raise DomainError("limit_price is not on caller-supplied tick")
        aware(self.as_of, "as_of")
        aware(self.effective_at, "effective_at")
        if self.effective_at < self.as_of:
            raise DomainError("order effective_at precedes as_of")
        if (
            self.order_type is not OrderType.LIMIT
            or not isinstance(self.time_in_force, TimeInForce)
            or self.currency is not Currency.CNY
        ):
            raise DomainError("unsupported order type, TIF or currency")


@dataclass(frozen=True, slots=True)
class Fill:
    """Authoritative execution report, not a submission acknowledgement."""

    fill_id: str
    order_id: str
    symbol: Symbol
    side: Side
    quantity: int
    price: Decimal
    fee: Decimal
    executed_at: datetime
    observed_at: datetime
    sellable_from: date | None = None

    def __post_init__(self) -> None:
        identifier(self.fill_id, "fill_id")
        identifier(self.order_id, "order_id")
        if not isinstance(self.symbol, Symbol) or not isinstance(self.side, Side):
            raise DomainError("fill symbol/side must be controlled")
        shares(self.quantity, "quantity", positive=True)
        decimal_value(self.price, "price", positive=True)
        decimal_value(self.fee, "fee")
        object.__setattr__(self, "fee", money(self.fee))
        aware(self.executed_at, "executed_at")
        aware(self.observed_at, "observed_at")
        if self.observed_at < self.executed_at:
            raise DomainError("fill observation precedes execution")
        if self.side is Side.BUY:
            if type(self.sellable_from) is not date:
                raise DomainError("buy fill requires externally determined sellable_from date")
            if self.sellable_from < self.executed_at.astimezone(SHANGHAI).date():
                raise DomainError("sellable_from precedes acquisition date")
        elif self.sellable_from is not None:
            raise DomainError("sell fill cannot set sellable_from")


@dataclass(frozen=True, slots=True)
class Order:
    """Order state and cumulative fills; UNKNOWN never means safe to retry."""

    order_id: str
    intent: OrderIntent
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: int = 0
    reject_reason: RejectReason | None = None
    last_observed_at: datetime | None = None
    placed_at: datetime | None = None
    submitted_at: datetime | None = None

    def __post_init__(self) -> None:
        identifier(self.order_id, "order_id")
        if not isinstance(self.intent, OrderIntent) or not isinstance(self.status, OrderStatus):
            raise DomainError("invalid order intent/status")
        shares(self.filled_quantity, "filled_quantity")
        if self.filled_quantity > self.intent.quantity:
            raise DomainError("filled quantity exceeds order")
        if self.status is OrderStatus.FILLED and self.filled_quantity != self.intent.quantity:
            raise DomainError("FILLED requires full quantity")
        if (
            self.status in {OrderStatus.NEW, OrderStatus.SUBMITTED, OrderStatus.ACK}
            and self.filled_quantity
        ):
            raise DomainError("unfilled status cannot carry executed quantity")
        if (
            self.status is OrderStatus.PARTIALLY_FILLED
            and not 0 < self.filled_quantity < self.intent.quantity
        ):
            raise DomainError("PARTIALLY_FILLED requires partial quantity")
        if self.status is OrderStatus.REJECTED:
            if not isinstance(self.reject_reason, RejectReason):
                raise DomainError("REJECTED requires controlled reason")
        elif self.reject_reason is not None:
            raise DomainError("reject reason only belongs to REJECTED")
        if self.last_observed_at is not None:
            aware(self.last_observed_at, "last_observed_at")
        if self.placed_at is not None:
            aware(self.placed_at, "placed_at")
            if self.placed_at < self.intent.effective_at:
                raise DomainError("placement precedes intent effective_at")
        if self.submitted_at is not None:
            aware(self.submitted_at, "submitted_at")
            if self.status is OrderStatus.NEW:
                raise DomainError("NEW order cannot have submitted_at")
            if self.placed_at is not None and self.submitted_at < self.placed_at:
                raise DomainError("submission precedes placement")
        if self.last_observed_at is not None:
            for name, stamp in (("placed_at", self.placed_at), ("submitted_at", self.submitted_at)):
                if stamp is not None and self.last_observed_at < stamp:
                    raise DomainError(f"last observation precedes {name}")

    @property
    def remaining_quantity(self) -> int:
        """Shares not yet filled, regardless of whether order is open."""
        return self.intent.quantity - self.filled_quantity

    @property
    def is_open(self) -> bool:
        """Conservatively reserve UNKNOWN orders until reconciled."""
        return self.status not in {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        }

    def transition(
        self, status: OrderStatus, observed_at: datetime, reason: RejectReason | None = None
    ) -> "Order":
        """Apply an explicit status report; terminal states cannot resurrect."""
        aware(observed_at, "observed_at")
        if not isinstance(status, OrderStatus) or status not in _TRANSITIONS[self.status]:
            raise DomainError(f"illegal order transition {self.status} -> {status}")
        if self.last_observed_at is not None and observed_at < self.last_observed_at:
            raise DomainError("out-of-order status report")
        if status is OrderStatus.REJECTED:
            if not isinstance(reason, RejectReason):
                raise DomainError("rejection requires controlled reason")
        elif reason is not None:
            raise DomainError("non-rejection report cannot include reject reason")
        resolved_status = (
            OrderStatus.PARTIALLY_FILLED
            if status is OrderStatus.ACK and self.filled_quantity
            else status
        )
        return replace(
            self,
            status=resolved_status,
            reject_reason=reason,
            last_observed_at=observed_at,
            submitted_at=(observed_at if status is OrderStatus.SUBMITTED else self.submitted_at),
        )

    def apply_fill(self, fill: Fill) -> "Order":
        """Accept a unique execution report on a nonterminal order, including UNKNOWN."""
        if not self.is_open or self.status is OrderStatus.NEW:
            raise DomainError("fill on unsubmitted or terminal order")
        if (fill.order_id, fill.symbol, fill.side) != (
            self.order_id,
            self.intent.symbol,
            self.intent.side,
        ):
            raise DomainError("fill does not match order")
        if not tick_aligned(fill.price, self.intent.tick_size):
            raise DomainError("fill price is not on caller-supplied tick")
        if fill.executed_at < self.intent.effective_at:
            raise DomainError("fill executed before order effective_at")
        if self.placed_at is not None and fill.executed_at < self.placed_at:
            raise DomainError("fill executed before local order placement")
        if self.submitted_at is not None and fill.executed_at < self.submitted_at:
            raise DomainError("fill executed before local request submission")
        if self.intent.side is Side.BUY and fill.price > self.intent.limit_price:
            raise DomainError("buy fill exceeds limit")
        if self.intent.side is Side.SELL and fill.price < self.intent.limit_price:
            raise DomainError("sell fill below limit")
        if fill.quantity > self.remaining_quantity:
            raise DomainError("fill exceeds remaining quantity")
        if self.last_observed_at is not None and fill.observed_at < self.last_observed_at:
            raise DomainError("out-of-order fill report")
        new_filled = self.filled_quantity + fill.quantity
        return replace(
            self,
            status=(
                OrderStatus.FILLED
                if new_filled == self.intent.quantity
                else OrderStatus.PARTIALLY_FILLED
            ),
            filled_quantity=new_filled,
            last_observed_at=fill.observed_at,
        )
