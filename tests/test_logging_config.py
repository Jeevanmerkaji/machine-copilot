import json
import logging

import pytest

from app.logging_config import JsonFormatter, setup_logging


@pytest.fixture
def isolated_root_logger():
    """setup_logging() mutates the global root logger — snapshot and restore
    it so a test exercising that function doesn't leak handlers/levels into
    every test that runs afterward in the same session."""
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    yield root
    root.handlers.clear()
    root.handlers.extend(original_handlers)
    root.setLevel(original_level)


def _make_record(message="hello", **extra):
    record = logging.LogRecord(
        name="test.logger",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_produces_valid_json_with_core_fields():
    record = _make_record("something happened")
    line = JsonFormatter().format(record)
    payload = json.loads(line)
    assert payload["message"] == "something happened"
    assert payload["level"] == "WARNING"
    assert payload["logger"] == "test.logger"
    assert "timestamp" in payload


def test_json_formatter_merges_extra_fields():
    record = _make_record("blocked", matched_rule="bypass + interlock")
    payload = json.loads(JsonFormatter().format(record))
    assert payload["matched_rule"] == "bypass + interlock"


def test_json_formatter_includes_exception_info():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _make_record("failed")
        record.exc_info = sys.exc_info()
    payload = json.loads(JsonFormatter().format(record))
    assert "ValueError" in payload["exc_info"]
    assert "boom" in payload["exc_info"]


def test_setup_logging_uses_json_formatter_when_configured(monkeypatch, isolated_root_logger):
    from app.logging_config import settings

    monkeypatch.setattr(settings, "log_format", "json")
    monkeypatch.setattr(settings, "log_level", "DEBUG")
    setup_logging()
    assert isinstance(isolated_root_logger.handlers[0].formatter, JsonFormatter)
    assert isolated_root_logger.level == logging.DEBUG


def test_setup_logging_uses_text_formatter_by_default(monkeypatch, isolated_root_logger):
    from app.logging_config import settings

    monkeypatch.setattr(settings, "log_format", "text")
    monkeypatch.setattr(settings, "log_level", "INFO")
    setup_logging()
    assert not isinstance(isolated_root_logger.handlers[0].formatter, JsonFormatter)
