# cnpos/core/automation/test_agent_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.automation.governance_loader_v1_2 import (
    GovernanceLoaderV1_2,
    GovernanceLoaderV1_2Error,
)

from cnpos.core.automation.state_manager_v1_2 import (
    AutomationStateManagerV1_2,
    AutomationStateManagerV1_2Error,
)

from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class AutomationTestAgentV1_2Error(Exception):
    """
    Raised when AutomationTestAgentV1_2 encounters
    an unrecoverable error.
    """


class AutomationTestAgentV1_2:
    """
    Deterministic automation testing agent.

    Responsibilities:
    - Execute governance validation.
    - Execute naming validation.
    - Execute import validation.
    - Execute validator-pipeline validation.
    - Produce structured testing reports.
    - Persist testing outcomes.
    """

    VERSION = "v1_2"
    DOMAIN = "automation"

    def __init__(
        self,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        state_manager: Optional[AutomationStateManagerV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
    ) -> None:
        self._governance_loader = (
            governance_loader
            or GovernanceLoaderV1_2()
        )

        self._state_manager = (
            state_manager
            or AutomationStateManagerV1_2()
        )

        self._validator_pipeline = (
            validator_pipeline
            or ValidatorPipelineV1_2()
        )

        logger.debug(
            "AutomationTestAgentV1_2 initialized."
        )

    def run_tests_for_module(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        module_type: str,
        code: str,
    ) -> Dict[str, Any]:
        """
        Execute validation checks for a generated module.
        """
        logger.info(
            "AutomationTestAgentV1_2.run_tests_for_module "
            "automation_id=%s module_path=%s",
            automation_id,
            module_path,
        )

        try:
            governance_spec = (
                self._governance_loader
                .load_governance_spec()
            )

        except GovernanceLoaderV1_2Error as exc:
            raise AutomationTestAgentV1_2Error(
                str(exc)
            ) from exc

        issues: List[str] = []

        self._check_naming(
            module_path=module_path,
            governance_spec=governance_spec,
            issues=issues,
        )

        self._check_imports(
            code=code,
            governance_spec=governance_spec,
            issues=issues,
        )

        payload: Dict[str, Any] = {
            "automation_id": automation_id,
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "code": code,
        }

        validator_metadata: Dict[str, Any] = {}

        try:
            validated_payload = (
                self._validator_pipeline.validate(
                    domain=self.DOMAIN,
                    payload=payload,
                    contract_schema=None,
                    governance_loader=None,
                    context={
                        "state_key": (
                            f"automation_test::{automation_id}"
                        )
                    },
                )
            )

            validator_metadata = (
                validated_payload.get(
                    "_validator_v1_2",
                    {},
                )
            )

        except ValidatorPipelineV1_2Error as exc:
            logger.error(
                "AutomationTestAgentV1_2 validator "
                "pipeline failed: %s",
                exc,
                exc_info=True,
            )

            issues.append(
                f"validator_pipeline: {exc}"
            )

            validator_metadata = {}

        success = len(issues) == 0

        self._record_test_result(
            automation_id=automation_id,
            module_path=module_path,
            domain=domain,
            success=success,
            module_type=module_type,
            issues=issues,
        )

        return {
            "automation_id": automation_id,
            "version": self.VERSION,
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "success": success,
            "issues": issues,
            "validator_metadata": validator_metadata,
        }

    def _check_naming(
        self,
        *,
        module_path: str,
        governance_spec: Dict[str, Any],
        issues: List[str],
    ) -> None:
        naming = governance_spec.get(
            "naming",
            {},
        )

        required_suffix = naming.get(
            "module_suffix",
            "_v1_2.py",
        )

        forbidden_suffixes = naming.get(
            "forbidden_suffixes",
            [],
        )

        if not module_path.endswith(
            required_suffix
        ):
            issues.append(
                (
                    f"Module path '{module_path}' "
                    f"must end with "
                    f"'{required_suffix}'"
                )
            )

        for suffix in forbidden_suffixes:
            if suffix in module_path:
                issues.append(
                    (
                        f"Module path '{module_path}' "
                        f"contains forbidden version "
                        f"identifier '{suffix}'"
                    )
                )

    def _check_imports(
        self,
        *,
        code: str,
        governance_spec: Dict[str, Any],
        issues: List[str],
    ) -> None:
        imports_spec = governance_spec.get(
            "imports",
            {},
        )

        forbidden_prefixes = (
            imports_spec.get(
                "forbid_legacy_prefixes",
                [],
            )
        )

        for line in code.splitlines():
            stripped = line.strip()

            if not (
                stripped.startswith("from ")
                or stripped.startswith("import ")
            ):
                continue

            for forbidden in forbidden_prefixes:
                if forbidden in stripped:
                    issues.append(
                        (
                            f"Forbidden import prefix "
                            f"'{forbidden}' found in "
                            f"'{stripped}'"
                        )
                    )

    def _record_test_result(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        success: bool,
        module_type: str,
        issues: List[str],
    ) -> None:
        try:
            self._state_manager.register_generated_module(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                success=success,
                metadata={
                    "module_type": module_type,
                    "issues": issues,
                    "tested_by": (
                        "AutomationTestAgentV1_2"
                    ),
                },
            )

        except AutomationStateManagerV1_2Error as exc:
            raise AutomationTestAgentV1_2Error(
                str(exc)
            ) from exc


__all__ = [
    "AutomationTestAgentV1_2",
    "AutomationTestAgentV1_2Error",
]
