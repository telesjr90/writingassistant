# WORKSPACE-025: Project Memory / Canon Cross-Linking and Health Spec

Status: Documentation-only planning handoff. Runtime implementation is future work.

Product working name: Dramatica-Informed Writing Assistant.

Current priority: Pre-Dramatica Project Workspace Foundation.

Related planning:

- WORKSPACE-001: `docs/roadmap/project_workspace_foundation_spec.md`
- WORKSPACE-008: `docs/roadmap/project_overview_page_spec.md`
- WORKSPACE-011: `docs/roadmap/project_memory_canon_page_structure_spec.md`
- WORKSPACE-012: `docs/roadmap/omi_ideas_candidates_page_spec.md`
- WORKSPACE-013: `docs/roadmap/approved_characters_page_spec.md`
- WORKSPACE-014: `docs/roadmap/approved_locations_settings_page_spec.md`
- WORKSPACE-015: `docs/roadmap/approved_timeline_page_spec.md`
- WORKSPACE-016: `docs/roadmap/approved_plot_threads_page_spec.md`
- WORKSPACE-017: `docs/roadmap/continuity_consistency_page_spec.md`
- WORKSPACE-018: `docs/roadmap/approved_open_questions_page_spec.md`
- WORKSPACE-019: `docs/roadmap/approved_relationships_page_spec.md`
- WORKSPACE-020: `docs/roadmap/approved_organizations_groups_page_spec.md`
- WORKSPACE-021: `docs/roadmap/approved_objects_items_page_spec.md`
- WORKSPACE-022: `docs/roadmap/approved_annotations_evidence_provenance_page_spec.md`
- WORKSPACE-023: `docs/roadmap/approved_contradictions_page_spec.md`
- WORKSPACE-024: `docs/roadmap/approved_scene_event_causality_review_spec.md`
- Project memory/canon storage: `docs/roadmap/project_memory_canon_storage_model.md`
- OMI story knowledge expansion: `docs/roadmap/omi_story_knowledge_candidate_expansion.md`
- Writer Assistant Core candidate schemas: `docs/roadmap/writer_assistant_core_candidate_schemas.md`

## 1. Purpose

This specification defines future project-level cross-linking, navigation, index-health, and reference-health planning for approved memory/canon. It consolidates shared rules across the approved-memory page series so category pages can agree on identity, links, labels, counts, warning states, and candidate/canon boundaries.

This spec is not a runtime memory implementation, not an apply-promotion implementation, not a repair tool, not an extractor, not a semantic search feature, not a generated summary feature, not a graph visualization feature, and not a Dramatica structural proof feature.

The future cross-linking and health layer should:

- Define shared cross-linking rules for approved memory/canon records across approved category pages.
- Define project-level `memory/index.json` planning without implementing it.
- Define a category registry plan for future memory files and page navigation.
- Define approved-memory navigation and category count snapshots.
- Define broken-reference, duplicate-ID, unsafe-ID, unsupported-schema, index-mismatch, and source-reference warning behavior.
- Define candidate/canon label consistency across approved pages, OMI pages, Project Overview, and Project Memory / Canon.
- Define cross-link behavior among approved memory records, source documents, evidence/provenance, OMI candidates, and promotion records.
- Keep health warnings non-destructive and separate from repair/rebuild behavior.
- Keep model/Ollama, extraction, semantic search, graph visualization, repair, apply-promotion, contradiction detection, and Dramatica behavior future-only.

The application may store, edit, and organize owner-authored prose, notes, metadata, and materials. The application may display owner-approved project memory/canon after explicit future promotion. The AI must never write, rewrite, continue, imitate, polish, improve, expand, or extend story prose.

Standard refusal message:

```text
I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose.
```

## 2. Covered Approved-Memory Categories

WORKSPACE-025 covers shared health and cross-link rules for:

- Characters.
- Locations/settings.
- Timeline events.
- Plot threads.
- Continuity/consistency issues.
- Open questions.
- Relationships.
- Organizations/groups.
- Objects/items.
- Annotations/evidence/provenance.
- Contradictions.
- Scene reviews/events/actions/causality notes.

Future extensibility should reserve space for aliases/nicknames, chapter/scene navigation summaries, owner review notes, and Dramatica-specific records as a later separate approved-memory family. Dramatica-specific records are not first-version Writer Assistant Core truth.

Shared category rules:

- Approved category records remain project-local.
- Approved category records must be owner-approved and applied by a future apply-promotion flow or another explicitly designed owner-approved approved-memory process.
- Pending, rejected, archived, needs-revision, uncertain, duplicate, approved-but-not-applied, and promotion-record-only states must not appear as approved records.
- Category pages may show OMI candidate and promotion counts only as separate candidate/audit links.
- Generic relationship, theme, contradiction, timeline, event, causality, or continuity links must not be presented as Dramatica proof.

## 3. Future Memory Files and Category Registry

Future memory/canon storage may use a folder-based target such as:

```text
projects/{project_id}/
  memory/
    index.json
    characters.json
    locations.json
    timeline.json
    plot_threads.json
    continuity.json
    open_questions.json
    relationships.json
    organizations.json
    objects.json
    annotations.json
    evidence_spans.json
    provenance.json
    contradictions.json
    scene_reviews.json
    events.json
    causality.json
```

Planning rules:

- Exact runtime schema is deferred.
- Files may be combined or split by later implementation decision.
- `memory/index.json` should be rebuildable or health-checkable, not the only source of truth.
- Approved category files remain the authoritative approved-memory source unless a later implementation explicitly changes that rule.
- Category records remain approved-only.
- OMI candidates and promotion records remain separate.
- Apply-promotion remains future-only.
- `memory/index.json` must never include pending candidates as approved truth.
- `memory/index.json` must not leak host filesystem paths.

Future category registry fields may include:

- `category`
- `display_label`
- `record_type`
- `file`
- `route`
- `status`
- `implemented`
- `approved_record_count`
- `candidate_count_link`
- `promotion_audit_count`
- `health_warning_count`
- `last_updated`
- `schema_version`

## 4. Shared Record Identity and Link Model

Approved memory records should have a stable shared identity model where practical:

| Field | Purpose |
| --- | --- |
| `record_id` | Stable approved record ID. |
| `record_type` | Specific approved record type. |
| `category` | Registry category such as `characters` or `timeline`. |
| `display_title` | Stored owner-approved display label. |
| `status` | Stored approved record status. |
| `approval_state` | Explicit approved/applied state. |
| `source_file` | Project-relative source memory file, if represented. |
| `source_record_ids` | Stored source record references. |
| `linked_record_ids` | Approved memory/canon record links. |
| `linked_candidate_ids` | OMI candidate provenance links only. |
| `linked_promotion_record_ids` | Promotion audit links only. |
| `linked_source_document_ids` | Source scene/chapter/note/material/document links. |
| `linked_evidence_record_ids` | Evidence record links. |
| `linked_provenance_record_ids` | Provenance/audit links. |
| `supersedes_record_ids` | Older approved records replaced by this record. |
| `superseded_by_record_id` | Newer approved record replacing this one. |
| `created_at`, `updated_at`, `approved_at`, `approved_by` | Audit timestamps and owner/reviewer metadata. |
| `schema_version`, `record_version` | Schema and record revision metadata. |
| `tags`, `notes` | Stored tags and owner/review notes. |

Link metadata may be stored as explicit records, derived index entries, or category fields depending on later implementation:

| Field | Purpose |
| --- | --- |
| `link_id` | Stable link ID if represented. |
| `from_record_id`, `from_record_type` | Link source. |
| `to_record_id`, `to_record_type` | Link target. |
| `link_type` | Relationship type such as source, evidence, related, supersedes, cause, effect, member, participant, or audit. |
| `link_direction` | One-way, two-way, inverse, or derived. |
| `link_status` | Active, broken, unresolved, unsupported, superseded, or pending review. |
| `evidence_record_ids`, `provenance_record_ids` | Link support and traceability. |
| `created_at`, `updated_at`, `approved_at`, `approved_by` | Link audit metadata. |
| `source_candidate_ids`, `promotion_record_ids` | Candidate/promotion audit context only. |
| `notes` | Stored owner/review notes. |

Clarifications:

- Links are approved-memory references, not generated truth.
- Links may be one-way, two-way, derived index entries, or explicit approved link records depending on later implementation.
- Broken links show warnings and do not delete or repair records.
- Candidate links are audit/provenance context only, not approved truth.
- Candidate-derived links must remain pending until owner-approved.
- Future extractor-created and model-created links must enter OMI first.

## 5. `memory/index.json` Planning

Future `memory/index.json` may contain:

- `project_id`
- `schema_version`
- `generated_at` or `updated_at`
- `category_registry`
- `category_counts`
- `record_lookup`
- `cross_reference_lookup`
- `source_document_lookup`
- `candidate_lookup`
- `promotion_record_lookup`
- `health_summary`
- `last_health_check`
- `rebuild_status`

Index rules:

- `memory/index.json` is derived/rebuildable or health-checkable.
- Index mismatch must warn, not auto-repair in the first version.
- Approved category files remain the authoritative approved-memory source unless later implementation decides otherwise.
- Index data must never make candidates, approved-but-not-applied candidates, or promotion records approved truth.
- Index data must not expose absolute host filesystem paths.
- Missing `memory/index.json` is a valid empty/degraded state when category files are absent or readable directly.

## 6. Navigation and Count Snapshots

Project Overview and Project Memory / Canon pages may show:

- Category cards.
- Approved record counts.
- Pending candidate counts as OMI links only.
- Promotion audit counts.
- Health warning counts.
- Broken-reference counts.
- Missing-source counts.
- Last updated timestamps.
- Empty states.
- Not implemented states.
- Category unavailable states.
- Links to category pages.
- Links to OMI candidate pages.
- Links to evidence/provenance pages.

Required count labels:

- `Approved records`
- `Pending candidates`
- `Promotion audit records`
- `Health warnings`
- `Broken links`
- `Missing sources`
- `Not implemented yet`

Count rules:

- Approved counts come only from approved memory/canon records.
- Pending candidate counts must link to OMI and stay visually separate.
- Promotion audit counts must not increase approved record counts.
- Missing or corrupt category counts must degrade into warnings.
- Category unavailable and not implemented states must be explicit.

## 7. Candidate / Canon Separation Across Cross-Links

Approved memory records may link to OMI candidates and promotion records only as audit/provenance context.

Rules:

- OMI candidates do not become approved truth through linking.
- Promotion records do not become approved truth without future apply-promotion.
- Cross-links do not promote candidates.
- Cross-links do not validate truth claims.
- Cross-links do not authorize memory mutation.
- Candidate-derived links remain pending until owner-approved.
- Future extractor-created links must enter OMI first.
- Future model-created links must enter OMI first.
- Generic relationship, theme, contradiction, event, or causality links do not prove Dramatica claims.
- Approved pages must not hydrate missing approved fields from candidates, promotion records, source text, search results, or inferred links.

## 8. Health Checks and Warning Classes

Future health checks should be read-only and non-destructive. Required warning classes include:

- Missing `memory/`.
- Missing `memory/index.json`.
- Corrupt `memory/index.json`.
- Missing category files.
- Corrupt category files.
- Unsupported schema versions.
- Duplicate record IDs within a category.
- Duplicate record IDs across categories if globally scoped IDs are required.
- Unsafe record IDs.
- Unsafe category names.
- Unsafe source IDs.
- Broken cross-record references.
- Broken source document references.
- Broken evidence/provenance references.
- Broken OMI candidate links.
- Broken promotion record links.
- Supersession cycles.
- Relationship cycles if unsupported.
- Hierarchy cycles if unsupported.
- Cause/effect cycles if represented.
- Related-question cycles if represented.
- Source hash mismatch if represented.
- Locator out-of-range if represented.
- Index count mismatch.
- Index lookup mismatch.
- Category registry mismatch.
- Records missing approval metadata.
- Records missing evidence/provenance where required.
- Pending candidates shown as approved truth.
- Promotion records shown as approved truth.
- Host filesystem path leakage.
- Copyright-unsafe excerpts.

Warnings must not:

- Auto-repair.
- Auto-delete.
- Auto-merge.
- Auto-promote.
- Rewrite IDs.
- Rewrite source locators.
- Infer missing links.
- Generate summaries, explanations, or fixes.
- Mutate memory/canon.
- Mutate OMI.
- Write training data.

Blocking warnings should prevent unsafe approved display for affected data. Non-blocking warnings may allow partial display where safe.

## 9. First-Version Operations

Allowed first-version operations:

- View memory health summary.
- View category counts.
- View cross-link warnings.
- View broken-reference warnings.
- View index mismatch warnings.
- Open linked category pages.
- Open linked source documents if available.
- Open linked evidence/provenance records if available.
- Open linked OMI candidates and promotion records as audit context.
- Filter/search health warnings locally.
- View candidate/canon boundary labels.

Future-only operations:

- Repair `memory/index.json`.
- Rebuild index.
- Apply-promotion.
- Edit approved memory.
- Merge/split records.
- Archive/restore records.
- Deduplicate records.
- Auto-link records.
- Extract story knowledge.
- Generate summaries.
- Generate explanations.
- Semantic search.
- Graph visualization.
- Timeline visualization.
- Contradiction detection.
- Source re-anchoring.
- Training/JSONL conversion.
- Dramatica structural/thematic classification.

## 10. Local Search and Filter Planning

First-version local deterministic search/filter may operate over:

- `record_id`
- `record_type`
- `category`
- `display_title`
- `status`
- `approval_state`
- `linked_record_ids`
- `linked_candidate_ids`
- `linked_promotion_record_ids`
- `linked_source_document_ids`
- `linked_evidence_record_ids`
- `linked_provenance_record_ids`
- Health warning type.
- Severity.
- Source file.
- Tags.
- `updated_at`
- `approved_at`

Rules:

- No semantic search.
- No model/Ollama calls.
- No generated summaries.
- No generated explanations.
- No extraction during search.
- No repair during search.
- No re-indexing during search.
- No contradiction detection during search.
- No Dramatica classification during search.
- Results must preserve approved-only labels.

## 11. API Planning

These route groups are future planning only. Do not implement them during WORKSPACE-025.

Route groups:

```text
GET /api/projects/{project_id}/memory
GET /api/projects/{project_id}/memory/index
GET /api/projects/{project_id}/memory/health
GET /api/projects/{project_id}/memory/links
GET /api/projects/{project_id}/memory/categories
GET /api/projects/{project_id}/memory/categories/{category}
GET /api/projects/{project_id}/memory/records/{record_id}
```

Every route/group must define:

- Purpose.
- Request shape.
- Response shape.
- Validation.
- Path safety.
- Candidate/canon boundary.
- No-prose boundary.
- Source/evidence safety.
- Index health behavior.
- Expected errors.

Shared route requirements:

- Validate `project_id` as a safe single path component.
- Validate category names against a registry or allow-list.
- Validate record IDs before lookup.
- Read only inside the selected project.
- Return project-relative references only.
- Do not expose absolute host filesystem paths.
- Return stored metadata only.
- Do not generate, rewrite, continue, imitate, polish, improve, expand, or extend prose.
- Do not call Ollama or any model in the first implementation.
- Do not create OMI records.
- Do not create memory files on read.
- Do not apply promotions.
- Do not repair or rebuild indexes in the first implementation.
- Do not write JSONL/training records or update dataset manifests.

Expected errors include invalid project ID, missing project, invalid category, missing category, missing record, corrupt index, unsupported schema, duplicate IDs, unsafe IDs, broken references, host path leakage risk, and sanitized partial read failure.

## 12. Frontend Planning

Do not implement UI in WORKSPACE-025. Future components:

- `ProjectMemoryCanonHealthPage`
- `MemoryCanonBoundaryBanner`
- `MemoryCategoryCards`
- `MemoryHealthSummaryPanel`
- `MemoryIndexStatusPanel`
- `MemoryCrossLinkWarningsPanel`
- `MemoryBrokenReferencesPanel`
- `MemoryCategoryRegistryPanel`
- `MemoryRecordLookupPanel`
- `MemoryCandidatePromotionAuditLinksPanel`
- `MemoryEvidenceProvenanceLinksPanel`
- `MemorySourceDocumentLinksPanel`
- `MemorySearchFilterControls`
- `MemoryHealthWarningList`
- `MemoryEmptyState`
- `MemoryNotImplementedState`
- `MemoryFutureActionsReference`

Frontend rules:

- No AI writing buttons.
- No generated summary button.
- No generated explanation button.
- No repair button in the first version.
- No apply-promotion button in the first version.
- No rebuild-index button in the first version.
- No semantic-search button in the first version.
- No graph visualization in the first version.
- No controls like fix memory, repair canon, summarize project, explain canon, infer links, generate links, resolve contradiction, rewrite scene, classify Dramatica role, convert to training data, or promote candidate.
- Warnings must be non-destructive.
- Candidate and promotion links must be labeled as audit/candidate context.
- Empty, unavailable, and not implemented states must be explicit.

## 13. Future Tests

Future implementation tests should cover:

- No memory directory.
- No `memory/index.json`.
- Load valid category registry.
- Load approved category counts.
- Empty approved-memory state.
- Pending candidates not counted as approved truth.
- Promotion records not counted as approved truth.
- Broken category file warning.
- Corrupt `memory/index.json` warning.
- Unsupported schema warning.
- Duplicate record IDs warning.
- Unsafe IDs rejected.
- Unsafe category names rejected.
- Broken cross-record reference warning.
- Broken source document warning.
- Broken evidence/provenance link warning.
- Broken OMI candidate link warning.
- Broken promotion record link warning.
- Supersession cycle warning.
- Hierarchy/cause/effect/related-question cycle warning where represented.
- Source hash mismatch warning if represented.
- Locator out-of-range warning if represented.
- Index count mismatch warning.
- Category registry mismatch warning.
- Missing approval metadata warning.
- Missing evidence/provenance warning when required.
- Host path leakage blocked.
- Copyright-unsafe excerpt warning.
- Local search/filter does not call model/Ollama.
- Page does not create OMI records.
- Page does not mutate memory/canon.
- Page does not promote candidates.
- Page does not rebuild index in the first version.
- Page does not write JSONL/training records.
- No AI prose-generation controls.
- No generated summaries/explanations/fixes.
- No invented links/evidence.
- No Dramatica structural/thematic proof claims.
- `training/data/dataset_manifest.json` unchanged.

## 14. Deferred Decisions

Deferred to later implementation tasks:

- Exact runtime schema for shared record/link envelopes.
- Whether all record IDs are globally unique or category-scoped.
- Whether links are explicit approved link records, category fields, derived index entries, or a hybrid.
- Exact category registry file shape and migration behavior.
- Whether `memory/index.json` is required, optional, lazy, or fully rebuildable.
- Exact health warning severity model.
- Exact source document registry and locator format.
- Exact evidence/provenance requirement by category.
- Exact host path redaction policy for API errors.
- Exact copyright-safe excerpt policy.
- Exact apply-promotion, repair, rebuild, edit, merge/split, archive/restore, and deduplication workflows.
- Whether Dramatica-specific approved-memory records become a separate future family.
- Browser/manual acceptance checklist for the implemented health page.

## 15. Implementation Non-Goals

WORKSPACE-025 does not implement:

- Runtime memory/canon storage.
- `memory/index.json`.
- Cross-link validation.
- Backend memory/canon routes.
- Frontend memory/canon UI.
- Apply-promotion.
- Repair/rebuild behavior.
- Extraction.
- Semantic search.
- Graph visualization.
- Contradiction detection.
- Dramatica-specific logic.
- Runtime project files under `projects/`.
- OMI records.
- Memory/canon runtime files.
- JSONL records.
- Training or fine-tuning.
- Ollama/live model verification.
- Package/dependency changes.
- Tests.
- Staging, commits, or pushes.
