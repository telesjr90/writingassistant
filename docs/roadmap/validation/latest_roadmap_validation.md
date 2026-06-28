# PHASE8-IMPL-017-T005 Frontend Apply-Promotion Confirmation Workflow

### Result

- Result: PASS.
- Scope: minimal frontend apply-promotion API helper and confirmation workflow/surface plus roadmap/status alignment.
- Parent task: `PHASE8-IMPL-017` - Apply-promotion contract, audit log, and approved memory/canon mutation boundary.
- Completed child recorded: `PHASE8-IMPL-017-T005` - Frontend apply-promotion confirmation workflow/surface.
- Frontend API helper: `submitApplyPromotion(projectId, payload)` in `frontend/src/api.js`.
- Frontend confirmation surface: `frontend/src/components/ApplyPromotionConfirmation.jsx`.
- Backend route called: `POST /api/projects/{project_id}/apply-promotion`.
- Prior child: `PHASE8-IMPL-017-T004` - complete/PASS and committed.
- Next child: `PHASE8-IMPL-017-T006` - Approved memory/canon mutation safety regression (ready/active next).
- `PHASE8-IMPL-017-T007` remains planned.
- No context tools were run inside T005. Generated context artifacts remain evidence only, not roadmap truth or task completion.

### Files Changed

- Updated: `frontend/src/api.js`
- Updated: `frontend/src/components/ReviewQueuePanel.jsx`
- Created: `frontend/src/components/ApplyPromotionConfirmation.jsx`
- Updated: `frontend/src/styles.css`
- Created: `tests/test_frontend_apply_promotion_workflow_source.py`
- Updated: `tests/test_frontend_owner_action_review_workflow_source.py`
- Updated: `tests/test_frontend_project_workspace_source.py`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/inventory/PHASE8-IMPL-017.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-017.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`

### Frontend Summary

- Added a fail-closed frontend API helper for the T004 backend route.
- Added a separate apply-promotion confirmation section in the review queue detail surface.
- Required explicit final owner confirmation before submit.
- Required owner actor, candidate id/type, allowed destination type, destination key/path, evidence refs, provenance refs, and source locator refs.
- Preserved candidate-only/no-canon warnings: queue presence is not approval, confidence is not truth, candidate persistence is not canon, and raw artifacts are support data.
- Kept review workflow commands separate from apply-promotion controls.
- Displayed backend promotion/audit result details when returned.

### Boundary Confirmation

- No backend implementation code changes.
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
- `PHASE8-IMPL-017-T006` is ready/active next.
- `PHASE8-IMPL-017-T007` remains planned.
- `PHASE8-IMPL-018` through `PHASE8-IMPL-022` remain future MVP-required parents.
- Fine-tuning remains deferred after MVP.
- Generated prose/prose-production paths remain permanently forbidden.
