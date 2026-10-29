# cnpos/core/automation/state_template_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class StateTemplateV1_2Error(Exception):
    """Raised when StateTemplateV1_2 cannot render a valid state template."""


class StateTemplateV1_2:
    """
    StateTemplateV1_2

    Deterministic state module template provider for CNPOS v1_2.

    Responsibilities:
    - Provide strict v1_2-compliant Python source for new state modules.
    - Enforce governance rules: future annotations, logger, error class, typed API.
    - Avoid forbidden suffixes (v1.2, v11, v1_1, v12) and legacy 'core.' imports.
    - Serve as a canonical building block for self-writing automation.

    The rendered template is a ready-to-write Python module, aligned with the
    cnpos.core.state architecture (continuity, mutation, automation state).
    """

    VERSION = "v1_2"

    def render(self, *, module_name: str, class_name: str) -> str:
        """
        Render a strict v1_2 state module template.

        Args:
            module_name:
                Target module filename (without .py), e.g. 'continuity_state_v1_2'.
            class_name:
                Main state class name, e.g. 'ContinuityStateV1_2'.
                Must end with 'V1_2' and must not contain forbidden suffixes.

        Returns:
            str: Python source code for the state module.

        Raises:
            StateTemplateV1_2Error: If naming is invalid.
        """
        self._validate_class_name(class_name)
        return STATE_TEMPLATE_SOURCE_V1_2.format(
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
            raise StateTemplateV1_2Error(
                f"class_name '{class_name}' must end with 'V1_2'"
            )

        forbidden = ("v1.2", "v11", "v1_1", "v12")
        lowered = class_name.lower()
        if any(suffix in lowered for suffix in forbidden):
            raise StateTemplateV1_2Error(
                f"class_name '{class_name}' contains forbidden suffix"
            )


STATE_TEMPLATE_SOURCE_V1_2 = """\
# {module_name}.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class {class_name}Error(Exception):
    \\"""Raised when {class_name} encounters a state management error.\\"""


class {class_name}:
    \\"""Deterministic state container for CNPOS v1_2.

    Responsibilities:
    - Store and retrieve structured state for a specific domain.
    - Provide a minimal, explicit API for state mutation.
    - Avoid hidden side effects and implicit global state.
    \\"""


    def __init__(self, *, initial_state: Optional[Dict[str, Any]] = None) -> None:
        self._state: Dict[str, Any] = initial_state or {}
        logger.debug("{class_name} initialized with state=%s", self._state)

    def get_state(self) -> Dict[str, Any]:
        \\"""Return a copy of the current state.\\"""
        logger.debug("{class_name}.get_state called")
        return dict(self._state)

    def update_state(self, updates: Dict[str, Any]) -> None:
        \\"""Apply updates to the current state.\\"""
        logger.debug("{class_name}.update_state called with updates=%s", updates)
        self._state.update(updates)
        logger.debug("{class_name}.update_state new state=%s", self._state)


__all__ = ["{class_name}", "{class_name}Error"]
"""

__all__ = ["StateTemplateV1_2", "StateTemplateV1_2Error"]
