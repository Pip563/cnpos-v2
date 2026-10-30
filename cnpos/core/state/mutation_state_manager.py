# cnpos/core/state/mutation_state_manager.py
from __future__ import annotations

from cnpos.core.state.mutation_state_manager_v1_2 import (
    MutationStateManagerV1_2 as MutationStateManager,
)
from cnpos.core.state.mutation_state_manager_v1_2 import (
    MutationStateManagerV1_2Error,
)

__all__ = ["MutationStateManager", "MutationStateManagerV1_2Error"]
