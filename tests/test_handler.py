from types import SimpleNamespace

from lambda_obs.handler import handler


def test_handler_greets_name():
    result = handler({"name": "lei"}, None)
    assert result["ok"] is True
    assert result["message"] == "hello lei"
    assert "correlation_id" in result


def test_handler_default_name():
    result = handler({}, None)
    assert result["message"] == "hello world"


def test_handler_uses_event_correlation_id():
    result = handler({"name": "lei", "correlation_id": "abc-999"}, None)
    assert result["correlation_id"] == "abc-999"


def test_handler_uses_header_correlation_id():
    result = handler(
        {"name": "lei", "headers": {"x-correlation-id": "hdr-1"}},
        None,
    )
    assert result["correlation_id"] == "hdr-1"


def test_handler_uses_context_request_id():
    ctx = SimpleNamespace(aws_request_id="req-42")
    result = handler({"name": "lei"}, ctx)
    assert result["correlation_id"] == "req-42"
