# cnpos/core/automation/validator_template_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ValidatorTemplateV1_2Error(Exception):
    """Raised when ValidatorTemplateV1_2 cannot render a valid validator template."""


class ValidatorTemplateV1_2:
    """
    ValidatorTemplateV1_2

    Deterministic validator module template provider for CNPOS v1_2.

    Responsibilities:
    - Provide strict v1_2-compliant Python source for new validator modules.
    - Enforce governance rules: future annotations, logger, error class, typed API.
    - Avoid forbidden suffixes (v1.2, v11, v1_1, v12) and legacy 'core.' imports.
    - Serve as a canonical building block for self-writing automation.

    The rendered template is a ready-to-write Python module, aligned with the
    cnpos.core.validators architecture (governance, continuity, mutation).
    """

    VERSION = "v1_2"

    def render(self *, module_name: str, class_name: str) -> str:
        """
        Render a strict v1_2 validator module template.

        Args:
            module_name:
                Target module filename (without .py), e.g. 'governance_validator_v1_2'.
            class_name:
                Main validator class name, e.g. 'GovernanceValidatorV1_2'.
                Must end with 'V1_2' and must not contain forbidden suffixes.

        Returns:
            str: Python source code for the validator module.

        Raises:
            ValidatorTemplateV1_2Error: If naming is invalid.
        """
        self._validate_class_name(class_name)
        return VALIDATOR_TEMPLATE_SOURCE_V1_2.format(
            module_name=module_name,
            class_name=class_name,
        )

    def _validate_class_name(self, class_name: str) -> None:
        """
        Enforce strict v1_2 class naming rules.

        Class names must:
        - End with 'V1_2'.
        - Not contain forbidden suffixes (v1.2, v11, v1_1, v12).
        """
        if not class_name.endswith("V1_2"):
            raise ValidatorTemplateV1_2Error(
                f"class_name '{class_name}' must end with 'V1_2'"
            )

        forbidden = ("v1.2", "v11", "v1_1", "v12")
        lowered = class_name.lower()
        if any(suffix in lowered for suffix in forbidden):
            raise ValidatorTemplateV1_2Error(
                f"class_name '{class_name}' contains forbidden suffix"
            )


VALIDATOR_TEMPLATE_SOURCE_V1_2 = """\
# {module_name}.py

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.governance.code_mutation_rules_v1_2 import CodeMutationRulesV1_2
from cnpos.core.runtime.continuity_engine_v1_2 import ContinuityEngineV1_2, ContinuityEngineV1_2Error

logger = logging.getLogger(__name__)


class {class_name}Error(Exception):
    \\"""Raised when {class_name} encounters a validation error.\\"""


class {class_name}:
    \\"""Deterministic validator for CNPOS v1_2.

    Responsibilities:
    - Validate payloads against governance, continuity, and mutation rules.
    - Operate as a pure function over structured payloads.
    - Avoid side effects except logging.
    \\"""


    def __init__(
        self,
        *,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        mutation_rules: Optional[CodeMutationRulesV1_2] = None,
        continuity_engine: Optional[ContinuityEngineV1_2] = None,
    ) -> None:
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._mutation_rules = mutation_rules or CodeMutationRulesV1_2()
        self._continuity_engine = continuity_engine or ContinuityEngineV1_2()

        logger.debug(
            "{class_name} initialized governance_loader=%s mutation_rules=%s continuity_engine=%s",
            self._governance_loader,
            self._mutation_rules,
            self._continuity_engine,
        )

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        \\"""Validate the given payload.

        Args:
            payload: Structured payload to validate.

        Returns:
            Dict[str, Any]: Validation result, including 'valid': bool and 'errors': list.
        \\"""
        logger.debug("{class_name}.validate called with payload=%s", payload)

        errors: List[str] = []

        # Governance validation
        try:
            spec = self._governance_loader.load_spec(domain=payload.get("domain", "unknown"))
        except Exception as exc:
            logger.exception("{class_name} governance load failed: %s", exc)
            errors.append(f"governance load failed: {exc}")
            spec = {}

        # Mutation rules validation
        mutation_result = self._mutation_rules.evaluate(payload)
        if not mutation_result.get("allowed", True):
            errors.append("mutation rules violation")

        # Continuity validation
        try:
            continuity_result = self._continuity_engine.check(payload=payload)
        except ContinuityEngineV1_2Error as exc:
            logger.exception("{class_name} continuity check failed: %s", exc)
            errors.append(f"continuity check failed: {exc}")
            continuity_result = {"status": "error", "error": str(exc)}

        valid = not errors

        result: Dict[str, Any] = {
            "valid": valid,
            "errors": errors,
            "spec": spec,
            "mutation": mutation_result,
            "continuity": continuity_result,
            "validator": "{class_name}",
        }

        logger.debug("{class_name}.validate returning result=%s", result)
        return result


__all__ = ["{class_name}", "{class_name}Error"]
"""

__all__ = ["ValidatorTemplateV1_2", "ValidatorTemplateV1_2Error"]
