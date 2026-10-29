# cnpos/core/validators/mutation_validator_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.governance.code_mutation_rules_v1_2 import CodeMutationRulesV1_2
from cnpos.core.state.character_mutation_classifier_v1_2 import (
    CharacterMutationClassifierV1_2,
    CharacterMutationClassifierV1_2Error,
)
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2

logger = logging.getLogger(__name__)


class MutationValidatorV1_2Error(Exception):
    """Raised when MutationValidatorV1_2 encounters an unrecoverable error."""
    pass


class MutationValidatorV1_2:
    """
    MutationValidatorV1_2

    Deterministic mutation validator for CNPOS v1_2.

    Responsibilities:
    - Classify character‑level mutations via CharacterMutationClassifierV1_2.
    - Apply code mutation rules via CodeMutationRulesV1_2.
    - Persist mutation state via MutationStateManagerV1_2.
    - Apply governance constraints via GovernanceLoaderV1_2.
    - Produce structured mutation reports for the validator pipeline.

    Domain‑aware:
    - "character" → character mutation classifier.
    - "code"      → code mutation rules.
    - Other domains can still be tracked via MutationStateManagerV1_2.
    """

    VERSION = "v1_2"

    def __init__(
        self,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        character_classifier: Optional[CharacterMutationClassifierV1_2] = None,
        code_rules: Optional[CodeMutationRulesV1_2] = None,
    ) -> None:
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._mutation_state_manager = mutation_state_manager or MutationStateManagerV1_2()
        self._character_classifier = character_classifier or CharacterMutationClassifierV1_2()
        self._code_rules = code_rules or CodeMutationRulesV1_2()

        logger.debug(
            "MutationValidatorV1_2 initialized governance_loader=%s mutation_state_manager=%s "
            "character_classifier=%s code_rules=%s",
            self._governance_loader,
            self._mutation_state_manager,
            self._character_classifier,
            self._code_rules,
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
        Validate a mutation for the given domain.

        Args:
            domain: Logical domain ("character", "code", etc.).
            payload: New payload to validate as mutation.
            context: Optional orchestration context.

        Returns:
            Dict[str, Any]: Mutation report:
                - 'domain'
                - 'version'
                - 'is_allowed'
                - 'mutation_id'
                - 'mutation_type'
                - 'violations'
                - 'details'
                - 'payload'
        """
        context = context or {}
        logger.info(
            "MutationValidatorV1_2.validate invoked domain=%s",
            domain,
        )

        try:
            if domain == "character":
                report = self._validate_character_mutation(payload=payload, context=context)
            elif domain == "code":
                report = self._validate_code_mutation(payload=payload, context=context)
            else:
                report = self._validate_generic_mutation(domain=domain, payload=payload, context=context)

            logger.debug(
                "MutationValidatorV1_2.validate completed domain=%s is_allowed=%s mutation_type=%s",
                domain,
                report.get("is_allowed"),
                report.get("mutation_type"),
            )
            return report

        except (MutationValidatorV1_2Error, CharacterMutationClassifierV1_2Error) as exc:
            logger.error(
                "MutationValidatorV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise MutationValidatorV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error(
                "MutationValidatorV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise MutationValidatorV1_2Error(
                f"Unexpected error in MutationValidatorV1_2.validate: {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Character mutations
    # -------------------------------------------------------------------------

    def _validate_character_mutation(
        self,
        *,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate character‑level mutation using CharacterMutationClassifierV1_2
        and governance rules.
        """
        character_id = str(payload.get("character_id", "unknown"))
        classification = self._character_classifier.classify(
            character_id=character_id,
            new_payload=payload,
            context=context,
        )

        is_mutation = bool(classification.get("is_mutation", False))
        mutation_type = classification.get("mutation_type", "none")
        details: List[str] = list(classification.get("details", []))

        # Governance rules for character mutations
        ruleset = self._governance_loader.load_ruleset(
            domain="character",
            context=context,
        )
        policy_result = self._governance_loader.evaluate_payload(
            domain="character",
            payload=payload,
            ruleset=ruleset,
            context=context,
        )

        violations: List[str] = list(policy_result.get("violations", []))
        details.extend(policy_result.get("warnings", []))

        is_allowed = is_mutation and len(violations) == 0

        mutation_id = self._mutation_state_manager.record_mutation(
            domain="character",
            mutation_type=mutation_type,
            payload=payload,
            active_state_snapshot=classification.get("previous_payload") or {},
            impact_summary={
                "is_mutation": is_mutation,
                "is_allowed": is_allowed,
                "violations": violations,
            },
            risk_level=policy_result.get("risk_level", "medium"),
        )

        report: Dict[str, Any] = {
            "domain": "character",
            "version": self.VERSION,
            "is_allowed": is_allowed,
            "mutation_id": mutation_id,
            "mutation_type": mutation_type,
            "violations": violations,
            "details": details,
            "payload": payload,
        }
        return report

    # -------------------------------------------------------------------------
    # Code mutations
    # -------------------------------------------------------------------------

    def _validate_code_mutation(
        self,
        *,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate code‑level mutation using CodeMutationRulesV1_2
        and governance rules.
        """
        rules_report = self._code_rules.evaluate_mutation(
            payload=payload,
            context=context,
        )

        mutation_type = rules_report.get("mutation_type", "code_change")
        violations: List[str] = list(rules_report.get("violations", []))
        details: List[str] = list(rules_report.get("details", []))

        # Governance overlay for code mutations
        ruleset = self._governance_loader.load_ruleset(
            domain="code",
            context=context,
        )
        policy_result = self._governance_loader.evaluate_payload(
            domain="code",
            payload=payload,
            ruleset=ruleset,
            context=context,
        )

        violations.extend(policy_result.get("violations", []))
        details.extend(policy_result.get("warnings", []))

        is_allowed = len(violations) == 0

        mutation_id = self._mutation_state_manager.record_mutation(
            domain="code",
            mutation_type=mutation_type,
            payload=payload,
            active_state_snapshot=rules_report.get("state_before") or {},
            impact_summary={
                "is_mutation": True,
                "is_allowed": is_allowed,
                "violations": violations,
            },
            risk_level=policy_result.get("risk_level", "high"),
        )

        report: Dict[str, Any] = {
            "domain": "code",
            "version": self.VERSION,
            "is_allowed": is_allowed,
            "mutation_id": mutation_id,
            "mutation_type": mutation_type,
            "violations": violations,
            "details": details,
            "payload": payload,
        }
        return report

    # -------------------------------------------------------------------------
    # Generic mutations (fallback)
    # -------------------------------------------------------------------------

    def _validate_generic_mutation(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generic mutation validation for domains that do not have
        dedicated classifiers/rules.
        """
        ruleset = self._governance_loader.load_ruleset(
            domain=domain,
            context=context,
        )
        policy_result = self._governance_loader.evaluate_payload(
            domain=domain,
            payload=payload,
            ruleset=ruleset,
            context=context,
        )

        violations: List[str] = list(policy_result.get("violations", []))
        details: List[str] = list(policy_result.get("warnings", []))
        is_allowed = len(violations) == 0

        mutation_id = self._mutation_state_manager.record_mutation(
            domain=domain,
            mutation_type="generic",
            payload=payload,
            active_state_snapshot={},
            impact_summary={
                "is_mutation": True,
                "is_allowed": is_allowed,
                "violations": violations,
            },
            risk_level=policy_result.get("risk_level", "low"),
        )

        report: Dict[str, Any] = {
            "domain": domain,
            "version": self.VERSION,
            "is_allowed": is_allowed,
            "mutation_id": mutation_id,
            "mutation_type": "generic",
            "violations": violations,
            "details": details,
            "payload": payload,
        }
        return report


__all__ = ["MutationValidatorV1_2", "MutationValidatorV1_2Error"]
