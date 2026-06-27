# PHASE8-IMPL-017-T004 Backend Apply-Promotion Implementation

### Result

- Result: PASS.
- Scope: minimal backend apply-promotion service/route implementation plus roadmap/status alignment.
- Parent task: `PHASE8-IMPL-017` - Apply-promotion contract, audit log, and approved memory/canon mutation boundary.
- Completed child recorded: `PHASE8-IMPL-017-T004` - Minimal backend apply-promotion service/route implementation.
- Backend module: `backend/story_knowledge/apply_promotion.py`.
- Backend route: `backend/routes/apply_promotion.py`.
- Route included from: `backend/main.py`.
- Prior child: `PHASE8-IMPL-017-T003` - complete/PASS and committed.
- Next child: `PHASE8-IMPL-017-T005` - Frontend apply-promotion confirmation workflow/surface (ready/active next).
- No context tools were run inside T004. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Created: `backend/story_knowledge/apply_promotion.py`
- Created: `backend/routes/apply_promotion.py`
- Updated: `backend/main.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-017.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`

### Backend Summary

- Implemented the expected public APIs: `validate_promotion_request`, `build_promotion_plan`, `validate_promotion_plan`, `build_promotion_audit_record`, `apply_promotion_plan`, `validate_promotion_audit_record`, `promotion_audit_storage_dir`, `promotion_audit_record_path`, `write_promotion_audit_record`, `read_promotion_audit_record`, and `list_promotion_audit_records`.
- Added `POST /api/projects/{project_id}/apply-promotion`.
- Apply-promotion requires explicit owner confirmation, candidate id/type, approved destination, evidence refs, provenance refs, source locator refs, and owner actor identity.
- Supported destinations remain limited to approved memory/canon categories.
- Plan building validates and previews mutation without writing.
- Apply writes structured approved memory under `writer_assistant/approved_memory/` only after a valid owner-confirmed plan.
- Audit records are project-local under `writer_assistant/promotion_audit/` and append-only.
- Fail-closed behavior rejects unsafe ids/paths, unsupported candidates/destinations, stale snapshots, invalid queue linkage, automatic promotion, confidence-as-truth, queue-presence-as-approval, extraction/model/raw artifact canon claims, generated prose fields, model prompt/output fields, and training artifact fields.

### Boundary Confirmation

- No frontend implementation code changes.
- No package/dependency changes.
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
- `PHASE8-IMPL-017-T005` is ready/active next.
- `PHASE8-IMPL-017-T006` and `PHASE8-IMPL-017-T007` remain planned.
- `PHASE8-IMPL-018` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
