# Automation

## Purpose and authority

Automation is a bounded subsystem that assists with planning, code generation, documentation, validation, and repair. It exists to improve speed without weakening CNPOS governance, architecture, safety, or traceability. Automation is not an authority and must not treat a successful run as approval.

[`GOVERNANCE.md`](GOVERNANCE.md) is the authoritative policy. Pip563 is the sole Project Owner and Architecture Authority. Automation must follow Pip563’s approved architecture and must stop when a decision or approval reserved for Pip563 is missing. This document describes operating rules subordinate to governance; it cannot grant authority or alter approved policy.

CNPOS is an architecture-first prototype. For the cinematic MVP, the intended terminal output is a validated render-job package, not rendered video or audio. Automation must not claim that a package constitutes media generation or production readiness.

## Permitted work

Within approved scope and applicable change controls, automation may:

- inspect the repository and report structure, ownership, contract, and policy drift;
- plan a bounded change and classify its risk;
- scaffold or modify implementation within approved paths and interfaces;
- create or update tests to verify approved behavior;
- make low-risk documentation, formatting, and clarity changes;
- run available validation and tests, reporting exact commands and results;
- prepare reviewable changes and remediation proposals.

Generated code, plans, tests, and reports are proposals until they pass required validation and human review. Automation must distinguish observed repository state from approved target architecture.

## Prohibited work without approval

Automation must not independently:

- define or modify governance policy;
- make or silently infer an architecture decision;
- change canonical paths, subsystem boundaries, ownership, dependency strategy, or public contracts;
- delete or replace modules, or create aliases, compatibility wrappers, duplicate implementations, or parallel sources of truth;
- bypass a required validator, test, review, or approval;
- treat existing code, a passing test, historical precedent, or a successful generation as approval;
- commit secrets or evade security, privacy, safety, or compliance controls.

When a requested task crosses these boundaries, automation must stop before making the governed change, state the decision needed, and request explicit authorization from Pip563. It may provide a proposal for review without presenting it as approved.

## Architecture and repository drift

The approved production domain is under `cnpos/core/`, with the separate top-level `tests/` ownership domain. Canonical subsystem structure, naming, imports, and module identities are governed by approved architecture and the module registry. These are target rules, not a claim that every current file conforms or that automated enforcement exists.

The repository currently contains discrepancies from the documented target, including tests under `cnpos/tests/` and files whose names do not follow the documented version pattern. Automation must report these as observed drift and must not relocate, rename, delete, or bless them without the approvals required by `GOVERNANCE.md`.

The one-responsibility discipline is:

```text
One canonical implementation
One accountable owner
One canonical path
One public identity
One canonical import
```

A registry subsystem label is an ownership domain, not a named individual. If a module lacks an explicit accountable owner, flag it for Pip563 rather than infer an owner from authorship or directory location.

## Automation lifecycle

For substantial work, use this bounded lifecycle:

```text
SCAN → PLAN → APPROVAL → WRITE → VALIDATE → TEST → REVIEW → RECORD
```

- **SCAN:** establish the requested scope, repository state, applicable policy, canonical target, and known drift.
- **PLAN:** propose the smallest change, classify risk, identify affected interfaces, and list checks.
- **APPROVAL:** obtain the explicit human authorization required by governance before restricted work.
- **WRITE:** implement only the approved scope.
- **VALIDATE / TEST:** run applicable checks that exist; record commands, results, and any unavailable checks without claiming success.
- **REVIEW:** obtain the required human review and resolve findings.
- **RECORD:** preserve intent, scope, approvals, exceptions, and evidence in the change or approved decision record.

Do not imply that a stage or tool is configured in the repository unless verified. If an applicable check is absent, report the gap; do not invent a passing result.

## Change classes and approvals

Use the classifications in `GOVERNANCE.md`; when a change fits multiple classes, use the most restrictive. In brief:

- **SAFE:** non-functional clarity, formatting, and documentation work; validate appropriately.
- **MODERATE:** internal non-breaking changes within an approved boundary; human review is required.
- **HIGH_RISK:** execution, state, persistence, public behavior, or contract-adjacent changes; affected module owner and Pip563 approval are required as specified in governance.
- **ARCHITECTURAL:** tree, paths, boundaries, ownership, dependencies, or design changes; Pip563’s prior approval is required.
- **BREAKING_CHANGE:** incompatible interfaces or migrations; Pip563’s approval and a compatibility/migration plan are required.
- **GOVERNANCE:** policy or authority changes; explicit Pip563 approval is required.

Automation may not approve its own changes. Approval must be explicit and traceable; silence and merge history do not count.

## Validation and completion

Where applicable, the project validation order is:

```text
Contract → Governance → Continuity → Mutation
```

A failure in a required check blocks acceptance unless a narrowly scoped, time-bound, recorded exception is approved under `GOVERNANCE.md`. Tests verify behavior and conformance; they do not define architecture. If tests disagree with approved policy or architecture, report the mismatch and request a decision rather than changing the specification to satisfy tests.

A module or capability is complete only to the level supported by its ownership, approved location and identity, contract conformance, validation, tests, documentation, review, and evidence. For the cinematic MVP, completion requires demonstrating a validated render-job package. It does not imply actual video/audio output.

## Security and auditability

Automation must protect credentials and sensitive data, minimize access, and document relevant external services, persistence, and generated artifacts. Outputs affecting governed resources must be attributable and reviewable. Record the scope, risk class, affected files or interfaces, approvals, validation evidence, and exceptions. Stop and escalate when authority, ownership, or a required safety decision is unclear.

## Related policy

- `GOVERNANCE.md` — authoritative authority, policy, approvals, and exception rules.
- `DEVELOPMENT_WORKFLOW.md` — human and automation change workflow.
- `MODULE_REGISTRY.md` — registered modules and ownership domains.
- `ROADMAP.md` — project sequencing and intended product scope.
