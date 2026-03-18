"""Lightweight metrics helper (EMF-inspired, original implementation)."""

from __future__ import annotations

import json
import sys
import time
from typing import Any, MutableMapping, TextIO


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
        self._metrics: dict[str, float] = {}
        self._dimensions: dict[str, str] = {"service": service}

    def add_dimension(self, key: str, value: str) -> None:
        self._dimensions[key] = value

    def add_metric(self, name: str, value: float, unit: str = "Count") -> None:
        # unit kept for callers; aggregated value is numeric only in buffer
        self._metrics[name] = self._metrics.get(name, 0.0) + float(value)
        self._metrics[f"{name}__unit"] = unit  # type: ignore[assignment]

    def clear(self) -> None:
        self._metrics.clear()

    def serialize(self) -> dict[str, Any]:
        metrics: dict[str, Any] = {}
        units: dict[str, str] = {}
        for key, value in self._metrics.items():
            if key.endswith("__unit"):
                units[key[:-6]] = str(value)
            else:
                metrics[key] = value
        return {
            "_aws": {
                "Timestamp": int(time.time() * 1000),
                "CloudWatchMetrics": [
                    {
                        "Namespace": self.namespace,
                        "Dimensions": [list(self._dimensions.keys())],
                        "Metrics": [
                            {"Name": name, "Unit": units.get(name, "Count")}
                            for name in metrics
                        ],
                    }
                ],
            },
            **self._dimensions,
            **metrics,
        }

    def flush(self) -> dict[str, Any]:
        payload = self.serialize()
        self.stream.write(json.dumps(payload, default=str) + "\n")
        self.stream.flush()
        self.clear()
        return payload
