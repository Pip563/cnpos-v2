# tests/test_character_mutation_classifier_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pytest

from cnpos.core.state.character_mutation_classifier_v1_2 import (
    CharacterMutationClassifierV1_2,
    CharacterMutationClassifierV1_2Error,
)


class FakeBackendManagerSuccess:
    """
    Fake backend manager that returns a deterministic rationale string.
    """

    def __init__(self, output: str = "Deterministic mutation rationale."):
        self._output = output
        self.calls: List[Dict[str, Any]] = []

    def generate(
        self,
        *,
        prompt: str,
        domain: str,
        phase: str,
        task_type: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.calls.append(
            {
                "prompt": prompt,
                "domain": domain,
                "phase": phase,
                "task_type": task_type,
                "extra": extra or {},
            }
        )
        return {"output": self._output}


class FakeBackendManagerEmpty:
    """
    Fake backend manager that returns an empty output to trigger fallback rationale.
    """

    def generate(
        self,
        *,
        prompt: str,
        domain: str,
        phase: str,
        task_type: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {"output": ""}


class FakeBackendManagerError:
    """
    Fake backend manager that raises an exception to trigger error rationale.
    """

    def generate(
        self,
        *,
        prompt: str,
        domain: str,
        phase: str,
        task_type: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raise RuntimeError("backend failure")


class FaultyCharacterMutationClassifier(CharacterMutationClassifierV1_2):
    """
    Subclass that forces an internal error during classification to test error path.
    """

    def _detect_mutations(
        self,
        previous: Dict[str, Any],
        current: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        raise RuntimeError("forced detection error")


def _build_basic_state() -> Dict[str, Any]:
    """
    Helper to build a minimal deterministic character state payload.
    """
    return {
        "character_id": "char-001",
        "traits": {"brave": True},
        "relationships": {"friend": "char-002"},
        "arc": {"phase": "introduction"},
        "metadata": {"version": "v1_2"},
    }


def test_character_mutation_classifier_basic_structure() -> None:
    """
    Ensure classify() returns a payload with the expected top-level structure
    and deterministic domain/phase values.
    """
    backend = FakeBackendManagerSuccess()
    classifier = CharacterMutationClassifierV1_2(backend_manager=backend)

    previous_state = _build_basic_state()
    new_state = _build_basic_state()
    new_state["traits"] = {"brave": True, "curious": True}

    result = classifier.classify(
        episode_id="ep-001",
        scene_id="sc-001",
        shot_id="sh-001",
        character_id="char-001",
        previous_state=previous_state,
        new_state=new_state,
        governance={"rules": "test"},
    )

    assert isinstance(result, dict)
    assert result["domain"] == "character"
    assert result["phase"] == "MUTATION"
    assert result["character_id"] == "char-001"
    assert result["episode_id"] == "ep-001"
    assert result["scene_id"] == "sc-001"
    assert result["shot_id"] == "sh-001"

    assert "mutations" in result
    assert isinstance(result["mutations"], list)

    assert "summary" in result
    summary = result["summary"]
    assert isinstance(summary, dict)
    assert "last_mutation_type" in summary
    assert "last_risk_level" in summary
    assert "counts_by_type" in summary
    assert isinstance(summary["counts_by_type"], dict)

    assert "rationale" in result
    assert isinstance(result["rationale"], str)
    assert result["rationale"] != ""


def test_character_mutation_classifier_no_significant_change() -> None:
    """
    When previous_state and new_state are identical, classifier should emit
    a NO_SIGNIFICANT_CHANGE mutation with low risk.
    """
    backend = FakeBackendManagerSuccess()
    classifier = CharacterMutationClassifierV1_2(backend_manager=backend)

    previous_state = _build_basic_state()
    new_state = _build_basic_state()

    result = classifier.classify(
        episode_id=None,
        scene_id=None,
        shot_id=None,
        character_id="char-001",
        previous_state=previous_state,
        new_state=new_state,
        governance=None,
    )

    mutations = result.get("mutations", [])
    assert isinstance(mutations, list)
    assert len(mutations) >= 1

    # Expect the fallback mutation type when no differences are detected.
    last_mutation = mutations[-1]
    assert last_mutation.get("mutation_type") == "NO_SIGNIFICANT_CHANGE"
    assert last_mutation.get("risk_level") == "low"

    summary = result.get("summary", {})
    assert summary.get("last_mutation_type") == "NO_SIGNIFICANT_CHANGE"
    assert summary.get("last_risk_level") == "low"
    counts = summary.get("counts_by_type", {})
    assert isinstance(counts, dict)
    assert counts.get("NO_SIGNIFICANT_CHANGE", 0) >= 1


def test_character_mutation_classifier_backend_rationale_success() -> None:
    """
    Verify that a successful backend call is used as the rationale text.
    """
    backend = FakeBackendManagerSuccess(output="Backend rationale OK.")
    classifier = CharacterMutationClassifierV1_2(backend_manager=backend)

    previous_state = _build_basic_state()
    new_state = _build_basic_state()
    new_state["arc"] = {"phase": "development"}

    result = classifier.classify(
        episode_id="ep-002",
        scene_id="sc-010",
        shot_id="sh-005",
        character_id="char-001",
        previous_state=previous_state,
        new_state=new_state,
        governance={"risk": "medium"},
    )

    rationale = result.get("rationale", "")
    assert rationale == "Backend rationale OK."
    assert len(backend.calls) == 1
    call = backend.calls[0]
    assert call["domain"] == "mutation"
    assert call["phase"] == "CHARACTER"
    assert call["task_type"] == "CHARACTER_MUTATION_RATIONALE"
    assert isinstance(call["extra"], dict)
    assert "payload" in call["extra"]


def test_character_mutation_classifier_backend_rationale_empty_output() -> None:
    """
    When backend returns empty output, classifier should fall back to a
    deterministic 'unavailable' rationale string.
    """
    backend = FakeBackendManagerEmpty()
    classifier = CharacterMutationClassifierV1_2(backend_manager=backend)

    previous_state = _build_basic_state()
    new_state = _build_basic_state()
    new_state["traits"]["loyal"] = True

    result = classifier.classify(
        episode_id="ep-003",
        scene_id="sc-020",
        shot_id="sh-010",
        character_id="char-001",
        previous_state=previous_state,
        new_state=new_state,
        governance=None,
    )

    rationale = result.get("rationale", "")
    assert isinstance(rationale, str)
    assert rationale.startswith("Mutation rationale unavailable: backend returned empty output.")


def test_character_mutation_classifier_backend_rationale_error() -> None:
    """
    When backend raises an error, classifier should return a rationale string
    indicating backend failure, without raising.
    """
    backend = FakeBackendManagerError()
    classifier = CharacterMutationClassifierV1_2(backend_manager=backend)

    previous_state = _build_basic_state()
    new_state = _build_basic_state()
    new_state["relationships"]["enemy"] = "char-003"

    result = classifier.classify(
        episode_id="ep-004",
        scene_id="sc-030",
        shot_id="sh-015",
        character_id="char-001",
        previous_state=previous_state,
        new_state=new_state,
        governance={"strict": True},
    )

    rationale = result.get("rationale", "")
    assert isinstance(rationale, str)
    assert rationale.startswith("Mutation rationale unavailable due to backend error:")
    assert "backend failure" in rationale


def test_character_mutation_classifier_error_path_on_internal_failure() -> None:
    """
    Force an internal error in mutation detection and verify that classify()
    returns a safe error payload instead of raising.
    """
    backend = FakeBackendManagerSuccess()
    classifier = FaultyCharacterMutationClassifier(backend_manager=backend)

    previous_state = _build_basic_state()
    new_state = _build_basic_state()

    result = classifier.classify(
        episode_id="ep-005",
        scene_id="sc-040",
        shot_id="sh-020",
        character_id="char-001",
        previous_state=previous_state,
        new_state=new_state,
        governance=None,
    )

    assert result["domain"] == "character"
    assert result["phase"] == "MUTATION"
    assert result["character_id"] == "char-001"
    assert result["episode_id"] == "ep-005"
    assert result["scene_id"] == "sc-040"
    assert result["shot_id"] == "sh-020"

    assert result.get("mutations") == []
    summary = result.get("summary", {})
    assert summary.get("last_mutation_type") == "UNKNOWN"
    assert summary.get("last_risk_level") == "low"
    assert isinstance(summary.get("counts_by_type", {}), dict)

    assert "rationale" in result
    assert "error" in result
    assert isinstance(result["error"], str)
    assert result["error"] != ""


def test_character_mutation_classifier_raises_custom_error_type() -> None:
    """
    Ensure the custom error type CharacterMutationClassifierV1_2Error exists
    and can be raised/caught as part of governance-aware error handling.
    """
    with pytest.raises(CharacterMutationClassifierV1_2Error):
        raise CharacterMutationClassifierV1_2Error("synthetic classifier error for test")
