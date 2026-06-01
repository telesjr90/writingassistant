# Risk Register

| ID | Risk | Impact | Likelihood | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| R1 | Model or docs overclaim Dramatica truth | High | High | Preserve owner-approved vs candidate vs insufficient-evidence boundaries | Active |
| R2 | Prose-generation leakage | High | Medium | Prompt, runtime guard, refusal eval, output parser limits | Active |
| R3 | Weak IC/RS labels become positive training truth | High | High | Owner approval plus excerpt-backed evidence required | Active |
| R4 | CIPS/dynamics trained from insufficient evidence | High | High | Keep positive CIPS/dynamics owner-gated | Active |
| R5 | Dataset gate remains blocked | High | High | Prioritize packets and book-backed evidence triage | Active |
| R6 | Task mix skew persists | Medium | High | Add throughline/refusal records while reducing story_check dominance | Active |
| R7 | External datasets import unsupported Dramatica truth | High | Medium | Registry disallowed-use fields and human review | Active |
| R8 | NotebookLM output treated as truth | High | Medium | Mark candidate-only in all plans and reports | Active |
| R9 | Local GPU cannot train primary model | High | Confirmed | Use RunPod/larger GPU; smoke only locally if explicitly allowed | Active |
| R10 | Smoke model accidentally deployed | High | Medium | Label artifacts and block production export/deploy | Active |
| R11 | Sample project mismatch hides app bugs | Medium | Confirmed | Align Elena vs Ember Crown before MVP evaluation | Active |
| R12 | Safe baseline has not been pushed to GitHub | Medium | Medium | Push local commit `25ef64d` after owner approval; do not claim remote publication until complete | Active |
| R13 | Backend dependency manifest drifts from implementation | Medium | Medium | Keep `backend/requirements.txt` separate from training requirements and validate as runtime dependencies evolve | Active |
| R14 | OMI candidate output mistaken for story truth | High | Medium | Use candidate-only status, provenance/status labels, destination selection, and owner approval gate | Active |
| R15 | OMI accidentally becomes prose generation | High | Medium | Apply no-prose guard; OMI must not write, rewrite, continue, imitate, polish, or improve story prose | Active |
| R16 | OMI promotion mutates bible/storyform without owner approval | High | Medium | Require explicit owner decision, destination, provenance, status, and final promotion action | Active |
| R17 | OMI scope creep delays core Story Check MVP | Medium | Medium | Phase OMI implementation after backend guardrails/schema foundation and keep design-first slice bounded | Active |
| R18 | Schema-valid NCP data mistaken for verified story truth | High | Medium | Separate JSON Schema validation from semantic certainty; require owner-approved context and insufficient-evidence reporting | Active |
| R19 | Generic relationship or theme language becomes false RS/Issue proof | High | Medium | Keep RS/Issue/CIPS/dynamics claims owner-gated and evidence-grounded; preserve unresolved fields rather than guessing | Active |
| R20 | OMI template starters drift into prose generation | High | Medium | Define template starters as structural scaffolding only; block scene, dialogue, paragraph, chapter, and ending text | Active |
| R21 | OMI promotion proceeds with incomplete metadata | High | Medium | Require owner decision, destination, provenance, status, source candidate ID, timestamp, and final confirmation before promotion | Active |
