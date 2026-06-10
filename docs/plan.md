```markdown
# Dramatica-Informed Writing Assistant – Minimal Viable Core Plan

## 0. Project Overview
We are building a single‑UI local writer assistant inspired by Subtxt. The MVP foundation remains useful, but the next implementation priority has pivoted from Dramatica-first analysis to a pre-Dramatica **Project Workspace Foundation**: project creation, project library/selector, OMI-guided idea capture, chapter/scene/note organization, and owner-authored prose storage/editing. After that workspace is usable, **Writer Assistant Core** adds candidate extraction, OMI review, evidence, approved project memory/canon, and continuity assistance.

The MVP foundation will:
- Use the **Narrative Context Protocol (NCP)** as a bounded structural reference, not the near-term product backbone.
- Allow writing & editing scenes in a local project.
- Perform a **Story Check** analysis that flags narrative drift, inconsistency, and missing beats.
- Include bounded **Organize My Idea (OMI)** planning that captures raw ideas and structured candidates without generating story prose.
- Display the results in a sidebar alongside the editor.

OMI is part of the App MVP, but it is analysis/planning only. It must not write, rewrite, continue, imitate, polish, or improve story prose, and it must not silently promote ideas, candidates, model output, or NotebookLM output into durable project truth. OMI MVP fields are `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`; the current runtime slice captures owner-authored raw ideas and structured candidate planning records, supports owner review decisions, creates promotion audit records without mutating durable truth, and shows lifecycle/status/provenance details in the OMI panel.

MVP completion is governed by `docs/roadmap/mvp_completion_test_matrix.md`. The next product milestone is the Project Workspace Foundation, not Dramatica-specific implementation, advanced extractor dependency work, RunPod, Books 4-5, or fine-tuning. Optional analysis extractors are future Writer Assistant Core research, not MVP blockers and not dependencies to install now. Extractor output must route through OMI as candidate-only records before any owner-approved promotion.

Product layers:

1. User-authored prose storage/editing: owner content can be created, saved, edited, and organized without being treated as an AI prose request.
2. AI-assisted analysis: the app can analyze owner-authored material, but outputs remain candidate-only.
3. Candidate extraction: characters, locations/settings, timeline events, important objects, plot threads, unresolved questions, navigation summaries, continuity flags, and possible contradictions can be suggested with evidence/provenance.
4. Owner approval: pending/rejected candidates are not canon; owner approval, destination, provenance, and confirmation are required.
5. Approved memory/canon: explicit owner-controlled promotion creates project-local truth.
6. Future Dramatica analysis: storyform, throughline, IC/RS, CIPS/dynamics, advanced analyst models, and fine-tuning come later.

The current workspace is `/home/tjrpirateking/projects/WritingAssistantApplication`. The UI is a React app served by a FastAPI backend.

---

## 1. Prerequisites
- **OpenAI Codex CLI** installed and authenticated.
- Node.js & Python 3.10+ installed.
- An OpenAI API key exported as `OPENAI_API_KEY`.
- Working directory: `/home/tjrpirateking/projects/WritingAssistantApplication`.

---

## Phase 2 – Data Preparation (updated)

Goal: Paused future track. If resumed, build a multi-task dataset that teaches a model to diagnose narrative coherence against approved structural context and to ask writer-focused questions, **never to generate prose**. This is no longer the next implementation priority for the app.

1. Base model: **Qwen/Qwen2.5-7B-Instruct** (primary). Fallback: Qwen3-4B-Instruct-2507 if GPU is constrained.
2. Dataset structure: multi‑task SFT records. Each example includes:
   - task: "story_check" | "throughline_classification" | "writer_questions" | "out_of_scope_refusal"
   - storyform_context (all four throughlines, dynamics, concerns, issues, problem/solution)
   - bible_summary
   - scene_text
   - user_request
   - gold_output (strict JSON matching the task schema)
3. Output schemas (included in the plan as reference):

   **Story Check:**
   {
     "task": "story_check",
     "coherence_score": 7,
     "throughline_alignment": {
       "overall_story": {"present": true, "evidence": ["..."], "concerns": []},
       "main_character": {"present": true, "evidence": ["..."], "concerns": ["..."]},
       "influence_character": {"present": false, "evidence": [], "concerns": ["..."]},
       "relationship_story": {"present": false, "evidence": [], "concerns": []}
     },
     "theme_drift": {"status": "none|mild|serious|insufficient_evidence", "reason": "..."},
     "character_consistency": {"status": "consistent|inconsistent|insufficient_evidence", "reason": "..."},
     "warnings": ["max 5"],
     "suggestions": ["max 5"],
     "insufficient_evidence": ["missing info"]
   }

   **Throughline classification:**
   {
     "task": "throughline_classification",
     "primary_throughline": "overall_story|main_character|influence_character|relationship_story|mixed|insufficient_evidence",
     "secondary_throughlines": [],
     "confidence": 0.78,
     "evidence_spans": [{"text": "...", "supports": "...", "reason": "..."}],
     "why_not": {"overall_story": "...", "main_character": "...", "influence_character": "...", "relationship_story": "..."}
   }

   **Writer questions:**
   {
     "task": "writer_questions",
     "questions": [{"throughline": "...", "story_point": "...", "diagnostic_purpose": "...", "question": "..."}],
     "no_prose_generated": true
   }

   **Out-of-scope refusal:**
   {
     "task": "out_of_scope_refusal",
     "request_type": "prose_generation",
     "allowed_help": ["analysis", "diagnostic questions", "structural classification"],
     "message": "I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose."
   }

4. Dataset mix:
   - Story Check diagnostics: 40‑45%
   - Throughline classification: 25‑30%
   - Writer diagnostic questions: 20‑25%
   - Out‑of‑scope refusals: 5‑10%
5. Prioritise contrast pairs: same scene interpreted as OS vs. MC, Change vs. Steadfast, IC pressure vs. Relationship Story conflict, missing evidence vs. confident classification.
6. Prompt template for training:
   System: "You are a Dramatica-informed narrative analysis assistant. You do not write, rewrite, continue, imitate, or improve prose. You only perform structural analysis, throughline classification, and writer-focused diagnostic questioning. Return only valid JSON matching the requested schema. If evidence is insufficient, say what is missing instead of guessing."
   User: "TASK: {task}\nALLOWED OUTPUT SCHEMA:\n{json_schema}\nSTORYFORM CONTEXT:\n{storyform_context}\nSTORY BIBLE:\n{bible_summary}\nSCENE TEXT:\n{scene_text}\nUSER REQUEST:\n{user_request}"
   Assistant: {gold_output}
7. Target: 500‑1000 examples. Generate semi‑synthetic with human correction.

---

## 0.1 Master Plan Status Sync

- Local Git has been initialized/repaired on `main`.
- `origin` is `https://github.com/telesjr90/writingassistant`.
- First safe local baseline commit exists: `25ef64d chore: initialize safe project baseline`.
- Safe repository metadata exists, including `.gitignore`, `README.md`, `LICENSE`, `.env.example`, and `backend/requirements.txt`.
- Push to GitHub remains TODO.
- OMI is included in the App MVP only as bounded analysis/planning: no prose generation, no story continuation, no rewriting, no silent promotion, owner-controlled, and candidate-first.
- OMI design fields are `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`.

---

## 0.2 MVP Phase Order

Current status: App-1 architecture audit, App-2 project file model, App-3 NCP compatibility subset, App-3a / OMI-001 schema/lifecycle, OMI-002 storage model, OMI-003 candidate creation flow, OMI-004 owner decision and destination selection, OMI-005 promotion gate enforcement, OMI-006 fuller OMI UI/status/provenance workflow, OMI-007 no-prose/no-silent-promotion tests, sample project alignment spec, local public-domain `projects/example` fixture alignment, GUARD-001 shared runtime no-prose guard, GUARD-002 request-path guard policy, GUARD-003 post-model Story Check output guard, BE-001 analysis mode config, BE-002 Story Check normalizer, SC-001 rich Story Check prompt alignment, SC-002 minimal-to-rich route/UI compatibility checks, App-7 mock Story Check mode, App-8 live qwen3/Ollama baseline verification, App-12 app-level evaluation fixtures, App-13 offline baseline evaluation harness, FE-001 rich Story Check diagnostics sidebar, App-4 scene editor hardening, and App-5 bible/storyform read/write layer are complete locally. `owner_sample_input.md` is reserved for future OMI raw idea/candidate testing, not project truth. MVP exit matrix execution/preflight ran on 2026-06-05. Step 1 refresh on 2026-06-06 found no dirty tracked `projects/example` fixture files; Step 2 refresh passed mock backend server smoke, backend route smoke, mock Story Check route smoke, and frontend dev-server smoke after approved localhost execution. Owner acceptance/documentation of the committed public-domain fixture state and browser/manual checklist items remains recommended. App MVP Phase 6 remains the recommended active phase.

Dataset, book-backed, RunPod, and fine-tuning work remains outside the App MVP critical path; the app can progress through mock mode and qwen3/Ollama baseline mode without those gates. Fine-tuning prep is paused after the Book 1-3 review JSONL mapping dry-run; the next fine-tuning step when resumed is P0 evidence extraction/verification before any JSONL drafting.

After owner acceptance of the Phase 6 MVP foundation, the next implementation priority order is:

- Phase 7: Project Workspace Foundation: project creation, project library/selector, OMI-guided project creation, chapters/scenes/notes/materials, owner-authored prose editor, project overview, and initial workspace pages.
- Phase 8: Writer Assistant Core candidate schemas, OMI story-knowledge expansion, and adapter contracts.
- Phase 9: Candidate extraction from owner-authored material through normalized CORE schemas and OMI candidates.
- Phase 10: Owner approval, evidence/review UI, project-memory/canon pages, and no-silent-promotion gates.
- Phase 11: Continuity, relationship, timeline, and plot assistance.
- Phase 12: Future graph/timeline/search assistance after approved memory is useful.
- Later: Advanced Dramatica analysis.
- Later: fine-tuning / `dramatica-analyst` model.

Dramatica analysis remains allowed as a later advanced layer. It is not the next implementation priority, and the fine-tuned model remains outside the MVP/core critical path.

| Phase | Scope | Completion Definition |
| --- | --- | --- |
| 0 | Repo baseline and source-of-truth sync | Git repaired on `main`, safe metadata exists, local baseline commit `25ef64d` exists, push remains TODO, and docs reflect current state. |
| 1 | App architecture audit and project model decisions | Project storage, NCP subset, sample fixture direction, and OMI schema/lifecycle are specified without overclaiming current runtime support. |
| 2 | Backend safety and schema foundation | Story Check schema/normalizer, candidate-vs-owner truth boundary, insufficient-evidence handling, and pre/post no-prose guardrails are defined or implemented. |
| 3 | Mock and baseline Story Check | Story Check mock mode is complete; qwen3/Ollama baseline config is explicit and covered with mocked tests; live baseline reaches Windows Ollama through `OLLAMA_BASE_URL` and returns normalized schema-valid rich Story Check JSON; app-level evaluation fixtures and an offline baseline evaluation harness exist for future regression work. |
| 4 | Frontend MVP diagnostics | FE-001 rich Story Check sidebar, App-4 scene editor hardening, App-5 bible/storyform read/write, GUARD-002 request-path policy, and GUARD-003 Story Check output guard are complete; remaining work includes evaluation fixtures, OMI, and broader MVP hardening. |
| 5 | Bounded OMI MVP implementation | OMI captures raw ideas and structured candidates with owner decision, destination, provenance, and status; it cannot write prose or silently promote durable truth. OMI-003 implements raw idea and candidate creation, OMI-004 implements owner decision/status/destination updates, OMI-005 creates promotion records without applying them to durable project truth, OMI-006 makes lifecycle/status/provenance and promotion readiness visible in the panel, and OMI-007 adds focused no-prose/no-silent-promotion boundary tests. |
| 6 | MVP hardening | Story Check mock/qwen3, no-prose guardrails, bounded OMI, save/load, docs, local smoke checks, and the MVP exit test matrix are verified before release readiness. |

---

## Book-Backed Phase Status (updated)

The book-backed phase is paused as a candidate evidence workflow for improving Dramatica-informed analysis coverage. It does not bypass the dataset gates above.

- Book 1 is completed through the book-backed packet workflow, verified from the WSL-mounted folder `/mnt/e/WritingAssistantApplication/docs/books/dcc`. The repo-local folder `docs/books/dcc` is not present in this workspace.
- Book 2 is completed through the book-backed packet workflow, verified from the WSL-mounted folder `/mnt/e/WritingAssistantApplication/docs/books/projecthm`. The repo-local folder `docs/books/projecthm` is not present in this workspace.
- Book 3 is completed through the book-backed packet workflow, verified from the WSL-mounted folder `/mnt/e/WritingAssistantApplication/docs/books/thggalaxy`. The repo-local folder `docs/books/thggalaxy` is not present in this workspace.
- Dataset gate audit, Book 1-3 cross-book coverage matrix, owner decision extraction worksheet, owner answers implementation, and review JSONL mapping dry-run are complete as local prep artifacts.
- No JSONL records were created, no records were promoted, `dataset_manifest.json` was not updated, and no training ran.
- The next fine-tuning task when this track resumes is P0 evidence extraction/verification before any JSONL drafting.
- Books 4-5 remain conditional and should not start while the fine-tuning/book-backed track is paused.
- Books 6+ remain blocked for this phase.
- NotebookLM output remains candidate-only, not training truth.
- Book-level master packets remain context, not direct SFT truth.
- Excerpt-backed, owner-approved evidence remains preferred for SFT review candidates.

---

## Phase 3 – Fine‑Tuning (updated)

Goal: Train Qwen2.5-7B-Instruct as a bounded structural analyst that returns JSON and refuses prose generation.

Status: blocked/paused. Dataset readiness remains blocked at 149 eligible records with a 351-record gap, task mix outside target range, and unresolved source records in the train split. The fine-tuned model remains outside the MVP critical path; continue app validation through mock mode and the qwen3/Ollama baseline path while fine-tuning is paused.

1. Framework: Unsloth (QLoRA) on a single ≤16GB GPU.
2. QLoRA settings:
   - Quantization: 4‑bit NF4
   - Sequence length: 2048 for classification/questions; 4096 for Story Check
   - LoRA rank r=16, alpha=32, dropout 0.05
   - Target modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
   - Learning rate: 1e-4 to 2e-4
   - Epochs: 2‑3 with early stopping
   - Batch size: small per‑device, gradient accumulation to effective batch 32‑64
   - Eval every 100‑250 steps
3. Export: GGUF q4_k_m for Ollama; q8_0 for quality testing.
4. Evaluation checklist (do not rely on “sounds smart”):
   - JSON validity ≥99%
   - Schema compliance ≥98%
   - Throughline macro‑F1 ≥85% (initial milestone)
   - OS/MC/IC/RS confusion rate tracked per label
   - No‑prose violation rate 0% on refusal set
   - Evidence span relevance (human reviewed)
   - Change vs. Steadfast contrast accuracy (separate test set)
   - “Insufficient evidence” calibration (must not overclaim)
   - Compatibility with current app: parse through FastAPI/Ollama path
5. After training, export GGUF, load into Ollama as `dramatica-analyst:8b`, and swap the backend model default only after a non-smoke model passes evaluation. OMI is in the App MVP as bounded planning; raw idea/candidate creation, owner decision/destination updates, record-only promotion gate enforcement, lifecycle/status/provenance display, and no-prose/no-silent-promotion boundary tests exist locally, but durable promotion application remains unimplemented.

---
## 4. Verification
After all tasks, your directory should contain a functional local application. To verify:
```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication/backend
./run.sh
# In another terminal
cd /home/tjrpirateking/projects/WritingAssistantApplication/frontend
npm run dev
# Open http://localhost:5173
```
You should see the project navigation, the editor, and the analysis sidebar with a working Story Check button.

---

## 5. Next Steps (Beyond MVP)
- Writer Assistant Core schema planning for story knowledge candidates, evidence spans, provenance, and project memory/canon.
- Project memory/canon storage planning now recommends future folder-based `memory/*.json` files plus `memory/index.json`; runtime apply-promotion remains unimplemented.
- OMI story-knowledge candidate expansion planning defines future typed review behavior, owner actions, merge/dedup planning, and promotion-readiness rules; runtime typed validation remains unimplemented.
- OMI expansion for `character_candidate`, `location_candidate`, `object_candidate`, `organization_candidate`, `timeline_event_candidate`, `relationship_candidate`, `plot_thread_candidate`, `continuity_warning_candidate`, `annotation_candidate`, and `open_question_candidate`.
- Story knowledge extraction pipeline research for candidate entities/actions/relationships/timeline notes through OMI.
- Project Workspace Foundation implementation: use `docs/roadmap/project_workspace_foundation_spec.md` as the WORKSPACE-001 handoff for the first usable workspace target, use `docs/roadmap/project_creation_flow_spec.md` as the WORKSPACE-002 handoff for blank project creation, OMI-guided setup, safe `project_id` handling, `project.json`, hybrid folder creation, API/UI planning, and no-prose/candidate-canon safety tests, use `docs/roadmap/project_selector_library_spec.md` as the WORKSPACE-003 handoff for scan-first project discovery, project cards/lists, search/filter/sort, opening/switching behavior, invalid/corrupt handling, archive/delete planning, API/UI planning, and path-safety tests, use `docs/roadmap/omi_guided_project_creation_spec.md` as the WORKSPACE-004 handoff for owner-authored setup inputs, setup candidates, wizard/storage model, OMI-to-project handoff, API/UI planning, and no-prose/no-silent-promotion tests, use `docs/roadmap/chapter_scene_data_model_spec.md` as the WORKSPACE-005 handoff for chapter records, scene Markdown compatibility, scene metadata, ID/order/movement rules, save/reload behavior, API/UI planning, extraction provenance, and no-prose save tests, use `docs/roadmap/notes_materials_data_model_spec.md` as the WORKSPACE-006 handoff for notes/materials body storage, metadata, IDs, links, save/reload, local search/filter, reference/license boundaries, API/UI planning, and extraction provenance, use `docs/roadmap/user_authored_document_editor_workflow_spec.md` as the WORKSPACE-007 handoff for shared scene/note/material editor state, save/reload semantics, unsaved-change protection, conflict detection, no-prose UI safety, analysis separation, API/UI planning, and future editor workflow tests, use `docs/roadmap/project_overview_page_spec.md` as the WORKSPACE-008 handoff for the project landing page, safe overview content, quick actions, recent documents, OMI status, approved memory/canon snapshot, health warnings, API/UI planning, and future overview tests, use `docs/roadmap/chapters_scenes_page_spec.md` as the WORKSPACE-009 handoff for the dedicated Chapters / Scenes page, chapter and scene operations, editor integration, ordering/consistency behavior, local search/filter, analysis separation, API/UI planning, and future page tests, use `docs/roadmap/notes_materials_page_spec.md` as the WORKSPACE-010 handoff for the dedicated Notes / Materials page, note/material operations, editor integration, organization/linking, local search/filter, provenance/license warnings, analysis separation, API/UI planning, and future page tests, use `docs/roadmap/project_memory_canon_page_structure_spec.md` as the WORKSPACE-011 handoff for the Project Memory / Canon page structure, approved-vs-candidate labeling, category cards, promotion-record snapshots, empty states before apply-promotion, API/UI planning, health warnings, and future tests, and use `docs/roadmap/omi_ideas_candidates_page_spec.md` as the WORKSPACE-012 handoff for the dedicated OMI Ideas / Candidates page, owner raw ideas, candidate review, evidence/provenance, promotion readiness, audit-only promotion records, local filters/search, warning states, API/UI planning, page relationships, and future tests, and use `docs/roadmap/approved_characters_page_spec.md` as the WORKSPACE-013 handoff for the first approved-only category page: applied `character_memory_record` display, evidence/provenance panel, linked sources panel, candidate backlog snapshot, warning states, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests, and use `docs/roadmap/approved_locations_settings_page_spec.md` as the WORKSPACE-014 handoff for the second approved-only category page: applied `location_memory_record` display, evidence/provenance panel, linked sources panel, place hierarchy placeholder, scene usage snapshot, candidate backlog snapshot, warning states including parent/child cycle detection, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests, and use `docs/roadmap/approved_timeline_page_spec.md` as the WORKSPACE-015 handoff for the third approved-only category page: applied `timeline_event_memory_record` display, evidence/provenance panel, linked sources panel, chronology/ordering placeholder, cause/effect placeholder, scene usage snapshot, candidate backlog snapshot, warning states including sequence collisions, chronology conflicts, and cause/effect cycles, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests, and use `docs/roadmap/approved_plot_threads_page_spec.md` as the WORKSPACE-016 handoff for the fourth approved-only category page: applied `plot_thread_memory_record` display, evidence/provenance panel, linked sources panel, linked timeline/scene snapshot, related characters/locations/objects snapshot, related open-questions and continuity-warnings placeholders, candidate backlog snapshot, warning states including thread status conflicts, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests, use `docs/roadmap/continuity_consistency_page_spec.md` as the WORKSPACE-017 handoff for the Continuity / Consistency page: applied `continuity_warning_memory_record` or `consistency_issue_memory_record` display, evidence/provenance panel, linked sources panel, linked story-knowledge snapshot, resolution placeholder, candidate backlog snapshot, warning states including status/resolution conflicts, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests, use `docs/roadmap/approved_open_questions_page_spec.md` as the WORKSPACE-018 handoff for the Approved Open Questions page: applied `open_question_memory_record` or `unresolved_question_memory_record` display, evidence/provenance panel, linked sources panel, linked story-knowledge snapshot, owner-answer/resolution placeholder, candidate backlog snapshot, warning states including answer/resolution conflicts and broken/cyclic related-question links, API/UI planning, no-prose/no-silent-promotion boundaries, and future tests, use `docs/roadmap/approved_relationships_page_spec.md` as the WORKSPACE-019 handoff for the Approved Relationships page: applied `relationship_memory_record` display, participant snapshot, linked story-knowledge snapshot, related plot/timeline/open-question/continuity snapshots, evidence/provenance panel, candidate backlog snapshot, warning states including participant/type/status conflicts and broken related links, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica Relationship Story boundaries, and use `docs/roadmap/approved_organizations_groups_page_spec.md` as the WORKSPACE-020 handoff for the Approved Organizations / Groups page: applied `organization_memory_record` or `group_memory_record` display, members/leadership snapshot, hierarchy snapshot, linked story-knowledge snapshot, related relationship/plot/timeline/open-question/continuity snapshots, evidence/provenance panel, candidate backlog snapshot, warning states including membership/leadership conflicts, hierarchy cycles, type/status conflicts, and broken related links, API/UI planning, no-prose/no-silent-promotion boundaries, and explicit non-Dramatica structural-claim boundaries.
- Future extractor architecture uses replaceable adapters around the app's own CORE pipeline. spaCy is the likely first future local NLP spike after contracts are ready; segram, BookNLP, GLiNER, LangExtract, Renard, CoreNLP/OpenIE/SUTime, AI-Reader-V2, narrative-blueprint, and NovelClaw are later references/spikes only. Generation-heavy systems remain blocked or documentation-only.
- Dynamic storyform questionnaire as a later advanced Dramatica layer.
- NovelClaw‑style memory banks as future inspiration only.
- Dramatron-style scene generation remains blocked/non-goal.
- World‑building interface (Notebook‑inspired).
- Support for local LLMs (Ollama).

---

**How to use this plan:**
1. Create the `codex.yml` file in your project root.
2. Place this entire plan as `docs/plan.md` in the repository.
3. Run Codex:
   ```bash
   codex init
   codex run "Follow the plan in plan.md step by step. Confirm with me before writing files."
   ```
```

