"""Runtime components. Imports are intentionally lazy to avoid package cycles."""
from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "BackendManagerV1_2": "cnpos.core.runtime.backend_manager_v1_2",
    "BackendManagerV1_2Error": "cnpos.core.runtime.backend_manager_v1_2",
    "ContinuityEngineV1_2": "cnpos.core.runtime.continuity_engine_v1_2",
    "ContinuityEngineV1_2Error": "cnpos.core.runtime.continuity_engine_v1_2",
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(import_module(module), name)
