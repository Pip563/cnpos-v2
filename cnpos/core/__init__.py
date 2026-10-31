# cnpos/core/__init__.py
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__version__ = "v1_2"

__all__ = [
    "__version__",
    "CharacterArcWorkerV1_2",
    "CharacterArcWorkerV1_2Error",
    "CharacterContinuityWorkerV1_2",
    "CharacterContinuityWorkerV1_2Error",
    "CharacterProfileWorkerV1_2",
    "CharacterProfileWorkerV1_2Error",
    "CodePlannerAgent",
    "CodePlannerAgentV1_2Error",
    "CodeReviewerAgent",
    "CodeReviewerAgentV1_2Error",
    "CodeTestAgent",
    "CodeTestAgentV1_2Error",
    "CodeWriterAgent",
    "CodeWriterAgentV1_2Error",
    "PromptAgent",
    "PromptAgentV1_2Error",
    "Back",
    "BackendManagerV1_2",
    "BackendManagerV1_2Error",
    "ContinuityEngineV1_2",
    "ContinuityEngineV1_2Error",
    "ContinuityStateV1_2",
    "MutationStateManagerV1_2",
    "CharacterMutationClassifierV1_2",
    "CinematicPipelineV1_2",
    "PipelineMapV1_2",
]


def __getattr__(name: str):
    lazy_imports = {
        "CharacterArcWorkerV1_2": "cnpos.core.agents.character_arc_worker_v1_2",
        "CharacterArcWorkerV1_2Error": "cnpos.core.agents.character_arc_worker_v1_2",
        "CharacterContinuityWorkerV1_2": "cnpos.core.agents.character_continuity_worker_v1_2",
        "CharacterContinuityWorkerV1_2Error": "cnpos.core.agents.character_continuity_worker_v1_2",
        "CharacterProfileWorkerV1_2": "cnpos.core.agents.character_profile_worker_v1_2",
        "CharacterProfileWorkerV1_2Error": "cnpos.core.agents.character_profile_worker_v1_2",
        "CodePlannerAgent": "cnpos.core.agents.code_planner_agent",
        "CodePlannerAgentV1_2Error": "cnpos.core.agents.code_planner_agent",
        "CodeReviewerAgent": "cnpos.core.agents.code_reviewer_agent",
        "CodeReviewerAgentV1_2Error": "cnpos.core.agents.code_reviewer_agent",
        "CodeTestAgent": "cnpos.core.agents.code_test_agent",
        "CodeTestAgentV1_2Error": "cnpos.core.agents.code_test_agent",
        "CodeWriterAgent": "cnpos.core.agents.code_writer_agent",
        "CodeWriterAgentV1_2Error": "cnpos.core.agents.code_writer_agent",
        "PromptAgent": "cnpos.core.agents.prompt_agent_v1_2",
        "PromptAgentV1_2Error": "cnpos.core.agents.prompt_agent_v1_2",
        "BackendManagerV1_2": "cnpos.core.runtime.backend_manager_v1_2",
        "BackendManagerV1_2Error": "cnpos.core.runtime.backend_manager_v1_2",
        "ContinuityEngineV1_2": "cnpos.core.runtime.continuity_engine_v1_2",
        "ContinuityEngineV1_2Error": "cnpos.core.runtime.continuity_engine_v1_2",
        "ContinuityStateV1_2": "cnpos.core.state.continuity_state_v1_2",
        "MutationStateManagerV1_2": "cnpos.core.state.mutation_state_manager_v1_2",
        "CharacterMutationClassifierV1_2": "cnpos.core.state.character_mutation_classifier_v1_2",
        "CinematicPipelineV1_2": "cnpos.core.orchestrators.cinematic_pipeline_v1_2",
        "PipelineMapV1_2": "cnpos.core.orchestrators.pipeline_map_v1_2",
        "Back": "cnpos.core.runtime.backend_manager_v1_2",
    }
    if name not in lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = __import__(lazy_imports[name], fromlist=[name])
    return getattr(module, name)
