# cnpos/core/automation/rewriter_agent_v1_2.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cnpos.core.automation.state_manager_v1_2 import (
    AutomationStateManagerV1_2,
    AutomationStateManagerV1_2Error,
)
from cnpos.core.automation.governance_loader_v1_2 import (
    GovernanceLoaderV1_2,
    GovernanceLoaderV1_2Error,
)
from cnpos.core.runtime.backend_manager_v1_2 import (
    BackendManagerV1_2,
)
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
    ValidatorPipelineV1_2Error,
)
from cnpos.core.state.mutation_state_manager_v1_2 import (
    MutationStateManagerV1_2,
    MutationStateManagerV1_2Error,
)

logger = logging.getLogger(__name__)


class AutomationRewriterAgentV1_2Error(Exception):
    """Raised when AutomationRewriterAgentV1_2 encounters an unrecoverable error."""
    pass


class AutomationRewriterAgentV1_2:
    """
    AutomationRewriterAgentV1_2

    Deterministic rewriter agent for the CNPOS automation subsystem v1_2.

    Responsibilities:
    - Take failed or drifted automation modules and attempt deterministic rewrites.
    - Use governance automation loader to obtain strict v1_2 constraints.
    - Use LLMBackendManagerV1_2 to generate revised code under governance rules.
    - Record rewrite cycles and outcomes in AutomationStateManagerV1_2.
    - Optionally record mutation metadata in MutationStateManagerV1_2.
    - Validate rewritten modules via ValidatorPipelineV1_2 before marking success.
    """

    VERSION = "v1_2"

    def __init__(
        self,
        automation_state_manager: Optional[AutomationStateManagerV1_2] = None,
        governance_loader: Optional[GovernanceAutomationLoaderV1_2] = None,
        backend_manager: Optional[BackendManagerV1_2] = None,
        mutation_state_manager: Optional[MutationStateManagerV1_2] = None,
        ) -> None:
        self._state = automation_state_manager or AutomationStateManagerV1_2()
        self._governance_loader = governance_loader or GovernanceAutomationLoaderV1_2()
        self._backend_manager = backend_manager or BackendManagerV1_2()
        self._validator_pipeline = validator_pipeline or ValidatorPipelineV1_2()
        self._mutation_state = mutation_state_manager or MutationStateManagerV1_2()

        logger.debug(
            "AutomationRewriterAgentV1_2 initialized state_manager=%s governance_loader=%s "
            "backend_manager=%s validator_pipeline=%s mutation_state_manager=%s",
            self._state,
            self._governance_loader,
            self._backend,
            self._validator_pipeline,
            self._mutation_state,
        )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def rewrite_module(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        module_type: str,
        code: str,
        issues: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Attempt a deterministic rewrite of a generated module.

        Args:
            automation_id: Automation identifier associated with the module.
            module_path: Path of the generated module.
            domain: Logical domain (episode, scene, shot, render, character, code, automation).
            module_type: Logical type ('worker', 'validator', 'state', 'orchestrator', 'automation').
            code: Current module code as text.
            issues: Optional list of issues detected by previous stages.

        Returns:
            Dict[str, Any]: Rewrite report:
                - 'automation_id'
                - 'version'
                - 'module_path'
                - 'domain'
                - 'module_type'
                - 'cycle_id'
                - 'success'
                - 'issues'
                - 'code'
                - 'validator_metadata'
        """
        issues = issues or []
        logger.info(
            "AutomationRewriterAgentV1_2.rewrite_module invoked id=%s path=%s domain=%s type=%s",
            automation_id,
            module_path,
            domain,
            module_type,
        )

        # Load governance spec for constraints
        try:
            governance_spec = self._governance_loader.load_governance_spec()
        except GovernanceAutomationLoaderV1_2Error as exc:
            logger.error(
                "AutomationRewriterAgentV1_2 failed to load governance spec: %s",
                exc,
                exc_info=True,
            )
            raise AutomationRewriterAgentV1_2Error(str(exc)) from exc

        # Record rewrite cycle start
        try:
            cycle_id = self._state.record_rewrite_cycle(
                module_path=module_path,
                domain=domain,
                cycle_index=self._next_cycle_index(automation_id=automation_id, domain=domain),
                success=False,
                reasons=issues,
            )
        except AutomationStateManagerV1_2Error as exc:
            logger.error(
                "AutomationRewriterAgentV1_2 failed to record rewrite cycle start: %s",
                exc,
                exc_info=True,
            )
            raise AutomationRewriterAgentV1_2Error(str(exc)) from exc

        # Build rewrite prompt
        prompt = self._build_rewrite_prompt(
            module_path=module_path,
            domain=domain,
            module_type=module_type,
            code=code,
            issues=issues,
            governance_spec=governance_spec,
        )

        # Generate rewritten code
        try:
            rewritten_code = self._backend.generate_code(
                prompt=prompt,
                context={
                    "domain": domain,
                    "module_type": module_type,
                    "automation_id": automation_id,
                    "cycle_id": cycle_id,
                    "phase": "REWRITE",
                    "version": self.VERSION,
                },
            )
        except BackendManagerV1_2Error as exc:
            logger.error(
                "AutomationRewriterAgentV1_2 backend rewrite failed: %s",
                exc,
                exc_info=True,
            )
            self._record_failure(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                module_type=module_type,
                cycle_id=cycle_id,
                reason=f"backend_manager: {exc}",
            )
            raise AutomationRewriterAgentV1_2Error(str(exc)) from exc

        # Validate rewritten code
        try:
            validated_payload = self._validator_pipeline.validate(
                domain="automation",
                payload={
                    "automation_id": automation_id,
                    "module_path": module_path,
                    "domain": domain,
                    "module_type": module_type,
                    "code": rewritten_code,
                },
                contract_schema=None,
                governance_loader=None,
                context={"state_key": f"automation_rewrite::{automation_id}::{cycle_id}"},
            )
            validator_metadata = validated_payload.get("_validator_v1_2", {})
            success = True
        except ValidatorPipelineV1_2Error as exc:
            logger.error(
                "AutomationRewriterAgentV1_2 validator pipeline failed on rewritten code: %s",
                exc,
                exc_info=True,
            )
            validator_metadata = {}
            success = False
            issues.append(f"validator_pipeline: {exc}")

        # Record mutation metadata
        try:
            self._mutation_state.record_mutation(
                domain=domain,
                mutation_type="automation_rewrite",
                payload={
                    "automation_id": automation_id,
                    "cycle_id": cycle_id,
                    "module_path": module_path,
                    "module_type": module_type,
                    "success": success,
                    "issues": issues,
                },
            )
        except MutationStateManagerV1_2Error as exc:
            logger.warning(
                "AutomationRewriterAgentV1_2 failed to record mutation in MutationStateManagerV1_2: %s",
                exc,
                exc_info=True,
            )

        # Record final outcome in state manager
        try:
            self._state.record_rewrite_cycle(
                module_path=module_path,
                domain=domain,
                cycle_index=self._next_cycle_index(automation_id=automation_id, domain=domain),
                success=success,
                reasons=issues,
            )
            self._state.register_generated_module(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                success=success,
                metadata={
                    "module_type": module_type,
                    "cycle_id": cycle_id,
                    "issues": issues,
                    "rewriter": "AutomationRewriterAgentV1_2",
                    "length": len(rewritten_code),
                },
            )
        except AutomationStateManagerV1_2Error as exc:
            logger.error(
                "AutomationRewriterAgentV1_2 failed to record final rewrite outcome: %s",
                exc,
                exc_info=True,
            )
            raise AutomationRewriterAgentV1_2Error(str(exc)) from exc

        report: Dict[str, Any] = {
            "automation_id": automation_id,
            "version": self.VERSION,
            "module_path": module_path,
            "domain": domain,
            "module_type": module_type,
            "cycle_id": cycle_id,
            "success": success,
            "issues": issues,
            "code": rewritten_code,
            "validator_metadata": validator_metadata,
        }

        logger.debug(
            "AutomationRewriterAgentV1_2.rewrite_module completed id=%s cycle_id=%s success=%s issues=%d",
            automation_id,
            cycle_id,
            success,
            len(issues),
        )
        return report

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _next_cycle_index(self, *, automation_id: str, domain: str) -> int:
        """
        Compute the next rewrite cycle index for a given automation_id/domain.
        """
        cycles = self._state.list_rewrite_cycles(domain=domain)
        relevant = [c for c in cycles if c.get("automation_id") == automation_id]
        if not relevant:
            return 0
        return max(c.get("cycle_index", 0) for c in relevant) + 1

    def _build_rewrite_prompt(
        self,
        *,
        module_path: str,
        domain: str,
        module_type: str,
        code: str,
        issues: List[str],
        governance_spec: Dict[str, Any],
    ) -> str:
        """
        Build a deterministic rewrite prompt for the backend manager.

        Encodes:
        - Current code and known issues.
        - v1_2 naming/import/structure constraints.
        - Governance rules for drift and mutation.
        """
        naming = governance_spec.get("naming", {})
        imports = governance_spec.get("imports", {})
        structure = governance_spec.get("structure", {})
        drift_cfg = governance_spec.get("drift", {})
        mutation_cfg = governance_spec.get("mutation", {})

        lines = [
            "You are the CNPOS v1_2 automation rewriter.",
            f"Module path: {module_path}",
            f"Domain: {domain}",
            f"Module type: {module_type}",
            "",
            "Current code:",
            code,
            "",
            "Known issues:",
            "\n".join(issues) if issues else "None explicitly listed.",
            "",
            "Governance constraints:",
            f"- Required module suffix: {naming.get('module_suffix', '_v1_2.py')}",
            f"- Forbidden suffixes: {', '.join(naming.get('forbidden_suffixes', []))}",
            f"- Allowed import prefix: {imports.get('allowed_prefix', 'cnpos.core.')}",
            f"- Required import suffix: {imports.get('required_suffix', '_v1_2')}",
            f"- Requires __future__ annotations: {structure.get('requires_future_annotations', True)}",
            f"- Requires logger: {structure.get('requires_logger', True)}",
            f"- Requires error class: {structure.get('requires_error_class', True)}",
            f"- Forbid drift: {drift_cfg.get('forbid_drift', True)}",
            f"- Track all mutations: {mutation_cfg.get('track_all_mutations', True)}",
            "",
            "Rewrite instructions:",
            "- Produce a full, deterministic v1_2 module.",
            "- Do not use legacy versions (v11, v1.1, v1.2, v12).",
            "- Ensure imports use 'cnpos.core.' and end with '_v1_2' where applicable.",
            "- Preserve architectural intent but fix structural, naming, and governance issues.",
            "- Return only the rewritten module code as plain text.",
        ]

        return "\n".join(lines)

    def _record_failure(
        self,
        *,
        automation_id: str,
        module_path: str,
        domain: str,
        module_type: str,
        cycle_id: str,
        reason: str,
    ) -> None:
        """
        Record a rewrite failure in the state manager.
        """
        try:
            self._state.register_generated_module(
                automation_id=automation_id,
                module_path=module_path,
                domain=domain,
                success=False,
                metadata={
                    "module_type": module_type,
                    "cycle_id": cycle_id,
                    "reason": reason,
                    "rewriter": "AutomationRewriterAgentV1_2",
                },
            )
        except AutomationStateManagerV1_2Error as exc:
            logger.error(
                "AutomationRewriterAgentV1_2._record_failure failed to record in state manager: %s",
                exc,
                exc_info=True,
            )


__all__ = ["AutomationRewriterAgentV1_2", "AutomationRewriterAgentV1_2Error"]
