# cnpos/core/state/character_mutation_classifier_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2

logger = logging.getLogger(__name__)


class CharacterMutationClassifierV1_2Error(Exception):
    """Raised when CharacterMutationClassifierV1_2 encounters an unrecoverable error."""
    pass


class CharacterMutationClassifierV1_2:
    """
    CharacterMutationClassifierV1_2

    Deterministic classifier for character‑level mutations in CNPOS v1_2.

    Responsibilities:
    - Compare new character payloads against mutation history.
    - Use LLMBackendManagerV1_2 for semantic mutation classification.
    - Produce structured mutation reports for validators and continuity systems.
    - Maintain strict v1_2 naming and deterministic behavior.

    Domain: character_mutation
    Version: v1_2
    """

    DOMAIN = "character_mutation"
    VERSION = "v1_2"

    def __init__(
        self,
        self._validator_pipeline = (
        validator_pipeline or ValidatorPipelineV1_2()
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
    ) -> None:
        elf._backend_manager = backend_manager or BackendManagerV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()

        logger.debug(
            "CharacterMutationClassifierV1_2 initialized backend_manager=%s mutation_state_manager=%s",
            self._backend_manager,
            self._mutation_state_manager,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def classify(
        self,
        character_id: str,
        new_payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Classify mutation for a character payload.

        Args:
            character_id: Unique character identifier.
            new_payload: New character payload to classify.
            context: Optional orchestration context.

        Returns:
            Dict[str, Any]: Mutation classification report:
                - 'character_id'
                - 'domain'
                - 'version'
                - 'is_mutation'
                - 'mutation_type'
                - 'previous_payload'
                - 'current_payload'
                - 'details'
        """
        context = context or {}
        logger.info(
            "CharacterMutationClassifierV1_2.classify invoked for character_id=%s",
            character_id,
        )

        previous_payload = self._mutation_state_manager.get_history(character_id)

        is_mutation, mutation_type, details = self._detect_mutation(
            previous_payload,
            new_payload,
            context,
        )

        report = {
            "character_id": character_id,
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "is_mutation": is_mutation,
            "mutation_type": mutation_type,
            "previous_payload": previous_payload,
            "current_payload": new_payload,
            "details": details,
        }

        # Update mutation history only when mutation is confirmed
        if is_mutation:
            self._mutation_state_manager.record_mutation(character_id, new_payload)

        logger.debug(
            "CharacterMutationClassifierV1_2.classify completed is_mutation=%s mutation_type=%s",
            is_mutation,
            mutation_type,
        )
        return report

    # -------------------------------------------------------------------------
    # Internal mutation detection
    # -------------------------------------------------------------------------

    def _detect_mutation(
        self,
        previous: Optional[Dict[str, Any]],
        current: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Tuple[bool, str, List[str]]:
        """
        Detect mutation between previous and current character payloads.

        Rules:
        - If no previous payload exists → no mutation.
        - Structural drift (added/removed keys) → mutation.
        - Value drift for shared keys → mutation.
        - Semantic drift → delegated to LLMBackendManagerV1_2.

        Returns:
            (is_mutation, mutation_type, details)
        """
        details: List[str] = []

        if previous is None:
            logger.debug("CharacterMutationClassifierV1_2._detect_mutation no previous payload; no mutation")
            return False, "none", details

        prev_keys = set(previous.keys())
        curr_keys = set(current.keys())

        added_keys = sorted(curr_keys - prev_keys)
        removed_keys = sorted(prev_keys - curr_keys)

        if added_keys:
            details.append(f"Added keys: {', '.join(added_keys)}")
        if removed_keys:
            details.append(f"Removed keys: {', '.join(removed_keys)}")

        shared_keys = prev_keys & curr_keys
        for key in sorted(shared_keys):
            if previous.get(key) != current.get(key):
                details.append(f"Value changed for key '{key}'")

        # If structural or value drift detected → mutation
        if details:
            return True, "structural_or_value", details

        # Semantic drift check via backend manager
        semantic_result = self._backend_manager.run_task(
            prompt="classify_character_mutation",
            parameters={
                "previous": previous,
                "current": current,
            },
            backend_key=context.get("backend_key"),
        )

        mutation_flag = bool(semantic_result.get("is_mutation", False))
        mutation_type = semantic_result.get("mutation_type", "semantic")
        semantic_details = semantic_result.get("details", [])

        if mutation_flag:
            details.extend(semantic_details)
            return True, mutation_type, details

        return False, "none", details


__all__ = ["CharacterMutationClassifierV1_2", "CharacterMutationClassifierV1_2Error"]
