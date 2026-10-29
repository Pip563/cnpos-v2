# cnpos/core/agents/code_reviewer_agent.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class CodeReviewerAgentV1_2Error(Exception):
    """Raised when CodeReviewerAgentV1_2 encounters an unrecoverable error."""
    pass


class CodeReviewerAgent:
    """
    Deterministic code reviewer agent for CNPOS v1_2.

    Responsibilities:
    - Perform static and semantic review of generated code artifacts.
    - Check compliance with governance rules (mutation safety, architecture constraints).
    - Produce actionable review feedback and suggested fixes.
    - Validate review results through the validator pipeline.
    - Route review tasks through the backend manager (LLM or rule-based backend).

    Domain: CODE_REVIEWER
    Version: v1_2
    """

    DOMAIN = "CODE_REVIEWER"
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
            "CodeReviewerAgent initialized with backend_manager=%s, "
            "validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def review(
        self,
        artifact: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for reviewing a code artifact.

        Args:
            artifact: Code artifact payload. Expected keys include:
                      - 'source': the code text to review
                      - 'metadata': optional metadata (module name, path, etc.)
                      - 'plan': optional code plan used to generate the artifact
            context: Optional orchestration context (pipeline identifiers, caller info).

        Returns:
            A validated review payload containing findings, severity levels,
            and suggested fixes.

        Raises:
            CodeReviewerAgentV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info(
            "CodeReviewerAgent.review invoked for artifact_id=%s",
            artifact.get("metadata", {}).get("id"),
        )

        try:
            policy = self._load_governance_policy()
            backend_request = self._build_backend_request(artifact, context, policy)
            raw_review = self._generate_review(backend_request)
            validated_review = self._validate_review(raw_review, policy, context)

            logger.info(
                "CodeReviewerAgent.review completed for artifact_id=%s",
                artifact.get("metadata", {}).get("id"),
            )
            return {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "review": validated_review,
                "context": context,
            }

        except (BackendManagerV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("CodeReviewerAgent: controlled failure: %s", exc, exc_info=True)
            raise CodeReviewerAgentV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("CodeReviewerAgent: unexpected failure: %s", exc, exc_info=True)
            raise CodeReviewerAgentV1_2Error(f"Unexpected error in CodeReviewerAgent.review: {exc}") from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_governance_policy(self) -> Dict[str, Any]:
        """
        Load governance policy for code review from GovernanceLoaderV1_2.

        Returns:
            Governance policy dict.
        """
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("CodeReviewerAgent: loaded governance policy for domain=%s", self.DOMAIN)
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
        logger.debug("CodeReviewerAgent: built backend_request=%s", backend_request)
        return backend_request

    def _generate_review(self, backend_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the code review task through BackendManagerV1_2.

        Returns:
            Raw review payload.
        """
        logger.debug("CodeReviewerAgent: routing code review through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="CODE_REVIEW",
            payload=backend_request,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for code review.")
        logger.debug("CodeReviewerAgent: backend returned raw_review=%s", response)
        return response

    def _validate_review(
        self,
        raw_review: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the generated review payload through ValidatorPipelineV1_2.

        Returns:
            Validated review payload.
        """
        logger.debug("CodeReviewerAgent: validating raw_review through ValidatorPipelineV1_2")
        validation_input: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": raw_review,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for code review validation.")
        logger.debug("CodeReviewerAgent: validated_review=%s", result)
        return result
