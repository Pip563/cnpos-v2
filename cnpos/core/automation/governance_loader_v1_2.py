#cnpos/core/automation/governance_loader_v1_2.py

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GovernanceLoaderV1_2Error(Exception):
    """
    Raised when GovernanceLoaderV1_2 encounters an unrecoverable error.
    """


class GovernanceLoaderV1_2:
    """
    GovernanceLoaderV1_2

    Deterministic governance and contract loader for the CNPOS
    automation subsystem.

    Responsibilities:
    - Load automation governance configuration.
    - Load domain contracts.
    - Load automation templates.
    - Load automation rulesets.
    - Enforce strict v1_2 path and naming conventions.
    - Provide a stable interface for planner, writer,
      reviewer, test, and rewriter agents.

    Architecture alignment:
    - cnpos/core/automation/governance_spec_v1_2.json
    - cnpos/core/contracts/*_contract_v1_2.json
    - cnpos/core/automation/*
    """

    VERSION = "v1_2"

    def __init__(
        self,
        base_dir: Optional[Path] = None,
    ) -> None:

        self._base_dir = (
            base_dir
            if base_dir is not None
            else Path("cnpos") / "core" / "automation"
        )

        self._contracts_dir = (
            Path("cnpos") / "core" / "contracts"
        )

        logger.debug(
            "GovernanceLoaderV1_2 initialized "
            "base_dir=%s contracts_dir=%s",
            self._base_dir,
            self._contracts_dir,
        )

    # ------------------------------------------------------------------
    # Governance specification
    # ------------------------------------------------------------------

    def load_governance_spec(self) -> Dict[str, Any]:
        """
        Load the automation governance specification.

        Returns:
            Dict[str, Any]

        Raises:
            GovernanceLoaderV1_2Error
        """
        spec_path = (
            self._base_dir /
            "governance_spec_v1_2.json"
        )

        if not spec_path.is_file():
            raise GovernanceLoaderV1_2Error(
                (
                    "Governance specification not found: "
                    f"{spec_path}"
                )
            )

        try:
            with spec_path.open(
                "r",
                encoding="utf-8",
            ) as file_handle:
                spec = json.load(file_handle)

        except Exception as exc:
            raise GovernanceLoaderV1_2Error(
                (
                    "Failed to load governance "
                    f"specification: {exc}"
                )
            ) from exc

        version = spec.get("version")

        if version != self.VERSION:
            raise GovernanceLoaderV1_2Error(
                (
                    "Governance specification version "
                    f"mismatch: expected {self.VERSION}, "
                    f"received {version}"
                )
            )

        logger.debug(
            "Governance specification loaded "
            "keys=%s",
            list(spec.keys()),
        )

        return spec

    # ------------------------------------------------------------------
    # Contracts
    # ------------------------------------------------------------------

    def load_contract(
        self,
        domain: str,
    ) -> Dict[str, Any]:
        """
        Load a contract definition.

        Supported domains:
        - episode
        - scene
        - shot
        - render

        Returns:
            Dict[str, Any]

        Raises:
            GovernanceLoaderV1_2Error
        """
        contract_path = (
            self._contracts_dir /
            f"{domain}_contract_v1_2.json"
        )

        if not contract_path.is_file():
            raise GovernanceLoaderV1_2Error(
                (
                    "Contract not found for domain "
                    f"'{domain}': {contract_path}"
                )
            )

        try:
            with contract_path.open(
                "r",
                encoding="utf-8",
            ) as file_handle:
                contract = json.load(file_handle)

        except Exception as exc:
            raise GovernanceLoaderV1_2Error(
                (
                    "Failed to load contract for "
                    f"domain '{domain}': {exc}"
                )
            ) from exc

        logger.debug(
            "Contract loaded domain=%s keys=%s",
            domain,
            list(contract.keys()),
        )

        return contract

    def load_episode_contract(self) -> Dict[str, Any]:
        """
        Convenience contract loader.
        """
        return self.load_contract("episode")

    def load_scene_contract(self) -> Dict[str, Any]:
        """
        Convenience contract loader.
        """
        return self.load_contract("scene")

    def load_shot_contract(self) -> Dict[str, Any]:
        """
        Convenience contract loader.
        """
        return self.load_contract("shot")

    def load_render_contract(self) -> Dict[str, Any]:
        """
        Convenience contract loader.
        """
        return self.load_contract("render")

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------

    def load_template(
        self,
        module_type: str,
    ) -> str:
        """
        Load an automation template.

        Returns:
            str

        Raises:
            GovernanceLoaderV1_2Error
        """
        template_path = (
            self._base_dir /
            f"{module_type}_template_v1_2.txt"
        )

        if not template_path.is_file():
            raise GovernanceLoaderV1_2Error(
                (
                    "Template not found for "
                    f"module_type '{module_type}': "
                    f"{template_path}"
                )
            )

        try:
            content = template_path.read_text(
                encoding="utf-8",
            )

        except Exception as exc:
            raise GovernanceLoaderV1_2Error(
                (
                    "Failed to load template for "
                    f"module_type '{module_type}': "
                    f"{exc}"
                )
            ) from exc

        logger.debug(
            "Template loaded module_type=%s "
            "length=%d",
            module_type,
            len(content),
        )

        return content

    # ------------------------------------------------------------------
    # Rulesets
    # ------------------------------------------------------------------

    def load_ruleset(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """
        Load a ruleset definition.

        Returns:
            Dict[str, Any]

        Raises:
            GovernanceLoaderV1_2Error
        """
        ruleset_path = (
            self._base_dir /
            f"{name}_ruleset_v1_2.json"
        )

        if not ruleset_path.is_file():
            raise GovernanceLoaderV1_2Error(
                (
                    "Ruleset not found: "
                    f"{ruleset_path}"
                )
            )

        try:
            with ruleset_path.open(
                "r",
                encoding="utf-8",
            ) as file_handle:
                ruleset = json.load(file_handle)

        except Exception as exc:
            raise GovernanceLoaderV1_2Error(
                (
                    "Failed to load ruleset "
                    f"'{name}': {exc}"
                )
            ) from exc

        logger.debug(
            "Ruleset loaded name=%s keys=%s",
            name,
            list(ruleset.keys()),
        )

        return ruleset


__all__ = [
    "GovernanceLoaderV1_2",
    "GovernanceLoaderV1_2Error",
]
