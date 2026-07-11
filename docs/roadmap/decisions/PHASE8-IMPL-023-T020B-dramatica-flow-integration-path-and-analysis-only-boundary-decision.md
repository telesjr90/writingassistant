# PHASE8-IMPL-023-T020B — Dramatica-flow Integration-Path and Analysis-Only Boundary Decision

## Result

PASS — the owner-controlled integration-path decision is complete. This is a docs-only decision; it implements no runtime, contract, evaluator, adapter, route, UI, or test.

## Exact Decision Outcome

```text
Complete dramatica-flow runtime:
OWNER-BLOCKED / REFERENCE-ONLY

Narrow dramatica-flow runtime subset:
REJECT/DEFER — no current source subset is authorized for direct execution

App-owned dramatica-flow-informed analysis-rubric path:
ACCEPTED for separate implementation

Automatic story truth, canon settlement, prose generation,
rewriting, revision, outlining, continuation, project-state mutation,
truth-file mutation, model/provider execution, and server/API execution:
FORBIDDEN
```

## Evidence Basis and Preserved T020A Result

T020A established a read-only installed-reference surface: source package `dramatica-flow` 0.1.0, Python `>=3.11`, `df = cli.main:app`, an editable venv whose source matches the expected checkout, detected CLI commands, model/network/server surfaces, project-state mutation surfaces, an MIT claim in README files, no root license file, and an unverified license. Installed-reference evidence is inventory only and is not authorization.

These T020A fields remain authoritative and hard false:

```text
dramatica_flow_analysis_only_runtime_authorized = false
dramatica_flow_live_runtime_available = false
runtime_dependency_available = false
```

T020B does not change T020A implementation or tests.

## Evaluation of the Three Options

### 1. Complete runtime — OWNER-BLOCKED / REFERENCE-ONLY

The complete runtime combines Writer, Architect, Auditor, and Reviser agents; chapter and outline generation; rewriting, revision, and polish behavior; DeepSeek, Ollama, and OpenAI-compatible model/provider surfaces; FastAPI/Uvicorn server surfaces; project and book initialization; world-state and truth-file storage; and chapter, snapshot, thread, and export behavior.

Those surfaces cannot be safely exposed as an analysis-only OMI runtime. Runtime contamination cannot be bounded merely by feature flags or by selecting a command whose name appears diagnostic. The complete runtime remains reference-only and owner-blocked.

### 2. Narrow runtime subset — REJECT/DEFER

No current source subset is authorized for direct execution. Neither `audit` nor `status` meets the OMI boundary, `doctor` and all remaining commands are forbidden, and no separate suitable pure/static analysis module was established. Reconsideration requires a new explicit owner decision after the reopening evidence below is proven.

### 3. App-owned analysis rubric — ACCEPTED for separate implementation

A separate local app-owned rubric may be informed only by allowed high-level concepts. It must use original rules, vocabulary, labels, identities, and contracts. T020B does not define or implement those contracts; T020C is the next task.

## Why `audit` Is Rejected

The CLI `audit` command is not a pure bounded candidate extractor. Static inspection shows that it:

- loads chapter prose from dramatica-flow project storage;
- loads truth-file context;
- constructs dramatica-flow agent data structures;
- invokes `AuditorAgent` through `_llm(...)`;
- emits issue descriptions and suggestions.

It is therefore model-backed, project-state-coupled, and truth-file-coupled. It does not accept only an explicit owner-selected OMI source or return a bounded candidate-only envelope with exact evidence and provenance. It is not authorized.

## Why `status` Is Not an OMI Analysis Runtime

Although `status` appears read-only, it reads dramatica-flow configuration, world state, and truth files; scans dramatica-flow chapter and snapshot directories; and reports existing project progress, open commitments, thread activity, and dormant-thread state.

It does not analyze an owner-provided raw idea or scene into evidence-backed OMI candidates. It has no bounded candidate-result schema and depends on dramatica-flow's truth/project-state model. It is not authorized as a live OMI adapter. Its high-level dormant-thread and narrative-commitment ideas may inform an app-owned rubric.

## Why `doctor` and the Remaining CLI Paths Are Forbidden

`doctor` tests model/API connectivity and is not an analysis command. `write`, `revise`, and `export` are prohibited prose or output paths. `init`, `book`, `setup`, and thread-management commands create or mutate external project state. Other commands do not become safe merely because their names sound diagnostic or read-only. No dramatica-flow CLI command is authorized by T020B.

## No Suitable Pure/Static Runtime Subset Established

The T020B context refresh found no separate pure/static analysis module that simultaneously:

- accepts owner-selected source text;
- avoids model/provider use;
- avoids project, world, and truth state;
- avoids filesystem mutation;
- returns a bounded machine-readable candidate-only envelope;
- preserves exact evidence and provenance; and
- cannot reach prose-generation or revision behavior.

The narrow-runtime option therefore remains rejected/deferred. A future owner-approved audit must prove every property before this option can reopen.

## Accepted High-Level Concepts

Only these high-level concepts may inform a future app-owned implementation:

- causal-chain diagnostics;
- hook, promise, mystery, and conflict lifecycle diagnostics;
- emotional-state and emotional-shift consistency;
- relationship-delta diagnostics;
- timeline and thread-activity diagnostics;
- character-knowledge and information-boundary diagnostics;
- audit questions across causality, character, relationships, timeline, commitments, and information boundaries.

The app-owned implementation must not copy external source code, prompts, templates, algorithms, issue text, suggestions, generated prose, or dramatica-flow project-state semantics. It must use original app-owned rules and labels.

## Future App-Owned Safety Boundary

The future path must be local and app-owned; deterministic or narrowly rule-assisted; in-memory for its core evaluation; owner-input-driven; analysis-only; candidate-only; evidence/provenance-backed; pending owner review; fail-closed; and free of high-confidence truth claims.

It must provide no automatic Storyform classification; no evaluator-owned persistence; no Memory/Canon mutation; no promotion or apply-promotion; no generated prose; no rewriting, continuation, outlining, drafting, polishing, revision, or improvement; no import or execution of dramatica-flow; no `.external_sources` runtime read; and no model/provider or server call.

## Identity and Labeling Separation

The existing T009 identity is preserved unchanged:

```text
adapter identity: dramatica_flow
schema: omi_dramatica_flow_analysis_handoff.v1
support label: dramatica-flow analysis support only
behavior: fixture-only
```

The future app-owned rubric must use identities and labeling distinct from the T009 `dramatica_flow` identity, the external dramatica-flow package, and official dramatica-flow output. T020C will define the exact internal identity, schemas, support label, category vocabulary, and candidate mappings. T020B intentionally defines none of those contracts.

## License Decision

- `MIT` is claimed through the README files.
- No root `LICENSE`, `LICENSE.md`, `LICENSE.txt`, or `COPYING` file was found.
- The project license remains unverified; this is not a legal conclusion.
- No external code, prompt, template, algorithm, or text may be copied.
- A root license file and owner review would be required before code reuse could be reconsidered.

License clarification alone would not authorize runtime execution. The product-boundary conflicts independently suffice to block it.

## Reopening Conditions

The complete or narrow runtime path may be reconsidered only through a new explicit owner decision after evidence proves all of the following:

1. A stable supported analysis-only entrypoint exists.
2. No model/provider/network/server call occurs.
3. No writer, architect, reviser, generation, rewrite, or export surface is reachable.
4. No world-state, truth-file, chapter, snapshot, thread, or external project mutation occurs.
5. Input is an explicit owner-selected source.
6. Output has a bounded machine-readable schema.
7. Every finding includes exact source evidence and provenance.
8. Findings are candidate-only and pending owner review.
9. No truth/canon/final/approved claim is made.
10. The path fails closed.
11. Licensing is sufficiently verified for the proposed use.
12. Isolated automated and manual safety validation passes.

Until then, the runtime remains owner-blocked.

## Preserved Contracts and Safety Confirmations

- T009 remains fixture-only and unchanged.
- T020A preflight and tests remain unchanged, including all three hard-false fields.
- No backend, test, frontend, project, external-source, venv, package, dependency, candidate, review, promotion, Memory, or Canon file changed.
- No dramatica-flow import or execution; no `df` execution; no server, model, provider, API, or network call; and no package installation occurred.
- No adapter, contract, evaluator, route, UI, persistence, project mutation, promotion/apply-promotion, or story prose was implemented or performed.

## Next-Task Frontier

`PHASE8-IMPL-023-T020` remains `in_progress`.

The next child is:

```text
PHASE8-IMPL-023-T020C
App-owned dramatica-flow-informed analysis-rubric contract
planned
```

T020C must define a pure app-owned input/output contract: internal identity, request/result schemas, user-facing support label, bounded diagnostic categories and category-to-candidate mappings, statement-kind rules, evidence/source-locator requirements, provenance, owner-decision and review-status requirements, confidence/uncertainty policies, and recursive fail-closed unsafe-output rejection. It must preserve T009 unchanged and must not implement an evaluator, OMI adapter, route, UI, persistence, Memory/Canon mutation, promotion/apply-promotion, model/server call, or story prose. Do not skip to T021.
