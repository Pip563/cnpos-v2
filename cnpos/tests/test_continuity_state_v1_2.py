# tests/test_continuity_state_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2

logger = logging.getLogger(__name__)


def test_continuity_state_v1_2_initial_state_is_empty() -> None:
    """
    ContinuityStateV1_2 must start with an empty deterministic state container.
    """
    state = ContinuityStateV1_2()
    full_state = state.get_full_state()

    assert isinstance(full_state, dict)
    assert full_state == {}


def test_continuity_state_v1_2_set_and_get_episode_state() -> None:
    """
    ContinuityStateV1_2 should store and retrieve episode-level continuity state.
    """
    state = ContinuityStateV1_2()

    episode_id = "ep_001"
    episode_state: Dict[str, Any] = {
        "title": "Pilot",
        "characters": ["alice", "bob"],
    }

    state.set_episode_state(episode_id=episode_id, payload=episode_state)

    retrieved = state.get_episode_state(episode_id=episode_id)
    assert isinstance(retrieved, dict)
    assert retrieved == episode_state


def test_continuity_state_v1_2_set_scene_and_shot_state() -> None:
    """
    ContinuityStateV1_2 must maintain the hierarchical structure:
    episode → scene → shot.
    """
    state = ContinuityStateV1_2()

    episode_id = "ep_001"
    scene_id = "sc_001"
    shot_id = "sh_001"

    episode_state: Dict[str, Any] = {"title": "Pilot"}
    scene_state: Dict[str, Any] = {"location": "Naples", "characters": ["alice"]}
    shot_state: Dict[str, Any] = {"frame": "CU", "duration": 3.2}

    state.set_episode_state(episode_id=episode_id, payload=episode_state)
    state.set_scene_state(
        episode_id=episode_id,
        scene_id=scene_id,
        payload=scene_state,
    )
    state.set_shot_state(
        episode_id=episode_id,
        scene_id=scene_id,
        shot_id=shot_id,
        payload=shot_state,
    )

    full_state = state.get_full_state()

    assert episode_id in full_state
    assert "_episode_state" in full_state[episode_id]
    assert "scenes" in full_state[episode_id]
    assert scene_id in full_state[episode_id]["scenes"]
    assert "_scene_state" in full_state[episode_id]["scenes"][scene_id]
    assert "shots" in full_state[episode_id]["scenes"][scene_id]
    assert shot_id in full_state[episode_id]["scenes"][scene_id]["shots"]
    assert "_shot_state" in full_state[episode_id]["scenes"][scene_id]["shots"][shot_id]


def test_continuity_state_v1_2_clear_episode_state() -> None:
    """
    ContinuityStateV1_2 should allow clearing an episode subtree deterministically.
    """
    state = ContinuityStateV1_2()

    episode_id = "ep_001"
    state.set_episode_state(episode_id=episode_id, payload={"title": "Pilot"})

    assert episode_id in state.get_full_state()

    state.clear_episode_state(episode_id=episode_id)

    full_state = state.get_full_state()
    assert episode_id not in full_state
