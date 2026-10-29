# tests/test_governance_validator_v1_2.py

import logging
from typing import Any, Dict, List, Optional

import pytest

from cnpos.core.validators.governance_validator_v1_2 import GovernanceValidator, GovernanceValidatorError


class FakeContinuityResult:
    def __init__(self, ok: bool, message: str = "") -> None:
        self.ok = ok
        self.message = message


class FakeGovernanceLoader:
    """
    Minimal fake GovernanceLoader for testing GovernanceValidator v1_2.

    Provides spec and policy structures compatible with the validator's expectations.
    """

    def __init__(self) -> None:
        self.spec_loaded = False
        self.policy_loaded = False

    def load_spec_v12(self) -> Dict[str, Any]:
        # NOTE: underlying implementation uses load_spec_v12; we mirror that name
        self.spec_loaded = True
        return {
            "continuity": {
                "rules": ["RULE_A", "RULE_B"],
            }
        }

    def load_policy_v12(self) -> Dict[str, Any]:
        # NOTE: underlying implementation uses load_policy_v12; we mirror that name
        self.policy_loaded = True
        return {
            "code": {
                "forbidden_terms": ["forbidden", "banned"],
                "max_length": 1000,
            },
            "character": {
                "forbidden_terms": ["unsafe"],
            },
        }


class FakeContinuityEngine:
    """
    Minimal fake ContinuityEngine for deterministic continuity enforcement tests.
    """

    def __init__(self) -> None:
        self.last_call: Optional[Dict[str, Any]] = None

    def evaluate(
        self,
        *,
        doc_type: str,
        payload: Dict[str, Any],
        active_state: Dict[str, Any],
        rules: Dict[str, Any],
    ) -> FakeContinuityResult:
        self.last_call = {
            "doc_type": doc_type,
            "payload": payload,
            "active_state": active_state,
            "rules": rules,
        }
        # Simple rule: if payload contains key "break_continuity", fail
        if payload.get("break_continuity"):
            return FakeContinuityResult(ok=False, message="Continuity broken")
        return FakeContinuityResult(ok=True, message="Continuity OK")


class FakeMutationStateManager:
    """
    Minimal fake MutationStateManager to verify mutation tracking calls.
    """

    def __init__(self) -> None:
        self.recorded: List[Dict[str, Any]] = []

    def record_mutation(self, doc_type: str, payload: Dict[str, Any]) -> None:
        self.recorded.append({"doc_type": doc_type, "payload": payload})


def _build_validator_with_fakes() -> GovernanceValidator:
    """
    Helper to construct GovernanceValidator with deterministic fake dependencies.
    """
    loader = FakeGovernanceLoader()
    continuity_engine = FakeContinuityEngine()
    mutation_state_manager = FakeMutationStateManager()
    validator = GovernanceValidator(
        governance_loader=loader,
        continuity_engine=continuity_engine,
        mutation_state_manager=mutation_state_manager,
    )
    # Sanity: spec/policy must be loaded on init
    assert hasattr(validator, "_spec")
    assert hasattr(validator, "_policy")
    assert loader.spec_loaded
    assert loader.policy_loaded
    return validator


def test_governance_validator_init_uses_provided_dependencies() -> None:
    """
    GovernanceValidator must accept explicit governance_loader, continuity_engine,
    and mutation_state_manager and store them for deterministic enforcement.
    """
    loader = FakeGovernanceLoader()
    continuity_engine = FakeContinuityEngine()
    mutation_state_manager = FakeMutationStateManager()

    validator = GovernanceValidator(
        governance_loader=loader,
        continuity_engine=continuity_engine,
        mutation_state_manager=mutation_state_manager,
    )

    # Internal attributes should reference the provided instances
    assert validator._governance_loader is loader
    assert validator._continuity_engine is continuity_engine
    assert validator._mutation_state_manager is mutation_state_manager

    # Spec and policy must be preloaded for v1_2 domains
    assert isinstance(validator._spec, dict)
    assert isinstance(validator._policy, dict)


def test_governance_validator_validate_success_path() -> None:
    """
    validate() should return a success payload when continuity and policy checks pass.
    """
    validator = _build_validator_with_fakes()

    payload = {
        "content": "This is safe content with no forbidden terms.",
        "meta": "ok",
    }
    context = {
        "active_state": {"episode": 1, "scene": 1},
    }

    result = validator.validate(doc_type="code", payload=payload, context=context)

    assert isinstance(result, dict)
    assert result["ok"] is True
    assert result["message"] == "Governance OK"
    assert isinstance(result["errors"], list)
    assert result["errors"] == []
    # normalized payload should be the original payload (no mutation in this fake)
    assert result["normalized"] == payload


def test_governance_validator_continuity_violation_is_reported() -> None:
    """
    validate() must surface continuity violations from ContinuityEngine as errors.
    """
    validator = _build_validator_with_fakes()

    payload = {
        "content": "Safe content",
        "break_continuity": True,  # triggers FakeContinuityEngine failure
    }
    context = {
        "active_state": {"episode": 2, "scene": 3},
    }

    result = validator.validate(doc_type="code", payload=payload, context=context)

    assert result["ok"] is False
    assert any(
        "Continuity violation" in err for err in result["errors"]
    ), "Expected continuity violation error in errors list"


def test_governance_validator_policy_forbidden_terms_are_enforced() -> None:
    """
    validate() must enforce governance policy forbidden_terms for the given doc_type.
    """
    validator = _build_validator_with_fakes()

    payload = {
        "content": "This contains a forbidden term.",
        "other": "banned content here",
    }
    context = {
        "active_state": {},
    }

    result = validator.validate(doc_type="code", payload=payload, context=context)

    assert result["ok"] is False
    # At least one error mentioning forbidden term should be present
    assert any(
        "forbidden" in err.lower() or "banned" in err.lower()
        for err in result["errors"]
    )


def test_governance_validator_mutation_tracking_is_called() -> None:
    """
    validate() must always record mutations via MutationStateManager, regardless of ok/failed.
    """
    loader = FakeGovernanceLoader()
    continuity_engine = FakeContinuityEngine()
    mutation_state_manager = FakeMutationStateManager()

    validator = GovernanceValidator(
        governance_loader=loader,
        continuity_engine=continuity_engine,
        mutation_state_manager=mutation_state_manager,
    )

    payload_ok = {"content": "safe"}
    payload_bad = {"content": "forbidden", "break_continuity": True}

    validator.validate(doc_type="code", payload=payload_ok, context={})
    validator.validate(doc_type="code", payload=payload_bad, context={})

    # Two calls must have been recorded
    assert len(mutation_state_manager.recorded) == 2
    assert mutation_state_manager.recorded[0]["payload"] == payload_ok
    assert mutation_state_manager.recorded[1]["payload"] == payload_bad


def test_governance_validator_raises_custom_error_on_internal_failure(monkeypatch: Any) -> None:
    """
    GovernanceValidatorError should be raised when internal validation logic fails unexpectedly.
    We simulate this by forcing _apply_policy to raise.
    """
    validator = _build_validator_with_fakes()

    def _broken_apply_policy(doc_type: str, payload: Dict[str, Any]) -> List[str]:
        raise RuntimeError("internal policy failure")

    monkeypatch.setattr(validator, "_apply_policy", _broken_apply_policy)

    with pytest.raises(GovernanceValidatorError):
        # We expect the validator to wrap internal failures in GovernanceValidatorError
        validator.validate(doc_type="code", payload={"content": "x"}, context={})


# ----------------------------------------------------------------------
# Discrepancies and inventions (governance alignment notes)
# ----------------------------------------------------------------------
#
# 1. The underlying implementation snippet uses module name `governance_validator_v12.py`
#    and methods `load_spec_v12` / `load_policy_v12`, while the architecture tree and
#    CNPOS v1_2 overview specify `governance_validator_v1_2.py` and strict v1_2 naming.
#    This test module assumes the canonical module path
#    `core.validators.governance_validator_v1_2` but mirrors the internal method names
#    (`load_spec_v12`, `load_policy_v12`) to stay aligned with the provided source.
#
# 2. The real ContinuityEngine and MutationStateManager implementations are not fully
#    documented in the attached snippets. To avoid coupling tests to unknown runtime
#    behavior, deterministic fake implementations (FakeContinuityEngine,
#    FakeMutationStateManager, FakeGovernanceLoader) are introduced. These fakes are
#    explicitly inventions, designed to:
#    - exercise GovernanceValidator's public API (`validate`)
#    - verify continuity error propagation
#    - verify policy enforcement and mutation tracking
#    without relying on LM Studio / Ollama or full continuity/mutation engines.
#
# 3. The user requested filename `tests/test_governance_validator_v1_2..py` with a
#    double dot. This module uses the corrected, governance-aligned name
#    `tests/test_governance_validator_v1_2.py` to preserve deterministic import
#    behavior and match the v1_2 test tree conventions.
#
# Confidence grade for this module: HIGH.
# The tests are structurally aligned with the described GovernanceValidator
# responsibilities and the CNPOS v1_2 architecture, while keeping dependencies
# isolated and deterministic.
