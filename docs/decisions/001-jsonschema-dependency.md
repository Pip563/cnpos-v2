# Decision: use `jsonschema` for v1_2 contract validation

- **Decision owner:** Pip563 (Project Owner and Architecture Authority)
- **Decision status:** approved
- **Scope:** declare `jsonschema` as a project dependency and use it to validate the existing checked-in Episode, Scene, Shot, and Render v1_2 JSON Schemas for the cinematic MVP package.
- **Approval source:** Pip563's explicit approval recorded in the project conversation on 2026-11-14.
- **Contract impact:** none. This decision does not authorize changing the existing v1_2 schemas or introducing a new contract.
- **Architecture impact:** dependency strategy changes are classified as ARCHITECTURAL under `GOVERNANCE.md`; Pip563 has approved this specific dependency addition. This is not blanket approval for additional dependencies or architecture changes.
- **Product boundary:** validation is for a render-job package specification. It does not implement or claim actual video/audio rendering.
- **Implementation record:** `pyproject.toml` declares `jsonschema` on branch `feature/cinematic-workers-and-package-mvp` in commit `09c46f91867c1806e9b9ff0c809248ccff746753`.
- **Validation evidence:** pending. The dependency installation, schema validation, tests, and package-producing example must be run and recorded before claiming the MVP works.

## Required governance-document follow-up

Pip563 directed that the dependency approval be reflected in the original `GOVERNANCE.md`, not only in this decision record. The governance amendment should state this narrow approval and preserve the existing requirement that future dependency-strategy changes require prior approval. Do not edit other governance policy as part of this amendment.
