#cnpos/core/automation/reviewer_agent_v1_2.py
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

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)

from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class AutomationReviewerAgentV1_2Error(Exception):
    """
    Raised when AutomationReviewerAgentV1_2 encounters
    an unrecoverable error.
    """


class AutomationReviewerAgentV1_2:
    """
    Deterministic review agent for the CNPOS automation subsystem.

    Responsibilities:
    - Review generated automation modules.
    - Enforce governance naming requirements.
    - Enforce governance import requirements.
    - Execute validator pipeline checks.
    - Generate structured review feedback.
    - Persist review outcomes to automation state.
    """

    VERSION = "v1_2"
    DOMAIN = "automation"

    def __init__(
        self,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        state_manager: Optional[AutomationStateManagerV1_2] = None,
        backend_manager: Optional[BackendManagerV1_2] = None,        
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
    ) -> None:
        self._governance_loader = (
            governance_loader or GovernanceLoaderV1_2()
        )

        self._state_manager = (
            state_manager or AutomationStateManagerV1_2()
        )

        self._backend_manager = backend_manager or BackendManagerV1_2()  
        )

        self._validator_pipeline = (
            validator_pipeline or ValidatorPipelineV1_2()
        )

        logger.debug(
            "AutomationReviewerAgentV1_2 initialized."
        )

    def review_module(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        module_type: str,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Review a generated automation module.
        """
        context = context or {}

        logger.info(
            "AutomationReviewerAgentV1_2.review_module "
            "automation_id=%s module_path=%s",
            automation_id,
            module_path,
        )

        try:
            governance_spec = (
                self._governance_loader.load_governance_spec()
            )

        except GovernanceLoaderV1_2Error as exc:
            raise AutomationReviewerAgentV1_2Error(
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
                            f"automation_review::{automation_id}"
                        ),
                        **context,
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
            issues.append(
                f"validator_pipeline: {exc}"
            )

        success = len(issues) == 0

        review_feedback = (
            self._generate_review_feedback(
                module_path=module_path,
                module_type=module_type,
                code=code,
                governance_spec=governance_spec,
                issues=issues,
            )
        )

        self._record_review(
            automation_id=automation_id,
            module_path=module_path,
            domain=domain,
            success=success,
            module_type=module_type,
            issues=issues,
            feedback=review_feedback,
        )

        return {
            "automation_id": automation_id,
            "version": self.VERSION,
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "success": success,
            "issues": issues,
            "review_feedback": review_feedback,
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

        if not module_path.endswith(required_suffix):
            issues.append(
                (
                    f"Module path '{module_path}' "
                    f"must end with '{required_suffix}'"
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

        allowed_prefix = imports_spec.get(
            "allowed_prefix",
            "cnpos.core.",
        )

        forbidden_prefixes = imports_spec.get(
            "forbid_legacy_prefixes",
            [],
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

            if (
                stripped.startswith("from ")
                and "cnpos.core." in stripped
                and allowed_prefix not in stripped
            ):
                issues.append(
                    (
                        f"Import '{stripped}' "
                        "uses an invalid prefix."
                    )
                )

    def _generate_review_feedback(
        self,
        *,
        module_path: str,
        module_type: str,
        code: str,
        governance_spec: Dict[str, Any],
        issues: List[str],
    ) -> str:
        try:
            prompt = (
                f"Review module: {module_path}\n"
                f"Module type: {module_type}\n"
                f"Issues: {issues}\n"
                f"Governance: {governance_spec}\n"
                f"Code:\n{code}"
            )

            result = self._backend_manager.generate(
                prompt=prompt,
                domain="code",
                phase="CODE_REVIEW",
                task_type="automation_review",
            )

            output = result.get("output")

            if (
                isinstance(output, str)
                and output.strip()
            ):
                return output.strip()

        except BackendManagerV1_2Error:
            pass

        except Exception:
            logger.exception(
                "Unexpected review feedback error."
            )

        if issues:
            return (
                "Review completed with governance "
                "or structural issues."
            )

        return (
            "Review completed successfully "
            "with no issues detected."
        )

    def _record_review(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        success: bool,
        module_type: str,
        issues: List[str],
        feedback: str,
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
                    "review_feedback": feedback,
                    "reviewer": (
                        "AutomationReviewerAgentV1_2"
                    ),
                },
            )

        except AutomationStateManagerV1_2Error as exc:
            raise AutomationReviewerAgentV1_2Error(
                str(exc)
            ) from exc


__all__ = [
    "AutomationReviewerAgentV1_2",
    "AutomationReviewerAgentV1_2Error",
]
