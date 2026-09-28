"""Typed, fail-closed configuration for the still-inert target package."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class ConfigurationError(ValueError):
    """A requested mode or permission is invalid or unsafe."""


class TradingMode(StrEnum):
    """Recognized operating modes; Phase 01 implements none of their execution paths."""

    DISABLED = "disabled"
    PAPER = "paper"
    SHADOW = "shadow"
    LIVE = "live"


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated startup settings without credentials or account identifiers."""

    trading_mode: TradingMode = TradingMode.DISABLED


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Parse settings; Phase 01 rejects live even when an enable flag is supplied."""
    values = os.environ if environ is None else environ
    raw_mode = values.get("TRADING_MODE", TradingMode.DISABLED.value)
    try:
        mode = TradingMode(raw_mode)
    except ValueError as exc:
        raise ConfigurationError("TRADING_MODE must be disabled, paper, shadow or live") from exc

    raw_allowed = values.get("TRADING_LIVE_ALLOWED", "false")
    if raw_allowed not in {"true", "false"}:
        raise ConfigurationError("TRADING_LIVE_ALLOWED must be exactly true or false")
    if mode is TradingMode.LIVE and raw_allowed != "true":
        raise ConfigurationError("live mode requires explicit TRADING_LIVE_ALLOWED=true")
    if mode is TradingMode.LIVE or raw_allowed == "true":
        raise ConfigurationError("live functionality is unavailable in Phase 01")
    return Settings(trading_mode=mode)
