"""Example Lambda handler using structured logging and metrics."""

from __future__ import annotations

import time
from typing import Any

from .logging import Logger
from .metrics import Metrics

logger = Logger(service="lambda-obs-starter")
metrics = Metrics(namespace="LambdaObsStarter", service="lambda-obs-starter")


def _request_id(event: dict[str, Any], context: Any) -> str | None:
    if context is not None and getattr(context, "aws_request_id", None):
        return str(context.aws_request_id)
    headers = (event or {}).get("headers") or {}
    for key in ("x-correlation-id", "X-Correlation-Id", "x-request-id"):
        if key in headers and headers[key]:
            return str(headers[key])
    return (event or {}).get("correlation_id")


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """Handle a simple greeting event.

    Expected event shape: ``{"name": "world"}``.
    Optional correlation via ``correlation_id`` or ``headers.x-correlation-id``.
    """
    started = time.perf_counter()
    name = (event or {}).get("name") or "world"
    cid = _request_id(event or {}, context)
    bound = logger.with_correlation_id(cid).bind(function="handler")
    if cid:
        metrics.add_dimension("correlation_present", "true")
    bound.info("invocation started", name=name)

    metrics.add_metric("Invocations", 1, unit="Count")
    try:
        greeting = f"hello {name}"
        metrics.add_metric("Success", 1, unit="Count")
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        metrics.timing("HandlerDuration", elapsed_ms)
        bound.info("invocation succeeded", greeting=greeting, duration_ms=round(elapsed_ms, 3))
        return {"ok": True, "message": greeting, "correlation_id": bound._base.get("correlation_id")}
    except Exception as exc:  # pragma: no cover - defensive
        metrics.add_metric("Errors", 1, unit="Count")
        bound.error("invocation failed", error=str(exc))
        raise
    finally:
        metrics.flush()
