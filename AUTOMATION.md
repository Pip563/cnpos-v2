# Automation

## 1. Purpose

This document defines the governance, scope, and operating boundaries of automation within CNPOS. It is subordinate to the authoritative governance and architecture documents, but it provides the operational policy for automation-assisted generation, maintenance, validation, and repair.

Automation is an official architectural subsystem, not an ungoverned shortcut. It exists to support deterministic, auditable, low-drift development while preserving governance, architecture, ownership, and validation rules.

---

## 2. Governing Principle

The project follows this precedence:

1. Legal, security, compliance, and safety obligations
2. Governance policy
3. Architecture authority
4. Canonical tree and canonical contracts
5. Validators and enforcement rules
6. Runtime operational realities
7. Test results

This means automation must never outrank governance or architecture. Automation is a tool for implementing approved policy, not a source of policy.

The decisive rule is:

> Architecture is the source of truth.

Automation must serve architecture, not redefine it.

---

## 3. Automation Role in the System

The automation subsystem is responsible for:

- planning work under approved architectural constraints,
- generating or updating code within canonical boundaries,
- creating or adapting tests where valid,
- validating conformance to governance and architecture,
- identifying drift, broken ownership, and contract violations,
- supporting controlled rewrite and repair operations,
- producing reviewable output that remains attributable and traceable.

Automation must support system continuity, not bypass it.

---

## 4. Automation Authority Boundaries

### 4.1 Allowed Automation Actions

Automation may perform the following tasks only when they remain within approved project policy:

- scaffold modules using approved templates,
- generate standard boilerplate under canonical naming and structure rules,
- create tests that match project test standards,
- perform low-risk refactors that preserve architecture and contracts,
- update documentation in approved contexts,
- apply formatting and non-functional cleanup,
- create or modify generated artifacts that remain within governance scope,
- validate code against known validators and project rules.

### 4.2 Forbidden Automation Actions

Automation must not:

- modify governance policy,
- redefine architecture or canonical structure,
- rewrite contracts without explicit human approval,
- delete modules without human sign-off and migration review,
- change ownership boundaries or canonical paths without review,
- merge directly to protected branches,
- bypass validator gates without an approved exception,
- act silently when affecting a governed or architectural resource,
- create duplicate modules, aliases, compatibility wrappers, or historical drift.

### 4.3 Human Oversight Requirement

All automation actions must be:

- attributable,
- logged,
- reviewable,
- validated,
- and bounded by mutation classification.

No automation action is considered valid merely because it executed successfully. It must remain compliant with repository policy and architecture.

---

## 5. Canonical Architecture Constraints

Automation must respect the canonical architecture defined by the project.

### 5.1 Required Production Structure

```text
cnpos/core/
├── agents/
├── automation/
├── contracts/
├── governance/
├── orchestrators/
├── runtime/
├── state/
├── validators/
└── ...
```

The testing subsystem remains a separate ownership domain:

```text
tests/
```

### 5.2 Naming and Import Rules

Automation must preserve the project naming standards:

- module files use the pattern `*_v1_2.py`
- class names use the pattern `<ClassName>V1_2`
- canonical imports begin with `from cnpos.core.`
- relative imports and legacy prefixes are prohibited
- historical implementations, aliases, and migration wrappers are not authoritative

### 5.3 Single Source of Truth

Every module must satisfy:

```text
One module
One owner
One path
One public identity
One canonical import
```

Automation must not create duplicate ownership, hidden aliases, drifted implementations, or parallel versions of the same responsibility.

---

## 6. Automation Lifecycle

The canonical automation lifecycle is:

```text
SCAN
  ↓
PLAN
  ↓
WRITE
  ↓
VALIDATE
  ↓
TEST
  ↓
REVIEW
  ↓
REPAIR
```

### 6.1 Lifecycle Semantics

- SCAN: Identify scope, ownership, canonical paths, and constraints.
- PLAN: Determine mutation class, required approval, and affected assets.
- WRITE: Generate code or documentation under controlled templates.
- VALIDATE: Run governance, architecture, and contract validation.
- TEST: Run relevant tests for changed behavior.
- REVIEW: Human review ensures correctness, risk, and policy conformance.
- REPAIR: Correct issues, revalidate, and resubmit if needed.

Automation may not skip validation or review for governed resources.

---

## 7. Mutation Classification Policy

All automation-driven changes must be classified by risk before execution or review.

### 7.1 Mutation Classes

- SAFE
  - comments
  - formatting
  - non-functional cleanup
  - documentation improvements
  - minor clarity updates

- MODERATE
  - internal refactor
  - naming alignment
  - simplification
  - non-breaking quality improvements

- HIGH_RISK
  - execution path changes
  - state modifications
  - persistence changes
  - API behavior changes
  - contract-adjacent changes

- ARCHITECTURAL
  - ownership changes
  - subsystem boundary changes
  - canonical structure changes
  - dependency strategy changes
  - major design changes

- BREAKING_CHANGE
  - incompatible interface changes
  - backward-incompatible behavior
  - migration-heavy changes
  - contract changes requiring downstream adjustment

### 7.2 Approval Rules

- SAFE: automation may proceed with validation
- MODERATE: automation may proceed with human review
- HIGH_RISK: human owner approval required
- ARCHITECTURAL: architecture authority approval required
- BREAKING_CHANGE: governance approval required

Mutation classification is mandatory whenever automation modifies code, structure, contracts, or ownership.

---

## 8. Review and Approval Model

### 8.1 Required Review Paths

All code changes must pass through the repository’s review process, including:

- module owner review for module-level correctness,
- reviewer validation for conformance and risk,
- architecture review for design-sensitive changes,
- governance review for policy-sensitive or high-risk changes.

### 8.2 Branch Protection and Merge Rules

- `main` is the protected stable branch.
- direct pushes to `main` are prohibited.
- changes must be proposed through pull requests.
- all required checks must pass before merge.
- architecture-sensitive and governance-sensitive changes require elevated approval.

### 8.3 Merge Policy

- policy changes require governance sign-off,
- architecture changes require architecture sign-off,
- module changes require module owner sign-off where applicable,
- breaking or high-risk changes require elevated review and explicit approval.

---

## 9. Validation and Enforcement

Validation is mandatory. The project distinguishes between:

- validation as enforcement,
- review as human judgment,
- tests as implementation verification.

A change is not valid merely because it compiles or passes local tests. It must satisfy:

- governance requirements,
- architecture conformance,
- ownership expectations,
- canonical naming and import compliance,
- relevant validation gates,
- and appropriate test coverage.

### 9.1 Validation Sequence

```text
Contract
  ↓
Governance
  ↓
Continuity
  ↓
Mutation
```

Automation must not bypass any required validation stage without a recorded exception.

---

## 10. Exception Policy

Exceptions are allowed only when explicit, narrow, and auditable.

Every exception must record:

- the reason,
- the affected module or subsystem,
- the scope of the override,
- the approving authority,
- the review or expiry date,
- and the audit record.

### 10.1 Bypass Rules

- bypassing governance validation is not allowed without explicit governance approval,
- bypassing continuity validation requires architecture or governance approval,
- bypassing validator enforcement without a recorded exception is a governance violation,
- no one may commit code that fails required governance checks unless the exception process is invoked and logged.

Exceptions are temporary and must remain reversible.

---

## 11. Ownership and Drift Control

Automation must respect ownership boundaries and prevent drift.

### 11.1 Ownership Model

The project enforces clear ownership by subsystem:

- Runtime owns execution semantics and operational behavior.
- State owns persistence and state integrity.
- Validators own enforcement logic.
- Governance owns policy and authority.
- Contracts own public interfaces and compatibility rules.
- Automation owns generation and scaffolding within defined rules.
- Tests own verification fidelity.
- Architecture owns canonical design intent.

### 11.2 Drift Policy

Drift is any compliance loss between a module and the project’s governing standards.

Examples include:

- path drift,
- ownership drift,
- naming drift,
- contract drift,
- validation drift,
- governance drift.

Automation must detect, report, and support remediation of drift. Drift does not become acceptable simply because code still runs.

---

## 12. Definition of Complete

A module is complete only when it satisfies the full project definition of completion:

- governance compliant,
- architecture compliant,
- canonical tree compliant,
- owned by an explicit module owner,
- public identity defined,
- contract compliant,
- validation passing,
- tests passing,
- documented,
- registered in the canonical structure or registry,
- free from unresolved drift,
- and safe to be depended upon by the system.

A module is not considered complete merely because it compiles or exists in the repository.

---

## 13. Security, Safety, and Operational Boundaries

Automation must never be used to evade system safety requirements.

It may assist with operational workflows only when:

- the workflow is within approved governance scope,
- ownership is clear,
- validation remains enforced,
- and runtime safety is protected.

Emergency runtime decisions may temporarily override implementation choices to preserve continuity or safety, but such overrides are operational and temporary. They do not establish permanent architecture or governance.

---

## 14. Documentation and Auditability

Automation outputs must be reviewable and attributable.

The project expects the following from automation:

- clear action logging,
- traceable outputs,
- explicit scope and risk classification,
- links to affected modules or interfaces,
- evidence of validation and review,
- and an auditable record of approvals and exceptions.

---

## 15. Operational Rules for Automation Agents

When automation is used for code generation or maintenance, it must follow these rules:

1. Read the relevant governance and architecture documents before making changes.
2. Identify the canonical location and owner of the affected module.
3. Classify the mutation before action.
4. Restrict work to approved templates and accepted boundaries.
5. Validate all generated or modified output.
6. Ensure no drift is introduced.
7. Produce review-ready diffs with clear intent.
8. Stop and escalate when a required approval is missing.

Automation must not treat governance or architecture as optional.

---

## 16. Final Policy Statement

Automation in CNPOS is a bounded, reviewable, auditable subsystem whose purpose is to accelerate compliant work without weakening governance.

Its operating principle is:

> Automation may assist with implementation, but it cannot override policy, architecture, ownership, validation, or safety.

The architecture remains authoritative. The governance model remains binding. The validators remain enforcement. The owners remain accountable. Tests remain evidence. Runtime remains operational reality.

If automation proposes a change that would alter policy, architecture, contracts, or ownership, it must stop and require human approval.

---

## 17. Summary

CNPOS automation is designed to support deterministic, low-drift development and architecture-preserving change. It is not a free-form code-writing engine. It is a governed subsystem that must remain within architectural and governance constraints.

The project’s automation mandate is:

- generate within approved templates,
- respect canonical structure,
- operate under mutation classification,
- require review and validation,
- preserve ownership and drift boundaries,
- and never bypass governance or architecture.

This is the authoritative operating model for automation in CNPOS.

---

## 18. Related Documents

- `GOVERNANCE.md`
- `README.md`
- canonical architecture documents
- canonical tree definitions
- contract definitions
- validator rules

All automation decisions should be evaluated against these documents before implementation begins.

