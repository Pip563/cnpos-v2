# cnpos/core/automation/code_pipeline_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.automation.planner_agent_v1_2 import (
    AutomationPlannerAgentV1_2,
    AutomationPlannerAgentV1_2Error,
)

from cnpos.core.automation.reviewer_agent_v1_2 import (
    AutomationReviewerAgentV1_2,
    AutomationReviewerAgentV1_2Error,
)

from cnpos.core.automation.rewriter_agent_v1_2 import (
    AutomationRewriterAgentV1_2,
    AutomationRewriterAgentV1_2Error,
)

from cnpos.core.automation.test_agent_v1_2 import (
    AutomationTestAgentV1_2,
    AutomationTestAgentV1_2Error,
)

from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)

logger = logging.getLogger(__name__)


class CodePipelineV1_2Error(Exception):
    """Raised when CodePipelineV1_2 encounters an unrecoverable error."""


class CodePipelineV1_2:
    """
    Deterministic code automation pipeline for CNPOS v1_2.

    Responsibilities:
    - Coordinate planner, reviewer, rewriter and test agents.
    - Enforce strict v1_2 governance.
    - Produce deterministic pipeline outputs.
    - Provide the canonical import target expected by pipeline_map_v1_2.py.
    """

    VERSION = "v1_2"
    DOMAIN = "code_pipeline_v1_2"

    def __init__(
        self,
        planner_agent: Optional[AutomationPlannerAgentV1_2] = None,
        reviewer_agent: Optional[AutomationReviewerAgentV1_2] = None,
        rewriter_agent: Optional[AutomationRewriterAgentV1_2] = None,
        test_agent: Optional[AutomationTestAgentV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
    ) -> None:
        self._planner = planner_agent or AutomationPlannerAgentV1_2()
        self._reviewer = reviewer_agent or AutomationReviewerAgentV1_2()
        self._rewriter = rewriter_agent or AutomationRewriterAgentV1_2()
        self._tester = test_agent or AutomationTestAgentV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()

        logger.debug("CodePipelineV1_2 initialized.")

    def run(
        self,
        module_path: str,
        domain: str,
        module_type: str,
        code: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}

        try:
            plan = self._planner.plan_module_generation(
                module_path=module_path,
                domain=domain,
                module_type=module_type,
                context=context,
            )

            automation_id = plan.get("automation_id", "unknown")

            review = self._reviewer.review_module(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                module_type=module_type,
                code=code,
                context=context,
            )

            test_report = self._tester.run_tests_for_module(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                module_type=module_type,
                code=code,
            )

            rewritten = None

            if not test_report.get("success", False):
                rewritten = self._rewriter.rewrite_module(
                    automation_id=automation_id,
                    module_path=module_path,
                    domain=domain,
                    module_type=module_type,
                    code=code,
                    issues=test_report.get("issues", []),
                )

            payload = {
                "version": self.VERSION,
                "domain": self.DOMAIN,
                "plan": plan,
                "review": review,
                "tests": test_report,
                "rewrite": rewritten,
            }

            validated_payload = self._validator_pipeline.validate(
                domain="automation",
                payload=payload,
                contract_schema=None,
                governance_loader=None,
                context={
                    "pipeline": self.DOMAIN,
                    "version": self.VERSION,
                },
            )

            return {
                "version": self.VERSION,
                "domain": self.DOMAIN,
                "validated_payload": validated_payload,
            }

        except (
            AutomationPlannerAgentV1_2Error,
            AutomationReviewerAgentV1_2Error,
            AutomationRewriterAgentV1_2Error,
            AutomationTestAgentV1_2Error,
            ValidatorPipelineV1_2Error,
        ) as exc:
            logger.error(
                "CodePipelineV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise CodePipelineV1_2Error(str(exc)) from exc

        except Exception as exc:
            logger.error(
                "CodePipelineV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise CodePipelineV1_2Error(f"Unexpected pipeline failure: {exc}") from exc


__all__ = ["CodePipelineV1_2", "CodePipelineV1_2Error"]
