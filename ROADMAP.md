# Roadmap

## 1. Purpose

This roadmap defines the planned evolution of CNPOS v2 as a governed, deterministic, auditable, low-drift architecture. It is aligned with the project’s governing principles:

- Architecture is the source of truth.
- Governance defines what is allowed.
- Ownership must remain explicit and bounded.
- Validation and review are mandatory.
- Automation supports implementation but does not set policy.

This document is intended to support planning, prioritization, and implementation sequencing. It does not override governance, architecture, or contracts. When conflict exists, governance and architecture remain authoritative.

---

## 2. Project Position

CNPOS v2 is currently positioned as a clean, canonical baseline for a governed software architecture that emphasizes:

- deterministic behavior
- auditability
- governance-first decision making
- canonical structure and ownership
- validation over drift
- automation-assisted but policy-controlled change

The repository currently reflects an architecture-first reset rather than a broad feature-complete product. The roadmap therefore focuses on establishing a stable, governed, extensible system foundation before broad expansion of domain features.

---

## 3. Strategic Goals

### 3.1 Architectural stability

Establish and preserve the canonical production structure:

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

Goals:

- lock architecture to the approved canonical tree
- prevent historical drift and duplicate ownership
- maintain one-module/one-owner/one-path discipline

### 3.2 Governance maturity

Make governance enforceable and reviewable.

Goals:

- formalize ownership and responsibility boundaries
- require mutation classification for non-trivial changes
- maintain strict validation and exception controls
- keep automation bounded and traceable

### 3.3 Validation and continuity

Ensure system correctness and operational continuity.

Goals:

- enforce architecture validation gates
- preserve continuity and mutation tracking
- require review and evidence before merge
- reduce drift and untracked changes

### 3.4 Automation capability

Use automation as a bounded support subsystem rather than as an unrestricted code generator.

Goals:

- scaffold only within canonical boundaries
- keep automation traceable and reviewable
- support controlled rewrite and repair workflows
- encourage governance-aware generation workflows

### 3.5 Product readiness

Evolve toward a defined production pipeline for narrative orchestration and governance-controlled execution.

Goals:

- formalize canonical contracts for narrative domains
- strengthen runtime orchestration flow
- close the gap between architecture baseline and business-ready execution
- move from structural compliance to operational maturity

---

## 4. Roadmap Phases

## Phase 1: Governance and Architecture Foundation

Status: In progress / foundational

Objectives:

- finalize canonical ownership boundaries
- maintain authoritative canonical tree and registry
- enforce naming and import standards
- confirm governance precedence and decision model
- standardize module registration and registry completeness

Key outcomes:

- clean architecture baseline
- explicit module ownership
- canonical structure preserved
- drift detection and enforcement established

Priority areas:

- governance documentation
- canonical tree discipline
- module registry maintenance
- validation gate framework

---

## Phase 2: Runtime and Continuity Maturity

Status: Planned

Objectives:

- strengthen runtime execution semantics
- formalize continuity and mutation state handling
- complete and validate state-related modules
- ensure runtime behavior remains consistent with architecture and policy

Key outcomes:

- stable execution engine behavior
- robust continuity tracking
- explicit mutation classification and reporting
- better operational traceability

Priority areas:

- runtime orchestration behavior
- continuity engine logic
- mutation manager and classification logic
- runtime validation and exception handling

---

## Phase 3: Validation and Enforcement Expansion

Status: Planned

Objectives:

- expand validation coverage across architecture, contracts, governance, and runtime behavior
- enforce review requirements and quality gates
- reduce ambiguity between validation, tests, and policy
- strengthen non-compliance detection

Key outcomes:

- stronger automated enforcement
- tighter governance conformance
- more reliable change safety
- lower drift risk across subsystems

Priority areas:

- validator pipeline maturity
- governance validation coverage
- contract conformance checks
- mutation validation workflows

---

## Phase 4: Automation and Code Generation Control

Status: Planned

Objectives:

- make automation a governed subsystem rather than an ad hoc tool
- ensure generated output increases compliance rather than drift
- support standard architecture-aware planning and rewrite workflows
- make all automation actions attributable and reviewable

Key outcomes:

- automation integrates with canonical architecture
- generated modules remain aligned to governance and structure
- review readiness improves
- automation reduces boilerplate without weakening policy

Priority areas:

- planning agents
- code generation templates
- validator-backed rewrite flows
- logging and traceability for automation actions

---

## Phase 5: Domain Execution and Narrative Pipeline Development

Status: Future / feature-oriented

Objectives:

- formalize the narrative production pipeline
- define and stabilize contract domains such as Episode, Scene, Shot, and Render
- connect orchestration, state, validation, and runtime into a coherent domain execution model
- support deterministic cinematic narrative generation and orchestration workflows

Key outcomes:

- narrative domain pipelines operate under approved architecture
- clear contract boundaries between domain and runtime concerns
- improved system determinism and continuity
- stronger support for orchestrated production flows

Priority areas:

- cinematic pipeline development
- character pipeline development
- contract refinement
- runtime orchestration improvements

---

## Phase 6: Production Hardening and Operational Readiness

Status: Future

Objectives:

- harden the system for maintainable operations
- improve review, audit, and exception workflows
- institutionalize release discipline and change control
- confirm operational readiness for broader adoption

Key outcomes:

- reliable operational behaviors
- stronger accountability and auditability
- production-ready review process
- lower change risk across architecture boundaries

Priority areas:

- release governance
- operational documentation
- environment/configuration management
- production review safeguards

---

## 5. Prioritized Workstreams

### 5.1 Immediate priorities

- maintain the canonical architecture and prevent drift
- complete module ownership clarity
- enforce naming and import standards
- continue validator, governance, and state alignment
- keep automation within defined governance boundaries

### 5.2 Near-term priorities

- strengthen runtime orchestration and continuity behavior
- expand contract and validator support
- improve automation traceability and review readiness
- stabilize core runtime pipelines

### 5.3 Medium-term priorities

- domain pipeline modeling for narrative and character workflows
- contract maturity and cross-module coordination
- operational readiness and formal documentation improvements
- controlled feature expansion beyond the core architecture baseline

### 5.4 Long-term priorities

- fully governed operational product workflows
- higher-level orchestration and execution automation
- broad domain execution support
- scalable, auditable extension of the canonical architecture

---

## 6. Milestones

### Milestone M1: Governance baseline locked

Target: immediate

Deliverables:

- governance and architecture documents aligned
- module registry in place
- canonical structure preserved
- mutation classification used consistently

### Milestone M2: Runtime and state stabilization

Target: short-term

Deliverables:

- runtime execution model stabilized
- continuity and mutation state management refined
- validator and governance pipeline improved

### Milestone M3: Controlled automation maturity

Target: short-term to medium-term

Deliverables:

- automation workflow governed by policy
- traceable generation and rewrite process
- compliant module scaffolding and validation support

### Milestone M4: Narrative pipelines and contract maturity

Target: medium-term

Deliverables:

- approved domain contract definitions
- canonical narrative execution flows
- stronger orchestration and continuity coordination

### Milestone M5: Production hardening

Target: medium- to long-term

Deliverables:

- release processes and operational readiness
- robust governance enforcement and review model
- scalable architecture discipline for future extension

---

## 7. Risks and Constraints

### 7.1 Architecture drift

The biggest risk to the project is any drift away from the approved architecture or canonical ownership structure.

Mitigation:

- keep registry and canonical tree authoritative
- require validation and review
- reject ungoverned compatibility wrappers or historical reintroductions

### 7.2 Governance overreach or ambiguity

If governance, architecture, and runtime concerns are conflated, decision-making becomes inconsistent and unsafe.

Mitigation:

- preserve the hierarchy of authority
- keep policy, architecture, implementation, validation, and runtime distinct

### 7.3 Automation misuse

Automation can quickly create drift if it is allowed to act outside policy or architecture.

Mitigation:

- use mutation classification
- require human review
- preserve validation gates and approval requirements

### 7.4 Scope creep

Building too many features before the architecture and governance model are stable can weaken the project.

Mitigation:

- prioritize canonical stability before broad feature expansion
- defer non-essential work until foundation is mature

---

## 8. Success Criteria

The roadmap is considered successful when:

- the canonical architecture remains stable and auditable
- module ownership is explicit and enforced
- governance and architecture decisions are consistently followed
- validation and tests support the architecture rather than redefine it
- automation improves speed without weakening policy
- narrative domain pipelines expand only inside approved architectural boundaries

---

## 9. Final Position

CNPOS v2 is best understood as a governance-driven architecture project with a strong emphasis on determinism, continuity, validation, and low drift. The roadmap therefore prioritizes architectural maturity, governance enforcement, and stable foundations before broad feature expansion.

The central principle is simple:

> Build the governed system first, then extend the feature domain within the authoritative architecture.

