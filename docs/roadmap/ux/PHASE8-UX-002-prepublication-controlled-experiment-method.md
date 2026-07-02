# PHASE8-UX-002 Prepublication Controlled-Experiment Method

## Purpose

This document defines a black-box controlled-experiment method for future `PHASE8-UX-002-T002A` external SaaS UI reference research.

The method exists only for a future research spike. It may inform UX planning and acceptance matrix design by helping map visible UI panel, workflow, and safe route-shape dependencies. It must not infer hidden algorithms as truth from black-box observations alone, copy an external product, or create product requirements by itself.

`PHASE8-UX` may also retrieve and summarize authorized non-black-box reference information when the owner has authorization to access or provide it. This includes official documentation, owner-provided evidence, authorized disclosures, and other lawful reference materials about algorithms, prompts, model routing, ranking logic, workflow rules, or implementation details. That information still needs to be collected, provenance-labeled, summarized, and reviewed before use as `PHASE8-UX` reference input.

## Non-Goals

- No product implementation.
- No crawler scripts.
- No dependency installation.
- No raw capture generation in this task.
- No `.external_sources` creation in this task.
- No Playwright, Browsertrix, Crawlee, Stagehand, or external SaaS run in this task.

## One-Variable-at-a-Time Method

- Establish and capture a baseline before state in a small owner-controlled test story in the owner's authenticated external SaaS account.
- Change exactly one variable.
- Capture the after state.
- Compare visible UI, workflow, and route-shape/status-class changes.
- Record confidence as `observed`, `inferred`, or `unknown`.
- Record alternative explanations such as cache, session history, background recomputation, prior state, account configuration, or unrelated platform changes.

All controlled-experiment findings are black-box observations. Hidden algorithms, prompts, model weights, model routing, ranking logic, and proprietary implementation details can be known only through explicit authorized disclosure, official documentation, owner-provided evidence, or other lawful non-black-box evidence. They must not be claimed as known from black-box controlled experiments alone.

Authorized non-black-box evidence may supplement controlled experiments, but it remains reference material. It does not become product architecture, roadmap truth, canon, or a product requirement by itself.

## Safe Controlled-Experiment Observation Schema

This schema is documentation only, not executable code:

```json
{
  "experiment_id": "experiment-0001",
  "captured_at": "ISO-8601",
  "reference_platform": "redacted-name-or-label",
  "account_scope": "owner-authenticated-only",
  "test_story_id": "local-reference-id",
  "variable_changed": {
    "name": "story premise",
    "before_summary": "short non-proprietary summary",
    "after_summary": "short non-proprietary summary",
    "raw_values_saved": false
  },
  "before_state": {
    "page_label": "Storyform Builder",
    "visible_panel_summaries": ["panel labels and high-level states only"],
    "screenshot_refs": ["untracked/path/before.png"],
    "trace_refs": ["untracked/path/before-trace.zip"]
  },
  "after_state": {
    "page_label": "Storyform Builder",
    "visible_panel_summaries": ["panel labels and high-level states only"],
    "screenshot_refs": ["untracked/path/after.png"],
    "trace_refs": ["untracked/path/after-trace.zip"]
  },
  "changed_ui_panels": [
    {
      "panel_label": "Analysis Suggestions",
      "change_type": "content_changed|enabled|disabled|warning_changed|count_changed|selection_changed",
      "change_summary": "high-level summary only"
    }
  ],
  "safe_network_observations": [
    {
      "method": "POST",
      "route_shape": "/api/.../analysis/...",
      "status_class": "2xx",
      "request_body_saved": false,
      "response_body_saved": false,
      "notes": "route shape only; no payload committed"
    }
  ],
  "analysis_output_shift": {
    "changed": true,
    "summary": "high-level category/label/state change only",
    "raw_output_saved": false
  },
  "inferred_dependency_edges": [
    {
      "from": "story premise",
      "to": "analysis suggestions panel",
      "relationship": "may influence",
      "confidence": "observed|inferred|unknown",
      "evidence_refs": ["experiment-0001", "screenshot ref", "trace ref"],
      "alternative_explanations": ["cache/state/session/history may also affect output"]
    }
  ],
  "mapping_to_our_ui": [
    {
      "phase8_ux_002_gap": "Story Check diagnostic-only UI",
      "pattern_to_borrow": "show selected source and changed analysis state",
      "pattern_to_reject": "opaque output without provenance/confidence caveat"
    }
  ],
  "safety_notes": [
    "No proprietary text copied into committed docs.",
    "No hidden algorithm claim made from black-box observation alone.",
    "Raw artifacts remain untracked."
  ]
}
```

## Safe Inferred Dependency Graph Schema

This schema is documentation only, not executable code:

```json
{
  "graph_id": "reference-ui-inferred-dependency-graph-0001",
  "created_at": "ISO-8601",
  "source": "summarized controlled experiments only",
  "nodes": [
    {
      "id": "variable.story_premise",
      "type": "input_variable",
      "label": "Story premise"
    },
    {
      "id": "panel.analysis_suggestions",
      "type": "ui_panel",
      "label": "Analysis suggestions"
    }
  ],
  "edges": [
    {
      "from": "variable.story_premise",
      "to": "panel.analysis_suggestions",
      "relationship": "may influence",
      "confidence": "observed",
      "evidence_experiment_ids": ["experiment-0001"],
      "notes": "Observed UI panel change after one variable change; hidden reasoning unknown."
    }
  ],
  "confidence_legend": {
    "observed": "directly visible in UI/network metadata under controlled one-variable change",
    "inferred": "reasonable hypothesis supported by repeated observations but not directly proven",
    "unknown": "not enough evidence or confounded by other changes"
  },
  "prohibited_claims": [
    "No claim of internal algorithm access from black-box observation alone.",
    "No claim of exact proprietary reasoning.",
    "No product requirement inferred solely from external behavior."
  ]
}
```

## Raw Untracked Output Extension

Future `PHASE8-UX-002-T002A` may use this proposed untracked structure:

```text
.external_sources/dramatica-ui-reference/
  controlled-experiments/
    experiments.jsonl
    dependency-graph-draft.json
    variable-change-log.md
    confidence-notes.md
    before-after-screenshots/
    traces/
    har/
```

This task must not create `.external_sources`. This task only documents the future structure. Raw controlled-experiment captures must never be committed.

## Committed Docs Output Extension

Future `PHASE8-UX-002` may include:

```text
docs/roadmap/ux/PHASE8-UX-002-controlled-experiment-method.md
docs/roadmap/ux/PHASE8-UX-002-inferred-dependency-patterns.md
```

These docs must contain summaries only. They must not contain raw screenshots, traces, HAR files, API payloads, copied platform text, auth state, browser profiles, cookies, raw scraped content, or raw response bodies.

## Placement in PHASE8-UX-002

- Controlled experiments belong in `PHASE8-UX-002-T002A` after `T001` parent publication and `T002` acceptance matrix framing.
- Experiments inform UI design patterns only.
- Experiments must not delay MVP-critical implementation once missing route/workflow UI is clear.
- The inferred dependency graph is a research artifact, not a product architecture requirement.

## Product Boundary

The app remains analysis-only, candidate-first, evidence/provenance-backed, and owner-controlled. Owner-authored prose storage/editing is allowed, but AI-generated prose is permanently forbidden. The app must never generate, rewrite, continue, imitate, polish, improve, expand, outline, draft, revise, or produce story prose.

Queue presence is not approval. Confidence is not truth. Candidate persistence is not canon. Raw artifacts are support data, not canon. Apply-promotion must be explicit, audited, owner-confirmed, and separate from extraction, queue state, confidence, and candidate persistence.
