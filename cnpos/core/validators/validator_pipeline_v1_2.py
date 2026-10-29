# cnpos/core/validators/validator_pipeline_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.validators.governance_validator_v1_2 import (
    GovernanceValidatorV1_2,
    GovernanceValidatorV1_2Error,
)
from cnpos.core.validators.continuity_validator_v1_2 import (
    ContinuityValidatorV1_2,
    ContinuityValidatorV1_2Error,
)
from cnpos.core.validators.mutation_validator_v1_2 import (
    MutationValidatorV1_2,
    MutationValidatorV1_2Error,
)

logger = logging.getLogger(__name__)


class ValidatorPipelineV1_2Error(Exception):
    """Raised when ValidatorPipelineV1_2 encounters an unrecoverable error."""
    pass


class ValidatorPipelineV1_2:
    """
    ValidatorPipelineV1_2

    Deterministic validator pipeline for CNPOS v1_2.

    Responsibilities:
    - Apply contract/schema checks.
    - Apply governance validation.
    - Apply continuity validation.
    - Apply mutation validation.
    - Return a validated payload enriched with validator metadata.

    This pipeline is version‑locked to v1_2 and only orchestrates v1_2 validators.
    """

    VERSION = "v1_2"

    def __init__(
        self,
        governance_validator: Optional[GovernanceValidatorV1_2] = None,
        continuity_validator: Optional[ContinuityValidatorV1_2] = None,
        mutation_validator: Optional[MutationValidatorV1_2] = None,
    ) -> None:
        self._governance_validator = governance_validator or GovernanceValidatorV1_2()
        self._continuity_validator = continuity_validator or ContinuityValidatorV1_2()
        self._mutation_validator = mutation_validator or MutationValidatorV1_2()

        logger.debug(
            "ValidatorPipelineV1_2 initialized governance_validator=%s continuity_validator=%s "
            "mutation_validator=%s",
            self._governance_validator,
            self._continuity_validator,
            self._mutation_validator,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def validate(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        contract_schema: Optional[Dict[str, Any]] = None,
        governance_loader: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the full v1_2 validator pipeline.

        Args:
            domain: Logical domain (episode, scene, shot, render, character, code).
            payload: Payload to validate.
            contract_schema: Optional contract/schema definition (JSON‑derived dict).
            governance_loader: Optional governance loader instance (for external wiring).
            context: Optional orchestration context.

        Returns:
            Dict[str, Any]: Validated payload, enriched with `_validator_v1_2` metadata.

        Raises:
            ValidatorPipelineV1_2Error if any critical validation fails.
        """
        context = context or {}
        logger.info(
            "ValidatorPipelineV1_2.validate invoked domain=%s",
            domain,
        )

        # Optionally override governance loader inside governance validator
        if governance_loader is not None:
            # This relies on GovernanceValidatorV1_2 being constructed with a loader;
            # re‑create it to keep behavior deterministic.
            self._governance_validator = GovernanceValidatorV1_2(
                governance_loader=governance_loader
            )

        contract_violations = self._run_contract_checks(
            payload=payload,
            contract_schema=contract_schema,
        )

        try:
            governance_report = self._governance_validator.validate(
                domain=domain,
                payload=payload,
                context=context,
            )
            continuity_report = self._continuity_validator.validate(
                domain=domain,
                payload=payload,
                state_key=context.get("state_key"),
                context=context,
            )
            mutation_report = self._mutation_validator.validate(
                domain=domain,
                payload=payload,
                context=context,
            )
        except (
            GovernanceValidatorV1_2Error,
            ContinuityValidatorV1_2Error,
            MutationValidatorV1_2Error,
        ) as exc:
            logger.error(
                "ValidatorPipelineV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise ValidatorPipelineV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error(
                "ValidatorPipelineV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise ValidatorPipelineV1_2Error(
                f"Unexpected error in ValidatorPipelineV1_2.validate: {exc}"
            ) from exc

        critical_failures: List[str] = []

        if contract_violations:
            critical_failures.append("contract")
        if not governance_report.get("is_compliant", True):
            critical_failures.append("governance")
        if not continuity_report.get("is_continuous", True):
            critical_failures.append("continuity")
        if not mutation_report.get("is_allowed", True):
            critical_failures.append("mutation")

        if critical_failures:
            logger.error(
                "ValidatorPipelineV1_2 critical failures=%s",
                critical_failures,
            )
            raise ValidatorPipelineV1_2Error(
                f"Validation failed in stages: {', '.join(critical_failures)}"
            )

        validated_payload = dict(payload)
        validated_payload["_validator_v1_2"] = {
            "version": self.VERSION,
            "contract_violations": contract_violations,
            "governance_report": governance_report,
            "continuity_report": continuity_report,
            "mutation_report": mutation_report,
        }

        logger.debug(
            "ValidatorPipelineV1_2.validate completed domain=%s contract_violations=%d",
            domain,
            len(contract_violations),
        )
        return validated_payload

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _run_contract_checks(
        self,
        *,
        payload: Dict[str, Any],
        contract_schema: Optional[Dict[str, Any]],
    ) -> List[str]:
        """
        Apply simple contract/schema checks based on the provided contract_schema.

        Returns:
            List[str]: Contract violation messages.
        """
        violations: List[str] = []
        if not contract_schema:
            return violations

        required_fields = contract_schema.get("required_fields") or contract_schema.get("required") or []
        for field in required_fields:
            if field not in payload:
                violations.append(f"Missing required contract field '{field}'")

        return violations


__all__ = ["ValidatorPipelineV1_2", "ValidatorPipelineV1_2Error"]
