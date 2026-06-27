# PHASE8-IMPL-017-T003 Expected-Red Apply-Promotion Contract

### Result

- Result: PASS.
- Scope: tests/docs/status only.
- Parent task: `PHASE8-IMPL-017` - Apply-promotion contract, audit log, and approved memory/canon mutation boundary.
- Completed child recorded: `PHASE8-IMPL-017-T003` - Tests-first expected-red apply-promotion contract.
- Expected-red contract: `tests/test_writer_assistant_core_apply_promotion_contract.py`.
- Prior child: `PHASE8-IMPL-017-T002` - complete/PASS and committed.
- Next child: `PHASE8-IMPL-017-T004` - Minimal backend apply-promotion service/route implementation (ready/active next).
- No context tools were run inside T003. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `tests/test_writer_assistant_core_apply_promotion_contract.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-017.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`

### Expected-Red Contract Summary

- The contract imports the future module path `backend.story_knowledge.apply_promotion`.
- The expected future public APIs are `validate_promotion_request`, `build_promotion_plan`, `validate_promotion_plan`, `build_promotion_audit_record`, `apply_promotion_plan`, `validate_promotion_audit_record`, `promotion_audit_storage_dir`, `promotion_audit_record_path`, `write_promotion_audit_record`, `read_promotion_audit_record`, and `list_promotion_audit_records`.
- The target test run is expected-red only because `backend.story_knowledge.apply_promotion` does not exist yet.
- The expected-red failure shape is limited to `ModuleNotFoundError` or `ImportError` for the missing future module/API.
- The contract covers promotion request validation, candidate/review boundaries, destination allowlist and forbidden destinations/actions, promotion plan shape, audit record shape, transaction/mutation behavior, fail-closed quarantine cases, and no-prose/no-model/no-training/no-runtime-extraction boundaries.

### Future Child Sequence

- `PHASE8-IMPL-017-T004` is ready/active next.
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
