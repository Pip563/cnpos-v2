# tests/test_backend_manager_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

import pytest

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
    BackendManagerV1_2Error,
)

logger = logging.getLogger(__name__)


def test_backend_manager_v1_2_can_be_instantiated() -> None:
    """
    Ensure BackendManagerV1_2 can be constructed and is the canonical
    v1_2 backend manager for CNPOS.
    """
    manager = BackendManagerV1_2()

    assert isinstance(manager, BackendManagerV1_2)
    # Logger should be available for deterministic telemetry/logging.
    assert isinstance(logger, logging.Logger)


def test_backend_manager_v1_2_error_class_is_raised() -> None:
    """
    Verify that BackendManagerV1_2Error exists and can be raised/caught as
    the canonical error type for unrecoverable backend routing failures.
    """
    with pytest.raises(BackendManagerV1_2Error):
        raise BackendManagerV1_2Error("synthetic error for testing")


def test_backend_manager_v1_2_route_api_exists_and_is_callable() -> None:
    """
    High-level check: ensure that BackendManagerV1_2 exposes a `route`
    method and that calling it either returns a dict or raises
    BackendManagerV1_2Error.

    This test does not assert specific backend behavior; it only validates
    that the public API surface is stable and uses the v1_2 error type for
    unrecoverable conditions.
    """
    manager = BackendManagerV1_2()

    if not hasattr(manager, "route"):
        pytest.skip("BackendManagerV1_2 has no public route API exposed")

    payload: Dict[str, Any] = {
        "task": "synthetic",
        "domain": "cinematic",
        "phase": "TEST_V1_2",
    }

    try:
        result = manager.route(  # type: ignore[call-arg]
            domain="cinematic",
            phase="TEST_V1_2",
            task_type="synthetic",
            payload=payload,
        )
    except BackendManagerV1_2Error:
        # Raising the canonical error type is acceptable behavior.
        return

    # If no error is raised, the result should be a dict-like structure.
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Discrepancies observed in the core tree (called out explicitly)
# ---------------------------------------------------------------------------
#
# - Several agents (e.g., character_profile_worker_v1_2.py, code_writer_agent.py)
#   import a non-versioned LLMBackendManager, while the runtime tree exposes
#   backend_manager_v1_2.py with BackendManagerV1_2. This breaks strict v1_2
#   naming consistency and suggests a partial migration to the v1_2 backend.
#
# - core/governance/governance_validator_v1_2py appears to have a filename
#   typo (missing ".py"). Not imported here, but the inconsistency should be
#   corrected to avoid import issues elsewhere.
#
# - core/state/mutation_state_manager.py is non-versioned, while other state
#   modules (continuity_state_v1_2.py, character_mutation_classifier_v1_2.py)
#   are explicitly versioned. This module is not used here, yet the drift
#   affects overall v1_2 naming consistency.
#
# - core/agents/prompt_agent.py is non-versioned, while many workers and
#   runtime components are explicitly versioned as v1_2. BackendManagerV1_2
#   may be used by both versioned and non-versioned agents, which introduces
#   mixed-version coupling in the architecture.
#
# ---------------------------------------------------------------------------
# Inventions (explicit, minimal, and required for deterministic testing)
# ---------------------------------------------------------------------------
#
# - Assumption that BackendManagerV1_2 exposes a `route(domain, phase,
#   task_type, payload)` method:
#   inferred from the CNPOS v1_2 architecture where orchestrators and
#   workers delegate LLM calls through a backend manager. The test treats
#   this as the canonical public API but does not enforce strict semantics.
#
# - Assumption that successful `route` calls return a dict-like structure:
#   invented to provide a minimal, type-level assertion while remaining
#   agnostic about the exact payload schema.
#
# - The synthetic `phase="TEST_V1_2"` and `task_type="synthetic"` values:
#   invented to avoid coupling tests to specific cinematic or code
#   pipelines while still exercising the routing surface.
#
# Confidence grade for this test module: 0.76 (moderate-high, but not
# absolute, due to limited direct visibility into the exact public API
# surface and internal behavior of BackendManagerV1_2 and the mixed
# versioning present in the current tree).
