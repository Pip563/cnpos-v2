# cnpos/core/validators/validator_pipeline_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.validators.continuity_validator_v1_2 import (
    ContinuityValidatorV1_2,
    ContinuityValidatorV1_2Error,
)
from cnpos.core.validators.governance_validator_v1_2 import (
    GovernanceValidatorV1_2,
    GovernanceValidatorV1_2Error,
)
from cnpos.core.validators.mutation_validator_v1_2 import (
    MutationValidatorV1_2,
    MutationValidatorV1_2Error,
)

logger = logging.getLogger(__name__)


class ValidatorPipelineV1_2Error(Exception):
    """Raised when ValidatorPipelineV1_2 encounters an unrecoverable error."""


class ValidatorPipelineV1_2:
    """Deterministic validator pipeline for CNPOS v1_2."""

    VERSION = "v1_2"

    def __init__(
        self,
        governance_validator: Optional[GovernanceValidatorV1_2] = None,
        continuity_validator: Optional[ContinuityValidatorV1_2] = None,
        mutation_validator: Optional[MutationValidatorV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._governance_validator = governance_validator or GovernanceValidatorV1_2(
            governance_loader=self._governance_loader
        )
        self._continuity_validator = continuity_validator or ContinuityValidatorV1_2(
            governance_loader=self._governance_loader
        )
        self._mutation_validator = mutation_validator or MutationValidatorV1_2(
            governance_loader=self._governance_loader
        )

        logger.debug(
            "ValidatorPipelineV1_2 initialized governance_validator=%s continuity_validator=%s mutation_validator=%s",
            self._governance_validator,
            self._continuity_validator,
            self._mutation_validator,
        )

    def validate(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run the full v1_2 validator pipeline and keep compatibility with both modern and test call patterns."""
        payload = kwargs.get("payload") or {}
        domain = kwargs.get("domain") or payload.get("domain") or "generic"
        context = kwargs.get("context") or {}
        phase = kwargs.get("phase")

        if args and isinstance(args[0], dict):
            payload = args[0]
            domain = kwargs.get("domain") or payload.get("domain") or domain
            context = kwargs.get("context") or {}

        governance_report = self._run_governance(domain, payload, context)
        contract_violations = self._run_contract_checks(payload, kwargs.get("contract_schema"))
        continuity_report = self._run_continuity(domain, payload, context)
        mutation_report = self._run_mutation(domain, payload, context)

        schema_ok = not contract_violations
        governance_ok = bool(governance_report.get("is_compliant", True))
        continuity_ok = bool(continuity_report.get("is_continuous", True))
        mutation_ok = bool(mutation_report.get("is_allowed", True))

        validated_payload: Dict[str, Any] = dict(payload)
        validated_payload.update(
            {
                "schema_ok": schema_ok,
                "governance_ok": governance_ok,
                "continuity_ok": continuity_ok,
                "mutation_ok": mutation_ok,
                "domain": domain,
                "version": self.VERSION,
            }
        )

        metadata = {
            "version": self.VERSION,
            "contract_violations": contract_violations,
            "governance_report": governance_report,
            "continuity_report": continuity_report,
            "mutation_report": mutation_report,
            "is_valid": schema_ok and governance_ok and continuity_ok and mutation_ok,
        }
        validated_payload["_validator_v1_2"] = metadata

        if phase is not None:
            return (metadata["is_valid"], validated_payload)

        return validated_payload

    def _run_governance(
        self,
        domain: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            if hasattr(self._governance_validator, "validate"):
                report = self._governance_validator.validate(
                    domain=domain,
                    payload=payload,
                    context=context,
                )
            else:
                violations = self._governance_validator.validate_governance_config(domain)
                report = {
                    "domain": domain,
                    "version": self.VERSION,
                    "is_compliant": not violations,
                    "violations": violations,
                    "warnings": [],
                    "payload": payload,
                }
            return report
        except Exception:
            return {
                "domain": domain,
                "version": self.VERSION,
                "is_compliant": False,
                "violations": ["governance validation error"],
                "warnings": [],
                "payload": payload,
            }

    def _run_contract_checks(
        self,
        payload: Dict[str, Any],
        contract_schema: Optional[Dict[str, Any]],
    ) -> List[str]:
        violations: List[str] = []
        if not contract_schema:
            return violations
        required_fields = contract_schema.get("required_fields") or contract_schema.get("required") or []
        for field in required_fields:
            if field not in payload:
                violations.append(f"Missing required contract field '{field}'")
        return violations

    def _run_continuity(
        self,
        domain: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            report = self._continuity_validator.validate(
                domain=domain,
                payload=payload,
                state_key=context.get("state_key"),
                context=context,
            )
            return report
        except Exception:
            return {
                "domain": domain,
                "version": self.VERSION,
                "state_key": context.get("state_key"),
                "is_continuous": False,
                "drift_level": "high",
                "violations": ["continuity validation error"],
                "previous_state": {},
                "current_payload": payload,
            }

    def _run_mutation(
        self,
        domain: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            report = self._mutation_validator.validate(
                domain=domain,
                payload=payload,
                context=context,
            )
            return report
        except Exception:
            return {
                "domain": domain,
                "version": self.VERSION,
                "is_allowed": False,
                "mutation_id": None,
                "mutation_type": "error",
                "violations": ["mutation validation error"],
                "details": ["mutation validation error"],
                "payload": payload,
            }


__all__ = ["ValidatorPipelineV1_2", "ValidatorPipelineV1_2Error"]
