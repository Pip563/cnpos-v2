# tests/test_validator_pipeline_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

import pytest

from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def validator_pipeline() -> ValidatorPipelineV1_2:
    """
    Provide a shared ValidatorPipelineV1_2 instance for tests.

    The architecture overview states:

    - "core/validators/validator_pipeline_v1_2.py"
    - "Roles: ... Validator pipeline: orchestrates all validators"

    This fixture assumes a default constructor consistent with that role.
    """
    return ValidatorPipelineV1_2()


def test_validator_pipeline_interface_code_domain_v1_2(
    validator_pipeline: ValidatorPipelineV1_2,
) -> None:
    """
    Basic interface check for the 'code' domain.

    Expectations (aligned with v1_2 architecture):

    - validate(...) returns a (bool, dict) tuple
    - payload is not mutated into a non-dict type
    - no exceptions are raised for a minimal, governance-compliant payload
    """
    payload: Dict[str, Any] = {
        "version": "v1_2",
        "domain": "code",
        "name": "validator_pipeline_v1_2",
        "metadata": {"source": "test_validator_pipeline_v1_2"},
    }

    ok, result = validator_pipeline.validate(
        phase="CODE_TEST_V1_2",
        domain="code",
        payload=payload,
    )

    assert isinstance(ok, bool)
    assert isinstance(result, dict)


def test_validator_pipeline_interface_cinematic_domain_v1_2(
    validator_pipeline: ValidatorPipelineV1_2,
) -> None:
    """
    Basic interface check for the 'cinematic' domain.

    This mirrors usage in the cinematic pipeline v1_2, where the
    validator pipeline is invoked for episode/scene/shot/render phases.
    """
    payload: Dict[str, Any] = {
        "version": "v1_2",
        "domain": "cinematic",
        "phase": "EPISODE",
        "episode_id": "ep-001",
        "continuity_state": {},
    }

    ok, result = validator_pipeline.validate(
        phase="EPISODE_V1_2",
        domain="cinematic",
        payload=payload,
    )

    assert isinstance(ok, bool)
    assert isinstance(result, dict)


def test_validator_pipeline_interface_character_domain_v1_2(
    validator_pipeline: ValidatorPipelineV1_2,
) -> None:
    """
    Basic interface check for the 'character' domain.

    The character subsystem relies on continuity and mutation validators;
    this test ensures the pipeline can be invoked with that domain.
    """
    payload: Dict[str, Any] = {
        "version": "v1_2",
        "domain": "character",
        "character_id": "char-001",
        "profile": {"name": "Test Character"},
        "continuity_state": {},
        "mutation_state": {},
    }

    ok, result = validator_pipeline.validate(
        phase="CHARACTER_PROFILE_V1_2",
        domain="character",
        payload=payload,
    )

    assert isinstance(ok, bool)
    assert isinstance(result, dict)


def test_validator_pipeline_rejects_dotted_version_v1_2(
    validator_pipeline: ValidatorPipelineV1_2,
) -> None:
    """
    Governance rule: dotted versions (v1.2) must be rejected.

    The full architecture overview explicitly states:

    - "All modules follow strict naming: *_v1_2.py"
    - "No dotted versions (v1.2), no collapsed versions (v12), no legacy (v11, v1_1)"

    This test encodes that rule at the validator level.
    """
    payload: Dict[str, Any] = {
        "version": "v1.2",  # intentionally invalid
        "domain": "code",
        "name": "validator_pipeline_v1_2",
    }

    ok, result = validator_pipeline.validate(
        phase="CODE_PLAN_V1_2",
        domain="code",
        payload=payload,
    )

    assert ok is False
    assert isinstance(result, dict)


def test_validator_pipeline_accepts_strict_v1_2_version(
    validator_pipeline: ValidatorPipelineV1_2,
) -> None:
    """
    Governance rule: strict v1_2 naming must be accepted.

    This is the positive counterpart to the dotted-version rejection test.
    """
    payload: Dict[str, Any] = {
        "version": "v1_2",
        "domain": "code",
        "name": "validator_pipeline_v1_2",
    }

    ok, result = validator_pipeline.validate(
        phase="CODE_PLAN_V1_2",
        domain="code",
        payload=payload,
    )

    assert ok is True
    assert isinstance(result, dict)


def test_validator_pipeline_exposes_governance_continuity_mutation_flags_v1_2(
    validator_pipeline: ValidatorPipelineV1_2,
) -> None:
    """
    ValidatorPipelineV1_2 is documented as orchestrating:

    - governance_validator_v1_2
    - continuity_validator_v1_2
    - mutation_validator_v1_2

    Telemetry also exposes:

    - validator_results_schema_ok_v1_2
    - validator_results_governance_ok_v1_2
    - validator_results_continuity_ok_v1_2
    - validator_results_mutation_ok_v1_2

    This test asserts that the returned payload contains corresponding
    boolean flags, making telemetry and tests consistent.
    """
    payload: Dict[str, Any] = {
        "version": "v1_2",
        "domain": "code",
        "name": "validator_pipeline_v1_2",
        "schema": {"dummy": True},
    }

    ok, result = validator_pipeline.validate(
        phase="CODE_REVIEW_V1_2",
        domain="code",
        payload=payload,
    )

    assert isinstance(ok, bool)
    assert isinstance(result, dict)

    # These keys encode the governance/continuity/mutation status
    assert "schema_ok" in result
    assert "governance_ok" in result
    assert "continuity_ok" in result
    assert "mutation_ok" in result
