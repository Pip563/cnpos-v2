# cnpos/core/automation/registry_scanner_v1_2.py

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from cnpos.core.automation.governance_loader_v1_2 import (
    AutomationLoaderV1_2,
    AutomationLoaderV1_2Error,
)

logger = logging.getLogger(__name__)


class RegistryScannerV1_2Error(Exception):
    """
    Raised when RegistryScannerV1_2 encounters an unrecoverable error.
    """
    pass


class RegistryScannerV1_2:
    """
    RegistryScannerV1_2

    Deterministic automation discovery component for CNPOS v1_2.

    Responsibilities:
    - Scan the CNPOS source tree.
    - Discover valid v1_2 modules.
    - Detect legacy naming drift.
    - Detect forbidden version suffixes.
    - Detect unregistered modules.
    - Build a normalized registry payload.
    - Provide deterministic output for automation planners,
      reviewers, testers, and orchestrators.

    This scanner performs discovery only.
    It does not mutate source files.
    """

    VERSION = "v1_2"
    DOMAIN = "automation"

    DEFAULT_SCAN_DIRECTORIES = (
        "automation",
        "governance",
        "runtime",
        "runtime/workers",
        "state",
        "validators",
        "orchestrators",
        "agents",
    )

    def __init__(
        self,
        automation_loader: Optional[AutomationLoaderV1_2] = None,
        root_path: Optional[Path] = None,
    ) -> None:
        self._loader = automation_loader or AutomationLoaderV1_2()
        self._root_path = root_path or (Path("cnpos") / "core")

        logger.debug(
            "RegistryScannerV1_2 initialized root_path=%s",
            self._root_path,
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def scan_registry(self) -> Dict[str, Any]:
        """
        Scan the CNPOS v1_2 tree and return a normalized registry.

        Returns:
            Dict[str, Any]
        """

        governance_spec = self._load_governance_spec()

        discovered_modules = self._discover_modules(
            governance_spec=governance_spec,
        )

        report = {
            "version": self.VERSION,
            "domain": self.DOMAIN,
            "root_path": str(self._root_path),
            "module_count": len(discovered_modules),
            "modules": discovered_modules,
            "violations": self._collect_violations(
                discovered_modules=discovered_modules,
                governance_spec=governance_spec,
            ),
        }

        logger.info(
            "RegistryScannerV1_2 discovered %d modules",
            report["module_count"],
        )

        return report

    def list_module_paths(self) -> List[str]:
        """
        Return discovered module paths.
        """

        registry = self.scan_registry()

        return sorted(
            module["module_path"]
            for module in registry["modules"]
        )

    def module_exists(
        self,
        module_name: str,
    ) -> bool:
        """
        Determine whether a module exists in the registry.
        """

        module_name = module_name.strip()

        registry = self.scan_registry()

        return any(
            module["module_name"] == module_name
            for module in registry["modules"]
        )

    # ------------------------------------------------------------------
    # GOVERNANCE
    # ------------------------------------------------------------------

    def _load_governance_spec(self) -> Dict[str, Any]:
        """
        Load governance specification.
        """

        try:
            return self._loader.load_governance_spec()

        except AutomationLoaderV1_2Error as exc:
            logger.error(
                "RegistryScannerV1_2 failed loading governance spec: %s",
                exc,
                exc_info=True,
            )
            raise RegistryScannerV1_2Error(str(exc)) from exc

    # ------------------------------------------------------------------
    # DISCOVERY
    # ------------------------------------------------------------------

    def _discover_modules(
        self,
        *,
        governance_spec: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Discover valid modules.
        """

        discovered_modules: List[Dict[str, Any]] = []

        required_suffix = (
            governance_spec.get("naming", {})
            .get("module_suffix", "_v1_2.py")
        )

        scan_directories = [
            self._root_path / directory
            for directory in self.DEFAULT_SCAN_DIRECTORIES
        ]

        seen_paths: Set[str] = set()

        for directory in scan_directories:
            if not directory.exists():
                continue

            for file_path in sorted(directory.rglob("*.py")):

                relative_path = str(
                   
