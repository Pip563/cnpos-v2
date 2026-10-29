# cnpos/core/agents/code_writer_agent.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CodeWriterAgentV1_2Error(Exception):
    """Raised when CodeWriterAgentV1_2 encounters an unrecoverable error."""
    pass


class CodeWriterAgent:
    """
    Deterministic code writer agent for CNPOS v1_2.

    Responsibilities:
    - Transform validated code plans into concrete source code artifacts.
    - Respect governance rules for mutation safety and architectural constraints.
    - Produce structured code payloads (source, metadata, and traceability info).
    - Validate generated code through the validator pipeline.
    - Route code-generation tasks through the backend manager.

    Domain: CODE_WRITER
    Version: v1_2
    """

    DOMAIN = "CODE_WRITER"
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
            "CodeWriterAgent initialized with backend_manager=%s, "
            "validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def write(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for generating code from a validated plan.

        Args:
            plan: Validated code plan payload produced by CodePlannerAgent.
                  Expected keys include:
                  - 'modules': planned modules and their responsibilities
                  - 'functions': planned functions and signatures
                  - 'tests': planned tests (optional)
                  - any additional metadata required by governance
            context: Optional orchestration context (pipeline identifiers, caller info).

        Returns:
            A validated code artifact payload containing:
            - 'source': generated code text
            - 'metadata': module path, name, and version
            - 'plan': the originating plan for traceability

        Raises:
            CodeWriterAgentV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info("CodeWriterAgent.write invoked for plan_id=%s", plan.get("id"))

        try:
            policy = self._load_governance_policy()
            backend_request = self._build_backend_request(plan, context, policy)
            raw_artifact = self._generate_code(backend_request)
            validated_artifact = self._validate_artifact(raw_artifact, policy, context)

            logger.info(
                "CodeWriterAgent.write completed for plan_id=%s",
                plan.get("id"),
            )
            return {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "artifact": validated_artifact,
                "context": context,
            }

        except (BackendManagerV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CodeWriterAgent: controlled failure: %s", exc, exc_info=True)
            raise CodeWriterAgentV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CodeWriterAgent: unexpected failure: %s", exc, exc_info=True)
            raise CodeWriterAgentV1_2Error(f"Unexpected error in CodeWriterAgent.write: {exc}") from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_governance_policy(self) -> Dict[str, Any]:
        """
        Load governance policy for code writing from GovernanceLoaderV1_2.

        Returns:
            Governance policy dict.
        """
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CodeWriterAgent: loaded governance policy for domain=%s", self.DOMAIN)
        return policy

    def _build_backend_request(
        self,
        plan: Dict[str, Any],
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
            "plan": plan,
            "context": context,
            "policy": policy,
        }
        logger.debug("CodeWriterAgent: built backend_request=%s", backend_request)
        return backend_request

    def _generate_code(self, backend_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the code-generation task through BackendManagerV1_2.

        Returns:
            Raw code artifact payload.
        """
        logger.debug("CodeWriterAgent: routing code generation through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="CODE_GENERATION",
            payload=backend_request,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for code generation.")
        logger.debug("CodeWriterAgent: backend returned raw_artifact=%s", response)
        return response

    def _validate_artifact(
        self,
        raw_artifact: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the generated code artifact through ValidatorPipelineV1_2.

        Returns:
            Validated code artifact payload.
        """
        logger.debug("CodeWriterAgent: validating raw_artifact through ValidatorPipelineV1_2")
        validation_input: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": raw_artifact,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for code artifact validation.")
        logger.debug("CodeWriterAgent: validated_artifact=%s", result)
        return result
