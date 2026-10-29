# cnpos/core/orchestrators/telemetry/metrics_exporter.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class OrchestratorMetricsExporterError(Exception):
    """Raised when OrchestratorMetricsExporter encounters an unrecoverable error."""
    pass


class OrchestratorMetricsExporter:
    """
    OrchestratorMetricsExporter

    Lightweight, version-agnostic metrics facade used by CNPOS v1_2 orchestrators.

    Responsibilities:
    - Provide a simple API for counters and gauges (increment, set, observe).
    - Act as an integration point for real metrics backends (Prometheus, StatsD, etc.).
    - Keep telemetry infrastructure stable across versions while serving v1_2 components.

    Notes:
    - This module is intentionally not suffixed with `_v1_2` to remain reusable
      across versions, while metric names themselves can carry `v1_2` suffixes.
    """

    def __init__(self) -> None:
        # Internal in-memory store; can be replaced by a real backend integration.
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        logger.debug("OrchestratorMetricsExporter initialized")

    # -------------------------------------------------------------------------
    # Counter API
    # -------------------------------------------------------------------------

    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, Any]] = None) -> None:
        """
        Increment a counter metric.

        Args:
            name: Metric name (e.g., 'cnpos_orchestrator_v1_2.episode_runs').
            value: Amount to increment by (default: 1.0).
            labels: Optional label dict for future backend integrations.
        """
        current = self._counters.get(name, 0.0)
        new_value = current + value
        self._counters[name] = new_value

        logger.debug(
            "OrchestratorMetricsExporter.increment name=%s value=%s new_total=%s labels=%s",
            name,
            value,
            new_value,
            labels or {},
        )

    # -------------------------------------------------------------------------
    # Gauge API
    # -------------------------------------------------------------------------

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, Any]] = None) -> None:
        """
        Set a gauge metric to a specific value.

        Args:
            name: Metric name.
            value: Gauge value.
            labels: Optional label dict for future backend integrations.
        """
        self._gauges[name] = value
        logger.debug(
            "OrchestratorMetricsExporter.set_gauge name=%s value=%s labels=%s",
            name,
            value,
            labels or {},
        )

    # -------------------------------------------------------------------------
    # Observation / timing API (no-op placeholder)
    # -------------------------------------------------------------------------

    def observe(self, name: str, value: float, labels: Optional[Dict[str, Any]] = None) -> None:
        """
        Observe a value for a distribution metric (e.g., latency).

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional label dict.

        Behavior:
            - Currently logs the observation; can be wired to histograms in a real backend.
        """
        logger.debug(
            "OrchestratorMetricsExporter.observe name=%s value=%s labels=%s",
            name,
            value,
            labels or {},
        )

    # -------------------------------------------------------------------------
    # Introspection helpers (useful for tests)
    # -------------------------------------------------------------------------

    def get_counter(self, name: str) -> float:
        """
        Return the current value of a counter (primarily for tests).
        """
        return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float:
        """
        Return the current value of a gauge (primarily for tests).
        """
        return self._gauges.get(name, 0.0)


__all__ = ["OrchestratorMetricsExporter", "OrchestratorMetricsExporterError"]
