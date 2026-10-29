# cnpos/core/agents/prompt_agent.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.backend_manager_v1_2 import BackendManagerV1_2, BackendManagerV1_2Error
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2, GovernanceLoaderV1_2Error

logger = logging.getLogger(__name__)


class PromptAgentV1_2Error(Exception):
    """Raised when PromptAgent encounters an unrecoverable error in v1_2."""
    pass


class PromptAgent:
    """
    Deterministic prompt agent for CNPOS v1_2.

    Responsibilities:
    - Build structured prompts for runtime workers and pipelines.
    - Normalize user/task inputs into backend-ready prompt payloads.
    - Enforce governance rules on prompt content and structure.
    - Validate prompts through the validator pipeline.
    - Route prompt-generation tasks through the backend manager.

    Domain: PROMPT_AGENT
    Version: v1_2
    """

    DOMAIN = "PROMPT_AGENT"
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
            "PromptAgent initialized with backend_manager=%s, "
            "validator_pipeline=%s, governance_loader=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._governance_loader,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def generate_prompt(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Entry point for generating a structured prompt.

        Args:
            request: High-level prompt request payload. Expected keys include:
                     - 'task': textual description of what the backend should do
                     - 'inputs': optional structured inputs (contracts, specs, state)
                     - 'constraints': optional governance/architecture constraints
            context: Optional orchestration context (pipeline identifiers, caller info).

        Returns:
            A validated prompt payload suitable for consumption by runtime workers
            (e.g., prompt_worker_v1_2) and backend manager.

        Raises:
            PromptAgentV1_2Error: if any step fails.
        """
        context = context or {}
        logger.info("PromptAgent.generate_prompt invoked with task=%s", request.get("task"))

        try:
            policy = self._load_governance_policy()
            backend_request = self._build_backend_request(request, context, policy)
            raw_prompt = self._generate_raw_prompt(backend_request)
            validated_prompt = self._validate_prompt(raw_prompt, policy, context)

            logger.info("PromptAgent.generate_prompt completed for task=%s", request.get("task"))
            return {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "prompt": validated_prompt,
                "context": context,
            }

        except (BackendManagerV1_2Error, ValidatorPipelineV1_2Error, GovernanceLoaderV1_2Error) as exc:
            logger.error("PromptAgent: controlled failure: %s", exc, exc_info=True)
            raise PromptAgentV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error("PromptAgent: unexpected failure: %s", exc, exc_info=True)
            raise PromptAgentV1_2Error(f"Unexpected error in PromptAgent.generate_prompt: {exc}") from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _load_governance_policy(self) -> Dict[str, Any]:
        """
        Load governance policy for prompt generation from GovernanceLoaderV1_2.

        Returns:
            Governance policy dict.
        """
        policy = self._governance_loader.load_policy(domain=self.DOMAIN, version=self.VERSION)
        logger.debug("PromptAgent: loaded governance policy for domain=%s", self.DOMAIN)
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
            "inputs": request.get("inputs"),
            "constraints": request.get("constraints"),
            "context": context,
            "policy": policy,
        }
        logger.debug("PromptAgent: built backend_request=%s", backend_request)
        return backend_request

    def _generate_raw_prompt(self, backend_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the prompt-construction task through BackendManagerV1_2.

        Returns:
            Raw prompt payload.
        """
        logger.debug("PromptAgent: routing prompt generation through BackendManagerV1_2")
        response = self._backend_manager.route(
            task_type="PROMPT_GENERATION",
            payload=backend_request,
        )
        if not isinstance(response, dict):
            raise BackendManagerV1_2Error("BackendManagerV1_2 returned non-dict response for prompt generation.")
        logger.debug("PromptAgent: backend returned raw_prompt=%s", response)
        return response

    def _validate_prompt(
        self,
        raw_prompt: Dict[str, Any],
        policy: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate the generated prompt payload through ValidatorPipelineV1_2.

        Returns:
            Validated prompt payload.
        """
        logger.debug("PromptAgent: validating raw_prompt through ValidatorPipelineV1_2")
        validation_input: Dict[str, Any] = {
            "domain": self.DOMAIN,
            "version": self.VERSION,
            "payload": raw_prompt,
            "policy": policy,
            "context": context,
        }
        result = self._validator_pipeline.run(validation_input)
        if not isinstance(result, dict):
            raise ValidatorPipelineV1_2Error("ValidatorPipelineV1_2 returned non-dict result for prompt validation.")
        logger.debug("PromptAgent: validated_prompt=%s", result)
        return result
