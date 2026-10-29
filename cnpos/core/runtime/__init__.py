# cnpos/core/runtime/__init__.py
from __future__ import annotations

import logging

from cnpos.core.runtime.backend_manager_v1_2 import (
    LLMBackendManagerV1_2,
    BackendManagerV1_2Error,
)
from cnpos.core.runtime.continuity_engine_v1_2 import (
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

logger = logging.getLogger(__name__)

__all__ = [
    # Backend manager
    "LLMBackendManagerV1_2",
    "BackendManagerV1_2Error",
    # Continuity engine
    "ContinuityEngineV1_2",
    "ContinuityEngineV1_2Error",
    # Workers
    "EpisodeWorkerV1_2",
    "SceneWorkerV1_2",
    "ShotWorkerV1_2",
    "RenderWorkerV1_2",
    "PromptWorkerV1_2",
    "WorkerRegistryV1_2",
]
