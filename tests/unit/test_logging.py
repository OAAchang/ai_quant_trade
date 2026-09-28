"""Structured logging initialization tests."""

import io
import json
from datetime import datetime

import pytest

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


@pytest.mark.parametrize(
    ("message", "secret"),
    [
        ('{"token": "REVIEW_FAKE"}', "REVIEW_FAKE"),
        ("{'password': 'REVIEW_FAKE'}", "REVIEW_FAKE"),
        ('password="REVIEW FAKE"', "REVIEW FAKE"),
        ("api_key=REVIEW_FAKE", "REVIEW_FAKE"),
    ],
)
def test_quoted_and_serialized_secrets_are_fully_redacted(message: str, secret: str) -> None:
    output = io.StringIO()
    logger = configure_logging(stream=output)
    logger.warning(message)
    event = json.loads(output.getvalue())
    assert secret not in event["message"]
    assert "[REDACTED]" in event["message"]


def test_exception_chain_and_stack_are_preserved_but_redacted() -> None:
    output = io.StringIO()
    logger = configure_logging(stream=output)
    try:
        try:
            raise ValueError('password="REVIEW FAKE"')
        except ValueError as cause:
            raise RuntimeError("outer failure") from cause
    except RuntimeError:
        logger.exception("operation failed", stack_info=True)
    event = json.loads(output.getvalue())
    assert "RuntimeError: outer failure" in event["exception"]
    assert "ValueError: password=" in event["exception"]
    assert "direct cause" in event["exception"]
    assert "Traceback" in event["exception"]
    assert "Stack (most recent call last)" in event["stack"]
    assert "REVIEW FAKE" not in output.getvalue()
