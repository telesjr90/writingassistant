# PHASE8-IMPL-023 OpenCode Go Model Routing and Small-Task Execution

> Applicability and supersession notice: this accepted record remains
> historical authority for its original PHASE8-IMPL-023 T014–T026 execution
> scope. It does not determine current remaining-MVP routing. Current routing is
> governed by
> `docs/roadmap/decisions/PHASE8-IMPL-026-T012-current-truth-execution-routing-and-ui-guidance.md`
> and `docs/project-memory/registries/execution-routing.json`. Do not use this
> historical record to exclude Codex/GPT from a current assignment or to select
> the current application frontier.

## Result

Accepted as the controlling implementation-platform and model-routing decision for remaining PHASE8-IMPL-023 MVP live-runtime integration (T014–T026).

## Decision

1. **OpenCode Go** is the selected low-cost coding-agent platform for all remaining MVP implementation work in this repo.
2. **Cursor remains the editor**. OpenCode Go runs from the Cursor integrated terminal.
3. The normal/recommended model for docs/status and small scoped edits is `opencode-go/deepseek-v4-flash`.
4. Escalation for harder runtime/debugging work: `opencode-go/minimax-m3`, `opencode-go/kimi-k2.7-code`, Qwen/GLM options available in OpenCode Go, or `opencode-go/deepseek-v4-pro` depending on difficulty.
5. Final review/hard blockers: `opencode-go/deepseek-v4-pro` or `opencode-go/minimax-m3`.
6. OpenAI, Anthropic, Google, GPT, Claude, Gemini, and Google-hosted Gemma are **excluded** from this implementation workflow.

## Model-Routing Plan

| Lane | Recommended Model(s) | When |
|------|---------------------|------|
| Docs/status | `opencode-go/deepseek-v4-flash` or local/Ollama when sufficient | Default for status updates, decision records, docs-only tasks |
| Small backend/code-test tasks | `opencode-go/deepseek-v4-flash` | Small scoped edits, tests-first expected-red, focused validation |
| Runtime adapters/debugging | `opencode-go/minimax-m3`, `opencode-go/kimi-k2.7-code`, Qwen/GLM, `opencode-go/deepseek-v4-pro` depending on difficulty | Multi-file runtime adapter wiring, debugging, environment probe work |
| Final review/hard blockers | `opencode-go/deepseek-v4-pro` or `opencode-go/minimax-m3` | Closeout review, blocked-task unblocking, architecture reconciliation |

Cheap models are acceptable only when prompts are small, focused, scoped, and tests-first. Use stronger models only for blockers, multi-file runtime debugging, and closeout review.

## Plan Change

The remaining PHASE8-IMPL-023 roadmap (T014–T026) is changed from broad one-shot tasks to smaller model-routed subtasks:

- one tool at a time
- tests first
- no broad context dumps
- prompt size caps
- manual validation after each tool
- selective commits after passing validation
- owner-blocked/unavailable is valid; fake-complete is not
- strong model review only for hard blockers and final closeout

## Required Subtask Structure

For each task T014 through T026, the implementation workflow must follow this pattern:

1. **Inspect** existing contracts, current docs, and adapter fixture boundaries before any code change.
2. **Document** availability/preflight requirements for the tool.
3. **Document** tests-first expectations (expected-red contract tests before implementation).
4. **Implement** only after inspection and tests pass in expected-red mode, in a later subtask step.
5. **Document** manual validation expectations.
6. **Run** validation (pytest focused tests, targeted command).
7. **Prepare** selective commit (git add of only intended files, verify with git diff --cached --stat).

## T014–T026 Subtask Split

Each task splits into small subtasks similar to the established PHASE8 microtask pattern:

- `T0XX-a` — inspect/docs: understand existing contracts, docs, fixture boundaries
- `T0XX-b` — expected-red tests: write tests-first contract coverage
- `T0XX-c` — implementation: wire live adapter, pass contract tests
- `T0XX-d` — manual validation: run against real tool, document findings
- `T0XX-e` — closeout: update roadmap, prepare selective commit

Validation commands for every subtask:

```bash
git status --short --branch
git diff --stat
git diff --check
<focused pytest command for touched files>
```

## Tool-Specific Routing Notes

- **spaCy (T014)**: Start with `opencode-go/deepseek-v4-flash`. Escalate to `opencode-go/minimax-m3` if spaCy dependency install, model download, or pipeline wiring blocks.
- **Ollama/local model (T015)**: Start with `opencode-go/deepseek-v4-flash`. Escalate to `opencode-go/deepseek-v4-pro` if JSON schema negotiation or fail-closed edge cases are complex.
- **Story Check (T016)**: `opencode-go/deepseek-v4-flash` should handle the existing route wiring. The live integration reuses the existing `backend/analysis_engine.py` path.
- **BookNLP (T017)**: Start with `opencode-go/deepseek-v4-flash`. Escalate to `opencode-go/kimi-k2.7-code` or `opencode-go/minimax-m3` if BookNLP Java dependency or TSV parsing edge cases block.
- **NCP (T018)**, **Subtxt (T019)**, **dramatica-flow (T020)**: Reference-only tools. May be owner-blocked after preflight. Use `opencode-go/deepseek-v4-flash` for docs-only owner-blocked decision; escalate if live integration is unexpectedly required.
- **Fusion validation (T021)**, **persistence validation (T022)**: `opencode-go/deepseek-v4-flash` for expected-red contract expansion; `opencode-go/deepseek-v4-pro` or `opencode-go/minimax-m3` for edge-case resolution.
- **Owner-review UI (T023)**: `opencode-go/deepseek-v4-flash` for frontend work; `opencode-go/deepseek-v4-pro` or `opencode-go/minimax-m3` if React state management or API integration is complex.
- **Automated/manual tests (T024/T025)**: `opencode-go/deepseek-v4-flash` for test scripting; `opencode-go/minimax-m3` for Playwright debugging.
- **Closeout (T026)**: `opencode-go/deepseek-v4-pro` or `opencode-go/minimax-m3` for final review pass.

## Boundaries

- Candidate-only, evidence/provenance-backed output.
- No Memory/Canon mutation during analysis/runtime extraction.
- No automatic promotion records from analysis/runtime/model/tool output.
- No automatic apply-promotion from model/tool output.
- Owner-approved apply-promotion remains a separate explicit workflow.
- No generated story prose.
- Tool/model output is not canon.
- Confidence/support is not truth.
- Queue presence is not approval.
- Candidate persistence is not canon.
- Fail closed when runtime/model/tool output is unsafe, malformed, unavailable, or ambiguous.
- Owner review required for all candidate promotion.
- Fixture/mock adapter contracts are scaffolding only; they do not prove live analysis and do not count as MVP completion.

## Supersession

This decision does not supersede any product-safety or architecture decisions. It adds a platform-routing layer on top of the existing PHASE8-IMPL-023 parent scope. Existing safety boundaries, candidate-only rules, no-prose rules, and MVP completion requirements are unchanged.
