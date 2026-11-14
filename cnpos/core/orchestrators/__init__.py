"""Orchestration components, lazily exported to avoid import cycles."""
from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "CharacterPipelineV1_2": "cnpos.core.orchestrators.character_pipeline_v1_2",
    "CharacterPipelineV1_2Error": "cnpos.core.orchestrators.character_pipeline_v1_2",
    "CinematicPipelineV1_2": "cnpos.core.orchestrators.cinematic_pipeline_v1_2",
    "CinematicPipelineV1_2Error": "cnpos.core.orchestrators.cinematic_pipeline_v1_2",
    "CNPOSOrchestratorV1_2": "cnpos.core.orchestrators.cnpos_orchestrator_v1_2",
    "CNPOSOrchestratorV1_2Error": "cnpos.core.orchestrators.cnpos_orchestrator_v1_2",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module), name)
