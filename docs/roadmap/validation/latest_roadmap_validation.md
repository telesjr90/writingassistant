# PHASE8-IMPL-017-T002 Apply-Promotion Boundary Decision and Audit Model

### Result

- Result: PASS.
- Scope: docs/decision/status only.
- Parent task: `PHASE8-IMPL-017` - Apply-promotion contract, audit log, and approved memory/canon mutation boundary.
- Completed child recorded: `PHASE8-IMPL-017-T002` - Apply-promotion boundary decision and audit model.
- Decision document: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`.
- Prior child: `PHASE8-IMPL-017-T001` - complete/PASS and committed.
- Next child: `PHASE8-IMPL-017-T003` - Tests-first expected-red apply-promotion contract (ready/active next).
- No context tools were run inside T002. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-017.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`
- Updated: `docs/master_plan.md`

### Decision Summary

- Apply-promotion is the only approved path from candidate/review workflow state into approved memory/canon for `PHASE8-IMPL-017`.
- Apply-promotion must be explicit owner-confirmed, audited, evidence/provenance-backed, and fail closed.
- Candidate records, review queue entries, owner-action review commands, confidence, extraction output, model output, raw artifact refs, and queue presence are not canon.
- Candidate persistence is not canon; queue presence is not approval; confidence is not truth; raw artifacts are support data.
- The future audit model requires `promotion_record_id`, `candidate_id`, `destination_type`, `destination_path` or `destination_key`, `owner_confirmation`, `evidence_refs`, `provenance_refs`, `source_locator_refs`, `promotion_status`, `no_generated_prose_confirmation`, `no_model_call_confirmation`, and `no_training_artifact_confirmation`.
- The future transaction model is two-stage: validate and build a promotion plan, then apply the owner-confirmed promotion plan and write an audit record.
- Future implementation must fail closed before mutation if validation fails; partial mutation without audit is forbidden.

### Future Parent Sequence

- `PHASE8-IMPL-017-T003` is ready/active next.
- `PHASE8-IMPL-017-T004` remains planned.
- `PHASE8-IMPL-017-T005` remains planned.
- `PHASE8-IMPL-017-T006` remains planned.
- `PHASE8-IMPL-017-T007` remains planned.
- `PHASE8-IMPL-018` remains future MVP-required raw artifact persistence.
- `PHASE8-IMPL-019` remains future MVP-required runtime extraction plus real BookNLP/spaCy install/run/import.
- `PHASE8-IMPL-020` remains future MVP-required model-assisted evidence-backed extraction.
- `PHASE8-IMPL-021` remains future MVP-required NCP/Subtxt/dramatica-flow analysis-only runtime.
- `PHASE8-IMPL-022` remains future MVP-required end-to-end MVP usability validation.

### Boundary Confirmation

- No backend implementation code changes.
- No frontend implementation code changes.
- No product test changes.
- No package/dependency changes.
- No apply-promotion runtime implementation.
- No memory/canon mutation runtime implementation.
- No project truth mutation.
- No raw artifact persistence.
- No runtime extraction.
- No BookNLP/spaCy install/run/import.
- No model/Ollama calls.
- No NCP/Subtxt/dramatica-flow runtime.
- No generated prose.
- No training/JSONL/dataset/model artifacts.
- No staging, commit, or push.
- No source-cache/generated context artifacts staged.

### MVP Scope Preservation

- `PHASE8-IMPL-017` is active and MVP-required.
- `PHASE8-IMPL-018` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.

### Required Boundary Tags Preserved

- `mvp_required_apply_promotion`
- `approved_memory_canon_mutation`
- `owner_confirmed_only`
- `audited_promotion`
- `candidate_to_approved_boundary`
- `no_auto_promotion`
- `no_confidence_as_truth`
- `no_queue_presence_as_approval`
- `no_extraction_as_canon`
- `no_generated_prose`
- `generated_prose_permanently_forbidden`
- `no_model_calls`
- `no_runtime_extraction`
- `no_raw_artifact_persistence`
- `no_training_artifacts`
