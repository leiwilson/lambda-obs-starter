from lambda_obs.handler import handler


def test_handler_greets_name():
    result = handler({"name": "lei"}, None)
    assert result["ok"] is True
    assert result["message"] == "hello lei"


def test_handler_default_name():
    result = handler({}, None)
    assert result["message"] == "hello world"
