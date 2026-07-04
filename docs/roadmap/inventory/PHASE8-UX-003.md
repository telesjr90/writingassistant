# PHASE8-UX-003 Inventory

## Relevant Decision and Status Records

- `docs/roadmap/decisions/PHASE8-UX-002-T007-owner-acceptance-gate-decision.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/validation/latest_roadmap_validation.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/roadmap_index.yaml`
- `docs/roadmap/enrichment/PHASE8-UX-002.enrichment.json`

## Existing Owner Acceptance Evidence

- `artifacts/mvp-readiness/owner-acceptance/evidence-report.md`
- `artifacts/mvp-readiness/owner-acceptance/workflow-log.json`
- `artifacts/mvp-readiness/owner-acceptance/checklist-results.json`
- `scripts/mvp-owner-acceptance-browser-smoke.mjs`

Current owner acceptance harness result: exit `0`, final automated decision `MANUAL_REVIEW_REQUIRED`.

## Existing OMI Browser Evidence

- `docs/roadmap/validation/omi_dashboard_browser_evidence.md`
- `docs/roadmap/validation/omi_candidate_detail_browser_evidence.md`
- `docs/roadmap/validation/omi_evidence_drawer_browser_evidence.md`
- `docs/roadmap/validation/omi_apply_promotion_browser_evidence.md`

These surfaces already provide PASS evidence for candidate/review and guarded apply-promotion boundaries. `PHASE8-UX-003` must map or route the owner harness to this evidence without treating it as owner acceptance.

## Target B Blockers

- `candidate_review_candidate_first_visible`
- `candidate_review_queue_not_approval`
- `candidate_review_read_only_state`
- `candidate_review_owner_action_explicit`
- `candidate_review_confidence_not_truth`
- `candidate_review_persistence_not_canon`
- `apply_promotion_requires_confirmation`
- `apply_promotion_audit_details`
- `apply_promotion_only_approved_workflow`
- `apply_promotion_failed_rejected_unchanged`
- `apply_promotion_no_bypass`

## Target C Blockers

- `manual_workspace_notes_project_scoped`
- `manual_workspace_materials_project_scoped`
- `model_assisted_ncp_structured_context_only`
- `model_assisted_subtxt_rubric_only`
- `model_assisted_dramatica_flow_analysis_only`
- `cyber_fixture_story_check_selected_source_path`
- `cyber_fixture_no_prose_prompt_path`

## Manual Review Only A Blockers

- `startup_owner_understands_analysis_boundaries`
- `project_isolation_playwright_evidence_reviewed`
- `runtime_extraction_unavailable_fail_closed`
- `runtime_extraction_failures_no_success_claim`
- `model_assisted_evidence_backed_only`
- `model_assisted_confidence_not_truth`
- `model_assisted_output_not_canon`
- final explicit owner Accepted/Blocked decision

## T001 Publication Artifacts

- `docs/roadmap/tasks/PHASE8-UX-003.md`
- `docs/roadmap/inventory/PHASE8-UX-003.md`
- `docs/roadmap/enrichment/PHASE8-UX-003.enrichment.json`
- Roadmap/status/governance updates publishing `PHASE8-UX-003`.

## Later Harness Areas to Inspect Only When Explicitly Scoped

- Existing Notes/Materials project-scoped create/save/reload surfaces.
- Existing OMI Dashboard, Candidate Detail, Evidence Drawer, and Apply-Promotion Confirmation surfaces.
- Existing analysis-runtime labels for NCP, Subtxt, and dramatica-flow.
- Existing owner-authored source create/import/select UI.
- Existing selected-source Story Check diagnostic-only path.
- Existing no-prose refusal/fail-closed evidence panel.

## T001 Boundary Inventory

- No frontend/backend/tests/package changes.
- No browser harness script edits.
- No candidates created.
- No Memory/Canon mutation.
- No apply-promotion run or enablement.
- No model/Ollama calls.
- No extraction.
- No generated prose controls.
- No staging, commit, or push.
