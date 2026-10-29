# cnpos/core/governance/governance_loader_v1_2.py

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GovernanceLoaderV1_2Error(Exception):
    """
    Raised when GovernanceLoaderV1_2 cannot load or interpret governance rules.
    """
    pass


class GovernanceLoaderV1_2:
    """
    GovernanceLoaderV1_2 (CNPOS v1_2)

    Deterministic governance rules loader for CNPOS v1_2.

    Responsibilities:
    - Load governance rule sets for specific domains (episode, scene, shot, render, character, code).
    - Provide a stable, JSON-compatible dict interface to validators and workers.
    - Enforce strict v1_2 naming and avoid legacy/dotted versions.
    - Centralize access to governance_global_v1_2.json and domain-specific sections.

    This loader is intentionally minimal and side-effect free so that:
    - GovernanceValidatorV1_2, ContinuityValidatorV1_2, MutationValidatorV1_2
      can query rules deterministically.
    - Workers (episode, scene, shot, render) can attach governance rules
      for their domain without knowing file layout.
    """

    def __init__(self, governance_root: Optional[str] = None) -> None:
        """
        Initialize the governance loader.

        Args:
            governance_root: Optional explicit path to the governance directory.
                             If not provided, it is resolved relative to the core
                             package root (cnpos/core/governance).
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._governance_root = governance_root or self._default_governance_root()
        self._global_governance_path = os.path.join(
            self._governance_root, "governance_global_v1_2.json"
        )
        self._cache: Dict[str, Dict[str, Any]] = {}

        self._logger.debug(
            "GovernanceLoaderV1_2 initialized with governance_root=%s, "
            "global_governance_path=%s",
            self._governance_root,
            self._global_governance_path,
        )

    def _default_governance_root(self) -> str:
        """
        Compute the default path to the governance directory relative to the core package.

        Returns:
            str: Absolute path to cnpos/core/governance.
        """
        # cnpos/core/governance/governance_loader_v1_2.py
        core_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(core_root, "governance")

    def _load_global_governance(self) -> Dict[str, Any]:
        """
        Load the global governance configuration (governance_global_v1_2.json).

        Returns:
            Dict[str, Any]: Parsed global governance configuration.

        Raises:
            GovernanceLoaderV1_2Error: If the file cannot be loaded or parsed.
        """
        if "_global" in self._cache:
            return self._cache["_global"]

        self._logger.info(
            "GovernanceLoaderV1_2 loading global governance from %s",
            self._global_governance_path,
        )

        if not os.path.exists(self._global_governance_path):
            # Explicit error: governance_global_v1_2.json is expected by v1_2 architecture.
            raise GovernanceLoaderV1_2Error(
                f"Global governance file not found: {self._global_governance_path}"
            )

        try:
            with open(self._global_governance_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            self._logger.error(
                "Failed to load global governance file %s: %s",
                self._global_governance_path,
                exc,
                exc_info=True,
            )
            raise GovernanceLoaderV1_2Error(
                f"Failed to load global governance file: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise GovernanceLoaderV1_2Error(
                "Global governance configuration must be a JSON object (dict)."
            )

        self._cache["_global"] = data
        self._logger.debug(
            "GovernanceLoaderV1_2 loaded global governance: keys=%s",
            list(data.keys()),
        )
        return data

    def load_rules(self, domain: str) -> Dict[str, Any]:
        """
        Load governance rules for a specific logical domain.

        Domains are aligned with the v1_2 architecture:
        - "episode", "scene", "shot", "render", "character", "code", "governance", etc.

        Args:
            domain: Logical domain name.

        Returns:
            Dict[str, Any]: Governance rules for the given domain.

        Raises:
            GovernanceLoaderV1_2Error: If rules cannot be resolved.
        """
        if domain in self._cache:
            return self._cache[domain]

        global_cfg = self._load_global_governance()

        # Expected structure (invention, but aligned with architecture overview):
        # {
        #   "allowed_domains": [...],
        #   "required_sections": [...],
        #   "domains": {
        #       "episode": {...},
        #       "scene": {...},
        #       "shot": {...},
        #       "render": {...},
        #       "character": {...},
        #       "code": {...},
        #       "governance": {...}
        #   }
        # }
        domains_cfg = global_cfg.get("domains", {})
        domain_rules = domains_cfg.get(domain)

        if domain_rules is None:
            # Fallback: build a minimal rule set using global defaults.
            self._logger.warning(
                "GovernanceLoaderV1_2: domain '%s' not found in global governance; "
                "falling back to minimal rules.",
                domain,
            )
            allowed_domains = global_cfg.get("allowed_domains", [])
            required_sections = global_cfg.get("required_sections", [])
            domain_rules = {
                "domain": domain,
                "allowed_domains": allowed_domains,
                "required_sections": required_sections,
            }

        if not isinstance(domain_rules, dict):
            raise GovernanceLoaderV1_2Error(
                f"Governance rules for domain '{domain}' must be a dict."
            )

        self._cache[domain] = domain_rules
        self._logger.debug(
            "GovernanceLoaderV1_2.load_rules(%s) -> keys=%s",
            domain,
            list(domain_rules.keys()),
        )
        return domain_rules

    def reload(self) -> None:
        """
        Clear the internal cache so that subsequent calls reload governance files.

        This is useful in long-running processes when governance_global_v1_2.json
        may be updated externally.
        """
        self._logger.info("GovernanceLoaderV1_2 cache cleared via reload()")
        self._cache.clear()
