# PHASE8-IMPL-018 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-018`
- Title: Raw artifact persistence implementation and project-local extraction artifact lifecycle
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active MVP-required parent; `PHASE8-IMPL-018-T001` complete/PASS; `PHASE8-IMPL-018-T002` ready/active next; `PHASE8-IMPL-018-T003` through `PHASE8-IMPL-018-T007` planned
- Depends on: completed `PHASE8-IMPL-017`
- Current child: `PHASE8-IMPL-018-T002` ready/active next after T001 publication
- Child sequence: T001 complete/PASS; T002 ready/active next; T003 planned; T004 planned; T005 planned; T006 planned; T007 planned
- Prior parent: `PHASE8-IMPL-017` complete/PASS through `PHASE8-IMPL-017-T007`
- Future MVP-required parents: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 2. Why This Parent Exists

`PHASE8-IMPL-017` delivered explicit owner-confirmed apply-promotion, audited promotion records, and approved memory/canon mutation through valid apply-promotion only. The next MVP-required gap is raw artifact persistence: the product needs a bounded, project-local, manifest-backed, path-safe, fail-closed way to persist already-produced raw extraction support bundles without turning those bundles into truth, candidates, approved memory, training data, or runtime extraction execution.

This parent exists so future child tasks can safely define and then implement the raw artifact persistence contract in a narrow sequence:

- publish the parent record and alignment state in T001
- decide the raw artifact persistence boundary and manifest model in T002
- pin the raw artifact persistence contract as expected-red in T003
- add the minimal backend raw artifact persistence helpers in T004
- add bundle/index lifecycle and evidence/provenance linkage in T005
- prove raw artifacts remain support data only and no_runtime_extraction in T006
- close the parent in T007

## 3. Boundary Summary

Allowed in this parent sequence:

- project-local raw artifact storage boundary definition
- raw artifact bundle/schema/manifest decision
- tests-first expected-red raw artifact persistence contract
- minimal backend raw artifact persistence helpers in later child scope only
- raw artifact bundle/index lifecycle and provenance linkage
- safety regression proving raw artifacts remain support data only
- parent closeout

Required boundary statements for this parent:

- `PHASE8-IMPL-018` is MVP-required.
- It follows `PHASE8-IMPL-017`.
- It owns raw artifact persistence lifecycle only.
- Raw artifacts are project-local support data only.
- Raw artifacts are not canon.
- Raw artifacts are not approved memory.
- Raw artifacts are not candidates by themselves.
- Raw artifacts are not training data.
- Raw artifact persistence must be manifest-backed and path-safe.
- Raw artifact persistence must preserve source/evidence/provenance linkage.
- Raw artifact persistence must not automatically create candidates.
- Raw artifact persistence must not automatically promote to canon.
- Raw artifact persistence must not call models.
- Raw artifact persistence must not trigger extraction.
- Raw artifact persistence must not install/run/import BookNLP or spaCy.
- Raw artifact persistence must not call NCP/Subtxt/dramatica-flow runtimes.
- Raw artifact persistence must not generate prose.
- Apply-promotion and approved memory/canon mutation were delivered in `PHASE8-IMPL-017` and must remain separate from raw artifact persistence.
- Real BookNLP/spaCy install/run/import plus runtime extraction remains `PHASE8-IMPL-019`.
- Model-assisted evidence-backed extraction remains `PHASE8-IMPL-020`.
- NCP/Subtxt/dramatica-flow runtime remains `PHASE8-IMPL-021`.
- E2E MVP usability validation remains `PHASE8-IMPL-022`.
- Fine-tuning remains deferred after MVP.
- Generated prose remains permanently forbidden.

Forbidden in `PHASE8-IMPL-018-T001`:

- backend implementation code changes
- frontend implementation code changes
- product test changes
- package/dependency changes
- raw artifact persistence runtime implementation
- raw artifact write/read/list helper implementation
- runtime extraction
- BookNLP/spaCy install/run/import
- model-assisted extraction
- model/Ollama calls
- NCP/Subtxt/dramatica-flow runtime
- apply-promotion changes
- approved memory/canon mutation
- generated prose or prose-production behavior
- training/JSONL/dataset/model artifacts
- raw artifact file creation

`PHASE8-IMPL-018-T001` changed docs/status only and published the parent record, inventory, enrichment JSON, and roadmap/status alignment. It did not implement raw artifact persistence or any runtime behavior.

Required boundary tags for this parent:

- `mvp_required_raw_artifact_persistence`
- `raw_artifacts_support_data_only`
- `raw_artifacts_not_canon`
- `raw_artifacts_not_candidates`
- `raw_artifacts_not_training_data`
- `project_local_raw_artifacts`
- `manifest_backed_raw_artifacts`
- `evidence_provenance_linked`
- `path_safe_fail_closed`
- `no_runtime_extraction`
- `no_booknlp_spacy_runtime`
- `no_model_calls`
- `no_apply_promotion`
- `no_memory_canon_mutation`
- `no_generated_prose`
- `generated_prose_permanently_forbidden`
- `no_training_artifacts`

## 4. MVP Relation

`PHASE8-IMPL-018` is MVP-required and active. It is the next parent after `PHASE8-IMPL-017` complete/PASS and must be completed before the later MVP-required parents for runtime extraction, model-assisted extraction, analysis-only runtime integration, and end-to-end MVP validation. `PHASE8-IMPL-019` through `PHASE8-IMPL-022` remain future MVP-required parents. Fine-tuning remains deferred after MVP.

## 5. Cross-References

- Prior parent task: `docs/roadmap/tasks/PHASE8-IMPL-017.md`
- Prior parent inventory: `docs/roadmap/inventory/PHASE8-IMPL-017.md`
- Prior parent enrichment: `docs/roadmap/enrichment/PHASE8-IMPL-017.enrichment.json`
- Prior decision record: `docs/roadmap/decisions/PHASE8-IMPL-017-apply-promotion-boundary-audit-model-decision.md`
- Current roadmap truth: `docs/roadmap/implementation_status.md`
- Current roadmap index: `docs/roadmap/roadmap_index.yaml`
- Current validation record: `docs/roadmap/validation/latest_roadmap_validation.md`
- Future parent sequence: `PHASE8-IMPL-019`, `PHASE8-IMPL-020`, `PHASE8-IMPL-021`, `PHASE8-IMPL-022`

## 6. Future Parent Deferrals

- `PHASE8-IMPL-019` owns real BookNLP/spaCy install/run/import plus runtime extraction.
- `PHASE8-IMPL-020` owns model-assisted evidence-backed extraction.
- `PHASE8-IMPL-021` owns NCP/Subtxt/dramatica-flow analysis-only runtime integration.
- `PHASE8-IMPL-022` owns end-to-end MVP usability validation.

Generated context artifacts remain evidence only and must not be treated as roadmap truth or task completion:

- `.codex-context/PHASE8-IMPL-017/` (ignored/evidence only if present)
- `ai_context/repomix-current-task-context.xml` (ignored; evidence only)
