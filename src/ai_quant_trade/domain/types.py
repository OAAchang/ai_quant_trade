"""Validated, I/O-free domain primitives. No exchange rule is implied here."""

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Context, Decimal, InvalidOperation, localcontext
from enum import StrEnum
from zoneinfo import ZoneInfo


class DomainError(ValueError):
    """Invalid domain input or transition; callers must fail closed."""


class Exchange(StrEnum):
    SSE = "SSE"
    SZSE = "SZSE"
    BSE = "BSE"


class Board(StrEnum):
    MAIN = "MAIN"
    STAR = "STAR"
    CHINEXT = "CHINEXT"
    BEIJING = "BEIJING"
    OTHER = "OTHER"


class Currency(StrEnum):
    CNY = "CNY"


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    LIMIT = "LIMIT"


class TimeInForce(StrEnum):
    DAY = "DAY"
    GTC = "GTC"


class OrderStatus(StrEnum):
    NEW = "NEW"
    SUBMITTED = "SUBMITTED"
    ACK = "ACK"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class RejectReason(StrEnum):
    INSUFFICIENT_CASH = "INSUFFICIENT_CASH"
    INSUFFICIENT_POSITION = "INSUFFICIENT_POSITION"
    INVALID_ORDER = "INVALID_ORDER"
    BROKER_REJECTED = "BROKER_REJECTED"
    RISK_REJECTED = "RISK_REJECTED"
    UNKNOWN = "UNKNOWN"


class PriceBasis(StrEnum):
    RAW = "RAW"
    RESEARCH_ADJUSTED = "RESEARCH_ADJUSTED"


SHANGHAI = ZoneInfo("Asia/Shanghai")
CENT = Decimal("0.01")
ARITHMETIC_CONTEXT = Context(prec=50, rounding=ROUND_HALF_UP)


def aware(value: datetime, name: str) -> datetime:
    """Require a real timezone offset, without silently assigning a timezone."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DomainError(f"{name} must be timezone-aware")
    return value


def decimal_value(value: Decimal, name: str, *, positive: bool = False) -> Decimal:
    """Reject floats, NaN/infinity and invalid signs at the accounting boundary."""
    if not isinstance(value, Decimal) or not value.is_finite():
        raise DomainError(f"{name} must be a finite Decimal")
    if (positive and value <= 0) or (not positive and value < 0):
        raise DomainError(f"{name} has invalid sign")
    return value


def shares(value: int, name: str, *, positive: bool = False) -> int:
    """Reject bool and fractional/negative share quantities."""
    if type(value) is not int or (positive and value <= 0) or (not positive and value < 0):
        raise DomainError(f"{name} must be an integer with valid sign")
    return value


def money(value: Decimal) -> Decimal:
    """Round monetary postings to CNY cents using ROUND_HALF_UP."""
    decimal_value(value, "money")
    try:
        with localcontext(ARITHMETIC_CONTEXT):
            return value.quantize(CENT, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise DomainError("money cannot be quantized to cents") from exc


def exact_money(value: Decimal, name: str) -> Decimal:
    """Require a caller-supplied amount already in cents."""
    decimal_value(value, name)
    if money(value) != value:
        raise DomainError(f"{name} must be in whole cents")
    return value


def signed_sum(*values: Decimal) -> Decimal:
    """Add signed monetary values with a fixed precision independent of callers."""
    with localcontext(ARITHMETIC_CONTEXT):
        return sum(values, Decimal("0.00"))


def price_amount(price: Decimal, quantity: int) -> Decimal:
    """Round one price-times-shares posting to cents."""
    with localcontext(ARITHMETIC_CONTEXT):
        return money(price * quantity)


def allocate_cost(cost_basis: Decimal, taken: int, held: int) -> Decimal:
    """Round a partial lot's cost; final disposal takes the remainder."""
    with localcontext(ARITHMETIC_CONTEXT):
        return money(cost_basis * taken / held)


def tick_aligned(price: Decimal, tick_size: Decimal) -> bool:
    """Check caller-supplied tick under fixed precision."""
    try:
        with localcontext(ARITHMETIC_CONTEXT):
            return price % tick_size == 0
    except InvalidOperation as exc:
        raise DomainError("price/tick cannot be evaluated") from exc


def identifier(value: str, name: str) -> str:
    """Require a stable, non-blank identifier without normalizing it."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 128:
        raise DomainError(f"{name} must be a non-blank stable identifier")
    return value


@dataclass(frozen=True, slots=True)
class Symbol:
    """Listed security identifier; no ticker-to-board guess is made."""

    code: str
    exchange: Exchange
    board: Board

    def __post_init__(self) -> None:
        if (
            not isinstance(self.code, str)
            or not 1 <= len(self.code) <= 16
            or not self.code.isascii()
            or not self.code.isalnum()
            or self.code != self.code.upper()
        ):
            raise DomainError("code must be uppercase ASCII alphanumeric")
        if not isinstance(self.exchange, Exchange) or not isinstance(self.board, Board):
            raise DomainError("exchange and board must be controlled enums")
