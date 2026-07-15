# PHASE8-IMPL-026-T004A — Convergence Remediation and Human-Readable Project Memory Architecture

## Decision

```
PHASE8-IMPL-026-T004A is complete/PASS-WITH-FINDINGS.
All 10 invalid directory source locators are repaired with tracked regular-file
replacements that substantiate each record. 4 source_missing findings remain,
all accurately classified as expected cross-branch absences that do not block
rendering. The human-readable rendering architecture is fully defined. T004 is
decomposed into T004A/T004B/T004C bounded children. T004B is planned next.
```

## Result

Complete/PASS-WITH-FINDINGS.

## Starting State

- Repository: `/home/tjrpirateking/projects/WritingAssistantApplication-project-memory`
- Branch: `docs/project-memory-foundation`
- Full HEAD: `23e92c2ed4b72380219238ac6b6cf32b993edea9`
- HEAD subject: `docs(pm): record first commit-bound snapshot and close T003 (T003B)`
- Staging area: empty
- Worktree: clean (before edits)
- Original application worktree not accessed or modified

## T003B Snapshot Verification

- Snapshot path: `.codex-context/project-memory/PHASE8-IMPL-026-T003B/20260713T230207Z/`
- Bound commit: `a04b65cc42ba37fe1357272416828e49479cbce1` (T003A implementation HEAD)
- Convergence result: PASS_WITH_FINDINGS
- Verification: all 11 package files present, SHA256SUMS valid

### Verified Finding Counts from convergence-findings.json

| Severity | Code | Count |
| --- | --- | --- |
| error | `source_locator_invalid` | 9 |
| warning | `source_locator_invalid` | 1 |
| warning | `source_missing` | 4 |
| **Total** | | **14** |

Finding codes verified: `source_locator_invalid`, `source_missing`.
No `critical` findings. No `blocks_publication: true` findings.

## Objective A — Repaired Invalid Directory Source Locators

All 10 invalid directory locators are repaired across 3 registries (assets.json,
features.json, projects.json). Each replacement is a tracked, repository-relative
regular file that directly substantiates the record.

### assets.json

| Record | Old Locator | New Locator(s) | Reason |
| --- | --- | --- | --- |
| `asset:example-project-fixture` | `projects/example/` | `projects/example/project.json` | Primary project metadata file describing the example fixture's purpose, status, provenance, and truth policy |
| `asset:elena-asset-family` | `projects/example/` | `docs/roadmap/project_file_model.md` | Documents Elena/Ember Crown mismatch (lines 93-94, 714) |
| | | `projects/example/bible.json` | Contains Elena/Whispering Woods material |
| | | `projects/example/storyform.json` | Contains Ember Crown/Mara/Calen material |

### features.json

| Record | Old Locator | New Locator(s) | Reason |
| --- | --- | --- | --- |
| `feature:owner-controlled-candidate-review` | `frontend/src/` | `docs/roadmap/decisions/PHASE8-IMPL-023-T023B-grouped-review-react-ui-and-owner-decision-integration.md` | Accepted decision documenting the grouped-review React UI and owner-decision integration (authoritative) |
| | | `frontend/src/omiGroupedReview.js` | Specific grouped-review implementation module (tracked source) |
| `feature:project-memory` | `docs/project-memory/` | `docs/project-memory/README.md` | Primary architecture and contributor documentation |
| `feature:project-memory` | `scripts/project_memory/` | `scripts/project_memory/validate_registries.py` | Core validation implementation |

### projects.json

| Record | Old Locator | New Locator(s) | Reason |
| --- | --- | --- | --- |
| `project:dramatica-informed-writing-assistant` | `backend/` | `backend/main.py` | FastAPI application entry point (root_app) |
| `project:dramatica-informed-writing-assistant` | `frontend/` | `frontend/src/App.jsx` | React application root (root_ui) |
| `project:project-memory-and-plan-integrity` | `docs/project-memory/` | `docs/project-memory/README.md` | Primary architecture documentation |
| `project:project-memory-and-plan-integrity` | `scripts/project_memory/` | `scripts/project_memory/validate_registries.py` | Core validation implementation |
| `project:project-memory-and-plan-integrity` | `tests/project_memory/` | `tests/project_memory/test_validate_registries.py` | Primary test coverage |

## Objective B — Preserved Missing-Source Findings

4 source_missing findings remain, none repaired or silenced.

| Finding ID | Record | Path | Authority | Reason Absent |
| --- | --- | --- | --- | --- |
| `source_missing-5fb89eebd5b8` | `capability:story-check-grounding-integrity` | `tests/test_story_check_grounding.py` | authoritative | Application-branch-only test file; expected absence from partial project-memory branch |
| `source_missing-92abda747061` | `evidence:ph8-impl-024-t002d-story-check-grounding` | `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z` | accepted_evidence | Generated evidence on application branch only |
| `source_missing-a41c2ae75318` | `evidence:q148-fastapi-test-harness-defect` | `.codex-context/PHASE8-IMPL-024/T002D-unrelated-test-harness-defect/20260713T020959Z` | accepted_evidence | Generated evidence on application branch only |
| `source_missing-69228282822b` | `tool:playwright-evidence-collector` | `.codex-context/application-uiux-audit/` | accepted_evidence | Generated evidence (directory locator) on application branch only |

### Missing-Source Classification

| Aspect | Verdict |
| --- | --- |
| Absence expected from current partial branch? | Yes — this branch does not contain application tests, generated evidence, or Playwright collector output |
| Requires future complete-commit synchronization? | Yes — full synchronization (T011) would resolve these |
| Prevents rendering? | No — renderer must display "unavailable in this checkout" |
| Evidence should be classified as invalid? | No — accepted application evidence remains valid; absence is a branch-state fact, not a record defect |
| T004A performs synchronization? | No |
| Q154 remains open? | Yes |

### Renderer Display Rule

The renderer output for missing-source records must display:

```text
Unavailable in this checkout — source file exists on the application branch
(not synchronized to docs/project-memory-foundation)
```

Records are not silenced, deleted, or reclassified.

## Objective C — Human-Readable Rendering Architecture

Architecture documented in `docs/project-memory/rendering/README.md`.

### Key Decisions

1. **Canonical inputs:** tracked registry manifest, 12 tracked registries, schema,
   one explicitly selected snapshot package, convergence findings, source inventory/hashes.
   No independent repository scanning during rendering.

2. **Input acceptance:** invalid registries, malformed snapshot JSON, non-generated-evidence
   snapshots, missing bound commit, nonpublication snapshots, identity mismatches, and
   invalid hashes are all rejected.

3. **Freshness:** every page displays bound commit, branch, timestamp, run ID, snapshot
   path, convergence result, and freshness state. "Current" only when bound commit
   exactly matches repository HEAD. Stale snapshots may render as historical views.

4. **Generated output boundary:** `.codex-context/project-memory/rendered/<TASK_ID>/<RUN_ID>/`.
   Pages are generated evidence, never authoritative, git-ignored, reproducible.

5. **Deterministic page set:** 14 pages in stable order (index, application-overview,
   product-boundaries, features, capabilities, current-roadmap, remaining-work,
   dependencies, decisions, assets, evidence, risks-and-open-questions,
   convergence-findings, technical-annex).

6. **Build manifest:** 20+ fields including renderer identity, bound commit, hashes,
   page list, navigation order, convergence result, exclusions, publication eligibility.

7. **Determinism:** sorted keys, stable record ordering, UTF-8, newline-terminated
   text files, no random IDs, no locale-dependent formatting.

8. **MkDocs boundary:** deferred to T004C. Renderer is independently usable without MkDocs.

## Objective D — Regression Protection

New test file: `tests/project_memory/test_tracked_registry_source_locators.py`

9 tests verify:
- All 12 registry files parse successfully
- No absolute source paths
- No traversal source paths (`..`)
- All non-missing source locators are tracked regular files (not directories, not symlinks)
- All record IDs are globally unique with correct namespace prefixes
- All authority classes are valid trust classes
- Registries are not mutated by the test
- No hidden control characters in source paths
- No backslash paths on Linux

### Known Missing Sources (excluded from regular-file check)

- `tests/test_story_check_grounding.py`
- `.codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z`
- `.codex-context/PHASE8-IMPL-024/T002D-unrelated-test-harness-defect/20260713T020959Z`
- `.codex-context/application-uiux-audit/`

## T004 Decomposition

### T004A — Convergence remediation and human-readable Project Memory architecture

Status: complete/PASS-WITH-FINDINGS.

Repairs directory-valued source locators, preserves missing-source findings,
defines rendering inputs/outputs/freshness/authority/navigation/page contracts/
build manifest/quality rules.

### T004B — Deterministic Markdown renderer implementation and focused tests

Status: planned next.

Implements standard-library deterministic renderer at `scripts/project_memory/render_docs.py`
and focused tests at `tests/project_memory/test_render_docs.py`. Generates Markdown
and build manifest from tracked registries plus one explicit snapshot.
No MkDocs installation or publication closeout.

### T004C — Clean-HEAD documentation generation, offline site quality gate, and T004 closeout

Status: planned.

Runs committed renderer against clean committed HEAD, performs approved offline
documentation-site integration, validates links/navigation/hashes/freshness
banners/reproducibility/generated-file boundaries, and closes T004.

## T004 Status After T004A

- T004: in_progress
- T004A: complete/PASS-WITH-FINDINGS
- T004B: planned next
- T004C: planned
- T005 remains planned and inactive

## Project Memory Roadmap State

- PHASE8-IMPL-026: published/active
- T001: complete/PASS
- T002: complete/PASS
- T003: complete/PASS-WITH-FINDINGS
- T003A: complete/PASS
- T003B: complete/PASS-WITH-FINDINGS
- T004: in_progress
- T004A: complete/PASS-WITH-FINDINGS
- T004B: planned next (not activated in application-roadmap terms)
- T004C: planned
- T005: planned and inactive
- Application frontier: PHASE8-IMPL-024-T003A (unchanged)
- PHASE8-IMPL-025: published/planned and inactive (unchanged)

## Open Questions

- Q151: open for T009's complete Plan Integrity classification model
- Q152: open for Serena adoption criteria
- Q153: open for embedding-model selection
- Q154: open for operational synchronization cadence; T004A does not resolve it

## Risk Updates

| Risk | Status | T004A Impact |
| --- | --- | --- |
| Invalid registry locator | Mitigated | All 10 directory-valued locators repaired with regular-file replacements; regression test added |
| Stale memory | Active | Renderer freshness contract requires exact commit binding |
| Branch synchronization inconsistency | Active | 4 source_missing findings remain; synchronization remains future |
| Generated-evidence promotion | Active, partially mitigated | Renderer output fixed to generated_evidence; page banners required |
| Human-readable pages hiding missing evidence | Newly mitigated | Mandatory "unavailable in this checkout" display rule |
| Renderer creating competing authority | Mitigated | Generated-output classification, page banners, and input acceptance rules |
| Prompt injection | Unchanged | Trust-aware retrieval not implemented |
| Tool provenance | Unchanged | No external tools used |
| Duplicate context systems | Unchanged | No additional systems introduced |
| Model-generated amendments | Unchanged | No models used |

## Authorized File Modifications

### Created
- `docs/project-memory/rendering/README.md`
- `tests/project_memory/test_tracked_registry_source_locators.py`
- `docs/roadmap/decisions/PHASE8-IMPL-026-T004A-convergence-remediation-and-human-readable-memory-architecture.md`

### Modified
- `docs/project-memory/registries/assets.json`
- `docs/project-memory/registries/features.json`
- `docs/project-memory/registries/projects.json`
- `docs/project-memory/README.md`
- `docs/roadmap/tasks/PHASE8-IMPL-026.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json`
- `docs/roadmap/inventory/PHASE8-IMPL-026.md`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/risk_register.md`
- `docs/roadmap/open_questions.md`

### Not Modified
- Project Memory schema, registry manifest, registries not proven affected
- Scanner implementation, snapshot builder, existing Project Memory tests
- `backend/`, `frontend/`, `projects/`, `artifacts/`
- `.github/`, `.claude/`, `.cursor/`, `.agents/`, `.opencode/`
- `.codex-context/`, `ai_context/`, `graphify-out/`
- Dependency manifests, environment files
- `docs/master_plan.md`, root `README.md`, `AGENTS.md`
- PHASE8-IMPL-024/025-specific files
- T003B snapshot (unaltered)

## Confirmation

- No renderer, generated site, publication snapshot, external tool, model,
  dependency, MCP server, plugin, index, or retrieval system was implemented
  or installed.
- Nothing was staged or committed.
- No scanner behavior was changed.
- The application frontier and PHASE8-IMPL-025 status remain unchanged.
- The T003B snapshot hashes are unchanged.
- The original application worktree was not accessed or modified.
