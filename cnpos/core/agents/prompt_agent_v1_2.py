# cnpos/core/runtime/workers/render_worker_v1_2.py
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
    BackendManagerV1_2Error,
)
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class RenderWorkerV1_2Error(Exception):
    """Raised when RenderWorkerV1_2 encounters an unrecoverable error."""


class RenderWorkerV1_2:
    """Deterministic render worker for CNPOS v1_2."""

    DOMAIN = "render"
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
                "render_contract_v1_2.json",
            )
        else:
            self._contract_path = contract_path

        self._contract_schema = self._load_contract_schema(self._contract_path)

        logger.debug(
            "RenderWorkerV1_2 initialized contract_path=%s",
            self._contract_path,
        )

    def run(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a render task."""
        context = context or {}
        logger.info(
            "RenderWorkerV1_2.run render_id=%s",
            payload.get("render_id"),
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
                "RenderWorkerV1_2 completed render_id=%s",
                payload.get("render_id"),
            )
            return result

        except (
            ValidatorPipelineV1_2Error,
            BackendManagerV1_2Error,
            RenderWorkerV1_2Error,
        ) as exc:
            logger.error(
                "RenderWorkerV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise RenderWorkerV1_2Error(str(exc)) from exc

        except Exception as exc:
            logger.error(
                "RenderWorkerV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise RenderWorkerV1_2Error(
                f"Unexpected error in RenderWorkerV1_2.run: {exc}"
            ) from exc

    def _load_contract_schema(self, contract_path: str) -> Dict[str, Any]:
        """Load render contract schema."""
        if not os.path.isfile(contract_path):
            raise RenderWorkerV1_2Error(f"Render contract not found: {contract_path}")

        try:
            with open(contract_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception as exc:
            raise RenderWorkerV1_2Error(
                f"Failed to load render contract: {exc}"
            ) from exc

    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payload through ValidatorPipelineV1_2."""
        required_fields = self._contract_schema.get("required", [])
        missing = [field for field in required_fields if field not in payload]

        if missing:
            raise RenderWorkerV1_2Error(
                f"Missing required contract fields: {missing}"
            )

        return self._validator_pipeline.validate(
            domain=self.DOMAIN,
            payload=payload,
            contract_schema=self._contract_schema,
            governance_loader=self._governance_loader,
            context={
                "worker": "RenderWorkerV1_2",
                "version": self.VERSION,
            },
        )

    def _execute_backend(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute render generation through backend manager."""
        prompt = payload.get("prompt")
        if not prompt:
            raise RenderWorkerV1_2Error("Render prompt is required.")

        result = self._backend_manager.generate(
            prompt=prompt,
            domain="cinematic",
            phase="RENDER",
            task_type=self.DOMAIN,
            extra={
                "context": context,
                "payload": payload,
            },
        )

        if not isinstance(result, dict):
            raise BackendManagerV1_2Error("Backend returned non-dict response.")

        return result


__all__ = ["RenderWorkerV1_2", "RenderWorkerV1_2Error"]
