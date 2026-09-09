# Dramatica-Informed Writing Assistant Product Contract

## Product purpose

The Dramatica-Informed Writing Assistant is a local-first, analysis-only,
owner-controlled writing workspace. It stores, edits, and organizes
owner-authored prose and project materials; analyzes exact owner-authored or
owner-provided sources; and presents provenance-backed findings as candidates
for explicit owner review.

The product helps the owner understand structure, continuity, relationships,
open questions, and project context without taking over authorship or allowing
a model, tool, confidence score, queue entry, candidate, or promotion record to
become approved truth automatically.

## Permanent safety and truth boundaries

- Owner-authored prose may be stored, edited, saved, and organized.
- The application and its agents must never write, rewrite, continue, imitate,
  polish, improve, expand, outline, draft, revise, or otherwise generate story
  prose.
- Analysis is candidate-first and evidence/provenance-backed. Confidence
  measures support strength; it does not establish truth.
- Tools and models do not select Storyform, structural, world-state,
  relationship, emotion, timeline, or canon truth.
- Raw artifacts are immutable support data, not candidates, Canon, or training
  data.
- Candidate persistence, queue presence, approval status, and promotion records
  are not Canon by themselves.
- Analysis, candidate creation, review status, and promotion records never
  mutate approved Memory/Canon automatically.
- The only authorized durable-truth transition is the separate audited
  apply-promotion workflow after explicit owner approval, destination choice,
  blocker validation, and final confirmation.
- Project Memory governance is preserved but paused and nonblocking for
  ordinary application work.

## Architecture principles

Stable source identity and hashes precede analysis. Immutable run manifests,
native/raw artifacts, evidence-ledger events, transformation lineage,
normalization, guardrails, fusion, candidate persistence, and owner review
preserve traceability.

Parallel contributors may run only when their declared inputs exist. Consumers
must not silently replace normalized evidence with raw text, substitute one
tool identity for another, or represent an app-owned rubric as evidence that a
related external runtime ran.

The product voice and interface should be calm, rigorous, and truthful. They
must keep evidence, provenance, uncertainty, candidate status, owner
checkpoints, and approved project truth visibly distinct. Accessibility and
responsive behavior must preserve those distinctions.

## MVP contract

The MVP is a usable local application that can:

- create and select projects;
- store, edit, save, and reload owner-authored scenes, notes, and materials;
- analyze exact owner sources while preserving stable source identities and
  hashes;
- persist immutable run manifests, native/raw artifacts, and evidence-ledger
  history;
- normalize and fuse findings without selecting truth;
- persist evidence-backed candidates and provide grouped owner review and
  lifecycle actions;
- create promotion audit records;
- apply an explicitly approved promotion through a separate, confirmed,
  audited workflow into approved project-local Memory/Canon;
- expose safe owner workflows; and
- pass current-version end-to-end owner acceptance, including required real
  integrations, negative states, accessibility and responsive evidence,
  filesystem non-mutation proof, and an explicit owner accept/reject/defer
  decision.

Fixtures and mocks remain required regression tools, but they do not satisfy a
required real integration edge. Each MVP-required external integration needs a
contract, a real application adapter, and bounded current-layer real execution.
Historical live runs remain foundation evidence only.

### Required free/local contributors

- spaCy evidence extraction;
- BookNLP literary evidence extraction;
- local Ollama with `qwen3:8b` for exact-source structured extraction and
  evidence-bounded interpretation;
- Story Check through the authorized local Ollama-backed path;
- NCP as a supported local/schema import, export, validation, and round-trip
  gateway when its roadmap scope becomes applicable; and
- app-owned deterministic and rubric contributors within their accepted
  internal scopes.

The app-owned `dramatica_flow_informed_rubric` is the approved application and
MVP boundary for permitted analysis-only concepts, rules, and structural
reasoning derived from the upstream `ydsgangge-ux/dramatica-flow` reference.
The external `dramatica_flow` runtime is not MVP-required. The app-owned rubric
must never be presented as proof that the external runtime ran. See the
[accepted owner decision](docs/roadmap/decisions/2026-09-08-dramatica-flow-analysis-only-reference-and-app-owned-rubric-mvp-boundary.md).

### Optional

- Official paid Subtxt/Dramatica integration is optional. A paid entitlement,
  production runner, and real paid call are not MVP prerequisites.
- An optional NCP candidate-review export bundle is distinct from the required
  approved-context standard export and remains subject to explicit owner
  semantics.

### Deferred or separately authorized

- Fine-tuning, training datasets, RunPod, GGUF/model artifact production, and a
  future `dramatica-analyst:8b` deployment;
- graph, timeline, and query visualization beyond the MVP parents;
- external SaaS research, crawling, and paid-platform experiments;
- official Subtxt paid execution; and
- any external `dramatica_flow` runtime integration, which requires separate
  explicit owner authorization and an analysis-only safety review.

Generated prose is permanently forbidden, not deferred.

## Authority and implementation links

This file is the durable human-readable product and MVP contract. It does not
record mutable task status, branches, commits, pass counts, temporary blockers,
or task chronology.

- Implementation policy and safety: [`AGENTS.md`](AGENTS.md)
- Machine-readable current roadmap state, dependencies, and frontier:
  [`docs/roadmap/roadmap_index.yaml`](docs/roadmap/roadmap_index.yaml)
- Detailed current work: the active task, inventory, and enrichment records
  referenced by the roadmap index
- Scoped owner decisions: accepted records under
  [`docs/roadmap/decisions/`](docs/roadmap/decisions/)

Historical plans, completed task records, generated context, audits, research,
and external references remain evidence for the state they document. They do
not independently define current product truth or implementation scope.
