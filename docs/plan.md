```markdown
# Dramatica-Informed Writing Assistant – Minimal Viable Core Plan

## 0. Project Overview
We are building a single‑UI writing tool inspired by Subtxt. The MVP will:
- Use the **Narrative Context Protocol (NCP)** as the structural backbone.
- Allow writing & editing scenes in a local project.
- Perform a **Story Check** analysis that flags narrative drift, inconsistency, and missing beats.
- Include bounded **Organize My Idea (OMI)** planning that captures raw ideas and structured candidates without generating story prose.
- Display the results in a sidebar alongside the editor.

OMI is part of the App MVP, but it is analysis/planning only. It must not write, rewrite, continue, imitate, polish, or improve story prose, and it must not silently promote ideas, candidates, model output, or NotebookLM output into durable project truth. OMI MVP fields are `raw_idea`, `candidates`, `owner_decision`, `destination`, `provenance`, and `status`; the first runtime slice now captures owner-authored raw ideas and structured candidate planning records without promotion.

The current workspace is `/home/tjrpirateking/projects/WritingAssistantApplication`. The UI is a React app served by a FastAPI backend.

---

## 1. Prerequisites
- **OpenAI Codex CLI** installed and authenticated.
- Node.js & Python 3.10+ installed.
- An OpenAI API key exported as `OPENAI_API_KEY`.
- Working directory: `/home/tjrpirateking/projects/WritingAssistantApplication`.

---

## Phase 2 – Data Preparation (updated)

Goal: Build a multi‑task dataset that teaches a model to diagnose narrative coherence against a Dramatica storyform and to ask writer‑focused questions, **never to generate prose**.

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

Current status: App-1 architecture audit, App-2 project file model, App-3 NCP compatibility subset, App-3a / OMI-001 schema/lifecycle, OMI-002 storage model, OMI-003 candidate creation flow, OMI-004 owner decision and destination selection, sample project alignment spec, local public-domain `projects/example` fixture alignment, GUARD-001 shared runtime no-prose guard, GUARD-002 request-path guard policy, GUARD-003 post-model Story Check output guard, BE-001 analysis mode config, BE-002 Story Check normalizer, SC-001 rich Story Check prompt alignment, SC-002 minimal-to-rich route/UI compatibility checks, App-7 mock Story Check mode, App-8 live qwen3/Ollama baseline verification, App-12 app-level evaluation fixtures, App-13 offline baseline evaluation harness, FE-001 rich Story Check diagnostics sidebar, App-4 scene editor hardening, and App-5 bible/storyform read/write layer are complete locally. `owner_sample_input.md` is reserved for future OMI raw idea/candidate testing, not project truth. The next App MVP task is OMI-005 promotion gate enforcement.

Dataset, book-backed, RunPod, and fine-tuning work remains outside the App MVP critical path; the app can progress through mock mode and qwen3/Ollama baseline mode without those gates.

| Phase | Scope | Completion Definition |
| --- | --- | --- |
| 0 | Repo baseline and source-of-truth sync | Git repaired on `main`, safe metadata exists, local baseline commit `25ef64d` exists, push remains TODO, and docs reflect current state. |
| 1 | App architecture audit and project model decisions | Project storage, NCP subset, sample fixture direction, and OMI schema/lifecycle are specified without overclaiming current runtime support. |
| 2 | Backend safety and schema foundation | Story Check schema/normalizer, candidate-vs-owner truth boundary, insufficient-evidence handling, and pre/post no-prose guardrails are defined or implemented. |
| 3 | Mock and baseline Story Check | Story Check mock mode is complete; qwen3/Ollama baseline config is explicit and covered with mocked tests; live baseline reaches Windows Ollama through `OLLAMA_BASE_URL` and returns normalized schema-valid rich Story Check JSON; app-level evaluation fixtures and an offline baseline evaluation harness exist for future regression work. |
| 4 | Frontend MVP diagnostics | FE-001 rich Story Check sidebar, App-4 scene editor hardening, App-5 bible/storyform read/write, GUARD-002 request-path policy, and GUARD-003 Story Check output guard are complete; remaining work includes evaluation fixtures, OMI, and broader MVP hardening. |
| 5 | Bounded OMI MVP implementation | OMI captures raw ideas and structured candidates with owner decision, destination, provenance, and status; it cannot write prose or silently promote durable truth. OMI-003 implements raw idea and candidate creation, and OMI-004 implements owner decision/status/destination updates without promotion. |
| 6 | MVP hardening | Story Check mock/qwen3, no-prose guardrails, bounded OMI, save/load, docs, and local smoke checks are verified before release readiness. |

---

## Book-Backed Phase Status (updated)

The book-backed phase is active as a candidate evidence workflow for improving Dramatica-informed analysis coverage. It does not bypass the dataset gates above.

- Book 1 is completed through the book-backed packet workflow, verified from the WSL-mounted folder `/mnt/e/WritingAssistantApplication/docs/books/dcc`. The repo-local folder `docs/books/dcc` is not present in this workspace.
- Book 2 is completed through the book-backed packet workflow, verified from the WSL-mounted folder `/mnt/e/WritingAssistantApplication/docs/books/projecthm`. The repo-local folder `docs/books/projecthm` is not present in this workspace.
- Book 3 is completed through the book-backed packet workflow, verified from the WSL-mounted folder `/mnt/e/WritingAssistantApplication/docs/books/thggalaxy`. The repo-local folder `docs/books/thggalaxy` is not present in this workspace.
- After Book 3, the next step is cross-book review and deciding whether Books 4-5 are needed.
- Books 6+ remain blocked for this phase.
- NotebookLM output remains candidate-only, not training truth.
- Book-level master packets remain context, not direct SFT truth.
- Excerpt-backed, owner-approved evidence remains preferred for SFT review candidates.

---

## Phase 3 – Fine‑Tuning (updated)

Goal: Train Qwen2.5-7B-Instruct as a bounded structural analyst that returns JSON and refuses prose generation.

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
5. After training, export GGUF, load into Ollama as `dramatica-analyst:8b`, and swap the backend model default only after a non-smoke model passes evaluation. OMI is in the App MVP as bounded planning; raw idea/candidate creation and owner decision/destination updates exist locally, but promotion remains unimplemented.

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
- Dynamic storyform questionnaire.
- NovelClaw‑style memory banks.
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

