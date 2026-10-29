# cnpos/core/automation/finalization_handler_v1_2.py

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from cnpos.core.automation.state_manager_v1_2 import (
    AutomationStateManagerV1_2,
    AutomationStateManagerV1_2Error,
)
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2
from cnpos.core.state.mutation_state_manager_v1_2 import MutationStateManagerV1_2
from cnpos.core.orchestrators.telemetry.telemetry_manager import TelemetryManager
from cnpos.core.orchestrators.telemetry.event_stream import EventStream
from cnpos.core.orchestrators.telemetry.metrics_exporter import (
    OrchestratorMetricsExporter,
)

logger = logging.getLogger(__name__)


class FinalizationHandlerV1_2Error(Exception):
    """Raised when FinalizationHandlerV1_2 encounters an unrecoverable error."""


class FinalizationHandlerV1_2:
    """
    FinalizationHandlerV1_2

    Deterministic finalization handler for CNPOS automation v1_2.

    Responsibilities:
    - Write successfully generated module source to disk.
    - Record finalization in AutomationStateManagerV1_2.
    - Update continuity and mutation state for the automation domain.
    - Emit telemetry events and metrics for finalization runs.

    This handler is the last step in the self-writing automation loop.
    """

    VERSION = "v1_2"
    DOMAIN = "automation_finalization_v1_2"

    def __init__(
        self,
        *,
        project_root: Optional[Path] = None,
        state_manager: Optional[AutomationStateManagerV1_2] = None,
        continuity_state: Optional[ContinuityStateV1_2] = None,
        mutation_state: Optional[MutationStateManagerV1_2] = None,
        telemetry_manager: Optional[TelemetryManager] = None,
        event_stream: Optional[EventStream] = None,
        metrics_exporter: Optional[OrchestratorMetricsExporter] = None,
    ) -> None:
        # Default project root: three levels up from this file (cnpos/)
        self._project_root = project_root or Path(__file__).resolve().parents[2]
        self._state_manager = state_manager or AutomationStateManagerV1_2()
        self._continuity_state = continuity_state or ContinuityStateV1_2()
        self._mutation_state = mutation_state or MutationStateManagerV1_2()
        self._telemetry_manager = telemetry_manager or TelemetryManager()
        self._event_stream = event_stream or EventStream()
        self._metrics_exporter = metrics_exporter or OrchestratorMetricsExporter()

        logger.debug(
            "FinalizationHandlerV1_2 initialized project_root=%s state_manager=%s "
            "continuity_state=%s mutation_state=%s telemetry_manager=%s "
            "event_stream=%s metrics_exporter=%s",
            self._project_root,
            self._state_manager,
            self._continuity_state,
            self._mutation_state,
            self._telemetry_manager,
            self._event_stream,
            self._metrics_exporter,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def finalize(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize a successful automation run.

        Expected result keys:
            - 'module_path': str (e.g. 'cnpos/core/runtime/new_worker_v1_2.py')
            - 'source_code': str (Python source to write)
            - 'status': 'success' | 'failed'
            - 'stage': str (last automation stage)

        Returns:
            Dict[str, Any]: Finalization summary.

        Raises:
            FinalizationHandlerV1_2Error: If finalization cannot complete successfully.
        """
        logger.debug("FinalizationHandlerV1_2.finalize called with result=%s", result)

        status = result.get("status")
        if status != "success":
            raise FinalizationHandlerV1_2Error(
                f"cannot finalize non-successful result (status={status})"
            )

        module_path_str = result.get("module_path")
        source_code = result.get("source_code")
        if not module_path_str or not isinstance(module_path_str, str):
            raise FinalizationHandlerV1_2Error("missing or invalid 'module_path' in result")
        if not source_code or not isinstance(source_code, str):
            raise FinalizationHandlerV1_2Error("missing or invalid 'source_code' in result")

        target_path = self._resolve_module_path(module_path_str)
        self._emit_event(
            "automation_finalization_started",
            {"module_path": module_path_str, "target_path": str(target_path)},
        )

        try:
            self._write_module(target_path, source_code)
            self._record_state(module_path_str, result)
            self._emit_event(
                "automation_finalization_completed",
                {"module_path": module_path_str, "target_path": str(target_path)},
            )
            self._export_metrics(result)
        except Exception as exc:
            logger.exception("FinalizationHandlerV1_2.finalize failed: %s", exc)
            self._emit_event(
                "automation_finalization_failed",
                {"module_path": module_path_str, "error": str(exc)},
            )
            raise FinalizationHandlerV1_2Error(str(exc)) from exc

        summary: Dict[str, Any] = {
            "status": "finalized",
            "module_path": module_path_str,
            "target_path": str(target_path),
            "version": self.VERSION,
            "domain": self.DOMAIN,
        }
        logger.debug("FinalizationHandlerV1_2.finalize summary=%s", summary)
        return summary

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _resolve_module_path(self, module_path_str: str) -> Path:
        """
        Resolve a module path string to a filesystem path.

        If module_path_str is relative (e.g. 'cnpos/core/runtime/worker_v1_2.py'),
        it is resolved against the project root.
        """
        path = Path(module_path_str)
        if not path.is_absolute():
            path = self._project_root / path
        logger.debug("FinalizationHandlerV1_2._resolve_module_path resolved %s -> %s", module_path_str, path)
        return path

    def _write_module(self, target_path: Path, source_code: str) -> None:
        """
        Write the generated module source to disk, creating parent directories if needed.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(source_code, encoding="utf-8")
        logger.debug("FinalizationHandlerV1_2._write_module wrote module to %s", target_path)

    def _record_state(self, module_path: str, result: Dict[str, Any]) -> None:
        """
        Record finalization in automation, continuity, and mutation state.
        """
        try:
            # INVENTED API: AutomationStateManagerV1_2.record_finalization(...)
            self._state_manager.record_finalization(
                module_path=module_path,
                domain=self.DOMAIN,
                version=self.VERSION,
                result=result,
            )
        except AutomationStateManagerV1_2Error as exc:
            logger.warning("FinalizationHandlerV1_2._record_state automation state error: %s", exc)

        # Continuity and mutation updates are intentionally minimal and explicit.
        self._continuity_state.update_state(
            {
                "last_finalized_module": module_path,
                "last_finalized_version": self.VERSION,
            }
        )
        self._mutation_state.record_mutation(
            {
                "type": "automation_finalization",
                "module_path": module_path,
                "version": self.VERSION,
            }
        )

    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Emit a telemetry event for finalization.
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
            logger.debug("FinalizationHandlerV1_2._emit_event failed (%s): %s", event_type, exc)

    def _export_metrics(self, result: Dict[str, Any]) -> None:
        """
        Export metrics for the finalization run.
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
            logger.debug("FinalizationHandlerV1_2._export_metrics failed: %s", exc)


__all__ = ["FinalizationHandlerV1_2", "FinalizationHandlerV1_2Error"]
