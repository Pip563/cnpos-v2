# cnpos/core/orchestrators/cinematic_pipeline_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)
from cnpos.core.runtime.continuity_engine_v1_2 import (
    ContinuityEngineV1_2,
    ContinuityEngineV1_2Error,
)
from cnpos.core.runtime.workers.episode_worker_v1_2 import EpisodeWorkerV1_2
from cnpos.core.runtime.workers.scene_worker_v1_2 import SceneWorkerV1_2
from cnpos.core.runtime.workers.shot_worker_v1_2 import ShotWorkerV1_2
from cnpos.core.runtime.workers.render_worker_v1_2 import RenderWorkerV1_2
from cnpos.core.runtime.workers.worker_registry_v1_2 import WorkerRegistryV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.governance.governance_validator_v1_2 import GovernanceValidatorV1_2

logger = logging.getLogger(__name__)


class CinematicPipelineV1_2Error(Exception):
    """Raised when CinematicPipelineV1_2 encounters an unrecoverable error."""


class CinematicPipelineV1_2:
    """Deterministic cinematic orchestration pipeline for CNPOS v1_2."""

    DOMAIN = "cinematic"
    VERSION = "v1_2"

    def __init__(
        self,
        backend_manager: Optional[BackendManagerV1_2] = None,
        continuity_engine: Optional[ContinuityEngineV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        governance_validator: Optional[GovernanceValidatorV1_2] = None,
        worker_registry: Optional[WorkerRegistryV1_2] = None,
    ) -> None:
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._continuity_engine = continuity_engine or ContinuityEngineV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._governance_validator = governance_validator or GovernanceValidatorV1_2(
            loader=self._governance_loader
        )
        self._worker_registry = worker_registry or WorkerRegistryV1_2()

        self._episode_worker = EpisodeWorkerV1_2(
            backend_manager=self._backend_manager,
            validator_pipeline=self._validator_pipeline,
        )
        self._scene_worker = SceneWorkerV1_2(
            validator_pipeline=self._validator_pipeline,
            continuity_engine=self._continuity_engine,
        )
        self._shot_worker = ShotWorkerV1_2(
            validator_pipeline=self._validator_pipeline,
            continuity_engine=self._continuity_engine,
        )
        self._render_worker = RenderWorkerV1_2(
            backend_manager=self._backend_manager,
            validator_pipeline=self._validator_pipeline,
        )

        logger.debug(
            "CinematicPipelineV1_2 initialized with backend_manager=%s, "
            "continuity_engine=%s, validator_pipeline=%s, worker_registry=%s",
            self._backend_manager,
            self._continuity_engine,
            self._validator_pipeline,
            self._worker_registry,
        )

    def run(self, episode_payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        logger.info(
            "CinematicPipelineV1_2.run invoked for episode_id=%s",
            episode_payload.get("episode_id"),
        )

        try:
            self._validate_governance()

            episode_result = self._run_episode(episode_payload, context)
            scenes_result = self._run_scenes(episode_result, context)
            shots_result = self._run_shots(scenes_result, context)
            render_result = self._run_render(episode_result, scenes_result, shots_result, context)
            continuity_result = self._run_continuity(episode_result, scenes_result, shots_result, render_result, context)

            result = {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "episode": episode_result,
                "scenes": scenes_result,
                "shots": shots_result,
                "render": render_result,
                "continuity": continuity_result,
                "context": context,
            }

            logger.info(
                "CinematicPipelineV1_2.run completed for episode_id=%s",
                episode_payload.get("episode_id"),
            )
            return result

        except (
            BackendManagerV1_2Error,
            ContinuityEngineV1_2Error,
            ValidatorPipelineV1_2Error,
            CinematicPipelineV1_2Error,
        ) as exc:
            logger.error("CinematicPipelineV1_2 controlled failure: %s", exc, exc_info=True)
            raise CinematicPipelineV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CinematicPipelineV1_2 unexpected failure: %s", exc, exc_info=True)
            raise CinematicPipelineV1_2Error(
                f"Unexpected error in CinematicPipelineV1_2.run: {exc}"
            ) from exc

    def _validate_governance(self) -> None:
        for domain in ("episode", "scene", "shot", "render"):
            violations = self._governance_validator.validate_governance_config(domain)
            if violations:
                logger.error(
                    "CinematicPipelineV1_2 governance violations for domain '%s': %s",
                    domain,
                    "; ".join(violations),
                )
                raise CinematicPipelineV1_2Error(
                    f"Governance configuration invalid for domain '{domain}': {violations}"
                )

    def _run_episode(self, episode_payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return self._episode_worker.run(episode_payload=episode_payload, context=context)

    def _run_scenes(self, episode_result: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._scene_worker.run(episode_payload=episode_result, context=context)

    def _run_shots(self, scenes_result: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._shot_worker.run(scenes_payload=scenes_result, context=context)

    def _run_render(
        self,
        episode_result: Dict[str, Any],
        scenes_result: List[Dict[str, Any]],
        shots_result: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._render_worker.run(
            episode_payload=episode_result,
            scenes_payload=scenes_result,
            shots_payload=shots_result,
            context=context,
        )

    def _run_continuity(
        self,
        episode_result: Dict[str, Any],
        scenes_result: List[Dict[str, Any]],
        shots_result: List[Dict[str, Any]],
        render_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        continuity_input = {
            "episode": episode_result,
            "scenes": scenes_result,
            "shots": shots_result,
            "render": render_result,
            "context": context,
        }
        return self._continuity_engine.run(continuity_input)


__all__ = ["CinematicPipelineV1_2", "CinematicPipelineV1_2Error"]
