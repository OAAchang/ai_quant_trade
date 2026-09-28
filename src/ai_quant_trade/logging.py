"""Structured logging initializer with no implicit configuration at import time."""

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import TextIO

_KEY_VALUE_SECRET = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?P<key_quote>['\"]?)"
    r"(?P<key>api[_-]?key|password|token|secret|account[_-]?id)"
    r"(?P=key_quote)\s*[:=]\s*"
    r"(?P<value>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|[^\s,}\]]+)"
)
_GITHUB_TOKEN = re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{36}\b")


def _redact_text(value: str) -> str:
    """Redact supported key/value formats and GitHub token shapes."""

    def replace(match: re.Match[str]) -> str:
        raw = match.group("value")
        quote = raw[0] if raw[0] in {"'", '"'} else ""
        return f"{match.group(0)[: -len(raw)]}{quote}[REDACTED]{quote}"

    return _GITHUB_TOKEN.sub("[REDACTED]", _KEY_VALUE_SECRET.sub(replace, value))


class JsonFormatter(logging.Formatter):
    """Emit stable JSON fields without serializing arbitrary record attributes."""

    def format(self, record: logging.LogRecord) -> str:
        """Format one event with an aware UTC timestamp."""
        event = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": _redact_text(record.getMessage()),
        }
        if record.exc_info:
            event["exception"] = _redact_text(self.formatException(record.exc_info))
        if record.stack_info:
            event["stack"] = _redact_text(record.stack_info)
        return json.dumps(event, ensure_ascii=False, separators=(",", ":"))


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
