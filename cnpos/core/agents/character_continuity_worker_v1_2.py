# cnpos/core/agents/character_continuity_worker_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.continuity_engine_v1_2 import ContinuityEngineV1_2, ContinuityEngineV1_2Error
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.state.character_mutation_classifier_v1_2 import CharacterMutationClassifierV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CharacterContinuityWorkerV1_2Error(Exception):
    """Raised when CharacterContinuityWorkerV1_2 encounters an unrecoverable error."""
    pass


class CharacterContinuityWorkerV1_2:
    """
    Deterministic character continuity worker for CNPOS v1_2.

    Responsibilities:
    - Maintain continuity for character-related payloads (profile, arc, scene presence).
    - Compare new character payloads against active continuity state.
    - Classify and record character mutations.
    - Enforce governance rules for allowed/forbidden continuity changes.
    - Validate continuity results through the validator pipeline.

    Domain: CHARACTER_CONTINUITY
    Version: v1_2
    """

    DOMAIN = "CHARACTER_CONTINUITY"
    VERSION = "v1_2"

    def __init__(
        self,
        continuity_engine: Optional[ContinuityEngineV1_2] = None,
        continuity_state: Optional[ContinuityStateV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        mutation_classifier: Optional[CharacterMutationClassifierV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._continuity_engine = continuity_engine or ContinuityEngineV1_2()
        self._continuity_state = continuity_state or ContinuityStateV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()
        self._mutation_classifier = mutation_classifier or CharacterMutationClassifierV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()

        logger.debug(
            "CharacterContinuityWorkerV1_2 initialized with continuity_engine=%s, continuity_state=%s, "
            "mutation_state_manager=%s, mutation_classifier=%s, validator_pipeline=%s, governance_loader=%s",
            self._continuity_engine,
            self._continuity_state,
            self._mutation_state_manager,
            self._mutation_classifier,
            self._validator_pipeline,
            self._governance_loader,
        )

    def run(
        self,
        character_payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for character continuity evaluation.

        Args:
            character_payload: New character-related payload (profile, arc, or scene-level data).
            context: Optional orchestration context (episode, scene, shot, pipeline identifiers).

        Returns:
            A validated continuity result payload, including drift/mutation information.

        Raises:
            CharacterContinuityWorkerV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info(
            "CharacterContinuityWorkerV1_2.run invoked for character_id=%s",
            character_payload.get("id"),
        )

        try:
            policy = self._load_governance_policy()
            active_state = self._load_active_state(character_payload, context)
            continuity_input = self._build_continuity_input(character_payload, active_state, context, policy)
            continuity_result = self._run_continuity_engine(continuity_input)
            mutation_info = self._classify_mutation(character_payload, active_state, continuity_result, context)
            self._record_mutation(character_payload, mutation_info, context)
            validated_result = self._validate_continuity_result(continuity_result, policy, context)

            logger.info(
                "CharacterContinuityWorkerV1_2.run completed for character_id=%s",
                character_payload.get("id"),
            )
            return {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "character_id": character_payload.get("id"),
                "continuity_result": validated_result,
                "mutation": mutation_info,
                "context": context,
            }

        except (ContinuityEngineV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CharacterContinuityWorkerV1_2: controlled failure: %s", exc, exc_info=True)
            raise CharacterContinuityWorkerV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CharacterContinuityWorkerV1_2: unexpected failure: %s", exc, exc_info=True)
            raise CharacterContinuityWorkerV1_2Error(f"Unexpected error in CharacterContinuityWorkerV1_2.run: {exc}") from exc

    def _load_governance_policy(self) -> Dict[str, Any]:
        """Load governance policy for character continuity from GovernanceLoaderV1_2."""
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CharacterContinuityWorkerV1_2: loaded governance policy for domain=%s", self.DOMAIN)
        return policy

    def _load_active_state(
        self,
        character_payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Load the active continuity state for the given character.

        Returns:
            Active continuity state payload or None if no state exists.
        """
        character_id = character_payload.get("id")
        active_state = self._continuity_state.get_state(
            domain=self.DOMAIN,
            key=str(character_id) if character_id is not None else None,
        )
        logger.debug(
            "CharacterContinuityWorkerV1_2: loaded active continuity state for character_id=%s: %s",
            character_id,
            active_state,
        )
        return active_state

    def _build_continuity_input(
        self,
        character_payload: Dict[str, Any],
        active_state: Optional[Dict[str, Any]],
        context: Dict[str, Any],
        policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the input payload for ContinuityEngineV1_2.

        Returns:
            Continuity engine input dict.
        """
        continuity_input: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "character_payload": character_payload,
            "active_state": active_state,
            "context": context,
            "policy": policy,
        }
        logger.debug("CharacterContinuityWorkerV1_2: built continuity_input=%s", continuity_input)
        return continuity_input

    def _run_continuity_engine(self, continuity_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute continuity checks using ContinuityEngineV1_2.

        Returns:
            Continuity result payload.
        """
        logger.debug("CharacterContinuityWorkerV1_2: running continuity engine")
        result = self._continuity_engine.check_continuity(continuity_input)
        if not isinstance(result, dict):
            raise ContinuityEngineV1_2Error("ContinuityEngineV1_2 returned non-dict result for character continuity.")
        logger.debug("CharacterContinuityWorkerV1_2: continuity_result=%s", result)

        # Persist updated continuity state if provided by engine
        updated_state = result.get("updated_state")
        if isinstance(updated_state, dict):
            character_id = continuity_input["character_payload"].get("id")
            self._continuity_state.set_state(
                domain=self.DOMAIN,
                key=str(character_id) if character_id is not None else None,
                state=updated_state,
            )
            logger.debug(
                "CharacterContinuityWorkerV1_2: updated continuity state for character_id=%s: %s",
                character_id,
                updated_state,
            )

        return result

    def _classify_mutation(
        self,
        character_payload: Dict[str, Any],
        active_state: Optional[Dict[str, Any]],
        continuity_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Classify character mutation based on continuity result.

        Returns:
            Mutation classification payload.
        """
        logger.debug("CharacterContinuityWorkerV1_2: classifying mutation")
        mutation_input: Dict[str, Any] = {
            "character_payload": character_payload,
            "active_state": active_state,
            "continuity_result": continuity_result,
            "context": context,
            "domain": self.DOMAIN,
            "version": self.VERSION,
        }
        mutation_info = self._mutation_classifier.classify(mutation_input)
        if not isinstance(mutation_info, dict):
            # If classifier returns non-dict, normalize to minimal mutation info
            mutation_info = {"classification": "unknown", "details": None}
        logger.debug("CharacterContinuityWorkerV1_2: mutation_info=%s", mutation_info)
        return mutation_info

    def _record_mutation(
        self,
        character_payload: Dict[str, Any],
        mutation_info: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """
        Record character continuity mutation in MutationStateManagerV1_2.
        """
        logger.debug("CharacterContinuityWorkerV1_2: recording mutation in MutationStateManagerV1_2")
        mutation_entry = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "character_id": character_payload.get("id"),
            "mutation": mutation_info,
            "context": context,
        }
        self._mutation_state_manager.record_mutation(mutation_entry)

    def _validate_continuity_result(
        self,
        continuity_result: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the continuity result payload through ValidatorPipelineV1_2.

        Returns:
            Validated continuity result payload.
        """
        logger.debug("CharacterContinuityWorkerV1_2: validating continuity_result through ValidatorPipelineV1_2")
        validation_input = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": continuity_result,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for character continuity.")
        logger.debug("CharacterContinuityWorkerV1_2: validated continuity_result=%s", result)
        return result
