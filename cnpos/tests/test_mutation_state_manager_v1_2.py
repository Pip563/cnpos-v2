# cnpos/tests/test_mutation_state_manager_v1_2.py

import time
from typing import Any, Dict

import pytest

from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2


@pytest.fixture
def mutation_state_manager() -> MutationStateManagerV1_2:
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
    assert entry["domain"] == "code"
    assert entry["mutation_type"] == "FUNCTION_ADDED"
    assert entry["risk_level"] == "medium"
    assert entry["state_before"] == snapshot

    timeline = mutation_state_manager.get_mutation_timeline("code")
    assert len(timeline) == 1
    assert timeline[0]["mutation_id"] == mutation_id


def test_compute_diff_returns_added_removed_and_changed() -> None:
    before = {"a": 1, "b": 2, "c": 3}
    after = {"a": 1, "b": 9, "d": 4}

    diff = MutationStateManagerV1_2().compute_diff(before=before, after=after)

    assert diff["added"] == {"d": 4}
    assert diff["removed"] == {"c": 3}
    assert diff["changed"]["b"] == {"old": 2, "new": 9}


def test_create_rollback_point_and_restore_snapshot() -> None:
    manager = MutationStateManagerV1_2()
    snapshot = {"module": "core.runtime.backend_manager_v1_2", "status": "ready"}

    manager.create_rollback_point("before-change", snapshot)
    restored = manager.rollback_to("before-change")

    assert restored == snapshot
    assert manager.rollback_to("missing") is None


def test_find_mutation_and_last_mutation() -> None:
    manager = MutationStateManagerV1_2()
    payload = _make_payload(domain="story")
    snapshot = {"story": "draft"}

    mutation_id = manager.record_mutation(
        domain="story",
        mutation_type="PLOT_ADDED",
        payload=payload,
        active_state_snapshot=snapshot,
        impact_summary={"risk_level": "low", "affected_components": ["story"], "notes": "story"},
        risk_level="low",
    )

    assert manager.find_mutation(mutation_id)["mutation_id"] == mutation_id
    assert manager.last_mutation("story")["mutation_id"] == mutation_id
    assert manager.last_mutation()["mutation_id"] == mutation_id


def test_get_mutation_timeline_returns_empty_for_unknown_domain() -> None:
    manager = MutationStateManagerV1_2()
    assert manager.get_mutation_timeline("unknown") == []
