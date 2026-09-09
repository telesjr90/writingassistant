# Dramatica-flow analysis-only reference and app-owned rubric MVP boundary

Date: 2026-09-08

Status: Accepted owner decision

## Decision

The upstream provenance/reference repository is
`ydsgangge-ux/dramatica-flow`. The observed upstream commit is
`3a6fa55e84a8248e596527f0a5013748945a6cb8`.

The application intentionally uses only the permitted analysis-only concepts,
rules, and structural reasoning from that project through the app-owned
`dramatica_flow_informed_rubric`. That app-owned rubric is the approved
application and MVP boundary for the dramatica-flow-derived functionality the
owner wants.

The external `dramatica_flow` runtime itself is not MVP-required. No external
dramatica-flow runtime execution is required for `PHASE8-IMPL-025-T007`,
`PHASE8-IMPL-025-T008`, `PHASE8-IMPL-025-T012`, or `PHASE8-IMPL-027`.

The app-owned `dramatica_flow_informed_rubric` must never be represented as
evidence that the external runtime ran. Any future external-runtime integration
requires a separate explicit owner authorization and an analysis-only safety
review.

## Permanent prohibited behavior

This decision does not authorize prose generation, rewriting, continuation,
revision, polish, improvement, expansion, outline or chapter generation,
autonomous authorial output, automatic structural or canon selection, or
uncontrolled story, world, or truth-state mutation.

## Historical preservation

Historical `T020B` remains unchanged. This decision resolves only the later MVP
classification question; it does not retroactively rewrite or invalidate the
historical record.
