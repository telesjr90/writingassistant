# PHASE8-IMPL-006 Evidence / Source-Map Contract Decision

## 1. Decision Summary

`PHASE8-IMPL-006` will use app-owned source maps and evidence records before any extractor runtime.

Accepted direction:

- Source identity is project-local and stable.
- Evidence must point back to owner-authored or owner-provided source text.
- Source locators are required before candidate normalization.
- Future BookNLP/spaCy outputs must map into app-owned locators and evidence records.
- Raw tool output is never canon.
- Extracted candidates are never canon.
- Owner review remains mandatory.
- No runtime extraction, package install, route, UI, model call, memory/canon mutation, or apply-promotion exists in T002.

## 2. Why This Decision Exists

`PHASE8-IMPL-006-T001` revised the parent to an evidence-first and BookNLP-ready foundation. The next implementation work needs a source/evidence contract before tests or helpers are written.

BookNLP-ready mapping requires stable source IDs, source snapshots/hashes, offset policy, provenance, and raw-output boundaries. Without this contract, future extraction could lose evidence, overclaim story truth, or mutate canon. T002 is the source of truth for `PHASE8-IMPL-006-T003` contract tests.

## 3. Evidence Basis

Local inputs:

- `docs/feasibility.md`
- `docs/booknlp.md`
- `docs/dramaticaflow.md`
- `docs/subtxt.md`
- `docs/ncp.md`
- `docs/roadmap/decisions/PHASE8-IMPL-006-evidence-first-booknlp-ready-scope-decision.md`
- `backend/story_knowledge/candidate_schema.py`
- `backend/story_knowledge/candidate_record.py`
- `backend/story_knowledge/candidate_storage.py`
- `backend/story_knowledge/candidate_persistence.py`
- `backend/story_knowledge/candidate_index.py`

Evidence summary:

- BookNLP is useful only after stable source maps/provenance exist.
- BookNLP output must be candidate-only and evidence-backed.
- dramatica-flow remains reference/wrapped-rubric only and must not write truth.
- Subtxt claims require evidence and insufficient-evidence handling.
- NCP import/export must stay approved-context only.
- Existing candidate schema, validation, storage, persistence, and index helpers establish candidate-only persistence boundaries.

Unknown or deferred details:

- Exact implementation module names remain future work.
- Exact fixture policy for BookNLP-like outputs remains T003/T005 work.
- Runtime raw output writing remains future work.

## 4. Source Document Identity Contract

Required source document reference fields:

- `project_id`
- `source_document_type`
- `source_document_id`
- `source_document_version`
- `source_label`
- `source_path_hint`
- `content_hash`
- `content_hash_algorithm`
- `created_at`
- `updated_at`

Allowed `source_document_type` values for this parent:

- `scene`
- `chapter`
- `note`
- `material`
- `bible`
- `storyform`
- `omi`
- `imported_context`

Decisions:

- `project_id` must be path-safe.
- `source_document_id` must be path-safe.
- `source_path_hint` is display/debug metadata only, not an arbitrary filesystem path to trust.
- Source identity must not point to training files, raw book sources outside project ownership, external paths, or package files.
- Owner-authored and owner-provided source material must be distinguishable from generated or tool output.
- Source document identity is not canon by itself.

## 5. Source Map Contract

A source map is the app-owned derived record that allows evidence to locate text inside a source document.

Source map shape:

- `source_map_id`
- `project_id`
- `source_document`
- `snapshot_id`
- `snapshot_hash`
- `snapshot_hash_algorithm`
- `snapshot_created_at`
- `text_encoding`
- `normalization_policy`
- `line_index_available`
- `char_offset_policy`
- `byte_offset_policy`
- `token_offset_policy`
- `segments`

Segment shape:

- `segment_id`
- `segment_type`
- `segment_index`
- `section_id`
- `chapter_id`
- `scene_id`
- `paragraph_index`
- `sentence_index`
- `line_start`
- `line_end`
- `char_start`
- `char_end`
- `byte_start`
- `byte_end`
- `token_start`
- `token_end`
- `text_excerpt`
- `excerpt_hash`

Allowed `segment_type` values:

- `document`
- `section`
- `chapter`
- `scene`
- `paragraph`
- `sentence`
- `line`
- `token_window`
- `custom`

Decisions:

- Source maps are derived support records, not canon.
- Source maps must be reproducible from a source snapshot where practical.
- Source maps must not rewrite or normalize owner text destructively.
- Source maps may store excerpts for evidence display, but excerpts are owner-authored/source-derived support, not generated prose.
- Source maps must support future BookNLP token/file mappings without requiring BookNLP installation in T002.

## 6. Offset Policy

Accepted offset policy:

- Primary app-owned offset: Python string character offsets over the exact UTF-8 decoded source snapshot.
- Secondary offset: UTF-8 byte offsets where needed for cross-tool raw output mapping.
- Optional offset: token offsets for tool output alignment.
- Optional line locators for human-readable review.
- All offsets are half-open intervals: `start` inclusive, `end` exclusive.
- Offsets must be non-negative integers.
- `end` must be greater than or equal to `start`.
- Offset ranges must not exceed the snapshot length for the relevant unit.
- If exact offsets are unavailable, record `locator_precision = "approximate"` and include a diagnostic note.
- If no reliable locator exists, create an insufficient-evidence candidate or reject normalization rather than inventing offsets.

Required fields for offset-bearing records:

- `char_start`
- `char_end`
- `byte_start`
- `byte_end`
- `token_start`
- `token_end`
- `line_start`
- `line_end`
- `locator_precision`

Allowed `locator_precision` values:

- `exact`
- `normalized`
- `approximate`
- `document_only`
- `unknown`

T002 decisions:

- `char_start` and `char_end` are mandatory for first-slice evidence records unless the record is explicitly an insufficient-evidence/placeholder record that allows no span.
- Byte offsets are not required immediately for first-slice app-owned evidence, but they are required when normalizing raw tool output that supplies byte offsets or requires byte-to-character alignment.
- Unicode policy: offsets are computed after exact UTF-8 decoding of the source snapshot; no NFC/NFD or whitespace normalization may replace the snapshot text for primary offsets.
- CRLF/LF policy: offsets are computed against the exact snapshot bytes/text as stored or captured; any display-only line normalization must be recorded as `normalization_policy` and cannot change the primary span basis.
- Generated text must not be used to fill missing evidence spans.

## 7. Evidence Record Contract

Evidence record fields:

- `evidence_id`
- `project_id`
- `source_locator`
- `source_document`
- `source_map_id`
- `snapshot_id`
- `snapshot_hash`
- `evidence_kind`
- `claim_supported`
- `text_excerpt`
- `excerpt_hash`
- `char_start`
- `char_end`
- `byte_start`
- `byte_end`
- `token_start`
- `token_end`
- `line_start`
- `line_end`
- `locator_precision`
- `confidence`
- `created_at`
- `created_by`
- `provenance`
- `notes`

Allowed `evidence_kind` values:

- `direct_quote`
- `mention`
- `entity_span`
- `event_span`
- `dialogue_quote`
- `relationship_signal`
- `timeline_signal`
- `conflict_signal`
- `continuity_signal`
- `source_metadata`
- `tool_output_reference`
- `owner_note`

Decisions:

- Evidence supports a candidate claim; it is not canon by itself.
- `text_excerpt` must be source-derived or owner-provided, not model-generated prose.
- Evidence may be empty only for placeholder/insufficient-evidence candidates if the candidate type allows it.
- Confidence must be bounded between `0.0` and `1.0`, but confidence does not create truth.
- Evidence records must be safe to persist or embed inside candidate records without writing memory/canon.

## 8. Source Locator Contract

Canonical `source_locator` fields:

- `project_id`
- `source_document_type`
- `source_document_id`
- `source_document_version`
- `source_map_id`
- `snapshot_id`
- `snapshot_hash`
- `segment_id`
- `section_id`
- `chapter_id`
- `scene_id`
- `paragraph_index`
- `sentence_index`
- `line_start`
- `line_end`
- `char_start`
- `char_end`
- `byte_start`
- `byte_end`
- `token_start`
- `token_end`
- `locator_precision`
- `source_label`
- `source_hash`

Decisions:

- `source_locator` remains compatible with existing `CORE_SOURCE_LOCATOR_FIELDS` where practical.
- Existing code currently supports a narrower locator field set; future implementation may extend candidate schema constants and validators.
- T002 does not modify candidate schema constants.
- T002 does not add runtime validation.
- Arbitrary filesystem path fields are rejected.
- External/training/dataset source fields are rejected.
- Source locators remain project-local.

## 9. Evidence Ledger Contract

Future storage targets:

- `projects/{project_id}/writer_assistant/evidence/ledger.json`
- `projects/{project_id}/writer_assistant/evidence/sources/{source_map_id}.json`
- `projects/{project_id}/writer_assistant/evidence/runs/{run_id}.json`

These paths are future targets only; T002 does not create files.

Decisions:

- The Evidence Ledger is derived support data, not canon.
- Candidate JSON remains the candidate source of truth.
- Approved memory/canon remains separate and future-only.
- Raw tool outputs remain separate from the Evidence Ledger.
- The Evidence Ledger must not include generated prose.
- The Evidence Ledger must not mutate source documents.

Ledger record types:

- `source_snapshot_record`
- `source_map_record`
- `evidence_record`
- `extraction_run_record`
- `raw_output_reference`
- `normalization_record`

## 10. Extraction Run Provenance Contract

Extraction run provenance fields:

- `run_id`
- `project_id`
- `tool_name`
- `tool_version`
- `adapter_name`
- `adapter_version`
- `run_type`
- `source_documents`
- `started_at`
- `finished_at`
- `status`
- `input_snapshot_hashes`
- `output_artifact_hashes`
- `created_candidate_ids`
- `rejected_output_count`
- `insufficient_evidence_count`
- `warnings`
- `parameters`
- `environment`
- `human_review_required`

Allowed `run_type` values:

- `manual`
- `deterministic_local`
- `booknlp_raw_import`
- `spacy_baseline`
- `mock_fixture`
- `model_assisted_future`

Allowed `status` values:

- `planned`
- `running`
- `complete`
- `failed`
- `partial`
- `rejected`

Decisions:

- `model_assisted_future` is a future value only, not authorized in this parent.
- Provenance must show what source snapshots were used.
- Provenance must show what tool/adapter produced raw output or candidates.
- Provenance does not make tool output authoritative.
- Human review remains required.

## 11. Raw Tool Output Storage Policy

Future storage targets:

- `projects/{project_id}/writer_assistant/extractions/{tool_name}/{run_id}/raw/`
- `projects/{project_id}/writer_assistant/extractions/{tool_name}/{run_id}/manifest.json`
- `projects/{project_id}/writer_assistant/extractions/{tool_name}/{run_id}/normalized_candidates.json` if a future parent authorizes it

Decisions:

- T002 does not create these paths.
- Raw tool output is never canon.
- Raw output is not candidate JSON until normalized and validated.
- Raw output should be reproducible or traceable to source snapshots.
- Raw output must not be written into memory, canon, bible, storyform, scenes, notes, materials, or owner-authored source files.
- Raw output may be deleted/rebuilt without changing approved truth.
- Raw output must not include generated story prose as authored content.
- Raw outputs from BookNLP-like tools should map through an adapter to evidence records and candidate records.

## 12. BookNLP-Ready Mapping Assumptions

Expected future raw BookNLP-like outputs to support:

- token records
- entity records
- quote records
- book-level JSON records
- supersense or semantic category records if present
- event records if present

Mapping assumptions:

- Token records can help establish token offsets and evidence spans.
- Entity records can map to possible character/location/object/organization candidates.
- Quote records can map to dialogue/quote attribution evidence and possible speaker candidates.
- Event records can map to event/action candidate evidence only if locator/evidence is reliable.
- Book-level JSON can support metadata/character aggregation only as candidate support.
- Coreference/alias clusters remain candidates until owner review.
- Relationship and timeline conclusions remain deferred unless evidence is explicit and contracts support them.

Decisions:

- BookNLP output is not canon.
- BookNLP output must not directly create memory/canon.
- BookNLP output must not create Storyform truth.
- BookNLP output must not be treated as owner-approved.
- BookNLP raw output must map to app-owned source locators and evidence records before candidate creation.
- BookNLP package install/run remains deferred.

## 13. Candidate Normalization Boundary

Accepted pattern:

```text
owner-authored/source text
-> source snapshot
-> source map
-> raw extractor output or manual/rule output
-> app-owned normalization
-> evidence record(s)
-> Writer Assistant Core candidate record
-> candidate persistence/index
-> owner review
```

Rejected patterns:

```text
raw extractor output
-> memory/canon
```

```text
raw extractor output
-> storyform truth
```

```text
raw extractor output
-> generated prose or rewritten source
```

```text
imported NCP or rubric label
-> automatic approved truth
```

Decisions:

- Candidate records must pass existing validation before write.
- Candidate records must keep `status`, `owner_decision`, `destination`, `confidence`, `source_locator`, `evidence`, and `provenance`.
- Existing candidate schema lacks some future source-map/evidence fields; future schema extension work may be required.
- Candidate confidence cannot bypass owner review.
- Insufficient-evidence output should be explicit, not guessed.

## 14. Safety and Guardrails

Hard guardrails:

- no prose generation
- no rewriting
- no continuation
- no style imitation
- no prose improvement
- no generated outline/story content
- no Storyform truth inference
- no automatic canon
- no memory/canon mutation
- no apply-promotion
- no owner-review bypass
- no raw output as truth
- no NCP import as truth
- no Subtxt label as proof
- no dramatica-flow runtime generation
- no model calls unless a later parent explicitly authorizes them
- no package install unless a later parent explicitly authorizes it

## 15. T003 Handoff

T003 should be tests-first only.

Likely test file:

- `tests/test_writer_assistant_core_source_evidence_contract.py`

T003 should add contract tests for future helper modules such as:

- `backend.story_knowledge.source_map`
- `backend.story_knowledge.evidence`

Expected future helper APIs may include:

- `validate_source_document_ref(source_document: dict) -> dict`
- `validate_source_map(source_map: dict) -> dict`
- `validate_source_locator(locator: dict) -> dict`
- `validate_evidence_record(evidence: dict) -> dict`
- `validate_extraction_run_provenance(run: dict) -> dict`

T003 may be expected red until T004 creates helpers.

T003 tests should cover:

- required fields
- allowed source document types
- path-safe IDs
- source hash fields
- snapshot IDs
- offset validation
- locator precision values
- evidence kind values
- provenance run type/status values
- no arbitrary filesystem paths
- no external/training/dataset paths
- no memory/canon mutation fields
- no generated prose fields
- BookNLP-ready raw output references as references only
- candidate-only boundaries
- no source map writes in tests
- no external tool execution

## 16. Deferred Work

Deferred work:

- runtime source-map helpers until T004
- evidence helper implementation until T004
- raw output storage helpers
- BookNLP install/run
- spaCy install/run
- extraction orchestrator implementation
- BookNLP adapter implementation
- candidate creation from raw tool output
- backend extraction routes
- frontend review UI
- NCP import/export
- Subtxt rubric implementation
- dramatica-flow-inspired analysis rubrics
- model-assisted extraction
- apply-promotion
- memory/canon mutation
- training/JSONL/dataset work

## 17. Accepted Decision

Decision: ACCEPT app-owned evidence/source-map contracts as the foundation before extractor runtime.

Decision: ACCEPT source locators and evidence records as required boundaries before candidate normalization.

Decision: ACCEPT BookNLP-ready raw output mapping as a future adapter target, not runtime implementation.

Decision: DEFER BookNLP/spaCy install, runtime extraction, raw output storage implementation, routes, UI, and package changes.

Decision: REJECT raw extractor output, NCP import, Subtxt labels, or dramatica-flow analysis as automatic canon/story truth.
