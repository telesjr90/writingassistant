# PHASE8-IMPL-023 Inventory

## Parent

- ID: `PHASE8-IMPL-023`
- Title: OMI AI Tool-Assisted Analysis Candidate Review MVP
- Status: published/historical foundation
- Latest completed child: `PHASE8-IMPL-023-T023B`
- Current obligations: T023C/T023D incorporated into PHASE8-IMPL-025-T011;
  T024 incorporated into T012; T025/T026 incorporated into terminal
  PHASE8-IMPL-027. Historical identities/evidence remain preserved.
- Immediate release-blocker frontier: `PHASE8-IMPL-024-T003B`
  (`planned/next/unimplemented`)

## Owner Override Sources

- `docs/roadmap/decisions/PHASE8-IMPL-023-owner-override-ai-tool-assisted-omi-analysis-required.md`
- `docs/roadmap/decisions/PHASE8-owner-override-block-full-mvp-closeout-omi-extraction-required.md`
- `docs/roadmap/decisions/PHASE8-final-owner-accepted-gate-decision.md`
- `docs/roadmap/decisions/PHASE8-post-accepted-owner-gate-next-readiness-step-decision.md` is superseded by the owner override.
- `docs/roadmap/decisions/PHASE8-UX-004-omi-manual-workflow-repair-decision.md`
- `docs/roadmap/decisions/PHASE8-UX-004-owner-manual-test-approval.md`

## Corrected MVP Scope

OMI must analyze raw idea text through an AI/tool-assisted analysis orchestrator and present evidence-backed findings for owner review.

The MVP target is not deterministic-marker-only extraction. `PHASE8-IMPL-023-T004` remains historically complete/PASS as backend deterministic marker extraction, but it is fallback/safety baseline only and is not sufficient for MVP completion.

## Layered Architecture Follow-On

- Controlling reconciliation: `docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md`.
- New planned parent: `PHASE8-IMPL-025 - Layered Analysis Architecture and Tool Integration Expansion`.
- Existing PHASE8-IMPL-023 adapter/fusion/persistence/review work is valid foundation and remains historically complete within each recorded scope.
- Full Subtxt licensing/authorization is resolved. Official/full Subtxt runtime is authorized and planned separately under PHASE8-IMPL-025 T005/T006.
- The completed app-owned `subtxt_informed_rubric` remains distinct, valid, supplemental, deterministic, and non-official.
- Missing layers include stable source/run identity, immutable evidence lineage, richer BookNLP mappings, evidence-bounded interpretation/grounding, shared semantic guardrails, project-level diagnostics, the full NCP gateway, expanded owner corrections, and isolated layered validation.
- PHASE8-IMPL-024 T001/T002/T003A are complete/PASS and T003B is the
  immediate implementation frontier. PHASE8-IMPL-025 remains inactive until
  full PHASE8-IMPL-024 closeout, passing closeout validation, and an accepted
  `FRESH` refresh.

## Current Known Limitation

- The current OMI path can store owner-authored raw ideas and candidate records.
- A deterministic marker extractor exists for explicit owner-authored markers.
- That deterministic extractor does not satisfy the corrected MVP target by itself.
- The corrected path now has orchestrated fixture-only adapter normalization, backend fusion/dedupe/conflict/uncertainty annotations, and candidate-only persistence for safe source-bound fused findings. Those fixture/mock adapter contracts prove safety/schema compatibility only; they do not prove live analysis and do not count as MVP completion.
- Full MVP completion remains blocked until OMI and analysis run real local/runtime analysis through all selected tools, or any unavailable tool is explicitly documented as BLOCKED by owner decision, and real runtime outputs are fused, persisted as candidates only, visible for grouped owner review, and validated end to end.

## Required Tool-Assisted Sources

The corrected OMI path can use:

- Ollama / local AI model for structured candidate extraction and validation.
- Story Check for fixture-only diagnostic structural observations/questions.
- BookNLP for narrative/entity/event/coreference-style extraction where applicable.
- spaCy for local entity/entity-like extraction, sentence segmentation, and rule-assisted NLP.
- NCP primarily as an explicit validated import/export gateway; current narrow import remains candidate-only.
- Full authorized Subtxt runtime as a separate official-runtime path with source/hash/evidence/provenance and candidate-only review boundaries.
- App-owned `subtxt_informed_rubric` as deterministic fallback, supplemental diagnostic contributor, and future semantic guardrail.
- App-owned `dramatica_flow_informed_rubric` as the valid local text-level path, with any future project-level diagnostics read-only and non-mutating.

## Required Candidate Types

Candidate identification must include these types where evidence exists:

- characters
- locations
- timeline/events
- relationships
- organizations/groups
- objects/items
- plot threads or story facts
- open questions / ambiguities
- storyform/context candidates only when supportable
- diagnostics/questions where appropriate

## Required Candidate Fields

Each extracted review candidate or diagnostic finding must carry:

- candidate type
- label/name
- extracted claim
- evidence/source excerpt
- source locator
- provenance/tool source
- support/confidence as support only, not truth
- owner decision state, default pending
- candidate/review status
- diagnostics/questions where appropriate

## Architecture Inventory

- OMI analysis orchestrator receives raw idea text.
- Each adapter returns candidate findings, diagnostics, evidence, provenance, and support labels.
- Normalization converts all outputs to a common OMI candidate schema.
- Fusion/dedupe groups equivalent findings, preserves conflicts, and keeps uncertainty visible.
- Persistence stores fused evidence-backed candidates as candidate/review material only.
- UI lists what was found, grouped by type/tool/evidence.
- Owner confirms, rejects, or revises findings.

This inventory is the implemented independent-adapter foundation. The accepted PHASE8-IMPL-025 target adds Layer 0 source identity, Layer 2 immutable run evidence, Layer 4 grounding/semantic guardrails, Layer 7 explicit approved-context handoff validation, Layer 8 NCP gateway behavior, and richer work within the existing extraction/interpretation/review layers.

## Tool Boundary Inventory

- Ollama/model: completed exact-source structured extraction plus a planned distinct normalized-evidence interpretation role; neither selects truth.
- Story Check: real runtime and PHASE8-IMPL-024 T002 exact-source factual
  grounding repair are complete/PASS; layered work reuses rather than reopens it.
- BookNLP/spaCy: evidence producers; BookNLP expansion, offsets, immutable artifacts, manifests, and uncertainty metadata remain planned.
- NCP: gateway role; imports are candidates and exports default to approved context only.
- Official/full Subtxt: authorized/planned, distinct from app-owned rubric identity.
- App-owned Subtxt-informed rubric: deterministic supplemental guardrail/fallback, not official Subtxt.
- App-owned dramatica-flow-informed rubric: valid local text-level diagnostic; project-level expansion remains read-only; generation/revision/continuation disabled.
- All tools must fail closed.

## Safety Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Candidate presence is not canon.
- Candidate confidence/support is not truth.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Tool/model output is not canon.
- Approval does not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- No generated story prose.
- No rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, revision, or writing suggestion.

## Child Task Inventory

- `PHASE8-IMPL-023-T001`: historical gap audit and architecture decision; superseded only where it selected deterministic-only MVP extraction.
- `PHASE8-IMPL-023-T002`: historical expected-red raw idea to candidate listing tests.
- `PHASE8-IMPL-023-T003`: historical backend extraction contract/schema.
- `PHASE8-IMPL-023-T004`: historical deterministic/rule-based backend extractor; fallback/safety baseline only.
- `PHASE8-IMPL-023-T004A`: owner override and AI/tool-assisted OMI architecture reset.
- `PHASE8-IMPL-023-T005`: tool-assisted extraction orchestrator contract and adapter boundaries.
- `PHASE8-IMPL-023-T006`: Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests.
- `PHASE8-IMPL-023-T007`: BookNLP/spaCy local NLP candidate extraction adapters; complete/PASS as fixture-only local NLP normalization.
- `PHASE8-IMPL-023-T008`: Story Check diagnostic-only OMI handoff; complete/PASS as fixture-only diagnostic handoff normalization.
- `PHASE8-IMPL-023-T009`: NCP/Subtxt/dramatica-flow diagnostic and context adapter contracts; complete/PASS as fixture-only handoff normalization.
- `PHASE8-IMPL-023-T010`: candidate fusion, dedupe, conflict handling, and evidence/provenance normalization; complete/PASS as backend-only fusion contract.
- `PHASE8-IMPL-023-T011`: candidate-only persistence for fused AI/tool-assisted findings; complete/PASS as backend-only persistence.
- `PHASE8-IMPL-023-T012A`: real local/runtime tools required for OMI MVP roadmap reset; complete/PASS as docs/status reset only.
- `PHASE8-IMPL-023-T013`: runtime configuration, preflight, health checks, and feature flags; complete/PASS as read-only backend/runtime preflight foundation only.
- `PHASE8-IMPL-023-T014`: live spaCy integration in OMI and analysis; ready/active next.
- `PHASE8-IMPL-023-T015`: live Ollama/local model integration in OMI and analysis.
- `PHASE8-IMPL-023-T016`: live Story Check integration in OMI and analysis.
- `PHASE8-IMPL-023-T017`: live BookNLP integration in OMI and analysis.
- `PHASE8-IMPL-023-T018`: live NCP integration in OMI and analysis.
- `PHASE8-IMPL-023-T019`: complete/PASS historical app-owned Subtxt-informed rubric path; not official/full Subtxt runtime. The authorized official path is planned in PHASE8-IMPL-025 T005/T006.
- `PHASE8-IMPL-023-T020`: live dramatica-flow integration in OMI and analysis.
- `PHASE8-IMPL-023-T021`: cross-tool fusion validation using real runtime outputs.
- `PHASE8-IMPL-023-T022`: candidate-only persistence validation using real runtime outputs.
- `PHASE8-IMPL-023-T023`: grouped owner-review UI for real runtime findings.
- `PHASE8-IMPL-023-T024`: historical automated end-to-end intent incorporated
  into PHASE8-IMPL-025-T012.
- `PHASE8-IMPL-023-T025`: historical manual live-project intent incorporated
  into PHASE8-IMPL-027.
- `PHASE8-IMPL-023-T026`: historical closeout identity superseded for current
  full-MVP closeout by PHASE8-IMPL-027.

## UI/UX Audit Reconciliation Dependency

The successful reconciliation collector is scoped evidence collection, not product-wide validation. It verified P0-A guided-creation input loss and P0-B ungrounded Story Check findings. Those defects are owned by `PHASE8-IMPL-024`; they do not change T023A/T023B completion but block broad owner acceptance and T026 closeout. Failed `playwright-advanced` attempts are excluded, and advanced mutation/apply-promotion/approved-data workflows remain `NOT_YET_TESTED`.

## UI/UX Inventory

- Raw idea intake state.
- Analysis status/progress/result.
- Candidate grouping by type.
- Tool/provenance grouping and display.
- Evidence/source locator display.
- Conflict and uncertainty display.
- Empty/fail-closed states.
- Review queue clarity.
- Error messages.
- Confirm/reject/revise owner decision actions.
- Clear next action after analysis.

## Validation Commands

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```
