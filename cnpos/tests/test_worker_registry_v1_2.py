# tests/test_worker_registry_v1_2.py

from __future__ import annotations

import logging
import pytest

from cnpos.core.runtime.workers.worker_registry_v1_2 import (
    WorkerRegistryV1_2,
    WorkerRegistryV1_2Error,
    WorkerEntry,
)

from cnpos.core.runtime.workers.episode_worker_v1_2 import EpisodeWorkerV1_2
from cnpos.core.runtime.workers.scene_worker_v1_2 import SceneWorkerV1_2
from cnpos.core.runtime.workers.shot_worker_v1_2 import ShotWorkerV1_2
from cnpos.core.runtime.workers.render_worker_v1_2 import RenderWorkerV1_2

logger = logging.getLogger(__name__)


def test_worker_registry_v1_2_initialization() -> None:
    """
    Ensure WorkerRegistryV1_2 initializes deterministically with the exact
    v1_2 worker mapping defined in the architecture.
    """
    registry = WorkerRegistryV1_2()

    assert isinstance(registry._registry, dict)
    assert set(registry._registry.keys()) == {
        "EPISODE_V1_2",
        "SCENE_V1_2",
        "SHOT_V1_2",
        "RENDER_V1_2",
    }

    # All entries must be WorkerEntry instances
    for entry in registry._registry.values():
        assert isinstance(entry, WorkerEntry)


def test_worker_registry_v1_2_resolve_valid_workers() -> None:
    """
    Ensure resolve() returns the correct worker class for each supported
    v1_2 cinematic phase.
    """
    registry = WorkerRegistryV1_2()

    assert registry.resolve("EPISODE_V1_2") is EpisodeWorkerV1_2
    assert registry.resolve("SCENE_V1_2") is SceneWorkerV1_2
    assert registry.resolve("SHOT_V1_2") is ShotWorkerV1_2
    assert registry.resolve("RENDER_V1_2") is RenderWorkerV1_2


def test_worker_registry_v1_2_resolve_invalid_phase() -> None:
    """
    Ensure resolve() raises WorkerRegistryV1_2Error for unknown phases.
    """
    registry = WorkerRegistryV1_2()

    with pytest.raises(WorkerRegistryV1_2Error):
        registry.resolve("UNKNOWN_PHASE")


def test_worker_registry_v1_2_instantiate_valid_workers() -> None:
    """
    Ensure instantiate() returns an instance of the correct worker class.
    """
    registry = WorkerRegistryV1_2()

    assert isinstance(registry.instantiate("EPISODE_V1_2"), EpisodeWorkerV1_2)
    assert isinstance(registry.instantiate("SCENE_V1_2"), SceneWorkerV1_2)
    assert isinstance(registry.instantiate("SHOT_V1_2"), ShotWorkerV1_2)
    assert isinstance(registry.instantiate("RENDER_V1_2"), RenderWorkerV1_2)


def test_worker_registry_v1_2_instantiate_invalid_phase() -> None:
    """
    Ensure instantiate() raises WorkerRegistryV1_2Error for unknown phases.
    """
    registry = WorkerRegistryV1_2()

    with pytest.raises(WorkerRegistryV1_2Error):
        registry.instantiate("INVALID_V1_2")


def test_worker_registry_v1_2_entries_are_immutable() -> None:
    """
    Ensure WorkerEntry dataclass is frozen (immutable), preventing accidental
    mutation of registry metadata.
    """
    registry = WorkerRegistryV1_2()
    entry = registry._registry["EPISODE_V1_2"]

    with pytest.raises(Exception):
        entry.name = "SHOULD_NOT_MUTATE"


def test_worker_registry_v1_2_logging_on_error(caplog: pytest.LogCaptureFixture) -> None:
    """
    Ensure resolve() logs an error when an unknown phase is requested.
    """
    registry = WorkerRegistryV1_2()

    with pytest.raises(WorkerRegistryV1_2Error):
        registry.resolve("BAD_PHASE")

    assert any("unknown phase" in msg.lower() for msg in caplog.messages)
