# cnpos/core/automation/module_templates_v1_2.py

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ModuleTemplatesV1_2Error(Exception):
    """Raised when ModuleTemplatesV1_2 cannot render a template."""


class ModuleTemplatesV1_2:
    """
    ModuleTemplatesV1_2

    Deterministic template provider for CNPOS v1_2 modules.

    Responsibilities:
    - Provide strict v1_2-compliant skeletons for new modules.
    - Enforce governance rules (future annotations, logger, error class, naming).
    - Avoid forbidden suffixes (v1.2, v11, v1_1, v12) and legacy imports.
    - Serve as the canonical source for self-writing automation.

    All templates are returned as Python source strings ready to be written
    to disk by the automation pipeline.
    """

    VERSION = "v1_2"

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def get_worker_template(self, *, module_name: str, class_name: str) -> str:
        """
        Return a strict v1_2 worker module template.

        Args:
            module_name: The target module filename (without .py).
            class_name: The main worker class name (must end with 'V1_2').

        Raises:
            ModuleTemplatesV1_2Error: If naming is invalid.
        """
        self._validate_class_suffix(class_name)
        return WORKER_TEMPLATE_V1_2.format(
            module_name=module_name,
            class_name=class_name,
        )

    def get_validator_template(self, *, module_name: str, class_name: str) -> str:
        """
        Return a strict v1_2 validator module template.

        Args:
            module_name: The target module filename (without .py).
            class_name: The main validator class name (must end with 'V1_2').

        Raises:
            ModuleTemplatesV1_2Error: If naming is invalid.
        """
        self._validate_class_suffix(class_name)
        return VALIDATOR_TEMPLATE_V1_2.format(
            module_name=module_name,
            class_name=class_name,
        )

    def get_state_template(self, *, module_name: str, class_name: str) -> str:
        """
        Return a strict v1_2 state module template.

        Args:
            module_name: The target module filename (without .py).
            class_name: The main state class name (must end with 'V1_2').

        Raises:
            ModuleTemplatesV1_2Error: If naming is invalid.
        """
        self._validate_class_suffix(class_name)
        return STATE_TEMPLATE_V1_2.format(
            module_name=module_name,
            class_name=class_name,
        )

    def get_orchestrator_template(self, *, module_name: str, class_name: str) -> str:
        """
        Return a strict v1_2 orchestrator module template.

        Args:
            module_name: The target module filename (without .py).
            class_name: The main orchestrator class name (must end with 'V1_2').

        Raises:
            ModuleTemplatesV1_2Error: If naming is invalid.
        """
        self._validate_class_suffix(class_name)
        return ORCHESTRATOR_TEMPLATE_V1_2.format(
            module_name=module_name,
            class_name=class_name,
        )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _validate_class_suffix(self, class_name: str) -> None:
        """
        Enforce strict v1_2 class naming rules.

        Class names must:
        - End with 'V1_2'.
        - Not contain forbidden suffixes (v1.2, v11, v1_1, v12).
        """
        if not class_name.endswith("V1_2"):
            raise ModuleTemplatesV1_2Error(
                f"class_name '{class_name}' must end with 'V1_2'"
            )

        forbidden = ("v1.2", "v11", "v1_1", "v12")
        lowered = class_name.lower()
        if any(suffix in lowered for suffix in forbidden):
            raise ModuleTemplatesV1_2Error(
                f"class_name '{class_name}' contains forbidden suffix"
            )


# -------------------------------------------------------------------------
# Template definitions (strict v1_2 skeletons)
# -------------------------------------------------------------------------

WORKER_TEMPLATE_V1_2 = """\
# {module_name}.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class {class_name}Error(Exception):
    \\"""Raised when {class_name} encounters an unrecoverable error.\\"""


class {class_name}:
    \\"""Deterministic worker for CNPOS v1_2.

    Responsibilities:
    - Implement a single, well-defined domain task (episode, scene, shot, render, character, code).
    - Use strict v1_2 imports (cnpos.core.*) and avoid legacy 'core.' paths.
    - Expose a clear, typed public API for orchestration and automation.
    \\"""


    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        logger.debug("{class_name} initialized with config=%s", self._config)

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        \\"""Execute the worker task.

        Args:
            payload: Structured input for the worker.

        Returns:
            Dict[str, Any]: Structured result payload.

        Raises:
            {class_name}Error: If the worker cannot complete successfully.
        \\"""
        logger.debug("{class_name}.run called with payload=%s", payload)
        # TODO: implement domain-specific logic here.
        result: Dict[str, Any] = {
            "status": "success",
            "payload": payload,
            "worker": "{class_name}",
        }
        logger.debug("{class_name}.run returning result=%s", result)
        return result


__all__ = ["{class_name}"]
"""

VALIDATOR_TEMPLATE_V1_2 = """\
# {module_name}.py

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class {class_name}Error(Exception):
    \\"""Raised when {class_name} encounters a validation error.\\"""


class {class_name}:
    \\"""Deterministic validator for CNPOS v1_2.

    Responsibilities:
    - Validate payloads against governance, continuity, and mutation rules.
    - Operate as a pure function over structured payloads.
    - Avoid side effects except logging.
    \\"""


    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        \\"""Validate the given payload.

        Args:
            payload: Structured payload to validate.

        Returns:
            Dict[str, Any]: Validation result, including 'valid': bool and 'errors': list.
        \\"""
        logger.debug("{class_name}.validate called with payload=%s", payload)
        # TODO: implement domain-specific validation logic here.
        result: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "validator": "{class_name}",
        }
        logger.debug("{class_name}.validate returning result=%s", result)
        return result


__all__ = ["{class_name}"]
"""

STATE_TEMPLATE_V1_2 = """\
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


__all__ = ["{class_name}"]
"""

ORCHESTRATOR_TEMPLATE_V1_2 = """\
# {module_name}.py

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class {class_name}Error(Exception):
    \\"""Raised when {class_name} encounters an unrecoverable orchestration error.\\"""


class {class_name}:
    \\"""Deterministic orchestrator for CNPOS v1_2.

    Responsibilities:
    - Coordinate one or more workers, validators, and state managers.
    - Emit telemetry events and metrics for orchestration runs.
    - Enforce strict v1_2 governance and naming rules.
    \\"""


    VERSION = "v1_2"
    DOMAIN = "{module_name}"

    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        logger.debug("{class_name} initialized with config=%s", self._config)

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
        # TODO: implement orchestration logic here.
        result: Dict[str, Any] = {
            "status": "success",
            "payload": payload,
            "orchestrator": "{class_name}",
            "version": self.VERSION,
            "domain": self.DOMAIN,
        }
        logger.debug("{class_name}.run returning result=%s", result)
        return result


__all__ = ["{class_name}"]
"""

__all__ = ["ModuleTemplatesV1_2", "ModuleTemplatesV1_2Error"]

