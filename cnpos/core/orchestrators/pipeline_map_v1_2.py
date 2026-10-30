# cnpos/core/orchestrators/pipeline_map_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict

from cnpos.core.automation.code_pipeline_v1_2 import CodePipelineV1_2
from cnpos.core.orchestrators.character_pipeline_v1_2 import CharacterPipelineV1_2
from cnpos.core.orchestrators.cinematic_pipeline_v1_2 import CinematicPipelineV1_2

logger = logging.getLogger(__name__)


class PipelineMapV1_2Error(Exception):
    """Raised when PipelineMapV1_2 encounters an unrecoverable error."""


class PipelineMapV1_2:
    """
    PipelineMapV1_2

    Deterministic registry of all orchestrated pipelines for CNPOS v1_2.

    Responsibilities:
    - Provide a stable mapping from logical pipeline keys to pipeline classes.
    - Ensure all pipelines are strict v1_2 and correctly imported.
    - Act as the single source of truth for cnpos_orchestrator_v1_2 routing.
    """

    VERSION = "v1_2"

    def __init__(self) -> None:
        self._pipelines: Dict[str, Any] = {
            "character_pipeline_v1_2": CharacterPipelineV1_2,
            "cinematic_pipeline_v1_2": CinematicPipelineV1_2,
            "code_pipeline_v1_2": CodePipelineV1_2,
            "code_automation_pipeline_v1_2": CodePipelineV1_2,
        }

        logger.debug(
            "PipelineMapV1_2 initialized with keys=%s",
            list(self._pipelines.keys()),
        )

    def get_pipeline_class(self, key: str) -> Any:
        try:
            pipeline_cls = self._pipelines[key]
        except KeyError as exc:
            logger.error(
                "PipelineMapV1_2.get_pipeline_class unknown key=%s",
                key,
                exc_info=True,
            )
            raise PipelineMapV1_2Error(f"Unknown pipeline key '{key}'") from exc

        return pipeline_cls

    def list_pipelines(self) -> Dict[str, Any]:
        return dict(self._pipelines)


__all__ = ["PipelineMapV1_2", "PipelineMapV1_2Error"]
