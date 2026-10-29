# cnpos/core/__init__.py
from __future__ import annotations

import logging

from cnpos.core.agents import (
    CharacterArcWorkerV1_2,
    CharacterArcWorkerV1_2Error,
    CharacterContinuityWorkerV1_2,
    CharacterContinuityWorkerV1_2Error,
    CharacterProfileWorkerV1_2,
    CharacterProfileWorkerV1_2Error,
    CodePlannerAgent,
    CodePlannerAgentV1_2Error,
    CodeReviewerAgent,
    CodeReviewerAgentV1_2Error,
    CodeTestAgent,
    CodeTestAgentV1_2Error,
    CodeWriterAgent,
    CodeWriterAgentV1_2Error,
    PromptAgent,
    PromptAgentV1_2Error,
)
from cnpos.core.contracts import (
    EPISODE_CONTRACT_V1_2,
    RENDER_CONTRACT_V1_2,
    SCENE_CONTRACT_V1_2,
    SHOT_CONTRACT_V1_2,
    load_contract,
)
from cnpos.core.governance import (
    CodeMutationRuleV1_2,
    CodeMutationRulesV1_2,
    CodeMut,
    GovernanceLoaderV1_2,
    GovernanceLoaderV1_2Error,
    GovernanceValidatorV1_2,
    GovernanceValidatorV1_2Error,
)
from cnpos.core.orchestrators import (
    OrchestratorV1_2,
    PipelineMapV1_2,
    CinematicPipelineV1_2,
    CodeAutomationPipelineV1_2,
)
from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
    ContinuityEngineV1_2,
    ContinuityEngineV1_2Error,
)
from cnpos.core.runtime.workers import (
    EpisodeWorkerV1_2,
    SceneWorkerV1_2,
    ShotWorkerV1_2,
    RenderWorkerV1_2,
    PromptWorkerV1_2,
    WorkerRegistryV1_2,
)
from cnpos.core.state import (
    ContinuityStateV1_2,
    MutationStateManagerV1_2,
    CharacterMutationClassifierV1_2,
)

logger = logging.getLogger(__name__)

__version__ = "v1_2"

__all__ = [
    # Version
    "__version__",
    # Agents
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
    # Contracts
    "EPISODE_CONTRACT_V1_2",
    "RENDER_CONTRACT_V1_2",
    "SCENE_CONTRACT_V1_2",
    "SHOT_CONTRACT_V1_2",
    "load_contract",
    # Governance
    "CodeMutationRuleV1_2",
    "CodeMutationRulesV1_2",
    "CodeMut",
    "GovernanceLoaderV1_2",
    "GovernanceLoaderV1_2Error",
    "GovernanceValidatorV1_2",
    "GovernanceValidatorV1_2Error",
    # Orchestrators
    "OrchestratorV1_2",
    "PipelineMapV1_2",
    "CinematicPipelineV1_2",
    "CodeAutomationPipelineV1_2",
    # Runtime
    "BackendManagerV1_2",
    "BackendManagerV1_2Error",
    "ContinuityEngineV1_2",
    "ContinuityEngineV1_2Error",
    # Workers
    "EpisodeWorkerV1_2",
    "SceneWorkerV1_2",
    "ShotWorkerV1_2",
    "RenderWorkerV1_2",
    "PromptWorkerV1_2",
    "WorkerRegistryV1_2",
    # State
    "ContinuityStateV1_2",
    "MutationStateManagerV1_2",
    "CharacterMutationClassifierV1_2",
]
