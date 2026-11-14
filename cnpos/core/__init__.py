"""CNPOS core public API with lazy imports to avoid package import cycles."""
from __future__ import annotations

from importlib import import_module

__version__ = "v1_2"

_EXPORTS = {
    "BackendManagerV1_2": "cnpos.core.runtime.backend_manager_v1_2",
    "BackendManagerV1_2Error": "cnpos.core.runtime.backend_manager_v1_2",
    "CharacterMutationClassifierV1_2": "cnpos.core.state.character_mutation_classifier_v1_2",
    "CharacterMutationClassifierV1_2Error": "cnpos.core.state.character_mutation_classifier_v1_2",
    "CharacterPipelineV1_2": "cnpos.core.orchestrators.character_pipeline_v1_2",
    "CharacterPipelineV1_2Error": "cnpos.core.orchestrators.character_pipeline_v1_2",
    "EpisodeWorkerV1_2": "cnpos.core.runtime.workers.episode_worker_v1_2",
    "EpisodeWorkerV1_2Error": "cnpos.core.runtime.workers.episode_worker_v1_2",
    "GovernanceLoaderV1_2": "cnpos.core.governance.governance_loader_v1_2",
    "GovernanceLoaderV1_2Error": "cnpos.core.governance.governance_loader_v1_2",
    "GovernanceValidatorV1_2": "cnpos.core.governance.governance_validator_v1_2",
    "GovernanceValidatorV1_2Error": "cnpos.core.governance.governance_validator_v1_2",
    "ValidatorPipelineV1_2": "cnpos.core.validators.validator_pipeline_v1_2",
    "ValidatorPipelineV1_2Error": "cnpos.core.validators.validator_pipeline_v1_2",
}

__all__ = ["__version__", *_EXPORTS]


def __getattr__(name: str):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_name)
    value = getattr(module, name)
    globals()[name] = value
    return value
