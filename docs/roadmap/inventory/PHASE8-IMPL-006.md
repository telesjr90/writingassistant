# PHASE8-IMPL-006 Inventory

## 1. Task Identity

- Parent ID: `PHASE8-IMPL-006`
- Title: Writer Assistant Core evidence-first extraction foundation and BookNLP-ready adapter strategy
- Track: Writer Assistant Core
- Phase: Phase 8
- Status: active
- Depends on: completed `PHASE8-IMPL-005`

## 2. Why This Parent Exists

`PHASE8-IMPL-005` chose the first extraction strategy and closed with a spaCy-first local deterministic/rule-assisted recommendation. Owner follow-up analysis in `docs/feasibility.md`, `docs/booknlp.md`, `docs/dramaticaflow.md`, `docs/subtxt.md`, and `docs/ncp.md` revised the next-parent shape.

The next safe parent should be evidence-first and BookNLP-ready before any runtime extraction starts. Stable source maps, source locators, evidence ledger shape, run provenance, and candidate normalization need to exist before BookNLP, spaCy, or any other extractor output can safely enter Writer Assistant Core.

## 3. Scope

In scope:

- evidence/source map contracts
- source document locator contracts
- Evidence Ledger design
- extraction run provenance model
- candidate normalization contracts
- raw tool output storage policy
- BookNLP-ready mapping strategy
- spaCy as optional lightweight baseline
- safety guardrails
- future integration points for dramatica-flow, Subtxt, and NCP

## 4. Non-Scope

Explicitly excluded:

- runtime extraction
- BookNLP install/run
- spaCy install/run
- dramatica-flow runtime
- NCP import/export
- Subtxt classifier
- generated prose
- rewriting
- continuation
- automatic Storyform truth
- memory/canon mutation
- apply-promotion
- frontend UI
- backend routes
- package/dependency changes
- training/JSONL/dataset work

## 5. Risks

- BookNLP output mistaken for canon
- BookNLP coreference/quote/event errors
- source locator mismatch
- raw tool output storage becoming truth
- dependency bloat
- premature package installation
- dramatica-flow generation leakage
- Subtxt overclaiming
- NCP import as truth
- owner-review bypass
- candidate/canon leakage
