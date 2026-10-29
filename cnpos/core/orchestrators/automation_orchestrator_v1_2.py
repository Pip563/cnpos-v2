# cnpos/core/orchestrators/automation_orchestrator_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.automation.code_automation_pipeline_v1_2 import (
    CodeAutomationPipelineV1_2,
    CodeAutomationPipelineV1_2Error,
)
from cnpos.core.automation.rewriter_agent_v1_2 import (
    AutomationRewriterAgentV1_2,
    AutomationRewriterAgentV1_2Error,
)
from cnpos.core.automation.state_manager_v1_2 import (
    AutomationStateManagerV1_2,
    AutomationStateManagerV1_2Error,
)
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)
from cnpos.core.orchestrators.telemetry.telemetry_manager import TelemetryManager
from cnpos.core.orchestrators.telemetry.event_stream import EventStream
from cnpos.core.orchestrators.telemetry.metrics_exporter import (
    OrchestratorMetricsExporter,
)

logger = logging.getLogger(__name__)


class AutomationOrchestratorV1_2Error(Exception):
    """Raised when AutomationOrchestratorV1_2 encounters an unrecoverable error."""


class AutomationOrchestratorV1_2:
    """
    AutomationOrchestratorV1_2

    Deterministic orchestrator for the CNPOS automation subsystem v1_2.

    Responsibilities:
    - Coordinate the code automation pipeline (plan → write → review → test).
    - Integrate the rewriter agent for deterministic self-repair of failed modules.
    - Persist automation runs and outcomes via AutomationStateManagerV1_2.
    - Emit telemetry events and metrics for all automation stages.
    - Enforce strict v1_2 validation via ValidatorPipelineV1_2.

    This orchestrator lives under cnpos.core.orchestrators and coordinates
    the automation domain without using legacy imports or non-v1_2 naming.
    """

    VERSION = "v1_2"
    DOMAIN = "automation_orchestrator_v1_2"

    def __init__(
        self,
        *,
        code_pipeline: Optional[CodeAutomationPipelineV1_2] = None,
        rewriter_agent: Optional[AutomationRewriterAgentV1_2] = None,
        state_manager: Optional[AutomationStateManagerV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        telemetry_manager: Optional[TelemetryManager] = None,
        event_stream: Optional[EventStream] = None,
        metrics_exporter: Optional[OrchestratorMetricsExporter] = None,
    ) -> None:
        self._code_pipeline = code_pipeline or CodeAutomationPipelineV1_2()
        self._rewriter_agent = rewriter_agent or AutomationRewriterAgentV1_2()
        self._state_manager = state_manager or AutomationStateManagerV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._telemetry_manager = telemetry_manager or TelemetryManager()
        self._event_stream = event_stream or EventStream()
        self._metrics_exporter = metrics_exporter or OrchestratorMetricsExporter()

        logger.debug(
            "AutomationOrchestratorV1_2 initialized "
            "code_pipeline=%s rewriter_agent=%s state_manager=%s "
            "validator_pipeline=%s telemetry_manager=%s event_stream=%s "
            "metrics_exporter=%s",
            self._code_pipeline,
            self._rewriter_agent,
            self._state_manager,
            self._validator_pipeline,
            self._telemetry_manager,
            self._event_stream,
            self._metrics_exporter,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run_module_generation(
        self,
        *,
        module_path: str,
        domain: str,
        module_type: str,
        context: Optional[Dict[str, Any]] = None,
        max_rewrites: int = 3,
    ) -> Dict[str, Any]:
        """
        Run the full automation loop for a single module, with optional rewrites.

        Args:
            module_path: Target module path (e.g. 'cnpos/core/runtime/new_worker_v1_2.py').
            domain: Logical domain (episode, scene, shot, render, character, code, automation).
            module_type: Logical type ('worker', 'validator', 'state', 'orchestrator', 'automation').
            context: Optional orchestration context.
            max_rewrites: Maximum number of rewrite attempts before failing.

        Returns:
            Dict[str, Any]: Final structured result of the automation run.

        Raises:
            AutomationOrchestratorV1_2Error: If the orchestration cannot complete successfully.
        """
        payload: Dict[str, Any] = {
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "context": context or {},
            "version": self.VERSION,
            "orchestrator_domain": self.DOMAIN,
        }

        self._emit_event("automation_run_started", payload)

        try:
            result = self._run_pipeline_with_rewrites(payload, max_rewrites=max_rewrites)
        except (CodeAutomationPipelineV1_2Error, AutomationRewriterAgentV1_2Error) as exc:
            logger.exception("AutomationOrchestratorV1_2 failed: %s", exc)
            self._emit_event("automation_run_failed", {"error": str(exc), **payload})
            raise AutomationOrchestratorV1_2Error(str(exc)) from exc

        self._persist_result(module_path=module_path, result=result)
        self._emit_event("automation_run_completed", {"result": result, **payload})
        self._export_metrics(result)

        return result

    # -------------------------------------------------------------------------
    # Internal orchestration helpers
    # -------------------------------------------------------------------------

    def _run_pipeline_with_rewrites(
        self,
        payload: Dict[str, Any],
        *,
        max_rewrites: int,
    ) -> Dict[str, Any]:
        """
        Execute the code automation pipeline and, if needed, trigger rewrites.

        The pipeline is expected to return a structured result containing at least:
        - 'status': 'success' | 'failed'
        - 'stage': last completed stage
        - 'details': structured metadata for debugging and telemetry
        """
        rewrites = 0
        current_payload = dict(payload)

        while True:
            self._emit_event("automation_pipeline_invocation", {"payload": current_payload})

            # INVENTED API: CodeAutomationPipelineV1_2.run(payload: Dict[str, Any]) -> Dict[str, Any]
            result = self._code_pipeline.run(current_payload)

            self._validate_result(result)

            status = result.get("status", "failed")
            if status == "success":
                return result

            if rewrites >= max_rewrites:
                logger.warning(
                    "Max rewrites reached for module_path=%s; last_result=%s",
                    current_payload.get("module_path"),
                    result,
                )
                return result

            rewrites += 1
            self._emit_event(
                "automation_rewrite_requested",
                {"payload": current_payload, "last_result": result, "rewrite_index": rewrites},
            )

            # INVENTED API: AutomationRewriterAgentV1_2.rewrite_module(payload, last_result) -> Dict[str, Any]
            current_payload = self._rewriter_agent.rewrite_module(
                payload=current_payload,
                last_result=result,
            )

    def _validate_result(self, result: Dict[str, Any]) -> None:
        """
        Route the result through ValidatorPipelineV1_2 to enforce governance,
        continuity, and mutation rules for the automation domain.
        """
        try:
            validated = self._validator_pipeline.validate(
                payload=result,
                domain=self.DOMAIN,
            )
            result.update({"validated": validated})
        except ValidatorPipelineV1_2Error as exc:
            logger.exception("ValidatorPipelineV1_2 failed for automation result: %s", exc)
            raise AutomationOrchestratorV1_2Error(
                f"Validation failed for automation result: {exc}"
            ) from exc

    def _persist_result(self, *, module_path: str, result: Dict[str, Any]) -> None:
        """
        Persist the final automation result via AutomationStateManagerV1_2.
        """
        try:
            # INVENTED API: AutomationStateManagerV1_2.record_run(...)
            self._state_manager.record_run(
                module_path=module_path,
                domain=self.DOMAIN,
                version=self.VERSION,
                result=result,
            )
        except AutomationStateManagerV1_2Error as exc:
            logger.warning("Failed to persist automation result: %s", exc)

    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Emit an orchestration event to the telemetry event stream.
        """
        try:
            self._event_stream.emit(
                event_type=event_type,
                data={
                    "domain": self.DOMAIN,
                    "version": self.VERSION,
                    **payload,
                },
            )
        except Exception as exc:
            logger.debug("Telemetry event emission failed (%s): %s", event_type, exc)

    def _export_metrics(self, result: Dict[str, Any]) -> None:
        """
        Export basic metrics for the automation run via OrchestratorMetricsExporter.
        """
        try:
            status = result.get("status", "unknown")
            stage = result.get("stage", "unknown")
            self._metrics_exporter.export(
                domain=self.DOMAIN,
                version=self.VERSION,
                status=status,
                stage=stage,
            )
        except Exception as exc:
            logger.debug("Metrics export failed: %s", exc)


__all__ = ["AutomationOrchestratorV1_2"]
