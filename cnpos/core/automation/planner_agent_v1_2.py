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


class AutomationPlannerAgentV1_2Error(Exception):
    """
    Raised when AutomationPlannerAgentV1_2 encounters an unrecoverable error.
    """


class AutomationPlannerAgentV1_2:
    """
    Deterministic planner agent for the CNPOS automation subsystem.

    Responsibilities:
    - Load governance specification.
    - Validate module naming.
    - Build deterministic automation stages.
    - Generate planning metadata.
    - Validate plan output through ValidatorPipelineV1_2.
    - Register planning activity in AutomationStateManagerV1_2.
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
            governance_loader or GovernanceLoaderV1_2()
        )

        self._state_manager = (
            state_manager or AutomationStateManagerV1_2()
        )

        self._validator_pipeline = (
            validator_pipeline or ValidatorPipelineV1_2()
        )

        logger.debug(
            "AutomationPlannerAgentV1_2 initialized."
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan_module_generation(
        self,
        *,
        module_path: str,
        domain: str,
        module_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a deterministic automation plan.
        """
        context = context or {}

        logger.info(
            "AutomationPlannerAgentV1_2.plan_module_generation "
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
            raise AutomationPlannerAgentV1_2Error(
                str(exc)
            ) from exc

        self._validate_naming_rules(
            module_path=module_path,
            governance_spec=governance_spec,
        )

        automation_id = self._register_plan(
            module_path=module_path,
            domain=domain,
            module_type=module_type,
            context=context,
        )

        plan = {
            "automation_id": automation_id,
            "version": self.VERSION,
            "domain": domain,
            "module_type": module_type,
            "module_path": module_path,
            "stages": self._build_stages(),
            "constraints": self._build_constraints(
                governance_spec=governance_spec,
                domain=domain,
                module_type=module_type,
            ),
        }

        try:
            self._validator_pipeline.validate(
                domain="automation",
                payload=plan,
                contract_schema=None,
                governance_loader=None,
                context={
                    "state_key": (
                        f"automation_plan::{automation_id}"
                    )
                },
            )
        except ValidatorPipelineV1_2Error as exc:
            raise AutomationPlannerAgentV1_2Error(
                f"Plan validation failed: {exc}"
            ) from exc

        return plan

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _register_plan(
        self,
        *,
        module_path: str,
        domain: str,
        module_type: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Register planning activity.
        """
        try:
            if hasattr(
                self._state_manager,
                "register_pending_module",
            ):
                return self._state_manager.register_pending_module(
                    module_path=module_path,
                    domain=domain,
                    stage="planned",
                    metadata={
                        "module_type": module_type,
                        "context": context,
                    },
                )
        except AutomationStateManagerV1_2Error as exc:
            raise AutomationPlannerAgentV1_2Error(
                str(exc)
            ) from exc

        return (
            f"{domain}::{module_type}::{module_path}"
        )

    def _validate_naming_rules(
        self,
        *,
        module_path: str,
        governance_spec: Dict[str, Any],
    ) -> None:
        """
        Validate module naming rules.
        """
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
            raise AutomationPlannerAgentV1_2Error(
                (
                    f"Module path '{module_path}' "
                    f"must end with '{required_suffix}'"
                )
            )

        for forbidden in forbidden_suffixes:
            if forbidden in module_path:
                raise AutomationPlannerAgentV1_2Error(
                    (
                        f"Module path '{module_path}' "
                        f"contains forbidden version "
                        f"identifier '{forbidden}'"
                    )
                )

    def _build_stages(self) -> List[Dict[str, str]]:
        """
        Build deterministic automation stages.
        """
        return [
            {"name": "plan"},
            {"name": "write"},
            {"name": "review"},
            {"name": "test"},
            {"name": "rewrite"},
            {"name": "finalize"},
        ]

    def _build_constraints(
        self,
        *,
        governance_spec: Dict[str, Any],
        domain: str,
        module_type: str,
    ) -> Dict[str, Any]:
        """
        Build planning constraints.
        """
        return {
            "domain": domain,
            "module_type": module_type,
            "naming": governance_spec.get("naming", {}),
            "imports": governance_spec.get("imports", {}),
            "structure": governance_spec.get("structure", {}),
            "validators": governance_spec.get("validators", {}),
            "drift": governance_spec.get("drift", {}),
            "automation": governance_spec.get("automation", {}),
        }


__all__ = [
    "AutomationPlannerAgentV1_2",
    "AutomationPlannerAgentV1_2Error",
]
