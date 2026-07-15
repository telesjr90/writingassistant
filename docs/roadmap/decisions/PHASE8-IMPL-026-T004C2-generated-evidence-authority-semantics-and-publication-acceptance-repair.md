# PHASE8-IMPL-026-T004C2 — Generated-evidence authority semantics and publication acceptance repair

## Result

T004C2: **complete/PASS**

Accepted current publication: **pending the post-T004C2 clean-HEAD refresh**.

## Starting repository

- Repository: `/home/tjrpirateking/projects/WritingAssistantApplication-project-memory`
- Branch: `docs/project-memory-foundation`
- Full HEAD: `91aef0425c22d2b1f0aaa6d4f3482baa1f5dc68c`
- Subject: `fix(pm): derive task status and enforce semantic render gates (T004C1)`
- Staging and tracked/untracked worktree: clean
- Original application worktree: not accessed or modified

## Rejected T004C1 refresh

- Run: `20260714T213628Z`
- Snapshot: `.codex-context/project-memory/PHASE8-IMPL-026-T004C1/20260714T213628Z/`
- Render: `.codex-context/project-memory/rendered/PHASE8-IMPL-026-T004C1/20260714T213628Z/`
- Quality: `.codex-context/project-memory/PHASE8-IMPL-026-T004C1-quality/20260714T213628Z/`
- Bound commit: `91aef0425c22d2b1f0aaa6d4f3482baa1f5dc68c`
- Snapshot/render structure: valid and checksum-clean
- Freshness: current
- Publication eligibility: true
- Task-state convergence: pass
- Structured authority result: fail
- Acceptance: rejected; it is not the accepted current publication

## Exact original authority matches

The committed T004C1 rule evaluated each whole page as:

```python
if "authoritative" in text and "generated evidence" not in text[:200]:
    authority_ok = False
```

Every page begins with the valid capitalized banner `Generated evidence — not
project authority`. The rule searched the first 200 characters for lowercase
`generated evidence`, so that banner never satisfied the case-sensitive guard.
Any later lowercase `authoritative` token rejected the page.

The rule encountered 58 lines across 11 pages:

- Tracked-record authority metadata (an **Authority** field with value
  `authoritative`):
  - `application-overview.md`: 39, 52
  - `assets.md`: 54, 65, 76
  - `features.md`: 40, 50, 60, 70, 80
  - `product-boundaries.md`: 41, 51, 61, 71, 81, 91, 101, 111, 121, 131
  - `decisions.md`: 39, 50, 63, 73, 83, 93, 103, 113
  - `current-roadmap.md`: 45, 56, 68, 78, 87, 97, 108, 119, 130, 141, 152, 163
  - `capabilities.md`: 43, 54, 65, 76, 87
  - `dependencies.md`: 42, 53, 64, 74, 84
- Tracked finding metadata: `convergence-findings.md:55`, an **Authority
  context** field with value `authoritative`.
- Trust-class vocabulary/counts: `index.md:84`,
  an `authoritative` count of 52; `technical-annex.md:127`, the
  `authoritative` trust-class value.
- Explicit non-authority disclaimers: `product-boundaries.md:83`, generated
  explanations “are not authoritative”; `technical-annex.md:156`, output is
  generated evidence, “never authoritative”.
- Higher-authority/prohibition descriptions: `product-boundaries.md:133`, no
  automatic mutation of authoritative state; `decisions.md:43`, authoritative
  roadmap and live code; `decisions.md:96`, PHASE8-IMPL-026 is the
  authoritative roadmap parent.

None of these 58 lines claims that the generated publication is authoritative.
They are tracked-source metadata, hierarchy/trust-class descriptions,
non-authority disclaimers, or references to accepted roadmap/owner authority.

## Verified cause

The failure was a validator false positive caused by page-wide keyword matching,
case-sensitive banner handling, and no statement-subject analysis. The rendered
wording is correct. `scripts/project_memory/render_docs.py` and
`tests/project_memory/test_render_docs.py` required no modification.

## Authority semantics contract

Generated pages must carry the exact `Generated Evidence — Not Project
Authority` banner. The validator allows:

- generated-evidence classifications and explicit non-authority statements;
- tracked-record authority metadata;
- accepted roadmap and owner-decision authority descriptions;
- seven-tier authority-hierarchy and eight trust-class descriptions;
- truth/canon/automatic-promotion prohibitions;
- technical validation descriptions and clearly labeled historical quotations;
- inline-code-only vocabulary and Markdown links to authoritative tracked sources.

The validator forbids a generated page, render, snapshot, package,
documentation, output, or publication from claiming that it:

- is authoritative, project authority, project truth, or a source of truth;
- controls roadmap, task, or project status;
- overrides, supersedes, or outranks tracked roadmap records or sources;
- resolves owner decisions;
- establishes canon;
- automatically approves or promotes candidates;
- has equal or greater authority than tracked sources.

## Validator repair

`scripts/project_memory/validate_rendered_docs.py` now:

- requires the exact generated-evidence banner;
- normalizes Markdown headings, table cells, and link labels;
- ignores fenced examples and inline-code-only authority vocabulary;
- recognizes negated disclaimers, technical rule descriptions, and historical quotations;
- applies explicit subject-aware forbidden-claim regular expressions;
- returns an `authority` object with `result`, `matches`,
  `allowed_references`, and `forbidden_claims`;
- reports each forbidden claim with page, line, text, rule, classification,
  and reason;
- removes the generic `Some pages may claim authoritative status` warning;
- treats forbidden authority claims as blocking semantic errors;
- carries the four accepted snapshot `source_missing` warnings into semantic
  results so the preserved package remains `PASS_WITH_FINDINGS` for the correct reason.

## Tests

`tests/project_memory/test_validate_rendered_docs.py` adds 27 focused authority
cases covering all required allowed and forbidden statements, headings, tables,
mixed allowed/forbidden content, diagnostics, fenced code, preserved-package
acceptance, and preservation checks. The validator file now contains 50 tests.

Total Project Memory tests: **245**.

## Validation and publication boundary

- No snapshot, render, or quality package was generated from the dirty worktree.
- The preserved `20260714T213628Z` render passes repaired authority validation
  with zero forbidden claims.
- Its overall semantic result remains `PASS_WITH_FINDINGS` solely because of
  four accepted nonblocking `source_missing` findings.
- T004/T004C/T004C1/T005 task-state checks, remaining work, application
  frontier, and PHASE8-IMPL-025 checks remain passing.
- A post-commit clean-HEAD snapshot/render/semantic/quality refresh is required
  before accepting a current publication.

## Status

| Task | Status |
| --- | --- |
| T004 | complete/PASS-WITH-FINDINGS |
| T004C | complete/PASS-WITH-FINDINGS |
| T004C1 | complete/PASS |
| T004C2 | complete/PASS |
| T005 | planned next/inactive |

T004 and T004C remain closed. T005 is not activated and must not start during
T004C2. The application frontier remains `PHASE8-IMPL-024-T003A`.
PHASE8-IMPL-025 remains published/planned and inactive.

## Q151–Q154

- Q151 — Full Plan Integrity classification model: open.
- Q152 — Serena adoption criteria: open.
- Q153 — Embedding-model selection: open.
- Q154 — Operational synchronization cadence: open. Exact commit binding and
  registry-derived task truth work. T004C1 exposed the false-positive authority
  gate. T004C2 repairs authority semantics. Operational refresh cadence remains
  unresolved.

## Risks

T004C2 mitigates naive authority-keyword matching, false rejection of correct
generated-evidence disclaimers, and authority failures without actionable
page/line evidence. Structurally valid packages still require explicit semantic,
authority, quality, and checksum acceptance. Stale operational publications and
synchronization cadence remain active risks.

## Tracked scope

Created:

- `docs/roadmap/decisions/PHASE8-IMPL-026-T004C2-generated-evidence-authority-semantics-and-publication-acceptance-repair.md`

Modified:

- `scripts/project_memory/validate_rendered_docs.py`
- `tests/project_memory/test_validate_rendered_docs.py`
- `docs/project-memory/README.md`
- `docs/project-memory/rendering/README.md`
- `docs/roadmap/tasks/PHASE8-IMPL-026.md`
- `docs/roadmap/inventory/PHASE8-IMPL-026.md`
- `docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json`
- `docs/roadmap/decision_log.md`
- `docs/roadmap/implementation_status.md`
- `docs/roadmap/task_backlog.md`
- `docs/roadmap/phase_map.md`
- `docs/roadmap/open_questions.md`
- `docs/roadmap/risk_register.md`

`docs/roadmap/roadmap_index.yaml` is unchanged because the established index
contains the PHASE8-IMPL-026 parent and T001 controlling decision, not lettered
post-closeout repair slices.

No protected schema, registry, scanner, snapshot builder, application,
dependency, generated-evidence, PHASE8-IMPL-024-specific, or
PHASE8-IMPL-025-specific path was modified.
