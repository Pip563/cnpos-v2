"""Character and automation agents, exposed lazily to avoid import cycles."""
from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "CharacterArcWorkerV1_2": "cnpos.core.agents.character_arc_worker_v1_2",
    "CharacterArcWorkerV1_2Error": "cnpos.core.agents.character_arc_worker_v1_2",
    "CharacterContinuityWorkerV1_2": "cnpos.core.agents.character_continuity_worker_v1_2",
    "CharacterContinuityWorkerV1_2Error": "cnpos.core.agents.character_continuity_worker_v1_2",
    "CharacterProfileWorkerV1_2": "cnpos.core.agents.character_profile_worker_v1_2",
    "CharacterProfileWorkerV1_2Error": "cnpos.core.agents.character_profile_worker_v1_2",
    "PromptAgent": "cnpos.core.agents.prompt_agent_v1_2",
    "PromptAgentV1_2": "cnpos.core.agents.prompt_agent_v1_2",
    "PromptAgentV1_2Error": "cnpos.core.agents.prompt_agent_v1_2",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module), name)
