# Module Registry

## Purpose and authority

This registry records currently declared canonical module identities and approved subsystem ownership domains for CNPOS. It supports explicit ownership and drift detection; it does not independently create or approve architecture.

[`GOVERNANCE.md`](GOVERNANCE.md) is the authoritative policy. Pip563 is the sole Project Owner and Architecture Authority. The approved architecture and decisions made by Pip563 define canonical structure and ownership. A registry entry, directory, test, or implementation cannot silently amend them.

A subsystem owner label such as `Runtime` or `Contracts` identifies an ownership domain, not a named individual. Each production module must have an accountable owner recorded in an approved ownership record. If one is absent or disputed, flag it for Pip563; do not infer an individual from authorship or path.

## Approved target structure

The approved production domain is under `cnpos/core/`; the separate test ownership domain is top-level `tests/`:

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

This is the approved target structure, not a claim that the current checkout conforms. The current repository includes `cnpos/tests/` and modules with noncanonical names, among other items that may require review. Record these as drift and resolve them under governance; do not move, rename, delete, or bless them without required approval.

## Declared leaf module identities

The following are the explicit leaf module identities in the registry baseline. Their listing does not establish that the module has been tested, is complete, or is actively used. Status records the registry declaration only.

| Module ID | Canonical path | Public identity | Ownership domain | Registry status |
|---|---|---|---|---|
| `cnpos.core.runtime.backend_manager_v1_2` | `cnpos/core/runtime/backend_manager_v1_2.py` | `BackendManagerV1_2` | Runtime | Declared |
| `cnpos.core.runtime.continuity_engine_v1_2` | `cnpos/core/runtime/continuity_engine_v1_2.py` | `ContinuityEngineV1_2` | Runtime | Declared |
| `cnpos.core.automation.code_pipeline_v1_2` | `cnpos/core/automation/code_pipeline_v1_2.py` | `CodeAutomationPipelineV1_2` | Automation | Declared |

These entries are the current explicit leaf-module baseline, not a complete list of every source file present in the repository. Additional production modules require an approved canonical identity and explicit owner before they are treated as registered modules.

## Subsystem ownership domains

The following approved boundaries describe subsystem responsibilities. They do not designate named individuals.

| Domain | Responsibility |
|---|---|
| Agents | Specialized workers and narrative-processing roles |
| Automation | Bounded planning, scaffolding, code generation, review support, and validation support |
| Contracts | Canonical schemas, interfaces, and compatibility discipline |
| Governance | Policy rules and governance enforcement mechanisms, subject to project authority in `GOVERNANCE.md` |
| Orchestrators | Pipeline coordination, sequencing, and flow control |
| Runtime | Execution behavior and backend/runtime coordination |
| State | Continuity, mutation, and state integrity |
| Validators | Contract, governance, continuity, and mutation enforcement |
| Tests | Verification evidence in the separate top-level test domain |

## Identity and naming rules

Approved v1_2 production modules follow these canonical rules unless Pip563 records an explicit exception or architecture decision:

- file names use `*_v1_2.py`;
- public classes use `<ClassName>V1_2`;
- canonical imports begin with `from cnpos.core.`;
- canonical production modules use absolute canonical imports, not relative or legacy imports;
- one responsibility has one canonical module, path, owner, public identity, and import.

A rule is a target requirement; this registry does not claim that an automated check currently enforces it. Existing deviations are drift pending review, not automatic permission for mass renaming or deletion.

## Registration and status

A module becomes registered only after its canonical path, public identity, and accountable owner are approved and recorded. A proposed or unregistered module must not be presented as canonical merely because it exists or is imported by code.

Use these registry statuses:

| Status | Meaning |
|---|---|
| Declared | Explicitly listed in the current registry baseline; completeness and runtime use are not implied |
| Proposed | Submitted for review; not an approved canonical module |
| Non-compliant | Present but known to conflict with an approved requirement or missing required ownership/identity |
| Deprecated | Retained for reference but not approved for new use, with migration or removal decision recorded |

Do not mark an entry `Active` or complete without evidence of approved status and intended use.

## Drift handling

When registry and repository disagree:

1. identify the file/module and the precise mismatch;
2. determine whether the registry, implementation, or approved architecture is stale;
3. assign an accountable owner or ask Pip563 to resolve missing ownership;
4. classify the remediation and obtain any required approval before changing policy, architecture, paths, contracts, or ownership;
5. implement the approved remediation and record validation evidence;
6. update this registry only to reflect an approved decision.

Tests and runtime results are evidence, not authority to change canonical identities. Do not create aliases or compatibility wrappers to hide drift unless Pip563 explicitly approves an exception or migration design.

## Completion standard

A module is complete only when its approved canonical path, owner, public identity, contract, implementation, validation, relevant tests, documentation, review, and registry entry are consistent, and no blocking drift remains. Presence in this registry alone is not evidence of completion or production readiness.

For the cinematic MVP, the registered/render contract boundary targets a validated render-job package. It does not imply actual video/audio rendering.
