# cnpos/core/automation/writer_agent_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

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


class AutomationWriterAgentV1_2Error(Exception):
    """
    Raised when AutomationWriterAgentV1_2 encounters an
    unrecoverable error.
    """


class AutomationWriterAgentV1_2:
    """
    Deterministic automation writer agent.

    Responsibilities:
    - Generate automation modules.
    - Enforce governance-driven output generation.
    - Produce strict v1_2 module content.
    - Register generated modules.
    - Validate generated output.
    - Maintain architectural consistency.
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
            "AutomationWriterAgentV1_2 initialized."
        )

    def write_from_plan(
        self,
        *,
        module_path: str,
        domain: str,
        module_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate automation code from a plan.
        """
        context = context or {}

        logger.info(
            "AutomationWriterAgentV1_2.write_from_plan "
            "module_path=%s domain=%s module_type=%s",
            module_path,
            domain,
            module_type,
        )

        try:
            governance_spec = (
                self._governance_loader.load_governance_spec()
            )

        except GovernanceLoaderV1_2Error as exc:
            raise AutomationWriterAgentV1_2Error(
                str(exc)
            ) from exc

        prompt = self._build_generation_prompt(
            module_path=module_path,
            domain=domain,
            module_type=module_type,
            governance_spec=governance_spec,
            context=context,
        )

        try:
            response = self._backend_manager.generate(
                prompt=prompt,
                domain="code",
                phase="CODE_WRITE",
                task_type="automation_generation",
            )

        except BackendManagerV1_2Error as exc:
            raise AutomationWriterAgentV1_2Error(
                str(exc)
            ) from exc

        generated_code = str(
            response.get(
                "output",
                "",
            )
        )

        payload = {
            "automation_id": (
                context.get(
                    "automation_id",
                    module_path,
                )
            ),
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "code": generated_code,
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
                            f"automation_write::{module_path}"
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
            raise AutomationWriterAgentV1_2Error(
                str(exc)
            ) from exc

        try:
            self._state_manager.register_generated_module(
                automation_id=payload["automation_id"],
                module_path=module_path,
                domain=domain,
                success=True,
                metadata={
                    "module_type": module_type,
                    "writer": (
                        "AutomationWriterAgentV1_2"
                    ),
                },
            )

        except AutomationStateManagerV1_2Error as exc:
            raise AutomationWriterAgentV1_2Error(
                str(exc)
            ) from exc

        return {
            "automation_id": payload["automation_id"],
            "version": self.VERSION,
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "code": generated_code,
            "validator_metadata": validator_metadata,
        }

    def _build_generation_prompt(
        self,
        *,
        module_path: str,
        domain: str,
        module_type: str,
        governance_spec: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """
        Build a deterministic generation prompt.
        """
        return (
            f"Module path: {module_path}\n"
            f"Domain: {domain}\n"
            f"Module type: {module_type}\n"
            f"Governance: {governance_spec}\n"
            f"Context: {context}\n\n"
            "Generate a strict v1_2 Python module.\n"
            "Use only cnpos.core imports.\n"
            "Do not use legacy versions.\n"
            "Return only module code."
        )


__all__ = [
    "AutomationWriterAgentV1_2",
    "AutomationWriterAgentV1_2Error",
]
