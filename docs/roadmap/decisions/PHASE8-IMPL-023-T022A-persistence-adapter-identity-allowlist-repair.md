# PHASE8-IMPL-023-T022A - Persistence Adapter-Identity Allowlist Repair

## Result

`PHASE8-IMPL-023-T022A = complete/PASS`.

The persistence validator now accepts the two current app-owned OMI adapter
identities already recognized by the orchestrator:

- `subtxt_informed_rubric`
- `dramatica_flow_informed_rubric`

All pre-existing persistence identities remain in the explicit static
allowlist. Unknown adapter identities still fail closed before any candidate
write.

## Root Cause and Repair

The orchestrator identity allowlist had both app-owned rubric identities, but
`backend/project_manager.py` had a stale `OMI_TOOL_ASSISTED_ADAPTER_IDENTITIES`
set. The first T022 persistence attempt therefore rejected the fused findings
with `Unknown OMI tool-assisted source_adapter: subtxt_informed_rubric`.

T022A adds exactly those two identities to the project-manager allowlist. It
does not derive identities dynamically, import the orchestrator, accept
arbitrary strings, alter persistence keys, change serialization, or change
orchestrator behavior.

## Contract Coverage

The focused persistence tests use only `tmp_path` projects with a
monkeypatched `PROJECTS_DIR`. They prove that:

- Both identities are members of the persistence allowlist.
- Each identity persists through the existing candidate-only path.
- Source adapter, exact provenance adapter/tool source, evidence,
  support-only metadata, fingerprints, normalized finding ID, pending and
  unapproved owner decision, `candidate_review_pending`, and promotion
  ineligibility survive serialization.
- A mixed two-finding call creates exactly two candidates.
- Replaying the mixed findings returns `already_persisted`, no new IDs, and
  both original IDs as reused IDs.
- An arbitrary unknown identity returns `invalid_finding_failed_closed` and
  writes no candidate.

The exact provenance checks remain unchanged: `provenance.adapter` and
`provenance.tool_source` must equal `source_adapter`.

## Validation

- `tests/test_omi_tool_assisted_persistence_contract.py`: 10 passed.
- No live adapter, runtime tool, model, network, npm, Node, or fixture
  adapter execution was used.
- No real T022 findings were persisted.

## Safety and Scope

Candidate persistence remains candidate-first, evidence/provenance-backed,
support-only, owner-controlled review material. Queue presence is not
approval. Candidate persistence is not canon. There is no Memory/Canon
mutation, promotion record, apply-promotion, automatic promotion, or prose.

The preserved T022 source idea, pre-existing candidates, OMI index, blocked
T022 evidence, and ignored bytecode remain untouched. No dependency,
orchestrator, or project behavior changed.

## Frontier

```text
PHASE8-IMPL-023-T022A = complete/PASS
PHASE8-IMPL-023-T022  = blocked/in_progress
PHASE8-IMPL-023       = published/active
full MVP completion   = blocked
```

Next:

```text
PHASE8-IMPL-023-T022B
Resume candidate-only persistence using preserved real T022 findings
planned
```

T022B must reuse source idea
`idea_2ef4930a04924577a2983e45408bba39`, consume the exact 113 preserved
findings from the blocked T022 result, make no live adapter call, persist all
findings once, replay them once to prove ID reuse, preserve the original
blocked evidence, and close T022 only after persistence, replay, mutation,
regression, and roadmap validation pass. T023 remains planned after T022.

No staging, commit, or push occurred.
