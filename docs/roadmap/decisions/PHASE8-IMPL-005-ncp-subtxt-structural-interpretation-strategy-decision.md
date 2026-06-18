# PHASE8-IMPL-005 NCP/Subtxt Structural Interpretation Strategy Decision

## 1. Decision Summary

`PHASE8-IMPL-005-T005` accepts **Narrative Context Protocol (NCP)** as **`reference-only`** now and an optional future **`approved-context import/export candidate`**.

`PHASE8-IMPL-005-T005` accepts **Subtxt docs** as **`reference-only`** now and an optional future **`semantic rubric candidate`**.

Neither NCP nor Subtxt becomes:

- runtime truth
- automatic canon
- automatic candidate promotion
- extraction runtime
- a bypass around owner review
- a generator or prose-production mechanism

Neither may generate, rewrite, continue, revise, imitate, polish, or improve story prose.

**Classifications:**

| Source | Classification now | Future safe role |
| --- | --- | --- |
| Narrative Context Protocol | `reference-only` | future `approved-context import/export candidate` |
| Subtxt docs | `reference-only` | future `semantic rubric candidate` |

Runtime adapter status for both: **REJECT/DEFER**.

Automatic truth status: **REJECTED**.

Import/export implementation status: **DEFERRED**.

Subtxt/Dramatica automatic classification status: **REJECTED**.

## 2. Why This Decision Exists

`PHASE8-IMPL-005-T003` inventoried NCP and Subtxt official sources in `docs/roadmap/inventory/PHASE8-IMPL-005-tool-source-inventory.md` and classified both as **`reference-only`**.

`PHASE8-IMPL-005-T004` already established that dramatica-flow is **`reference-only`** and that generation, revision, and continuation behavior are rejected.

`PHASE8-IMPL-005-T005` is needed before `PHASE8-IMPL-005-T006` so the app can separate structural schema/rubric references from actual extraction adapter strategy.

The app remains analysis-only, candidate-first, evidence-backed, and owner-reviewed. NCP and Subtxt may inform future structural context and interpretation discipline, but they must not become automatic truth, generation prompts, or runtime dependencies in this parent.

## 3. Evidence Basis

Evidence comes from T003 official source review and local roadmap docs. T005 did not perform new external source retrieval.

### Internal artifacts

- `docs/roadmap/inventory/PHASE8-IMPL-005-tool-source-inventory.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-dramatica-flow-analysis-only-reference-decision.md`
- `docs/roadmap/ncp_compatibility_subset.md`
- `docs/roadmap/omi_mvp_schema_lifecycle.md`
- `docs/roadmap/writer_assistant_core_candidate_schemas.md`

### NCP purpose and schema role

Per T003:

- Official repo README states NCP is a standardized JSON schema for authorial intent / Storyform transport; "there is no standalone app here."
- Repository structure includes `schema/`, `examples/`, and validation tests.
- NCP is transport-focused, not an extraction pipeline.

### NCP storyform/moments/ideation relevance

Per T003 and `docs/roadmap/ncp_compatibility_subset.md`:

- NCP JSON includes premise, four throughlines (objective_story, main_character, influence_character, relationship_story), optional `story.ideation`, `story.moments[]`, and storyform fields (domain, concern, issue, problem, solution, etc.).
- App MVP NCP subset already frames OS/MC/IC/RS separation, players, dynamics, storypoints, perspectives, and storybeats as owner-approved structural context only.

### NCP authorial-intent and interoperability framing

Per T003:

- README describes standardized schema for tools to exchange structural intent.
- `dramatica.com/ncp` describes portable Storyform data.
- MIT License (`LICENSE.md`) retrieved.

### NCP license/dependency/runtime screen from T003

- License: MIT — low adoption risk for schema reference and future import/export design.
- Dependency footprint: JSON/YAML schema and examples; no runtime Python package required for reference use.
- Runtime requirements: none for reference; future import/export would require app-owned parser/validator only.
- Local-first/privacy: schema files are local/static; no remote service required for reference use.
- Prose generation: does not generate prose; transports structural intent.
- Evidence/provenance: schema encodes structural intent, not source text spans; no extraction provenance model.
- Main safety risk: imported Storyform fields treated as automatic truth if owner review is bypassed.

### Subtxt semantic/rubric role

Per T003:

- Official docs describe Subtxt/Dramatica as a tool for authors at the objective narrative structure level.
- Key concepts include Objective Narrative Structure, Storypoints/Storybeats, and author-level interpretation guidance.
- Docs are conceptual rubric, not a downloadable library or API.

### Subtxt source-of-conflict guidance

Per T003:

- Key concepts page includes "Subject Matter is Not Conflict" and "Identifying a Source of Conflict."
- Analytical questions such as "If I remove this, would there still be a problem?" support diagnostic framing rather than automatic labeling.

### Subtxt author-level interpretation guidance

Per T003:

- Docs position Subtxt/Dramatica interpretation at author/story-argument level, not character belief by default.
- Muse transcript example on key concepts page is interpretive Q&A about structure, not prose continuation.

### Subtxt terms/license gaps

- License/terms: **unknown** — no license or terms page retrieved in T003 scope.
- Maintenance/version: **unknown** — live site content retrieved 2026-06-17; no version/changelog retrieved.
- Risk: medium for redistribution/quotation if documentation text is reused directly; low for internal rubric reference.

### Limits and unknowns

- T005 does not verify NCP schema field completeness against app candidate schemas.
- Subtxt site license/terms remain unresolved.
- No NCP import/export or Subtxt rubric runtime exists.
- `docs/roadmap/ncp_compatibility_subset.md` documents existing `storyform.py` validation behavior but does not authorize automatic storyform mutation from imports or model output.

## 4. NCP Strategy Accepted

NCP may inform:

- future approved structural-context export
- future approved structural-context import as candidates
- approved storyform representation where evidence and owner decisions support it
- approved OS/MC/IC/RS context transport
- approved story moments, beats, scenes, chapters, sequences, and references
- approved authorial-intent metadata
- future validation rules for NCP-shaped approved exports
- future compatibility with Dramatica/NCP ecosystem

NCP must not:

- become candidate source of truth
- convert raw candidates into canon
- bypass OMI review
- auto-fill storyform fields
- auto-promote throughline/storypoint labels
- treat imported NCP as verified project truth
- export unapproved candidates as final structure
- write memory/canon files automatically
- trigger model calls
- generate outlines or prose
- replace app-owned candidate schema
- replace project-local memory/canon

## 5. NCP Import/Export Boundary

### Accepted future export pattern

```text
approved memory/canon + approved structural claims + approved storyform/moments
→ app-owned NCP export builder
→ preview/export artifact
→ no raw candidates included as final truth
```

### Accepted future import pattern

```text
imported NCP file
→ validation/normalization
→ candidate records / proposed structural context
→ source locator + provenance
→ owner review
→ approved memory/canon only after explicit promotion
```

### Rejected pattern

```text
imported NCP
→ direct project truth / storyform / memory / canon mutation
```

Also reject:

```text
candidate records
→ automatic NCP export as final truth
```

Imported NCP must be treated as owner-provided source material or proposed structure, not verified truth.

## 6. NCP Candidate Mapping Guidance

Possible future candidate mappings:

- `storyform_context_candidate`
- `throughline_candidate`
- `storypoint_candidate`
- `story_moment_candidate`
- `structural_context_candidate`
- `authorial_intent_note_candidate`
- `ncp_import_candidate`
- `ncp_export_preview_record`

Possible approved destinations after owner review:

- approved project memory/canon
- approved storyform context
- approved project bible context
- approved story moments/scene-event context
- future NCP export preview

**Guardrail:**

No NCP mapping becomes durable truth without owner approval, evidence/provenance, destination, and future apply-promotion behavior.

## 7. Subtxt Strategy Accepted

Subtxt docs may inform:

- semantic interpretation rubric
- Dramatica-informed label discipline
- author-level vs character-level interpretation
- source-of-conflict reasoning
- subject matter vs conflict distinction
- insufficient-evidence rules
- diagnostic question framing
- rubric language for future candidate review
- T006 extraction-strategy scoring where relevant

Subtxt docs must not:

- become runtime dependency
- become automatic classifier
- become proof of storyform truth
- generate story content
- rewrite prose
- produce continuation
- overrule owner decisions
- bypass candidate review
- bypass evidence/provenance
- cause unsupported OS/MC/IC/RS/CIPS/dynamics claims
- become hidden prompts that generate prose or outlines

## 8. Subtxt Semantic Rubric Guidance

Safe future rubric principles:

### 1. Author-level interpretation

- Storyform labels describe author/story argument structure, not character beliefs by default.
- Candidate records should clearly separate character knowledge from author-level structural analysis.

### 2. Subject matter is not conflict

- A topic, object, location, event, or social issue is not automatically a Dramatica conflict.
- Candidate claims should explain why/how it functions as conflict or mark insufficient evidence.

### 3. Evidence before label

- No throughline/storypoint/domain/concern/issue/problem label should be asserted without evidence.
- Weak evidence should produce diagnostic questions or insufficient-evidence candidates.

### 4. Structural function over plot summary

- Candidate analysis should identify structural function only when supported.
- Plot content alone is not enough to prove Dramatica structure.

### 5. Diagnostic questions over invention

- If the app lacks enough evidence, it should ask diagnostic questions.
- It must not invent missing story structure, generate scenes, continue plot, or rewrite material.

### 6. Candidate-only until owner approval

- All Subtxt/Dramatica-informed interpretations remain candidates unless owner-approved.

## 9. Combined NCP/Subtxt Use in App-Owned Pipeline

### Accepted future pattern

```text
owner-authored text / owner-provided structure
→ app-owned analysis/extraction or import flow
→ candidate records with source locator + evidence + provenance
→ Subtxt-informed semantic rubric checks
→ optional NCP-shaped structural context only after approval
→ owner review
→ approved memory/canon only through future explicit apply-promotion
```

### Rejected patterns

```text
Subtxt/Dramatica interpretation
→ automatic storyform truth
```

```text
NCP import
→ automatic storyform/memory/canon truth
```

```text
NCP/Subtxt docs
→ generation prompt
→ outlines/prose/continuation/revision
```

## 10. Relationship to T004 and T006

- `PHASE8-IMPL-005-T004` decided dramatica-flow is `reference-only` and rejected generation/revision/continuation behavior.
- `PHASE8-IMPL-005-T005` decides NCP/Subtxt structural/rubric boundaries.
- `PHASE8-IMPL-005-T006` will decide the first extraction strategy among spaCy, segram, BookNLP, GLiNER, LangExtract, Renard, and reference-only guidance.
- T005 does **not** decide final extraction strategy.
- T005 does **not** implement import/export.
- T005 does **not** implement Subtxt/Dramatica analysis.

## 11. Future Implementation Requirements

Any future NCP/Subtxt-inspired implementation must:

- be reimplemented inside the app-owned codebase
- be tests-first in a future parent
- consume only owner-authored, owner-approved, or owner-provided material
- produce candidates first unless exporting already approved data
- attach source locator/evidence/provenance where relevant
- preserve candidate/canon separation
- pass no-prose/no-rewrite/no-continuation guardrails
- not auto-fill storyform as truth
- not mutate memory/canon
- not export raw candidates as final NCP truth
- not import NCP as canon without owner review
- not call models unless a future model-assisted parent explicitly authorizes it
- not treat Subtxt/Dramatica labels as verified without evidence and owner review

## 12. Accepted Decision

**Decision:** ACCEPT NCP as reference-only now and optional future approved-context import/export schema.

**Decision:** ACCEPT Subtxt docs as reference-only semantic interpretation and Dramatica-informed rubric guidance.

**Runtime adapter status:** REJECT/DEFER for both.

**Automatic truth status:** REJECTED.

**Import/export implementation status:** DEFERRED.

**Subtxt/Dramatica automatic classification status:** REJECTED.

**Safe future use:** candidate-only and approved-context structural/rubric guidance after app-owned implementation design.

## 13. Open Follow-Ups

- **T006:** Decide first extraction path and how reference-only NCP/Subtxt guidance should inform scoring.
- **Future parent:** Define NCP import/export preview architecture if selected.
- **Future parent:** Define Subtxt-informed candidate validation/rubric tests if selected.
- **Future parent:** Define storyform/throughline candidate evidence requirements.
- **Future legal/source review:** Resolve Subtxt docs terms/license if documentation text will be reused directly.
- **Future UI decision:** Decide where NCP export preview or import review would appear.
- **Future schema decision:** Decide whether app-owned candidate schemas need explicit NCP mapping fields.

## Safety Confirmation

- Docs/decision only.
- No NCP import/export implementation.
- No Subtxt analysis implementation.
- No external source retrieval in T005 beyond T003 inventory.
- No tools installed, cloned, or executed.
- No model calls.
- No runtime code, tests, routes, UI, package changes, training data, JSONL, dataset work, memory/canon mutation, staging, or commits.
