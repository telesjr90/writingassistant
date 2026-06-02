# Risk Register

| ID | Risk | Impact | Likelihood | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| R1 | Model or docs overclaim Dramatica truth | High | High | Preserve owner-approved vs candidate vs insufficient-evidence boundaries | Active |
| R2 | Prose-generation leakage | High | Medium | Shared `backend/guardrails.py` input classifier and refusal response implemented; route/output integration and refusal eval remain TODO | Active |
| R3 | Weak IC/RS labels become positive training truth | High | High | Owner approval plus excerpt-backed evidence required | Active |
| R4 | CIPS/dynamics trained from insufficient evidence | High | High | Keep positive CIPS/dynamics owner-gated | Active |
| R5 | Dataset gate remains blocked | High | High | Prioritize packets and book-backed evidence triage | Active |
| R6 | Task mix skew persists | Medium | High | Add throughline/refusal records while reducing story_check dominance | Active |
| R7 | External datasets import unsupported Dramatica truth | High | Medium | Registry disallowed-use fields and human review | Active |
| R8 | NotebookLM output treated as truth | High | Medium | Mark candidate-only in all plans and reports | Active |
| R9 | Local GPU cannot train primary model | High | Confirmed | Use RunPod/larger GPU; smoke only locally if explicitly allowed | Active |
| R10 | Smoke model accidentally deployed | High | Medium | Label artifacts and block production export/deploy | Active |
| R11 | Sample project mismatch hides app bugs | Medium | Low | Local ignored `projects/example` fixture is now aligned from public-domain scene source; continue validating before MVP quality claims | Mitigated locally |
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
| R22 | Sample fixture introduces provenance or copyright ambiguity | High | Low | Local fixture metadata records public-domain source provenance; owner idea input is excluded from project truth and reserved for OMI tests | Mitigated locally |
| R23 | Malformed or noncompliant model JSON breaks Story Check UX | High | Medium | BE-002 reusable Story Check normalizer validates with `jsonschema` where available, coerces minimal UI fields, preserves rich diagnostics, and returns deterministic fallback for malformed output; SC-001 prompt now requests the normalized rich schema explicitly | Mitigated locally |
| R24 | Minimal UI breaks when Story Check responses become rich | Medium | Medium | SC-002 route compatibility tests cover minimal, rich, fallback, diagnostic, missing-rich-field, unknown-field, and error-shaped reports; current sidebar preserves raw JSON until FE-001 rich rendering | Mitigated locally |
| R25 | Live App-8 verification can regress on local Ollama transport or malformed qwen3 output | Medium | Medium | `OLLAMA_BASE_URL` supports WSL-to-Windows Ollama and App-8 live verification passed locally on 2026-06-01; keep `ANALYSIS_MODE=mock` usable for demos/tests and re-run live smoke after endpoint/model changes | Mitigated locally |
