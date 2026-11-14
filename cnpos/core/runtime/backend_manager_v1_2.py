from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class BackendManagerV1_2Error(Exception):
    """Raised when a backend cannot be resolved or execute a task."""


class BackendManagerV1_2:
    """Small deterministic router for registered CNPOS v1_2 backends."""

    VERSION = "v1_2"
    DEFAULT_BACKEND_KEY = "default"

    def __init__(self) -> None:
        self._backends: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register_backend(self, key: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        if not key or not callable(handler):
            raise BackendManagerV1_2Error("A non-empty key and callable handler are required.")
        self._backends[key] = handler

    def unregister_backend(self, key: str) -> None:
        try:
            del self._backends[key]
        except KeyError as exc:
            raise BackendManagerV1_2Error(f"Unknown backend key '{key}'.") from exc

    def execute(self, task: Dict[str, Any], backend_key: Optional[str] = None) -> Dict[str, Any]:
        key = backend_key or self.DEFAULT_BACKEND_KEY
        handler = self._backends.get(key)
        if handler is None:
            raise BackendManagerV1_2Error(f"Unknown backend key '{key}'.")
        try:
            result = handler(task)
        except Exception as exc:
            raise BackendManagerV1_2Error(f"Backend '{key}' failed: {exc}") from exc
        if not isinstance(result, dict):
            raise BackendManagerV1_2Error(f"Backend '{key}' returned a non-dict response.")
        return result

    def route(
        self,
        *,
        payload: Dict[str, Any],
        domain: str = "runtime",
        phase: str = "TASK",
        backend_key: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        task = {"domain": domain, "phase": phase, "task_type": task_type, "payload": payload}
        return self.execute(task, backend_key=backend_key)

    def run_task(
        self,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None,
        backend_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        task = {"prompt": prompt, "parameters": parameters or {}, "domain": "runtime", "phase": "TASK"}
        return self.execute(task, backend_key=backend_key)


__all__ = ["BackendManagerV1_2", "BackendManagerV1_2Error"]
