from __future__ import annotations

import copy
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MutationStateManagerV1_2Error(Exception):
    """Raised when mutation state cannot be recorded or recovered."""


class MutationStateManagerV1_2:
    """In-memory mutation log, timelines, diffs, and rollback snapshots."""

    def __init__(self) -> None:
        self._mutation_log: List[Dict[str, Any]] = []
        self._rollback_points: Dict[str, Dict[str, Any]] = {}

    def record_mutation(
        self,
        mutation: Optional[Dict[str, Any]] = None,
        *,
        domain: Optional[str] = None,
        mutation_type: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        active_state_snapshot: Optional[Dict[str, Any]] = None,
        impact_summary: Optional[Dict[str, Any]] = None,
        risk_level: Optional[str] = None,
    ) -> str:
        """Record either a mutation event dict or the explicit keyword API."""
        if mutation is not None and not isinstance(mutation, dict):
            raise MutationStateManagerV1_2Error("Mutation must be a dictionary.")
        event = copy.deepcopy(mutation or {})
        event_domain = domain or event.get("domain", "unknown")
        event_type = mutation_type or event.get("mutation_type", "STATE_CHANGE")
        event_payload = payload if payload is not None else event
        state_before = active_state_snapshot if active_state_snapshot is not None else event.get("state_before", {})
        impact = impact_summary if impact_summary is not None else event.get("impact_summary", {})
        risk = risk_level or event.get("risk_level", "low")
        mutation_id = str(event.get("mutation_id") or uuid.uuid4())
        entry = {
            **event,
            "mutation_id": mutation_id,
            "timestamp": event.get("timestamp", time.time()),
            "domain": event_domain,
            "mutation_type": event_type,
            "payload": copy.deepcopy(event_payload),
            "impact_summary": copy.deepcopy(impact),
            "risk_level": risk,
            "state_before": copy.deepcopy(state_before),
        }
        self._mutation_log.append(entry)
        logger.debug("Recorded mutation %s in domain %s", mutation_id, event_domain)
        return mutation_id

    def compute_diff(self, *, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(before, dict) or not isinstance(after, dict):
            raise MutationStateManagerV1_2Error("Diff inputs must be dictionaries.")
        return {
            "added": {key: copy.deepcopy(after[key]) for key in after.keys() - before.keys()},
            "removed": {key: copy.deepcopy(before[key]) for key in before.keys() - after.keys()},
            "changed": {
                key: {"old": copy.deepcopy(before[key]), "new": copy.deepcopy(after[key])}
                for key in before.keys() & after.keys()
                if before[key] != after[key]
            },
        }

    def create_rollback_point(self, label: str, state_snapshot: Dict[str, Any]) -> None:
        if not label or not isinstance(state_snapshot, dict):
            raise MutationStateManagerV1_2Error("A label and dictionary snapshot are required.")
        self._rollback_points[label] = copy.deepcopy(state_snapshot)

    def rollback_to(self, label: str) -> Optional[Dict[str, Any]]:
        snapshot = self._rollback_points.get(label)
        return copy.deepcopy(snapshot) if snapshot is not None else None

    def get_mutation_timeline(self, domain: str) -> List[Dict[str, Any]]:
        return [copy.deepcopy(entry) for entry in self._mutation_log if entry.get("domain") == domain]

    def get_global_mutation_log(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self._mutation_log)

    def find_mutation(self, mutation_id: str) -> Optional[Dict[str, Any]]:
        for entry in self._mutation_log:
            if entry.get("mutation_id") == mutation_id:
                return copy.deepcopy(entry)
        return None

    def last_mutation(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        timeline = self._mutation_log if domain is None else [e for e in self._mutation_log if e.get("domain") == domain]
        return copy.deepcopy(timeline[-1]) if timeline else None


__all__ = ["MutationStateManagerV1_2", "MutationStateManagerV1_2Error"]
