# PHASE8-IMPL-020-T002 Model-assisted extraction and diagnostic workflow boundary decision

## Status

Accepted. `PHASE8-IMPL-020-T002` is complete/PASS as docs/decision only.

This decision performs no model calls, no Ollama calls, no model-assisted extraction implementation, no backend implementation, no frontend implementation, no tests, no routes, no UI, no package/dependency changes, no candidate records, no review queue entries, no apply-promotion, no approved memory/canon mutation, no training artifacts, and no generated prose.

`PHASE8-IMPL-020-T003` is ready/active next for expected-red model-assisted extraction contract tests. `PHASE8-IMPL-020-T004`, `PHASE8-IMPL-020-T005`, `PHASE8-IMPL-020-T006`, and `PHASE8-IMPL-020-T007` remain planned. `PHASE8-IMPL-021` and `PHASE8-IMPL-022` remain future MVP-required parents. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden. `PHASE8-UX-001` remains read-only terminology/boundary reference only.

## Decision

Future model-assisted evidence-backed extraction and diagnostic workflow may be introduced only by later explicitly scoped children after tests. The accepted boundary is local-first, path-safe, evidence-backed, candidate-first, owner-review-required, and fail closed.

Model-assisted output may support only evidence-backed candidate observation, diagnostic question, uncertainty note, insufficient-evidence note, candidate extraction support, safe refusal / blocked request result, and unavailable / fail-closed / quarantined result.

Confidence is not truth. Model output is not canon. No model output as truth. No silent fallback may claim model-assisted extraction succeeded.

## 1. Request Boundary

Future model-assisted requests must be path-safe and must operate only over owner-authored or owner-provided project text/materials.

Requests must carry `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available. Requests must separate raw source text from user intent. Requests must include explicit guard confirmations for no-prose, no-rewrite, no-continuation, no-outline, no-training, no-canon, and no-apply-promotion.

Missing required refs or unsafe paths must fail closed. Owner-authored prose storage/editing is allowed and must not be misclassified as a model-generation request.

## 2. Model-use Boundary

T002 itself performs no model calls.

Future model-assisted runtime may only be introduced by later explicitly scoped children after tests. Future model assistance must be local-first and guarded. Future model output may support only evidence-backed candidate observations, diagnostic questions, uncertainty notes, and candidate extraction support.

Model output must never be treated as truth by confidence score, fluent wording, diagnostic framing, extracted pattern, queue presence, raw artifact presence, or candidate persistence.

Confidence is not truth. Model output is not canon. No model output as truth. No silent fallback may claim model-assisted extraction succeeded.

## 3. Output Boundary

Allowed future output classes:

- `evidence-backed candidate observation`
- `diagnostic question`
- `uncertainty note`
- `insufficient-evidence note`
- `candidate extraction support`
- `safe refusal / blocked request result`
- `unavailable / fail-closed / quarantined result`

Forbidden future output classes:

- `generated_prose`
- `rewritten_prose`
- `continuation`
- `outline`
- `draft`
- `revision`
- `style imitation`
- `polish/improvement/expansion`
- `model_prompt artifact`
- `model_completion artifact`
- `training_jsonl`
- `dataset_manifest`
- `model_artifact`
- `promotion_record`
- `approved_memory`
- `canon`
- `bible`
- `storyform`
- `scene_mutation`
- `note_mutation`
- `material_mutation`

## 4. Evidence, Provenance, And Source-locator Boundary

Future model-assisted outputs used for candidate/review workflows must preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` where available.

Unsupported, missing, invalid, or ambiguous source locators must produce insufficient-evidence, rejected, quarantined, or fail-closed states. Evidence must be traceable to owner-authored or owner-provided sources.

Model interpretations without evidence must be diagnostic questions or uncertainty notes, not candidate truth.

## 5. Candidate/review Handoff Boundary

Future model-assisted candidate support is candidate-first and owner-review-required.

T002 must not create candidate records. Future candidate persistence/review queue creation is allowed only when explicitly scoped in a later child. Queue presence is not approval. Candidate persistence is not canon. Owner review remains mandatory.

Apply-promotion remains the separate explicit audited owner-confirmed path from `PHASE8-IMPL-017`.

## 6. Memory, Canon, And Training Boundary

No automatic canon. No memory/canon mutation. No approved memory writes. No bible/storyform/scenes/notes/materials mutation. No apply-promotion.

No training artifacts. No training/JSONL/dataset/model artifacts. Raw artifacts and model output are support data only. Model-assisted output cannot create training data.

## 7. Refusal, No-prose, And Diagnostic Fallback Boundary

Prose-generation requests must be refused with the standard no-prose refusal direction.

If the user asks for rewrite, continuation, outline, draft, revision, polish, expansion, imitation, or story prose, the future workflow must refuse or redirect to analysis/diagnostic questions only.

Diagnostic-question fallback is allowed. Insufficient-evidence fallback is required when evidence is not enough.

## 8. State Vocabulary For T003+ Contracts

Future contracts must use explicit states rather than silent success:

- `disabled`
- `unavailable`
- `model_unavailable`
- `model_call_blocked`
- `configuration_invalid`
- `request_invalid`
- `unsafe_path`
- `missing_source_refs`
- `missing_evidence_refs`
- `missing_provenance_refs`
- `missing_source_locator_refs`
- `source_locator_invalid`
- `unsupported_output_type`
- `malformed_output`
- `evidence_insufficient`
- `refused_no_prose`
- `quarantined`
- `rejected`
- `candidate_support_ready`
- `diagnostic_questions_ready`
- `valid`
- `fail_closed`

## 9. Future Implementation Split

- `PHASE8-IMPL-020-T003` - Expected-red model-assisted extraction contract tests. Ready/active next.
- `PHASE8-IMPL-020-T004` - Minimal model-assisted request/output guard implementation. Planned.
- `PHASE8-IMPL-020-T005` - Evidence-backed diagnostic/candidate handoff implementation. Planned.
- `PHASE8-IMPL-020-T006` - Model-assisted extraction safety regression. Planned.
- `PHASE8-IMPL-020-T007` - Parent closeout. Planned.

## Scope Boundary

This decision does not implement model-assisted extraction, does not call models/Ollama, does not run BookNLP/spaCy extraction over project text, does not implement NCP/Subtxt/dramatica-flow runtime, does not mutate approved memory/canon, does not persist candidates, does not create review queue entries, does not apply promotion, does not create training/JSONL/dataset/model artifacts, and does not generate prose, rewrite, continuation, outline, draft, revision, polish, expansion, imitation, or story prose.

