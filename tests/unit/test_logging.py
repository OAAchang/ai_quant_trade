"""Structured logging initialization tests."""

import io
import json
from datetime import datetime

from ai_quant_trade.logging import configure_logging


def test_json_log_is_aware_and_handler_is_not_duplicated() -> None:
    first = io.StringIO()
    logger = configure_logging(stream=first)
    logger.info("foundation ready")
    event = json.loads(first.getvalue())
    assert event["level"] == "INFO"
    assert event["logger"] == "ai_quant_trade"
    assert event["message"] == "foundation ready"
    assert datetime.fromisoformat(event["timestamp"]).tzinfo is not None

    second = io.StringIO()
    configure_logging(stream=second)
    logger.info("second")
    assert first.getvalue().count("second") == 0
    assert second.getvalue().count("second") == 1
    assert len(logger.handlers) == 1


def test_common_key_value_secret_is_redacted() -> None:
    output = io.StringIO()
    logger = configure_logging(stream=output)
    logger.warning("token=%s", "do-not-log-me")
    event = json.loads(output.getvalue())
    assert event["message"] == "token=[REDACTED]"
    assert "do-not-log-me" not in output.getvalue()
