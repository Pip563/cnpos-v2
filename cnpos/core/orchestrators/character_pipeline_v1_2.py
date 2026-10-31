# cnpos/core/runtime/workers/episode_worker_v1_2.py
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class EpisodeWorkerV1_2Error(Exception):
    """Raised when EpisodeWorkerV1_2 encounters an unrecoverable error."""


class EpisodeWorkerV1_2:
    """Deterministic episode-level worker for CNPOS v1_2."""

    DOMAIN = "episode"
    VERSION = "v1_2"

    def __init__(
        self,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        backend_manager: Optional[BackendManagerV1_2] = None,
        contract_path: Optional[str] = None,
    ) -> None:
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._backend_manager = backend_manager or BackendManagerV1_2()

        if contract_path is None:
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
            "EpisodeWorkerV1_2 initialized with contract_path=%s backend_manager=%s",
            self._contract_path,
            self._backend_manager,
        )

    def run(
        self,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute an episode task."""
        if payload is None:
            payload = request or {}
        context = context or {}

        logger.info(
            "EpisodeWorkerV1_2.run invoked for episode_id=%s",
            payload.get("episode_id") if isinstance(payload, dict) else None,
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
                payload.get("episode_id") if isinstance(payload, dict) else None,
            )
            return result

        except (
            ValidatorPipelineV1_2Error,
            BackendManagerV1_2Error,
            EpisodeWorkerV1_2Error,
        ) as exc:
            logger.error("EpisodeWorkerV1_2 controlled failure: %s", exc, exc_info=True)
            raise EpisodeWorkerV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("EpisodeWorkerV1_2 unexpected failure: %s", exc, exc_info=True)
            raise EpisodeWorkerV1_2Error(
                f"Unexpected error in EpisodeWorkerV1_2.run: {exc}"
            ) from exc

    def _load_contract_schema(self, path: str) -> Dict[str, Any]:
        """Load episode contract schema from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as handle:
                schema = json.load(handle)
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
        """Validate episode payload against contract and governance rules."""
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
        """Execute episode generation via BackendManagerV1_2."""
        prompt = str(payload.get("prompt") or payload.get("seed") or "").strip()
        if not prompt:
            prompt = json.dumps(payload, sort_keys=True)

        parameters = payload.get("parameters") or {}

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
