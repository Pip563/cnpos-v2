# cnpos/core/orchestrators/telemetry/telemetry_manager.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.orchestrators.telemetry.event_stream import EventStream
from cnpos.core.orchestrators.telemetry.metrics_exporter import (
    OrchestratorMetricsExporter,
)

logger = logging.getLogger(__name__)


class TelemetryManagerError(Exception):
    """Raised when TelemetryManager encounters an unrecoverable error."""
    pass


class TelemetryManager:
    """
    TelemetryManager

    Version-agnostic telemetry coordinator for CNPOS v1_2 orchestrators.

    Responsibilities:
    - Provide a simple facade for recording events and metrics.
    - Wire EventStream and OrchestratorMetricsExporter together.
    - Keep telemetry infrastructure stable across versions while serving v1_2
      pipelines and orchestrators.

    Notes:
    - Module is intentionally not suffixed with `_v1_2`; event and metric names
      themselves can carry `v1_2` suffixes.
    """

    def __init__(
        self,
        event_stream: Optional[EventStream] = None,
        metrics_exporter: Optional[OrchestratorMetricsExporter] = None,
    ) -> None:
        self._event_stream = event_stream or EventStream()
        self._metrics_exporter = metrics_exporter or OrchestratorMetricsExporter()

        logger.debug(
            "TelemetryManager initialized with event_stream=%s, metrics_exporter=%s",
            self._event_stream,
            self._metrics_exporter,
        )

    # -------------------------------------------------------------------------
    # Event API
    # -------------------------------------------------------------------------

    def record_event(
        self,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record an event via EventStream.

        Args:
            event_name: Name of the event.
            payload: Optional structured payload.
        """
        logger.debug(
            "TelemetryManager.record_event event_name=%s payload_keys=%s",
            event_name,
            list((payload or {}).keys()),
        )
        try:
            self._event_stream.record_event(event_name, payload or {})
        except Exception as exc:
            logger.error(
                "TelemetryManager.record_event error for event '%s': %s",
                event_name,
                exc,
                exc_info=True,
            )
            raise TelemetryManagerError(
                f"Error while recording event '{event_name}': {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Metrics API
    # -------------------------------------------------------------------------

    def increment_metric(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Increment a counter metric via OrchestratorMetricsExporter.
        """
        logger.debug(
            "TelemetryManager.increment_metric name=%s value=%s labels=%s",
            name,
            value,
            labels or {},
        )
        try:
            self._metrics_exporter.increment(name, value, labels)
        except Exception as exc:
            logger.error(
                "TelemetryManager.increment_metric error for metric '%s': %s",
                name,
                exc,
                exc_info=True,
            )
            raise TelemetryManagerError(
                f"Error while incrementing metric '{name}': {exc}"
            ) from exc

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Set a gauge metric via OrchestratorMetricsExporter.
        """
        logger.debug(
            "TelemetryManager.set_gauge name=%s value=%s labels=%s",
            name,
            value,
            labels or {},
        )
        try:
            self._metrics_exporter.set_gauge(name, value, labels)
        except Exception as exc:
            logger.error(
                "TelemetryManager.set_gauge error for metric '%s': %s",
                name,
                exc,
                exc_info=True,
            )
            raise TelemetryManagerError(
                f"Error while setting gauge '{name}': {exc}"
            ) from exc

    def observe_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Observe a distribution metric via OrchestratorMetricsExporter.
        """
        logger.debug(
            "TelemetryManager.observe_metric name=%s value=%s labels=%s",
            name,
            value,
            labels or {},
        )
        try:
            self._metrics_exporter.observe(name, value, labels)
        except Exception as exc:
            logger.error(
                "TelemetryManager.observe_metric error for metric '%s': %s",
                name,
                exc,
                exc_info=True,
            )
            raise TelemetryManagerError(
                f"Error while observing metric '{name}': {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Accessors (useful for tests / advanced wiring)
    # -------------------------------------------------------------------------

    @property
    def event_stream(self) -> EventStream:
        """Expose the underlying EventStream instance."""
        return self._event_stream

    @property
    def metrics_exporter(self) -> OrchestratorMetricsExporter:
        """Expose the underlying OrchestratorMetricsExporter instance."""
        return self._metrics_exporter


__all__ = ["TelemetryManager", "TelemetryManagerError"]
