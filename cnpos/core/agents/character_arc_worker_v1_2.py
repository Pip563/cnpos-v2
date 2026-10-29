# cnpos/core/agents/character_arc_worker_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, List

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.runtime.continuity_engine_v1_2 import ContinuityEngineV1_2, ContinuityEngineV1_2Error
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CharacterArcWorkerV1_2Error(Exception):
    """
    Raised when CharacterArcWorkerV1_2 encounters an unrecoverable error.
    """
    pass


class CharacterArcWorkerV1_2:
    """
    Deterministic character arc worker for CNPOS v1_2.

    Responsibilities:
    - Generate and update character arcs across episodes and scenes.
    - Enforce governance policies and mutation rules for character evolution.
    - Maintain continuity with existing character state.
    - Route arc-generation tasks through the backend manager.
    - Pass all outputs through the validator pipeline before committing.

    This worker operates at the "CHARACTER_ARC" domain and is designed
    to be invoked by the character pipeline and orchestrator.
    """

    DOMAIN = "CHARACTER_ARC"
    VERSION = "v1_2"

    def __init__(
        self,
        backend_manager: Optional[BackendManagerV1_2] = None,
        continuity_engine: Optional[ContinuityEngineV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._continuity_engine = continuity_engine or ContinuityEngineV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()

        logger.debug(
            "CharacterArcWorkerV1_2 initialized with backend_manager=%s, continuity_engine=%s, "
            "mutation_state_manager=%s, validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._continuity_engine,
            self._mutation_state_manager,
            self._validator_pipeline,
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(
        self,
        character_profile: Dict[str, Any],
        existing_arc: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for generating or updating a character arc.

        Args:
            character_profile: The canonical character profile payload.
            existing_arc: Optional existing arc to extend or repair.
            context: Optional orchestration context (episode, scene, shot, etc.).

        Returns:
            A validated, governance-compliant character arc payload.

        Raises:
            CharacterArcWorkerV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info(
            "CharacterArcWorkerV1_2.run invoked for character_id=%s",
            character_profile.get("id"),
        )

        try:
            # Step 1: Load governance policy for character arcs
            policy = self._load_governance_policy()

            # Step 2: Build request payload for backend
            request_payload = self._build_backend_request(character_profile, existing_arc, context, policy)

            # Step 3: Route to backend for arc generation
            generated_arc = self._generate_arc(request_payload)

            # Step 4: Continuity check against existing arc and character state
            continuous_arc = self._apply_continuity_checks(character_profile, existing_arc, generated_arc, context)

            # Step 5: Record mutation in mutation state manager
            self._record_mutation(character_profile, existing_arc, continuous_arc, context)

            # Step 6: Validate final arc through validator pipeline
            validated_arc = self._validate_arc(continuous_arc, policy, context)

            logger.info(
                "CharacterArcWorkerV1_2.run completed for character_id=%s",
                character_profile.get("id"),
            )
            return validated_arc

        except (BackendManagerV1_2Error, ContinuityEngineV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CharacterArcWorkerV1_2: controlled failure: %s", exc, exc_info=True)
            raise CharacterArcWorkerV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CharacterArcWorkerV1_2: unexpected failure: %s", exc, exc_info=True)
            raise CharacterArcWorkerV1_2Error(f"Unexpected error in CharacterArcWorkerV1_2.run: {exc}") from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_governance_policy(self) -> Dict[str, Any]:
        """
        Load governance policy for character arcs from GovernanceLoaderV1_2.

        Returns:
            Governance policy dict.
        """
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CharacterArcWorkerV1_2: loaded governance policy for domain=%s", self.DOMAIN)
        return policy

    def _build_backend_request(
        self,
        character_profile: Dict[str, Any],
        existing_arc: Optional[Dict[str, Any]],
        context: Dict[str, Any],
        policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the request payload for the backend manager.

        Returns:
            Request payload dict.
        """
        request: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "character_profile": character_profile,
            "existing_arc": existing_arc,
            "context": context,
            "policy": policy,
        }
        logger.debug("CharacterArcWorkerV1_2: built backend request payload=%s", request)
        return request

    def _generate_arc(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the arc-generation task through BackendManagerV1_2.

        Returns:
            Generated character arc payload.
        """
        logger.debug("CharacterArcWorkerV1_2: routing arc generation through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="CHARACTER_ARC_GENERATION",
            payload=request_payload,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for character arc generation.")
        logger.debug("CharacterArcWorkerV1_2: backend generated arc=%s", response)
        return response

    def _apply_continuity_checks(
        self,
        character_profile: Dict[str, Any],
        existing_arc: Optional[Dict[str, Any]],
        generated_arc: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply continuity checks using ContinuityEngineV1_2.

        Returns:
            Continuity-adjusted character arc payload.
        """
        logger.debug("CharacterArcWorkerV1_2: applying continuity checks")
        continuity_input = {
            "character_profile": character_profile,
            "existing_arc": existing_arc,
            "generated_arc": generated_arc,
            "context": context,
            "domain": self.DOMAIN,
            "version": self.VERSION,
        }
        result = self._continuity_engine.check_continuity(continuity_input)
        if not isinstance(result, dict):
            raise ContinuityEngineV1_2Error("ContinuityEngineV1_2 returned non-dict result for character arc continuity.")
        logger.debug("CharacterArcWorkerV1_2: continuity-adjusted arc=%s", result)
        return result

    def _record_mutation(
        self,
        character_profile: Dict[str, Any],
        existing_arc: Optional[Dict[str, Any]],
        new_arc: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """
        Record character arc mutation in MutationStateManagerV1_2.
        """
        logger.debug("CharacterArcWorkerV1_2: recording mutation in MutationStateManagerV1_2")
        mutation_entry = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "character_id": character_profile.get("id"),
            "existing_arc": existing_arc,
            "new_arc": new_arc,
            "context": context,
        }
        self._mutation_state_manager.record_mutation(mutation_entry)

    def _validate_arc(
        self,
        arc_payload: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the final character arc payload through ValidatorPipelineV1_2.

        Returns:
            Validated character arc payload.
        """
        logger.debug("CharacterArcWorkerV1_2: validating arc through ValidatorPipelineV1_2")
        validation_input = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": arc_payload,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for character arc validation.")
        logger.debug("CharacterArcWorkerV1_2: validated arc=%s", result)
        return result
