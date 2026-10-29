# cnpos/core/orchestrators/pipeline_map_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict

from cnpos.core.orchestrators.character_pipeline_v1_2 import CharacterPipelineV1_2
from cnpos.core.orchestrators.cinematic_pipeline_v1_2 import CinematicPipelineV1_2
from cnpos.core.automation.code_pipeline_v1_2 import (
    CodePipelineV1_2,
)
logger = logging.getLogger(__name__)


class PipelineMapV1_2Error(Exception):
    """Raised when PipelineMapV1_2 encounters an unrecoverable error."""
    pass


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
            # Cinematic / character pipelines
            "character_pipeline_v1_2": CharacterPipelineV1_2,
            "cinematic_pipeline_v1_2": CinematicPipelineV1_2,
            # Code automation pipeline (located under cnpos/core/orchestrators/)
            "code_automation_pipeline_v1_2": CodeAutomationPipelineV1_2,
        }

        logger.debug(
            "PipelineMapV1_2 initialized with keys=%s",
            list(self._pipelines.keys()),
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def get_pipeline_class(self, key: str) -> Any:
        """
        Return the pipeline class associated with the given key.

        Args:
            key: Logical pipeline identifier (e.g., 'code_automation_pipeline_v1_2').

        Returns:
            Any: Pipeline class.

        Raises:
            PipelineMapV1_2Error if the key is unknown.
        """
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
        """
        Return a copy of the pipeline registry.
        """
        return dict(self._pipelines)


__all__ = ["PipelineMapV1_2", "PipelineMapV1_2Error"]
