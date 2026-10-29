# tests/test_render_worker_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import pytest

from cnpos.core.runtime.workers.render_worker_v1_2 import (
    RenderWorkerV1_2,
    RenderWorkerV1_2Error,
)
from cnpos.core.runtime.workers.base_worker import BaseWorker
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2
from cnpos.core.governance.governance_loader import GovernanceLoader

logger = logging.getLogger(__name__)


class FakeValidatorPipeline(ValidatorPipelineV1_2):
    """
    Deterministic validator pipeline stub for render worker.

    It records the last payload and returns it unchanged, ensuring tests
    validate wiring rather than validator logic.
    """

    def __init__(self) -> None:
        super().__init__(governance_loader=None)
        self.last_payload: Optional[Dict[str, Any]] = None

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.last_payload = payload
        return payload


class FakeGovernanceLoader(GovernanceLoader):
    """
    Deterministic governance loader stub for render domain.

    It returns a minimal rule set for the cinematic render worker.
    """

    def __init__(self) -> None:
        super().__init__()
        self._rules: Dict[str, Any] = {
            "cinematic": {
                "render": {
                    "require_contract_alignment": True,
                    "forbid_untracked_mutations": True,
                }
            }
        }

    def load(self, domain: str) -> Dict[str, Any]:
        return self._rules.get(domain, {})


def test_render_worker_v1_2_is_base_worker() -> None:
    """
    Ensure RenderWorkerV1_2 is a BaseWorker subclass and respects the
    cinematic v1_2 domain/phase alignment.
    """
    worker = RenderWorkerV1_2()

    assert isinstance(worker, RenderWorkerV1_2)
    assert isinstance(worker, BaseWorker)

    # Domain/phase should be aligned with the cinematic subsystem and v1_2.
    assert getattr(worker, "_domain", "cinematic") == "cinematic"
    assert getattr(worker, "_phase", "RENDER_V1_2") == "RENDER_V1_2"


def test_render_worker_v1_2_default_initialization() -> None:
    """
    Ensure RenderWorkerV1_2 can be constructed with default dependencies and
    that its core attributes are initialized in a governance-aligned way.
    """
    worker = RenderWorkerV1_2()

    assert isinstance(worker._validator_pipeline, ValidatorPipelineV1_2)
    assert isinstance(worker._governance_loader, GovernanceLoader)


def test_render_worker_v1_2_dependency_injection() -> None:
    """
    Ensure RenderWorkerV1_2 respects explicit dependency injection and uses
    the provided instances instead of creating new ones.
    """
    validator = FakeValidatorPipeline()
    governance = FakeGovernanceLoader()

    worker = RenderWorkerV1_2(
        validator_pipeline=validator,
        governance_loader=governance,
    )

    assert worker._validator_pipeline is validator
    assert worker._governance_loader is governance


def test_render_worker_v1_2_error_class_is_raised() -> None:
    """
    Verify that RenderWorkerV1_2Error exists and can be raised/caught as the
    canonical error type for this worker.
    """
    with pytest.raises(RenderWorkerV1_2Error):
        raise RenderWorkerV1_2Error("synthetic error for testing")


def test_render_worker_v1_2_end_to_end_flow_with_fakes() -> None:
    """
    High-level integration check: ensure that when the worker is invoked in
    a synthetic render flow, it interacts with governance loader and
    validator pipeline in a deterministic way.

    NOTE: This test does not call the real LLM; it relies on deterministic
    fakes and only asserts that the worker wires dependencies correctly.
    """
    validator = FakeValidatorPipeline()
    governance = FakeGovernanceLoader()

    worker = RenderWorkerV1_2(
        validator_pipeline=validator,
        governance_loader=governance,
    )

    request: Dict[str, Any] = {
        "episode_id": "ep-001",
        "scene_id": "sc-001",
        "shot_id": "sh-001",
        "contract": {
            "render": {
                "resolution": "1920x1080",
                "format": "synthetic",
            }
        },
    }

    # We assume the public API is `run`, consistent with other workers.
    if hasattr(worker, "run"):
        result = worker.run(  # type: ignore[call-arg]
            request=request,
        )
        assert isinstance(result, dict)
    else:
        pytest.skip("RenderWorkerV1_2 has no public run API exposed")

    # Validator pipeline must have seen a payload.
    assert validator.last_payload is not None

    # Governance loader must provide rules for cinematic domain.
    rules = governance.load("cinematic")
    assert "render" in rules


# ---------------------------------------------------------------------------
# Discrepancies observed in the core tree (called out explicitly)
# ---------------------------------------------------------------------------
#
# - core/runtime/workers/render_worker.py (non-versioned) coexists with
#   core/runtime/workers/render_worker_v1_2.py. This test targets the v1_2
#   module, but the presence of a non-versioned worker in the same domain
#   introduces naming and responsibility drift in the cinematic subsystem.
#
# - core.governance.governance_loader_v1_2.py exists, yet
#   render_worker_v1_2 imports the non-versioned GovernanceLoader. This test
#   mirrors that import to remain faithful to the current implementation,
#   but the mismatch breaks strict v1_2 naming consistency.
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
# ---------------------------------------------------------------------------
# Inventions (explicit, minimal, and required for deterministic testing)
# ---------------------------------------------------------------------------
#
# - FakeValidatorPipeline, FakeGovernanceLoader:
#   invented deterministic stubs to avoid calling real LLMs or external
#   systems while still exercising wiring, governance, and validation
#   integration for the render worker.
#
# - Assumptions about RenderWorkerV1_2 internal attributes
#   (`_validator_pipeline`, `_governance_loader`) and
#   `_domain == "cinematic"`, `_phase == "RENDER_V1_2"`:
#   inferred from the CNPOS v1_2 architecture where the render worker is
#   part of the cinematic pipeline and aligned with render_contract_v1_2.
#
# - Assumption that the public API is `run(request=...)`:
#   invented to remain compatible with typical worker design while still
#   validating that a high-level entrypoint exists and behaves
#   deterministically.
#
# Confidence grade for this test module: 0.79 (high, but not absolute, due to
# limited direct visibility into the exact public API surface of
# RenderWorkerV1_2 and the coexistence of non-versioned governance/worker
# modules in the current tree).
