"""Pure, append-only account aggregate with balanced monetary journals."""

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TypeAlias

from ai_quant_trade.domain.orders import Fill, Order
from ai_quant_trade.domain.positions import Position, PositionLot
from ai_quant_trade.domain.types import (
    SHANGHAI,
    Currency,
    DomainError,
    OrderStatus,
    RejectReason,
    Side,
    Symbol,
    allocate_cost,
    aware,
    exact_money,
    identifier,
    money,
    price_amount,
    shares,
    signed_sum,
)


class LedgerAccount(StrEnum):
    """Signed-debit journal account names; sum of postings is zero."""

    CASH = "CASH"
    INVENTORY = "INVENTORY"
    FEES = "FEES"
    REALIZED_PNL = "REALIZED_PNL"
    EXTERNAL_EQUITY = "EXTERNAL_EQUITY"


@dataclass(frozen=True, slots=True)
class Posting:
    """Signed debit amount in CNY cents (debit positive, credit negative)."""

    account: LedgerAccount
    amount: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.account, LedgerAccount) or not isinstance(self.amount, Decimal):
            raise DomainError("invalid journal posting")
        magnitude = self.amount.copy_abs()
        if not self.amount.is_finite() or money(magnitude) != magnitude:
            raise DomainError("posting must be finite CNY cents")


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """Balanced financial effect of one funding or fill event."""

    event_id: str
    postings: tuple[Posting, ...]

    def __post_init__(self) -> None:
        identifier(self.event_id, "event_id")
        if (
            type(self.postings) is not tuple
            or not self.postings
            or any(not isinstance(p, Posting) for p in self.postings)
            or signed_sum(*(p.amount for p in self.postings)) != 0
        ):
            raise DomainError("journal postings must balance")


@dataclass(frozen=True, slots=True)
class FundingRecorded:
    """Explicit external cash funding; withdrawals are out of Phase 02 scope."""

    event_id: str
    amount: Decimal
    observed_at: datetime

    def __post_init__(self) -> None:
        identifier(self.event_id, "event_id")
        exact_money(self.amount, "funding amount")
        if self.amount <= 0:
            raise DomainError("funding must be positive")
        aware(self.observed_at, "observed_at")


@dataclass(frozen=True, slots=True)
class OrderPlaced:
    """A local order record, not evidence of broker submission."""

    event_id: str
    order: Order
    observed_at: datetime

    def __post_init__(self) -> None:
        identifier(self.event_id, "event_id")
        if (
            not isinstance(self.order, Order)
            or self.order.status is not OrderStatus.NEW
            or self.order.placed_at is not None
            or self.order.submitted_at is not None
        ):
            raise DomainError("OrderPlaced requires a NEW order")
        aware(self.observed_at, "observed_at")


@dataclass(frozen=True, slots=True)
class OrderStatusRecorded:
    """Status event; SUBMITTED observed_at is local request-dispatch instant."""

    event_id: str
    order_id: str
    status: OrderStatus
    observed_at: datetime
    reason: RejectReason | None = None

    def __post_init__(self) -> None:
        identifier(self.event_id, "event_id")
        identifier(self.order_id, "order_id")
        if not isinstance(self.status, OrderStatus):
            raise DomainError("status must be controlled")
        aware(self.observed_at, "observed_at")
        if self.status is OrderStatus.REJECTED:
            if not isinstance(self.reason, RejectReason):
                raise DomainError("REJECTED status event requires controlled reason")
        elif self.reason is not None:
            raise DomainError("non-rejection status event cannot include reason")


@dataclass(frozen=True, slots=True)
class FillRecorded:
    """Uniquely identified execution observation."""

    event_id: str
    fill: Fill
    observed_at: datetime

    def __post_init__(self) -> None:
        identifier(self.event_id, "event_id")
        if not isinstance(self.fill, Fill):
            raise DomainError("fill must be Fill")
        aware(self.observed_at, "observed_at")
        if self.observed_at != self.fill.observed_at:
            raise DomainError("fill event and fill observation differ")


LedgerEvent: TypeAlias = FundingRecorded | OrderPlaced | OrderStatusRecorded | FillRecorded


@dataclass(frozen=True, slots=True)
class CashBalance:
    """Derived cash; buys are checked on fill, not reserved at intent creation."""

    total: Decimal
    frozen: Decimal
    as_of: datetime
    currency: Currency = Currency.CNY

    def __post_init__(self) -> None:
        exact_money(self.total, "cash total")
        exact_money(self.frozen, "cash frozen")
        aware(self.as_of, "as_of")
        if self.frozen > self.total or self.currency is not Currency.CNY:
            raise DomainError("invalid frozen cash or currency")

    @property
    def available(self) -> Decimal:
        """Cash that can be debited at this snapshot."""
        return signed_sum(self.total, self.frozen.copy_negate())


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    """Derived account state at a specified observation time."""

    cash: CashBalance
    positions: tuple[Position, ...]
    orders: tuple[Order, ...]
    event_count: int
    as_of: datetime

    def __post_init__(self) -> None:
        aware(self.as_of, "as_of")
        shares(self.event_count, "event_count")
        if (
            not isinstance(self.cash, CashBalance)
            or type(self.positions) is not tuple
            or any(not isinstance(p, Position) for p in self.positions)
            or type(self.orders) is not tuple
            or any(not isinstance(o, Order) for o in self.orders)
        ):
            raise DomainError("snapshot fields must be immutable domain objects")
        if self.cash.as_of != self.as_of or any(p.as_of != self.as_of for p in self.positions):
            raise DomainError("snapshot timestamps disagree")


@dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    """Single-account portfolio in this phase; no market-value inference."""

    account: AccountSnapshot
    as_of: datetime

    def __post_init__(self) -> None:
        aware(self.as_of, "as_of")
        if not isinstance(self.account, AccountSnapshot):
            raise DomainError("portfolio account must be AccountSnapshot")
        if self.account.as_of != self.as_of:
            raise DomainError("portfolio and account timestamps disagree")


class Account:
    """Controlled in-memory aggregate. Append validates atomically; replay is deterministic."""

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []
        self._journals: list[JournalEntry] = []
        self._orders: dict[str, Order] = {}
        self._lots: dict[Symbol, tuple[PositionLot, ...]] = {}
        self._cash = Decimal("0.00")
        self._event_ids: dict[str, LedgerEvent] = {}
        self._fill_ids: dict[str, Fill] = {}
        self._intent_keys: dict[str, str] = {}
        self._last_observed_at: datetime | None = None
        self._last_execution_at: datetime | None = None

    @property
    def events(self) -> tuple[LedgerEvent, ...]:
        """Immutable view of the append-only event sequence."""
        return tuple(self._events)

    @property
    def journals(self) -> tuple[JournalEntry, ...]:
        """Immutable view of balanced monetary entries."""
        return tuple(self._journals)

    @classmethod
    def replay(cls, events: tuple[LedgerEvent, ...]) -> "Account":
        """Rebuild from a supplied sequence; no snapshot is authoritative."""
        account = cls()
        for event in events:
            account.append(event)
        return account

    def append(self, event: LedgerEvent) -> bool:
        """Apply one event atomically; identical duplicate IDs are no-ops."""
        if not isinstance(event, (FundingRecorded, OrderPlaced, OrderStatusRecorded, FillRecorded)):
            raise DomainError("unsupported ledger event")
        previous = self._event_ids.get(event.event_id)
        if previous is not None:
            if previous == event:
                return False
            raise DomainError("event ID collision with different payload")
        if isinstance(event, FillRecorded) and event.fill.fill_id in self._fill_ids:
            if self._fill_ids[event.fill.fill_id] == event.fill:
                return False
            raise DomainError("fill ID collision with different payload")
        if self._last_observed_at is not None and event.observed_at < self._last_observed_at:
            raise DomainError("ledger event observed out of order")
        orders = self._orders.copy()
        lots = self._lots.copy()
        cash = self._cash
        journal: JournalEntry | None = None
        if isinstance(event, FundingRecorded):
            cash = signed_sum(cash, event.amount)
            journal = JournalEntry(
                event.event_id,
                (
                    Posting(LedgerAccount.CASH, event.amount),
                    Posting(LedgerAccount.EXTERNAL_EQUITY, event.amount.copy_negate()),
                ),
            )
        elif isinstance(event, OrderPlaced):
            order = event.order
            if order.order_id in orders or order.intent.idempotency_key in self._intent_keys:
                raise DomainError("duplicate order ID or intent idempotency key")
            if event.observed_at < order.intent.effective_at:
                raise DomainError("order placement before effective_at")
            if order.intent.side is Side.SELL:
                session_date = order.intent.effective_at.astimezone(SHANGHAI).date()
                eligible = sum(
                    lot.sellable_on(session_date) for lot in lots.get(order.intent.symbol, ())
                )
                frozen = sum(
                    o.remaining_quantity
                    for o in orders.values()
                    if o.is_open
                    and o.intent.side is Side.SELL
                    and o.intent.symbol == order.intent.symbol
                )
                if order.intent.quantity > eligible - frozen:
                    raise DomainError("insufficient sellable position for order")
            orders[order.order_id] = replace(
                order, placed_at=event.observed_at, last_observed_at=event.observed_at
            )
        elif isinstance(event, OrderStatusRecorded):
            status_order = orders.get(event.order_id)
            if status_order is None:
                raise DomainError("status report for unknown order")
            orders[event.order_id] = status_order.transition(
                event.status, event.observed_at, event.reason
            )
        else:
            fill = event.fill
            if self._last_execution_at is not None and fill.executed_at < self._last_execution_at:
                raise DomainError("out-of-order execution requires reconciliation")
            fill_order = orders.get(fill.order_id)
            if fill_order is None:
                raise DomainError("fill for unknown order")
            updated = fill_order.apply_fill(fill)
            notional = price_amount(fill.price, fill.quantity)
            if notional <= 0:
                raise DomainError("fill notional rounds to zero cents")
            if fill.side is Side.BUY:
                debit = signed_sum(notional, fill.fee)
                if debit > cash:
                    raise DomainError("insufficient cash for fill")
                cash = signed_sum(cash, debit.copy_negate())
                symbol_lots = lots.get(fill.symbol, ())
                lots[fill.symbol] = (
                    *symbol_lots,
                    PositionLot(
                        lot_id=fill.fill_id,
                        symbol=fill.symbol,
                        quantity=fill.quantity,
                        unit_cost=fill.price,
                        cost_basis=notional,
                        acquired_at=fill.executed_at,
                        sellable_from=fill.sellable_from,  # type: ignore[arg-type]
                    ),
                )
                journal = JournalEntry(
                    event.event_id,
                    (
                        Posting(LedgerAccount.CASH, debit.copy_negate()),
                        Posting(LedgerAccount.INVENTORY, notional),
                        Posting(LedgerAccount.FEES, fill.fee),
                    ),
                )
            else:
                session_date = fill.executed_at.astimezone(SHANGHAI).date()
                remaining = fill.quantity
                basis = Decimal("0.00")
                kept: list[PositionLot] = []
                for lot in lots.get(fill.symbol, ()):
                    take = min(remaining, lot.sellable_on(session_date))
                    if take:
                        allocated = (
                            lot.cost_basis
                            if take == lot.quantity
                            else allocate_cost(lot.cost_basis, take, lot.quantity)
                        )
                        basis = signed_sum(basis, allocated)
                        remaining -= take
                    if lot.quantity > take:
                        kept.append(
                            replace(
                                lot,
                                quantity=lot.quantity - take,
                                cost_basis=(
                                    signed_sum(lot.cost_basis, allocated.copy_negate())
                                    if take
                                    else lot.cost_basis
                                ),
                            )
                        )
                if remaining:
                    raise DomainError("oversell or lot not yet sellable")
                proceeds = signed_sum(notional, fill.fee.copy_negate())
                if proceeds < 0:
                    raise DomainError("sell fee exceeds proceeds")
                cash = signed_sum(cash, proceeds)
                lots[fill.symbol] = tuple(kept)
                journal = JournalEntry(
                    event.event_id,
                    (
                        Posting(LedgerAccount.CASH, proceeds),
                        Posting(LedgerAccount.INVENTORY, basis.copy_negate()),
                        Posting(LedgerAccount.FEES, fill.fee),
                        Posting(
                            LedgerAccount.REALIZED_PNL,
                            signed_sum(basis, notional.copy_negate()),
                        ),
                    ),
                )
            orders[fill.order_id] = updated
        # Commit only after every check and journal construction has succeeded.
        self._cash = cash
        self._orders = orders
        self._lots = lots
        self._events.append(event)
        self._event_ids[event.event_id] = event
        self._last_observed_at = event.observed_at
        if journal is not None:
            self._journals.append(journal)
        if isinstance(event, OrderPlaced):
            self._intent_keys[event.order.intent.idempotency_key] = event.order.order_id
        if isinstance(event, FillRecorded):
            self._fill_ids[event.fill.fill_id] = event.fill
            self._last_execution_at = event.fill.executed_at
        return True

    def snapshot(self, as_of: datetime) -> AccountSnapshot:
        """Derive balances, lots and open-sell reservations from applied events."""
        aware(as_of, "as_of")
        if self._last_observed_at is not None and as_of < self._last_observed_at:
            raise DomainError("snapshot before latest observed event")
        positions = []
        for symbol, symbol_lots in sorted(
            self._lots.items(), key=lambda item: (item[0].exchange.value, item[0].code)
        ):
            if not symbol_lots:
                continue
            frozen = sum(
                order.remaining_quantity
                for order in self._orders.values()
                if order.is_open
                and order.intent.side is Side.SELL
                and order.intent.symbol == symbol
            )
            positions.append(Position(symbol, symbol_lots, frozen, as_of))
        return AccountSnapshot(
            CashBalance(self._cash, Decimal("0.00"), as_of),
            tuple(positions),
            tuple(self._orders[key] for key in sorted(self._orders)),
            len(self._events),
            as_of,
        )
