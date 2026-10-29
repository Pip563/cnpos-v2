# cnpos/core/contracts/__init__.py
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Contract file names (v1_2 only)
# ---------------------------------------------------------------------------

EPISODE_CONTRACT_V1_2 = "episode_contract_v1_2.json"
RENDER_CONTRACT_V1_2 = "render_contract_v1_2.json"
SCENE_CONTRACT_V1_2 = "scene_contract_v1_2.json"
SHOT_CONTRACT_V1_2 = "shot_contract_v1_2.json"

__all__ = [
    "EPISODE_CONTRACT_V1_2",
    "RENDER_CONTRACT_V1_2",
    "SCENE_CONTRACT_V1_2",
    "SHOT_CONTRACT_V1_2",
    "load_contract",
]


def _contracts_root() -> Path:
    """
    Resolve the contracts directory for cnpos.core.contracts.

    This uses the module's file location to avoid hard-coded paths and
    keeps compatibility with different installation layouts.
    """
    return Path(__file__).resolve().parent


def load_contract(name: str) -> Dict[str, Any]:
    """
    Load a v1_2 JSON contract by file name.

    Args:
        name: One of the known contract file names, e.g.
              EPISODE_CONTRACT_V1_2, RENDER_CONTRACT_V1_2,
              SCENE_CONTRACT_V1_2, SHOT_CONTRACT_V1_2.

    Returns:
        Parsed JSON contract as a Python dict.

    Raises:
        FileNotFoundError: if the contract file does not exist.
        ValueError: if the contract cannot be parsed as JSON.
    """
    root = _contracts_root()
    path = root / name

    logger.debug("Loading contract file: %s", path)

    if not path.is_file():
        logger.error("Contract file not found: %s", path)
        raise FileNotFoundError(f"Contract file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse contract JSON: %s", path, exc_info=True)
        raise ValueError(f"Invalid JSON in contract file {path}: {exc}") from exc

    logger.debug("Loaded contract '%s' with keys: %s", name, list(data.keys()))
    return data
