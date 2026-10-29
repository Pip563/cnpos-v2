# cnpos/core/automation/rewrite_loop_coordinator_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.automation.rewriter_agent_v1_2 import (
    AutomationRewriterAgentV1_2,
    AutomationRewriterAgentV1_2Error,
)
from cnpos.core.automation.state_manager_v1_2 import (
    AutomationStateManagerV1_2,
)
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)
from cnpos.core.state.mutation_state_manager_v1_2 import (
    MutationStateManagerV1_2,
)
from cnpos.core.state.continuity_state_v1_2 import (
    ContinuityStateV1_2,
)

logger = logging.getLogger(__name__)


class RewriteLoopCoordinatorV1_2Error(Exception):
    """
    Raised when RewriteLoopCoordinatorV1_2 encounters an
    unrecoverable orchestration failure.
    """
    pass


class RewriteLoopCoordinatorV1_2:
    """
    RewriteLoopCoordinatorV1_2

    Deterministic rewrite coordinator for the CNPOS automation subsystem.

    Responsibilities:
    - Coordinate rewrite cycles after review failures.
    - Coordinate rewrite cycles after test failures.
    - Coordinate rewrite cycles after governance failures.
    - Coordinate rewrite cycles after continuity failures.
    - Coordinate rewrite cycles after mutation failures.
    - Coordinate rewrite cycles after validator failures.
    - Loop until ValidatorPipelineV1_2 passes.
    - Record rewrite activity in automation state.
    - Prevent infinite rewrite recursion.

    Governance Requirements:
    - Strict v1_2 naming.
    - Deterministic output.
    - No legacy imports.
    - No version drift.
    """

    VERSION = "v1_2"
    DOMAIN = "automation_rewrite_loop_v1_2"

    def __init__(
        self,
        *,
        rewriter_agent: Optional[AutomationRewriterAgentV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        state_manager: Optional[AutomationStateManagerV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        continuity_state: Optional[ContinuityStateV1_2] = None,
    ) -> None:
        self._rewriter_agent = rewriter_agent or AutomationRewriterAgentV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._state_manager = state_manager or AutomationStateManagerV1_2()
        self._mutation_state_manager = (
            mutation_state_manager or MutationStateManagerV1_2()
        )
        self._continuity_state = continuity_state or ContinuityStateV1_2()

        logger.debug(
            "RewriteLoopCoordinatorV1_2 initialized "
            "rewriter_agent=%s "
            "validator_pipeline=%s "
            "state_manager=%s",
            self._rewriter_agent,
            self._validator_pipeline,
            self._state_manager,
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def run_until_pass(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        module_type: str,
        code: str,
        review_report: Optional[Dict[str, Any]] = None,
        test_report: Optional[Dict[str, Any]] = None,
        max_cycles: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute deterministic rewrite cycles until validation succeeds.

        Args:
            automation_id:
                Automation identifier.

            module_path:
                Module path being repaired.

            domain:
                Automation domain.

            module_type:
                Worker / validator / orchestrator /
                state / automation.

            code:
                Current module source.

            review_report:
                Reviewer output.

            test_report:
                Tester output.

            max_cycles:
                Maximum rewrite attempts.

        Returns:
            Dict[str, Any]
        """
        logger.info(
            "RewriteLoopCoordinatorV1_2.run_until_pass "
            "automation_id=%s module_path=%s",
            automation_id,
            module_path,
        )

        current_code = code

        collected_issues: List[str] = []
        collected_issues.extend(
            self._extract_issues(review_report)
        )
        collected_issues.extend(
            self._extract_issues(test_report)
        )

        cycle_index = 0

        while cycle_index <= max_cycles:
            validation_result = self._validate_code(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                module_type=module_type,
                code=current_code,
            )

            if validation_result["success"]:
                logger.info(
                    "RewriteLoopCoordinatorV1_2 validation passed "
                    "automation_id=%s cycle
