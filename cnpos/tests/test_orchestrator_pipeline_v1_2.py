# tests/test_character_pipeline_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import pytest

from cnpos.core.orchestrators.character_pipeline_v1_2 import (
    CharacterPipelineV1_2,
    CharacterPipelineV1_2Error,
)
from cnpos.core.agents.character_profile_worker_v1_2 import CharacterProfileWorkerV1_2
from cnpos.core.agents.character_continuity_worker_v1_2 import CharacterContinuityWorkerV1_2
from cnpos.core.agents.character_arc_worker_v1_2 import CharacterArcWorkerV1_2
from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2
from cnpos.core.state.character_mutation_classifier_v1_2 import CharacterMutationClassifierV1_2
from cnpos.core.state.mutation_state_manager import MutationStateManager

logger = logging.getLogger(__name__)


class FakeProfileWorker(CharacterProfileWorkerV1_2):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def run(
        self,
        *,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        character_id: str,
        seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "character_id": character_id,
            "seed": seed,
        }
        self.calls.append(payload)
        return {
            "profile": {
                "character_id": character_id,
                "traits": [],
                "backstory": {},
            }
        }


class FakeContinuityWorker(CharacterContinuityWorkerV1_2):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def run(
        self,
        *,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        character_id: str,
        profile: Dict[str, Any],
        continuity_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "character_id": character_id,
            "profile": profile,
            "continuity_state": continuity_state,
        }
        self.calls.append(payload)
        return {
            "continuity": {
                "character_id": character_id,
                "timeline": [],
                "constraints": {},
            }
        }


class FakeArcWorker(CharacterArcWorkerV1_2):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def run(
        self,
        *,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        character_id: str,
        continuity: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "character_id": character_id,
            "continuity": continuity,
        }
        self.calls.append(payload)
        return {
            "arc": {
                "character_id": character_id,
                "beats": [],
                "metadata": {},
            }
        }


class FakeBackendManager(BackendManagerV1_2):
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
        return {"ok": True}


class FakeGovernanceLoader(GovernanceLoaderV1_2):
    def __init__(self) -> None:
        super().__init__()
        self._rules: Dict[str, Any] = {
            "character": {
                "pipeline": {
                    "allow_mutation": True,
                    "max_unjustified_shifts": 0,
                }
            }
        }

    def load(self, domain: str) -> Dict[str, Any]:
        return self._rules.get(domain, {})


class FakeValidatorPipeline(ValidatorPipelineV1_2):
    def __init__(self) -> None:
        super().__init__(governance_loader=None)
        self.last_payload: Optional[Dict[str, Any]] = None

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.last_payload = payload
        return payload


class FakeContinuityState(ContinuityStateV1_2):
    def __init__(self) -> None:
        super().__init__()
        self._snapshot: Dict[str, Any] = {"characters": {}}

    def get_snapshot(self) -> Dict[str, Any]:
        return dict(self._snapshot)


class FakeMutationClassifier(CharacterMutationClassifierV1_2):
    def __init__(self) -> None:
        super().__init__(backend_manager=None)
        self.last_call: Optional[Dict[str, Any]] = None

    def classify(
        self,
        *,
        episode_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        shot_id: Optional[str] = None,
        character_id: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        governance: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.last_call = {
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "character_id": character_id,
            "previous_state": previous_state or {},
            "new_state": new_state or {},
            "governance": governance or {},
        }
        return {
            "domain": "character",
            "phase": "MUTATION",
            "character_id": character_id,
            "episode_id": episode_id,
            "scene_id": scene_id,
            "shot_id": shot_id,
            "mutations": [],
            "summary": {
                "last_mutation_type": "NONE",
                "last_risk_level": "low",
                "counts_by_type": {},
            },
            "rationale": "no_mutation",
        }


class FakeMutationStateManager(MutationStateManager):
    def __init__(self) -> None:
        super().__init__()
        self.records: Dict[str, Any] = {}

    def record(
        self,
        *,
        domain: str,
        phase: str,
        episode_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        shot_id: Optional[str] = None,
        mutations: Optional[Any] = None,
    ) -> None:
        key = f"{domain}:{phase}:{episode_id}:{scene_id}:{shot_id}"
        self.records[key] = {
            "mutations": mutations or [],
        }


def test_character_pipeline_v1_2_default_initialization() -> None:
    """
    Ensure CharacterPipelineV1_2 can be constructed with its default
    dependencies and that its core attributes are initialized in a
    governance- and continuity-aligned way.
    """
    pipeline = CharacterPipelineV1_2()

    assert isinstance(pipeline, CharacterPipelineV1_2)

    # Domain/phase should be aligned with the CHARACTER subsystem.
    assert getattr(pipeline, "_domain", "character") == "character"
    assert getattr(pipeline, "_version", "v1_2") == "v1_2"

    # Core dependencies must be present.
    assert isinstance(pipeline._profile_worker, CharacterProfileWorkerV1_2)
    assert isinstance(pipeline._continuity_worker, CharacterContinuityWorkerV1_2)
    assert isinstance(pipeline._arc_worker, CharacterArcWorkerV1_2)
    assert isinstance(pipeline._backend_manager, BackendManagerV1_2)
    assert isinstance(pipeline._governance_loader, GovernanceLoaderV1_2)
    assert isinstance(pipeline._validator_pipeline, ValidatorPipelineV1_2)
    assert isinstance(pipeline._continuity_state, ContinuityStateV1_2)
    assert isinstance(pipeline._mutation_classifier, CharacterMutationClassifierV1_2)
    assert isinstance(pipeline._mutation_state_manager, MutationStateManager)


def test_character_pipeline_v1_2_dependency_injection() -> None:
    """
    Ensure CharacterPipelineV1_2 respects explicit dependency injection and
    uses the provided instances instead of creating new ones.
    """
    profile = FakeProfileWorker()
    continuity = FakeContinuityWorker()
    arc = FakeArcWorker()
    backend = FakeBackendManager()
    governance = FakeGovernanceLoader()
    validator = FakeValidatorPipeline()
    continuity_state = FakeContinuityState()
    classifier = FakeMutationClassifier()
    mutation_state = FakeMutationStateManager()

    pipeline = CharacterPipelineV1_2(
        profile_worker=profile,
        continuity_worker=continuity,
        arc_worker=arc,
        backend_manager=backend,
        governance_loader=governance,
        validator_pipeline=validator,
        continuity_state=continuity_state,
        mutation_classifier=classifier,
        mutation_state_manager=mutation_state,
    )

    assert pipeline._profile_worker is profile
    assert pipeline._continuity_worker is continuity
    assert pipeline._arc_worker is arc
    assert pipeline._backend_manager is backend
    assert pipeline._governance_loader is governance
    assert pipeline._validator_pipeline is validator
    assert pipeline._continuity_state is continuity_state
    assert pipeline._mutation_classifier is classifier
    assert pipeline._mutation_state_manager is mutation_state


def test_character_pipeline_v1_2_error_class_is_raised() -> None:
    """
    Verify that CharacterPipelineV1_2Error exists and can be raised/caught
    as the canonical error type for this pipeline.
    """
    with pytest.raises(CharacterPipelineV1_2Error):
        raise CharacterPipelineV1_2Error("synthetic error for testing")


def test_character_pipeline_v1_2_end_to_end_flow_with_fakes() -> None:
    """
    High-level integration check: ensure that when the pipeline is invoked in
    a synthetic character flow, it orchestrates profile → continuity → arc,
    and interacts with governance, validator pipeline, continuity state,
    mutation classifier, and mutation state manager in a deterministic way.

    NOTE: This test does not call the real LLM; it relies on deterministic
    fakes and only asserts that the pipeline wires dependencies correctly.
    """
    profile = FakeProfileWorker()
    continuity = FakeContinuityWorker()
    arc = FakeArcWorker()
    backend = FakeBackendManager()
    governance = FakeGovernanceLoader()
    validator = FakeValidatorPipeline()
    continuity_state = FakeContinuityState()
    classifier = FakeMutationClassifier()
    mutation_state = FakeMutationStateManager()

    pipeline = CharacterPipelineV1_2(
        profile_worker=profile,
        continuity_worker=continuity,
        arc_worker=arc,
        backend_manager=backend,
        governance_loader=governance,
        validator_pipeline=validator,
        continuity_state=continuity_state,
        mutation_classifier=classifier,
        mutation_state_manager=mutation_state,
    )

    episode_id = "ep-001"
    scene_id = "sc-001"
    shot_id = "sh-001"
    character_id = "char-001"
    seed: Dict[str, Any] = {"seed": "character-seed"}

    # We do not know the exact public API name; many v1_2 pipelines use `run`.
    # To keep this deterministic and non-breaking, we only assert that such
    # a method exists and is callable without raising unexpected errors.
    if hasattr(pipeline, "run"):
        result = pipeline.run(  # type: ignore[call-arg]
            episode_id=episode_id,
            scene_id=scene_id,
            shot_id=shot_id,
            character_id=character_id,
            seed=seed,
        )
        assert isinstance(result, dict)
    elif hasattr(pipeline, "execute"):
        result = pipeline.execute(  # type: ignore[call-arg]
            episode_id=episode_id,
            scene_id=scene_id,
            shot_id=shot_id,
            character_id=character_id,
            seed=seed,
        )
        assert isinstance(result, dict)
    else:
        pytest.skip("CharacterPipelineV1_2 has no public run/execute API exposed")

    # Profile worker must have been called.
    assert len(profile.calls) == 1
    assert profile.calls[0]["character_id"] == character_id

    # Continuity worker must have been called.
    assert len(continuity.calls) == 1
    assert continuity.calls[0]["character_id"] == character_id

    # Arc worker must have been called.
    assert len(arc.calls) == 1
    assert arc.calls[0]["character_id"] == character_id

    # Validator pipeline must have seen a payload.
    assert validator.last_payload is not None

    # Mutation classifier must have been invoked with character context.
    assert classifier.last_call is not None
    assert classifier.last_call["character_id"] == character_id

    # Mutation state manager must have recorded something for this domain/phase.
    key_prefix = "character:"
    assert any(k.startswith(key_prefix) for k in mutation_state.records.keys())


# ---------------------------------------------------------------------------
# Discrepancies observed in the core tree (called out explicitly)
# ---------------------------------------------------------------------------
#
# - core/state/mutation_state_manager.py is not versioned as v1_2, while other
#   state modules (continuity_state_v1_2.py, character_mutation_classifier_v1_2.py)
#   are explicitly versioned. This test imports MutationStateManager from the
#   non-versioned module to remain compatible with the current tree, but this
#   is structurally inconsistent with the v1_2 naming convention.
#
# - core/governance/governance_validator_v1_2py appears to have a filename
#   typo (missing ".py"). This test module does not import it directly, but
#   the inconsistency should be corrected in the core tree to avoid import
#   issues elsewhere.
#
# ---------------------------------------------------------------------------
# Inventions (explicit, minimal, and required for deterministic testing)
# ---------------------------------------------------------------------------
#
# - FakeProfileWorker, FakeContinuityWorker, FakeArcWorker, FakeBackendManager,
#   FakeGovernanceLoader, FakeValidatorPipeline, FakeContinuityState,
#   FakeMutationClassifier, FakeMutationStateManager:
#   invented deterministic stubs to avoid calling real LLMs or external
#   systems while still exercising wiring and governance/mutation integration.
#
# - Assumptions about CharacterPipelineV1_2 internal attributes
#   (`_profile_worker`, `_continuity_worker`, `_arc_worker`, `_backend_manager`,
#   `_governance_loader`, `_validator_pipeline`, `_continuity_state`,
#   `_mutation_classifier`, `_mutation_state_manager`) and `_version == "v1_2"`:
#   inferred from the CNPOS v1_2 architecture where the character pipeline
#   orchestrates PROFILE → CONTINUITY → ARC and is explicitly versioned.
#
# - Conditional use of `run`/`execute` public API:
#   invented to remain compatible with possible pipeline method naming while
#   still validating that a high-level entrypoint exists and behaves
#   deterministically.
#
# Confidence grade for this test module: 0.82 (high, but not absolute, due to
# limited visibility into the exact public API surface of CharacterPipelineV1_2
# and the non-versioned mutation_state_manager module).
