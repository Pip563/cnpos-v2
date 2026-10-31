# cnpos/core/state/character_mutation_classifier_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2

logger = logging.getLogger(__name__)


class CharacterMutationClassifierV1_2Error(Exception):
    """Raised when CharacterMutationClassifierV1_2 encounters an unrecoverable error."""


class CharacterMutationClassifierV1_2:
    """Deterministic classifier for character-level mutations in CNPOS v1_2."""

    DOMAIN = "character"
    VERSION = "v1_2"

    def __init__(
        self,
        backend_manager: Optional[BackendManagerV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
    ) -> None:
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()
        self._history: Dict[str, Dict[str, Any]] = {}

        logger.debug(
            "CharacterMutationClassifierV1_2 initialized backend_manager=%s mutation_state_manager=%s",
            self._backend_manager,
            self._mutation_state_manager,
        )

    def classify(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Classify a mutation for a character payload."""
        context = kwargs.get("context") or {}

        try:
            if args and isinstance(args[0], dict):
                payload = args[0]
                character_id = str(payload.get("character_id") or payload.get("id") or "unknown")
                previous_state = payload.get("previous_state") or payload.get("previous_payload") or {}
                new_state = payload.get("new_state") or payload.get("new_payload") or payload.get("current_payload") or payload
                episode_id = payload.get("episode_id")
                scene_id = payload.get("scene_id")
                shot_id = payload.get("shot_id")
                governance = payload.get("governance")
            else:
                character_id = str(
                    kwargs.get("character_id") or kwargs.get("id") or (args[0] if args else "unknown")
                )
                previous_state = kwargs.get("previous_state") or kwargs.get("previous_payload") or {}
                new_state = (
                    kwargs.get("new_state")
                    or kwargs.get("new_payload")
                    or kwargs.get("current_payload")
                    or kwargs.get("payload")
                    or previous_state
                )
                episode_id = kwargs.get("episode_id")
                scene_id = kwargs.get("scene_id")
                shot_id = kwargs.get("shot_id")
                governance = kwargs.get("governance")

            if not isinstance(previous_state, dict):
                previous_state = {}
            if not isinstance(new_state, dict):
                new_state = previous_state

            result = self._classify_state(
                character_id=character_id,
                previous_state=previous_state,
                new_state=new_state,
                episode_id=episode_id,
                scene_id=scene_id,
                shot_id=shot_id,
                governance=governance,
                context=context,
            )
            self._history[character_id] = result
            return result

        except Exception as exc:  # pragma: no cover - defensive recovery path
            logger.error("CharacterMutationClassifierV1_2.classify error: %s", exc, exc_info=True)
            return {
                "domain": self.DOMAIN,
                "phase": "MUTATION",
                "character_id": str(kwargs.get("character_id") or "unknown"),
                "episode_id": kwargs.get("episode_id"),
                "scene_id": kwargs.get("scene_id"),
                "shot_id": kwargs.get("shot_id"),
                "mutations": [],
                "summary": {
                    "last_mutation_type": "UNKNOWN",
                    "last_risk_level": "low",
                    "counts_by_type": {},
                },
                "rationale": f"Mutation rationale unavailable due to backend error: {exc}",
                "error": str(exc),
            }

    def _classify_state(
        self,
        *,
        character_id: str,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        episode_id: Optional[str],
        scene_id: Optional[str],
        shot_id: Optional[str],
        governance: Optional[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Classify deterministic mutation and produce structured rationale."""
        mutation_details = self._detect_mutations(previous_state, new_state)
        if mutation_details:
            mutation_type = mutation_details[-1].get("mutation_type", "VALUE_CHANGE")
            risk_level = mutation_details[-1].get("risk_level", "medium")
            details = mutation_details
        else:
            mutation_type = "NO_SIGNIFICANT_CHANGE"
            risk_level = "low"
            details = [{
                "mutation_type": mutation_type,
                "risk_level": risk_level,
                "details": ["No significant change detected."],
            }]

        rationale = self._build_rationale(
            previous_state=previous_state,
            new_state=new_state,
            governance=governance,
            mutation_type=mutation_type,
            risk_level=risk_level,
            context=context,
        )

        summary = {
            "last_mutation_type": mutation_type,
            "last_risk_level": risk_level,
            "counts_by_type": {mutation_type: len(details)},
        }

        result = {
            "domain": self.DOMAIN,
            "phase": "MUTATION",
            "character_id": character_id,
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "mutations": details,
            "summary": summary,
            "rationale": rationale,
        }
        self._history[character_id] = result
        return result

    def _detect_mutations(
        self,
        previous: Optional[Dict[str, Any]],
        current: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Compute a deterministic mutation list for a character state diff."""
        if not isinstance(previous, dict):
            previous = {}
        if not isinstance(current, dict):
            current = {}

        if previous == current:
            return []

        details: List[Dict[str, Any]] = []
        prev_keys = set(previous.keys())
        curr_keys = set(current.keys())

        added = sorted(curr_keys - prev_keys)
        removed = sorted(prev_keys - curr_keys)
        changed = []
        for key in sorted(prev_keys & curr_keys):
            if previous.get(key) != current.get(key):
                changed.append(key)

        if added or removed or changed:
            details.append(
                {
                    "mutation_type": "STRUCTURAL_CHANGE" if added or removed else "VALUE_CHANGE",
                    "risk_level": "medium" if changed else "low",
                    "details": [
                        f"Added keys: {', '.join(added)}" if added else None,
                        f"Removed keys: {', '.join(removed)}" if removed else None,
                        *[f"Value changed for key '{key}'" for key in changed],
                    ],
                }
            )

        return details

    def _build_rationale(
        self,
        *,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        governance: Optional[Dict[str, Any]],
        mutation_type: str,
        risk_level: str,
        context: Dict[str, Any],
    ) -> str:
        """Generate a deterministic rationale string using the backend manager when available."""
        if hasattr(self._backend_manager, "generate"):
            try:
                extra = {
                    "previous": previous_state,
                    "current": new_state,
                    "governance": governance,
                    "context": context,
                    "mutation_type": mutation_type,
                    "risk_level": risk_level,
                }
                response = self._backend_manager.generate(
                    prompt="classify_character_mutation",
                    domain="mutation",
                    phase="CHARACTER",
                    task_type="CHARACTER_MUTATION_RATIONALE",
                    extra=extra,
                )
                if isinstance(response, dict):
                    output = response.get("output")
                    if output is None or str(output).strip() == "":
                        return "Mutation rationale unavailable: backend returned empty output."
                    return str(output)
                value = str(response).strip()
                if not value:
                    return "Mutation rationale unavailable: backend returned empty output."
                return value
            except Exception as exc:
                return f"Mutation rationale unavailable due to backend error: {exc}"

        if previous_state == new_state:
            return "Mutation rationale unavailable: no significant change detected."

        return (
            f"Mutation classified as '{mutation_type}' with risk '{risk_level}' "
            f"based on the state delta."
        )


__all__ = ["CharacterMutationClassifierV1_2", "CharacterMutationClassifierV1_2Error"]
