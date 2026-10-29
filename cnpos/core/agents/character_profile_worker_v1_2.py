# cnpos/core/agents/character_profile_worker_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.runtime.continuity_engine_v1_2 import ContinuityEngineV1_2, ContinuityEngineV1_2Error
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.state.character_mutation_classifier_v1_2 import CharacterMutationClassifierV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CharacterProfileWorkerV1_2Error(Exception):
    """Raised when CharacterProfileWorkerV1_2 encounters an unrecoverable error."""
    pass


class CharacterProfileWorkerV1_2:
    """
    Deterministic character profile worker for CNPOS v1_2.

    Responsibilities:
    - Generate, normalize, and update canonical character profiles.
    - Enforce governance rules for allowed profile fields and constraints.
    - Maintain continuity with existing character profile state.
    - Classify and record profile mutations.
    - Route profile-generation tasks through the backend manager.
    - Validate final profiles through the validator pipeline.

    Domain: CHARACTER_PROFILE
    Version: v1_2
    """

    DOMAIN = "CHARACTER_PROFILE"
    VERSION = "v1_2"

    def __init__(
        self,
        backend_manager: Optional[BackendManagerV1_2] = None,
        continuity_engine: Optional[ContinuityEngineV1_2] = None,
        continuity_state: Optional[ContinuityStateV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        mutation_classifier: Optional[CharacterMutationClassifierV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._continuity_engine = continuity_engine or ContinuityEngineV1_2()
        self._continuity_state = continuity_state or ContinuityStateV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()
        self._mutation_classifier = mutation_classifier or CharacterMutationClassifierV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()

        logger.debug(
            "CharacterProfileWorkerV1_2 initialized with backend_manager=%s, continuity_engine=%s, "
            "continuity_state=%s, mutation_state_manager=%s, mutation_classifier=%s, "
            "validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._continuity_engine,
            self._continuity_state,
            self._mutation_state_manager,
            self._mutation_classifier,
            self._validator_pipeline,
            self._governance_loader,
        )

    def run(
        self,
        seed_payload: Dict[str, Any],
        existing_profile: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for generating or updating a character profile.

        Args:
            seed_payload: Input payload used to derive or update the character profile
                          (could be script metadata, casting info, or partial profile).
            existing_profile: Optional existing profile to reconcile or extend.
            context: Optional orchestration context (episode, scene, shot, pipeline identifiers).

        Returns:
            A validated, governance-compliant character profile payload.

        Raises:
            CharacterProfileWorkerV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info(
            "CharacterProfileWorkerV1_2.run invoked for seed_id=%s",
            seed_payload.get("id"),
        )

        try:
            policy = self._load_governance_policy()
            backend_request = self._build_backend_request(seed_payload, existing_profile, context, policy)
            generated_profile = self._generate_profile(backend_request)
            active_state = self._load_active_state(generated_profile, context)
            continuity_input = self._build_continuity_input(generated_profile, active_state, context, policy)
            continuity_result = self._run_continuity_engine(continuity_input)
            mutation_info = self._classify_mutation(generated_profile, active_state, continuity_result, context)
            self._record_mutation(generated_profile, mutation_info, context)
            validated_profile = self._validate_profile(generated_profile, continuity_result, policy, context)

            logger.info(
                "CharacterProfileWorkerV1_2.run completed for character_id=%s",
                validated_profile.get("id"),
            )
            return validated_profile

        except (BackendManagerV1_2Error, ContinuityEngineV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CharacterProfileWorkerV1_2: controlled failure: %s", exc, exc_info=True)
            raise CharacterProfileWorkerV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CharacterProfileWorkerV1_2: unexpected failure: %s", exc, exc_info=True)
            raise CharacterProfileWorkerV1_2Error(f"Unexpected error in CharacterProfileWorkerV1_2.run: {exc}") from exc

    def _load_governance_policy(self) -> Dict[str, Any]:
        """Load governance policy for character profiles from GovernanceLoaderV1_2."""
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CharacterProfileWorkerV1_2: loaded governance policy for domain=%s", self.DOMAIN)
        return policy

    def _build_backend_request(
        self,
        seed_payload: Dict[str, Any],
        existing_profile: Optional[Dict[str, Any]],
        context: Dict[str, Any],
        policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the request payload for the backend manager."""
        request: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "seed_payload": seed_payload,
            "existing_profile": existing_profile,
            "context": context,
            "policy": policy,
        }
        logger.debug("CharacterProfileWorkerV1_2: built backend request payload=%s", request)
        return request

    def _generate_profile(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route the profile-generation task through BackendManagerV1_2."""
        logger.debug("CharacterProfileWorkerV1_2: routing profile generation through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="CHARACTER_PROFILE_GENERATION",
            payload=request_payload,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for character profile generation.")
        logger.debug("CharacterProfileWorkerV1_2: backend generated profile=%s", response)
        return response

    def _load_active_state(
        self,
        profile_payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Load the active continuity state for the given character profile.

        Returns:
            Active continuity state payload or None if no state exists.
        """
        character_id = profile_payload.get("id")
        active_state = self._continuity_state.get_state(
            domain=self.DOMAIN,
            key=str(character_id) if character_id is not None else None,
        )
        logger.debug(
            "CharacterProfileWorkerV1_2: loaded active continuity state for character_id=%s: %s",
            character_id,
            active_state,
        )
        return active_state

    def _build_continuity_input(
        self,
        profile_payload: Dict[str, Any],
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
            "profile_payload": profile_payload,
            "active_state": active_state,
            "context": context,
            "policy": policy,
        }
        logger.debug("CharacterProfileWorkerV1_2: built continuity_input=%s", continuity_input)
        return continuity_input

    def _run_continuity_engine(self, continuity_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute continuity checks using ContinuityEngineV1_2.

        Returns:
            Continuity result payload.
        """
        logger.debug("CharacterProfileWorkerV1_2: running continuity engine")
        result = self._continuity_engine.check_continuity(continuity_input)
        if not isinstance(result, dict):
            raise ContinuityEngineV1_2Error("ContinuityEngineV1_2 returned non-dict result for character profile continuity.")
        logger.debug("CharacterProfileWorkerV1_2: continuity_result=%s", result)

        updated_state = result.get("updated_state")
        if isinstance(updated_state, dict):
            character_id = continuity_input["profile_payload"].get("id")
            self._continuity_state.set_state(
                domain=self.DOMAIN,
                key=str(character_id) if character_id is not None else None,
                state=updated_state,
            )
            logger.debug(
                "CharacterProfileWorkerV1_2: updated continuity state for character_id=%s: %s",
                character_id,
                updated_state,
            )

        return result

    def _classify_mutation(
        self,
        profile_payload: Dict[str, Any],
        active_state: Optional[Dict[str, Any]],
        continuity_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Classify character profile mutation based on continuity result.

        Returns:
            Mutation classification payload.
        """
        logger.debug("CharacterProfileWorkerV1_2: classifying mutation")
        mutation_input: Dict[str, Any] = {
            "profile_payload": profile_payload,
            "active_state": active_state,
            "continuity_result": continuity_result,
            "context": context,
            "domain": self.DOMAIN,
            "version": self.VERSION,
        }
        mutation_info = self._mutation_classifier.classify(mutation_input)
        if not isinstance(mutation_info, dict):
            mutation_info = {"classification": "unknown", "details": None}
        logger.debug("CharacterProfileWorkerV1_2: mutation_info=%s", mutation_info)
        return mutation_info

    def _record_mutation(
        self,
        profile_payload: Dict[str, Any],
        mutation_info: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """
        Record character profile mutation in MutationStateManagerV1_2.
        """
        logger.debug("CharacterProfileWorkerV1_2: recording mutation in MutationStateManagerV1_2")
        mutation_entry = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "character_id": profile_payload.get("id"),
            "mutation": mutation_info,
            "context": context,
        }
        self._mutation_state_manager.record_mutation(mutation_entry)

    def _validate_profile(
        self,
        profile_payload: Dict[str, Any],
        continuity_result: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the final character profile payload through ValidatorPipelineV1_2.

        Returns:
            Validated character profile payload.
        """
        logger.debug("CharacterProfileWorkerV1_2: validating profile through ValidatorPipelineV1_2")
        validation_input = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": {
                "profile": profile_payload,
                "continuity_result": continuity_result,
            },
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for character profile validation.")
        logger.debug("CharacterProfileWorkerV1_2: validated profile payload=%s", result)

        # Expect the validator to return the normalized profile under "profile"
        normalized_profile = result.get("profile", profile_payload)
        return normalized_profile
