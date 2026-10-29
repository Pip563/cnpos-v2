# cnpos/core/orchestrators/__init__.py
from __future__ import annotations

import logging

from cnpos.core.orchestrators.character_pipeline_v1_2 import (
    CharacterPipelineV1_2,
    CharacterPipelineV1_2Error,
)
from cnpos.core.orchestrators.cinematic_pipeline_v1_2 import (
    CinematicPipelineV1_2,
    CinematicPipelineV1_2Error,
)
from cnpos.core.orchestrators.cnpos_orchestrator_v1_2 import (
    CNPOSOrchestratorV1_2,
    CNPOSOrchestratorV1_2Error,
)
from cnpos.core.automation.code_pipeline_v1_2 import (
    CodeAutomationPipelineV1_2,
    CodeAutomationPipelineV1_2Error,
)
from cnpos.core.orchestrators.pipeline_map_v1_2 import PipelineMapV1_2
from cnpos.core.orchestrators.telemetry.telemetry_manager import TelemetryManager
from cnpos.core.orchestrators.telemetry.event_stream import EventStream
from cnpos.core.orchestrators.telemetry.metrics_exporter import OrchestratorMetricsExporter

logger = logging.getLogger(__name__)

__all__ = [
    # Pipelines
    "CharacterPipelineV1_2",
    "CharacterPipelineV1_2Error",
    "CinematicPipelineV1_2",
    "CinematicPipelineV1_2Error",
    "CodeAutomationPipelineV1_2",
    "CodeAutomationPipelineV1_2Error",
    # Top-level orchestrator
    "CNPOSOrchestratorV1_2",
    "CNPOSOrchestratorV1_2Error",
    # Pipeline map
    "PipelineMapV1_2",
    # Telemetry
    "TelemetryManager",
    "EventStream",
    "OrchestratorMetricsExporter",
]
