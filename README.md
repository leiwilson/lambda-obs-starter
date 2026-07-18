# lambda-obs-starter

Minimal AWS Lambda starter with **structured JSON logging**, a small **metrics helper**, and **local unit tests**. No AWS account or credentials required.

## Features

- Structured logger that emits one JSON object per line (CloudWatch-friendly)
- Simple EMF-style metrics buffer you can flush as a log line
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

result = handler({"name": "world"}, None)
print(result)  # {"message": "hello world", "ok": true}
```

## Layout

```
src/lambda_obs/
  logging.py   # structured JSON logger
  metrics.py   # metrics helper
  handler.py   # example Lambda entrypoint
tests/
.github/workflows/ci.yml
```

## Design notes

Inspired by the *ideas* behind AWS Lambda Powertools (structured logs + custom metrics), but this is an original, tiny teaching scaffold — not a fork or copy of AWS Powertools code.

## License

MIT

## Local testing

Unit tests are credential-free and do not call AWS. Run `pytest -q` after installing with `pip install -e ".[dev]"`.
