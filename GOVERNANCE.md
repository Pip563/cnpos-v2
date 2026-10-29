# Governance

## 1. Purpose

This document defines the governance model for CNPOS. It establishes:
- who has authority to decide,
- how decisions are made,
- what is permitted and prohibited,
- how ownership is assigned,
- how automation is constrained,
- how exceptions are handled,
- how changes are reviewed and merged,
- and what it means for a module to be considered complete.

This document is the authoritative policy for the project. Architecture specifications, contracts, validation rules, runtime behavior, and tests are subordinate to this document when they conflict with it.

---

## 2. Governing Principles

CNPOS distinguishes between policy, architecture, implementation, validation, and operational reality.

The governing principles are:

- Policy decides what is allowed.
- Architecture decides what is fit for the system.
- Implementation decides how to do it.
- Validators enforce conformance.
- Tests verify correctness.
- Runtime reveals real-world behavior.
- Governance is the final authority for policy decisions.

In other words:

- Governance answers: "Is this permitted?"
- Architecture answers: "Is this the right design?"
- Implementation answers: "How do we build it?"
- Validators and tests answer: "Does it conform and work?"
- Runtime answers: "Does it remain safe under real operation?"

These questions are different and must not be conflated.

---

## 3. Decision Hierarchy and Precedence

The project uses the following precedence:

1. Legal, security, compliance, and safety obligations
2. Governance policy
3. Architecture authority
4. Canonical tree and canonical contracts
5. Validators and enforcement rules
6. Runtime operational realities
7. Test results

This precedence is intentionally ordered. A failing validator or test does not override a governing policy. A runtime issue does not automatically establish permanent design authority. Architecture does not override governance when governance has explicitly established a rule.

### 3.1 Formal Authority Ordering

The authoritative order is:

Governance
  ↓
Architecture Authority
  ↓
Canonical Tree
  ↓
Contracts
  ↓
Validators
  ↓
Runtime
  ↓
Tests

This hierarchy should be read as a decision-order model, not as a reporting chain.

Important clarification:
- Governance is authoritative over what is allowed.
- Architecture is authoritative over what the system should look like.
- Validators are not authority; they are enforcement mechanisms.
- Runtime is not authority; it is operational evidence.
- Tests are evidence, not policy.

---

## 4. Conflict Resolution Policy

### 4.1 Governance Conflict

If the question is: "Is this allowed?"

Authority:
- Governance

Owners:
- Project owner
- Maintainers
- Governance authority

Resolution:
- Governance rules take precedence.

### 4.2 Architecture Conflict

If the question is: "Is this the correct system design?"

Authority:
- Architecture Authority
- Technical lead
- Senior engineering authority

Owners:
- Architecture owner
- Module owners in affected domain
- Maintainers

Resolution:
- Architecture decisions are binding within the policy defined by governance.

### 4.3 Implementation Conflict

If the question is: "Did we implement it correctly?"

Authority:
- Validators
- Tests
- Review process
- Module owner

Owners:
- Reviewer
- Maintainer
- Module owner

Resolution:
- Implementation must conform to architecture and governance.
- A failing validation or test is a defect to be corrected, not a new design authority.

### 4.4 Runtime Conflict

If the question is: "Can the system safely operate right now?"

Authority:
- Runtime owner
- Incident commander
- On-call operator or operations lead

Owners:
- Runtime/operations authority

Resolution:
- Emergency operational decisions may temporarily override implementation choices to protect safety or continuity.
- Such overrides do not become permanent architecture or governance.

---

## 5. Roles and Responsibilities

### 5.1 Project Owner

The project owner has final responsibility for project direction, policy enforcement, and governance decisions.

Responsibilities:
- maintain the governance document,
- resolve disputes that cannot be resolved by architecture or maintainers,
- approve major governance changes,
- ensure continuity and accountability.

### 5.2 Maintainers

Maintainers are the project’s decision-making and review body for operational continuity.

Responsibilities:
- review and approve changes,
- enforce governance policy,
- ensure modules remain compliant,
- approve exceptions where permitted,
- ensure module ownership is maintained.

### 5.3 Architecture Authority

Architecture Authority governs design intent and system coherence.

Responsibilities:
- define canonical boundaries,
- approve architectural changes,
- define subsystem responsibilities,
- approve interface, dependency, and contract changes,
- resolve design conflicts where governance is silent.

### 5.4 Module Owners

Every module has one owner.

Requirements:
- one module
- one owner
- one path
- one public identity

Responsibilities:
- maintain module compliance,
- guard against drift,
- ensure governance and validation rules are met,
- approve or reject scoped changes within their module,
- maintain documentation and module health.

### 5.5 Reviewers

Reviewers participate in change validation.

Responsibilities:
- inspect correctness,
- validate conformance to policy,
- identify risk and edge cases,
- ensure changes are consistent with architecture and governance.

### 5.6 Contributors

Contributors may propose changes via pull requests or issue-driven collaboration.

Responsibilities:
- follow governing rules,
- route changes through the defined workflow,
- maintain traceability,
- avoid bypassing governance or validation.

### 5.7 Automation

Automation is a bounded tool, not an authority.

Automation may operate only within defined policy boundaries.

Responsibilities:
- generate or modify code under approved templates,
- perform validations and report results,
- support maintainers and module owners,
- never act outside approved mutation and governance scope.

---

## 6. Ownership Model

Ownership must be defined at the subsystem level.

The project adopts the following ownership model:

- Runtime owns execution semantics and operational behavior.
- State owns persistence and state integrity.
- Validators own enforcement logic.
- Governance owns policy, approvals, and authority.
- Contracts own public API and compatibility rules.
- Automation owns generation and scaffolding only within defined policy.
- Tests own verification fidelity.
- Architecture owns canonical design intent.

This model exists to ensure that:
- a module has one accountable owner,
- governance does not become diffuse,
- architecture remains coherent,
- responsibilities are explicit,
- automation cannot silently cross ownership boundaries.

### 6.1 Ownership Rules

The project enforces the following:

- One module has one owner.
- One owner has one public identity for the module.
- One module has one canonical path.
- Ownership is explicit in the module registry or canonical tree.
- Ownership cannot be implicit or inferred solely from who last edited the file.
- A module owner may delegate technical review, but not authority.

---

## 7. Single Source of Truth

The project has a single source of truth for design and policy.

The authoritative sources are:
- this GOVERNANCE.md,
- Architecture Authority documents,
- canonical tree definitions,
- contract definitions,
- governance policy definitions,
- approved validation rules.

Architecture documents, implementation files, and generated outputs are not sources of independent authority. They are subordinate to the authoritative definitions.

If there is a conflict between:
- implementation
- architecture
- governance

then the precedence defined in Section 3 governs.

---

## 8. Automation Authority

This is the most important policy area for the project’s future growth.

Automation is allowed only under defined, bounded authority.

### 8.1 Allowed Automation Actions

| Action | Policy |
|---|---|
| Create modules | Allowed under approved templates and canonical structure |
| Rewrite modules | Allowed only for low-risk mutation classes and after validation |
| Create tests | Allowed, but subject to project test standards |
| Modify governance | Forbidden for automation |
| Modify contracts | Forbidden without explicit architecture and human approval |
| Delete modules | Forbidden by default; requires human approval and migration plan |
| Merge directly to main | Forbidden |
| Change canonical tree | Forbidden without explicit architecture approval |

### 8.2 Automation Boundaries

Automation may:
- scaffold modules,
- generate standard boilerplate,
- create common test scaffolding,
- rewrite non-critical implementation details,
- update documentation when explicitly approved.

Automation may not:
- redefine policy,
- override governance,
- edit core contracts without review,
- delete modules without human sign-off,
- rewrite canonical architecture without approval,
- bypass validation gates.

### 8.3 Human Oversight Requirement

All automation actions must be:
- logged,
- attributable,
- traceable,
- reviewable,
- bound by mutation classification.

No automation action shall be silent, undocumented, or unreviewed when it affects a governed or architectural resource.

---

## 9. Mutation Classification Policy

The project defines mutation classes to govern automation and review risk.

### 9.1 Mutation Classes

- SAFE
  - comments
  - formatting
  - non-functional cleanup
  - documentation improvements
  - minor internal clarity changes

- MODERATE
  - internal refactor
  - naming alignment
  - code simplification
  - non-breaking functional improvements

- HIGH_RISK
  - execution path changes
  - state changes
  - persistence changes
  - API behavior changes
  - contract-adjacent change

- ARCHITECTURAL
  - ownership changes
  - subsystem boundary changes
  - canonical structure changes
  - dependency strategy changes
  - major design changes

- BREAKING_CHANGE
  - incompatible interface changes
  - backward-incompatible behavior
  - major migration requirement
  - contract changes that require downstream adaptation

### 9.2 Mutation Approval Rules

- SAFE: automation may act with validation
- MODERATE: automation may act with human review
- HIGH_RISK: human owner approval required
- ARCHITECTURAL: architecture authority approval required
- BREAKING_CHANGE: governance approval required

Mutation classification is mandatory for all changes that affect code generation, rewriting, or substantial refactoring.

---

## 10. Human Override Rules

Exceptions are allowed, but they must be explicit, narrow, and auditable.

### 10.1 Exception Process

A human may bypass validation only under an approved exception process. The exception must include:
- the reason,
- the affected module or subsystem,
- the scope of the override,
- the approving authority,
- the expiry or review date,
- an audit record.

### 10.2 Bypass Rules

- Bypassing governance validation is not allowed except by explicit governance approval.
- Bypassing continuity validation requires architecture or governance approval.
- Bypassing validator enforcement without a recorded exception is a governance violation.
- No one may commit code that fails governance checks unless the exception process is invoked and logged.

### 10.3 Exception Principle

Exceptions are temporary and must be:
- narrow,
- justified,
- time-bound,
- reviewed,
- and reversible.

Exceptions should not become permanent policy by default.

---

## 11. Validation and Review

Validators and tests are required but not sufficient.

The project distinguishes between:
- validation as enforcement,
- review as human judgment,
- tests as implementation verification.

A pull request or change is not valid simply because all automated checks passed. It must also satisfy:
- governance rules,
- architecture conformance,
- ownership review,
- compatibility expectations,
- and relevant test coverage.

Validation failures are not optional recommendations. They are blockers unless a recorded exception is in place.

---

## 12. Branching Governance

The repository must use a protected branch model.

### 12.1 Branching Rules

- main is the protected stable branch.
- feature/* branches are used for development.
- hotfix/* branches may be used for urgent fixes.
- release/* branches may be used for controlled release work when required.
- direct pushes to main are prohibited.

### 12.2 Pull Request Rules

- All changes to main require a pull request.
- All pull requests require review.
- All policy-sensitive or architecture-sensitive changes require additional approval.
- Critical changes require architecture or governance approval.
- No merge should occur without required validation checks passing.

### 12.3 Merge Policy

- changes to governed policies require governance sign-off,
- changes to architecture require architecture sign-off,
- changes to modules require module owner sign-off where applicable,
- changes with breaking or high-risk mutation classes require elevated review.

---

## 13. Versioning Policy

The project must avoid ambiguity between architectural versioning and repository versioning.

### 13.1 Current Policy

As of this document:
- v1_2 is the active internal architecture baseline unless a future governance decision explicitly changes it.
- cnpos-v2 is the repository or product designation and does not in itself constitute a changed architecture baseline.

If the project intentionally moves to a new architecture baseline, that move must be:
- documented,
- approved,
- implemented with a migration plan,
- and explicitly declared in governance.

### 13.2 Versioning Rules

- Do not mix v1_2 and v2_0 in the same governance model without an explicit migration policy.
- No implicit re-baselining.
- New major architectures require governance approval.
- Compatibility obligations must be documented when a version boundary changes.

---

## 14. Definition of “Complete”

A module is complete only when it satisfies all required conditions.

A module is complete only if:

- it is governance compliant,
- it is architecture compliant,
- it conforms to canonical tree rules,
- it has an explicit owner,
- it has an explicit public identity,
- it is contract compliant,
- it passes validation checks,
- it passes relevant tests,
- it is documented,
- it is registered in the canonical structure or registry,
- it has no unresolved drift violations,
- and it is in a state that can be safely depended on by the system.

A module is not considered complete merely because it compiles or because the code exists. Completion means it is ready to be trusted as part of the system.

---

## 15. Drift Policy

Drift is any reduction in compliance between a module and the project’s governing standards.

Examples include:
- path drift,
- ownership drift,
- naming drift,
- contract drift,
- governance drift,
- validation drift.

Drift must be:
- detected,
- reported,
- assigned to an owner,
- and remediated.

If drift is not remediated, the module remains non-compliant and should not be considered complete.

---

## 16. Decision Records

Governance decisions must be recorded.

The project should maintain:
- approved governance changes,
- architecture decisions,
- exception approvals,
- mutation classifications,
- major branch merges,
- and significant deprecations or migration decisions.

Record keeping ensures:
- accountability,
- historical traceability,
- continuity,
- reduced ambiguity,
- and a clear audit trail.

---

## 17. Enforcement

Governance requires enforcement.

Non-compliance is not merely a technical concern; it is a governance issue.

The project will enforce:
- module ownership,
- canonical paths,
- validation gate compliance,
- approved mutation classes,
- protected branch policy,
- contract discipline,
- governance and architecture approval rules.

Enforcement may include:
- rejection of pull requests,
- requirement of remediation,
- suspension of automation authority,
- escalation to project owner or maintainers,
- and formal exception review.

---

## 18. Amendment Process

This governance document may be amended only by the appropriate authority.

### 18.1 Amendment Rules

- changes to policy require governance approval,
- changes to architecture require architecture approval,
- changes to operational procedures may be approved by maintainers,
- broad or systemic changes require broader review.

### 18.2 Amendment Principle

Governance changes must be:
- explicit,
- justified,
- reviewed,
- and recorded.

No silent governance change is valid.

---

## 19. Final Governance Statement

The project is governed by a clear distinction between:

- what is allowed,
- what is architecturally correct,
- how it is implemented,
- how it is verified,
- and what is safe in real operation.

The core governing rule is:

Policy decides what is allowed.
Architecture decides what is fit for the system.
Implementation decides how to do it.
Tests verify correctness.
Runtime reveals the real world.

This principle should be treated as the foundational decision model for all governance, architecture, review, automation, and operational activity in CNPOS.
