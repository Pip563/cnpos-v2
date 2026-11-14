"""Validator components, lazily exported to prevent circular imports."""
from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "ContinuityValidatorV1_2": "cnpos.core.validators.continuity_validator_v1_2",
    "ContinuityValidatorV1_2Error": "cnpos.core.validators.continuity_validator_v1_2",
    "GovernanceValidatorV1_2": "cnpos.core.validators.governance_validator_v1_2",
    "GovernanceValidatorV1_2Error": "cnpos.core.validators.governance_validator_v1_2",
    "MutationValidatorV1_2": "cnpos.core.validators.mutation_validator_v1_2",
    "MutationValidatorV1_2Error": "cnpos.core.validators.mutation_validator_v1_2",
    "ValidatorPipelineV1_2": "cnpos.core.validators.validator_pipeline_v1_2",
    "ValidatorPipelineV1_2Error": "cnpos.core.validators.validator_pipeline_v1_2",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module), name)
