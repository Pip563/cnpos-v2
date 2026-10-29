<<<<<<< HEAD
=======

>>>>>>> a90e32b (Add authoritative architecture README)
Architecture is the authority, not tests, aliases, historical modules, backups, or migrations. Architecture_Authority_V1_2..docx
The approved production structure is exactly the canonical tree defined in canonical_tree_v1_2.md.
Tests are a separate ownership domain from production architecture. architectural_decision.document.docx
CNPOS is intended to be deterministic, auditable, governance-driven, low-drift, maintainable, testable, and architecturally consistent. Architecture_Authority_V1_2..docx
The automation subsystem is an official architectural subsystem responsible for autonomous code-generation workflows. Architecture_Authority_V1_2..docx
README.md
# CNPOS v2

## Cinematic Narrative Planning and Orchestration System

CNPOS v2 is a deterministic, auditable, governance-driven, low-drift architecture for cinematic narrative generation, continuity management, orchestration, validation, and automation-assisted software development.

The project is built around a single governing principle:

> Architecture is the source of truth.

The architecture defines authority, ownership, module placement, naming, validation requirements, and system behaviour. Tests validate architecture. Architecture does not change merely to satisfy historical tests.

---

# Mission

The purpose of CNPOS is to provide a:

- Deterministic system
- Auditable system
- Governance-driven system
- Low-drift system
- Maintainable system
- Testable system
- Architecturally consistent system

Architectural decisions prioritise:

```text
clarity > convenience
consistency > compatibility
determinism > flexibility
architecture > tests
```

---

# Core Principles

## Architecture Authority

Architecture is the authoritative source of truth.

The following are not authoritative:

- Historical implementations
- Legacy modules
- Compatibility layers
- Aliases
- Migration bridges
- Backups
- Historical naming conventions
- Individual test expectations

Only the approved architecture and governance specifications define valid system structure.

---

## Single Source of Truth

Every responsibility must have:

```text
One module
One owner
One path
One public identity
One canonical import
```

The architecture explicitly rejects:

```text
Duplicate ownership
Replacement aliases
Parallel implementations
Compatibility wrappers
Historical duplicates
```

---

## Deterministic Behaviour

Given identical inputs, the system should produce identical outputs.

Deterministic execution is required throughout:

- Runtime processing
- Validation
- State transitions
- Automation pipelines
- Governance enforcement

---

## Low Drift Architecture

Architectural drift is actively prevented through:

- Governance validation
- Continuity validation
- Mutation validation
- Canonical naming enforcement
- Canonical import enforcement
- Approved ownership domains

---

# Canonical Architecture

## Production Architecture

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
```

## Separate Ownership Domain

```text
tests/
```

The testing subsystem is intentionally separated from production architecture and represents an independent ownership boundary.

---

# Subsystems

## Agents

The agents subsystem contains specialised workers and processing components responsible for narrative and automation activities.

Examples include:

- Character Profile Worker
- Character Continuity Worker
- Character Arc Worker
- Prompt Agent
- Code Planner Agent
- Code Writer Agent
- Code Reviewer Agent
- Code Test Agent

---

## Automation

The automation subsystem provides autonomous code-generation and architecture-maintenance workflows.

Its purpose is to assist with the controlled creation and maintenance of CNPOS modules while maintaining governance compliance.

Core automation responsibilities include:

- Planning
- Code generation
- Review
- Testing
- Rewrite coordination
- State management
- Governance loading

The automation lifecycle follows:

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

---

## Contracts

Contracts define canonical interfaces and schemas used throughout the platform.

Current contract domains include:

- Episode
- Scene
- Shot
- Render

Contracts establish consistency between producers, validators, workers, and orchestrators.

---

## Governance

The governance subsystem defines architectural rules and operational constraints.

Responsibilities include:

- Naming governance
- Import governance
- Mutation governance
- Drift prevention
- Architecture enforcement

Governance exists to ensure that all system evolution remains aligned with the approved architecture.

---

## Runtime

The runtime subsystem manages execution.

Canonical runtime ownership includes:

```text
backend_manager_v1_2.py
continuity_engine_v1_2.py
```

The runtime layer executes approved workflows and coordinates worker interactions.

---

## State

The state subsystem manages continuity and mutation information across the system.

Canonical state ownership includes:

```text
continuity_state_v1_2.py
mutation_state_manager_v1_2.py
character_mutation_classifier_v1_2.py
```

Responsibilities include:

- Continuity persistence
- Mutation tracking
- State transitions
- Character evolution classification

---

## Validators

The validator subsystem enforces architectural and operational compliance.

Canonical validators include:

```text
validator_pipeline_v1_2.py
governance_validator_v1_2.py
continuity_validator_v1_2.py
mutation_validator_v1_2.py
```

Validation order is:

```text
Contract
  ↓
Governance
  ↓
Continuity
  ↓
Mutation
```

No mutation should be accepted without successful validation.

---

## Orchestrators

Orchestrators coordinate subsystem execution.

Primary orchestration responsibilities include:

- Pipeline execution
- Runtime coordination
- Worker sequencing
- Telemetry integration
- Automation orchestration

Orchestrators manage flow, not business logic.

---

# Canonical Pipelines

## Cinematic Pipeline

Owner:

```text
orchestrators/cinematic_pipeline_v1_2.py
```

Stages:

```text
Episode
  ↓
Scene
  ↓
Shot
  ↓
Render
```

---

## Character Pipeline

Owner:

```text
orchestrators/character_pipeline_v1_2.py
```

Stages:

```text
Profile
  ↓
Continuity
  ↓
Arc
```

---

## Code Automation Pipeline

Owner:

```text
automation/code_pipeline_v1_2.py
```

Stages:

```text
AutomationPlannerAgentV1_2
  ↓
AutomationWriterAgentV1_2
  ↓
AutomationReviewerAgentV1_2
  ↓
AutomationTestAgentV1_2
```

---

# Naming Standards

## Modules

Required pattern:

```text
*_v1_2.py
```

Examples:

```text
scene_worker_v1_2.py
backend_manager_v1_2.py
validator_pipeline_v1_2.py
```

---

## Classes

Required pattern:

```text
<ClassName>V1_2
```

Examples:

```text
SceneWorkerV1_2
BackendManagerV1_2
AutomationReviewerAgentV1_2
```

---

# Import Standards

All canonical imports begin with:

```python
from cnpos.core.
```

Example:

```python
from cnpos.core.validators.validator_pipeline_v1_2 import (
    ValidatorPipelineV1_2,
)
```

Relative imports and legacy prefixes are prohibited.

---

# Development Rules

Every new module should satisfy:

```text
One module
One owner
One path
One version
One public identity

No aliases
No drift
No ambiguity
```

When conflicts occur:

```text
Architecture wins.
Tests adapt.
```

---

# Repository Status

This repository represents the clean CNPOS v2 baseline.

The architecture has been intentionally rebuilt to remove:

- Legacy compatibility layers
- Historical remediation artefacts
- Architectural drift
- Redundant ownership
- Obsolete repository structures

while preserving deterministic execution, governance enforcement, continuity management, validation integrity, and automation-assisted development.

---

# Licence

Licence information to be added.


Assessment: The uploaded documents significantly improved accuracy. The README above now reflects the authoritative architecture documents, canonical tree, governance rules, ownership boundaries, validation order, and automation pipeline definitions rather than my earlier architectural interpretation.
