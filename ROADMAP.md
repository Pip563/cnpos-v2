# Roadmap

## Purpose

This roadmap sets the order for evolving CNPOS within the policy in [`GOVERNANCE.md`](GOVERNANCE.md). It guides priorities but does not approve architecture, policy, contracts, ownership, or exceptions. Pip563 is the sole Project Owner and Architecture Authority; work requiring those decisions must receive explicit approval and be recorded before implementation.

## Project position and product boundary

CNPOS is an architecture-first cinematic narrative planning and orchestration prototype. It has scaffolding for an Episode → Scene → Shot → Render flow, but repository structure alone does not demonstrate reliable end-to-end execution or a completed production system.

The cinematic MVP output is a **validated render-job package**, not final video/audio. The package is a structured, validated specification for downstream execution. Actual media generation and assembly are post-MVP unless separately approved and planned.

The internal architecture baseline is v1_2. The repository/product name `cnpos-v2` does not itself change that baseline.

## Planning principles

- Resolve foundational ambiguity before broad feature work.
- Preserve the approved canonical architecture and make drift visible rather than normalizing it silently.
- Prefer the smallest demonstrable end-to-end capability over broad, unverified scaffolding.
- Use deterministic local behavior and a fake backend for repeatable tests where external services are unnecessary.
- Keep contracts, validation, ownership, and approval evidence explicit.
- Describe only behavior that has been demonstrated; distinguish plans from completed capabilities.

## Work sequence

### Phase 1: Verify governance and repository baseline — foundational, in progress

- Use `GOVERNANCE.md` as the policy authority and record Pip563 as both Project Owner and Architecture Authority.
- Compare the approved target tree, registry, contracts, and naming/import requirements with the actual checkout.
- Identify conflicts, unowned modules, stale tests, and missing validation commands as findings; do not redesign architecture to make the tree appear compliant.
- Confirm which differences require remediation or an explicit approved decision.

**Exit evidence:** a concise drift inventory with owners or decisions assigned and an approved canonical baseline. This phase is not complete solely because the documents have been edited.

### Phase 2: Deliver one deterministic local cinematic flow — next product milestone

- Define and use the approved pipeline API and compatible worker input/output shapes.
- Provide a deterministic local fake backend for repeatable execution.
- Run an episode request through scenes, shots, render-job assembly, and continuity checks.
- Validate the resulting package against the approved contract and assert its required contents in an integration test.
- Provide a documented runnable example that works from a clean environment.
- Fix only issues needed for this slice; defer unrelated style, mass renaming, or broad refactoring.

**Exit evidence:** a fresh checkout can run the documented example and integration test reproducibly, producing the agreed validated render-job package.

### Phase 3: Stabilize contracts and continuity

- Define required fields, identifiers, ordering, parent-child relationships, and lifecycle rules for Episode, Scene, Shot, and Render-job artifacts.
- Establish validation behavior and ensure invalid outputs do not advance to later stages.
- Define continuity state scope, reset, persistence, and recovery expectations for the MVP; do not claim durable storage unless implemented and tested.
- Add focused positive, negative, and repeat-run determinism tests.

**Exit evidence:** stage contracts and continuity behavior are documented, enforced, and tested against the vertical slice.

### Phase 4: Harden validation and delivery

- Add or refine architecture, registry, contract, and governance drift checks where approved.
- Add CI for supported Python versions and agreed checks only after confirming the commands and dependencies work locally.
- Document setup, real commands, backend boundaries, validation evidence, and known limitations.
- Record approvals, exceptions, and release evidence in the approved workflow.

**Exit evidence:** required checks run automatically where configured, setup is reproducible, and a release claim is supported by review and validation evidence.

### Phase 5: Consider an execution/rendering bridge — post-MVP decision

Only after the render-job package boundary is demonstrated, decide whether to build a separate execution worker for actual media output. Any backend integration must define asset references, submission, progress/status, failure/retry behavior, output verification, provenance, resource/security requirements, and approval boundaries before implementation.

**Exit evidence:** an explicit approved product decision and a successful example at the chosen output boundary. Do not claim video production when the system only emits a render specification.

## Priority order

```text
Verify baseline
  → Demonstrate local package-producing flow
  → Stabilize contracts and continuity
  → Add validation and delivery automation
  → Decide whether to implement actual media execution
```

## Risks and controls

| Risk | Control |
|---|---|
| Architecture and tree drift | Compare against approved documents; record mismatches and resolve through Pip563 rather than silently changing the target |
| Stale or incompatible tests | Verify against approved APIs/contracts; tests provide evidence but do not override architecture |
| External backend dependency | Use a deterministic local fake backend for the MVP; document external dependencies if later approved |
| Scope creep into media generation | Keep the MVP at validated render-job package output; decide on a separate execution bridge later |
| Over-complexity | Favor a single tested vertical slice and defer unrelated refactoring or stylistic cleanup |
| Unsupported readiness claims | State actual status and attach reproducible validation evidence to completion claims |

## Success criteria

The near-term roadmap succeeds when:

- governance authority and decision paths are explicit;
- approved structure, registry, and actual repository state have a documented reconciliation plan;
- a clean environment can reproducibly produce and validate a render-job package from an episode request;
- contracts, continuity checks, and tests provide evidence for that flow;
- required checks and operational claims are documented and verified rather than assumed.

CNPOS should be described as a **governance-driven cinematic orchestration prototype** until the end-to-end package workflow is demonstrated. A validated package is not final media.
