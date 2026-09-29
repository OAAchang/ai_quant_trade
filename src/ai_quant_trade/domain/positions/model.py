"""Immutable lots; settlement eligibility is supplied, not inferred."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from ai_quant_trade.domain.types import (
    SHANGHAI,
    DomainError,
    Symbol,
    aware,
    decimal_value,
    exact_money,
    identifier,
    shares,
)


@dataclass(frozen=True, slots=True)
class PositionLot:
    """A buy fill's remaining shares and explicit rule-derived sellable date."""

    lot_id: str
    symbol: Symbol
    quantity: int
    unit_cost: Decimal
    cost_basis: Decimal
    acquired_at: datetime
    sellable_from: date

    def __post_init__(self) -> None:
        identifier(self.lot_id, "lot_id")
        if not isinstance(self.symbol, Symbol):
            raise DomainError("lot symbol must be Symbol")
        shares(self.quantity, "quantity", positive=True)
        decimal_value(self.unit_cost, "unit_cost", positive=True)
        exact_money(self.cost_basis, "cost_basis")
        aware(self.acquired_at, "acquired_at")
        if (
            type(self.sellable_from) is not date
            or self.sellable_from < self.acquired_at.astimezone(SHANGHAI).date()
        ):
            raise DomainError("invalid lot sellable_from date")

    def sellable_on(self, session_date: date) -> int:
        """Return eligible quantity for an explicitly supplied session date."""
        if type(session_date) is not date:
            raise DomainError("session_date must be a date")
        return self.quantity if session_date >= self.sellable_from else 0


@dataclass(frozen=True, slots=True)
class Position:
    """Derived lot position, including quantity frozen by open sell orders."""

    symbol: Symbol
    lots: tuple[PositionLot, ...]
    frozen_quantity: int
    as_of: datetime

    def __post_init__(self) -> None:
        aware(self.as_of, "as_of")
        if not isinstance(self.symbol, Symbol) or type(self.lots) is not tuple:
            raise DomainError("position symbol/lots must be immutable domain objects")
        if any(not isinstance(lot, PositionLot) for lot in self.lots):
            raise DomainError("position lots must be PositionLot objects")
        shares(self.frozen_quantity, "frozen_quantity")
        if any(lot.symbol != self.symbol for lot in self.lots):
            raise DomainError("position contains another symbol")
        if self.frozen_quantity > self.quantity:
            raise DomainError("frozen shares exceed held shares")

    @property
    def quantity(self) -> int:
        """All remaining shares, including unsellable lots."""
        return sum(lot.quantity for lot in self.lots)

    def sellable_quantity(self, session_date: date) -> int:
        """Available eligible shares after conservative order reservation."""
        eligible = sum(lot.sellable_on(session_date) for lot in self.lots)
        return max(0, eligible - self.frozen_quantity)
