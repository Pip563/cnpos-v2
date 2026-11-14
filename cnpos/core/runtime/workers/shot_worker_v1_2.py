from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2


class ShotWorkerV1_2Error(Exception):
    """Raised when shot generation or validation fails."""


class ShotWorkerV1_2:
    DOMAIN = "shot"
    VERSION = "v1_2"

    def __init__(self, validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
                 backend_manager: Optional[BackendManagerV1_2] = None,
                 contract_path: Optional[str] = None) -> None:
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._backend_manager = backend_manager or BackendManagerV1_2()
        path = contract_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts", "shot_contract_v1_2.json")
        with open(path, encoding="utf-8") as handle:
            self._schema = json.load(handle)
        Draft202012Validator.check_schema(self._schema)

    def run(self, scenes_payload: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        context = context or {}
        result = []
        for scene_result in scenes_payload:
            scene = scene_result["validated_payload"]
            descriptors = scene.get("shots") or [{"shot_id": f"{scene['scene_id']}-shot-001", "index": 0, "type": "MS", "description": scene.get("summary", scene["slugline"])}]
            for descriptor in descriptors:
                shot = {
                    "domain": "SHOT", "version": "v1_2",
                    "shot_id": descriptor["shot_id"], "scene_id": scene["scene_id"],
                    "episode_id": scene["episode_id"], "index": descriptor["index"],
                    "type": descriptor.get("type", "MS"), "duration_seconds": descriptor.get("duration_seconds", 5),
                    "actions": descriptor.get("actions", [{"action_id": f"{descriptor['shot_id']}-action-001", "description": descriptor.get("description", "Establish the scene.")}]),
                }
                Draft202012Validator(self._schema).validate(shot)
                validated = self._validator_pipeline.validate(domain=self.DOMAIN, payload=shot, contract_schema=self._schema, context=context)
                prompt = descriptor.get("prompt", f"Shot: {descriptor.get('description', shot['type'])}")
                backend = self._backend_manager.run_task(prompt=prompt, parameters={"stage": self.DOMAIN, "shot_id": shot["shot_id"]}, backend_key=context.get("backend_key"))
                result.append({"domain": self.DOMAIN, "version": self.VERSION, "validated_payload": validated, "backend_result": backend, "prompt": prompt})
        return result


__all__ = ["ShotWorkerV1_2", "ShotWorkerV1_2Error"]
