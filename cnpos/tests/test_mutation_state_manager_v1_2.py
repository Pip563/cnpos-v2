# tests/test_mutation_state_manager_v1_2.py

import time
from typing import Any, Dict

import pytest

from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2


@pytest.fixture
def mutation_state_manager() -> MutationStateManagerV1_2:
    """
    Provide a fresh MutationStateManagerV1_2 instance for each test.

    MutationStateManagerV1_2 is responsible for:
    - Tracking all mutations applied to the system
    - Providing mutation history per domain
    - Providing mutation diffs (old → new)
    - Providing rollback snapshots
    - Providing mutation timelines for continuity + governance
    - Integrating with orchestrator + validator pipeline
    """
    return MutationStateManagerV1_2()


def _make_payload(domain: str = "code") -> Dict[str, Any]:
    return {
        "domain": domain,
        "change": "FUNCTION_ADDED",
        "details": {"name": "foo", "signature": "foo(x: int) -> int"},
    }


def _make_state_snapshot() -> Dict[str, Any]:
    return {
        "module": "core.validators.validator_pipeline_v1_2",
        "functions": ["validate", "run"],
    }


def _make_impact_summary(risk: str = "medium") -> Dict[str, Any]:
    return {
        "risk_level": risk,
        "affected_components": ["validator_pipeline_v1_2"],
        "notes": "Test mutation impact summary.",
    }


# ----------------------------------------------------------------------
# record_mutation: global log + domain timelines
# ----------------------------------------------------------------------


def test_record_mutation_tracks_global_and_domain_timeline(
    mutation_state_manager: MutationStateManagerV1_2,
) -> None:
    payload = _make_payload(domain="code")
    snapshot = _make_state_snapshot()
    impact = _make_impact_summary(risk="medium")

    mutation_id = mutation_state_manager.record_mutation(
        domain="code",
        mutation_type="FUNCTION_ADDED",
        payload=payload,
        active_state_snapshot=snapshot,
        impact_summary=impact,
        risk_level="medium",
    )

    assert isinstance(mutation_id, str)
    assert mutation_id

    global_log = mutation_state_manager.get_global_mutation_log()
    assert len(global_log) == 1

    entry = global_log[0]
    assert entry["mutation_id"] == mutation_id
    assert entry["domain
