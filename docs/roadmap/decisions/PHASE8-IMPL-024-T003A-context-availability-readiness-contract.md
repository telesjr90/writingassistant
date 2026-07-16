# PHASE8-IMPL-024-T003A Context Availability and Readiness Contract

## Decision

`PHASE8-IMPL-024-T003A - Context-availability/readiness contract for Bible, storyform, and storyform-context` is complete/PASS. The canonical application-owned contract is the deterministic read-only `GET /api/projects/{project_name}/context-readiness` endpoint with schema version `project_context_readiness.v1`.

The existing project-list metadata, direct Bible route, direct storyform route, storyform-context route, and OMI runtime preflight retain their established semantics. The OMI preflight remains project-agnostic and tool/runtime-oriented; it is not a substitute for project-resource readiness. T003A therefore adds one dedicated endpoint rather than overlapping resource-specific readiness endpoints or changing direct-load behavior.

## Contract

Every response identifies the project and reports Bible, storyform, and storyform-context in a stable order. Each resource exposes:

- `resource_id` and `resource_type`;
- `exists`, `structurally_valid`, and `ready` booleans;
- stable `state` and nullable `reason_code`;
- at most three controlled diagnostic messages; and
- a safe project-relative `source_locator`.

The stable state vocabulary is:

- `absent` — an optional stored resource does not exist;
- `invalid` — a stored resource exists but its encoding, JSON shape, or accepted schema is invalid;
- `unavailable` — a derived resource or deterministic validation/construction prerequisite is unavailable;
- `ready` — the resource is present or deterministically derived, structurally valid, and ready for its intended consumer; and
- `not_applicable` — reserved for a future repository-evidence-proven non-applicable state. Current project evidence does not require emitting it for these three resources.

No confidence value is used as truth. Availability implies neither owner approval, canon status, story truth, candidate promotion, nor durable Memory/Canon status.

## Resource Rules

### Bible

`bible.json` is absent when the optional file does not exist. It is ready only when it is a regular UTF-8 JSON object. Malformed JSON, unsupported encoding, and unsupported/non-object structure are invalid with stable Bible-specific reason codes. Filename presence alone is insufficient.

### Storyform

`storyform.json` is absent when the optional file does not exist. It is ready only when it is a regular UTF-8 JSON object and passes the existing authoritative `Storyform.validate_data` schema validator. Malformed JSON, unsupported encoding/shape, and schema validation failure are distinct invalid reasons. If the deterministic validator input is unavailable, the storyform is unavailable rather than guessed valid or repaired.

### Storyform-context

Storyform-context is derived in memory from the existing validated storyform through `Storyform.to_prompt_context`; no context file is created. It is ready only when the underlying storyform is ready and deterministic construction returns non-empty context. The contract distinguishes underlying storyform absence, underlying storyform invalidity, unavailable validator prerequisites, empty derived context, and construction failure. It never fabricates Storyform values, classifies Dramatica elements, invokes a model, or persists derived context.

The report-level `all_ready` value requires all three resources to be ready, matching the combined Bible/storyform prerequisites of the non-mock Story Check source-context path without invoking Story Check.

## Absence, Invalidity, and Request Failures

Normal optional-resource absence is an HTTP-success readiness response with explicit `absent`/dependent `unavailable` states. T003B can use it before direct resource loads, avoiding speculative missing-resource requests and noisy normal 404 responses.

Invalid resources remain successful readiness responses with `ready: false`, stable reason codes, bounded diagnostics, and no raw content or exception traces. T003A never repairs, rewrites, or creates a resource.

Genuine request failures are not collapsed into absence: unsafe project IDs or resource locators return 400; a missing project returns 404; permission/read failures and unexpected server failures return controlled 500 responses. No absolute host path is returned.

## Safety and Non-Mutation

The contract is local-first, deterministic, read-only, model-free, candidate-neutral, and non-canon. It invokes no Story Check, OMI analysis, Ollama, BookNLP, spaCy, NCP, Subtxt, dramatica-flow, external service, candidate persistence, promotion, apply-promotion, or Memory/Canon mutation. It creates no Bible, storyform, storyform-context, training, dataset, model-artifact, or story-prose output.

## Files Changed

- `backend/context_readiness.py`
- `backend/main.py`
- `tests/test_context_readiness.py`
- `tests/test_context_routes.py`
- authoritative PHASE8-IMPL-024 task, status, index, inventory, enrichment, backlog, phase-map, risk, open-question, and decision records

The `tests/test_context_routes.py` change completes its existing lightweight FastAPI stub (`Request`, `APIRouter`, responses, middleware, and route registration) so the directly related hermetic route regression collects without installing FastAPI.

## Validation

- Focused T003A contract: `8 passed`.
- Directly related backend regression set: `268 passed` across context readiness/routes, project storage, storyform, request guards, Story Check engine/grounding, and OMI runtime preflight.
- `tests/test_project_creation.py` was not included in the related batch because it requires the absent FastAPI package; package installation is forbidden and project-creation behavior is unchanged. Temporary-project creation/storage behavior is covered by the focused readiness tests and `tests/test_project_manager.py`.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- `git diff --check`: PASS.

## Remaining Work

T003 remains active/in progress. `PHASE8-IMPL-024-T003B` is next and owns conditional frontend loading and presentation of absent, invalid, and request-failure states. `PHASE8-IMPL-024-T003C` remains planned and owns browser console/network regression validation. T004 and later PHASE8-IMPL-024 tasks remain planned. PHASE8-IMPL-025 remains published/planned and inactive. Broad owner acceptance and MVP readiness remain blocked.
