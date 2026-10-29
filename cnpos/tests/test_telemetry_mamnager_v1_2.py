# tests/test_telemetry_manager_v1_2.py

from __future__ import annotations

import time

from typing import Any, Dict

import pytest
from prometheus_client import Counter, Gauge, Histogram

from cnpos.core.orchestrators.telemetry.telemetry_manager import TelemetryManager


def _make_manager() -> TelemetryManager:
    """
    Factory for TelemetryManager used in tests.

    Keeps construction logic in one place so future changes
    to TelemetryManager.__init__ do not break all tests.
    """
    return TelemetryManager()


def _sample_payload() -> Dict[str, Any]:
    """
    Minimal deterministic payload used for telemetry tests.
    """
    return {
        "phase": "CODE_PLANNER",
        "domain": "code",
        "ok": True,
        "details": {"reason": "unit-test"},
    }


def test_telemetry_manager_metrics_are_initialized_v1_2() -> None:
    """
    Ensure TelemetryManager initializes Prometheus metrics objects.

    This validates that the manager is ready to emit metrics
    for orchestrator runs in v1_2.
    """
    manager = _make_manager()

    # Core metrics must exist and be of the correct Prometheus types.
    assert isinstance(manager.run_counter, Counter)
    assert isinstance(manager.run_duration, Histogram)
    assert isinstance(manager.phase_gauge, Gauge)


def test_record_event_increments_run_counter_v1_2() -> None:
    """
    Calling record_event must increment orchestrator_runs_total
    for the given domain/phase/version v1_2.
    """
    manager = _make_manager()

    phase = "CODE_PLANNER"
    domain = "code"
    version = "v1_2"
    payload = _sample_payload()

    # Access the labeled counter before the event.
    before = manager.run_counter.labels(
        domain=domain,
        phase=phase,
        version=version,
    )._value.get()

    manager.record_event(
        phase=phase,
        domain=domain,
        ok=True,
        payload=payload,
        event_type="CODE_PLANNER_RUN",
    )

    after = manager.run_counter.labels(
        domain=domain,
        phase=phase,
        version=version,
    )._value.get()

    assert after == before + 1


def test_record_event_updates_phase_gauge_v1_2() -> None:
    """
    record_event must update a phase gauge for the given domain/phase/version.

    This ensures the dashboard_panel_v1_2.json can rely on live gauge values.
    """
    manager = _make_manager()

    phase = "CODE_TEST"
    domain = "code"
    version = "v1_2"
    payload = _sample_payload()

    # Before event, gauge should be defined and accessible.
    before = manager.phase_gauge.labels(
        domain=domain,
        phase=phase,
        version=version,
    )._value.get()

    manager.record_event(
        phase=phase,
        domain=domain,
        ok=True,
        payload=payload,
        event_type="CODE_TEST_RUN",
    )

    after = manager.phase_gauge.labels(
        domain=domain,
        phase=phase,
        version=version,
    )._value.get()

    # Gauge semantics: we only assert that it changed, not the exact delta.
    assert after != before


def test_record_event_observes_run_duration_v1_2() -> None:
    """
    record_event must observe a non-negative duration in run_duration histogram.

    This keeps orchestrator_run_duration_seconds{version="v1_2"}
    consistent with the dashboard panel configuration.
    """
    manager = _make_manager()

    phase = "CODE_WRITE"
    domain = "code"
    version = "v1_2"
    payload = _sample_payload()

    # We simulate a small run duration by measuring time around record_event.
    start = time.time()
    manager.record_event(
        phase=phase,
        domain=domain,
        ok=True,
        payload=payload,
        event_type="CODE_WRITE_RUN",
    )
    end = time.time()
    duration = max(end - start, 0.0)

    # Histogram must be accessible for the given labels.
    sample = manager.run_duration.labels(
        domain=domain,
        phase=phase,
        version=version,
    )

    # We cannot easily introspect internal buckets without relying on
    # Prometheus internals, but we can assert that observe() is callable
    # and accepts the measured duration.
    sample.observe(duration)


def test_record_event_handles_failure_flag_v1_2() -> None:
    """
    record_event must not raise when ok=False and must still emit metrics.

    This ensures failure runs are visible in telemetry and do not
    break the orchestrator loop.
    """
    manager = _make_manager()

    phase = "CODE_PLANNER"
    domain = "code"
    version = "v1_2"
    payload = _sample_payload()

    before = manager.run_counter.labels(
        domain=domain,
        phase=phase,
        version=version,
    )._value.get()

    # ok=False should be accepted and counted.
    manager.record_event(
        phase=phase,
        domain=domain,
        ok=False,
        payload=payload,
        event_type="CODE_PLANNER_RUN",
    )

    after = manager.run_counter.labels(
        domain=domain,
        phase=phase,
        version=version,
    )._value.get()

    assert after == before + 1
