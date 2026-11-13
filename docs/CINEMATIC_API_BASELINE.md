# Cinematic v1_2 API baseline reconciliation

**Status:** blocked before end-to-end implementation evidence  
**Reviewed ref:** `main` at `f5b2711f700fa13d1055c2ae1dbb582e00b8449a`  
**Scope:** record the observed API, stale-test mismatches, and missing evidence only. No contract, architecture, canonical path, ownership, or test-location changes are made by this report.

## Authority and boundary

`GOVERNANCE.md` is authoritative. Pip563 is the Project Owner and Architecture Authority. The internal baseline is v1_2. The cinematic MVP is a validated render-job package—not generated or assembled video/audio (`README.md`, `ROADMAP.md`, and `GOVERNANCE.md`).

The repository's Pipeline MVP issue #1 records Pip563's approval to proceed with the HIGH_RISK MVP within its stated scope. It explicitly requires verifying the current API, contracts, tests, and checks first, and prohibits architecture, contract, ownership, or test-location changes without separate approval.

## Observed pipeline API

At the reviewed ref, `cnpos/core/orchestrators/cinematic_pipeline_v1_2.py` declares:

- `CinematicPipelineV1_2.__init__(backend_manager=None, continuity_engine=None, validator_pipeline=None, governance_loader=None, governance_validator=None, worker_registry=None)`.
- `run(episode_payload, context=None)`.
- A result mapping with `domain`, `version`, `episode`, `scenes`, `shots`, `render`, `continuity`, and `context`.
- An intended sequence of governance validation, episode, scenes, shots, render, then continuity.
- Worker calls using `episode_payload=...` for the episode and scenes workers, `scenes_payload=...` for shots, and episode/scenes/shots payloads for render.

That is the apparent orchestration interface, not a confirmed runnable API: the imported worker modules and the orchestrator's calls do not agree on the worker signatures in the checked-in source reviewed. Do not treat this interface as an accepted, functioning end-to-end contract until those source discrepancies have been resolved against Pip563's approved v1_2 implementation.

## Worker and source discrepancies

The expected worker-level shape, based on the worker modules and checked-in contracts, is a worker accepting its stage payload and optional context, returning a stage result with validated payload/backend result, and using the Episode, Scene, Shot, or Render v1_2 contract as appropriate. The checked-in files do not consistently implement that expectation:

| Expected path | Observed discrepancy |
|---|---|
| `cnpos/core/runtime/workers/episode_worker_v1_2.py` | The content returned at this path defines `BackendManagerV1_2`, rather than the imported `EpisodeWorkerV1_2` symbol. |
| `cnpos/core/runtime/workers/scene_worker_v1_2.py` | Defines `SceneWorkerV1_2` with `run(payload, context=None)`, but the orchestrator passes `episode_payload=`. The file also contains the malformed statement `bacackend_manager: Optional[BackendManagerV1_2] = None,ontext = context or {}`. |
| `cnpos/core/runtime/workers/shot_worker_v1_2.py` | The content returned at this path defines `SceneWorkerV1_2`, not the imported `ShotWorkerV1_2` symbol. |
| `cnpos/core/runtime/workers/render_worker_v1_2.py` | The content returned at this path defines `ShotWorkerV1_2`, not the imported `RenderWorkerV1_2` symbol. |
| `cnpos/core/orchestrators/cinematic_pipeline_v1_2.py` | Constructs Scene and Shot workers with a `continuity_engine=` argument, while the observed Scene/Shot constructors do not accept that argument. It then invokes a continuity `run()` method; the reviewed `ContinuityEngineV1_2` exposes `evaluate(domain, new_payload)` and `get_active_state(domain)`, not `run()`. |

These are blocking source/API inconsistencies, not a reason to alter the approved architecture or contracts. The source returned from the repository paths should be checked against the approved source of truth before implementation. This report does not infer a replacement implementation.

## Stale tests

`cnpos/tests/test_cinematic_pipeline_v1_2.py` is stale relative to the pipeline source:

- It injects `prompt_agent`, `continuity_state`, `mutation_classifier`, and `mutation_state_manager`; those are not parameters of the pipeline constructor.
- It asserts private attributes such as `_prompt_agent`, `_continuity_state`, and `_mutation_classifier` that the current pipeline constructor does not initialize.
- Its end-to-end case calls `pipeline.run(request=request)`, while the declared public method is `run(episode_payload, context=None)`.
- The fake continuity engine implements `update(...)`; the current continuity engine interface is `evaluate(domain, new_payload)`.
- Fakes and assertions expect backend `route(...)` calls and worker registry lookups, but the inspected pipeline's stage workers are instantiated directly and execute through `run_task(...)`.
- Its fake validator overrides `validate(payload)` only, while stage workers call `validate(domain=..., payload=..., contract_schema=..., governance_loader=...)`.

The per-worker tests also contain stale assumptions: `cnpos/tests/test_episode_worker_v1_2.py` expects injected prompt/continuity/mutation dependencies not declared by the observed Episode worker source. The Scene and Render worker tests assume `run(request=...)`, a `BaseWorker` inheritance/phase attributes, and domain/phase behaviors not established by the v1_2 worker code. These tests should be rewritten only after the actual approved worker modules have been restored/confirmed; otherwise they would encode guesses rather than the approved API.

The target test ownership domain is top-level `tests/`, but current tests live under `cnpos/tests/`. Per scope, this discrepancy is recorded only; no test relocation is performed.

## Contract and governance findings

The checked-in contracts are present at:

- `cnpos/core/contracts/episode_contract_v1_2.json`
- `cnpos/core/contracts/scene_contract_v1_2.json`
- `cnpos/core/contracts/shot_contract_v1_2.json`
- `cnpos/core/contracts/render_contract_v1_2.json`

They require structured v1_2 episode, scene, shot, and render payloads. In particular, Render requires `domain`, `version`, `render_id`, `episode_id`, `status`, and `output`; render status is one of `queued`, `running`, `completed`, `failed`, or `cancelled`. Package-level cross-reference checks (shot-to-scene/episode, ordering, identifiers, path existence) are not demonstrated by the schema presence alone.

Governance requires prior approval for high-risk execution behavior and requires traceable validation/review evidence. The existing issue approval applies to the scoped MVP; it is not evidence that the checked-in implementation conforms or that tests pass.

## Missing acceptance evidence / blockers

No evidence was established in this review for:

1. A clean-checkout command that runs one episode through the current real worker chain.
2. A deterministic local fake backend exercised through those actual workers.
3. Schema validation of actual Episode, Scene, Shot, and Render artifacts.
4. A finalized package directory containing the manifest, narrative/prompt/support artifacts, stable references, and continuity/validation report.
5. Cross-reference/path checks that reject missing or broken package inputs.
6. Positive and negative continuity tests that block finalization on mismatch.
7. Equivalent outputs across repeat runs, or clear pipeline-failure behavior.
8. Exact local test commands/results or successful configured CI. No workflow file was established in the inspected `.github` contents.

No test command was run in this review; therefore no passing/failing test result is claimed.

## Safe next actions

1. Ask Pip563 to identify/confirm the approved v1_2 worker source for the mismatched paths, or restore those files from the explicitly approved implementation. Keep the existing contract set and canonical paths unchanged.
2. Reconcile each worker constructor, `run` signature, and return shape with the approved `CinematicPipelineV1_2` stage calls. Treat any API or execution correction as HIGH_RISK and keep it within issue #1's explicit approval/scope.
3. Once the source/API is confirmed, rewrite the existing cinematic and affected worker tests in place under `cnpos/tests/` to call the real signatures and validate real v1_2 contract artifacts. Do not relocate tests.
4. Add a minimal single-episode integration test using deterministic fakes, followed by contract, continuity-negative, package-reference, and deterministic-repeat coverage required by issue #1.
5. Run checks from a clean environment and record exact commands and outputs in the PR/issue. Claim MVP completion only after those results and review evidence are available.

## Evidence links

- [Pipeline implementation](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/cnpos/core/orchestrators/cinematic_pipeline_v1_2.py)
- [Cinematic pipeline tests](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/cnpos/tests/test_cinematic_pipeline_v1_2.py)
- [Episode contract](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/cnpos/core/contracts/episode_contract_v1_2.json)
- [Scene contract](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/cnpos/core/contracts/scene_contract_v1_2.json)
- [Shot contract](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/cnpos/core/contracts/shot_contract_v1_2.json)
- [Render contract](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/cnpos/core/contracts/render_contract_v1_2.json)
- [Governance policy](https://github.com/Pip563/cnpos-v2/blob/f5b2711f700fa13d1055c2ae1dbb582e00b8449a/GOVERNANCE.md)
- [Approved MVP issue and scope](https://github.com/Pip563/cnpos-v2/issues/1)
