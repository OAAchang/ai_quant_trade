"""Structured logging initializer with no implicit configuration at import time."""

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import TextIO

_KEY_VALUE_SECRET = re.compile(
    r"(?i)\b(api[_-]?key|password|token|secret|account[_-]?id)\s*[:=]\s*\S+"
)
_GITHUB_TOKEN = re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{36}\b")


class JsonFormatter(logging.Formatter):
    """Emit stable JSON fields without serializing arbitrary record attributes."""

    def format(self, record: logging.LogRecord) -> str:
        """Format one event with an aware UTC timestamp."""
        message = _KEY_VALUE_SECRET.sub(
            lambda match: f"{match.group(1)}=[REDACTED]", record.getMessage()
        )
        message = _GITHUB_TOKEN.sub("[REDACTED]", message)
        return json.dumps(
            {
                "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": message,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )


def configure_logging(*, level: int = logging.INFO, stream: TextIO | None = None) -> logging.Logger:
    """Configure only the package logger and replace only handlers installed by this function."""
    logger = logging.getLogger("ai_quant_trade")
    for handler in tuple(logger.handlers):
        if getattr(handler, "_ai_quant_trade_managed", False):
            logger.removeHandler(handler)
            handler.close()
    handler = logging.StreamHandler(sys.stderr if stream is None else stream)
    handler.setFormatter(JsonFormatter())
    handler._ai_quant_trade_managed = True  # type: ignore[attr-defined]
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger
