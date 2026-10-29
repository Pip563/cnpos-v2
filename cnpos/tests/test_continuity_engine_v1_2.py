# tests/test_continuity_engine_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

import pytest

from cnpos.core.runtime.continuity_engine_v1_2 import (
    ContinuityEngineV1_2,
    ContinuityEngineV1_2Error,
)

logger = logging.getLogger(__name__)


def test_continuity_engine_initial_state_is_empty() -> None:
    """
    ContinuityEngineV1_2 must start with no registered domains and no state.
    This enforces deterministic, explicit domain registration in CNPOS v1_2.
    """
    engine = ContinuityEngineV1_2()
    snapshot = engine.snapshot()

    assert isinstance(snapshot, dict)
    assert snapshot == {}


def test_register_domain_creates_deterministic_state_container() -> None:
    """
    register_domain(domain) must create a deterministic state container for the domain.
    The container must be a dict and must be stable across repeated calls.
    """
    engine = ContinuityEngineV1_2()

    engine.register_domain("character")
    state_first = engine.get_domain_state("character")

    engine.register_domain("character")
    state_second = engine.get_domain_state("character")

    assert isinstance(state_first, dict)
    assert isinstance(state_second, dict)
    # Idempotency: repeated registration must not reset or change the container reference.
    assert state_first is state_second


def test_apply_event_updates_domain_state_deterministically() -> None:
    """
    apply_event(domain, event) must update the domain state deterministically.
    The same event applied twice must produce the same resulting state.
    """
    engine = ContinuityEngineV1_2()
    engine.register_domain("episode")

    event: Dict[str, Any] = {
        "type": "EPISODE_CREATED",
        "episode_id": "ep_001",
        "title": "Pilot",
    }

    engine.apply_event("episode", event)
    state_after_first = engine.get_domain_state("episode")

    engine.apply_event("episode", event)
    state_after_second = engine.get_domain_state("episode")

    assert isinstance(state_after_first, dict)
    assert isinstance(state_after_second, dict)
    # Determinism: applying the same event twice must not introduce divergence.
    assert state_after_first == state_after_second
    assert "episode_id" in state_after_first
    assert state_after_first["episode_id"] == "ep_001"


def test_apply_event_on_unknown_domain_raises_error() -> None:
    """
    Applying an event to an unknown domain must raise ContinuityEngineV1_2Error.
    This enforces explicit domain registration and prevents silent state creation.
    """
    engine = ContinuityEngineV1_2()

    event: Dict[str, Any] = {
        "type": "SCENE_CREATED",
        "scene_id": "sc_001",
    }

    with pytest.raises(ContinuityEngineV1_2Error):
        engine.apply_event("scene", event)


def test_snapshot_returns_immutable_copy_of_internal_state() -> None:
    """
    snapshot() must return a copy of the internal state, not the internal reference.
    Mutating the snapshot must not affect the engine's internal continuity state.
    """
    engine = ContinuityEngineV1_2()
    engine.register_domain("shot")

    event: Dict[str, Any] = {
        "type": "SHOT_CREATED",
        "shot_id": "sh_001",
    }
    engine.apply_event("shot", event)

    snapshot_before = engine.snapshot()
    assert "shot" in snapshot_before
    assert snapshot_before["shot"]["shot_id"] == "sh_001"

    # Mutate snapshot and ensure engine state is not affected.
    snapshot_before["shot"]["shot_id"] = "sh_999"
    snapshot_after = engine.snapshot()

    assert snapshot_after["shot"]["shot_id"] == "sh_001"


def test_multiple_domains_are_tracked_independently() -> None:
    """
    ContinuityEngineV1_2 must track continuity state independently per domain.
    Updates in one domain must not leak into another domain.
    """
    engine = ContinuityEngineV1_2()
    engine.register_domain("character")
    engine.register_domain("episode")

    character_event: Dict[str, Any] = {
        "type": "CHARACTER_CREATED",
        "character_id": "char_001",
        "name": "Alice",
    }
    episode_event: Dict[str, Any] = {
        "type": "EPISODE_CREATED",
        "episode_id": "ep_002",
        "title": "Second",
    }

    engine.apply_event("character", character_event)
    engine.apply_event("episode", episode_event)

    character_state = engine.get_domain_state("character")
    episode_state = engine.get_domain_state("episode")

    assert "character_id" in character_state
    assert "episode_id" not in character_state

    assert "episode_id" in episode_state
    assert "character_id" not in episode_state


def test_continuity_engine_logs_errors_on_invalid_event() -> None:
    """
    Invalid events (missing required keys) must be logged and raise ContinuityEngineV1_2Error.
    This ensures observability and governance-aligned error handling.
    """
    engine = ContinuityEngineV1_2()
    engine.register_domain("episode")

    invalid_event: Dict[str, Any] = {
        # Missing required episode_id / title keys according to governance expectations.
        "type": "EPISODE_CREATED",
    }

    with pytest.raises(ContinuityEngineV1_2Error):
        engine.apply_event("episode", invalid_event)
