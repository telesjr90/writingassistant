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
| OMI minimum schema | Accepted | Design target fields: `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`; OMI-003 through OMI-007 now implement the MVP candidate/review/promotion-record slices without apply-promotion behavior |
| Durable memory promotion rule | Accepted | Owner must explicitly approve, choose destination, attach evidence/provenance, and confirm promotion |
| No-prose enforcement policy | Accepted | Enforce before model call and after model output |
| Mock mode output | Accepted | Use deterministic fixture JSON for `story_check`, `throughline_classification`, `writer_questions`, and `out_of_scope_refusal` |
| Reference repo role | Accepted | Prose-generation and autonomous-agent repos remain documentation-only; NCP may inform structure |
| qwen25 cloud smoke config | Accepted | Revise or create cloud smoke config before RunPod smoke |
| Books 4-5 decision gate | Accepted | Books 4-5 are conditional only after cross-book coverage review |
| Book folder policy | Accepted | Keep raw source text outside Git; store only safe derived metadata/review artifacts in repo |
| IC/RS evidence threshold | Accepted | Require owner-approved exact evidence per record; target at least 15-20 strong IC and 15-20 strong RS examples, preferably 30+ each |
| Book evidence approval format | Accepted | Use a consolidated owner-review worksheet with candidate answer, excerpt IDs, evidence, weak/contradicting evidence, confidence, owner decision, and final training status |
| MVP exit test matrix | Accepted | MVP completion requires formal recorded validation across repo safety, backend tests, frontend build, Story Check modes, guardrails, context, OMI, evaluation harness, and manual smoke |
| Optional extractor track | Accepted as future/post-workspace | External tools may be evaluated later as replaceable candidate-only adapters around the app-owned pipeline; no extractor may generate prose, silently alter project truth, or bypass OMI |
| Book 1-3 owner answers implemented as prep artifacts | Accepted | Owner answers have been received and implemented in local reports as documentation/candidate queues only; no review JSONL, training JSONL, promotion, manifest update, or training run was performed |
| Fine-tuning prep paused after Book 1-3 mapping dry-run | Accepted | Dataset gate audit, Book 1-3 coverage matrix, owner decision extraction, owner-answer implementation, and review JSONL mapping dry-run are complete; no records were created or promoted; next fine-tuning step when resumed is evidence extraction/verification |
| App MVP Phase 6 promoted as active phase | Accepted | Fine-tuning remains outside the MVP critical path, so current project focus returns to MVP hardening / MVP exit matrix execution-preflight |
| Phase 6 Step 1 repo-safety refresh | Accepted | 2026-06-06 refresh found no dirty tracked `projects/example` fixture files; full backend tests, focused backend groups, frontend build, offline baseline eval, and mock Story Check smoke passed; live qwen3 remains deferred by design |
| Phase 6 Step 2 smoke refresh | Accepted | In-process mock backend route smoke passed, but true localhost backend/frontend server smokes are blocked by the current sandbox socket/listen restriction; browser checks remain owner-manual and live qwen3 remains deferred |
| Product pivot to Writer Assistant Core | Accepted and extended | Near-term work shifted from Dramatica-first analyzer planning to a local writer assistant core. The 2026-06-07 planning update adds Project Workspace Foundation before expanded Core extraction so the app becomes a usable writing workspace first. Dramatica remains a later advanced analysis layer. |
| OMI as central story knowledge review system | Accepted | Extracted story knowledge must enter OMI as candidate records with provenance/evidence where practical before any owner-approved promotion into durable project memory/canon. |
| External extractor dependency rule | Accepted | Do not install spaCy, segram, BookNLP, GLiNER, LangExtract, Renard, CoreNLP/OpenIE/SUTime, or other extractor dependencies until a dedicated spike evaluates license, maintenance, runtime cost, privacy/local-first behavior, evidence grounding, safety, candidate-only behavior, and OMI integration. |
| CORE-002/CORE-003 candidate and evidence model | Accepted as documentation | `docs/roadmap/writer_assistant_core_candidate_schemas.md` defines the first Writer Assistant Core candidate types plus shared base, evidence, provenance, owner decision, and promotion status models. Runtime implementation and project memory/canon layout remain future work. |
| CORE-004 project memory/canon storage model | Accepted as documentation | `docs/roadmap/project_memory_canon_storage_model.md` recommends folder-based `memory/*.json` files plus `memory/index.json` as the future durable story-knowledge target after OMI review and a later apply-promotion step. |
| CORE-005 OMI story-knowledge candidate expansion | Accepted as documentation | `docs/roadmap/omi_story_knowledge_candidate_expansion.md` defines future OMI typed review behavior, owner actions, merge/dedup planning, promotion-readiness rules, and UI/test implications without implementing runtime validation or apply-promotion. |
| Project Workspace Foundation before Dramatica expansion | Accepted | The app must become a general writing-project workspace before Dramatica-specific features, advanced extractors, RunPod work, Books 4-5, or fine-tuning expand. |
| WORKSPACE-001 Project Workspace Foundation spec | Accepted as documentation | `docs/roadmap/project_workspace_foundation_spec.md` defines the first usable workspace target, blank and OMI-guided creation flows, project library, pages, storage/model targets, safety rules, candidate/canon display rules, task sequence, and acceptance checklist. Runtime implementation remains future work. |
| Workspace-first priority order | Accepted | Sequence is project creation/library, chapters/scenes/notes/materials, owner-authored prose storage/editing, candidate extraction, owner approval and memory/canon pages, then later Dramatica-specific analysis. |
| OMI-guided project creation and idea capture | Accepted | OMI should support owner-controlled project setup and idea capture, organizing owner-provided ideas into candidates without generating story prose or canon. |
| Owner-authored prose storage is allowed | Accepted | The app may store, edit, save, reload, and organize owner-authored prose; owner-authored content must not be treated as a prohibited assistant prose-generation request. |
| AI-generated prose remains prohibited | Accepted | The AI must not write, rewrite, continue, imitate, polish, improve, or extend story prose; the standard refusal message remains required for those requests. |
| AI analysis of owner-authored prose is allowed | Accepted | The app/AI may analyze owner-authored material and project materials, but analysis output remains candidate-only until explicit owner approval. |
| Extracted project knowledge remains candidate-first | Accepted | Characters, locations/settings, timeline events, objects, plot threads, unresolved questions, summaries, continuity flags, and contradictions are OMI candidates until owner review. |
| Approved project knowledge is project-local canon only by explicit promotion | Accepted | Approved information becomes project-local memory/canon only through owner-controlled promotion, evidence/provenance, destination, final confirmation, and future apply-promotion. |
| External NLP/story tools integrate as adapters | Accepted | External tools may become replaceable adapters around the app-owned Writer Assistant Core pipeline; tool output is never authoritative and becomes OMI candidates, not canon. |
| Future extractor spike order | Accepted | spaCy is the likely first future local NLP spike after workspace and contracts are ready; segram, BookNLP, GLiNER, LangExtract, Renard, CoreNLP/OpenIE/SUTime, AI-Reader-V2, narrative-blueprint, and NovelClaw are later references/spikes only. Generation-heavy systems remain blocked or documentation-only. |
| WORKSPACE-002 project creation flow | Accepted as documentation | `docs/roadmap/project_creation_flow_spec.md` defines the future blank and OMI-guided project creation flow. First implementation should use a title-derived, owner-editable, filesystem-safe `project_id`, a metadata-only `project.json`, hybrid core-folder creation, scan-first project library support, no model calls, no generated prose, and candidate-only OMI setup until explicit owner confirmation. Runtime implementation remains future work. |
| WORKSPACE-003 project selector/library | Accepted as documentation | `docs/roadmap/project_selector_library_spec.md` defines the future selector/library flow. First implementation should scan `projects/` for folders with valid `project.json`, treat missing/corrupt/duplicate/unsafe folders as warning or recovery states, keep `projects/index.json` rebuildable navigation metadata only, show lightweight owner-authored metadata and cheap counts, open Project Overview by default, warn before switching away from unsaved owner-authored edits, and avoid model calls, extraction, OMI promotion, memory/canon mutation, deletion, training writes, or generated prose during listing/opening. Runtime implementation remains future work. |
| WORKSPACE-004 OMI-guided project creation | Accepted as documentation | `docs/roadmap/omi_guided_project_creation_spec.md` defines the future OMI-guided setup flow. First implementation should capture owner-authored ideas and metadata as staged setup state, organize setup candidates without prose generation, let the owner review and select fields, create the project only after final confirmation through WORKSPACE-002 rules, record `creation_method: "omi_guided"`, and copy selected raw idea/candidate records into project-local OMI for traceability without memory/canon apply-promotion. Runtime implementation remains future work. |
| WORKSPACE-005 chapter and scene data model | Accepted as documentation | `docs/roadmap/chapter_scene_data_model_spec.md` defines the future chapter/scene model. First implementation should keep owner-authored scene prose in Markdown, store chapter records and scene metadata separately, use generated stable IDs, treat `chapter.scene_ids` as canonical scene order, keep `scene_metadata.chapter_id` as a consistency aid, preserve unsaved owner edits on save/reload/switch boundaries, and avoid model calls, AI prose generation, OMI promotion, memory/canon mutation, extractor logic, training writes, or runtime project-file creation during planning. Runtime implementation remains future work. |

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
| Run cross-book coverage review | Books 4-5 decision | DONE locally for Books 1-3; Books 4-5 remain conditional and are not active while fine-tuning/book-backed prep is paused |
| Define safe book artifact set | Git hygiene and provenance | Raw source text stays outside Git |
| Run MVP completion test matrix | MVP exit | Preflight executed on 2026-06-05; Step 1 cleared the prior dirty-fixture blocker and passed automated tests/build/mock/offline checks; Step 2 passed in-process route smoke but sandbox blocks localhost server/dev-server smokes, so final MVP exit needs owner exception or rerun in a socket-enabled local environment |
| Research optional extractors | Post-MVP analysis tooling | Keep extractor output candidate-only through OMI, with provenance, owner review, guardrails, and no direct promotion |
| Review JSONL mapping dry-run for Book 1-3 owner candidates | Fine-tuning prep | DONE locally; next fine-tuning step when resumed is P0 evidence extraction/verification, not JSONL drafting |
| Define Writer Assistant Core schemas | Next product track | DONE locally as documentation in `docs/roadmap/writer_assistant_core_candidate_schemas.md`; CORE-004 project memory/canon storage remains next |
| Define project memory/canon storage | Writer Assistant Core storage | DONE locally as documentation; runtime apply-promotion, rollback tests, deduplication, IDs/hashes, and extractor strategy remain future tasks |
| Define OMI story-knowledge candidate expansion | Writer Assistant Core OMI review | DONE locally as documentation; runtime typed validation, filters, merge/dedup controls, and promotion-readiness calculations remain future tasks |
| Implement Project Workspace Foundation | Pre-Dramatica product milestone | FUTURE; project creation, selector/library, chapters/scenes/notes/materials, owner-authored editor, project pages, OMI-guided creation, extraction triggers, owner approval, and memory/canon pages remain implementation tasks |
