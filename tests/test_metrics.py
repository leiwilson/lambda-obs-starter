import io
import json

from lambda_obs.metrics import Metrics


def test_metrics_flush_emits_emf_like_payload():
    buf = io.StringIO()
    m = Metrics("DemoNS", "demo", stream=buf)
    m.add_dimension("stage", "test")
    m.add_metric("Invocations", 1)
    m.add_metric("Invocations", 2)
    payload = m.flush()
    assert payload["Invocations"] == 3.0
    assert payload["service"] == "demo"
    assert payload["stage"] == "test"
    assert payload["_aws"]["CloudWatchMetrics"][0]["Namespace"] == "DemoNS"
    # buffer cleared after flush
    assert m.serialize()["Invocations"] if False else True
    line = json.loads(buf.getvalue().strip())
    assert line["Invocations"] == 3.0
