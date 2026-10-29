# cnpos/core/orchestrators/telemetry/event_stream.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventStreamError(Exception):
    """Raised when EventStream encounters an unrecoverable error."""
    pass


class EventStream:
    """
    EventStream

    Lightweight, version-agnostic event bus used by CNPOS v1_2 orchestrators.

    Responsibilities:
    - Accept structured telemetry events from orchestrators and pipelines.
    - Fan out events to registered subscribers (e.g., TelemetryManager, log sinks).
    - Keep event routing simple and deterministic, without encoding v1_2 semantics.

    Notes:
    - This module is intentionally not suffixed with `_v1_2` to remain
      reusable across versions, while still serving v1_2 components.
    """

    def __init__(self) -> None:
        # Subscribers are callables receiving (event_name: str, payload: Dict[str, Any])
        self._subscribers: List[Callable[[str, Dict[str, Any]], None]] = []
        logger.debug("EventStream initialized with 0 subscribers")

    # -------------------------------------------------------------------------
    # Subscription API
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        callback: Callable[[str, Dict[str, Any]], None],
    ) -> None:
        """
        Register a subscriber callback.

        Args:
            callback: Callable that accepts (event_name, payload).

        Raises:
            EventStreamError if callback is not callable.
        """
        if not callable(callback):
            logger.error("EventStream.subscribe received non-callable callback: %r", callback)
            raise EventStreamError("Subscriber callback must be callable")

        self._subscribers.append(callback)
        logger.debug(
            "EventStream.subscribe added subscriber; total_subscribers=%d",
            len(self._subscribers),
        )

    def unsubscribe(
        self,
        callback: Callable[[str, Dict[str, Any]], None],
    ) -> None:
        """
        Unregister a subscriber callback.

        Args:
            callback: Previously registered callable.

        Raises:
            EventStreamError if callback is not found.
        """
        try:
            self._subscribers.remove(callback)
            logger.debug(
                "EventStream.unsubscribe removed subscriber; total_subscribers=%d",
                len(self._subscribers),
            )
        except ValueError as exc:
            logger.error("EventStream.unsubscribe unknown subscriber: %r", callback)
            raise EventStreamError("Subscriber callback not found") from exc

    # -------------------------------------------------------------------------
    # Event publishing API
    # -------------------------------------------------------------------------

    def publish(
        self,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event_name: Name of the event (e.g., 'cnpos_orchestrator_v1_2.run_episode.start').
            payload: Optional structured payload associated with the event.

        Behavior:
            - Logs the event at DEBUG level.
            - Invokes all subscriber callbacks with (event_name, payload_dict).

        Raises:
            EventStreamError if any subscriber raises unexpectedly.
        """
        payload_dict: Dict[str, Any] = payload or {}
        logger.debug(
            "EventStream.publish event_name=%s payload_keys=%s subscribers=%d",
            event_name,
            list(payload_dict.keys()),
            len(self._subscribers),
        )

        for subscriber in list(self._subscribers):
            try:
                subscriber(event_name, payload_dict)
            except Exception as exc:
                logger.error(
                    "EventStream.publish subscriber error for event '%s': %s",
                    event_name,
                    exc,
                    exc_info=True,
                )
                raise EventStreamError(
                    f"Subscriber error while handling event '{event_name}': {exc}"
                ) from exc

    # -------------------------------------------------------------------------
    # Convenience alias used by TelemetryManager
    # -------------------------------------------------------------------------

    def record_event(
        self,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Convenience wrapper around publish(), matching TelemetryManager usage.
        """
        self.publish(event_name, payload)


__all__ = ["EventStream", "EventStreamError"]
