# cnpos/core/runtime/workers/worker_registry_v1_2.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from cnpos.core.runtime.workers.episode_worker_v1_2 import EpisodeWorkerV1_2
from cnpos.core.runtime.workers.scene_worker_v1_2 import SceneWorkerV1_2
from cnpos.core.runtime.workers.shot_worker_v1_2 import ShotWorkerV1_2
from cnpos.core.runtime.workers.render_worker_v1_2 import RenderWorkerV1_2
from cnpos.core.runtime.workers.prompt_worker_v1_2 import PromptWorkerV1_2

logger = logging.getLogger(__name__)


class WorkerRegistryV1_2Error(Exception):
    """Raised when WorkerRegistryV1_2 encounters an unrecoverable error."""
    pass


from dataclasses import dataclass
from typing import Any, Type


@dataclass(frozen=True)
class WorkerDescriptorV1_2:
    """
    Immutable descriptor for a v1_2 worker.
    """

    name: str
    cls: Type[Any]
    domain: str
    version: str = "v1_2"

class WorkerRegistryV1_2:
    """
    WorkerRegistryV1_2

    Deterministic registry for runtime workers in CNPOS v1_2.

    Responsibilities:
    - Maintain a mapping from worker name to worker class/descriptor.
    - Provide lookup helpers for orchestrators and pipelines.
    - Ensure only v1_2-compliant workers are registered.
    """

    def __init__(self) -> None:
        self._workers: Dict[str, WorkerDescriptorV1_2] = {}
        self._bootstrap_default_workers()
        logger.debug(
            "WorkerRegistryV1_2 initialized with workers=%s",
            list(self._workers.keys()),
        )

    # -------------------------------------------------------------------------
    # Bootstrap
    # -------------------------------------------------------------------------

    def _bootstrap_default_workers(self) -> None:
        """
        Register the default v1_2 workers.
        """
        self.register_worker(
            name="episode_worker_v1_2",
            cls=EpisodeWorkerV1_2,
            domain=EpisodeWorkerV1_2.DOMAIN,
        )
        self.register_worker(
            name="scene_worker_v1_2",
            cls=SceneWorkerV1_2,
            domain=SceneWorkerV1_2.DOMAIN,
        )
        self.register_worker(
            name="shot_worker_v1_2",
            cls=ShotWorkerV1_2,
            domain=ShotWorkerV1_2.DOMAIN,
        )
        self.register_worker(
            name="render_worker_v1_2",
            cls=RenderWorkerV1_2,
            domain=RenderWorkerV1_2.DOMAIN,
        )
        self.register_worker(
            name="prompt_worker_v1_2",
            cls=PromptWorkerV1_2,
            domain=PromptWorkerV1_2.DOMAIN,
        )

    # -------------------------------------------------------------------------
    # Registration API
    # -------------------------------------------------------------------------

    def register_worker(
        self,
        name: str,
        cls: Type[Any],
        domain: str,
    ) -> None:
        """
        Register a worker class.

        Args:
            name: Unique worker name (should include `_v1_2` suffix).
            cls: Worker class.
            domain: Logical domain (episode, scene, shot, render, prompt).

        Raises:
            WorkerRegistryV1_2Error if name is invalid or already registered.
        """
        if not name.endswith("_v1_2"):
            logger.error(
                "WorkerRegistryV1_2.register_worker name without v1_2 suffix: %s",
                name,
            )
            raise WorkerRegistryV1_2Error(
                "Worker name must end with '_v1_2' to be v1_2-compliant"
            )

        if name in self._workers:
            logger.error(
                "WorkerRegistryV1_2.register_worker duplicate name: %s",
                name,
            )
            raise WorkerRegistryV1_2Error(f"Worker '{name}' is already registered")

        descriptor = WorkerDescriptorV1_2(
            name=name,
            cls=cls,
            domain=domain,
        )
        self._workers[name] = descriptor

        logger.debug(
            "WorkerRegistryV1_2.register_worker registered name=%s domain=%s",
            name,
            domain,
        )

    # -------------------------------------------------------------------------
    # Lookup API
    # -------------------------------------------------------------------------

    def get_worker_descriptor(self, name: str) -> WorkerDescriptorV1_2:
        """
        Retrieve a worker descriptor by name.

        Raises:
            WorkerRegistryV1_2Error if worker is unknown.
        """
        descriptor = self._workers.get(name)
        if descriptor is None:
            logger.error(
                "WorkerRegistryV1_2.get_worker_descriptor unknown worker: %s",
                name,
            )
            raise WorkerRegistryV1_2Error(f"Unknown worker '{name}'")
        return descriptor

    def create_worker_instance(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Instantiate a worker by name.

        Args:
            name: Registered worker name.
            **kwargs: Extra keyword arguments passed to the worker constructor.

        Returns:
            Instantiated worker object.

        Raises:
            WorkerRegistryV1_2Error if worker is unknown or instantiation fails.
        """
        descriptor = self.get_worker_descriptor(name)
        try:
            instance = descriptor.cls(**kwargs)
            logger.debug(
                "WorkerRegistryV1_2.create_worker_instance name=%s instance=%s",
                name,
                instance,
            )
            return instance
        except Exception as exc:
            logger.error(
                "WorkerRegistryV1_2.create_worker_instance error for '%s': %s",
                name,
                exc,
                exc_info=True,
            )
            raise WorkerRegistryV1_2Error(
                f"Failed to instantiate worker '{name}': {exc}"
            ) from exc

    def list_workers(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered workers.

        Returns:
            Dict[name, { 'domain': str, 'version': str }]
        """
        summary: Dict[str, Dict[str, Any]] = {
            name: {
                "domain": descriptor.domain,
                "version": descriptor.version,
            }
            for name, descriptor in self._workers.items()
        }
        logger.debug(
            "WorkerRegistryV1_2.list_workers summary=%s",
            summary,
        )
        return summary


__all__ = ["WorkerRegistryV1_2", "WorkerRegistryV1_2Error", "WorkerDescriptorV1_2"]
