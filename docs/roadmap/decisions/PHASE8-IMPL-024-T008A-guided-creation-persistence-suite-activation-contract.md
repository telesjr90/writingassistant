# PHASE8-IMPL-024-T008A Guided-Creation Persistence Suite Activation Contract

## Status

Owner-approved documentation and task-activation record. This is a documentation and sequencing decision only; it does not implement or execute T008A.

## Activation

`PHASE8-IMPL-024-T008A - Guided-creation persistence suite` is activated as the immediate planned, dependency-satisfied, eligible application frontier under parent `PHASE8-IMPL-024-T008`. T008A has not begun.

Activation follows the completed T004 (responsive containment) and T005 (accessibility semantics and target sizing) workstreams through their six accepted commits:

| Task  | Commit                                     | Subject                                                          |
| ----- | ------------------------------------------ | ---------------------------------------------------------------- |
| T004A | `d6318c678f07015f0bfebc6997cc8c69cfd7cd2a` | `fix(ui): contain document controls (T004A)`                     |
| T004B | `d72ace8f25afb248afc39f6b38d1ad0fcdd8bcf6` | `fix(ui): contain OMI responsive workspace (T004B)`              |
| T004C | `faae964f65e7d68efe3c16bf21f11c6c258ff2d6` | `fix(ui): close responsive containment gaps (T004C)`             |
| T005A | `0825ababcf9f4785e6b55aee6b19fc5c7419355b` | `fix(ui): reconcile heading hierarchy and target policy (T005A)` |
| T005B | `30d33eda3aa077bd675aba1b6a3527b9d74ba348` | `fix(ui): improve mobile targets and focus visibility (T005B)`   |
| T005C | `a0d3bac4e3b7ce3f2c479c525e456c9a041fd17e` | `fix(ui): restore guided review focus (T005C)`                   |

T004A-T004C and parent T004 are complete/PASS. T005A-T005C and parent T005 are complete/PASS. PHASE8-IMPL-024 remains active and incomplete. Broad owner acceptance and MVP readiness remain blocked.

## T008 child order and dependencies

The owner-approved child order is:

1. T008A — Guided-creation persistence suite (planned, dependency-satisfied, eligible, immediate frontier, not begun)
2. T008B — Candidate lifecycle and grouped-review owner-decision suite (planned, unstarted, depends on T008A)
3. T008C — Promotion creation and handoff suite (planned, unstarted, depends on T008B)
4. T008D — Apply-promotion suite (planned, unstarted, depends on T008C)
5. T008E — Review-queue command suite (planned, unstarted, depends on T008D)
6. T008F — Non-mutating resilience and accessibility suite (planned, unstarted, depends on T008E)

The parent T008 workstream is active/in_progress. No T008 child is complete or in progress. T008B-T008F remain unstarted and dependency-gated. Do not activate or implement them.

## T008A controlling contract

### Purpose

Validate the accepted OMI-guided creation persistence contract through the real application path while preserving all pre-existing projects and owner-controlled, non-canon boundaries.

### Initial mode

T008A begins as validation-only.

No product code may be edited merely to make validation pass.

If a product defect is found:

1. preserve exact evidence;
2. identify the smallest suspected product surface;
3. stop;
4. report `PRODUCT_DEFECT_FOUND`;
5. require explicit correction authorization.

If the required validation infrastructure is absent:

- report `BLOCKED_TEST_INFRASTRUCTURE`;
- do not install dependencies;
- do not create or rewrite tooling without separate owner authorization.

### Required persistence assertions

The final T008A matrix must validate, where supported by the accepted live contract:

- one unique disposable `uiux-audit-*` project is created through the real guided-creation route and frontend path;
- exact owner-entered title is preserved;
- exact owner-entered raw idea is preserved;
- exact owner-entered setup-note text is preserved;
- project metadata identifies `creation_method: omi_guided`;
- the linked OMI idea exists;
- the linked setup Note exists;
- response and persisted metadata agree on project, OMI idea, and setup Note IDs;
- owner provenance is preserved;
- `model_generated` remains false where required by the accepted contract;
- stored records remain candidate/non-canon unless explicitly owner-approved elsewhere;
- no promotion occurs;
- no apply-promotion occurs;
- no approved Memory or Canon mutation occurs;
- ordinary blank-project creation remains isolated and unchanged;
- every pre-existing project is preserved;
- writes are restricted to the exact disposable project;
- failure handling is fail-closed and leaves no unexplained partial persistence;
- rollback and `recovery_required` behavior are tested only where the accepted implementation contract and current tooling support those states.

### Mutation isolation

Require:

1. one unique disposable project;
2. complete API and filesystem manifests before mutation;
3. immediate rejection or stop on writes outside the disposable project;
4. preservation of every pre-existing project;
5. exact request and response evidence;
6. exact persisted-file evidence;
7. evidence packaging before cleanup;
8. cleanup of only the exact disposable project;
9. an after-cleanup manifest proving restoration of pre-existing state;
10. no approved Memory or Canon mutation;
11. no promotion or apply-promotion;
12. no model, Story Check, extraction, or analysis-runtime call.

### Exclusions

T008A must not include:

- candidate owner-decision mutation;
- grouped-review mutation;
- promotion creation;
- apply-promotion;
- review-queue commands;
- the full T008F resilience/accessibility matrix;
- application feature implementation;
- schema or persistence redesign.

## Product boundaries

- Analysis-only, candidate-first, evidence/provenance-backed, and owner-controlled.
- Never generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, or revise story prose.
- Never treat candidates, confidence, queue presence, model output, or tools as canon.
- Never automatically promote or apply promotion.
- Never mutate approved Memory or Canon.
- Never modify datasets, training files, book sources, models, or fine-tuning configuration.
- Never call live models, Ollama, Story Check, extraction, BookNLP, spaCy, NCP, Subtxt, dramatica-flow, or another analysis runtime.

## Implementation-only mode

Project Memory remains preserved but paused and nonblocking. Do not invoke, repair, update, require, or use Project Memory scripts, tests, freshness, supervision, Plan Integrity, execution routing, Project Source rotations, continuation packages, or the Project Memory GitHub workflow. Reactivation as an application gate requires a later explicit owner decision.

## Git safety

Do not stage, commit, push, amend, rebase, reset, clean, restore, or stash during this activation. Committing requires separate explicit owner authorization.
