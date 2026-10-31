# cnpos/core/agents/prompt_agent_v1_2.py
from __future__ import annotations

from cnpos.core.agents.prompt_agent import PromptAgent, PromptAgentV1_2Error


class PromptAgentV1_2(PromptAgent):
    """Canonical v1_2 prompt agent wrapper."""

    DOMAIN = "PROMPT_AGENT"
    VERSION = "v1_2"


__all__ = ["PromptAgent", "PromptAgentV1_2", "PromptAgentV1_2Error"]
