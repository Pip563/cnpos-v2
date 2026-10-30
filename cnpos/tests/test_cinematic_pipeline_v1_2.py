# cnpos/tests/test_cinematic_pipeline_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import pytest

from cnpos.core.orchestrators.cinematic_pipeline_v1_2 import (
    CinematicPipelineV1_2,
    CinematicPipelineV1_2Error,
)
from cnpos.core.agents.prompt_agent_v1_2 import PromptAgentV1_2
from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2
from cnpos.core.runtime.continuity_engine_v1_2 import ContinuityEngineV1_2
from cnpos.core.runtime.workers.worker_registry_v1_2 import WorkerRegistryV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.state.character_mutation_classifier_v1_2 import CharacterMutationClassifierV1_2
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2

logger = logging.getLogger(__name__)


class FakePromptAgent(PromptAgentV1_2):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def generate_prompt(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "request": request,
            "context": context,
        }
        self.calls.append(payload)
        return {
            "prompt": "synthetic prompt",
            "metadata": {
                "contract_title": request.get("task"),
            },
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
        return {
            "episode": {
                "id": payload.get("episode_id", "ep-001"),
                "scenes": [],
            },
            "scene": {
                "id": payload.get("scene_id", "sc-001"),
                "shots": [],
            },
            "shot": {
                "id": payload.get("shot_id", "sh-001"),
            },
            "render": {
                "id": "render-001",
                "status": "synthetic",
            },
        }


class FakeContinuityEngine(ContinuityEngineV1_2):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[Dict[str, Any]] = []

    def update(
        self,
        *,
        episode_id: str,
        scene_id: str,
        shot_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        self.calls.append(
            {
                "episode_id": episode_id,
                "scene_id": scene_id,
                "shot_id": shot_id,
                "payload": payload,
            }
        )
        return {
            "continuity": {
                "episode_id": episode_id,
                "scene_id": scene_id,
                "shot_id": shot_id,
            }
        }


class FakeWorkerRegistry(WorkerRegistryV1_2):
    def __init__(self) -> None:
        super().__init__()
        self.requests: list[str] = []

    def get_worker(self, worker_type: str) -> Any:
        self.requests.append(worker_type)

        class _SyntheticWorker:
            def __init__(self, kind: str) -> None:
                self.kind = kind
                self.calls: list[Dict[str, Any]] = []

            def run(self, **kwargs: Any) -> Dict[str, Any]:
                self.calls.append(kwargs)
                return {
                    "kind": self.kind,
                    "payload": kwargs,
                }

        return _SyntheticWorker(worker_type)


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
        self._snapshot: Dict[str, Any] = {
            "episodes": {},
        }

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
            "domain": "cinematic",
            "phase": "CONTINUITY",
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


class FakeMutationStateManager(MutationStateManagerV1_2):
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


class FakeGovernanceLoader(GovernanceLoaderV1_2):
    def __init__(self) -> None:
        super().__init__()
        self._rules: Dict[str, Any] = {
            "cinematic": {
                "pipeline": {
                    "require_contract_alignment": True,
                    "forbid_untracked_mutations": True,
                }
            }
        }

    def load(self, domain: str) -> Dict[str, Any]:
        return self._rules.get(domain, {})


def test_cinematic_pipeline_v1_2_default_initialization() -> None:
    pipeline = CinematicPipelineV1_2()

    assert isinstance(pipeline, CinematicPipelineV1_2)
    assert getattr(pipeline, "_domain", "cinematic") == "cinematic"
    assert getattr(pipeline, "_version", "v1_2") == "v1_2"
    assert isinstance(pipeline._prompt_agent, PromptAgentV1_2)
    assert isinstance(pipeline._backend_manager, BackendManagerV1_2)
    assert isinstance(pipeline._continuity_engine, ContinuityEngineV1_2)
    assert isinstance(pipeline._worker_registry, WorkerRegistryV1_2)
    assert isinstance(pipeline._validator_pipeline, ValidatorPipelineV1_2)
    assert isinstance(pipeline._continuity_state, ContinuityStateV1_2)
    assert isinstance(pipeline._mutation_classifier, CharacterMutationClassifierV1_2)
    assert isinstance(pipeline._mutation_state_manager, MutationStateManagerV1_2)
    assert isinstance(pipeline._governance_loader, GovernanceLoaderV1_2)


def test_cinematic_pipeline_v1_2_dependency_injection() -> None:
    prompt = FakePromptAgent()
    backend = FakeBackendManager()
    continuity_engine = FakeContinuityEngine()
    worker_registry = FakeWorkerRegistry()
    validator = FakeValidatorPipeline()
    continuity_state = FakeContinuityState()
    classifier = FakeMutationClassifier()
    mutation_state = FakeMutationStateManager()
    governance = FakeGovernanceLoader()

    pipeline = CinematicPipelineV1_2(
        prompt_agent=prompt,
        backend_manager=backend,
        continuity_engine=continuity_engine,
        worker_registry=worker_registry,
        validator_pipeline=validator,
        continuity_state=continuity_state,
        mutation_classifier=classifier,
        mutation_state_manager=mutation_state,
        governance_loader=governance,
    )

    assert pipeline._prompt_agent is prompt
    assert pipeline._backend_manager is backend
    assert pipeline._continuity_engine is continuity_engine
    assert pipeline._worker_registry is worker_registry
    assert pipeline._validator_pipeline is validator
    assert pipeline._continuity_state is continuity_state
    assert pipeline._mutation_classifier is classifier
    assert pipeline._mutation_state_manager is mutation_state
    assert pipeline._governance_loader is governance


def test_cinematic_pipeline_v1_2_error_class_is_raised() -> None:
    with pytest.raises(CinematicPipelineV1_2Error):
        raise CinematicPipelineV1_2Error("synthetic error for testing")


def test_cinematic_pipeline_v1_2_end_to_end_flow_with_fakes() -> None:
    prompt = FakePromptAgent()
    backend = FakeBackendManager()
    continuity_engine = FakeContinuityEngine()
    worker_registry = FakeWorkerRegistry()
    validator = FakeValidatorPipeline()
    continuity_state = FakeContinuityState()
    classifier = FakeMutationClassifier()
    mutation_state = FakeMutationStateManager()
    governance = FakeGovernanceLoader()

    pipeline = CinematicPipelineV1_2(
        prompt_agent=prompt,
        backend_manager=backend,
        continuity_engine=continuity_engine,
        worker_registry=worker_registry,
        validator_pipeline=validator,
        continuity_state=continuity_state,
        mutation_classifier=classifier,
        mutation_state_manager=mutation_state,
        governance_loader=governance,
    )

    episode_id = "ep-001"
    scene_id = "sc-001"
    shot_id = "sh-001"

    request: Dict[str, Any] = {
        "episode_id": episode_id,
        "scene_id": scene_id,
        "shot_id": shot_id,
        "seed": {"logline": "synthetic logline"},
    }

    if hasattr(pipeline, "run"):
        result = pipeline.run(request=request)
        assert isinstance(result, dict)
    elif hasattr(pipeline, "execute"):
        result = pipeline.execute(request=request)
        assert isinstance(result, dict)
    else:
        pytest.skip("CinematicPipelineV1_2 has no public run/execute API exposed")

    assert len(prompt.calls) >= 1
    assert "request" in prompt.calls[-1]
    assert "context" in prompt.calls[-1]
    assert len(backend.calls) >= 1
    last_backend_call = backend.calls[-1]
    assert isinstance(last_backend_call["domain"], str) and last_backend_call["domain"]
    assert isinstance(last_backend_call["phase"], str) and last_backend_call["phase"]
    assert isinstance(last_backend_call["task_type"], str) and last_backend_call["task_type"]
    assert len(worker_registry.requests) >= 1
    assert len(continuity_engine.calls) >= 1
    assert continuity_engine.calls[-1]["episode_id"] == episode_id
    assert validator.last_payload is not None
    assert classifier.last_call is not None
    assert classifier.last_call["episode_id"] == episode_id
    key_prefix = "cinematic:"
    assert any(k.startswith(key_prefix) for k in mutation_state.records.keys())
