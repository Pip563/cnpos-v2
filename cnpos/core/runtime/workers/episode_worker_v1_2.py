# cnpos/core/runtime/workers/episode_worker_v1_2.py
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)
logger = logging.getLogger(__name__)


class EpisodeWorkerV1_2Error(Exception):
    """Raised when EpisodeWorkerV1_2 encounters an unrecoverable error."""
    pass


class EpisodeWorkerV1_2:
    """
    EpisodeWorkerV1_2

    Deterministic episode-level worker for CNPOS v1_2.

    Responsibilities:
    - Load and apply the episode contract (episode_contract_v1_2.json).
    - Validate episode payloads via ValidatorPipelineV1_2 and governance rules.
    - Route episode generation/execution to LLMBackendManagerV1_2.
    - Provide a stable episode domain entry point for cinematic pipelines.

    Domain: episode
    Version: v1_2
    """

    DOMAIN = "episode"
    VERSION = "v1_2"

    def __init__(
        self,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        backend_manager: Optional[BackendManagerV1_2] = None,
        contract_path: Optional[str] = None,
    ) -> None:
        super().__init__(domain=self.DOMAIN, version=self.VERSION)

        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._validator_pipeline = (
        validator_pipeline or ValidatorPipelineV1_2()
        )
        # Resolve contract path relative to core/contracts
        backend_manager: Optional[BackendManagerV1_2] = None,if contract_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self._contract_path = os.path.join(
                base_dir,
                "contracts",
                "episode_contract_v1_2.json",
            )
        else:
            self._contract_path = contract_path

        self._contract_schema = self._load_contract_schema(self._contract_path)

        logger.debug(
            "EpisodeWorkerV1_2 initialized with contract_path=%s",
            self._contract_path,
        )

    # -------------------------------------------------------------------------
    # Runtime worker API
    # -------------------------------------------------------------------------

    def run(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an episode task.

        Args:
            payload: Episode payload (episode spec, prompts, metadata).
            context: Optional orchestration context.

        Returns:
            Dict[str, Any]: Episode execution result, including:
                - 'domain'
                - 'version'
                - 'validated_payload'
                - 'backend_result'
        """
        context = context or {}
        logger.info(
            "EpisodeWorkerV1_2.run invoked for episode_id=%s",
            payload.get("episode_id"),
        )

        try:
            validated_payload = self._validate_payload(payload)
            backend_result = self._execute_backend(validated_payload, context)

            result = {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "validated_payload": validated_payload,
                "backend_result": backend_result,
                "context": context,
            }

            logger.info(
                "EpisodeWorkerV1_2.run completed for episode_id=%s",
                payload.get("episode_id"),
            )
            return result

        except (
            ValidatorPipelineV1_2Error,
            BackendManagerV1_2Error,
            EpisodeWorkerV1_2Error,
        ) as exc:
            logger.error(
                "EpisodeWorkerV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise EpisodeWorkerV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error(
                "EpisodeWorkerV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise EpisodeWorkerV1_2Error(
                f"Unexpected error in EpisodeWorkerV1_2.run: {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_contract_schema(self, path: str) -> Dict[str, Any]:
        """
        Load episode contract schema from JSON file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            logger.debug(
                "EpisodeWorkerV1_2._load_contract_schema loaded schema from %s",
                path,
            )
            return schema
        except Exception as exc:
            logger.error(
                "EpisodeWorkerV1_2._load_contract_schema error reading %s: %s",
                path,
                exc,
                exc_info=True,
            )
            raise EpisodeWorkerV1_2Error(
                f"Failed to load episode contract schema from '{path}': {exc}"
            ) from exc

    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate episode payload against contract and governance rules.
        """
        logger.debug(
            "EpisodeWorkerV1_2._validate_payload payload_keys=%s",
            list(payload.keys()),
        )
        validated = self._validator_pipeline.validate(
            domain=self.DOMAIN,
            payload=payload,
            contract_schema=self._contract_schema,
            governance_loader=self._governance_loader,
        )
        logger.debug(
            "EpisodeWorkerV1_2._validate_payload completed; validated_keys=%s",
            list(validated.keys()),
        )
        return validated

    def _execute_backend(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute episode generation via LLMBackendManagerV1_2.

        Expected payload fields:
            - 'prompt': main episode prompt or instruction.
            - 'parameters': optional backend parameters.

        Returns:
            Dict[str, Any]: Backend result.
        """
        prompt = str(payload.get("prompt", "")).strip()
        parameters = payload.get("parameters") or {}

        if not prompt:
            logger.error("EpisodeWorkerV1_2._execute_backend missing 'prompt' in payload")
            raise EpisodeWorkerV1_2Error("Episode payload must contain a non-empty 'prompt'")

        logger.debug(
            "EpisodeWorkerV1_2._execute_backend prompt_len=%d parameters_keys=%s",
            len(prompt),
            list(parameters.keys()),
        )

        result = self._backend_manager.run_task(
            prompt=prompt,
            parameters=parameters,
            backend_key=context.get("backend_key"),
        )
        logger.debug(
            "EpisodeWorkerV1_2._execute_backend backend_result_keys=%s",
            list(result.keys()),
        )
        return result


__all__ = ["EpisodeWorkerV1_2", "EpisodeWorkerV1_2Error"]
