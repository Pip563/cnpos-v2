# cnpos/core/automation/orchestrator_template_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OrchestratorTemplateV1_2Error(Exception):
    """Raised when OrchestratorTemplateV1_2 cannot render a valid orchestrator template."""


class OrchestratorTemplateV1_2:
    """
    OrchestratorTemplateV1_2

    Deterministic orchestrator module template provider for CNPOS v1_2.

    Responsibilities:
    - Provide strict v1_2-compliant Python source for new orchestrator modules.
    - Enforce governance rules: future annotations, logger, error class, typed API.
    - Avoid forbidden suffixes (v1.2, v11, v1_1, v12) and legacy 'core.' imports.
    - Serve as a canonical building block for self-writing automation.

    The rendered template is a ready-to-write Python module, aligned with the
    cnpos.core.orchestrators architecture (pipelines, telemetry, validators).
    """

    VERSION = "v1_2"

    def render(self, *, module_name: str, class_name: str) -> str:
        """
        Render a strict v1_2 orchestrator module template.

        Args:
            module_name:
                Target module filename (without .py), e.g. 'cinematic_pipeline_v1_2'.
            class_name:
                Main orchestrator class name, e.g. 'CinematicPipelineV1_2'.
                Must end with 'V1_2' and must not contain forbidden suffixes.

        Returns:
            str: Python source code for the orchestrator module.

        Raises:
            OrchestratorTemplateV1_2Error: If naming is invalid.
        """
        self._validate_class_name(class_name)
        return ORCHESTRATOR_TEMPLATE_SOURCE_V1_2.format(
            module_name=module_name,
            class_name=class_name,
        )

    def _validate_class_name(self, class_name: str) -> None:
        """
        Enforce strict v1_2 class naming rules.

        Class names must:
        - End with 'V1_2'.
        - Not contain forbidden suffixes (v1.2, v11, v1_1, v12).
        """
        if not class_name.endswith("V1_2"):
            raise OrchestratorTemplateV1_2Error(
                f"class_name '{class_name}' must end with 'V1_2'"
            )

        forbidden = ("v1.2", "v11", "v1_1", "v12")
        lowered = class_name.lower()
        if any(suffix in lowered for suffix in forbidden):
            raise OrchestratorTemplateV1_2Error(
                f"class_name '{class_name}' contains forbidden suffix"
            )


ORCHESTRATOR_TEMPLATE_SOURCE_V1_2 = """\
# {module_name}.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)
from cnpos.core.validators.validator_pipeline_v1_2 import ValidatorPipelineV1_2, ValidatorPipelineV1_2Error
from cnpos.core.orchestrators.telemetry.telemetry_manager import TelemetryManager
from cnpos.core.orchestrators.telemetry.event_stream import EventStream
from cnpos.core.orchestrators.telemetry.metrics_exporter import OrchestratorMetricsExporter

logger = logging.getLogger(__name__)


class {class_name}Error(Exception):
    \\"""Raised when {class_name} encounters an unrecoverable orchestration error.\\"""


class {class_name}:
    \\"""Deterministic orchestrator for CNPOS v1_2.

    Responsibilities:
    - Coordinate one or more workers and pipelines for a specific domain.
    - Emit telemetry events and metrics for orchestration runs.
    - Enforce strict v1_2 governance and naming rules.
    \\"""


    VERSION = "v1_2"
    DOMAIN = "{module_name}"

    def __init__(
        self,
        *,
        backend_manager: Optional[BackendManagerV1_2] = None,
        validator_pipeline: Optional[ValidatorPipelineV1_2] = None,
        telemetry_manager: Optional[TelemetryManager] = None,
        event_stream: Optional[EventStream] = None,
        metrics_exporter: Optional[OrchestratorMetricsExporter] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        backend_manager: Optional[BackendManagerV1_2] = None,
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._telemetry_manager = telemetry_manager or TelemetryManager()
        self._event_stream = event_stream or EventStream()
        self._metrics_exporter = metrics_exporter or OrchestratorMetricsExporter()
        self._config = config or {}

        logger.debug(
            "{class_name} initialized backend_manager=%s validator_pipeline=%s "
            "telemetry_manager=%s event_stream=%s metrics_exporter=%s config=%s",
            self._backend_manager,
            self._validator_pipeline,
            self._telemetry_manager,
            self._event_stream,
            self._metrics_exporter,
            self._config,
        )

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        \\"""Execute an orchestration run.

        Args:
            payload: Structured orchestration payload.

        Returns:
            Dict[str, Any]: Structured orchestration result.

        Raises:
            {class_name}Error: If orchestration cannot complete successfully.
        \\"""
        logger.debug("{class_name}.run called with payload=%s", payload)

        self._emit_event("orchestration_started", {"payload": payload})

        try:
            backend_result = self._backend_manager.execute(
                task=payload.get("task", "unknown"),
                payload=payload,
            )
        except BackendManagerV1_2Error as exc:
            logger.exception("{class_name} backend execution failed: %s", exc)
            self._emit_event("orchestration_failed", {"error": str(exc)})
            raise {class_name}Error(f"backend execution failed: {exc}") from exc

        result: Dict[str, Any] = {
            "status": "success",
            "payload": payload,
            "backend_result": backend_result,
            "orchestrator": "{class_name}",
            "version": self.VERSION,
            "domain": self.DOMAIN,
        }

        try:
            validated = self._validator_pipeline.validate(
                payload=result,
                domain=payload.get("domain", self.DOMAIN),
            )
            result["validated"] = validated
        except ValidatorPipelineV1_2Error as exc:
            logger.exception("{class_name} validation failed: %s", exc)
            self._emit_event("orchestration_failed", {"error": str(exc)})
            raise {class_name}Error(f"validation failed: {exc}") from exc

        self._emit_event("orchestration_completed", {"result": result})
        self._export_metrics(result)

        logger.debug("{class_name}.run returning result=%s", result)
        return result

    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        \\"""Emit a telemetry event for the orchestration run.\\"""
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
            logger.debug("{class_name} telemetry emission failed (%s): %s", event_type, exc)

    def _export_metrics(self, result: Dict[str, Any]) -> None:
        \\"""Export metrics for the orchestration run.\\"""
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
            logger.debug("{class_name} metrics export failed: %s", exc)


__all__ = ["{class_name}", "{class_name}Error"]
"""

__all__ = ["OrchestratorTemplateV1_2", "OrchestratorTemplateV1_2Error"]
