# cnpos/core/agents/code_planner_agent.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CodePlannerAgentV1_2Error(Exception):
    """Raised when CodePlannerAgentV1_2 encounters an unrecoverable error."""
    pass


class CodePlannerAgent:
    """
    Deterministic code planning agent for CNPOS v1_2.

    Responsibilities:
    - Transform high-level code tasks into structured implementation plans.
    - Decompose requirements into modules, functions, tests, and mutation-safe steps.
    - Enforce governance rules for allowed code mutations and architecture constraints.
    - Validate generated plans through the validator pipeline.
    - Route planning tasks through the backend manager (LLM or rule-based backend).

    Domain: CODE_PLANNER
    Version: v1_2
    """

    DOMAIN = "CODE_PLANNER"
    VERSION = "v1_2"

    def __init__(
        self,
        backend_manager: Optional[BackendManagerV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
    ) -> None:
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()

        logger.debug(
            "CodePlannerAgent initialized with backend_manager=%s, "
            "validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def plan(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for generating a deterministic code plan.

        Args:
            request: High-level code request payload. Expected keys include:
                     - 'task': textual description of the coding task
                     - 'constraints': optional architectural or governance constraints
                     - 'inputs': optional structured inputs (existing modules, specs, etc.)
            context: Optional orchestration context (pipeline identifiers, caller info).

        Returns:
            A validated code plan payload, suitable for consumption by code_writer_agent
            and downstream agents.

        Raises:
            CodePlannerAgentV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info("CodePlannerAgent.plan invoked with task=%s", request.get("task"))

        try:
            policy = self._load_governance_policy()
            backend_request = self._build_backend_request(request, context, policy)
            raw_plan = self._generate_plan(backend_request)
            validated_plan = self._validate_plan(raw_plan, policy, context)

            logger.info("CodePlannerAgent.plan completed for task=%s", request.get("task"))
            return {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "plan": validated_plan,
                "context": context,
            }

        except (BackendManagerV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CodePlannerAgent: controlled failure: %s", exc, exc_info=True)
            raise CodePlannerAgentV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CodePlannerAgent: unexpected failure: %s", exc, exc_info=True)
            raise CodePlannerAgentV1_2Error(f"Unexpected error in CodePlannerAgent.plan: {exc}") from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_governance_policy(self) -> Dict[str, Any]:
        """
        Load governance policy for code planning from GovernanceLoaderV1_2.

        Returns:
            Governance policy dict.
        """
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CodePlannerAgent: loaded governance policy for domain=%s", self.DOMAIN)
        return policy

    def _build_backend_request(
        self,
        request: Dict[str, Any],
        context: Dict[str, Any],
        policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the request payload for the backend manager.

        Returns:
            Backend request dict.
        """
        backend_request: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "task": request.get("task"),
            "constraints": request.get("constraints"),
            "inputs": request.get("inputs"),
            "context": context,
            "policy": policy,
        }
        logger.debug("CodePlannerAgent: built backend_request=%s", backend_request)
        return backend_request

    def _generate_plan(self, backend_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the code planning task through BackendManagerV1_2.

        Returns:
            Raw code plan payload.
        """
        logger.debug("CodePlannerAgent: routing code planning through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="CODE_PLANNING",
            payload=backend_request,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for code planning.")
        logger.debug("CodePlannerAgent: backend returned raw_plan=%s", response)
        return response

    def _validate_plan(
        self,
        raw_plan: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the generated code plan through ValidatorPipelineV1_2.

        Returns:
            Validated code plan payload.
        """
        logger.debug("CodePlannerAgent: validating raw_plan through ValidatorPipelineV1_2")
        validation_input: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": raw_plan,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for code plan validation.")
        logger.debug("CodePlannerAgent: validated_plan=%s", result)
        return result
