# Module Registry

## 1. Purpose

This document is the authoritative module registry for CNPOS v2. It records the canonical production modules that are recognized as part of the approved architecture, along with their owning subsystem and public identity.

This registry is subordinate to the project’s governance and architecture authority documents. A module is considered valid only when it is:

- in the approved canonical structure,
- explicitly owned,
- consistently named,
- registered here or by the canonical authority documents,
- and free from unresolved drift.

---

## 2. Authority and Scope

### 2.1 Production scope

The production architecture is defined as:

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

### 2.2 Registry rules

The following rules apply:

- one module = one owner
- one module = one canonical path
- one module = one public identity
- no duplicate implementations
- no historical aliases or compatibility wrappers as authoritative modules
- architecture and governance supersede local convenience or implementation drift

---

## 3. Canonical Module Registry

| Module ID | Canonical path | Public identity | Subsystem owner | Status | Notes |
|---|---|---|---|---|---|
| `cnpos.core.runtime.backend_manager_v1_2` | `cnpos/core/runtime/backend_manager_v1_2.py` | `BackendManagerV1_2` | Runtime | Active | Canonical runtime manager module |
| `cnpos.core.runtime.continuity_engine_v1_2` | `cnpos/core/runtime/continuity_engine_v1_2.py` | `ContinuityEngineV1_2` | Runtime | Active | Canonical continuity execution engine |
| `cnpos.core.automation.code_pipeline_v1_2` | `cnpos/core/automation/code_pipeline_v1_2.py` | `CodeAutomationPipelineV1_2` | Automation | Active | Canonical automation pipeline module |
| `cnpos.core.agents` | `cnpos/core/agents/` | Agent subsystem | Agents | Canonical boundary | Subsystem container; individual modules must be declared explicitly |
| `cnpos.core.contracts` | `cnpos/core/contracts/` | Contracts subsystem | Contracts | Canonical boundary | Contract domain and schemas are governed here |
| `cnpos.core.governance` | `cnpos/core/governance/` | Governance subsystem | Governance | Canonical boundary | Policy enforcement and governance logic |
| `cnpos.core.orchestrators` | `cnpos/core/orchestrators/` | Orchestrators subsystem | Orchestrators | Canonical boundary | Execution orchestration and coordination |
| `cnpos.core.state` | `cnpos/core/state/` | State subsystem | State | Canonical boundary | Continuity and mutation state management |
| `cnpos.core.validators` | `cnpos/core/validators/` | Validators subsystem | Validators | Canonical boundary | Validation, continuity, mutation, and governance checks |

---

## 4. Subsystem Register

The following subsystem domains are recognized as canonical ownership domains and should be treated as authoritative design boundaries:

### 4.1 Agents

Owner: Agents

Responsibilities:

- specialized workers
- narrative-processing roles
- continuity and character-specific support
- automation-assisted operational agents

### 4.2 Automation

Owner: Automation

Responsibilities:

- planning
- code generation
- review support
- validation support
- rewrite coordination
- governance-aware scaffolding

### 4.3 Contracts

Owner: Contracts

Responsibilities:

- canonical interface definitions
- schema validation contracts
- public API stability and contract discipline

### 4.4 Governance

Owner: Governance

Responsibilities:

- policy enforcement
- approval logic
- architecture rules
- mutation classification support
- governance validation

### 4.5 Orchestrators

Owner: Orchestrators

Responsibilities:

- pipeline coordination
- runtime sequencing
- worker coordination
- telemetry and operational flow control

### 4.6 Runtime

Owner: Runtime

Responsibilities:

- execution behavior
- system orchestration semantics
- manager and engine behavior
- operational behavior under approved policy

### 4.7 State

Owner: State

Responsibilities:

- continuity tracking
- mutation state management
- persistence of stateful lifecycle information
- continuity and mutation classification support

### 4.8 Validators

Owner: Validators

Responsibilities:

- enforcement logic
- governance validation
- continuity validation
- mutation validation
- contract-validation pipeline execution

---

## 5. Required Naming and Identity Rules

All registered modules must satisfy the following rules:

- filename pattern: `*_v1_2.py`
- class pattern: `<ClassName>V1_2`
- canonical import prefix: `from cnpos.core.`
- relative imports are prohibited in canonical production modules
- legacy, historical, and alias modules are not authoritative by default

Registered module identities are thus expected to reflect the canonical naming pattern and the architecture’s single-source-of-truth model.

---

## 6. Registry Completeness Requirement

A module is not fully complete unless it is both:

- present in the canonical architecture and
- represented in this registry or an equivalent approved authority registry.

Unregistered code that exists in the repository but is not in the approved architecture or registry should be treated as drift until remediated.

---

## 7. Drift Policy for Registry Entries

Drift is any mismatch between the codebase and the project’s approved structure, ownership, or naming standards.

Examples include:

- path drift
- ownership drift
- naming drift
- contract drift
- governance drift
- validation drift

When drift is detected:

1. identify the affected module
2. assign ownership
3. record the violation
4. remediate the module or mark it as non-compliant
5. revalidate before re-accepting it into normal operation

---

## 8. Registry Status Definitions

| Status | Meaning |
|---|---|
| Active | Canonical production module in normal use |
| Canonical boundary | Approved subsystem container, not necessarily a leaf module |
| Draft | Not yet approved for full canonical use |
| Deprecated | Retained only for historical reference and should not be used in new work |
| Non-compliant | Present but violates canonical structure or ownership rules |

---

## 9. Current Registered Canonical Modules

The currently recognized canonical modules based on the available authority materials are:

```text
cnpos.core.runtime.backend_manager_v1_2
cnpos.core.runtime.continuity_engine_v1_2
cnpos.core.automation.code_pipeline_v1_2
```

These are the explicit module identities presently declared in the authoritative registry materials and should be treated as the minimum canonical registry baseline.

---

## 10. Final Rule

The module registry is not a convenience list. It is a governance and architecture artifact that preserves ownership, naming integrity, and canonical placement.

If a module is not registered, not owned, or not aligned with the canonical structure, it is not authoritative unless an explicit governance or architecture decision states otherwise.

