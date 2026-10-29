# cnpos/core/governance/code_mutation_rules_v1_2.py
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CodeMutationRuleV1_2:
    """
    Single deterministic mutation rule for CNPOS v1_2.

    Each rule describes constraints that must be satisfied by a mutation
    payload before it can be accepted by the governance and validator
    pipeline.
    """

    rule_id: str
    description: str
    allowed_domains: List[str] = field(default_factory=list)
    max_changes: Optional[int] = None
    require_tests: bool = False
    require_governance_tag: bool = False


class CodeMutationRulesV1_2:
    """
    Central registry of code mutation rules for CNPOS v1_2.

    This registry is intentionally static and deterministic: rules are
    defined in code and not mutated at runtime, so that governance
    decisions are reproducible across runs and environments.
    """

    def __init__(self) -> None:
        self._rules: List[CodeMutationRuleV1_2] = self._build_default_rules()
        logger.debug("Initialized CodeMutationRulesV1_2 with %d rules", len(self._rules))

    @staticmethod
    def _build_default_rules() -> List[CodeMutationRuleV1_2]:
        """
        Build the default v1_2 rule set.

        The rules are designed to align with the validator pipeline and
        continuity/governance expectations for CNPOS v1_2.
        """
        return [
            CodeMutationRuleV1_2(
                rule_id="v1_2-domain-allowed",
                description="Mutations must target a known v1_2 domain "
                            "(AGENTS, RUNTIME, ORCHESTRATORS, GOVERNANCE, STATE, CONTRACTS).",
                allowed_domains=[
                    "AGENTS",
                    "RUNTIME",
                    "ORCHESTRATORS",
                    "GOVERNANCE",
                    "STATE",
                    "CONTRACTS",
                ],
            ),
            CodeMutationRuleV1_2(
                rule_id="v1_2-max-changes-default",
                description="Default limit on number of changed files per mutation.",
                max_changes=10,
            ),
            CodeMutationRuleV1_2(
                rule_id="v1_2-require-tests",
                description="Mutations that touch executable Python modules must include tests.",
                require_tests=True,
            ),
            CodeMutationRuleV1_2(
                rule_id="v1_2-require-governance-tag",
                description="All mutations must carry at least one governance tag "
                            "for audit and telemetry.",
                require_governance_tag=True,
            ),
        ]

    def all_rules(self) -> List[CodeMutationRuleV1_2]:
        """
        Return the full list of mutation rules for v1_2.
        """
        return list(self._rules)

    def rules_for_domain(self, domain: str) -> List[CodeMutationRuleV1_2]:
        """
        Filter rules that apply to a given domain.

        Args:
            domain: High-level domain name (e.g. 'AGENTS', 'RUNTIME').

        Returns:
            List of rules that either explicitly allow the domain or
            have no domain restriction.
        """
        domain_upper = domain.upper()
        filtered: List[CodeMutationRuleV1_2] = []

        for rule in self._rules:
            if not rule.allowed_domains or domain_upper in rule.allowed_domains:
                filtered.append(rule)

        logger.debug(
            "Selected %d rules for domain '%s'", len(filtered), domain_upper
        )
        return filtered

    def validate_mutation(self, payload: Dict[str, Any]) -> List[str]:
        """
        Validate a mutation payload against the v1_2 rule set.

        Expected payload keys (inferred from validator usage):
            - domain: str
            - changes: List[Dict[str, Any]] (each describing a file/module change)
            - tests: Optional[List[str]] (test identifiers or paths)
            - governance_tags: Optional[List[str]] (policy/flag identifiers)

        Args:
            payload: Mutation description as a dict.

        Returns:
            List of violation messages. An empty list means the mutation
            satisfies all rules.
        """
        violations: List[str] = []

        domain = str(payload.get("domain", "")).upper()
        changes = payload.get("changes") or []
        tests = payload.get("tests") or []
        governance_tags = payload.get("governance_tags") or []

        rules = self.rules_for_domain(domain)

        for rule in rules:
            # Domain rule: already filtered by rules_for_domain, but we still
            # enforce that domain is non-empty and recognized.
            if rule.rule_id == "v1_2-domain-allowed":
                if not domain:
                    violations.append(
                        "Mutation payload must specify a non-empty 'domain'."
                    )

            # Max changes rule.
            if rule.max_changes is not None:
                if not isinstance(changes, list):
                    violations.append(
                        f"Mutation 'changes' must be a list for rule {rule.rule_id}."
                    )
                elif len(changes) > rule.max_changes:
                    violations.append(
                        f"Mutation exceeds maximum allowed changes "
                        f"({len(changes)} > {rule.max_changes}) for rule {rule.rule_id}."
                    )

            # Require tests rule.
            if rule.require_tests:
                # Only enforce when there are code changes.
                if isinstance(changes, list) and changes and not tests:
                    violations.append(
                        "Mutations that change Python modules must include associated tests."
                    )

            # Require governance tag rule.
            if rule.require_governance_tag and not governance_tags:
                violations.append(
                    "Mutation payload must include at least one governance tag."
                )

        logger.debug(
            "Validated mutation for domain '%s': %d violation(s)", domain, len(violations)
        )
        return violations


# Public singleton used by validators and governance loader.
CodeMut = CodeMutationRulesV1_2()

__all__ = ["CodeMutationRuleV1_2", "CodeMutationRulesV1_2", "CodeMut"]
