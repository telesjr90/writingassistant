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
| R12 | Invalid Git repository prevents issue/project workflow | Medium | Confirmed | Initialize or repair Git after owner decision | Active |
| R13 | Missing dependency strategy blocks reproducibility | Medium | Medium | Add Python dependency plan after decision | Active |
| R14 | OMI assumptions leak into implementation | Medium | Medium | Keep OMI design-only until schema/storage approved | Active |
