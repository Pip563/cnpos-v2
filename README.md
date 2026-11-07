# CNPOS v2

## Cinematic Narrative Planning and Orchestration System

CNPOS is a governance-driven project for cinematic narrative planning, orchestration, continuity, validation, and controlled automation. It prioritizes deterministic behavior where controllable, clear contracts, traceable decisions, maintainability, and low architectural drift.

**Current status:** CNPOS is an architecture-first prototype, not a completed cinematic production system. The repository contains scaffolding for an Episode → Scene → Shot → Render flow, but the existence of components does not establish a reliable end-to-end workflow or actual media production.

**MVP boundary:** the intended cinematic MVP produces a validated render-job package. It does not generate or assemble final video or audio. A render-job package is a structured, validated specification for downstream execution; it must not be described as rendered media.

## Authority and source of truth

[`GOVERNANCE.md`](GOVERNANCE.md) is the authoritative policy document. **Pip563 is the sole Project Owner and Architecture Authority.** Governance defines what is allowed; architecture approved by Pip563 defines the system design within that policy.

The approved architecture, canonical tree, contracts, and module registry define intended structure and interfaces. Implementation, tests, and runtime behavior provide evidence and must conform to approved decisions; they do not silently redefine them. Raise conflicts and unresolved ownership to Pip563 rather than inventing an exception.

## Architectural principles

- One canonical implementation, owner, path, public identity, and import per responsibility.
- Production modules belong under `cnpos/core/` in the approved subsystem structure.
- Tests are a separate ownership domain at the repository-level `tests/` path.
- Contracts define interfaces between producers, validators, workers, and orchestrators.
- Validation and human review are required according to change risk.
- Decisions, approvals, exceptions, and validation evidence must be traceable.
- Prefer clarity and small explicit interfaces over stylistic complexity or unnecessary flexibility.

The internal architecture baseline is **v1_2**. The repository name `cnpos-v2` does not itself change that baseline. See [`MODULE_REGISTRY.md`](MODULE_REGISTRY.md) for registered modules and subsystem boundaries.

## Intended subsystem structure

```text
cnpos/core/
├── agents/
├── automation/
├── contracts/
├── governance/
├── orchestrators/
├── runtime/
├── state/
└── validators/

tests/
```

This is the approved target structure, not a claim that the current checkout fully conforms. The current repository contains tests under `cnpos/tests/`, among other items that may need reconciliation. Such differences are architectural drift to assess and resolve under `GOVERNANCE.md`; do not move or rename files solely to make this README appear accurate.

## Cinematic workflow boundary

The intended orchestration sequence is:

```text
Episode
  ↓
Scene
  ↓
Shot
  ↓
Render job
```

The contract domains are Episode, Scene, Shot, and Render. In the MVP, the Render stage means creating and validating a render-job package. A downstream renderer or media-generation service is outside this boundary unless separately approved and documented.

A successful end-to-end path, configured production backend, and demonstrated render-job package remain implementation evidence to establish. Do not infer completion from the presence of workers, contracts, or an orchestrator.

## Validation and tests

Where applicable, validation follows this sequence:

```text
Contract
  ↓
Governance
  ↓
Continuity
  ↓
Mutation
```

Tests verify behavior and conformance; they are not architectural authority. When tests conflict with approved governance, architecture, or contracts, identify and resolve the discrepancy through the decision process in [`GOVERNANCE.md`](GOVERNANCE.md).

Use the checks actually configured in the checkout. Do not assume that a documented command or workflow exists or passes unless it has been run and its result recorded.

## Development and decisions

Before substantial work:

1. Identify the requested outcome, affected modules, canonical path, and owner.
2. Classify the change and identify required approvals.
3. Obtain approval before architectural, governance, contract, or other high-risk work as required by `GOVERNANCE.md`.
4. Implement the smallest change that meets the approved scope.
5. Run relevant validation and tests, then record results and review evidence.

Automation may assist with implementation and validation but cannot define policy, architecture, ownership, or exceptions. See [`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md) and [`AUTOMATION.md`](AUTOMATION.md).

## Project documents

- [`GOVERNANCE.md`](GOVERNANCE.md) — authority, policy, approvals, exceptions, and completion criteria.
- [`MODULE_REGISTRY.md`](MODULE_REGISTRY.md) — registered modules and subsystem ownership domains.
- [`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md) — change and review workflow.
- [`AUTOMATION.md`](AUTOMATION.md) — boundaries for automation.
- [`ROADMAP.md`](ROADMAP.md) — planned evolution and project priorities.

This README is the project-level overview and architecture summary. Where it conflicts with governance or an approved architecture decision, follow the authoritative source and update this summary through the approved workflow.
