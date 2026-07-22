import io
import json

from lambda_obs.metrics import Metrics


def test_metrics_flush_emits_emf_line():
    buf = io.StringIO()
    m = Metrics("DemoNS", "demo", stream=buf)
    m.add_metric("Invocations", 1)
    payload = m.flush()
    assert payload["Invocations"] == 1.0
    assert payload["service"] == "demo"
    line = json.loads(buf.getvalue().strip())
    assert line["_aws"]["CloudWatchMetrics"][0]["Namespace"] == "DemoNS"
    assert m._values == {}


def test_metrics_add_dimension():
    buf = io.StringIO()
    m = Metrics("DemoNS", "demo", stream=buf)
    m.add_dimension("stage", "dev")
    m.add_metric("Errors", 2)
    payload = m.flush()
    assert payload["stage"] == "dev"
    assert payload["Errors"] == 2.0


def test_metrics_set_metric_is_absolute():
    buf = io.StringIO()
    m = Metrics("DemoNS", "demo", stream=buf)
    m.set_metric("QueueDepth", 5, unit="Count")
    m.set_metric("QueueDepth", 3, unit="Count")
    payload = m.flush()
    assert payload["QueueDepth"] == 3.0


def test_metrics_timing():
    buf = io.StringIO()
    m = Metrics("DemoNS", "demo", stream=buf)
    m.timing("HandlerDuration", 12.5)
    payload = m.flush()
    assert payload["HandlerDuration"] == 12.5
    units = {
        item["Name"]: item["Unit"]
        for item in payload["_aws"]["CloudWatchMetrics"][0]["Metrics"]
    }
    assert units["HandlerDuration"] == "Milliseconds"
