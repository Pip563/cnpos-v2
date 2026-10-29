# cnpos/core/state/mutation_state_manager_v1_2.py

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MutationStateManagerV1_2Error(Exception):
    """Raised when MutationStateManagerV1_2 encounters an unrecoverable error."""
    pass


class MutationStateManagerV1_2:
    """
    MutationStateManagerV1_2

    Dedicated mutation state manager for CNPOS v1_2.

    Responsibilities:
    - Track all mutations applied to the system.
    - Provide mutation history per domain.
    - Provide mutation diffs (old → new).
    - Provide rollback snapshots.
    - Provide mutation timelines for continuity + governance.
    - Integrate with orchestrator + validator pipeline.

    All payloads are plain dicts; no legacy versions (v11, v1_1, v1.2 dotted, v12)
    are involved. This module is deterministic and side-effect free beyond its
    internal state containers.
    """

    def __init__(self) -> None:
        # Global mutation log (chronological)
        self._mutation_log: List[Dict[str, Any]] = []

        # Domain-specific mutation timelines
        self._story_mutations: List[Dict[str, Any]] = []
        self._character_mutations: List[Dict[str, Any]] = []
        self._code_mutations: List[Dict[str, Any]] = []

        # Rollback snapshots
        self._rollback_points: Dict[str, Dict[str, Any]] = {}

        logger.debug("MutationStateManagerV1_2 initialized.")

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def record_mutation(
        self,
        *,
        domain: str,
        mutation_type: str,
        payload: Dict[str, Any],
        active_state_snapshot: Dict[str, Any],
        impact_summary: Dict[str, Any],
        risk_level: str,
    ) -> str:
        """
        Record a mutation event and return its mutation_id.

        Args:
            domain: Logical domain ("story", "character", "code", etc.).
            mutation_type: High-level mutation type identifier.
            payload: Mutation payload (diff, metadata, etc.).
            active_state_snapshot: State before mutation is applied.
            impact_summary: Structured summary of mutation impact.
            risk_level: Risk level ("low", "medium", "high", "critical").

        Returns:
            str: Generated mutation_id.
        """
        mutation_id = str(uuid.uuid4())
        timestamp = time.time()

        entry: Dict[str, Any] = {
            "mutation_id": mutation_id,
            "timestamp": timestamp,
            "domain": domain,
            "mutation_type": mutation_type,
            "payload": payload,
            "impact_summary": impact_summary,
            "risk_level": risk_level,
            "state_before": active_state_snapshot,
        }

        # Global log
        self._mutation_log.append(entry)

        # Domain timeline
        if domain == "story":
            self._story_mutations.append(entry)
        elif domain == "character":
            self._character_mutations.append(entry)
        elif domain == "code":
            self._code_mutations.append(entry)

        logger.debug(
            "MutationStateManagerV1_2 recorded mutation_id=%s domain=%s type=%s risk=%s",
            mutation_id,
            domain,
            mutation_type,
            risk_level,
        )

        return mutation_id

    # ----------------------------------------------------------------------
    # DIFF ENGINE
    # ----------------------------------------------------------------------

    def compute_diff(
        self,
        *,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compute a simple diff between two state snapshots.

        Returns:
            Dict[str, Any]: {
                "added": Dict[str, Any],
                "removed": Dict[str, Any],
                "changed": Dict[str, Dict[str, Any]],
            }
        """
        diff: Dict[str, Any] = {
            "added": {},
            "removed": {},
            "changed": {},
        }

        # Added keys
        for key in after.keys() - before.keys():
            diff["added"][key] = after[key]

        # Removed keys
        for key in before.keys() - after.keys():
            diff["removed"][key] = before[key]

        # Changed keys
        for key in before.keys() & after.keys():
            if before[key] != after[key]:
                diff["changed"][key] = {
                    "old": before[key],
                    "new": after[key],
                }

        logger.debug(
            "MutationStateManagerV1_2 computed diff: added=%d removed=%d changed=%d",
            len(diff["added"]),
            len(diff["removed"]),
            len(diff["changed"]),
        )

        return diff

    # ----------------------------------------------------------------------
    # ROLLBACK SUPPORT
    # ----------------------------------------------------------------------

    def create_rollback_point(self, label: str, state_snapshot: Dict[str, Any]) -> None:
        """
        Create a rollback snapshot with a human-readable label.

        Args:
            label: Identifier for the rollback point.
            state_snapshot: State snapshot to store.
        """
        self._rollback_points[label] = state_snapshot
        logger.debug(
            "MutationStateManagerV1_2 created rollback point label=%s", label
        )

    def rollback_to(self, label: str) -> Optional[Dict[str, Any]]:
        """
        Return the rollback snapshot for orchestrator to restore.

        Args:
            label: Identifier for the rollback point.

        Returns:
            Optional[Dict[str, Any]]: Stored snapshot or None.
        """
        snapshot = self._rollback_points.get(label)
        logger.debug(
            "MutationStateManagerV1_2 rollback_to label=%s found=%s",
            label,
            snapshot is not None,
        )
        return snapshot

    # ----------------------------------------------------------------------
    # TIMELINE ACCESSORS
    # ----------------------------------------------------------------------

    def get_mutation_timeline(self, domain: str) -> List[Dict[str, Any]]:
        """
        Return the mutation timeline for a given domain.

        Args:
            domain: "story" | "character" | "code".

        Returns:
            List[Dict[str, Any]]: Timeline entries.
        """
        if domain == "story":
            return list(self._story_mutations)
        if domain == "character":
            return list(self._character_mutations)
        if domain == "code":
            return list(self._code_mutations)
        return []

    def get_global_mutation_log(self) -> List[Dict[str, Any]]:
        """
        Return the global mutation log.

        Returns:
            List[Dict[str, Any]]: All mutation entries.
        """
        return list(self._mutation_log)

    # ----------------------------------------------------------------------
    # QUERY UTILITIES
    # ----------------------------------------------------------------------

    def find_mutation(self, mutation_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a mutation entry by its mutation_id.

        Args:
            mutation_id: Identifier of the mutation.

        Returns:
            Optional[Dict[str, Any]]: Matching entry or None.
        """
        for entry in self._mutation_log:
            if entry.get("mutation_id") == mutation_id:
                return entry
        return None

    def last_mutation(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return the last mutation entry, optionally scoped by domain.

        Args:
            domain: Optional domain filter ("story", "character", "code").

        Returns:
            Optional[Dict[str, Any]]: Last entry or None.
        """
        if domain is None:
            return self._mutation_log[-1] if self._mutation_log else None

        timeline = self.get_mutation_timeline(domain)
        return timeline[-1] if timeline else None
