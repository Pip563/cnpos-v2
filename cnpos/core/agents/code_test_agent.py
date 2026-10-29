# cnpos/core/agents/code_test_agent.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CodeTestAgentV1_2Error(Exception):
    """Raised when CodeTestAgentV1_2 encounters an unrecoverable error."""
    pass


class CodeTestAgent:
    """
    Deterministic code test agent for CNPOS v1_2.

    Responsibilities:
    - Generate and/or execute tests for code artifacts.
    - Enforce governance rules for mutation-safe testing and coverage requirements.
    - Produce structured test results and diagnostics.
    - Validate test results through the validator pipeline.
    - Route test-generation and execution tasks through the backend manager.

    Domain: CODE_TEST
    Version: v1_2
    """

    DOMAIN = "CODE_TEST"
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
            "CodeTestAgent initialized with backend_manager=%s, "
            "validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run_tests(
        self,
        artifact: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for generating and/or executing tests for a code artifact.

        Args:
            artifact: Code artifact payload. Expected keys include:
                      - 'source': the code text to test
                      - 'metadata': optional metadata (module name, path, etc.)
                      - 'plan': optional code plan used to generate the artifact
            context: Optional orchestration context (pipeline identifiers, caller info).

        Returns:
            A validated test result payload containing test cases, execution status,
            coverage information, and diagnostics.

        Raises:
            CodeTestAgentV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info(
            "CodeTestAgent.run_tests invoked for artifact_id=%s",
            artifact.get("metadata", {}).get("id"),
        )

        try:
            policy = self._load_governance_policy()
            backend_request = self._build_backend_request(artifact, context, policy)
            raw_results = self._generate_and_execute_tests(backend_request)
            validated_results = self._validate_test_results(raw_results, policy, context)

            logger.info(
                "CodeTestAgent.run_tests completed for artifact_id=%s",
                artifact.get("metadata", {}).get("id"),
            )
            return {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "results": validated_results,
                "context": context,
            }

        except (BackendManagerV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CodeTestAgent: controlled failure: %s", exc, exc_info=True)
            raise CodeTestAgentV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CodeTestAgent: unexpected failure: %s", exc, exc_info=True)
            raise CodeTestAgentV1_2Error(f"Unexpected error in CodeTestAgent.run_tests: {exc}") from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_governance_policy(self) -> Dict[str, Any]:
        """
        Load governance policy for code testing from GovernanceLoaderV1_2.

        Returns:
            Governance policy dict.
        """
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CodeTestAgent: loaded governance policy for domain=%s", self.DOMAIN)
        return policy

    def _build_backend_request(
        self,
        artifact: Dict[str, Any],
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
            "artifact": artifact,
            "context": context,
            "policy": policy,
        }
        logger.debug("CodeTestAgent: built backend_request=%s", backend_request)
        return backend_request

    def _generate_and_execute_tests(self, backend_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the test-generation and execution task through BackendManagerV1_2.

        Returns:
            Raw test results payload.
        """
        logger.debug("CodeTestAgent: routing test-generation/execution through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="CODE_TESTING",
            payload=backend_request,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for code testing.")
        logger.debug("CodeTestAgent: backend returned raw_results=%s", response)
        return response

    def _validate_test_results(
        self,
        raw_results: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the test results payload through ValidatorPipelineV1_2.

        Returns:
            Validated test results payload.
        """
        logger.debug("CodeTestAgent: validating raw_results through ValidatorPipelineV1_2")
        validation_input: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": raw_results,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for code testing validation.")
        logger.debug("CodeTestAgent: validated_results=%s", result)
        return result
