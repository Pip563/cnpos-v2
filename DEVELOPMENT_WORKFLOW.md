# Development Workflow

## 1. Purpose

This document defines the standard development workflow for CNPOS v2. It is intended to preserve the project’s governing principles:

- Architecture is the source of truth.
- Governance defines what is allowed.
- Ownership is explicit and bounded.
- Validation and review are mandatory.
- Automation is a support tool, not an authority.
- Drift is unacceptable unless intentionally remediated.

This workflow is subordinate to the project’s governance and architecture authority documents. When a rule in this file conflicts with governance or architecture, governance and architecture take precedence.

---

## 2. Core Principles

### 2.1 Architecture-first development

All work must align with the canonical architecture and approved subsystem boundaries.

- Production code belongs under `cnpos/core/...`
- Tests live in a separate ownership domain: `tests/`
- Historical modules, aliases, and compatibility wrappers are not authoritative
- Canonical naming and import patterns are mandatory

### 2.2 Single source of truth

Every module should have:

- one module
- one owner
- one path
- one public identity
- one canonical import

No duplicate implementation or hidden compatibility layer should be introduced without explicit approval.

### 2.3 Governance and review

The project is governed by clear decision precedence:

1. legal, security, compliance, and safety obligations
2. governance policy
3. architecture authority
4. canonical tree and canonical contracts
5. validators and enforcement rules
6. runtime operational realities
7. test results

This means failing tests or a quick runtime workaround do not override policy or architecture.

---

## 3. Repository Structure and Ownership

The authoritative production structure is:

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

Tests are intentionally separated:

```text
tests/
```

Subsytem ownership is expected to be explicit and stable:

- Runtime: operational behavior and execution semantics
- State: continuity, persistence, and state integrity
- Validators: enforcement logic
- Governance: policy and authority
- Contracts: public interfaces and compatibility rules
- Automation: generation and scaffolding only within approved boundaries
- Tests: verification fidelity
- Architecture: canonical design intent

A change must not cross ownership boundaries without review and approval.

---

## 4. Development Environment

### 4.1 Prerequisites

Required:

- Python 3.10 or newer
- Git
- a virtual environment
- repository access with proper permissions

### 4.2 Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Additional services, if required by a specific module, must be documented in the module or task scope before work begins.

### 4.3 Running the project

The project entry point is exposed through the package CLI:

```bash
python -m cnpos --help
```

Examples:

```bash
python -m cnpos codegen --module my_module
```

Use the project’s actual module and command surfaces as they exist in the repository. Do not invent alternate entry points or compatibility aliases.

---

## 5. Branching Model

The repository uses a protected branch model.

### 5.1 Required branches

- `main`: protected stable branch
- `feature/*`: normal development work
- `hotfix/*`: urgent production fixes
- `release/*`: controlled release work when required

### 5.2 Branch rules

- direct pushes to `main` are prohibited
- all changes to `main` must go through a pull request
- all required checks must pass before merge
- architecture-sensitive and governance-sensitive work requires elevated approval

### 5.3 Branch naming

Use concise, descriptive branch names.

Examples:

```text
feature/character-continuity-validator
feature/code-automation-scan-plan
hotfix/validator-regression
release/v1_2.1
```

---

## 6. Working on a Change

### 6.1 Before writing code

Before making a change, do all of the following:

1. read the relevant governance and architecture documents
2. identify the canonical module path and owner
3. identify the boundary of the task
4. classify the mutation risk
5. confirm whether automation is allowed for the task
6. identify the validation commands that apply

### 6.2 Mutation classification

Every substantial change must be classified before implementation. The project uses the following classes:

- SAFE
  - comments
  - formatting
  - documentation improvements
  - non-functional cleanup
  - small clarity changes

- MODERATE
  - internal refactors
  - naming alignment
  - simplification
  - non-breaking quality work

- HIGH_RISK
  - execution-path changes
  - state changes
  - persistence changes
  - API behavior changes
  - contract-adjacent work

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
  - contract changes that require downstream adaptation

Approval requirements:

- SAFE: automation may proceed with validation
- MODERATE: automation may proceed with human review
- HIGH_RISK: human owner approval required
- ARCHITECTURAL: architecture authority approval required
- BREAKING_CHANGE: governance approval required

### 6.3 Required standards for implementation

Every new or changed module must satisfy:

- one owner
- one canonical path
- one public identity
- canonical naming convention
- canonical import pattern
- no duplicate ownership
- no hidden aliases or migration wrappers
- no architecture drift

Never “fix” architecture to suit a convenient implementation. Architecture wins.

---

## 7. Automation Workflow

Automation is allowed only within defined governance and architectural boundaries.

### 7.1 Automation lifecycle

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

### 7.2 Allowed automation actions

Automation may:

- scaffold modules under approved templates
- generate boilerplate within canonical structure
- create relevant tests
- update documentation when explicitly appropriate
- perform low-risk cleanup and formatting
- validate outputs against known rules

### 7.3 Forbidden automation actions

Automation must not:

- modify governance policy
- change the architecture or canonical tree without approval
- rewrite contracts without explicit human approval
- delete modules without human sign-off and migration review
- bypass validation gates without a recorded exception
- create duplicate functionality or historical drift
- act silently when affecting a governed or architectural resource

If a task would alter policy, architecture, contracts, or ownership, automation must stop and require human approval.

---

## 8. Validation Requirements

Validation is mandatory. The project distinguishes between:

- validation as enforcement
- review as human judgment
- tests as implementation verification

### 8.1 Required validation order

```text
Contract
  ↓
Governance
  ↓
Continuity
  ↓
Mutation
```

### 8.2 Required checks before PR

Before opening or completing a pull request, ensure the change:

- matches canonical structure
- uses the correct naming pattern
- passes relevant validation checks
- passes relevant tests
- satisfies module ownership rules
- does not introduce drift
- remains reviewable and attributable

Use the project’s actual validation and test commands when they exist. If a repository-specific check is missing, document the validation method used and why it is relevant.

### 8.3 Exception process

Exceptions are allowed only when explicit, narrow, and auditable.

An exception must include:

- the reason
- the affected module or subsystem
- the scope of the override
- the approving authority
- expiry or review date
- audit record

Bypassing governance validation without an approved exception is not allowed.

---

## 9. Testing and Verification

The testing subsystem is separate from production architecture. Tests verify behavior and conformance, but they do not define architecture.

### 9.1 Minimum expectations

A change is not complete simply because it compiles or runs locally. It should satisfy:

- relevant unit or functional tests
- integration checks where applicable
- governance and architectural validation
- ownership and contract compliance
- review feedback

### 9.2 Test commands

At a minimum, the project should be validated with the repository’s real test command, for example:

```bash
pytest
```

If a module-specific command is required, it must be documented in the module or task description.

---

## 10. Pull Request Workflow

### 10.1 Before opening a PR

Open a branch from `main` or the active release branch and complete the following:

- confirm branch naming follows convention
- confirm the task is scoped and bounded
- confirm mutation class is assigned
- confirm the canonical path and ownership are correct
- run relevant validation and tests
- ensure no drift is introduced
- review the diff for reviewability

### 10.2 PR content expectations

The PR should include:

- concise summary of the change
- affected modules or subsystems
- mutation classification
- validation performed
- any approvals or exceptions
- relevant screenshots or artifacts if needed

### 10.3 Required reviewers

At minimum:

- module owner review for module-level correctness
- reviewer validation for conformance and risk
- architecture review for design-sensitive changes
- governance review for policy-sensitive changes

A PR that changes architecture, contracts, governance, or ownership must follow the elevated approval path.

### 10.4 Merge rules

- `main` is protected
- direct pushes to `main` are prohibited
- all required checks must pass
- breaking or high-risk changes require explicit review and approval
- no merge without the required approvals and validation evidence

---

## 11. Review Expectations

Review is human judgment layered over validation.

Reviewers should check:

- correctness
- risk
- conformance to architecture and governance
- unnecessary drift or scope creep
- ownership clarity
- documentation and traceability

The burden is not only on the author. Reviewers are expected to enforce policy and flag non-compliance.

---

## 12. Definition of Done

A change is complete only when it satisfies the project definition of completion:

- governance compliant
- architecture compliant
- canonical tree compliant
- explicit owner assigned
- public identity defined
- contract compliant
- validation checks passing
- relevant tests passing
- documented
- no unresolved drift
- safe to be depended on by the system

A task is not complete merely because the code compiles.

---

## 13. Documentation and Auditability

All substantial work should leave a clear trail.

Required records include:

- branch or task ID
- module or subsystem affected
- reason for the change
- validation evidence
- reviewer approvals
- any exception or deviation

The project values traceability, accountability, and auditability over informal convenience.

---

## 14. Escalation and Conflict Resolution

If a change conflicts with governance or architecture:

- do not override the rules informally
- stop and escalate to the appropriate authority
- record the conflict and the decision path
- do not permit “silent exceptions” or hidden workarounds

Governance and architecture are the final authority for design and policy decisions.

---

## 15. Final Workflow Summary

The baseline development workflow for CNPOS is:

```text
Read governance and architecture
Identify canonical path and owner
Classify mutation risk
Implement within approved boundaries
Validate and test
Open PR with clear evidence
Get required review and approvals
Merge only through the protected workflow
Verify completion against the definition of done
```

This workflow keeps the repository deterministic, auditable, low-drift, and faithful to the authorized production architecture.

---

## 16. Related Documents

- `README.md`
- `GOVERNANCE.md`
- `AUTOMATION.md`
- canonical architecture documents
- canonical tree definitions
- contract definitions

If a rule in this workflow conflicts with those documents, the governing documents take priority.

