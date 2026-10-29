# cnpos/core/governance/governance_validator_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List

from cnpos.core.governance.governance_loader_v1_2 import (
    GovernanceLoaderV1_2,
    GovernanceLoaderV1_2Error,
)
from cnpos.core.governance.code_mutation_rules_v1_2 import (
    CodeMut,
    CodeMutationRuleV1_2,
)

logger = logging.getLogger(__name__)


class GovernanceValidatorV1_2Error(Exception):
    """
    Raised when GovernanceValidatorV1_2 encounters an unrecoverable error.
    """
    pass


class GovernanceValidatorV1_2:
    """
    GovernanceValidatorV1_2 (CNPOS v1_2)

    Deterministic governance configuration and mutation validator for CNPOS v1_2.

    Responsibilities:
    - Validate governance configuration for a given domain using GovernanceLoaderV1_2.
    - Validate mutation payloads against CodeMutationRulesV1_2 (CodeMut).
    - Provide a simple, JSON-compatible interface for higher-level validators
      and orchestrators.

    This module lives under cnpos.core.governance and is focused on
    governance-specific concerns; the cnpos.core.validators.governance_validator_v1_2
    module can wrap or delegate to this one when performing full pipeline validation.
    """

    VERSION = "v1_2"

    def __init__(self, loader: GovernanceLoaderV1_2 | None = None) -> None:
        self._loader = loader or GovernanceLoaderV1_2()
        logger.debug(
            "GovernanceValidatorV1_2 initialized with loader=%s", self._loader
        )

    # -------------------------------------------------------------------------
    # Governance configuration validation
    # -------------------------------------------------------------------------

    def validate_governance_config(self, domain: str) -> List[str]:
        """
        Validate governance configuration for a given domain.

        Args:
            domain: Logical domain name (e.g. 'episode', 'scene', 'shot',
                    'render', 'character', 'code').

        Returns:
            List of violation messages. Empty list means configuration is valid.

        Raises:
            GovernanceValidatorV1_2Error: if configuration cannot be loaded.
        """
        try:
            rules = self._loader.load_rules(domain)
        except GovernanceLoaderV1_2Error as exc:
            logger.error(
                "GovernanceValidatorV1_2: failed to load rules for domain '%s': %s",
                domain,
                exc,
                exc_info=True,
            )
            raise GovernanceValidatorV1_2Error(str(exc)) from exc

        violations: List[str] = []

        # Expected structure (aligned with GovernanceLoaderV1_2):
        # {
        #   "domain": "episode",
        #   "allowed_domains": [...],
        #   "required_sections": [...],
        #   ...
        # }
        if rules.get("domain") != domain:
            violations.append(
                f"Governance rules domain mismatch: expected '{domain}', "
                f"got '{rules.get('domain')}'."
            )

        required_sections = rules.get("required_sections", [])
        if not isinstance(required_sections, list):
            violations.append(
                "Governance rules 'required_sections' must be a list."
            )

        # Minimal structural check: ensure each required section is present.
        for section in required_sections:
            if section not in rules:
                violations.append(
                    f"Governance rules missing required section '{section}' "
                    f"for domain '{domain}'."
                )

        logger.debug(
            "GovernanceValidatorV1_2.validate_governance_config(%s) -> %d violation(s)",
            domain,
            len(violations),
        )
        return violations

    # -------------------------------------------------------------------------
    # Mutation payload validation (delegates to CodeMut)
    # -------------------------------------------------------------------------

    def validate_mutation_payload(self, payload: Dict[str, Any]) -> List[str]:
        """
        Validate a mutation payload against the v1_2 code mutation rules.

        This is a thin wrapper around CodeMut.validate_mutation, with
        additional logging and version tagging.

        Expected payload keys (see CodeMutationRulesV1_2.validate_mutation):
            - domain: str
            - changes: List[Dict[str, Any]]
            - tests: Optional[List[str]]
            - governance_tags: Optional[List[str]]

        Args:
            payload: Mutation description as a dict.

        Returns:
            List of violation messages. Empty list means the mutation
            satisfies all rules.
        """
        logger.info(
            "GovernanceValidatorV1_2.validate_mutation_payload invoked for domain=%s",
            payload.get("domain"),
        )

        violations = CodeMut.validate_mutation(payload)

        logger.debug(
            "GovernanceValidatorV1_2.validate_mutation_payload -> %d violation(s)",
            len(violations),
        )
        return violations


__all__ = ["GovernanceValidatorV1_2", "GovernanceValidatorV1_2Error"]
