# cnpos/core/runtime/workers/prompt_worker_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from cnpos.core.agents.prompt_agent_v1_2 import PromptAgentV1_2
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class PromptWorkerV1_2Error(Exception):
    """Raised when PromptWorkerV1_2 encounters an unrecoverable error."""


class PromptWorkerV1_2:
    """
    PromptWorkerV1_2

    Deterministic prompt-level worker for CNPOS v1_2.

    Responsibilities:
    - Accept raw prompt payloads from orchestrators/pipelines.
    - Validate prompt payloads via ValidatorPipelineV1_2.
    - Delegate actual LLM interaction to PromptAgentV1_2.
    - Provide a stable prompt domain entry point for both cinematic and code pipelines.

    Domain: prompt
    Version: v1_2
    """

    DOMAIN = "prompt"
    VERSION = "v1_2"

    def __init__(
        self,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        prompt_agent: Optional[PromptAgentV1_2] = None,
    ) -> None:
        super().__init__()

        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._prompt_agent = prompt_agent or PromptAgentV1_2()

        logger.debug(
            "PromptWorkerV1_2 initialized with validator_pipeline=%s prompt_agent=%s",
            self._validator_pipeline,
            self._prompt_agent,
        )

    def run(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        logger.info(
            "PromptWorkerV1_2.run invoked for prompt_id=%s",
            payload.get("prompt_id"),
        )

        try:
            validated_payload = self._validate_payload(payload)
            agent_result = self._execute_agent(validated_payload, context)

            result = {
                "domain": self.DOMAIN,
                "version": self.VERSION,
                "validated_payload": validated_payload,
                "agent_result": agent_result,
                "context": context,
            }

            logger.info(
                "PromptWorkerV1_2.run completed for prompt_id=%s",
                payload.get("prompt_id"),
            )
            return result

        except (ValidatorPipelineV1_2Error, PromptWorkerV1_2Error) as exc:
            logger.error(
                "PromptWorkerV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise PromptWorkerV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error(
                "PromptWorkerV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise PromptWorkerV1_2Error(
                f"Unexpected error in PromptWorkerV1_2.run: {exc}"
            ) from exc

    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug(
            "PromptWorkerV1_2._validate_payload payload_keys=%s",
            list(payload.keys()),
        )
        validated = self._validator_pipeline.validate(
            domain=self.DOMAIN,
            payload=payload,
            contract_schema=None,
            governance_loader=None,
        )
        logger.debug(
            "PromptWorkerV1_2._validate_payload completed; validated_keys=%s",
            list(validated.keys()),
        )
        return validated

    def _extract_prompt_and_parameters(
        self,
        payload: Dict[str, Any],
    ) -> Tuple[str, Dict[str, Any]]:
        prompt = str(payload.get("prompt", "")).strip()
        parameters = payload.get("parameters") or {}

        if not prompt:
            logger.error("PromptWorkerV1_2._extract_prompt_and_parameters missing 'prompt'")
            raise PromptWorkerV1_2Error("Prompt payload must contain a non-empty 'prompt'")

        logger.debug(
            "PromptWorkerV1_2._extract_prompt_and_parameters prompt_len=%d parameters_keys=%s",
            len(prompt),
            list(parameters.keys()),
        )
        return prompt, parameters

    def _execute_agent(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt, parameters = self._extract_prompt_and_parameters(payload)

        logger.debug(
            "PromptWorkerV1_2._execute_agent backend_key=%s",
            context.get("backend_key"),
        )

        result = self._prompt_agent.generate_prompt(
            request={
                "task": prompt,
                "inputs": payload.get("inputs"),
                "constraints": payload.get("constraints"),
            },
            context=context,
        )

        logger.debug(
            "PromptWorkerV1_2._execute_agent agent_result_keys=%s",
            list(result.keys()),
        )
        return result


__all__ = ["PromptWorkerV1_2", "PromptWorkerV1_2Error"]
