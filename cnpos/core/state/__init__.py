"""State components. Keep package initialization free of eager imports."""
from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "MutationStateManagerV1_2": "cnpos.core.state.mutation_state_manager_v1_2",
    "MutationStateManagerV1_2Error": "cnpos.core.state.mutation_state_manager_v1_2",
    "ContinuityStateV1_2": "cnpos.core.state.continuity_state_v1_2",
    "CharacterMutationClassifierV1_2": "cnpos.core.state.character_mutation_classifier_v1_2",
    "CharacterMutationClassifierV1_2Error": "cnpos.core.state.character_mutation_classifier_v1_2",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module), name)
