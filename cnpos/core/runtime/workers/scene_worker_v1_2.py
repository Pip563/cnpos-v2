from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2


class SceneWorkerV1_2Error(Exception):
    """Raised when scene generation or validation fails."""


class SceneWorkerV1_2:
    DOMAIN = "scene"
    VERSION = "v1_2"

    def __init__(self, validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
                 backend_manager: Optional[BackendManagerV1_2] = None,
                 contract_path: Optional[str] = None) -> None:
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._backend_manager = backend_manager or BackendManagerV1_2()
        path = contract_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts", "scene_contract_v1_2.json")
        with open(path, encoding="utf-8") as handle:
            self._schema = json.load(handle)
        Draft202012Validator.check_schema(self._schema)

    def run(self, episode_payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        context = context or {}
        episode = episode_payload.get("validated_payload", episode_payload)
        output = []
        for descriptor in episode.get("scenes", []):
            scene = {
                "domain": "SCENE", "version": "v1_2",
                "scene_id": descriptor["scene_id"], "episode_id": episode["episode_id"],
                "index": descriptor["index"], "slugline": descriptor["slugline"],
                "summary": descriptor.get("summary", ""),
                "characters": descriptor.get("characters", []),
                "shots": descriptor.get("shots", []),
                "beats": descriptor.get("beats", []),
                "prompt": descriptor.get("prompt", f"Scene: {descriptor['slugline']}"),
            }
            # Keep generation-only prompt outside the contract artifact.
            prompt = scene.pop("prompt")
            Draft202012Validator(self._schema).validate(scene)
            validated = self._validator_pipeline.validate(domain=self.DOMAIN, payload=scene, contract_schema=self._schema, context=context)
            backend = self._backend_manager.run_task(prompt=prompt, parameters={"stage": self.DOMAIN, "scene_id": scene["scene_id"]}, backend_key=context.get("backend_key"))
            output.append({"domain": self.DOMAIN, "version": self.VERSION, "validated_payload": validated, "backend_result": backend, "prompt": prompt})
        return output


__all__ = ["SceneWorkerV1_2", "SceneWorkerV1_2Error"]
