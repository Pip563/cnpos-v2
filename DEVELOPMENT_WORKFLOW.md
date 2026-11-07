# Development Workflow

## Purpose

This document describes how to propose, implement, verify, review, and record changes to CNPOS. It is subordinate to [`GOVERNANCE.md`](GOVERNANCE.md), which defines project authority and binding policy.

**Pip563 is the sole Project Owner and Architecture Authority.** Governance defines what is allowed; architecture approved by Pip563 defines the design within that policy. Contributors, reviewers, tests, runtime behavior, and automation provide input or evidence; they do not silently change governance or architecture.

CNPOS is an architecture-first prototype. The cinematic MVP output is a validated render-job package, not actual video or audio. Work must stay within the approved scope and must not claim a higher completion level than demonstrated.

## Repository baseline

The approved production domain is `cnpos/core/`, organized by the approved subsystem architecture. The approved test ownership domain is top-level `tests/`. The current checkout contains tests under `cnpos/tests/` and other potential differences from documented naming and registry rules. Treat these as observed drift requiring assessment—not as proof that the target architecture changed. Do not move or rename files solely to align appearances; obtain approval when remediation changes paths, ownership, or architecture.

Use `MODULE_REGISTRY.md` and approved architecture to identify canonical identities and ownership. If the owner or canonical identity is missing or disputed, pause that portion of work and refer it to Pip563. Do not infer an individual owner from a subsystem label, commit history, or directory.

## Change procedure

For substantial work, follow these steps:

1. **Define the outcome:** state the user-visible or system behavior to change and what is out of scope.
2. **Inspect the baseline:** identify affected files, contracts, ownership, current repository drift, and checks actually available.
3. **Classify risk:** use the classes and approval requirements in `GOVERNANCE.md`. Apply the most restrictive applicable class.
4. **Plan minimally:** state the smallest change that satisfies the request, its compatibility impact, and its validation plan.
5. **Obtain prior approval:** get explicit Pip563 approval before architectural or governance changes, breaking changes, and other work requiring prior approval. Record it in the change or decision record.
6. **Implement within scope:** preserve approved boundaries and avoid unrelated style or naming changes.
7. **Validate and test:** run relevant checks that exist. Record exact commands and outcomes; disclose missing or unavailable checks.
8. **Review and resolve:** obtain required human review, address findings, and revalidate affected behavior.
9. **Record completion:** include the scope, affected modules, risk class, approvals, exceptions, checks, and evidence supporting the completion claim.

For small documentation-only changes, keep the same principles proportionate: identify the authoritative policy, make only the requested edits, and avoid accidental policy or architecture changes.

## Change classes

| Class | Examples | Approval route |
|---|---|---|
| SAFE | Comments, formatting, non-functional clarity, documentation that does not change policy | Appropriate validation and review for the change |
| MODERATE | Internal refactor or quality improvement within an approved boundary | Relevant module owner and human review |
| HIGH_RISK | Execution behavior, state, persistence, public behavior, or contract-adjacent work | Affected module owner and Pip563 approval as required by governance |
| ARCHITECTURAL | Canonical paths/tree, subsystem boundaries, ownership model, dependency strategy, system design | Pip563 as Architecture Authority; obtain approval before implementation |
| BREAKING_CHANGE | Incompatible interface behavior or consumer migration | Pip563 approval and a compatibility/migration plan |
| GOVERNANCE | Policy, authority, exception, or enforcement rules | Explicit Pip563 approval and recorded decision |

Automation may help plan, implement, and verify approved changes, but cannot provide required human approval or modify policy/architecture on its own. See `AUTOMATION.md`.

## Validation and test expectations

Where applicable, the project validation order is:

```text
Contract → Governance → Continuity ��� Mutation
```

Run relevant checks and tests that are actually configured. Do not claim that `pytest`, a CLI command, CI, branch protection, or any other check is passing or configured unless verified for the current checkout. When a needed check is absent, identify that as a gap and document the alternative verification, if any.

Tests verify implementation behavior and conformance; they do not define the approved architecture. If code, tests, or fixtures conflict with governance, architecture, or contracts, document the discrepancy and route it to Pip563. Do not alter architecture merely to satisfy stale tests. Required validation failures block acceptance unless a valid exception is explicitly approved and recorded.

## Review and repository changes

Repository changes should be proposed through pull requests to `main`, consistent with the governance policy. Direct pushes to `main` are prohibited by project policy. These statements describe the required process and do not assert that the current GitHub branch-protection configuration has been checked.

A change proposal should include:

- concise intent and scope;
- affected modules, contracts, or ownership domains;
- mutation class and required approvals;
- compatibility or migration impact;
- validation commands and results, including unavailable checks;
- review evidence and any approved exception.

Reviewers assess correctness, risk, conformance, unnecessary scope, ownership, and evidence. Review does not replace an approval reserved for Pip563 or a module owner.

## Definition of done

A change is done only when it conforms to approved governance, architecture, paths, ownership, and contracts; passes applicable validation and tests; has the required review and approval evidence; is documented for its intended use; and has no unresolved blocking drift. Claims must be limited to what has actually been demonstrated.

For the cinematic MVP, the completion target is a reproducible example producing a validated render-job package. It is not a rendered video/audio deliverable.

## Related documents

- `GOVERNANCE.md` — binding authority and policy.
- `README.md` — project overview and architecture summary.
- `AUTOMATION.md` — automation boundaries.
- `MODULE_REGISTRY.md` — registered identities and ownership domains.
- `ROADMAP.md` — priorities and milestones.
