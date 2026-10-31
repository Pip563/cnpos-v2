# cnpos/core/governance/governance_validator_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.governance.governance_loader_v1_2 import (
    GovernanceLoaderV1_2,
    GovernanceLoaderV1_2Error,
)
from cnpos.core.governance.code_mutation_rules_v1_2 import CodeMut

logger = logging.getLogger(__name__)


class GovernanceValidatorV1_2Error(Exception):
    """Raised when GovernanceValidatorV1_2 encounters an unrecoverable error."""


class GovernanceValidatorV1_2:
    """Deterministic governance configuration and mutation validator for CNPOS v1_2."""

    VERSION = "v1_2"

    def __init__(self, loader: Optional[GovernanceLoaderV1_2] = None) -> None:
        self._loader = loader or GovernanceLoaderV1_2()
        logger.debug(
            "GovernanceValidatorV1_2 initialized with loader=%s", self._loader
        )

    def validate_governance_config(self, domain: str) -> List[str]:
        try:
            rules = self._loader.load_rules(domain)
        except GovernanceLoaderV1_2Error as exc:
            raise GovernanceValidatorV1_2Error(str(exc)) from exc

        violations: List[str] = []
        if rules.get("domain") != domain:
            violations.append(
                f"Governance rules domain mismatch: expected '{domain}', got '{rules.get('domain')}'."
            )

        required_sections = rules.get("required_sections", [])
        if not isinstance(required_sections, list):
            violations.append("Governance rules 'required_sections' must be a list.")
        for section in required_sections:
            if section not in rules:
                violations.append(
                    f"Governance rules missing required section '{section}' for domain '{domain}'."
                )
        return violations

    def validate_mutation_payload(self, payload: Dict[str, Any]) -> List[str]:
        logger.info(
            "GovernanceValidatorV1_2.validate_mutation_payload invoked for domain=%s",
            payload.get("domain"),
        )
        return CodeMut.validate_mutation(payload)

    def validate(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        violations = self.validate_governance_config(domain)
        risk_level = "low"
        if violations:
            risk_level = "high"
            is_compliant = False
        else:
            is_compliant = True
        return {
            "domain": domain,
            "version": self.VERSION,
            "is_compliant": is_compliant,
            "violations": violations,
            "warnings": [],
            "payload": payload,
            "risk_level": risk_level,
        }


__all__ = ["GovernanceValidatorV1_2", "GovernanceValidatorV1_2Error"]
