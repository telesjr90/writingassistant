# Latest Roadmap Validation

## PHASE8-IMPL-011-T003 Review Queue Data Shape and Lifecycle Decision

### Result

- Result: PASS.
- Scope: docs/decision only.
- Parent task: `PHASE8-IMPL-011` - Writer Assistant Core candidate review queue and persistence gate planning.
- Completed child recorded: `PHASE8-IMPL-011-T003` - Review queue data shape and lifecycle decision.
- Active/ready child after T003: `PHASE8-IMPL-011-T004` - Candidate persistence gate contract tests.
- Next child after T004: `PHASE8-IMPL-011-T005` - Minimal candidate persistence gate helper, if authorized.

### Files Changed

- Created: `docs/roadmap/decisions/PHASE8-IMPL-011-review-queue-data-shape-lifecycle-decision.md`
- Updated: `docs/roadmap/tasks/PHASE8-IMPL-011.md`
- Updated: `docs/roadmap/enrichment/PHASE8-IMPL-011.enrichment.json`
- Updated: `docs/roadmap/implementation_status.md`
- Updated: `docs/roadmap/roadmap_index.yaml`
- Updated: `docs/roadmap/task_backlog.md`
- Updated: `docs/roadmap/phase_map.md`
- Updated: `docs/master_plan.md`
- Updated: `docs/roadmap/validation/latest_roadmap_validation.md`
- Updated: `docs/roadmap/decision_log.md`
- Updated: `docs/roadmap/risk_register.md`
- Updated: `docs/roadmap/open_questions.md`

### Decision Artifact Summary

T003 accepts the review queue data shape and lifecycle decision. Review queue entries are workflow support only. Queue presence, sorting, grouping, priority, confidence, and source count do not imply owner approval or canon truth.

Queue entries may reference candidate records only after the T002 persistence gate. They must not create records automatically, update candidate records to approved/canon/promoted, mutate memory/canon, implement apply-promotion, trigger routes/UI/tools/models, or carry generated prose/rewrite/continuation fields.

### Review Queue Purpose

The future queue is project-local workflow support for organizing candidate records that require owner review and displaying evidence, provenance, uncertainty, and pending/rejected/needs-info/ready-for-review states. It is not canon, memory, approval, storyform truth, apply-promotion, or generated prose.

### Review Queue Entry Shape

Required future fields include `queue_entry_id`, `project_id`, `candidate_record_id`, `candidate_type`, `target_category`, `review_status`, `lifecycle_state`, `source_document`, `source_locator`, `evidence_summary`, `evidence_refs`, `provenance_summary`, `provenance_refs`, `confidence`, `uncertainty_flags`, `normalization_status`, `raw_output_refs`, `human_review_required`, `created_at`, and `updated_at`.

Forbidden fields include approval/canon/memory/apply-promotion/prose/runtime/route/UI/model trigger fields.

### Lifecycle and Status Labels

Accepted lifecycle states include `draft_ready_for_review`, `needs_more_evidence`, `blocked_invalid_support`, `owner_review_pending`, `owner_reviewed_rejected`, `owner_reviewed_deferred`, `duplicate_candidate`, `superseded_candidate`, and `archived_without_promotion`.

Accepted review statuses include `pending`, `needs_info`, `rejected`, `deferred`, `duplicate`, `superseded`, and `archived`. `approved` is not a PHASE8-IMPL-011 queue status.

### Evidence and Support Boundaries

Every queue entry must support display of source document identity, source locator, evidence excerpt or summary, evidence refs, provenance summary/refs, raw refs where applicable, normalization status, confidence as uncertainty, insufficient-evidence/rejected-output reasons where applicable, and `human_review_required`.

Invalid source/evidence/provenance fails closed. Insufficient evidence may enter only as `needs_more_evidence` or `blocked_invalid_support`; rejected output may be tracked for audit/review only, not as ready.

### Handoff

T004 should be tests-first and encode both T002 persistence gate rules and T003 queue data shape/lifecycle boundaries before implementation. T005 remains optional helper implementation only if T002-T004 authorize. T006 remains safety regression or conditional hardening.

### Validation Results

- Enrichment JSON parse: PASS.
- `python3 scripts/check_enrichment.py`: PASS.
- `python3 scripts/validate_roadmap.py`: PASS.
- Non-LeanCTX whitespace check: PASS.
- Narrow `/usr/bin/git diff --check -- ...`: PASS.
- Source-cache safety checks: PASS. `.external_sources/` is not staged and appears only as ignored.

### Boundary Confirmation

- Docs/decision only.
- No context tools run.
- No web research.
- No external tools installed.
- No external repos cloned/fetched/pulled.
- No external tool code executed/imported/vendored.
- No demos run.
- No model calls.
- No runtime extraction added.
- No real BookNLP/spaCy install or execution.
- No candidate persistence added.
- No review queue implementation added.
- No review UI/API added.
- No tests changed.
- No backend routes changed.
- No frontend files changed.
- No package/dependency files changed.
- No project runtime files changed.
- No raw artifact writes.
- No generated prose/rewrite/continuation behavior added.
- No apply-promotion or memory/canon mutation added.
- No training/JSONL/dataset work.
- No staging, commit, or push.

### Notes

- A direct `rg` command was blocked by a local hook that suggested LeanCTX. T003 did not run LeanCTX because the task explicitly forbids context tools.
- A follow-up focused `git grep` check was used for local evidence inspection.

### Next Step

`PHASE8-IMPL-011-T004` - Candidate persistence gate contract tests.
