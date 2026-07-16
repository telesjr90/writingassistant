# PHASE8-IMPL-025 — Layered Analysis Architecture and Subtxt Owner Authorization

## Result

Accepted as the controlling documentation-only architecture reconciliation.
This decision publishes a target and planned implementation path; it does not
implement, execute, or validate any runtime.

## Owner authorization and supersession

The owner has resolved and approved all Subtxt licensing and authorization
concerns. Full Subtxt runtime implementation is authorized and required as a
separate, explicitly labeled path.

This decision supersedes the following only where they classify full/live
Subtxt as owner-blocked, licensing-blocked, reference-only by owner decision,
or unavailable because authorization was absent:

- `docs/roadmap/decisions/PHASE8-IMPL-005-ncp-subtxt-structural-interpretation-strategy-decision.md`;
- `docs/roadmap/decisions/PHASE8-IMPL-023-T019B-subtxt-integration-path-decision.md`;
- the historical owner-blocked/licensing statements in T019C through T019F
  and their roadmap summaries.

Their technical inventories and completed implementation evidence remain
historically valid. In particular, the T019 app-owned
`subtxt_informed_rubric` contract, evaluator, adapter, and manual validation
remain complete/PASS. They are not renamed, relabeled, or treated as official
Subtxt execution, and they do not satisfy the newly authorized full-runtime
path by themselves.

Product safety is not superseded. The application remains analysis-only,
candidate-first, evidence/provenance-backed, and owner-controlled. No story
prose generation, rewriting, continuation, polishing, outlining, drafting,
automatic Storyform truth, automatic approval, automatic promotion,
automatic apply-promotion, or direct tool/model mutation of Memory/Canon is
authorized.

## Architecture conclusion

The implemented foundation primarily follows this valid but incomplete flow:

```text
source/raw idea
  -> independent adapters
  -> normalization
  -> fusion/conflict/uncertainty
  -> candidate persistence
  -> owner review
```

The accepted target supports both parallel independent contributors and
sequential layered cooperation.

### Layer 0 — Owner source and source identity

- stable project, document, chapter, and scene IDs;
- exact owner-authored input snapshot;
- content hash;
- offsets and source map;
- source ownership and type.

### Layer 1 — Raw extraction

- spaCy;
- BookNLP;
- explicit NCP import-artifact parsing;
- deterministic app extraction where applicable.

### Layer 2 — Raw artifact and evidence ledger

- immutable tool outputs;
- run manifest;
- tool/model versions;
- source hashes;
- exact offsets and excerpts;
- transformation lineage.

### Layer 3 — Interpretation and diagnostics

- Ollama structured extraction;
- Story Check;
- full authorized Subtxt runtime;
- app-owned Subtxt-informed rubric;
- app-owned dramatica-flow-informed rubric;
- future read-only project-level narrative diagnostics.

### Layer 4 — Grounding and semantic guardrails

- exact-source factual grounding;
- unsupported-output quarantine;
- subject-matter-versus-conflict checks;
- author-intent dependency;
- insufficient-evidence state;
- perspective/Storypoint overclaim prevention;
- no silent rewriting of tool/model output.

### Layer 5 — Fusion

- deterministic normalized IDs;
- fingerprints;
- duplicate relationships;
- corroboration;
- conflicts without truth selection;
- uncertainty labels;
- preserved provenance.

### Layer 6 — Candidate persistence and owner review

- pending candidate-only storage;
- approve, reject, and needs-more-evidence decisions;
- merge, split, correct, and supersede workflows;
- no canon effect from review status alone.

### Layer 7 — Explicit promotion and approved context

- separate promotion record;
- blocker validation;
- final owner confirmation;
- audited apply-promotion;
- approved Memory/Canon mutation only here.

### Layer 8 — NCP gateway

- external NCP import as candidates;
- immutable original import artifact;
- approved-context export;
- canonical schema validation;
- explicit round-trip provenance.

## Tool-role decisions

### spaCy

spaCy is a lightweight local evidence producer for entities, syntax,
dependencies, and rule-based signals. It does not decide structural truth.

### BookNLP

BookNLP is the richer literary evidence producer for characters,
aliases/coreference candidates, quotes, speaker attribution, entities,
events, actions, possessions, supersense categories, and token/dependency
evidence. The validated character/location adapter remains correct but
incomplete. Future work adds precise token-to-character offset translation,
immutable raw artifacts, manifests, source hashes, coreference risk metadata,
expanded mappings, and authoritative fusion/persistence validation.

### Ollama

Ollama has two distinct roles: structured candidate extraction from the exact
owner-selected source, and evidence-bounded interpretation of normalized
evidence. Both require exact source identity/hash, evidence spans, provenance,
unsupported-output handling, and no automatic truth or canon.

### Story Check

The PHASE8-IMPL-024 P0 grounding repair is complete/PASS and remains
authoritative. PHASE8-IMPL-025 consumes it without reopening or duplicating
the completed repair. Story Check becomes an evidence-bounded diagnostic consumer that identifies
the exact source and hash, includes direct evidence for factual warnings,
validates factual claims deterministically, quarantines unsupported output,
and fails closed on source mismatch.

### Full Subtxt runtime

Official/full Subtxt runtime identity remains distinct from the app-owned
`subtxt_informed_rubric`. The full-runtime path requires a current callable
surface inventory, analysis-only allowlist, generation/rewrite/mutation
blocklist, read-only preflight, request/result contracts, official-runtime
provenance, adapter implementation, candidate normalization, evidence-ledger
integration, semantic-guardrail use, deterministic/mocked/real validation,
candidate-only persistence validation, grouped-review validation, and
documentation closeout.

Subtxt may use its required internal model or analysis components. Provenance
must identify runtime version, model/provider when available, input source and
hash, analysis operation, and every transformation into app candidate records.
Subtxt output remains non-canon and owner-review-required.

### App-owned Subtxt-informed rubric

The existing rubric remains a deterministic fallback, supplemental diagnostic
contributor, and semantic guardrail. Its future cross-adapter role classifies
claims as supported, unsupported, ambiguous, subject-matter-only,
author-intent-dependent, or insufficient evidence. It never silently rewrites
the original tool/model output.

### App-owned dramatica-flow-informed rubric

The existing local text-level rubric remains valid. A separate future
read-only project-level diagnostic path may analyze causal chains,
timeline/thread activity, information boundaries, relationship deltas,
emotional-state changes, hooks/foreshadowing, promise/payoff lifecycle, and
continuity warnings. Outline/chapter generation, rewriting, revision,
continuation, world-state settlement, truth-file mutation, and automatic
relationship/emotion/hook mutation remain forbidden.

### NCP

NCP is primarily an explicit import/export gateway, not a default raw-text
analyzer. The current owner-selected candidate-import validator is a valid
narrow foundation. The full gateway preserves an immutable original artifact,
pins schema/mapping versions, validates before import/export, retains original
JSON-pointer and source-value-hash provenance, maps NCP types explicitly,
treats external status as source metadata only, reconciles conflicts without
automatic truth, exports approved context only by default, optionally creates
a separately labeled candidate review bundle, and never treats omitted fields
as deletion without explicit owner action.

## Preserved implemented foundation

- Real local spaCy extraction is complete/PASS.
- Real Ollama/qwen3:8b structured candidate extraction is complete/PASS.
- Story Check runs through the existing analysis engine and Ollama; its P0
  factual-grounding repair is complete/PASS and is preserved as foundation.
- Real BookNLP character/location findings and the narrow compatibility repair
  are complete/PASS.
- Owner-selected NCP JSON validation/import produces candidate-only findings.
- Both app-owned rubrics are implemented and validated, but neither is its
  original/official external runtime.
- Deterministic fusion IDs/fingerprints, duplicate/conflict/uncertainty
  metadata, candidate-only persistence, and grouped review are implemented.
- T023A and T023B remain complete/PASS.

These are foundation-level results. They do not prove that the missing layers
or the new PHASE8-IMPL-025 workstreams are complete.

## Planned parent and sequencing

`PHASE8-IMPL-025 — Layered Analysis Architecture and Tool Integration
Expansion` is published/planned and inactive. T001/T002 are already
complete/PASS. Activation waits for full PHASE8-IMPL-024 parent closeout,
passing closeout validation, and an accepted `FRESH` Project Memory refresh.

After that boundary, PHASE8-IMPL-025 proceeds through the
tool-role/orchestration contract, source identity/run manifest, immutable
evidence ledger, BookNLP expansion, full Subtxt inventory/contracts, full
Subtxt integration, evidence-bounded Ollama/Story Check, cross-adapter semantic
guardrails, project-level diagnostics, full NCP gateway, bounded owner-review
lifecycle expansion, and isolated layered end-to-end validation.

## No implementation in this decision

No application code, tests, runtime project data, evidence artifact, external
source, package/dependency file, model, training artifact, dataset, JSONL,
Memory/Canon record, candidate, promotion, branch, staging state, commit, or
remote was changed by this decision.
