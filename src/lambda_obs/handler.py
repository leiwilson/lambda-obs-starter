"""Example Lambda handler using structured logging and metrics."""

from __future__ import annotations

from typing import Any

from .logging import Logger
from .metrics import Metrics

logger = Logger(service="lambda-obs-starter")
metrics = Metrics(namespace="LambdaObsStarter", service="lambda-obs-starter")


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """Handle a simple greeting event.

    Expected event shape: ``{"name": "world"}``.
    """
    name = (event or {}).get("name") or "world"
    bound = logger.bind(function="handler")
    bound.info("invocation started", name=name)

    metrics.add_metric("Invocations", 1, unit="Count")
    try:
        greeting = f"hello {name}"
        metrics.add_metric("Success", 1, unit="Count")
        bound.info("invocation succeeded", greeting=greeting)
        return {"ok": True, "message": greeting}
    except Exception as exc:  # pragma: no cover - defensive
        metrics.add_metric("Errors", 1, unit="Count")
        bound.error("invocation failed", error=str(exc))
        raise
    finally:
        metrics.flush()
