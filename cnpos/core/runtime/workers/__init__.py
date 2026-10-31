# cnpos/core/runtime/backend_manager_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class BackendManagerV1_2Error(Exception):
    """Raised when BackendManagerV1_2 cannot execute or route a task."""


class BackendManagerV1_2:
    """Deterministic backend manager for CNPOS v1_2."""

    VERSION = "v1_2"
    DEFAULT_BACKEND_KEY = "default"

    def __init__(self) -> None:
        self._backends: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        logger.debug("BackendManagerV1_2 initialized with zero registered backends.")

    def register_backend(
        self,
        key: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        if not callable(handler):
            raise BackendManagerV1_2Error("Backend handler must be callable.")
        self._backends[key] = handler
        logger.debug("Backend registered key=%s total_backends=%d", key, len(self._backends))

    def unregister_backend(self, key: str) -> None:
        if key not in self._backends:
            raise BackendManagerV1_2Error(f"Unknown backend key '{key}'.")
        del self._backends[key]
        logger.debug("Backend unregistered key=%s total_backends=%d", key, len(self._backends))

    def execute(self, task: Dict[str, Any], backend_key: Optional[str] = None) -> Dict[str, Any]:
        key = backend_key or self.DEFAULT_BACKEND_KEY
        handler = self._backends.get(key)

        if handler is None:
            raise BackendManagerV1_2Error(f"Unknown backend key '{key}'.")

        try:
            result = handler(task)
            if not isinstance(result, dict):
                raise BackendManagerV1_2Error(f"Backend '{key}' returned a non-dict response.")
            return result
        except BackendManagerV1_2Error:
            raise
        except Exception as exc:
            raise BackendManagerV1_2Error(f"Backend '{key}' failed: {exc}") from exc

    def route(
        self,
        *,
        domain: str,
        phase: str,
        payload: Dict[str, Any],
        backend_key: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        task = {
            "domain": domain,
            "phase": phase,
            "task_type": task_type,
            "payload": payload,
        }
        return self.execute(task=task, backend_key=backend_key)

    def run_task(
        self,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None,
        backend_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        task = {
            "prompt": prompt,
            "parameters": parameters or {},
            "domain": "runtime",
            "phase": "TASK",
        }
        return self.execute(task=task, backend_key=backend_key)


LLMBackendManagerV1_2 = BackendManagerV1_2

__all__ = [
    "BackendManagerV1_2",
    "BackendManagerV1_2Error",
]
