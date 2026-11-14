from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from jsonschema import Draft202012Validator

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2

logger = logging.getLogger(__name__)


class EpisodeWorkerV1_2Error(Exception):
    """Raised when episode validation or deterministic execution fails."""


class EpisodeWorkerV1_2:
    DOMAIN = "episode"
    VERSION = "v1_2"

    def __init__(self, validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
                 backend_manager: Optional[BackendManagerV1_2] = None,
                 contract_path: Optional[str] = None) -> None:
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._contract_path = contract_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts", "episode_contract_v1_2.json")
        with open(self._contract_path, encoding="utf-8") as handle:
            self._schema = json.load(handle)
        Draft202012Validator.check_schema(self._schema)

    def run(self, episode_payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        try:
            Draft202012Validator(self._schema).validate(episode_payload)
            validated = self._validator_pipeline.validate(domain=self.DOMAIN, payload=episode_payload, contract_schema=self._schema, context=context)
            result = self._backend_manager.run_task(
                prompt=f"episode:{episode_payload['episode_id']}:{episode_payload['logline']}",
                parameters={"stage": self.DOMAIN, "episode_id": episode_payload["episode_id"]},
                backend_key=context.get("backend_key"),
            )
            return {"domain": self.DOMAIN, "version": self.VERSION, "validated_payload": validated, "backend_result": result, "context": context}
        except Exception as exc:
            raise EpisodeWorkerV1_2Error(str(exc)) from exc


__all__ = ["EpisodeWorkerV1_2", "EpisodeWorkerV1_2Error"]
