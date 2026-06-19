# PHASE8-IMPL-006

## ID

`PHASE8-IMPL-006`

## Title

Writer Assistant Core evidence-first extraction foundation and BookNLP-ready adapter strategy

## Goal

Publish and execute an evidence-first extraction foundation parent that prepares Writer Assistant Core for automated extraction without implementing extraction in T001. The parent prioritizes stable source maps, source locator contracts, an Evidence Ledger/provenance layer, raw tool output policy, candidate normalization, candidate-only persistence boundaries, no-prose/no-model/no-canon guardrails, and a BookNLP-ready adapter contract.

## Why Now

`PHASE8-IMPL-005` completed tool evaluation and extraction strategy through `PHASE8-IMPL-005-T007`. It recommended a spaCy-first local deterministic/rule-assisted extraction foundation.

After closeout, the owner saved follow-up analysis in five local answer files. Those files show the safer next parent is not a generic spaCy-only implementation parent. The next parent should be evidence-first and BookNLP-ready, with spaCy remaining a lightweight baseline/support option and BookNLP becoming the first serious literary extractor candidate once source maps and provenance are stable.

## Dependencies

- Completed parent: `PHASE8-IMPL-005` - Writer Assistant Core tool evaluation and extraction strategy decision.
- Completed child: `PHASE8-IMPL-005-T007` - Roadmap/status closeout.
- Existing candidate infrastructure:
  - `backend/story_knowledge/candidate_schema.py`
  - `backend/story_knowledge/candidate_record.py`
  - `backend/story_knowledge/candidate_storage.py`
  - `backend/story_knowledge/candidate_persistence.py`
  - `backend/story_knowledge/candidate_index.py`

## Evidence Inputs

- `docs/feasibility.md`
- `docs/booknlp.md`
- `docs/dramaticaflow.md`
- `docs/subtxt.md`
- `docs/ncp.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-evaluation-scope-fixture-rubric-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-dramatica-flow-analysis-only-reference-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-ncp-subtxt-structural-interpretation-strategy-decision.md`
- `docs/roadmap/decisions/PHASE8-IMPL-005-nlp-extraction-adapter-strategy-decision.md`

## Scope

Include:

- stable source map contracts
- source document locator contracts
- Evidence Ledger design
- extraction run provenance model
- raw tool output storage policy
- candidate normalization contract
- candidate-only persistence boundaries
- no-prose/no-model/no-canon-mutation guardrails
- BookNLP-ready adapter contract
- optional spaCy baseline decision point
- future dramatica-flow-inspired analysis rubric mapping
- future Subtxt semantic guardrail mapping
- future NCP approved-context import/export mapping

## Exclusions

- extraction implementation in T001
- BookNLP install or execution
- spaCy install or execution
- package/dependency changes
- external repository clone
- external tool execution
- context tool execution
- web/source retrieval
- model/Ollama calls
- runtime code
- tests in T001
- backend routes
- frontend UI
- runtime project files
- training data, JSONL records, datasets, or manifests
- generated prose, rewrite, continuation, imitation, polish, improvement, or expansion
- automatic Storyform truth
- apply-promotion
- memory/canon mutation

## Child-Task Plan

1. `PHASE8-IMPL-006-T001` - Publish evidence-first extraction foundation parent and scope decision. Status: complete after this docs/status/planning publication.
2. `PHASE8-IMPL-006-T002` - Evidence/source-map contract decision. Status: ready.
3. `PHASE8-IMPL-006-T003` - Evidence/source-map contract tests. Status: planned.
4. `PHASE8-IMPL-006-T004` - Minimal source-map/evidence helper implementation. Status: planned.
5. `PHASE8-IMPL-006-T005` - BookNLP-ready raw output and adapter contract decision. Status: planned.
6. `PHASE8-IMPL-006-T006` - BookNLP-ready adapter contract tests. Status: planned.
7. `PHASE8-IMPL-006-T007` - Roadmap/status closeout. Status: planned.

## Acceptance Criteria

- `PHASE8-IMPL-006` is active/published in roadmap docs.
- Parent scope is evidence-first + BookNLP-ready, not spaCy-only.
- The five local answer files are referenced as evidence inputs.
- `PHASE8-IMPL-005` remains complete through `PHASE8-IMPL-005-T007`.
- `PHASE8-IMPL-006-T001` is marked complete if successful.
- `PHASE8-IMPL-006-T002` is marked ready/active.
- No runtime extraction is claimed.
- No external tools are installed, cloned, or executed.
- No code/tests are changed.
- No generated prose/rewrite/continuation behavior is added.
- No memory/canon mutation is added.

## Validation Expectations

For `PHASE8-IMPL-006-T001`:

- `python3 scripts/check_enrichment.py`
- `python3 scripts/validate_roadmap.py`
- non-LeanCTX whitespace check on changed docs
- narrow `git diff --check` if local hooks allow it without LeanCTX

Do not run pytest because no tests or runtime code should change. Do not run app servers, frontend build, browser validation, model calls, Ollama, CCE, Graphify, Repomix, AI Context, MCP tools, LeanCTX, external repo clone, package install, demos, or tool execution.

## Safety / Product Boundaries

- The app is analysis-only.
- BookNLP is not canon.
- spaCy is not the sole center of this parent.
- dramatica-flow remains analysis-only/reference or future wrapped rubric source.
- Subtxt remains semantic guardrail/rubric source.
- NCP remains approved-context import/export target.
- Owner review remains mandatory.
- All outputs remain candidates until owner approval.
- No automatic canon mutation is allowed.

## Current Status

`PHASE8-IMPL-006` is active/published by `PHASE8-IMPL-006-T001`. `PHASE8-IMPL-006-T001` is docs/status/planning only and creates the parent, inventory, enrichment JSON, and scope decision. No runtime extraction starts in T001. No external tools are installed or run.

Next child: `PHASE8-IMPL-006-T002` - Evidence/source-map contract decision.
