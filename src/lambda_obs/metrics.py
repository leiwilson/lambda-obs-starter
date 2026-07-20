"""Lightweight metrics helper (EMF-inspired, original implementation)."""

from __future__ import annotations

import json
import sys
import time
from typing import Any, TextIO


class Metrics:
    """Collect counters/gauges and flush them as a single JSON metrics line."""

    def __init__(
        self,
        namespace: str,
        service: str,
        *,
        stream: TextIO | None = None,
    ) -> None:
        self.namespace = namespace
        self.service = service
        self.stream = stream or sys.stdout
        self._values: dict[str, float] = {}
        self._units: dict[str, str] = {}
        self._dimensions: dict[str, str] = {"service": service}

    def add_dimension(self, key: str, value: str) -> None:
        self._dimensions[key] = value

    def add_metric(self, name: str, value: float, unit: str = "Count") -> None:
        self._values[name] = self._values.get(name, 0.0) + float(value)
        self._units[name] = unit

    def clear(self) -> None:
        self._values.clear()
        self._units.clear()

    def serialize(self) -> dict[str, Any]:
        return {
            "_aws": {
                "Timestamp": int(time.time() * 1000),
                "CloudWatchMetrics": [
                    {
                        "Namespace": self.namespace,
                        "Dimensions": [list(self._dimensions.keys())],
                        "Metrics": [
                            {"Name": name, "Unit": self._units.get(name, "Count")}
                            for name in self._values
                        ],
                    }
                ],
            },
            **self._dimensions,
            **self._values,
        }

    def flush(self) -> dict[str, Any]:
        payload = self.serialize()
        self.stream.write(json.dumps(payload, default=str) + "\n")
        self.stream.flush()
        self.clear()
        return payload
