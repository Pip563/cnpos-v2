# cnpos/core/validators/governance_validator_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2

logger = logging.getLogger(__name__)


class GovernanceValidatorV1_2Error(Exception):
    """Raised when GovernanceValidatorV1_2 encounters an unrecoverable error."""
    pass


class GovernanceValidatorV1_2:
    """
    GovernanceValidatorV1_2

    Deterministic governance validator for CNPOS v1_2.

    Responsibilities:
    - Load and apply governance rules for a given domain.
    - Validate payloads against governance constraints (safety, style, policy).
    - Produce structured governance reports for the validator pipeline.
    - Remain version‑locked to v1_2 (no legacy v11, v1_1, v1.2, v12).

    Domain‑agnostic: can be used for cinematic, character, and code domains.
    """

    VERSION = "v1_2"

    def __init__(
        self,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        logger.debug(
            "GovernanceValidatorV1_2 initialized governance_loader=%s",
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def validate(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate a payload against governance rules.

        Args:
            domain: Logical domain (episode, scene, shot, render, character, code).
            payload: Payload to validate.
            context: Optional orchestration context.

        Returns:
            Dict[str, Any]: Governance report:
                - 'domain'
                - 'version'
                - 'is_compliant'
                - 'violations'
                - 'warnings'
                - 'payload'
        """
        context = context or {}
        logger.info(
            "GovernanceValidatorV1_2.validate invoked domain=%s",
            domain,
        )

        try:
            ruleset = self._load_ruleset(domain=domain, context=context)
            report = self._apply_ruleset(
                domain=domain,
                payload=payload,
                ruleset=ruleset,
                context=context,
            )

            logger.debug(
                "GovernanceValidatorV1_2.validate completed domain=%s is_compliant=%s violations_count=%d",
                domain,
                report.get("is_compliant"),
                len(report.get("violations", [])),
            )
            return report

        except GovernanceValidatorV1_2Error as exc:
            logger.error(
                "GovernanceValidatorV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise
        except Exception as exc:
            logger.error(
                "GovernanceValidatorV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise GovernanceValidatorV1_2Error(
                f"Unexpected error in GovernanceValidatorV1_2.validate: {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_ruleset(
        self,
        *,
        domain: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Load governance ruleset for the given domain.

        Returns:
            Dict[str, Any]: Ruleset definition.
        """
        ruleset = self._governance_loader.load_ruleset(
            domain=domain,
            context=context,
        )
        logger.debug(
            "GovernanceValidatorV1_2._load_ruleset domain=%s ruleset_keys=%s",
            domain,
            list(ruleset.keys()),
        )
        return ruleset

    def _apply_ruleset(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        ruleset: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply governance ruleset to the payload.

        Returns:
            Dict[str, Any]: Governance report.
        """
        violations: List[str] = []
        warnings: List[str] = []

        # Simple structural checks (presence of required fields)
        required_fields = ruleset.get("required_fields", [])
        for field in required_fields:
            if field not in payload:
                violations.append(f"Missing required field '{field}'")

        # Policy checks delegated to governance_loader for consistency
        policy_result = self._governance_loader.evaluate_payload(
            domain=domain,
            payload=payload,
            ruleset=ruleset,
            context=context,
        )

        violations.extend(policy_result.get("violations", []))
        warnings.extend(policy_result.get("warnings", []))

        is_compliant = len(violations) == 0

        report: Dict[str, Any] = {
            "domain": domain,
            "version": self.VERSION,
            "is_compliant": is_compliant,
            "violations": violations,
            "warnings": warnings,
            "payload": payload,
        }

        logger.debug(
            "GovernanceValidatorV1_2._apply_ruleset domain=%s is_compliant=%s violations_count=%d warnings_count=%d",
            domain,
            is_compliant,
            len(violations),
            len(warnings),
        )
        return report


__all__ = ["GovernanceValidatorV1_2", "GovernanceValidatorV1_2Error"]
