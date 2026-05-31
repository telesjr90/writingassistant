# Decision Log

## Accepted Decisions

| Decision | Status | Rationale |
| --- | --- | --- |
| Product is analysis-only | Accepted | Protects writer authorship and keeps training/eval bounded |
| Standard refusal message | Accepted | Consistent no-prose behavior across app and training |
| Local-first architecture | Accepted | Current app uses FastAPI, React, local project files, and Ollama |
| Current baseline model is `qwen3:8b` | Accepted | Verified in `backend/analysis_engine.py` default |
| Future model name is `dramatica-analyst:8b` | Accepted | Target deployment name after non-smoke eval |
| MVP does not require fine-tuning | Accepted | App can progress with mock and baseline Ollama modes |
| NotebookLM/book output is candidate-only | Accepted | Prevents unreviewed aggregation from becoming truth |
| Book-level master packets are context, not direct SFT truth | Accepted | Excerpt-backed owner approval is required for training candidates |
| Packets promote through review JSONL first | Accepted | Avoids direct promotion of weak or unreviewed labels |
| No full verifier parity claim | Accepted | Current system cannot prove complete Dramatica storyforms |
| Canonical repository name | Accepted | Use `telesjr90/writingassistant` |
| Product working name | Accepted | Use Dramatica-Informed Writing Assistant |
| License boundary | Accepted | MIT applies to app source code only; training data, book sources, packet evidence, model artifacts, and datasets are excluded pending separate provenance/license review |
| Git initialization | Accepted | Local Git is initialized/repaired on `main`; `origin` is `https://github.com/telesjr90/writingassistant`; first safe local baseline commit is `25ef64d chore: initialize safe project baseline`; push remains TODO |
| Python dependency strategy | Accepted | Use simple requirements files now; `backend/requirements.txt` exists and remains separate from `training/requirements-unsloth.txt`; revisit `pyproject.toml`/`uv` later |
| Node target | Accepted | Target Node `>=22.12.0 <23`; package metadata update is deferred |
| Example fixture direction | Accepted | Replace Elena/Ember Crown mismatch later with one clean aligned fixture, preferably public-domain or owner-created |
| OMI MVP inclusion | Accepted | OMI is in the App MVP, bounded to analysis-only, no-prose, no story continuation, no rewriting, owner-controlled, candidate-first planning |
| OMI minimum schema | Accepted | Design target fields: `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`; do not assume endpoints/storage/UI exist yet |
| Durable memory promotion rule | Accepted | Owner must explicitly approve, choose destination, attach evidence/provenance, and confirm promotion |
| No-prose enforcement policy | Accepted | Enforce before model call and after model output |
| Mock mode output | Accepted | Use deterministic fixture JSON for `story_check`, `throughline_classification`, `writer_questions`, and `out_of_scope_refusal` |
| Reference repo role | Accepted | Prose-generation and autonomous-agent repos remain documentation-only; NCP may inform structure |
| qwen25 cloud smoke config | Accepted | Revise or create cloud smoke config before RunPod smoke |
| Books 4-5 decision gate | Accepted | Books 4-5 are conditional only after cross-book coverage review |
| Book folder policy | Accepted | Keep raw source text outside Git; store only safe derived metadata/review artifacts in repo |
| IC/RS evidence threshold | Accepted | Require owner-approved exact evidence per record; target at least 15-20 strong IC and 15-20 strong RS examples, preferably 30+ each |
| Book evidence approval format | Accepted | Use a consolidated owner-review worksheet with candidate answer, excerpt IDs, evidence, weak/contradicting evidence, confidence, owner decision, and final training status |

## Follow-Up Tasks, Not Open Decisions

| Task | Needed for | Current note |
| --- | --- | --- |
| Push safe baseline to GitHub | Remote publication | Local baseline exists; no push has been performed yet |
| Validate backend requirements over time | Reproducible backend setup | `backend/requirements.txt` exists; keep separate from `training/requirements-unsloth.txt` |
| Declare Node engine | Frontend setup | Target is `>=22.12.0 <23`; `package.json` not edited in this task |
| Replace sample fixture | MVP fixtures and docs | Use one aligned public-domain or owner-created fixture |
| Define OMI API/storage implementation | MVP OMI runtime work | Implementation-level follow-up; OMI remains candidate-first and no-prose |
| Build no-prose guard | Runtime safety | Must check before model call and after output |
| Build mock fixtures | App/test foundation | Four supported task JSON fixtures required |
| Revise cloud smoke config | RunPod readiness | Required before RunPod smoke |
| Run cross-book coverage review | Books 4-5 decision | Must review Books 1-3 coverage first |
| Define safe book artifact set | Git hygiene and provenance | Raw source text stays outside Git |
