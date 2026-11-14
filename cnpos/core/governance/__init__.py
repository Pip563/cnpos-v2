"""Governance components, lazily exported to avoid import cycles."""
from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "GovernanceLoaderV1_2": "cnpos.core.governance.governance_loader_v1_2",
    "GovernanceLoaderV1_2Error": "cnpos.core.governance.governance_loader_v1_2",
    "GovernanceValidatorV1_2": "cnpos.core.governance.governance_validator_v1_2",
    "GovernanceValidatorV1_2Error": "cnpos.core.governance.governance_validator_v1_2",
    "CodeMutationRulesV1_2": "cnpos.core.governance.code_mutation_rules_v1_2",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module), name)
