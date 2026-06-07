# Optional Analysis Extractors

## Purpose

This document defines a future Writer Assistant Core extractor track for app-level analysis tooling. Extractors may help identify candidate entities, aliases, actions, relationships, event notes, timelines, plot threads, open questions, continuity issues, contradictions, and annotations from owner-provided scene or project context, but they are not part of the current MVP exit gate and no extractor dependency should be installed now.

The intended flow is:

```text
Owner scene/project context
  -> optional extractor
  -> candidate entities/actions/relationships/timeline notes
  -> OMI candidate record
  -> owner review
  -> optional approved promotion through OMI gates
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

## Tool Evaluation Table

| Tool | Possible Role | Strength | Primary Risk | MVP Position |
| --- | --- | --- | --- | --- |
| `segram` | Semantic/action/entity extraction from owner-authored text | Likely safest first candidate for entities, actions, and dependency-style structural notes | NLP output can overclaim relationships or causal meaning | First future extractor spike candidate after schemas, OMI flow, evidence spans, and tests are ready; do not install now |
| `fabula` | Knowledge graph/entity/event/relationship extraction | Useful for graph-shaped candidate records and relationship/timeline notes | Graph output may look like truth without owner review | Second-stage candidate after basic extractor schema exists |
| `silverfish` | Relationship extraction and evidence clusters | Could support relationship-candidate evidence grouping | Relationship extraction may be mistaken for Relationship Story proof | Later candidate after relationship review UI and evidence-span model exist |
| `AI-Reader-V2` | Visualization/UI reference for maps, timelines, relationship graphs | Useful interaction reference for future OMI views | UI patterns could imply extractor certainty or authoring automation | Visualization/UI reference only; do not install as runtime dependency |
| `narrative-blueprint` | Configurable batch/evaluation pipeline reference | Useful for future extractor evaluation harness shape | Pipeline scope could drift into generation or training data production | Future batch/evaluation inspiration after at least one extractor exists |

Dependency rule: do not install external extractor dependencies until a dedicated spike branch/task evaluates license, maintenance, runtime cost, safety, candidate-only behavior, and integration with OMI.

## Rejected or Deferred Tools

Generation-heavy systems such as Inkos/story-engine-style tools are deferred or rejected for this app path. They are incompatible with the current no prose boundary when used as generation systems.

They may only be referenced at a documentation level for architecture comparison. They must not be integrated as runtime dependencies, prompt chains, UI controls, or automated authoring flows.

## OMI Integration Path

Future extractor integration should use OMI as the only storage and review path:

1. Owner selects a scene or project context source.
2. Extractor runs locally or in a reviewed offline pipeline.
3. Extractor output is normalized into a structured JSON object.
4. Output is saved as an OMI candidate record with provenance and evidence.
5. Owner reviews, rejects, revises, or approves the candidate.
6. Any future durable application must use OMI promotion gates and final confirmation.

No extractor path may directly create an OMI promotion record. Promotion records remain owner-confirmed audit records.

## Guardrail Requirements

Future extractor work must enforce:

- No prose generation in extractor prompts, UI labels, or output fields.
- No direct mutation of project truth files.
- Request guard use for any future freeform assistant/model instruction fields.
- Output guard use for any model-authored extractor summaries or labels.
- Evidence-span preservation for owner-authored source snippets.
- Explicit insufficient-evidence reporting instead of guessing IC, RS, CIPS, dynamics, or storyform truth.

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

1. Extractor research and license review.
2. Offline proof of concept against synthetic or public-domain fixtures only.
3. Extractor output schema and normalizer design.
4. OMI candidate creation integration behind explicit owner action.
5. UI display for candidate entities/actions/relationships/timeline notes.
6. Evaluation fixtures and regression tests.
7. Optional local extractor runtime after dependency and performance review.

## Future Tests Needed

- Extractor output is saved only as OMI candidates.
- Extractor output never mutates `bible.json`, `storyform.json`, `scenes/`, `project.json`, `owner_memory.json`, OMI promotions, `training/data`, or `dataset_manifest.json`.
- No prose-generation markers appear in extractor output.
- Owner-authored evidence spans are preserved.
- Extractor claims remain candidate-only with provenance.
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
