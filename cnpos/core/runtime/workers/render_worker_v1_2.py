from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2


class RenderWorkerV1_2Error(Exception):
    """Raised when render-job construction or validation fails."""


class RenderWorkerV1_2:
    DOMAIN = "render"
    VERSION = "v1_2"

    def __init__(self, validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
                 backend_manager: Optional[BackendManagerV1_2] = None,
                 contract_path: Optional[str] = None) -> None:
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._backend_manager = backend_manager or BackendManagerV1_2()
        path = contract_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts", "render_contract_v1_2.json")
        with open(path, encoding="utf-8") as handle:
            self._schema = json.load(handle)
        Draft202012Validator.check_schema(self._schema)

    def run(self, episode_payload: Dict[str, Any], scenes_payload: List[Dict[str, Any]], shots_payload: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        episode = episode_payload.get("validated_payload", episode_payload)
        manifest = {
            "domain": "RENDER", "version": "v1_2", "render_id": f"render-{episode['episode_id']}",
            "episode_id": episode["episode_id"], "status": "queued",
            "output": {"container": "mp4", "codec": "h264", "resolution": "1920x1080", "frame_rate": 24},
            "assets": {"video_tracks": [], "audio_tracks": []},
            "timeline": [{"event_id": f"cut-{i:03d}", "type": "cut", "start_timecode": f"00:00:{i*5:02d}:00"} for i, _ in enumerate(shots_payload)],
        }
        Draft202012Validator(self._schema).validate(manifest)
        validated = self._validator_pipeline.validate(domain=self.DOMAIN, payload=manifest, contract_schema=self._schema, context=context)
        backend = self._backend_manager.run_task(prompt=f"Render job for {episode['episode_id']}", parameters={"stage": self.DOMAIN, "render_id": manifest["render_id"]}, backend_key=context.get("backend_key"))
        return {"domain": self.DOMAIN, "version": self.VERSION, "validated_payload": validated, "backend_result": backend, "context": context}


__all__ = ["RenderWorkerV1_2", "RenderWorkerV1_2Error"]
