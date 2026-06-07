# Optional Analysis Extractors

## Purpose

This document defines a future Writer Assistant Core extractor track for app-level analysis tooling. Extractors may help identify candidate entities, aliases, actions, relationships, event notes, timelines, plot threads, open questions, chapter/scene navigation summaries, continuity issues, contradictions, and annotations from owner-provided scene, chapter, note, or project context. They are not part of the current MVP exit gate, not part of the Project Workspace Foundation implementation, and no extractor dependency should be installed now.

External NLP/story-analysis tools must integrate as replaceable adapters around the app's own extraction pipeline. They are not the pipeline itself and they are never authorities for canon.

The intended flow is:

```text
owner-authored scene/chapter/note text
  -> extraction orchestrator
  -> tool-specific adapters
  -> normalized CORE candidate schemas
  -> evidence/provenance attachment
  -> OMI candidate records
  -> owner review
  -> promotion record
  -> future apply-promotion
  -> memory/*.json canon records
```

Extractor output is candidate analysis only. It is not durable project truth.

## Non-Goals

- Do not generate story prose.
- Do not rewrite, continue, imitate, polish, improve, or extend owner text.
- Do not create scenes, chapters, dialogue, paragraphs, openings, endings, or final story text.
- Do not directly update `bible.json`, `storyform.json`, `scenes/`, `project.json`, `owner_memory.json`, OMI promotions, `training/data`, or `dataset_manifest.json`.
- Do not treat schema-valid extractor output as verified Dramatica/NCP truth.
- Do not add extractor dependencies until a separate implementation task evaluates license, maintenance, runtime cost, and safety.
- Do not add extractor dependencies until schemas, OMI candidate flow, evidence spans, and tests are ready.
- Do not add extractor dependencies until the Project Workspace Foundation can save/reload owner-authored chapters/scenes/notes/materials.
- Do not treat adapter output as canon or as an OMI promotion record.

## Analysis-Only Boundary

Extractors may produce structural observations such as:

- Entity candidates.
- Action or event candidates.
- Relationship candidates.
- Timeline note candidates.
- Plot thread candidates.
- Open-question candidates.
- Continuity or contradiction warning candidates.
- Annotation candidates.
- Navigation summary candidates.
- Evidence clusters.
- Ambiguity or insufficient-evidence notes.

Extractors must not produce prose-generation suggestions or replacement text. Any extractor integration must preserve the no prose boundary and route outputs into OMI as candidate-only records.

## Candidate-Only Data Flow

Candidate output must be stored, if implemented later, as structured OMI candidate material:

- `candidate_type`: a bounded extractor-derived candidate type.
- `candidate_content`: JSON object containing labels, links, evidence, and uncertainty notes.
- `destination`: candidate-only destination selected from the OMI allowlist.
- `provenance`: extractor name, version, source path, source hash, timestamp, and owner/project context.
- `evidence`: exact short owner-authored spans or project-local references where needed.
- `owner_decision`: pending until explicit owner review.

Extractor output may not bypass OMI review, OMI owner decision, OMI promotion gate, or final owner confirmation.

## Future Adapter Shape

Documentation-only future shape; this task does not create these files:

```text
backend/story_knowledge/
  extraction_orchestrator.py
  schemas.py
  evidence.py
  normalizers.py
  adapters/
    spacy_adapter.py
    segram_adapter.py
    booknlp_adapter.py
    gliner_adapter.py
    langextract_adapter.py
    renard_adapter.py
    corenlp_adapter.py
```

The app-owned contracts should define normalized CORE candidate schemas, evidence/provenance attachment, and OMI handoff before any tool dependency is installed.

## Tool Evaluation Table

| Tool | Possible Role | Strength | Primary Risk | MVP Position |
| --- | --- | --- | --- | --- |
| `spaCy` | First likely future local NLP adapter spike | NER, POS tagging, dependency parsing, sentence segmentation, lemmatization, entity linking, and rule/matcher workflows | Baseline NLP can miss fictional entities, aliases, and narrative semantics | First future implementation spike only after workspace and contracts are ready; do not install now |
| `segram` | Later semantic/action extraction adapter spike | Semantic/action/entity extraction after basic parsing exists | Can overclaim relationship, action, or causal meaning | Later spike after spaCy-style adapter, evidence spans, and review UI exist; do not install now |
| `BookNLP` | Later offline chapter/manuscript adapter spike | Designed for books and long English documents; literary characters, aliases, coreference, quote attribution, and events | Long-document output can look authoritative and may be costly to validate | Later offline spike after workspace document model is stable; do not install now |
| `GLiNER` | Later custom-entity extraction adapter spike | Zero-shot NER with arbitrary labels, including fictional locations, magical objects, artifacts, organizations, factions, species, and titles; can run on consumer hardware | Arbitrary labels can hallucinate or over-tag without evidence review | Later custom-entity spike; do not install now |
| `LangExtract` | Evidence-grounding design reference | Exact source-span/source-grounding patterns are useful for candidate evidence | Could be mistaken for required runtime dependency | Design reference only, not default runtime dependency |
| `Renard` | Later relationship graph/reference spike | Relationship/reference graph inspiration | Graph output can imply truth before owner review | Later only after relationship review UI and evidence spans exist |
| `Stanford CoreNLP` / OpenIE / SUTime | Later relation/timeline references | Relation extraction and temporal parsing references | Heavy dependency/runtime cost and overconfident relation/timeline claims | Later relation/timeline spike references only if needed |
| `AI-Reader-V2` | Visualization/UI reference for maps, timelines, relationship graphs | Useful interaction reference for future OMI/project views | UI patterns could imply extractor certainty or authoring automation | Visualization/UI reference only; do not install as runtime dependency |
| `narrative-blueprint` | Configurable batch/evaluation pipeline reference | Useful for future extractor evaluation harness shape | Pipeline scope could drift into generation or training data production | Future batch/evaluation inspiration after at least one adapter exists |
| `NovelClaw` | Memory-bank/workspace inspiration | Useful reference for workspace/memory organization patterns | Generation/memory-bank behavior could blur no-prose and canon boundaries | Inspiration only; do not adopt generation features |

Dependency rule: do not install external extractor dependencies until a dedicated spike branch/task evaluates license, maintenance, runtime cost, privacy/local-first behavior, evidence grounding, safety, candidate-only behavior, and integration with OMI.

## Rejected or Deferred Tools

Dramatron, ai-story-writer, Inkos, and generation-heavy story-engine systems are blocked or documentation-only references for this app path. They are incompatible with the current no prose boundary when used as generation systems.

They may only be referenced at a documentation level for architecture comparison. They must not be integrated as runtime dependencies, prompt chains, UI controls, or automated authoring flows.

Legacy references such as `fabula` and `silverfish` remain historical planning references only unless a future dedicated review reintroduces them as candidate-only adapters.

## OMI Integration Path

Future extractor integration should use OMI as the only storage and review path:

1. Owner saves chapter, scene, note, or project material.
2. Owner or policy triggers extraction manually, automatically after save, or through a future hybrid strategy.
3. Extraction orchestrator calls reviewed adapters.
4. Adapter output is normalized into CORE candidate schemas.
5. Evidence/provenance is attached, preferably with exact source spans where practical.
6. Output is saved as an OMI candidate record.
7. Owner reviews, rejects, revises, merges, splits, marks uncertain, requests more evidence, or approves the candidate.
8. Any future durable application must use OMI promotion gates, final confirmation, and future apply-promotion.

No extractor path may directly create an OMI promotion record. Promotion records remain owner-confirmed audit records.

## Guardrail Requirements

Future extractor work must enforce:

- No prose generation in extractor prompts, UI labels, or output fields.
- No direct mutation of project truth files.
- Request guard use for any future freeform assistant/model instruction fields.
- Output guard use for any model-authored extractor summaries or labels.
- Evidence-span preservation for owner-authored source snippets.
- Explicit insufficient-evidence reporting instead of guessing IC, RS, CIPS, dynamics, or storyform truth.
- Navigation summaries remain navigation aids, not rewritten prose.

Owner-authored source content should not be treated as assistant request intent when saved or analyzed.

## Provenance Requirements

Every extractor-derived OMI candidate should include:

- `source_type`: `extractor_candidate`.
- `source_path`: project-relative scene/context path where applicable.
- `source_label`: human-readable owner source label.
- `created_by`: `tool`.
- `tool`: extractor name.
- `tool_version`: if available.
- `model`: null unless a model is involved.
- `prompt_id`: null unless a model prompt is involved.
- `timestamp`: extraction time.
- `source_hash`: hash of owner source where practical.
- `snapshot_hash`: hash of candidate output where practical.
- `confidence`: candidate confidence, not story truth certainty.
- `notes`: uncertainty, limitations, and owner review notes.

## Future Implementation Phases

1. Project Workspace Foundation save/reload paths for chapters/scenes/notes/materials.
2. Internal CORE candidate schemas, evidence/provenance contracts, and OMI review flow.
3. Adapter architecture and license/privacy/runtime review.
4. spaCy baseline adapter spike against synthetic or public-domain fixtures only.
5. Offline proof of concept for additional adapters only if the baseline proves useful.
6. OMI candidate creation integration behind explicit owner action or approved trigger strategy.
7. UI display for candidate entities/actions/relationships/timeline notes/navigation summaries.
8. Evaluation fixtures and regression tests.
9. Optional local extractor runtime after dependency and performance review.

## Future Tests Needed

- Extractor output is saved only as OMI candidates.
- Extractor output never mutates `bible.json`, `storyform.json`, `scenes/`, `project.json`, `owner_memory.json`, OMI promotions, `training/data`, or `dataset_manifest.json`.
- No prose-generation markers appear in extractor output.
- Owner-authored evidence spans are preserved.
- Extractor claims remain candidate-only with provenance.
- Navigation summaries remain navigation-only and do not rewrite source prose.
- IC, RS, CIPS, dynamics, and storyform claims remain insufficient evidence unless owner-approved evidence exists.
- Unsafe paths and missing provenance are rejected.
- License/provenance metadata is required before enabling a tool.

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Extractor overclaims story truth | Store output as OMI candidate-only records with explicit uncertainty and owner review |
| Extractor output becomes durable truth | Require OMI owner approval, promotion gate, final confirmation, and separate apply behavior |
| Accidental prose generation | Keep extractor tasks structural and use no-prose guardrails for model-authored fields |
| Provenance loss | Require source path, source hash, tool name/version, timestamp, and candidate snapshot hash |
| Dependency bloat | Evaluate licenses, maintenance, install size, and runtime cost before adding dependencies |
| License uncertainty | Keep tools as references until license review is complete |
| Relationship extraction mistaken for RS proof | Label relationship candidates as generic relationship evidence, not Relationship Story proof |
| Tool output treated as canon | Every adapter output becomes an OMI candidate; approved canon requires owner promotion and future apply-promotion |
| Extractor work starts before workspace is usable | Keep extractor spikes sequenced after Project Workspace Foundation and internal contracts |
