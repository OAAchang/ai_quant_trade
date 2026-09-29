"""Timestamped market and research boundary objects, without data I/O."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ai_quant_trade.domain.types import (
    DomainError,
    PriceBasis,
    Symbol,
    aware,
    decimal_value,
    shares,
)


@dataclass(frozen=True, slots=True)
class Bar:
    """OHLCV with explicit research/raw price basis and observation time."""

    symbol: Symbol
    as_of: datetime
    observed_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    price_basis: PriceBasis

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, Symbol):
            raise DomainError("bar symbol must be Symbol")
        aware(self.as_of, "as_of")
        aware(self.observed_at, "observed_at")
        if self.observed_at < self.as_of:
            raise DomainError("bar observed_at precedes as_of")
        for name in ("open", "high", "low", "close"):
            decimal_value(getattr(self, name), name, positive=True)
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close):
            raise DomainError("OHLC bounds are inconsistent")
        shares(self.volume, "volume")
        if not isinstance(self.price_basis, PriceBasis):
            raise DomainError("price_basis must be controlled")


@dataclass(frozen=True, slots=True)
class Quote:
    """Observed raw executable bid/ask; no adjusted research price is executable."""

    symbol: Symbol
    as_of: datetime
    observed_at: datetime
    bid: Decimal
    ask: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, Symbol):
            raise DomainError("quote symbol must be Symbol")
        aware(self.as_of, "as_of")
        aware(self.observed_at, "observed_at")
        if self.observed_at < self.as_of:
            raise DomainError("quote observed_at precedes as_of")
        decimal_value(self.bid, "bid", positive=True)
        decimal_value(self.ask, "ask", positive=True)
        if self.bid > self.ask:
            raise DomainError("bid exceeds ask")


@dataclass(frozen=True, slots=True)
class Signal:
    """Research score available only at/after observation; no broker capability."""

    signal_id: str
    symbol: Symbol
    score: Decimal
    as_of: datetime
    observed_at: datetime
    effective_at: datetime

    def __post_init__(self) -> None:
        from ai_quant_trade.domain.types import identifier

        identifier(self.signal_id, "signal_id")
        if not isinstance(self.symbol, Symbol):
            raise DomainError("signal symbol must be Symbol")
        if not isinstance(self.score, Decimal) or not self.score.is_finite():
            raise DomainError("score must be a finite Decimal")
        for name in ("as_of", "observed_at", "effective_at"):
            aware(getattr(self, name), name)
        if self.observed_at < self.as_of or self.effective_at < self.observed_at:
            raise DomainError("signal timing would look ahead")


@dataclass(frozen=True, slots=True)
class TargetPosition:
    """A desired portfolio weight, not an order instruction."""

    symbol: Symbol
    weight: Decimal
    as_of: datetime
    effective_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, Symbol):
            raise DomainError("target symbol must be Symbol")
        decimal_value(self.weight, "weight")
        if self.weight > 1:
            raise DomainError("long-only weight cannot exceed one")
        aware(self.as_of, "as_of")
        aware(self.effective_at, "effective_at")
        if self.effective_at < self.as_of:
            raise DomainError("target effective_at precedes as_of")
