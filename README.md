# lambda-obs-starter

Minimal AWS Lambda starter with **structured JSON logging**, a small **metrics helper**, and **local unit tests**. No AWS account or credentials required.

## Features

- Structured logger that emits one JSON object per line (CloudWatch-friendly)
- Correlation IDs for tracing a single invocation across log lines
- Simple EMF-style metrics buffer you can flush as a log line (counters, gauges, timings)
- Example Lambda handler wiring logger + metrics
- Pure unit tests (no network, no AWS credentials)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Handler example

```python
from lambda_obs.handler import handler

result = handler({"name": "world", "correlation_id": "demo-1"}, None)
print(result)  # {"message": "hello world", "ok": true, "correlation_id": "demo-1"}
```

Pass a correlation id via event field, `headers.x-correlation-id`, or Lambda `context.aws_request_id`.

## Layout

```
src/lambda_obs/
  logging.py   # structured JSON logger + correlation ids
  metrics.py   # metrics helper (count / set / timing)
  handler.py   # example Lambda entrypoint
tests/
.github/workflows/ci.yml
```

## Operations

### Structured logs in CloudWatch

Each log line is a single JSON object. Filter and explore with CloudWatch Logs Insights, for example:

```
fields @timestamp, level, message, correlation_id
| filter ispresent(correlation_id)
| sort @timestamp desc
| limit 50
```

### Metrics (EMF)

`Metrics.flush()` writes an Embedded Metric Format line to stdout. In Lambda, CloudWatch extracts the namespace, dimensions, and metric values automatically—no extra agent required.

Useful starter metrics from the example handler:

- `Invocations` / `Success` / `Errors` (Count)
- `HandlerDuration` (Milliseconds)

### Correlation

Prefer one correlation id per request. Propagate it to downstream calls and keep it on every log line via `Logger.with_correlation_id(...)`.

### Local vs deployed

| Concern | Local | Deployed Lambda |
| --- | --- | --- |
| Credentials | Not required for unit tests | Execution role only |
| Logs | stdout / captured in tests | CloudWatch Logs |
| Metrics | JSON line on stdout | EMF → CloudWatch Metrics |

### CI

GitHub Actions runs `pytest` across Python 3.10–3.12 on pushes and pull requests to `main` and `develop`.

## Design notes

Inspired by the *ideas* behind AWS Lambda Powertools (structured logs + custom metrics), but this is an original, tiny teaching scaffold — not a fork or copy of AWS Powertools code.

## License

MIT

## Local testing

Unit tests are credential-free and do not call AWS. Run `pytest -q` after installing with `pip install -e ".[dev]"`.
