# cnpos/core/runtime/continuity_engine_v1_2.py
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Tuple, Optional

from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2

logger = logging.getLogger(__name__)

# v1_2-compliant version pattern (no dotted versions like v1.2)
VERSION_PATTERN = re.compile(r"v\d+_\d+$")


class ContinuityEngineV1_2Error(Exception):
    """Raised when continuity_engine_v1_2 encounters an unrecoverable error."""
    pass


class ContinuityEngineV1_2:
    """
    ContinuityEngineV1_2

    Deterministic continuity engine for CNPOS v1_2.

    Responsibilities:
    - Compare new payloads against active continuity state.
    - Detect drift across domains (episode, scene, shot, character, code).
    - Enforce v1_2 version naming (no dotted versions, no legacy).
    - Provide structured continuity reports for validators and orchestrators.

    Domain: CONTINUITY_ENGINE
    Version: v1_2
    """

    VERSION = "v1_2"

    def __init__(self, state: Optional[ContinuityStateV1_2] = None) -> None:
        self._state = state or ContinuityStateV1_2()
        logger.debug("ContinuityEngineV1_2 initialized with state=%s", self._state)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def evaluate(
        self,
        domain: str,
        new_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate continuity for a given domain and payload.

        Args:
            domain: Continuity domain (e.g., 'episode', 'scene', 'shot', 'character', 'code').
            new_payload: New payload to compare against active state.

        Returns:
            Dict[str, Any]: Continuity report with keys:
                - 'domain'
                - 'engine_version'
                - 'is_drift'
                - 'reasons' (List[str])
                - 'previous_state'
                - 'current_payload'
        """
        domain = domain.lower()
        logger.debug(
            "ContinuityEngineV1_2.evaluate domain=%s payload_keys=%s",
            domain,
            list(new_payload.keys()),
        )

        previous_state = self._state.get_state(domain)
        is_drift, reasons = self._detect_drift(previous_state, new_payload)

        report = {
            "domain": domain,
            "engine_version": self.VERSION,
            "is_drift": is_drift,
            "reasons": reasons,
            "previous_state": previous_state,
            "current_payload": new_payload,
        }

        if not is_drift:
            # Only update state when continuity is preserved
            self._state.set_state(domain, new_payload)

        logger.debug(
            "ContinuityEngineV1_2.evaluate domain=%s is_drift=%s reasons=%s",
            domain,
            is_drift,
            reasons,
        )
        return report

    def get_active_state(self, domain: str) -> Dict[str, Any]:
        """
        Return the active continuity state for a domain.
        """
        return self._state.get_state(domain.lower())

    # -------------------------------------------------------------------------
    # Internal drift detection
    # -------------------------------------------------------------------------

    def _detect_drift(
        self,
        previous: Optional[Dict[str, Any]],
        current: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Detect drift between previous and current payloads.

        Rules:
        - If no previous state exists, continuity is considered intact (no drift).
        - Version field (if present) must match v1_2 pattern and previous value.
        - Structural drift: key set changes.
        - Simple content drift: direct value inequality for shared keys.

        Returns:
            (is_drift, reasons)
        """
        reasons: List[str] = []

        if previous is None:
            logger.debug("ContinuityEngineV1_2._detect_drift no previous state; no drift")
            return False, reasons

        # Version check
        prev_version = str(previous.get("version", "")).strip()
        curr_version = str(current.get("version", "")).strip()

        if curr_version and not VERSION_PATTERN.match(curr_version):
            reasons.append(
                f"Current payload version '{curr_version}' does not match v1_2 pattern"
            )

        if prev_version and curr_version and prev_version != curr_version:
            reasons.append(
                f"Version changed from '{prev_version}' to '{curr_version}'"
            )

        # Structural drift: keys
        prev_keys = set(previous.keys())
        curr_keys = set(current.keys())

        added_keys = sorted(curr_keys - prev_keys)
        removed_keys = sorted(prev_keys - curr_keys)

        if added_keys:
            reasons.append(f"Added keys: {', '.join(added_keys)}")
        if removed_keys:
            reasons.append(f"Removed keys: {', '.join(removed_keys)}")

        # Content drift: simple equality check for shared keys
        shared_keys = prev_keys & curr_keys
        for key in sorted(shared_keys):
            if previous.get(key) != current.get(key):
                reasons.append(f"Value changed for key '{key}'")

        is_drift = len(reasons) > 0
        logger.debug(
            "ContinuityEngineV1_2._detect_drift is_drift=%s reasons=%s",
            is_drift,
            reasons,
        )
        return is_drift, reasons


__all__ = ["ContinuityEngineV1_2", "ContinuityEngineV1_2Error"]
