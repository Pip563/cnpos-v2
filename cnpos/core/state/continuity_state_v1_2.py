# cnpos/core/state/continuity_state_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ContinuityStateV1_2:
    """
    Deterministic continuity state container for CNPOS v1_2.

    This class stores and retrieves continuity state for the cinematic
    hierarchy (episode → scene → shot) in a structured, version‑scoped
    way. It is intentionally minimal and side‑effect free so that:

    - ContinuityEngineV1_2 and validators can query and update state
      without ambiguity.
    - Orchestrators and workers can rely on a single source of truth
      for continuity across the pipelines.
    - No legacy versions (v11, v1_1, v1.2 dotted, v12) are involved.

    The internal structure is:

        {
            episode_id: {
                "_episode_state": {...},
                "scenes": {
                    scene_id: {
                        "_scene_state": {...},
                        "shots": {
                            shot_id: {
                                "_shot_state": {...}
                            }
                        }
                    }
                }
            }
        }

    All state payloads are plain dicts, typically derived from contracts
    and validated upstream.
    """

    def __init__(self) -> None:
        self._state: Dict[str, Dict[str, Any]] = {}

    def get_episode_state(self, episode_id: str) -> Dict[str, Any]:
        """
        Return the continuity state for an episode.

        If no state exists yet, an empty dict is returned.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return {}
        return episode.get("_episode_state", {})

    def set_episode_state(self, episode_id: str, state: Dict[str, Any]) -> None:
        """
        Set or replace the continuity state for an episode.
        """
        episode = self._state.setdefault(episode_id, {"scenes": {}})
        episode["_episode_state"] = dict(state)

    def get_scene_state(self, episode_id: str, scene_id: str) -> Dict[str, Any]:
        """
        Return the continuity state for a scene within an episode.

        If no state exists yet, an empty dict is returned.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return {}
        scenes = episode.get("scenes", {})
        scene = scenes.get(scene_id)
        if not scene:
            return {}
        return scene.get("_scene_state", {})

    def set_scene_state(
        self,
        episode_id: str,
        scene_id: str,
        state: Dict[str, Any],
    ) -> None:
        """
        Set or replace the continuity state for a scene within an episode.
        """
        episode = self._state.setdefault(episode_id, {"scenes": {}})
        scenes = episode.setdefault("scenes", {})
        scene = scenes.setdefault(scene_id, {"shots": {}})
        scene["_scene_state"] = dict(state)

    def get_shot_state(
        self,
        episode_id: str,
        scene_id: str,
        shot_id: str,
    ) -> Dict[str, Any]:
        """
        Return the continuity state for a shot within a scene and episode.

        If no state exists yet, an empty dict is returned.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return {}
        scenes = episode.get("scenes", {})
        scene = scenes.get(scene_id)
        if not scene:
            return {}
        shots = scene.get("shots", {})
        shot = shots.get(shot_id)
        if not shot:
            return {}
        return shot.get("_shot_state", {})

    def set_shot_state(
        self,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        state: Dict[str, Any],
    ) -> None:
        """
        Set or replace the continuity state for a shot within a scene and episode.
        """
        episode = self._state.setdefault(episode_id, {"scenes": {}})
        scenes = episode.setdefault("scenes", {})
        scene = scenes.setdefault(scene_id, {"shots": {}})
        shots = scene.setdefault("shots", {})
        shot = shots.setdefault(shot_id, {})
        shot["_shot_state"] = dict(state)

    def clear_episode(self, episode_id: str) -> None:
        """
        Remove all continuity state for a given episode.
        """
        if episode_id in self._state:
            del self._state[episode_id]

    def clear_scene(self, episode_id: str, scene_id: str) -> None:
        """
        Remove continuity state for a given scene (and its shots) within an episode.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return
        scenes = episode.get("scenes", {})
        if scene_id in scenes:
            del scenes[scene_id]

    def clear_shot(self, episode_id: str, scene_id: str, shot_id: str) -> None:
        """
        Remove continuity state for a given shot within a scene and episode.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return
        scenes = episode.get("scenes", {})
        scene = scenes.get(scene_id)
        if not scene:
            return
        shots = scene.get("shots", {})
        if shot_id in shots:
            del shots[shot_id]

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a deep snapshot of the entire continuity state structure.

        This is useful for debugging, telemetry, or exporting continuity
        state for tests and diagnostics.
        """
        # Shallow copy at top level; nested dicts are assumed to be
        # treated as immutable by callers.
        return dict(self._state)

    def has_episode(self, episode_id: str) -> bool:
        """
        Check whether continuity state exists for the given episode.
        """
        return episode_id in self._state

    def has_scene(self, episode_id: str, scene_id: str) -> bool:
        """
        Check whether continuity state exists for the given scene.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return False
        scenes = episode.get("scenes", {})
        return scene_id in scenes

    def has_shot(self, episode_id: str, scene_id: str, shot_id: str) -> bool:
        """
        Check whether continuity state exists for the given shot.
        """
        episode = self._state.get(episode_id)
        if not episode:
            return False
        scenes = episode.get("scenes", {})
        scene = scenes.get(scene_id)
        if not scene:
            return False
        shots = scene.get("shots", {})
        return shot_id in shots
