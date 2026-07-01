# PHASE8-IMPL-021-T002 Analysis-only Runtime Integration Boundary and Allowlist Decision

## Result

- Task: `PHASE8-IMPL-021-T002`
- Parent: `PHASE8-IMPL-021` - Analysis-only NCP/Subtxt/dramatica-flow runtime integration
- Result: complete/PASS
- Scope: docs/decision only

T002 defines the analysis-only runtime integration boundary and audited allowlist policy for future `PHASE8-IMPL-021` children. It implements no runtime, code, tests, routes, UI, dependency, model, persistence, canon, promotion, training, or generated-prose changes.

`PHASE8-IMPL-021-T003` is ready/active next. `PHASE8-IMPL-021-T004`, `PHASE8-IMPL-021-T005`, `PHASE8-IMPL-021-T006`, and `PHASE8-IMPL-021-T007` remain planned. `PHASE8-IMPL-022` remains future MVP-required. Fine-tuning remains deferred after MVP. Generated prose/prose-production paths remain permanently forbidden.

## NCP Boundary

NCP is structured context interchange only.

Allowed future NCP use:

- read structured context packets
- normalize approved/candidate-safe context fields
- map external context fields into candidate-first internal handoff shapes
- preserve `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` when available
- surface unsupported/ambiguous fields as diagnostic questions or insufficient-evidence notes

Forbidden NCP use:

- no canon import by default
- no approved memory mutation
- no apply-promotion
- no prose generation
- no storyform truth claims without owner review
- no training data creation
- no silent fallback

## Subtxt Boundary

Subtxt is rubric/diagnostic guidance only.

Allowed future Subtxt use:

- diagnostic rubric references
- throughline/story-point question framing
- insufficient-evidence guidance
- conflict/throughline rubric checks only when source/evidence/provenance backed
- diagnostic question generation without prose suggestions

Forbidden Subtxt use:

- no automatic classifier truth
- no canon truth
- no generated story prose
- no rewrite/continuation/outline/draft/revision/polish/expansion/style imitation
- no owner intent inference as truth
- no training artifact creation
- no apply-promotion

## dramatica-flow Boundary

dramatica-flow is usable only through audited analysis-only allowlists.

Allowed future dramatica-flow use:

- analysis-only graph/flow/rubric concepts that can be mapped to candidate observations or diagnostics
- source/evidence/provenance/source-locator-backed outputs
- deterministic request/output filtering
- explicit unavailable/quarantined/fail-closed states
- allowlisted modules/functions/configurations only after they are documented and test-covered

Forbidden dramatica-flow use:

- generated prose
- rewritten prose
- continuation
- outline generation
- chapter generation
- draft generation
- revision
- polish
- improvement
- expansion
- style imitation
- write/revise features
- export-as-prose
- story-prose paths
- training/dataset/model artifact paths
- canon/approved memory mutation
- apply-promotion
- hidden project writes

## Audited Allowlist Policy

Future allowlist records must be documented before use and must fail closed when absent, incomplete, ambiguous, or denied. T002 defines the shape only; it does not implement the allowlist.

Required future allowlist record fields:

- `tool_name`
- `module_or_feature_name`
- `allowed_action`
- `forbidden_actions`
- `output_classes_allowed`
- `output_classes_forbidden`
- `required_refs`
- `source_locator_policy`
- `evidence_policy`
- `provenance_policy`
- `owner_review_policy`
- `fail_closed_policy`
- `no_silent_fallback_policy`
- `no_prose_policy`
- `no_training_policy`
- `no_canon_policy`
- `no_apply_promotion_policy`
- `validation_tests_required`
- `audit_notes`

## Request Shape Decision

Future requests must include:

- `project_id`
- `source_refs`
- `evidence_refs`
- `provenance_refs`
- `source_locator_refs` when available
- owner-authored or owner-provided source boundary
- `tool_name`
- `requested_action`
- `allowlist_key`
- `analysis_intent`
- no_generated_prose confirmation
- no_rewrite confirmation
- no_continuation confirmation
- no_outline confirmation
- no_training confirmation
- no_canon confirmation
- no_apply_promotion confirmation

## Output Shape Decision

Allowed future output classes:

- `evidence_backed_candidate_observation`
- `diagnostic_question`
- `uncertainty_note`
- `insufficient_evidence_note`
- `rubric_mapping_support`
- `context_interchange_support`
- `quarantined_result`
- `unavailable_result`
- `fail_closed_result`
- `refused_no_prose`
- `blocked_request`

Forbidden future output classes:

- `generated_prose`
- `rewritten_prose`
- `continuation`
- `outline`
- `chapter_generation`
- `draft`
- `revision`
- `polish`
- `improvement`
- `expansion`
- `style_imitation`
- `export_as_prose`
- `story_prose`
- `model_prompt_artifact`
- `model_completion_artifact`
- `training_jsonl`
- `dataset_manifest`
- `model_artifact`
- `promotion_record`
- `approved_memory`
- `canon`
- `bible`
- `storyform_truth`
- `scene_mutation`
- `note_mutation`
- `material_mutation`

## State Vocabulary Decision

Future state vocabulary must include:

- `disabled`
- `unavailable`
- `dependency_missing`
- `configuration_invalid`
- `allowlist_missing`
- `allowlist_denied`
- `unsupported_tool`
- `unsupported_action`
- `request_invalid`
- `unsafe_path`
- `missing_source_refs`
- `missing_evidence_refs`
- `missing_provenance_refs`
- `missing_source_locator_refs`
- `source_locator_invalid`
- `unsupported_output_type`
- `forbidden_output_type`
- `malformed_output`
- `evidence_insufficient`
- `refused_no_prose`
- `blocked_request`
- `quarantined`
- `rejected`
- `diagnostic_questions_ready`
- `candidate_support_ready`
- `valid`
- `fail_closed`

## Handoff and Review Boundary

- runtime outputs are candidate-first
- owner review is required
- `source_refs`, `evidence_refs`, `provenance_refs`, and `source_locator_refs` must be preserved when available
- confidence is not truth
- tool output is not canon
- tool output is not truth
- no model output as truth
- no automatic canon
- no apply-promotion
- no memory/canon mutation
- no training artifacts
- no generated prose
- no rewrite
- no continuation
- no outline
- fail closed
- no silent fallback
- queue presence is not approval
- candidate persistence is not canon
- apply-promotion remains the separate explicit audited owner-confirmed path

## Scope Boundary

T002 is docs/decision only. T002 did not implement NCP runtime, Subtxt runtime, dramatica-flow runtime, backend code, frontend code, tests, package/dependency changes, routes, UI, model/Ollama calls, BookNLP/spaCy extraction, candidate persistence, review queue entries, approved memory/canon mutation, apply-promotion, training/JSONL/dataset/model artifacts, generated prose, rewrite, continuation, outline, draft, revision, polish, expansion, style imitation, export-as-prose, chapter prose, or story prose.
