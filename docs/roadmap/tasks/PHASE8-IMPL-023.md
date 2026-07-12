# PHASE8-IMPL-023 - OMI AI Tool-Assisted Analysis Candidate Review MVP

## Status

Published and active.

Latest completed child: `PHASE8-IMPL-023-T023B - Grouped-review React UI and owner-decision integration`.

T023 remains in progress. T023C and T023D remain planned. T024-T026 remain reserved and incomplete.

The immediate release-blocker frontier is now the separate `PHASE8-IMPL-024` parent, beginning with backend-only `PHASE8-IMPL-024-T001A`. The UI/UX audit does not invalidate or downgrade T023A/T023B, but broad owner acceptance and PHASE8-IMPL-023 closeout are blocked until the PHASE8-IMPL-024 P0 integrity repairs and their focused validation pass.

Full MVP completion closeout remains blocked by the PHASE8-IMPL-024 P0 integrity work and the missing layered-architecture gates now owned by PHASE8-IMPL-025. Scoped real-runtime fusion, candidate-only persistence, and grouped-review foundations already exist and remain valid; they are not proof that the full target is complete. Subtxt licensing/authorization is resolved and cannot be used as an owner-blocked closeout exception.

## Goal

Build the real MVP OMI path where raw idea input is analyzed by an AI/tool-assisted analysis orchestrator and converted into structured, evidence-backed review candidates for owner review.

## Owner Override

Deterministic-marker-only extraction is not the MVP OMI target.

MVP OMI requires tool-assisted analysis that can use Ollama/local AI models, Story Check, BookNLP, spaCy, NCP, Subtxt, and dramatica-flow. Tool output must become evidence-backed candidates only.

`PHASE8-IMPL-023-T004` remains historically complete/PASS as backend deterministic marker extraction, but it is superseded and re-scoped as a fallback/safety baseline only. It is not sufficient for MVP completion by itself.

## Layered Architecture Reconciliation

`docs/roadmap/decisions/PHASE8-IMPL-025-layered-analysis-architecture-and-subtxt-owner-authorization.md` preserves this parent's completed work as foundation and publishes the missing layered-plus-parallel path under the separate planned `PHASE8-IMPL-025` parent.

- Current foundation: independent adapters -> normalization -> fusion/conflict/uncertainty -> candidate persistence -> owner review.
- Missing prerequisites/consumers: stable source identity and exact source snapshots/hashes/maps; immutable `AnalysisRunManifest`; immutable raw artifact/evidence lineage; expanded BookNLP mappings; full authorized Subtxt runtime; evidence-bounded Ollama/Story Check; shared semantic guardrails; project-level diagnostics; full NCP gateway; expanded correction workflows; isolated layered validation.
- Full Subtxt licensing and authorization concerns are resolved. Full runtime is authorized and planned separately in PHASE8-IMPL-025 T005/T006.
- T019C-T019F remain complete/PASS for the app-owned `subtxt_informed_rubric`; they are not official/full Subtxt execution and are not downgraded.
- T023A and T023B remain complete/PASS. Existing persisted findings remain pending, unapproved, promotion-ineligible, candidate-only, and non-canon.
- The immediate implementation task remains `PHASE8-IMPL-024-T001A`; PHASE8-IMPL-024 T001/T002 precede PHASE8-IMPL-025 activation.

## Current Gap

The current OMI path includes real spaCy, Ollama, Story Check, BookNLP, and NCP-import execution; both app-owned rubrics; deterministic fusion/conflict/uncertainty; candidate-only persistence; and grouped-review UI foundations. The deterministic marker extractor remains fallback-only, and fixture contracts remain schema/safety evidence rather than substitutes for live proof.

The immediate gaps are P0 guided-creation integrity and Story Check factual grounding. The subsequent architecture gaps are stable source/run identity, immutable raw/evidence lineage, expanded BookNLP output, official/full authorized Subtxt runtime, evidence-bounded interpretation, shared semantic guardrails, read-only project diagnostics, full NCP approved export/round trip, expanded owner corrections, and isolated end-to-end validation.

Technical unavailability must remain explicit and fail closed. Full Subtxt runtime work is planned and may not be omitted or reclassified as owner-blocked for licensing/authorization reasons.

## MVP Behavior

- User enters or saves raw idea text in OMI.
- OMI runs tool-assisted analysis through the orchestrator.
- Adapters return candidate findings, diagnostics, evidence, provenance, source locators, and support labels.
- The normalization layer converts all outputs to the common OMI candidate schema.
- The fusion/dedupe layer groups equivalent findings and keeps conflicts or uncertainty visible.
- The UI lists findings grouped by type, tool/provenance, and evidence.
- The owner confirms, rejects, or revises findings.
- Candidate presence is not canon, confidence is not truth, queue presence is not approval, and tool/model output is not canon.

## Candidate Types

Candidate types include, where evidence exists:

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

Each finding must carry:

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

## Architecture

- OMI analysis orchestrator receives raw idea text.
- Tool adapters perform bounded analysis and return candidate findings only.
- Normalization converts every adapter output to the common OMI candidate schema.
- Fusion/dedupe groups equivalent findings, preserves conflicts, and shows uncertainty.
- Persistence stores fused evidence-backed candidates as candidate/review material only.
- UI lists what was found and lets the owner confirm, reject, or revise.

This architecture is an implemented independent-contributor foundation, not the complete target. The accepted target layers source identity, raw extraction, immutable run evidence, interpretation, grounding/semantic guardrails, fusion, candidate review, explicit promotion/approved context, and the NCP gateway while still allowing independent contributors to run in parallel when their declared inputs are satisfied.

## Tool Boundaries

- Ollama/model: the completed exact-source structured extraction path remains valid; PHASE8-IMPL-025 adds a distinct evidence-bounded interpretation role over normalized evidence. Both are source/hash/evidence/provenance-bound and non-canon.
- Story Check: real runtime execution is complete/PASS, but PHASE8-IMPL-024 T002 remains the P0 exact-source/hash/factual-grounding/quarantine repair. PHASE8-IMPL-025 consumes that repair without duplicating it.
- BookNLP/spaCy: evidence producers only. Current real character/location/entity-style findings remain valid; BookNLP alias/coreference, quotes/speakers, events, possessions, richer entity types, offsets, artifacts, and run manifests remain planned.
- NCP: primarily an explicit import/export gateway. The current owner-selected candidate-import validator is a valid narrow foundation; external status is not local approval and approved-context export remains planned.
- Official/full Subtxt: authorized and planned separately under PHASE8-IMPL-025 T005/T006 with official identity/version/model/provider provenance, analysis allowlist, generation/rewrite/mutation blocklist, source hashes, evidence ledger, candidate-only persistence, and grouped-review validation.
- App-owned `subtxt_informed_rubric`: preserved deterministic fallback, supplemental contributor, and future semantic guardrail; never official Subtxt output and never automatic Dramatica truth.
- App-owned `dramatica_flow_informed_rubric`: preserved local text-level rubric; future project-level causal/thread/information/relationship/emotional/promise-payoff/hook diagnostics are read-only candidates only. Generation/revision/continuation and truth-state mutation remain forbidden.
- All tools fail closed.

## Acceptance Criteria

- Given raw idea text, OMI can produce non-empty tool-assisted candidate findings where evidence exists.
- Candidate list is visible in the UI and grouped by type.
- Each candidate has candidate type, label/name, extracted claim, evidence/source excerpt, source locator, provenance/tool source, support label, status, and owner decision state.
- Diagnostics/questions are shown where appropriate without writing or suggesting story prose.
- Empty or unsupported analysis fails closed with a clear explanation and does not create misleading empty shells.
- UI clearly separates extracted candidates from approved Memory/Canon.
- No automatic Memory/Canon mutation occurs.
- No automatic apply-promotion occurs.
- No generated story prose is produced.
- Tool/model output is never treated as canon or truth.

## UI/UX Improvement Scope

- Better raw idea intake state.
- Clear analysis status, progress, and result.
- Clear candidate grouping by type.
- Empty and fail-closed states.
- Review queue clarity.
- Evidence/provenance/source locator display.
- Conflict/uncertainty display.
- Better error messages.
- Clear next action after candidate analysis.

## Boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- No generated prose.
- No rewrite, continuation, outline, draft, polish, improvement, expansion, imitation, revision, or writing suggestion.
- Confidence/support is not truth.
- Candidate presence is not canon.
- Candidate persistence is not canon.
- Queue presence is not approval.
- Tool/model output is not canon.
- Candidate approval does not automatically mutate Memory/Canon.
- Apply-promotion remains explicit, audited, owner-confirmed, and separate.
- Raw idea analysis must not write, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, suggest, or produce story prose.

## Child Task Sequence

- `PHASE8-IMPL-023-T001` - Historical gap audit and architecture decision. Scope: docs/decision and narrow source audit only; superseded only where it selected deterministic-only MVP extraction.
- `PHASE8-IMPL-023-T002` - Historical expected-red raw idea to candidate listing tests. Scope: tests-first expected-red only under the previous path.
- `PHASE8-IMPL-023-T003` - Historical backend extraction contract/schema. Scope: contract/schema implementation under the previous path.
- `PHASE8-IMPL-023-T004` - Historical deterministic/rule-based backend extractor. Scope: fallback/safety baseline only; not sufficient for MVP completion.
- `PHASE8-IMPL-023-T004A` - Owner override and AI/tool-assisted OMI architecture reset. Scope: docs/status/architecture correction only; complete/PASS.
- `PHASE8-IMPL-023-T005` - Tool-assisted extraction orchestrator contract and adapter boundaries. Scope: corrected orchestrator contract and adapter boundaries.
- `PHASE8-IMPL-023-T006` - Ollama/model-assisted structured extraction contract with JSON/schema validation and no-prose tests. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T007` - BookNLP/spaCy local NLP candidate extraction adapters. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T008` - Story Check diagnostic-only OMI handoff. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T009` - NCP/Subtxt/dramatica-flow diagnostic and context adapter contracts. Scope: fixture-only; complete/PASS.
- `PHASE8-IMPL-023-T010` - Candidate fusion, dedupe, conflict handling, and evidence/provenance normalization. Scope: backend-only contract; complete/PASS.
- `PHASE8-IMPL-023-T011` - Candidate-only persistence for fused AI/tool-assisted findings. Scope: backend-only; complete/PASS.
- `PHASE8-IMPL-023-T012A` - Real local/runtime tools required for OMI MVP roadmap reset. Scope: complete/PASS; docs/status reset only.
- `PHASE8-IMPL-023-T013` - Runtime configuration, preflight, health checks, and feature flags. Scope: complete/PASS; read-only backend/runtime preflight foundation only; no live tool/model analysis.
- `PHASE8-IMPL-023-T014` - Live spaCy integration in OMI and analysis. Scope: ready/active next.
- `PHASE8-IMPL-023-T015` - Live Ollama/local model integration in OMI and analysis.
- `PHASE8-IMPL-023-T016` - Live Story Check integration in OMI and analysis.
- `PHASE8-IMPL-023-T017` - Live BookNLP integration in OMI and analysis.
- `PHASE8-IMPL-023-T018` - Live NCP integration in OMI and analysis.
- `PHASE8-IMPL-023-T019` - Historical Subtxt path complete/PASS for the app-owned Subtxt-informed rubric sequence; full official/authorized Subtxt runtime is a separate planned PHASE8-IMPL-025 T005/T006 path and T019 is not reclassified as official runtime execution.
- `PHASE8-IMPL-023-T020` - Live dramatica-flow integration in OMI and analysis.
- `PHASE8-IMPL-023-T021` - Cross-tool fusion validation using real runtime outputs.
- `PHASE8-IMPL-023-T022` - Candidate-only persistence validation using real runtime outputs.
- `PHASE8-IMPL-023-T023` - Grouped owner-review UI for real runtime findings.
- `PHASE8-IMPL-023-T024` - Automated end-to-end live OMI test.
- `PHASE8-IMPL-023-T025` - Manual Cyber Detective Story live OMI test.
- `PHASE8-IMPL-023-T026` - Historical closeout identity retained; current closeout must also account for PHASE8-IMPL-024 P0 integrity and PHASE8-IMPL-025 layered gates. Subtxt licensing/authorization cannot satisfy the historical owner-blocked branch.

Audit-reconciliation dependency: T023C/T023D and T024-T026 retain their identities and planned status. They do not satisfy guided-creation persistence, Story Check grounding, or product-wide validation. `PHASE8-IMPL-024-T001A` is the next implementation task before broad readiness work resumes.

Architecture-reconciliation dependency: PHASE8-IMPL-025 is a separate planned non-UI parent. It does not overload PHASE8-IMPL-024's repair children or downgrade PHASE8-IMPL-023 results. It adds the missing source/run/evidence layers, full Subtxt runtime, expanded BookNLP/NCP/guardrail/diagnostic/review work, and layered validation after PHASE8-IMPL-024 T001/T002.

## Non-Goals

- Do not mark full MVP complete in this parent reset.
- Do not run extraction in this parent reset.
- Do not create candidates in this parent reset.
- Do not mutate Memory/Canon.
- Do not create promotion records.
- Do not run apply-promotion.
- Do not run Ollama/models, Story Check, BookNLP, spaCy, NCP, Subtxt, or dramatica-flow in this parent reset.
- Do not generate, rewrite, continue, outline, draft, polish, improve, expand, imitate, revise, suggest, or produce story prose.
- Do not create training data, JSONL records, datasets, model artifacts, or fine-tuning configs.
- Do not stage, commit, or push unless explicitly requested.

## Validation Commands

Parent reset validation:

```bash
python3 scripts/check_enrichment.py
python3 scripts/validate_roadmap.py
python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null
git diff --check
git status --short --branch
git diff --name-only
```
