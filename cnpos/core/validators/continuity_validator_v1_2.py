# cnpos/core/validators/continuity_validator_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cnpos.core.governance.governance_loader_v1_2 import GovernanceLoaderV1_2
from cnpos.core.runtime.continuity_engine_v1_2 import (
    ContinuityEngineV1_2,
    ContinuityEngineV1_2Error,
)
from cnpos.core.state.continuity_state_v1_2 import ContinuityStateV1_2

logger = logging.getLogger(__name__)


class ContinuityValidatorV1_2Error(Exception):
    """Raised when ContinuityValidatorV1_2 encounters an unrecoverable error."""
    pass


class ContinuityValidatorV1_2:
    """
    ContinuityValidatorV1_2

    Deterministic continuity validator for CNPOS v1_2.

    Responsibilities:
    - Compare new payloads against active continuity state.
    - Use ContinuityEngineV1_2 to detect drift and continuity violations.
    - Apply governance constraints via GovernanceLoaderV1_2 when required.
    - Produce structured continuity reports for the validator pipeline.

    Domain‑agnostic: works for episode, scene, shot, render, character, and code
    domains, as long as a continuity state snapshot is provided.
    """

    VERSION = "v1_2"

    def __init__(
        self,
        continuity_engine: Optional[ContinuityEngineV1_2] = None,
        governance_loader: Optional[GovernanceLoaderV1_2] = None,
        continuity_state: Optional[ContinuityStateV1_2] = None,
    ) -> None:
        self._continuity_engine = continuity_engine or ContinuityEngineV1_2()
        self._governance_loader = governance_loader or GovernanceLoaderV1_2()
        self._continuity_state = continuity_state or ContinuityStateV1_2()

        logger.debug(
            "ContinuityValidatorV1_2 initialized engine=%s governance_loader=%s continuity_state=%s",
            self._continuity_engine,
            self._governance_loader,
            self._continuity_state,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def validate(
        self,
        *,
        domain: str,
        payload: Dict[str, Any],
        state_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate continuity for a given domain payload.

        Args:
            domain: Logical domain (episode, scene, shot, render, character, code).
            payload: New payload to validate.
            state_key: Optional key to retrieve a specific continuity slice.
            context: Optional orchestration context.

        Returns:
            Dict[str, Any]: Continuity report:
                - 'domain'
                - 'version'
                - 'state_key'
                - 'is_continuous'
                - 'drift_level'
                - 'violations'
                - 'previous_state'
                - 'current_payload'
        """
        context = context or {}
        logger.info(
            "ContinuityValidatorV1_2.validate invoked domain=%s state_key=%s",
            domain,
            state_key,
        )

        try:
            previous_state = self._get_previous_state(domain=domain, state_key=state_key)
            report = self._run_continuity_engine(
                domain=domain,
                previous_state=previous_state,
                current_payload=payload,
                context=context,
            )

            # Optionally persist updated continuity state when continuous
            if report.get("is_continuous", False):
                self._update_continuity_state(
                    domain=domain,
                    state_key=state_key,
                    payload=payload,
                )

            logger.debug(
                "ContinuityValidatorV1_2.validate completed domain=%s state_key=%s is_continuous=%s drift_level=%s",
                domain,
                state_key,
                report.get("is_continuous"),
                report.get("drift_level"),
            )
            return report

        except (ContinuityEngineV1_2Error, ContinuityValidatorV1_2Error) as exc:
            logger.error(
                "ContinuityValidatorV1_2 controlled failure: %s",
                exc,
                exc_info=True,
            )
            raise ContinuityValidatorV1_2Error(str(exc)) from exc
        except Exception as exc:
            logger.error(
                "ContinuityValidatorV1_2 unexpected failure: %s",
                exc,
                exc_info=True,
            )
            raise ContinuityValidatorV1_2Error(
                f"Unexpected error in ContinuityValidatorV1_2.validate: {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _get_previous_state(
        self,
        *,
        domain: str,
        state_key: Optional[str],
    ) -> Dict[str, Any]:
        """
        Retrieve previous continuity state for the given domain/state_key.
        """
        previous_state = self._continuity_state.get_state(domain=domain, key=state_key)
        logger.debug(
            "ContinuityValidatorV1_2._get_previous_state domain=%s state_key=%s has_state=%s",
            domain,
            state_key,
            previous_state is not None,
        )
        return previous_state or {}

    def _update_continuity_state(
        self,
        *,
        domain: str,
        state_key: Optional[str],
        payload: Dict[str, Any],
    ) -> None:
        """
        Persist updated continuity state after a successful continuity check.
        """
        self._continuity_state.set_state(domain=domain, key=state_key, state=payload)
        logger.debug(
            "ContinuityValidatorV1_2._update_continuity_state domain=%s state_key=%s",
            domain,
            state_key,
        )

    def _run_continuity_engine(
        self,
        *,
        domain: str,
        previous_state: Dict[str, Any],
        current_payload: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Delegate continuity evaluation to ContinuityEngineV1_2.

        Returns:
            Dict[str, Any]: Engine continuity report normalized for validator use.
        """
        logger.debug(
            "ContinuityValidatorV1_2._run_continuity_engine domain=%s prev_keys=%d curr_keys=%d",
            domain,
            len(previous_state.keys()),
            len(current_payload.keys()),
        )

        engine_report = self._continuity_engine.evaluate_continuity(
            domain=domain,
            previous_state=previous_state,
            current_payload=current_payload,
            governance_loader=self._governance_loader,
            context=context,
        )

        # Normalize engine report to a stable validator schema
        normalized: Dict[str, Any] = {
            "domain": domain,
            "version": self.VERSION,
            "state_key": context.get("state_key"),
            "is_continuous": bool(engine_report.get("is_continuous", True)),
            "drift_level": engine_report.get("drift_level", "none"),
            "violations": engine_report.get("violations", []),
            "previous_state": previous_state,
            "current_payload": current_payload,
        }

        logger.debug(
            "ContinuityValidatorV1_2._run_continuity_engine normalized is_continuous=%s drift_level=%s violations_count=%d",
            normalized["is_continuous"],
            normalized["drift_level"],
            len(normalized["violations"]),
        )
        return normalized


__all__ = ["ContinuityValidatorV1_2", "ContinuityValidatorV1_2Error"]
