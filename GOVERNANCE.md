# Governance

## 1. Purpose and scope

This document defines the decision authority, ownership rules, change controls, validation requirements, and exception process for CNPOS v2. It is the authoritative source for project policy. Architecture documents define the approved system design within that policy; implementation, validators, tests, and runtime evidence do not independently change policy or architecture.

CNPOS is a governance-driven, deterministic, auditable, maintainable, testable, low-drift cinematic narrative planning and orchestration system. The repository is an architecture-first project, not evidence by itself of a complete production media-rendering system. The near-term cinematic product boundary is a validated render-job package. Actual video or audio generation and assembly are outside that boundary unless separately approved and documented.

This policy applies to human contributors and automation, all production modules, contracts, tests, documentation, generated artifacts, and repository changes.

## 2. Decision authority

### 2.1 Project Owner and Architecture Authority

**Pip563 is the sole Project Owner and the Architecture Authority.** These are distinct responsibilities assigned to the same person:

- As Project Owner, Pip563 has final authority over project direction, governance policy, exceptions, and accountability.
- As Architecture Authority, Pip563 has final authority over canonical architecture, boundaries, interfaces, dependencies, and design decisions.

No other person or role is an Architecture Authority unless Pip563 explicitly appoints them in a recorded project decision. Maintainers, reviewers, module owners, validators, tests, and automation may contribute evidence or recommendations, but do not override the Project Owner or Architecture Authority.

Pip563 may delegate a specific review or decision within a stated scope. Delegation must be recorded, must not be inferred from repository activity, and does not transfer final authority over governance or architecture unless the record explicitly says so.

### 2.2 Decision precedence

Applicable legal, security, compliance, and safety obligations take precedence over project decisions. Within those obligations, use this order:

1. Governance policy — what is permitted.
2. Architecture approved by Pip563 — what the system is designed to be.
3. Approved canonical tree, contracts, and recorded decisions — the specific approved structure and interfaces.
4. Validators — automated enforcement of defined rules.
5. Runtime behavior and operational evidence — evidence about actual operation.
6. Tests — evidence about implementation behavior and conformance.

This is a decision hierarchy, not a claim that lower-level evidence is unimportant. Conflicting implementation, test expectations, or runtime workarounds must be investigated and escalated; they do not silently amend policy or architecture. Governance determines what is allowed, and architecture determines the design within governance.

## 3. Project principles and approved baseline

CNPOS development follows these principles:

- Preserve deterministic behavior where the system controls the process; identify nondeterministic external behavior explicitly.
- Keep decisions, changes, approvals, exceptions, and validation evidence traceable.
- Prefer clarity, consistency, and a small explicit interface over stylistic complexity or unnecessary flexibility.
- Keep one canonical implementation, owner, path, public identity, and import for each responsibility.
- Keep contracts and validation at the boundaries between producers and consumers.
- Treat tests as verification evidence, not as architectural authority.
- Expand product capability only after the relevant contracts, execution path, and completion evidence are defined.

The approved production structure is under `cnpos/core/`, organized by the project’s canonical architecture. Tests belong to the separate top-level `tests/` ownership domain. The applicable canonical tree and module registry define approved locations and subsystem ownership. A conflict or missing entry is drift to report and resolve, not permission to invent a new structure.

The current internal architecture baseline is v1_2. The repository/product designation `cnpos-v2` does not itself change that baseline. A version transition requires an explicit, approved, recorded decision and migration plan.

## 4. Roles and ownership

- **Project Owner / Architecture Authority — Pip563:** final policy and architecture decisions; approves governance and architectural changes, project-level exceptions, and unresolved ownership conflicts.
- **Module owner:** accountable for the module’s correctness, contract compliance, documentation, and drift remediation within the approved design. The owner must be identified in the module registry or another approved ownership record. Ownership is not inferred solely from authorship.
- **Reviewer:** provides independent review of correctness, risk, and conformance. Review does not replace required approval.
- **Contributor:** proposes changes, identifies scope and risk, supplies validation evidence, and follows review and approval requirements.
- **Automation:** assists with bounded implementation and validation. It has no authority to define policy, architecture, ownership, or exceptions.

If a module or decision has no recorded owner, or ownership is disputed, pause affected work and refer it to Pip563. A subsystem label in the registry identifies an ownership domain; it is not automatically a named individual.

## 5. Changes and required approvals

Every substantial change must state its scope, affected modules or domains, risk class, required approvals, and validation plan before implementation. Use the following classes:

| Class | Typical scope | Required approval |
|---|---|---|
| SAFE | Documentation, comments, formatting, non-functional clarity changes | Validation appropriate to the change; review when required by the repository workflow |
| MODERATE | Internal refactor or non-breaking quality improvement within an approved boundary | Relevant module owner and human review |
| HIGH_RISK | Execution behavior, state, persistence, public behavior, or contract-adjacent change | Affected module owner and Pip563 before implementation or merge |
| ARCHITECTURAL | Canonical paths/tree, subsystem boundaries, ownership model, dependency strategy, or system design | Pip563 as Architecture Authority |
| BREAKING_CHANGE | Incompatible contract/API behavior or migration affecting consumers | Pip563 as Project Owner and Architecture Authority; migration and compatibility plan required |
| GOVERNANCE | Policy, authority, approval, exception, or enforcement rule | Pip563 as Project Owner; record the decision and update the authoritative policy through the approved repository workflow |

When a change fits multiple classes, use the most restrictive class. An approval must be explicit and traceable; silence, code presence, passing tests, or a merged precedent is not approval. Automation must stop and request human authorization whenever required approval is missing.

## 6. Required change workflow

Changes follow this sequence:

1. **Scope:** identify the requested outcome, affected domain, canonical path, and owner.
2. **Classify:** assign the change class and identify required approvals.
3. **Plan:** define the smallest compliant change, risks, contracts affected, and checks to run.
4. **Approve:** obtain required human approvals before work that requires prior approval.
5. **Implement:** stay within approved scope and do not silently change policy, architecture, contracts, or ownership.
6. **Validate and test:** run applicable governance, architecture, contract, and behavior checks; record commands and results.
7. **Review:** obtain the required human review and resolve findings.
8. **Record:** preserve the decision, approvals, exceptions, and validation evidence in the change or an approved decision record.

Repository changes are proposed through pull requests to `main`; direct pushes to `main` are prohibited by project policy. Required repository checks and reviews must pass before merge. This document states project policy and does not assert that a particular branch-protection setting or automated check is currently configured.

## 7. Contracts, validation, and tests

Contracts define public data and interface expectations. Producers and consumers must use the approved contract; a test fixture or implementation must not redefine it implicitly. Contract changes require the approval appropriate to their risk class and must identify compatibility effects.

Where applicable, validation is performed in this order:

```text
Contract
  ↓
Governance
  ↓
Continuity
  ↓
Mutation
```

A failed required validation blocks acceptance unless an explicit, valid exception applies. Tests verify implementation behavior and must reflect approved contracts and architecture. If a test conflicts with an approved specification, report the discrepancy, establish which artifact is wrong, and obtain approval before changing the specification. Do not alter architecture merely to make a stale test pass.

A change is not complete solely because it compiles, a test passes, or code exists. Completion requires the applicable governance and architecture conformance, ownership, contract, validation, test, documentation, and review evidence.

## 8. Exceptions and emergency operation

Exceptions must be explicit, narrow, justified, attributable, reversible, and time-bound. Each record must identify:

- the reason and risk,
- affected modules or subsystem,
- exact scope and duration or review date,
- approving authority,
- compensating controls and validation evidence,
- and the record where the exception is tracked.

Pip563 approves governance and architecture exceptions. A module owner may approve only a scoped implementation decision delegated to that owner; this cannot override governance, architecture, or a contract. No one may silently bypass a required validator or review gate.

An immediate operational action may be taken to protect people, data, or system continuity. It must be limited to what is necessary, documented promptly, and reviewed by Pip563. An emergency action is temporary operational handling; it does not establish a permanent policy or architecture change.

## 9. Security, safety, and data handling

Legal, security, privacy, compliance, and safety obligations must be respected in design and operation. Changes involving credentials, external services, user data, generated media, or persistent state must document the relevant risks, access boundaries, retention expectations, and failure behavior before those capabilities are treated as production-ready. Secrets must not be committed to the repository. Automation may not be used to bypass these safeguards.

## 10. Drift, records, and enforcement

Drift is a mismatch between the approved policy, architecture, contracts, ownership records, and repository contents. Examples include unregistered production modules, noncanonical paths or identities, conflicting contracts, unowned responsibilities, and tests that encode unapproved behavior.

When drift is found:

1. describe the mismatch and affected scope;
2. assign an owner or escalate missing ownership to Pip563;
3. classify the required remediation;
4. obtain approval if the fix changes architecture, policy, contracts, or ownership;
5. remediate, validate, and record the result.

Do not treat drift as approved merely because it runs or has existed for some time. Until resolved, identify affected work as non-compliant and do not depend on it as an approved capability.

Record material governance and architecture decisions, approvals, exceptions, ownership assignments, and migrations in a traceable repository record or pull request. Enforcement may include blocking or reverting a change, requiring remediation, or suspending automation from the affected scope until compliance is restored.

## 11. Policy maintenance

Pip563 is responsible for maintaining this document. A policy change must be explicit, reviewed, justified, and recorded through the repository’s approved change workflow. A governance edit does not take effect by being proposed or merged without the required Project Owner approval.

Other project documents must remain consistent with this policy. If a document appears to conflict, pause the affected decision and ask Pip563 to resolve it; do not silently select whichever wording is more convenient. Approved decisions should be reflected in the relevant authoritative documents to prevent recurring ambiguity.

## 12. Completion standard

A module or capability is complete only when it:

- has an approved canonical location, owner, and public identity;
- conforms to governance, architecture, and applicable contracts;
- passes applicable validation and tests;
- is documented sufficiently for its intended use;
- has review and approval evidence appropriate to its risk;
- has no unresolved blocking drift; and
- is demonstrated at the level claimed.

For the cinematic MVP, the claimed output is a validated render-job package, not rendered video or audio. A capability must not be described as media production or production-ready until its actual output boundary and evidence support that claim.

---

**Authority statement:** Pip563 is the sole Project Owner and Architecture Authority for CNPOS. Governance defines what is allowed; Pip563’s approved architecture defines the system design within that policy; implementation, tests, and runtime behavior provide evidence and must conform to those decisions.
