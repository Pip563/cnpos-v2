from __future__ import annotations

from unittest.mock import Mock

import pytest

from cnpos.core.automation.rewrite_loop_coordinator_v1_2 import (
    RewriteLoopCoordinatorV1_2,
    RewriteLoopCoordinatorV1_2Error,
)
from cnpos.core.automation.rewriter_agent_v1_2 import (
    AutomationRewriterAgentV1_2Error,
)
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2Error,
)


def test_validation_success_without_rewrite() -> None:
    validator_pipeline = Mock()
    validator_pipeline.validate.return_value = {
        "_validator_v1_2": {
            "status": "passed",
        }
    }

    rewriter_agent = Mock()

    coordinator = RewriteLoopCoordinatorV1_2(
        rewriter_agent=rewriter_agent,
        validator_pipeline=validator_pipeline,
    )

    result = coordinator.run_until_pass(
        automation_id="automation_001",
        module_path="cnpos/core/automation/example_module_v1_2.py",
        domain="automation",
        module_type="worker",
        code="valid_code",
    )

    assert result["success"] is True
    assert result["rewrite_cycles"] == 0
    rewriter_agent.rewrite_module.assert_not_called()


def test_single_rewrite_after_validator_failure() -> None:
    validator_pipeline = Mock()

    validator_pipeline.validate.side_effect = [
        ValidatorPipelineV1_2Error("initial failure"),
        {
            "_validator_v1_2": {
                "status": "passed",
            }
        },
    ]

    rewriter_agent = Mock()

    rewriter_agent.rewrite_module.return_value = {
        "code": "rewritten_code",
    }

    coordinator = RewriteLoopCoordinatorV1_2(
        rewriter_agent=rewriter_agent,
        validator_pipeline=validator_pipeline,
    )

    result = coordinator.run_until_pass(
        automation_id="automation_002",
        module_path="cnpos/core/automation/example_module_v1_2.py",
        domain="automation",
        module_type="worker",
        code="broken_code",
    )

    assert result["success"] is True
    assert result["rewrite_cycles"] == 1
    assert rewriter_agent.rewrite_module.call_count == 1


def test_review_issues_are_forwarded_to_rewriter() -> None:
    validator_pipeline = Mock()

    validator_pipeline.validate.side_effect = [
        ValidatorPipelineV1_2Error("review failure"),
        {
            "_validator_v1_2": {}
        },
    ]

    rewriter_agent = Mock()

    rewriter_agent.rewrite_module.return_value = {
        "code": "rewritten_code",
    }

    coordinator = RewriteLoopCoordinatorV1_2(
        rewriter_agent=rewriter_agent,
        validator_pipeline=validator_pipeline,
    )

    coordinator.run_until_pass(
        automation_id="automation_003",
        module_path="cnpos/core/automation/example_module_v1_2.py",
        domain="automation",
        module_type="worker",
        code="broken_code",
        review_report={
            "issues": [
                "review failure",
                "governance mismatch",
            ]
        },
    )

    call_kwargs = rewriter_agent.rewrite_module.call_args.kwargs

    assert "review failure" in call_kwargs["issues"]
    assert "governance mismatch" in call_kwargs["issues"]


def test_test_issues_are_forwarded_to_rewriter() -> None:
    validator_pipeline = Mock()

    validator_pipeline.validate.side_effect = [
        ValidatorPipelineV1_2Error("test failure"),
        {
            "_validator_v1_2": {}
        },
    ]

    rewriter_agent = Mock()

    rewriter_agent.rewrite_module.return_value = {
        "code": "rewritten_code",
    }

    coordinator = RewriteLoopCoordinatorV1_2(
        rewriter_agent=rewriter_agent,
        validator_pipeline=validator_pipeline,
    )

    coordinator.run_until_pass(
        automation_id="automation_004",
        module_path="cnpos/core/automation/example_module_v1_2.py",
        domain="automation",
        module_type="worker",
        code="broken_code",
        test_report={
            "issues": [
                "test failure",
                "drift detected",
            ]
        },
    )

    call_kwargs = rewriter_agent.rewrite_module.call_args.kwargs

    assert "test failure" in call_kwargs["issues"]
    assert "drift detected" in call_kwargs["issues"]


def test_maximum_cycles_are_enforced() -> None:
    validator_pipeline = Mock()

    validator_pipeline.validate.side_effect = (
        ValidatorPipelineV1_2Error("persistent failure")
    )

    rewriter_agent = Mock()

    rewriter_agent.rewrite_module.return_value = {
        "code": "rewritten_code",
    }

    coordinator = RewriteLoopCoordinatorV1_2(
        rewriter_agent=rewriter_agent,
        validator_pipeline=validator_pipeline,
    )

    result = coordinator.run_until_pass(
        automation_id="automation_005",
        module_path="cnpos/core/automation/example_module_v1_2.py",
        domain="automation",
        module_type="worker",
        code="broken_code",
        max_cycles=3,
    )

    assert result["success"] is False
    assert result["rewrite_cycles"] == 3
    assert rewriter_agent.rewrite_module.call_count == 3


def test_rewriter_error_is_promoted() -> None:
    validator_pipeline = Mock()

    validator_pipeline.validate.side_effect = (
        ValidatorPipelineV1_2Error("validator failure")
    )

    rewriter_agent = Mock()

    rewriter_agent.rewrite_module.side_effect = (
        AutomationRewriterAgentV1_2Error("rewrite failed")
    )

    coordinator = RewriteLoopCoordinatorV1_2(
        rewriter_agent=rewriter_agent,
        validator_pipeline=validator_pipeline,
    )

    with pytest.raises(RewriteLoopCoordinatorV1_2Error):
        coordinator.run_until_pass(
            automation_id="automation_006",
            module_path="cnpos/core/automation/example_module_v1_2.py",
            domain="automation",
            module_type="worker",
            code="broken_code",
        )


def test_validator_issues_are_accumulated() -> None:
    validator_pipeline = Mock

