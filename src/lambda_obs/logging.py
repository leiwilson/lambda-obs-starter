"""Structured JSON logging helpers for Lambda-style runtimes."""

from __future__ import annotations

import json
import sys
import time
import uuid
from typing import Any, Mapping, MutableMapping, TextIO


class Logger:
    """Emit one JSON object per line with service and level fields."""

    def __init__(
        self,
        service: str,
        *,
        stream: TextIO | None = None,
        base: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self.service = service
        self.stream = stream or sys.stdout
        self._base: dict[str, Any] = dict(base or {})
        if correlation_id:
            self._base.setdefault("correlation_id", correlation_id)

    def bind(self, **kwargs: Any) -> "Logger":
        merged = {**self._base, **kwargs}
        child = Logger(self.service, stream=self.stream, base=merged)
        return child

    def with_correlation_id(self, correlation_id: str | None = None) -> "Logger":
        """Return a child logger bound to a correlation id (generated if omitted)."""
        cid = correlation_id or str(uuid.uuid4())
        return self.bind(correlation_id=cid)

    def _emit(self, level: str, message: str, **fields: Any) -> None:
        payload: MutableMapping[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "service": self.service,
            "message": message,
        }
        payload.update(self._base)
        payload.update(fields)
        self.stream.write(json.dumps(payload, default=str) + "\n")
        self.stream.flush()

    def debug(self, message: str, **fields: Any) -> None:
        self._emit("DEBUG", message, **fields)

    def info(self, message: str, **fields: Any) -> None:
        self._emit("INFO", message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._emit("WARNING", message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit("ERROR", message, **fields)
