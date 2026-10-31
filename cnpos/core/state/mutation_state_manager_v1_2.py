# cnpos/core/validators/governance_validator_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2

logger = logging.getLogger(__name__)


class GovernanceValidatorV1_2Error(Exception):
    """Raised when GovernanceValidatorV1_2 encounters an unrecoverable error."""


class GovernanceValidatorV1_2:
    """Deterministic governance validator wrapper for the v1_2 validator pipeline."""

    VERSION = "v1_2"

    def __init__(
        self,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()

    def validate(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        ruleset = self._governance_loader.load_rules(domain)
        violations: List[str] = []
        required_fields = ruleset.get("required_fields", [])
        for field in required_fields:
            if field not in payload:
                violations.append(f"Missing required field '{field}'")

        return {
            "domain": domain,
            "version": self.VERSION,
            "is_compliant": not violations,
            "violations": violations,
            "warnings": [],
            "payload": payload,
        }

    def validate_governance_config(self, domain: str) -> List[str]:
        try:
            ruleset = self._governance_loader.load_rules(domain)
        except Exception:
            return [f"Governance rules load failed for domain '{domain}'"]
        return [] if isinstance(ruleset, dict) else ["Invalid governance rules format"]


__all__ = ["GovernanceValidatorV1_2", "GovernanceValidatorV1_2Error"]
