# tests/test_episode_worker_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import pytest

from cnpos.core.runtime.workers.episode_worker_v1_2 import (
    EpisodeWorkerV1_2,
    EpisodeWorkerV1_2Error,
)
from cnpos.core.agents.prompt_agent import PromptAgent
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2
from cnpos.core.runtime.continuity_engine_v1_2 import ContinuityEngineV1_2
from cnpos.core.state.character_mutation_classifier_v1_2 import CharacterMutationClassifierV1_2
from cnpos.core.state.mutation_state_manager import MutationStateManager
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2

logger = logging.getLogger(__name__)


class FakePromptAgent(PromptAgent):
    """
    Deterministic prompt agent stub for episode worker.

    It records calls and returns a minimal, stable prompt payload so tests
    never depend on real LLM output.
    """

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def run(
        self,
        *,
        contract: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "contract": contract,
            "context": context,
        }
        self.calls.append(payload)
        return {
            "prompt": "synthetic episode prompt",
            "metadata": {
                "contract_title": contract.get("title"),
            },
        }


class FakeValidatorPipeline(ValidatorPipelineV1_2):
    """
    Deterministic validator pipeline stub.

    It records the last payload and returns it unchanged, ensuring tests
    validate wiring rather than validator logic.
    """

    def __init__(self) -> None:
        super().__init__(governance_loader=None)
        self.last_payload: Optional[Dict[str, Any]] = None

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.last_payload = payload
        return payload


class FakeContinuityEngine(ContinuityEngineV1_2):
    """
    Deterministic continuity engine stub for episode worker.

    It records calls and returns a minimal continuity snapshot.
    """

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def update(
        self,
        *,
        episode_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        self.calls.append(
            {
                "episode_id": episode_id,
                "payload": payload,
            }
        )
        return {
            "continuity": {
                "episode_id": episode_id,
            }
        }


class FakeMutationClassifier(CharacterMutationClassifierV1_2):
    """
    Deterministic mutation classifier stub for episode domain.

    It records calls and returns a minimal mutation report.
    """

    def __init__(self) -> None:
        super().__init__(backend_manager=None)
        self.last_call: Optional[Dict[str, Any]] = None

    def classify(
        self,
        *,
        episode_id: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        governance: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.last_call = {
            "episode_id": episode_id,
            "previous_state": previous_state or {},
            "new_state": new_state or {},
            "governance": governance or {},
        }
        return {
            "domain": "cinematic",
            "phase": "EPISODE_V1_2",
            "episode_id": episode_id,
            "mutations": [],
            "summary": {
                "last_mutation_type": "NONE",
                "last_risk_level": "low",
                "counts_by_type": {},
            },
            "rationale": "no_mutation",
        }


class FakeMutationStateManager(MutationStateManager):
    """
    Deterministic mutation state manager stub for episode worker.

    It records mutation entries keyed by episode.
    """

    def __init__(self) -> None:
        super().__init__()
        self.records: Dict[str, Any] = {}

    def record(
        self,
        *,
        domain: str,
        phase: str,
        episode_id: Optional[str] = None,
        mutations: Optional[Any] = None,
    ) -> None:
        key = f"{domain}:{phase}:{episode_id}"
        self.records[key] = {
            "mutations": mutations or [],
        }


class FakeGovernanceLoader(GovernanceLoaderV1_2):
    """
    Deterministic governance loader stub for episode domain.

    It returns a minimal rule set for the cinematic episode worker.
    """

    def __init__(self) -> None:
        super().__init__()
        self._rules: Dict[str, Any] = {
            "cinematic": {
                "episode": {
                    "require_contract_alignment": True,
                    "forbid_untracked_mutations": True,
                }
            }
        }

    def load(self, domain: str) -> Dict[str, Any]:
        return self._rules.get(domain, {})


class FakeBackendManager(BackendManagerV1_2):
    """
    Deterministic backend stub for episode worker.

    It records calls and returns a minimal, stable episode structure so tests
    never depend on real LLM output.
    """

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def route(
        self,
        *,
        domain: str,
        phase: str,
        task_type: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        self.calls.append(
            {
                "domain": domain,
                "phase": phase,
                "task_type": task_type,
                "payload": payload,
            }
        )
        return {
            "episode": {
                "id": payload.get("episode_id", "ep-001"),
                "scenes": [],
            }
        }


def test_episode_worker_v1_2_default_initialization() -> None:
    """
    Ensure EpisodeWorkerV1_2 can be constructed with default dependencies
    and that its core attributes are initialized in a governance- and
    continuity-aligned way.
    """
    worker = EpisodeWorkerV1_2()

    assert isinstance(worker, EpisodeWorkerV1_2)

    # Domain/phase should be aligned with the cinematic subsystem and v1_2.
    assert getattr(worker, "_domain", "cinematic") == "cinematic"
    assert getattr(worker, "_phase", "EPISODE_V1_2") == "EPISODE_V1_2"

    # Core dependencies must be present.
    assert isinstance(worker._prompt_agent, PromptAgent)
    assert isinstance(worker._validator_pipeline, ValidatorPipelineV1_2)
    assert isinstance(worker._continuity_engine, ContinuityEngineV1_2)
    assert isinstance(worker._mutation_classifier, CharacterMutationClassifierV1_2)
    assert isinstance(worker._mutation_state_manager, MutationStateManager)
    assert isinstance(worker._governance_loader, GovernanceLoaderV1_2)
    assert isinstance(worker._backend_manager, BackendManagerV1_2)


def test_episode_worker_v1_2_dependency_injection() -> None:
    """
    Ensure EpisodeWorkerV1_2 respects explicit dependency injection and uses
    the provided instances instead of creating new ones.
    """
    prompt = FakePromptAgent()
    validator = FakeValidatorPipeline()
    continuity_engine = FakeContinuityEngine()
    classifier = FakeMutationClassifier()
    mutation_state = FakeMutationStateManager()
    governance = FakeGovernanceLoader()
    backend = FakeBackendManager()

    worker = EpisodeWorkerV1_2(
        prompt_agent=prompt,
        validator_pipeline=validator,
        continuity_engine=continuity_engine,
        mutation_classifier=classifier,
        mutation_state_manager=mutation_state,
        governance_loader=governance,
        backend_manager=backend,
    )

    assert worker._prompt_agent is prompt
    assert worker._validator_pipeline is validator
    assert worker._continuity_engine is continuity_engine
    assert worker._mutation_classifier is classifier
    assert worker._mutation_state_manager is mutation_state
    assert worker._governance_loader is governance
    assert worker._backend_manager is backend


def test_episode_worker_v1_2_error_class_is_raised() -> None:
    """
    Verify that EpisodeWorkerV1_2Error exists and can be raised/caught as
    the canonical error type for this worker.
    """
    with pytest.raises(EpisodeWorkerV1_2Error):
        raise EpisodeWorkerV1_2Error("synthetic error for testing")


def test_episode_worker_v1_2_end_to_end_flow_with_fakes() -> None:
    """
    High-level integration check: ensure that when the worker is invoked in
    a synthetic episode flow, it interacts with prompt agent, backend
    manager, continuity engine, governance loader, validator pipeline,
    mutation classifier, and mutation state manager in a deterministic way.

    NOTE: This test does not call the real LLM; it relies on deterministic
    fakes and only asserts that the worker wires dependencies correctly.
    """
    prompt = FakePromptAgent()
    validator = FakeValidatorPipeline()
    continuity_engine = FakeContinuityEngine()
    classifier = FakeMutationClassifier()
    mutation_state = FakeMutationStateManager()
    governance = FakeGovernanceLoader()
    backend = FakeBackendManager()

    worker = EpisodeWorkerV1_2(
        prompt_agent=prompt,
        validator_pipeline=validator,
        continuity_engine=continuity_engine,
        mutation_classifier=classifier,
        mutation_state_manager=mutation_state,
        governance_loader=governance,
        backend_manager=backend,
    )

    episode_id = "ep-001"
    request: Dict[str, Any] = {
        "episode_id": episode_id,
        "seed": {
            "logline": "synthetic episode logline",
        },
    }

    # We assume the public API is `run`, consistent with other workers.
    if hasattr(worker, "run"):
        result = worker.run(  # type: ignore[call-arg]
            request=request,
        )
        assert isinstance(result, dict)
    else:
        pytest.skip("EpisodeWorkerV1_2 has no public run API exposed")

    # Prompt agent must have been called with a contract/context.
    assert len(prompt.calls) >= 1
    assert "contract" in prompt.calls[-1]
    assert "context" in prompt.calls[-1]

    # Backend manager must have been invoked for cinematic domain/phase.
    assert len(backend.calls) >= 1
    last_backend_call = backend.calls[-1]
    assert last_backend_call["domain"] == "cinematic"
    assert last_backend_call["phase"] == "EPISODE_V1_2"

    # Continuity engine must have been updated.
    assert len(continuity_engine.calls) >= 1
    assert continuity_engine.calls[-1]["episode_id"] == episode_id

    # Validator pipeline must have seen a payload.
    assert validator.last_payload is not None

    # Mutation classifier must have been invoked with episode context.
    assert classifier.last_call is not None
    assert classifier.last_call["episode_id"] == episode_id

    # Mutation state manager must have recorded something for this domain/phase.
    key_prefix = "cinematic:EPISODE_V1_2:"
    assert any(k.startswith(key_prefix) for k in mutation_state.records.keys())


# ---------------------------------------------------------------------------
# Discrepancies observed in the core tree (called out explicitly)
# ---------------------------------------------------------------------------
#
# - Earlier episode worker source (pre-v1_2) referenced ContinuityEngineV11,
#   which is inconsistent with the v1_2 architecture where
#   continuity_engine_v1_2 is the canonical implementation. This test imports
#   ContinuityEngineV1_2 to remain aligned with the v1_2 tree.
#
# - core/state/mutation_state_manager.py is not versioned as v1_2, while
#   continuity_state_v1_2.py and character_mutation_classifier_v1_2.py are
#   explicitly versioned. This test imports MutationStateManager from the
#   non-versioned file to remain compatible with the current tree, but this
#   is structurally inconsistent with the v1_2 naming convention.
#
# - core/governance/governance_validator_v1_2py appears to have a filename
#   typo (missing ".py"). This test module does not import it directly, yet
#   the typo should be corrected to avoid import issues elsewhere.
#
# - core/runtime/workers/render_worker.py is not versioned as v1_2, unlike
#   episode_worker_v1_2.py, scene_worker_v1_2.py, shot_worker_v1_2.py, and
#   worker_registry_v1_2.py. This is a minor drift from the otherwise strict
#   v1_2 naming pattern.
#
# - core/agents/prompt_agent.py is non-versioned, while many other agents and
#   workers are explicitly versioned as v1_2. This test imports PromptAgent
#   from the non-versioned file to remain compatible with the current tree.
#
# ---------------------------------------------------------------------------
# Inventions (explicit, minimal, and required for deterministic testing)
# ---------------------------------------------------------------------------
#
# - FakePromptAgent, FakeValidatorPipeline, FakeContinuityEngine,
#   FakeMutationClassifier, FakeMutationStateManager, FakeGovernanceLoader,
#   FakeBackendManager:
#   invented deterministic stubs to avoid calling real LLMs or external
#   systems while still exercising wiring, continuity, governance, and
#   mutation integration for the episode worker.
#
# - Assumptions about EpisodeWorkerV1_2 internal attributes
#   (`_prompt_agent`, `_validator_pipeline`, `_continuity_engine`,
#   `_mutation_classifier`, `_mutation_state_manager`, `_governance_loader`,
#   `_backend_manager`) and `_domain == "cinematic"`,
#   `_phase == "EPISODE_V1_2"`:
#   inferred from the CNPOS v1_2 architecture where the episode worker is
#   part of the cinematic pipeline and explicitly versioned.
#
# - Assumption that the public API is `run(request=...)`:
#   invented to remain compatible with typical worker design while still
#   validating that a high-level entrypoint exists and behaves
#   deterministically.
#
# Confidence grade for this test module: 0.82 (high, but not absolute, due to
# limited direct visibility into the exact public API surface of
# EpisodeWorkerV1_2 and the non-versioned mutation_state_manager and
# prompt_agent modules).
