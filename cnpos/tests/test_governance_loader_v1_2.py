# tests/test_governance_loader_v1_2.py

import json
import os
from typing import Dict, Any

import pytest

from cnpos.core.governance.governance_loader_v1_2 import (
    GovernanceLoaderV1_2,
    GovernanceLoaderV1_2Error,
)


@pytest.fixture(autouse=True)
def clear_governance_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure GOVERNANCE_ROOT_V1_2 does not leak across tests."""
    monkeypatch.delenv("GOVERNANCE_ROOT_V1_2", raising=False)


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def test_default_base_dir_ends_with_rules_v1_2() -> None:
    """
    GovernanceLoaderV1_2 without explicit base_dir or env var
    must resolve a default directory ending with 'rules_v1_2'.
    """
    loader = GovernanceLoaderV1_2()
    assert loader.base_dir.endswith("rules_v1_2")


def test_env_var_overrides_default_base_dir(tmp_path: pytest.TempPathFactory) -> None:
    """
    GOVERNANCE_ROOT_V1_2 must override the default base_dir resolution.
    """
    base_dir = tmp_path.mktemp("governance_root")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    loader = GovernanceLoaderV1_2()
    assert loader.base_dir == str(base_dir)


def test_load_code_rules_success(tmp_path: pytest.TempPathFactory) -> None:
    """
    load_code_rules must load code_mutation_rules_v1_2.json
    from the configured base_dir and return a dict.
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    payload = {"rules": ["FUNCTION_ADDED", "FUNCTION_REMOVED"]}
    _write_json(os.path.join(str(base_dir), "code_mutation_rules_v1_2.json"), payload)

    loader = GovernanceLoaderV1_2()
    result = loader.load_code_rules()
    assert result == payload


def test_load_character_rules_success(tmp_path: pytest.TempPathFactory) -> None:
    """
    load_character_rules must load character_mutation_rules_v1_2.json
    and return a dict.
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    payload = {"rules": ["CHARACTER_ADDED", "ARC_SHIFT"]}
    _write_json(
        os.path.join(str(base_dir), "character_mutation_rules_v1_2.json"),
        payload,
    )

    loader = GovernanceLoaderV1_2()
    result = loader.load_character_rules()
    assert result == payload


def test_load_continuity_rules_success(tmp_path: pytest.TempPathFactory) -> None:
    """
    load_continuity_rules must load continuity_rules_v1_2.json
    and return a dict.
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    payload = {"rules": ["EPISODE_CONTINUITY", "SCENE_CONTINUITY"]}
    _write_json(
        os.path.join(str(base_dir), "continuity_rules_v1_2.json"),
        payload,
    )

    loader = GovernanceLoaderV1_2()
    result = loader.load_continuity_rules()
    assert result == payload


def test_load_global_rules_success(tmp_path: pytest.TempPathFactory) -> None:
    """
    load_global_rules must load governance_global_v1_2.json
    and return a dict.
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    payload = {"rules": ["NO_LEGACY_VERSION", "STRICT_V1_2_NAMING"]}
    _write_json(
        os.path.join(str(base_dir), "governance_global_v1_2.json"),
        payload,
    )

    loader = GovernanceLoaderV1_2()
    result = loader.load_global_rules()
    assert result == payload


def test_load_json_missing_file_raises_error(tmp_path: pytest.TempPathFactory) -> None:
    """
    _load_json must raise GovernanceLoaderV1_2Error when the file does not exist.
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    loader = GovernanceLoaderV1_2()
    with pytest.raises(GovernanceLoaderV1_2Error):
        loader._load_json("non_existing_file_v1_2.json")  # type: ignore[attr-defined]


def test_load_json_non_dict_root_raises_error(tmp_path: pytest.TempPathFactory) -> None:
    """
    _load_json must reject JSON payloads whose root is not an object (dict).
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    path = os.path.join(str(base_dir), "code_mutation_rules_v1_2.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(["not", "a", "dict"], f)

    loader = GovernanceLoaderV1_2()
    with pytest.raises(GovernanceLoaderV1_2Error):
        loader.load_code_rules()


def test_load_all_aggregates_all_rule_sets(tmp_path: pytest.TempPathFactory) -> None:
    """
    load_all must return a dict with 'code', 'character', 'continuity', and 'global'
    keys, each containing the corresponding rule set.
    """
    base_dir = tmp_path.mktemp("rules")
    os.environ["GOVERNANCE_ROOT_V1_2"] = str(base_dir)

    code_payload = {"rules": ["FUNCTION_ADDED"]}
    character_payload = {"rules": ["CHARACTER_ADDED"]}
    continuity_payload = {"rules": ["EPISODE_CONTINUITY"]}
    global_payload = {"rules": ["STRICT_V1_2_NAMING"]}

    _write_json(
        os.path.join(str(base_dir), "code_mutation_rules_v1_2.json"),
        code_payload,
    )
    _write_json(
        os.path.join(str(base_dir), "character_mutation_rules_v1_2.json"),
        character_payload,
    )
    _write_json(
        os.path.join(str(base_dir), "continuity_rules_v1_2.json"),
        continuity_payload,
    )
    _write_json(
        os.path.join(str(base_dir), "governance_global_v1_2.json"),
        global_payload,
    )

    loader = GovernanceLoaderV1_2()
    result = loader.load_all()

    assert set(result.keys()) == {"code", "character", "continuity", "global"}
    assert result["code"] == code_payload
    assert result["character"] == character_payload
    assert result["continuity"] == continuity_payload
    assert result["global"] == global_payload


# ----------------------------------------------------------------------
# Discrepancies and inventions
# ----------------------------------------------------------------------
#
# Discrepancy:
# - core/validators/governance_validator_v12.py references GovernanceLoader
#   and methods load_spec_v12/load_policy_v12, which are not present in
#   GovernanceLoaderV1_2 as documented. This suggests a legacy/alternate
#   governance loader path that is inconsistent with the v1_2 architecture.
#
# Inventions (minimal, governance-aligned):
# - Tests assume that GovernanceLoaderV1_2 exposes .base_dir and _load_json
#   as shown in the documentation and that rule files are JSON objects.
# - Tests use tmp_path and GOVERNANCE_ROOT_V1_2 to avoid touching real
#   filesystem paths while still exercising the documented behavior.
#
# Confidence grade for this module: 0.86 (high, but not absolute due to
# partial, slightly noisy source snippets around governance_loader_v1_2).
