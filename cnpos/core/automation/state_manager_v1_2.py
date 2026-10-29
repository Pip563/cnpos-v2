# cnpos/core/automation/state_manager_v1_2.py
from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AutomationStateManagerV1_2Error(Exception):
    """Raised when AutomationStateManagerV1_2 encounters an unrecoverable error."""
    pass


class AutomationStateManagerV1_2:
    """
    AutomationStateManagerV1_2

    Deterministic state manager for the automation system in CNPOS v1_2.

    Responsibilities:
    - Track generated modules (success/failure).
    - Track pending modules and their pipeline stage.
    - Track drift events between expected vs generated.
    - Track rewrite cycles and their outcomes.
    - Provide rollback snapshots for automation runs.
    - Provide query utilities for orchestrators and telemetry.

    All records are immutable once stored; updates are modeled as new entries.
    """

    VERSION = "v1_2"

    def __init__(self) -> None:
        # Core registries
        self._generated_modules: List[Dict[str, Any]] = []
        self._pending_modules: List[Dict[str, Any]] = []
        self._failed_modules: List[Dict[str, Any]] = []
        self._drift_events: List[Dict[str, Any]] = []
        self._rewrite_cycles: List[Dict[str, Any]] = []

        # Rollback snapshots keyed by label
        self._rollback_points: Dict[str, Dict[str, Any]] = {}

        logger.debug("AutomationStateManagerV1_2 initialized.")

    # -------------------------------------------------------------------------
    # Module lifecycle
    # -------------------------------------------------------------------------

    def register_pending_module(
        self,
        *,
        module_path: str,
        domain: str,
        stage: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Register a module as pending in the automation pipeline.

        Returns:
            str: automation_id for this pending module.
        """
        automation_id = str(uuid.uuid4())
        entry = {
            "automation_id": automation_id,
            "timestamp": time.time(),
            "module_path": module_path,
            "domain": domain,
            "stage": stage,
            "status": "pending",
            "metadata": metadata or {},
        }
        self._pending_modules.append(entry)

        logger.debug(
            "AutomationStateManagerV1_2.register_pending_module id=%s path=%s stage=%s",
            automation_id,
            module_path,
            stage,
        )
        return automation_id

    def register_generated_module(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a module as generated (success or failure).

        If success=False, the entry is also added to failed_modules.
        """
        entry = {
            "automation_id": automation_id,
            "timestamp": time.time(),
            "module_path": module_path,
            "domain": domain,
            "status": "success" if success else "failure",
            "metadata": metadata or {},
        }
        self._generated_modules.append(entry)

        if not success:
            self._failed_modules.append(entry)

        logger.debug(
            "AutomationStateManagerV1_2.register_generated_module id=%s path=%s success=%s",
            automation_id,
            module_path,
            success,
        )

    # -------------------------------------------------------------------------
    # Drift tracking
    # -------------------------------------------------------------------------

    def record_drift_event(
        self,
        *,
        module_path: str,
        domain: str,
        expected_spec: Dict[str, Any],
        actual_result: Dict[str, Any],
        details: Optional[List[str]] = None,
    ) -> str:
        """
        Record a drift event between expected vs generated module.

        Returns:
            str: drift_id.
        """
        drift_id = str(uuid.uuid4())
        entry = {
            "drift_id": drift_id,
            "timestamp": time.time(),
            "module_path": module_path,
            "domain": domain,
            "expected_spec": expected_spec,
            "actual_result": actual_result,
            "details": details or [],
        }
        self._drift_events.append(entry)

        logger.debug(
            "AutomationStateManagerV1_2.record_drift_event drift_id=%s path=%s domain=%s",
            drift_id,
            module_path,
            domain,
        )
        return drift_id

    # -------------------------------------------------------------------------
    # Rewrite cycles
    # -------------------------------------------------------------------------

    def record_rewrite_cycle(
        self,
        *,
        module_path: str,
        domain: str,
        cycle_index: int,
        success: bool,
        reasons: Optional[List[str]] = None,
    ) -> str:
        """
        Record a rewrite cycle for a module.

        Returns:
            str: cycle_id.
        """
        cycle_id = str(uuid.uuid4())
        entry = {
            "cycle_id": cycle_id,
            "timestamp": time.time(),
            "module_path": module_path,
            "domain": domain,
            "cycle_index": cycle_index,
            "success": success,
            "reasons": reasons or [],
        }
        self._rewrite_cycles.append(entry)

        logger.debug(
            "AutomationStateManagerV1_2.record_rewrite_cycle cycle_id=%s path=%s index=%d success=%s",
            cycle_id,
            module_path,
            cycle_index,
            success,
        )
        return cycle_id

    # -------------------------------------------------------------------------
    # Rollback snapshots
    # -------------------------------------------------------------------------

    def create_rollback_point(
        self,
        *,
        label: str,
        snapshot: Dict[str, Any],
    ) -> None:
        """
        Store a rollback snapshot for the automation system.

        Args:
            label: Human-readable identifier.
            snapshot: Arbitrary state snapshot (e.g., automation config).
        """
        self._rollback_points[label] = snapshot
        logger.debug(
            "AutomationStateManagerV1_2.create_rollback_point label=%s",
            label,
        )

    def rollback_to(self, label: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a rollback snapshot by label.

        Returns:
            Optional[Dict[str, Any]]: Snapshot or None.
        """
        snapshot = self._rollback_points.get(label)
        logger.debug(
            "AutomationStateManagerV1_2.rollback_to label=%s found=%s",
            label,
            snapshot is not None,
        )
        return snapshot

    # -------------------------------------------------------------------------
    # Query utilities
    # -------------------------------------------------------------------------

    def list_pending(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List pending modules, optionally filtered by domain.
        """
        if domain is None:
            return list(self._pending_modules)
        return [e for e in self._pending_modules if e.get("domain") == domain]

    def list_generated(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List generated modules, optionally filtered by domain.
        """
        if domain is None:
            return list(self._generated_modules)
        return [e for e in self._generated_modules if e.get("domain") == domain]

    def list_failed(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List failed modules, optionally filtered by domain.
        """
        if domain is None:
            return list(self._failed_modules)
        return [e for e in self._failed_modules if e.get("domain") == domain]

    def list_drift_events(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List drift events, optionally filtered by domain.
        """
        if domain is None:
            return list(self._drift_events)
        return [e for e in self._drift_events if e.get("domain") == domain]

    def list_rewrite_cycles(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List rewrite cycles, optionally filtered by domain.
        """
        if domain is None:
            return list(self._rewrite_cycles)
        return [e for e in self._rewrite_cycles if e.get("domain") == domain]

    def last_generated(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return the last generated module entry, optionally filtered by domain.
        """
        entries = self.list_generated(domain=domain)
        return entries[-1] if entries else None

    def last_failed(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return the last failed module entry, optionally filtered by domain.
        """
        entries = self.list_failed(domain=domain)
        return entries[-1] if entries else None

    def last_drift(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return the last drift event, optionally filtered by domain.
        """
        entries = self.list_drift_events(domain=domain)
        return entries[-1] if entries else None

    def last_rewrite_cycle(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return the last rewrite cycle, optionally filtered by domain.
        """
        entries = self.list_rewrite_cycles(domain=domain)
        return entries[-1] if entries else None


__all__ = ["AutomationStateManagerV1_2", "AutomationStateManagerV1_2Error"]
