# cnpos/core/orchestrators/code_automation_pipeline_v1_2.py
"""
Code Automation Orchestrator v1_2

This orchestrator coordinates the full automation subsystem located in:
    cnpos/core/automation/

It wires together:
- Automation agents (planner, reviewer, writer, rewriter, tester)
- Automation pipeline (code_pipeline_v1_2)
- Governance (rules + validator)
- State managers (automation + mutation + continuity)
- Runtime backend + worker registry
- Validators subsystem
- Telemetry subsystem

Strict rules enforced:
- All imports use cnpos.core.*
- All modules use _v1_2 suffix
- No legacy core.* imports
- No v12, v1.2, v11, v1.1 variants
"""

from __future__ import annotations
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# AUTOMATION SUBSYSTEM
# ---------------------------------------------------------------------------

from cnpos.core.automation.code_pipeline_v1_2 import CodePipelineV1_2
from cnpos.core.automation.planner_agent_v1_2 import AutomationPlannerAgentV1_2
from cnpos.core.automation.reviewer_agent_v1_2 import ReviewerAgentV1_2
from cnpos.core.automation.writer_agent_v1_2 import WriterAgentV1_2
from cnpos.core.automation.rewriter_agent_v1_2 import RewriterAgentV1_2
from cnpos.core.automation.test_agent_v1_2 import TestAgentV1_2
from cnpos.core.automation.state_manager_v1_2 import AutomationStateManagerV1_2
from cnpos.core.automation.governance_loader_v1_2 import load_automation_governance_v1_2

# ---------------------------------------------------------------------------
# GOVERNANCE SUBSYSTEM
# ---------------------------------------------------------------------------

from cnpos.core.governance.code_mutation_rules_v1_2 import CODE_MUTATION_RULES_V1_2
from cnpos.core.governance.governance_validator_v1_2 import GovernanceValidatorV1_2

# ---------------------------------------------------------------------------
# RUNTIME SUBSYSTEM
# ---------------------------------------------------------------------------

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)
from cnpos.core.runtime.workers.worker_registry_v1_2 import WorkerRegistryV1_2
from cnpos.core.runtime.workers.prompt_worker_v1_2 import PromptWorkerV1_2
from cnpos.core.runtime.workers.render_worker_v1_2 import RenderWorkerV1_2

# ---------------------------------------------------------------------------
# STATE SUBSYSTEM
# ---------------------------------------------------------------------------

from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2

# ---------------------------------------------------------------------------
# VALIDATORS SUBSYSTEM
# ---------------------------------------------------------------------------

from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2
from cnpos.core.validators.mutation_validator_v1_2 import MutationValidatorV1_2
from cnpos.core.validators.continuity_validator_v1_2 import ContinuityValidatorV1_2
from cnpos.core.validators.governance_validator_v1_2 import GovernanceValidatorV1_2 as GlobalGovernanceValidatorV1_2

# ---------------------------------------------------------------------------
# TELEMETRY SUBSYSTEM
# ---------------------------------------------------------------------------

from cnpos.core.orchestrators.telemetry.telemetry_manager import TelemetryManager
from cnpos.core.orchestrators.telemetry.event_stream import EventStream


# ===========================================================================
# CONTEXT OBJECT
# ===========================================================================

class CodeAutomationContextV1_2:
    """
    Aggregates all components required by the automation orchestrator.
    Keeps routing explicit and prevents architectural drift.
    """

    def __init__(
        self,
        backend_manager: BackendManagerV1_2,
        worker_registry: WorkerRegistryV1_2,
        automation_state_manager: AutomationStateManagerV1_2,
        mutation_state_manager: MutationStateManagerV1_2,
        continuity_state: ContinuityStateV1_2,
        governance_validator: GovernanceValidatorV1_2,
        global_governance_validator: GlobalGovernanceValidatorV1_2,
        validator_pipeline: ValidatorPipelineV1_2,
        telemetry_manager: TelemetryManager,
        event_stream: EventStream,
    ) -> None:
        self.backend_manager = backend_manager
        self.worker_registry = worker_registry
        self.automation_state_manager = automation_state_manager
        self.mutation_state_manager = mutation_state_manager
        self.continuity_state = continuity_state
        self.governance_validator = governance_validator
        self.global_governance_validator = global_governance_validator
        self.validator_pipeline = validator_pipeline
        self.telemetry_manager = telemetry_manager
        self.event_stream = event_stream


# ===========================================================================
# CONTEXT BUILDER
# ===========================================================================

def build_code_automation_context_v1_2(
    backend_config: Optional[Dict[str, Any]] = None,
) -> CodeAutomationContextV1_2:
    """
    Builds a fully wired automation context.
    This is the single routing point that makes the system aware of the
    new cnpos/core/automation/ structure.
    """

    # Runtime
    backend_manager = BackendManagerV1_2(
        config=backend_config or {}
    )
    worker_registry = WorkerRegistryV1_2()
    worker_registry.register_worker("prompt", PromptWorkerV1_2)
    worker_registry.register_worker("render", RenderWorkerV1_2)

    # State
    automation_state_manager = AutomationStateManagerV1_2()
    mutation_state_manager = MutationStateManagerV1_2()
    continuity_state = ContinuityStateV1_2()

    # Governance
    governance_spec = load_automation_governance_v1_2()
    governance_validator = GovernanceValidatorV1_2(
        governance_spec=governance_spec,
        mutation_rules=CODE_MUTATION_RULES_V1_2,
    )

    global_governance_validator = GlobalGovernanceValidatorV1_2(
        governance_spec=governance_spec,
        mutation_rules=CODE_MUTATION_RULES_V1_2,
    )

    # Validators pipeline
    mutation_validator = MutationValidatorV1_2(mutation_state_manager)
    continuity_validator = ContinuityValidatorV1_2(continuity_state)

    validator_pipeline = ValidatorPipelineV1_2(
        mutation_validator=mutation_validator,
        continuity_validator=continuity_validator,
        governance_validator=global_governance_validator,
    )

    # Telemetry
    event_stream = EventStream()
    telemetry_manager = TelemetryManager(event_stream)

    return CodeAutomationContextV1_2(
        backend_manager=backend_manager,
        worker_registry=worker_registry,
        automation_state_manager=automation_state_manager,
        mutation_state_manager=mutation_state_manager,
        continuity_state=continuity_state,
        governance_validator=governance_validator,
        global_governance_validator=global_governance_validator,
        validator_pipeline=validator_pipeline,
        telemetry_manager=telemetry_manager,
        event_stream=event_stream,
    )


# ===========================================================================
# ORCHESTRATOR ENTRY POINT
# ===========================================================================

def run_code_automation_pipeline_v1_2(
    task_spec: Dict[str, Any],
    backend_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main entry point used by:
        python -m cnpos codegen --module <module>

    Steps:
    - Build context
    - Instantiate automation agents
    - Wire them into CodePipelineV1_2
    - Run pipeline
    - Emit telemetry
    """

    context = build_code_automation_context_v1_2(backend_config)

    # Agents
    planner = AutomationPlannerAgentV1_2(context.backend_manager)
    reviewer = ReviewerAgentV1_2(context.backend_manager)
    writer = WriterAgentV1_2(context.backend_manager)
    rewriter = RewriterAgentV1_2(context.backend_manager)
    tester = TestAgentV1_2(context.backend_manager)

    # Pipeline
    pipeline = CodePipelineV1_2(
        AutomationPlannerAgentV1_2=planner,
        reviewer_agent=reviewer,
        writer_agent=writer,
        rewriter_agent=rewriter,
        test_agent=tester,
        automation_state_manager=context.automation_state_manager,
        governance_validator=context.governance_validator,
        validator_pipeline=context.validator_pipeline,
        worker_registry=context.worker_registry,
        telemetry_manager=context.telemetry_manager,
    )

    context.telemetry_manager.record_event(
        "code_automation_pipeline_v1_2.start",
        {"task_spec": task_spec},
    )

    result = pipeline.run(task_spec)

    context.telemetry_manager.record_event(
        "code_automation_pipeline_v1_2.end",
        {"result": result},
    )

    return result
