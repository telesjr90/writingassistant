# PHASE8-IMPL-025-T002 — Source Identity and AnalysisRunManifest

## Result

`PHASE8-IMPL-025-T002` is complete/PASS. It implements the pure, local shared
source/snapshot identity and immutable `AnalysisRunManifest` contracts required
by the accepted T001 layered-plus-parallel architecture. It does not begin
T003, execute an analysis tool or model, persist an artifact or ledger, create
or persist a candidate, mutate project data, promote anything, or alter
Memory/Canon.

`PHASE8-IMPL-025-T003` is now planned, dependency-satisfied/eligible, and not
begun. PHASE8-IMPL-025 remains published/active and no later child is active.
Project Memory remains paused and nonblocking.

## T002A — stable source identity

`backend/story_knowledge/source_map.py` now defines the versioned
`writer-assistant-source-identity.v1` value contract. A frozen
`SourceIdentity` identifies the project, source-document type and stable ID,
document version, explicit ownership class, optional section/chapter/scene
hierarchy, exact snapshot ID, exact content hash, and optional source-map ID.

The source-document type vocabulary remains the existing source-map
vocabulary. Ownership is closed to `owner_authored`,
`owner_selected_imported`, and `app_owned_derived`. Hierarchy levels are
optional. IDs are path-safe; absolute filesystem paths and path traversal are
invalid. Display/path hints are not identity inputs.

`build_exact_source_snapshot` derives the lowercase SHA-256 content digest from
the exact string encoded as UTF-8 and derives a deterministic snapshot ID from
stable logical identity plus that digest. The same logical source and exact
content produce the same identity; exact content or line-ending changes
produce another snapshot identity.

## T002B — snapshots, hashes, and offsets

`ExactSourceSnapshot` preserves the exact owner-input string and validates it
against its identity hash. The accepted bases are explicit:

- content hash: `sha256` over `utf-8-exact`;
- character offsets: `unicode-code-points-zero-based-half-open`;
- byte offsets: `utf-8-bytes-zero-based-half-open`.

Line and token bases remain explicitly unavailable (`available: false`, basis
`null`) unless a caller supplies an actual basis. T002 does not invent a
tokenizer or fabricate line/token offsets.

`translate_exact_offset_range` converts only between the exact character and
UTF-8 byte bases and only while the exact snapshot is present. Optional
expected snapshot ID and content hash checks fail closed. Byte boundaries that
split a UTF-8 code point, out-of-range spans, mismatched snapshots/hashes, and
unknown/approximate bases are rejected. ASCII offsets correspond; multibyte
offsets intentionally diverge.

The existing legacy source-locator validator retains its character-first
compatibility. The canonical locator mode can represent exact byte-only spans
when the byte basis is explicit. Canonical locators may retain both exact
character and byte ranges, and a narrow projection helper emits the existing
candidate locator shape without migrating persisted candidates.

Story Check remains unchanged. Its exact server-selected source, SHA-256 over
exact UTF-8 content, and zero-based half-open UTF-8 byte offsets map directly
to the shared content hash and byte-offset basis. Character offsets are added
only through provable exact-snapshot translation; byte values are never
relabeled as character values.

## T002C — immutable AnalysisRunManifest

`backend/story_knowledge/analysis_run_manifest.py` defines the frozen,
deterministically serialized `analysis-run-manifest.v1` contract. A finalized
manifest carries:

- stable run and project IDs;
- one or more exact frozen source identities, snapshot hashes, and source-map
  references;
- requested operation IDs, exact existing adapter IDs, consumed/produced T001
  dependency classes, immutable semantic configuration, and feature flags;
- an explicit validated acyclic dependency graph;
- separate internal adapter, owner-facing label, implementation-kind, and
  actual tool/runtime/provider/model provenance planes;
- explicit `available`, `unavailable`, or `unknown` provenance without
  fabricated names or versions;
- storage-independent raw/derived artifact identity references for later T003
  use, with no path, layout, persistence, retention, replay, or cleanup API;
- transformation and output lineage;
- contributor lineage and selected-graph coverage; and
- creation/finalization metadata.

All nested configuration and feature-flag values are recursively immutable.
Serialization is stable and defensive. The finalized manifest has no mutable
`planned`/`running` lifecycle, `updated_at`, timeout, cancellation, storage
directory, or persistence-control state. Those live control-plane concerns
remain T003F scope.

The existing T001 adapter identities are unchanged, including distinct
official/external, app-owned, fixture/mock, and deterministic-fallback
identity. `deterministic_fallback` must remain labeled as fallback and cannot
impersonate another contributor.

## T002D — unsuccessful and partial lineage

The manifest preserves exactly the six accepted adapter result states:
`succeeded`, `empty`, `skipped`, `unavailable`, `failed_closed`, and `error`.
`complete`, `partial`, and `degraded` are run-coverage classifications only,
not adapter states.

Every selected contributor retains its adapter, operation, exact source
snapshots, explanation, available provenance, coverage contribution, and
output IDs. Output dispositions are `validated`, `rejected`, `quarantined`,
or `unverified`. Rejected, quarantined, and unverified output requires an
explicit verification, guardrail, or missing-evidence reason and retains its
original storage-independent output reference plus transformation/evidence
lineage. It is not converted into candidate truth.

## Compatibility and boundaries

- Existing source-document, source-map, segment, locator, evidence, extraction
  provenance, and raw-output-reference dictionary validators remain valid.
- Existing candidate records remain unchanged; only a deterministic canonical
  locator projection is added.
- Story Check code and accepted grounding semantics are unchanged.
- OMI adapter identities and six-state result vocabulary are unchanged.
- `raw_extraction_storage.py` and `extraction_orchestrator.py` are unchanged.
- T003 raw-artifact/evidence-ledger persistence, storage layout, retention,
  cleanup, deletion, replay, tamper storage, API/control-plane behavior, and
  persisted-data migration are not implemented.

The manifest is analysis-only, candidate-first, evidence/provenance-backed,
and owner-controlled. Its closed values reject generated-prose, truth/canon,
promotion/apply-promotion, candidate-persistence, project-mutation, and
storage-path configuration fields.

## Validation

Focused source/manifest contract validation: 146 passed. Candidate,
raw-extraction-storage, Story Check contract, and Story Check integration
compatibility: 404 passed with five existing Pydantic deprecation warnings.
OMI orchestrator/persistence/Story Check adapter preservation: 80 passed with
five existing Pydantic deprecation warnings.

The optional broad application suite could not collect in the available local
environment because `httpx` is absent and the environment exposes incomplete
FastAPI/Pydantic imports. No dependency install or package change was
authorized or performed. All required focused and compatibility suites passed.

## Resolved question and next frontier

This decision resolves Q141. The immutable schema is the frozen source,
operation, dependency, provenance, artifact-reference, transformation,
contributor, output-lineage, coverage, and finalization contract described
above. Q140 raw-artifact retention/cleanup and later T003 questions remain
unresolved.

T003 is the next planned, dependency-satisfied/eligible, not-begun frontier.
This decision does not activate or begin it.
