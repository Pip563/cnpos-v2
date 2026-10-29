from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional


logger = logging.getLogger(__name__)


class BackendManagerV1_2Error(Exception):
    """
    Raised when BackendManagerV1_2 cannot execute or route a task.
    """


class BackendManagerV1_2:
    """
    Deterministic backend manager for CNPOS v1_2.

    Responsibilities:
    - Register backend handlers.
    - Route tasks to registered backends.
    - Provide a stable runtime interface for workers and agents.
    - Maintain strict v1_2 compatibility.
    """

    VERSION = "v1_2"

    DEFAULT_BACKEND_KEY = "default"

    def __init__(self) -> None:
        self._backends: Dict[
            str,
            Callable[[Dict[str, Any]], Dict[str, Any]]
        ] = {}

        logger.debug(
            "LLMBackendManagerV1_2 initialized with zero registered backends."
        )

    # ------------------------------------------------------------------
    # Backend registration
    # ------------------------------------------------------------------

    def register_backend(
        self,
        key: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        """
        Register a backend handler.

        Args:
            key:
                Backend identifier.

            handler:
                Callable accepting a task payload and returning a result payload.
        """
        if not callable(handler):
            raise BackendManagerV1_2Error(
                "Backend handler must be callable."
            )

        self._backends[key] = handler

        logger.debug(
            "Backend registered key=%s total_backends=%d",
            key,
            len(self._backends),
        )

    def unregister_backend(self, key: str) -> None:
        """
        Remove a backend registration.
        """
        if key not in self._backends:
            raise BackendManagerV1_2Error(
                f"Unknown backend key '{key}'."
            )

        del self._backends[key]

        logger.debug(
            "Backend unregistered key=%s total_backends=%d",
            key,
            len(self._backends),
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        task: Dict[str, Any],
        backend_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task using the selected backend.
        """
        key = backend_key or self.DEFAULT_BACKEND_KEY

        handler = self._backends.get(key)

        if handler is None:
            raise BackendManagerV1_2Error(
                f"Unknown backend key '{key}'."
            )

        try:
            result = handler(task)

            if not isinstance(result, dict):
                raise BackendManagerV1_2Error(
                    f"Backend '{key}' returned a non-dict response."
                )

            return result

        except BackendManagerV1_2Error:
            raise

        except Exception as exc:
            raise BackendManagerV1_2Error(
                f"Backend '{key}' failed: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Runtime compatibility helpers
    # ------------------------------------------------------------------

    def route(
        self,
        *,
        domain: str,
        phase: str,
        payload: Dict[str, Any],
        backend_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route a structured task.

        This method exists because several v1_2 workers and tests
        expect a public route() interface.
        """
        task = {
            "domain": domain,
            "phase": phase,
            "payload": payload,
        }

        return self.execute(
            task=task,
            backend_key=backend_key,
        )

    def run_task(
        self,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None,
        backend_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convenience helper for prompt-driven operations.
        """
        task = {
            "prompt": prompt,
            "parameters": parameters or {},
        }

        return self.execute(
            task=task,
            backend_key=backend_key,
        )

