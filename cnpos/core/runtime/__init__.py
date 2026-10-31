# cnpos/core/__init__.py
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__version__ = "v1_2"

__all__ = [
    "__version__",
    "BackendManagerV1_2",
    "CharacterMutationClassifierV1_2",
    "CharacterPipelineV1_2",
    "EpisodeWorkerV1_2",
    "GovernanceLoaderV1_2",
    "GovernanceValidatorV1_2",
    "ValidatorPipelineV1_2",
]


def __getattr__(name: str):
    lazy_imports = {
        "BackendManagerV1_2": "cnpos.core.runtime.backend_manager_v1_2",
        "CharacterMutationClassifierV1_2": "cnpos.core.state.character_mutation_classifier_v1_2",
        "CharacterPipelineV1_2": "cnpos.core.orchestrators.character_pipeline_v1_2",
        "EpisodeWorkerV1_2": "cnpos.core.runtime.workers.episode_worker_v1_2",
        "GovernanceLoaderV1_2": "cnpos.core.governance.governance_loader_v1_2",
        "GovernanceValidatorV1_2": "cnpos.core.governance.governance_validator_v1_2",
        "ValidatorPipelineV1_2": "cnpos.core.validators.validator_pipeline_v1_2",
    }
    if name not in lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = __import__(lazy_imports[name], fromlist=[name])
    return getattr(module, name)
