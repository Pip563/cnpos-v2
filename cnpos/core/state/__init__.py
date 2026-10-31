# cnpos/core/state/mutation_state_manager_v1_2.py
from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MutationStateManagerV1_2Error(Exception):
    """Raised when MutationStateManagerV1_2 encounters an unrecoverable error."""


class MutationStateManagerV1_2:
    """Dedicated mutation state manager for CNPOS v1_2."""

    def __init__(self) -> None:
        self._mutation_log: List[Dict[str, Any]] = []
        self._story_mutations: List[Dict[str, Any]] = []
        self._character_mutations: List[Dict[str, Any]] = []
        self._code_mutations: List[Dict[str, Any]] = []
        self._rollback_points: Dict[str, Dict[str, Any]] = {}
        logger.debug("MutationStateManagerV1_2 initialized.")

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
        self._mutation_log.append(entry)
        if domain == "story":
            self._story_mutations.append(entry)
        elif domain == "character":
            self._character_mutations.append(entry)
        elif domain == "code":
            self._code_mutations.append(entry)
        return mutation_id

    def compute_diff(
        self,
        *,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> Dict[str, Any]:
        diff: Dict[str, Any] = {"added": {}, "removed": {}, "changed": {}}
        for key in after.keys() - before.keys():
            diff["added"][key] = after[key]
        for key in before.keys() - after.keys():
            diff["removed"][key] = before[key]
        for key in before.keys() & after.keys():
            if before[key] != after[key]:
                diff["changed"][key] = {"old": before[key], "new": after[key]}
        return diff

    def create_rollback_point(self, label: str, state_snapshot: Dict[str, Any]) -> None:
        self._rollback_points[label] = state_snapshot

    def rollback_to(self, label: str) -> Optional[Dict[str, Any]]:
        return self._rollback_points.get(label)

    def get_mutation_timeline(self, domain: str) -> List[Dict[str, Any]]:
        if domain == "story":
            return list(self._story_mutations)
        if domain == "character":
            return list(self._character_mutations)
        if domain == "code":
            return list(self._code_mutations)
        return []

    def get_global_mutation_log(self) -> List[Dict[str, Any]]:
        return list(self._mutation_log)

    def find_mutation(self, mutation_id: str) -> Optional[Dict[str, Any]]:
        for entry in self._mutation_log:
            if entry.get("mutation_id") == mutation_id:
                return entry
        return None

    def last_mutation(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if domain is None:
            return self._mutation_log[-1] if self._mutation_log else None
        timeline = self.get_mutation_timeline(domain)
        return timeline[-1] if timeline else None


__all__ = ["MutationStateManagerV1_2", "MutationStateManagerV1_2Error"]
