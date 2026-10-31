# cnpos/core/orchestrators/character_pipeline_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.agents.character_arc_worker_v1_2 import (
    CharacterArcWorkerV1_2,
    CharacterArcWorkerV1_2Error,
)
from cnpos.core.agents.character_continuity_worker_v1_2 import (
    CharacterContinuityWorkerV1_2,
    CharacterContinuityWorkerV1_2Error,
)
from cnpos.core.agents.character_profile_worker_v1_2 import (
    CharacterProfileWorkerV1_2,
    CharacterProfileWorkerV1_2Error,
)
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.governance.governance_validator_v1_2 import GovernanceValidatorV1_2
from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.state.character_mutation_classifier_v1_2 import CharacterMutationClassifierV1_2
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class CharacterPipelineV1_2Error(Exception):
    """Raised when CharacterPipelineV1_2 encounters an unrecoverable error."""


class CharacterPipelineV1_2:
    """Deterministic character orchestration pipeline for CNPOS v1_2."""

    DOMAIN = "character_pipeline"
    VERSION = "v1_2"

    def __init__(
        self,
        backend_manager: Optional[BackendManagerV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        continuity_state: Optional[ContinuityStateV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        mutation_classifier: Optional[CharacterMutationClassifierV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        governance_validator: Optional[GovernanceValidatorV1_2] = None,
    ) -> None:
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._continuity_state = continuity_state or ContinuityStateV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._governance_validator = (
            governance_validator or GovernanceValidatorV1_2(loader=self._governance_loader)
        )

        self._mutation_classifier = mutation_classifier or CharacterMutationClassifierV1_2(
            backend_manager=self._backend_manager,
            mutation_state_manager=self._mutation_state_manager,
        )

        self._profile_worker = CharacterProfileWorkerV1_2(
            backend_manager=self._backend_manager,
            validator_pipeline=self._validator_pipeline,
        )
        self._continuity_worker = CharacterContinuityWorkerV1_2(
            continuity_state=self._continuity_state,
            validator_pipeline=self._validator_pipeline,
        )
        self._arc_worker = CharacterArcWorkerV1_2(
            backend_manager=self._backend_manager,
            validator_pipeline=self._validator_pipeline,
        )

        logger.debug(
            "CharacterPipelineV1_2 initialized with backend_manager=%s, validator_pipeline=%s, continuity_state=%s, mutation_state_manager=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._continuity_state,
            self._mutation_state_manager,
        )

    def run(
        self,
        episode_payload: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Orchestrate full character processing for an episode payload."""
        episode_payload = episode_payload or payload or {}
        context = context or {}

        logger.info(
            "CharacterPipelineV1_2.run invoked for episode_id=%s",
            episode_payload.get("episode_id"),
        )

        try:
            self._validate_governance()
            profiles = self._run_profiles(episode_payload, context)
            continuity = self._run_continuity(episode_payload, profiles, context)
            arcs = self._run_arcs(episode_payload, profiles, continuity, context)
            mutations = self._classify_and_record_mutations(
                episode_payload,
                profiles,
                continuity,
                arcs,
                context,
            )

            result = {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "profiles": profiles,
                "continuity": continuity,
                "arcs": arcs,
                "mutations": mutations,
                "context": context,
            }

            logger.info(
                "CharacterPipelineV1_2.run completed for episode_id=%s",
                episode_payload.get("episode_id"),
            )
            return result

        except (
            CharacterProfileWorkerV1_2Error,
            CharacterContinuityWorkerV1_2Error,
            CharacterArcWorkerV1_2Error,
            BackendManagerV1_2Error,
            ValidatorPipelineV1_2Error,
            CharacterPipelineV1_2Error,
        ) as exc:
            logger.error("CharacterPipelineV1_2 controlled failure: %s", exc, exc_info=True)
            raise CharacterPipelineV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CharacterPipelineV1_2 unexpected failure: %s", exc, exc_info=True)
            raise CharacterPipelineV1_2Error(
                f"Unexpected error in CharacterPipelineV1_2.run: {exc}"
            ) from exc

    def _validate_governance(self) -> None:
        """Validate governance configuration for the 'character' domain."""
        violations = self._governance_validator.validate_governance_config("character")
        if violations:
            logger.error(
                "CharacterPipelineV1_2 governance violations: %s",
                "; ".join(violations),
            )
            raise CharacterPipelineV1_2Error(
                f"Governance configuration invalid for 'character' domain: {violations}"
            )

    def _run_profiles(
        self,
        episode_payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Run character profile worker for all characters in the episode."""
        characters = episode_payload.get("characters", [])
        profiles: List[Dict[str, Any]] = []

        for character in characters:
            profile = self._profile_worker.run(
                character_payload=character,
                context=context,
            )
            profiles.append(profile)

        logger.debug(
            "CharacterPipelineV1_2._run_profiles produced %d profiles",
            len(profiles),
        )
        return profiles

    def _run_continuity(
        self,
        episode_payload: Dict[str, Any],
        profiles: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run character continuity worker using episode payload and profiles."""
        continuity_result = self._continuity_worker.run(
            episode_payload=episode_payload,
            profiles=profiles,
            context=context,
        )
        logger.debug(
            "CharacterPipelineV1_2._run_continuity result keys=%s",
            list(continuity_result.keys()),
        )
        return continuity_result

    def _run_arcs(
        self,
        episode_payload: Dict[str, Any],
        profiles: List[Dict[str, Any]],
        continuity: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run character arc worker using episode payload, profiles, and continuity."""
        arcs_result = self._arc_worker.run(
            episode_payload=episode_payload,
            profiles=profiles,
            continuity=continuity,
            context=context,
        )
        logger.debug(
            "CharacterPipelineV1_2._run_arcs result keys=%s",
            list(arcs_result.keys()),
        )
        return arcs_result

    def _classify_and_record_mutations(
        self,
        episode_payload: Dict[str, Any],
        profiles: List[Dict[str, Any]],
        continuity: Dict[str, Any],
        arcs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Classify character-related mutations and record them in the mutation state manager."""
        mutation_input = {
            "episode": episode_payload,
            "profiles": profiles,
            "continuity": continuity,
            "arcs": arcs,
            "context": context,
        }

        classification = self._mutation_classifier.classify(mutation_input)
        self._mutation_state_manager.record_mutation(
            domain="character",
            mutation_type="character_pipeline",
            payload=classification,
            active_state_snapshot=episode_payload,
            impact_summary={"source": "character_pipeline"},
            risk_level="medium",
        )

        logger.debug(
            "CharacterPipelineV1_2._classify_and_record_mutations recorded mutation for episode_id=%s",
            episode_payload.get("episode_id"),
        )
        return classification


__all__ = ["CharacterPipelineV1_2", "CharacterPipelineV1_2Error"]
