import io
import json

from lambda_obs.logging import Logger


def test_logger_emits_json_line():
    buf = io.StringIO()
    log = Logger("demo", stream=buf)
    log.info("hello", request_id="abc")
    line = buf.getvalue().strip()
    payload = json.loads(line)
    assert payload["level"] == "INFO"
    assert payload["service"] == "demo"
    assert payload["message"] == "hello"
    assert payload["request_id"] == "abc"
    assert "timestamp" in payload


def test_logger_bind_adds_fields():
    buf = io.StringIO()
    log = Logger("demo", stream=buf).bind(cold_start=True)
    log.warning("slow")
    payload = json.loads(buf.getvalue().strip())
    assert payload["cold_start"] is True
    assert payload["level"] == "WARNING"


def test_logger_with_correlation_id():
    buf = io.StringIO()
    log = Logger("demo", stream=buf).with_correlation_id("corr-123")
    log.info("traced")
    payload = json.loads(buf.getvalue().strip())
    assert payload["correlation_id"] == "corr-123"


def test_logger_generates_correlation_id():
    buf = io.StringIO()
    log = Logger("demo", stream=buf).with_correlation_id()
    log.info("traced")
    payload = json.loads(buf.getvalue().strip())
    assert "correlation_id" in payload
    assert len(payload["correlation_id"]) > 0
