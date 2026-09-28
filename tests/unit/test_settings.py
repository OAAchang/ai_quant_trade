"""Fail-closed settings behavior at the environment boundary."""

import pytest

from ai_quant_trade.settings import ConfigurationError, Settings, TradingMode, load_settings


def test_default_is_disabled() -> None:
    assert load_settings({}) == Settings()
    assert load_settings({}).trading_mode is TradingMode.DISABLED


@pytest.mark.parametrize("raw_mode", ["LIVE", "unexpected", "", "paper "])
def test_invalid_mode_fails(raw_mode: str) -> None:
    with pytest.raises(ConfigurationError, match="TRADING_MODE"):
        load_settings({"TRADING_MODE": raw_mode})


def test_live_requires_explicit_permission() -> None:
    with pytest.raises(ConfigurationError, match="requires explicit"):
        load_settings({"TRADING_MODE": "live"})


@pytest.mark.parametrize("raw_allowed", ["1", "yes", "True", "", "TRUE"])
def test_permission_flag_is_strict(raw_allowed: str) -> None:
    with pytest.raises(ConfigurationError, match="TRADING_LIVE_ALLOWED"):
        load_settings({"TRADING_LIVE_ALLOWED": raw_allowed})


@pytest.mark.parametrize("raw_mode", ["disabled", "live"])
def test_explicit_live_flag_still_fails_closed(raw_mode: str) -> None:
    with pytest.raises(ConfigurationError, match="unavailable in Phase 01"):
        load_settings({"TRADING_MODE": raw_mode, "TRADING_LIVE_ALLOWED": "true"})
