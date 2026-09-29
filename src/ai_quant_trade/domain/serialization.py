"""Whitelisted schema-v1 JSON serialization for pure domain objects."""

import json
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

from ai_quant_trade.domain.accounting.ledger import (
    AccountSnapshot,
    CashBalance,
    FillRecorded,
    FundingRecorded,
    JournalEntry,
    LedgerAccount,
    OrderPlaced,
    OrderStatusRecorded,
    PortfolioSnapshot,
    Posting,
)
from ai_quant_trade.domain.market import Bar, Quote, Signal, TargetPosition
from ai_quant_trade.domain.orders import Fill, Order, OrderIntent
from ai_quant_trade.domain.positions import Position, PositionLot
from ai_quant_trade.domain.types import (
    Board,
    Currency,
    DomainError,
    Exchange,
    OrderStatus,
    OrderType,
    PriceBasis,
    RejectReason,
    Side,
    Symbol,
    TimeInForce,
    aware,
)

SCHEMA = "ai_quant_trade.domain"
VERSION = 1
_CLASSES = (
    Symbol,
    Bar,
    Quote,
    Signal,
    TargetPosition,
    OrderIntent,
    Order,
    Fill,
    PositionLot,
    Position,
    CashBalance,
    AccountSnapshot,
    PortfolioSnapshot,
    Posting,
    JournalEntry,
    FundingRecorded,
    OrderPlaced,
    OrderStatusRecorded,
    FillRecorded,
)
_ENUMS = (
    Exchange,
    Board,
    Currency,
    Side,
    OrderType,
    TimeInForce,
    OrderStatus,
    RejectReason,
    PriceBasis,
    LedgerAccount,
)
_CLASS_BY_NAME = {cls.__name__: cls for cls in _CLASSES}
_ENUM_BY_NAME = {cls.__name__: cls for cls in _ENUMS}


def _encode(value: Any) -> Any:
    if isinstance(value, Enum):
        if type(value) not in _ENUMS:
            raise DomainError("unregistered enum")
        return {"$enum": type(value).__name__, "value": value.value}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise DomainError("non-finite Decimal")
        return {"$decimal": str(value)}
    if isinstance(value, datetime):
        aware(value, "serialized datetime")
        return {"$datetime": value.isoformat()}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if type(value) in _CLASSES and is_dataclass(value):
        return {
            "$type": type(value).__name__,
            **{field.name: _encode(getattr(value, field.name)) for field in fields(value)},
        }
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise DomainError(f"unsupported serialization type: {type(value).__name__}")


def _decode(value: Any) -> Any:
    if value is None or type(value) in (str, int, bool):
        return value
    if isinstance(value, list):
        return tuple(_decode(item) for item in value)
    if isinstance(value, dict):
        if "$decimal" in value and len(value) == 1:
            if type(value["$decimal"]) is not str:
                raise DomainError("decimal encoding must be a string")
            try:
                result = Decimal(value["$decimal"])
            except (InvalidOperation, TypeError) as exc:
                raise DomainError("invalid decimal encoding") from exc
            if not result.is_finite():
                raise DomainError("non-finite decimal encoding")
            return result
        if "$datetime" in value and len(value) == 1:
            try:
                return aware(datetime.fromisoformat(value["$datetime"]), "serialized datetime")
            except (TypeError, ValueError) as exc:
                raise DomainError("invalid datetime encoding") from exc
        if "$date" in value and len(value) == 1:
            try:
                return date.fromisoformat(value["$date"])
            except (TypeError, ValueError) as exc:
                raise DomainError("invalid date encoding") from exc
        if "$enum" in value and set(value) == {"$enum", "value"}:
            enum_cls = _ENUM_BY_NAME.get(value["$enum"])
            if enum_cls is None:
                raise DomainError("unknown enum encoding")
            try:
                return enum_cls(value["value"])
            except ValueError as exc:
                raise DomainError("invalid enum value") from exc
        if "$type" in value:
            cls = _CLASS_BY_NAME.get(value["$type"])
            if cls is None:
                raise DomainError("unknown object type")
            expected = {field.name for field in fields(cls)}
            if set(value) != expected | {"$type"}:
                raise DomainError("object fields differ from schema v1")
            try:
                return cls(**{name: _decode(value[name]) for name in expected})
            except TypeError as exc:
                raise DomainError("invalid object field type") from exc
    raise DomainError("invalid or unrecognized domain encoding")


def to_json(value: object) -> str:
    """Serialize one whitelisted domain object with schema and version."""
    if type(value) not in _CLASSES:
        raise DomainError("top-level value is not a domain object")
    return json.dumps(
        {"schema": SCHEMA, "version": VERSION, "payload": _encode(value)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def from_json(raw: str) -> object:
    """Reject unknown versions/types rather than guessing a migration."""
    try:
        data = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise DomainError("invalid JSON") from exc
    if (
        not isinstance(data, dict)
        or set(data) != {"schema", "version", "payload"}
        or data["schema"] != SCHEMA
        or type(data["version"]) is not int
        or data["version"] != VERSION
    ):
        raise DomainError("unsupported domain schema or version")
    result = _decode(data["payload"])
    if type(result) not in _CLASSES:
        raise DomainError("top-level payload is not a domain object")
    return result
