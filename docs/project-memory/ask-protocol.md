# Project Memory Ask Protocol

Project Memory Ask is a deterministic, read-only question-and-evidence contract.
It uses tracked repository sources and ordinary repository search/read access. It
is not a live chat service, retrieval system, roadmap mutation path, or source of
project truth.

## Request contract

Every request records these fields:

| Field | Requirement |
| --- | --- |
| `question` | The exact question to answer. |
| `repository_root` | The repository root that may be inspected. |
| `expected_branch` | Expected branch when supplied; otherwise explicitly `not_supplied`. |
| `expected_commit` | Full expected commit when supplied; otherwise explicitly `not_supplied`. |
| `task_or_feature_scope` | The bounded task, feature, or decision scope. |
| `requested_evidence_classes` | Requested authority or trust classes. |
| `freshness_requirement` | Required commit/branch freshness. |
| `historical_evidence_permitted` | Boolean; historical evidence is excluded unless true. |
| `maximum_scope` | Maximum paths, records, or bounded search area. |
| `protected_paths` | Paths that must not be accessed or changed. |
| `owner_decision_requirement` | Whether an accepted owner decision is required. |

Missing optional branch or commit expectations are not inferred. The response
must identify them as limitations and still bind every inspected source to the
actual repository state.

## Response contract

Every response contains these fields in this order:

1. `direct_answer`
2. `result`: exactly one of `ANSWERED`, `PARTIAL`, `INSUFFICIENT_EVIDENCE`,
   `CONFLICT`, or `OUT_OF_SCOPE`
3. `facts`
4. `inferences`
5. `authoritative_sources`
6. `supporting_generated_evidence`
7. `source_locators`
8. `authority_class_by_source`
9. `source_freshness_and_bound_commit`
10. `conflicts_and_uncertainty`
11. `owner_pending_decisions`
12. `limitations`
13. `recommended_next_deterministic_check`

Facts and inferences are separate lists. Every fact cites a repository-relative
path plus a line range or stable registry record ID. Every listed source states
its authority class, freshness, and bound commit (or explicitly states that the
tracked source is inspected at current HEAD). Generated evidence is listed only
as support and never under authoritative sources. Unknown information remains
unknown; confidence language does not convert an inference into a fact.

## Consultation and precedence

Use the authority hierarchy in
`docs/roadmap/decisions/PHASE8-IMPL-026-T001-project-memory-authority-lifecycle-provenance-foundation.md`:

1. accepted roadmap and decision records;
2. live code and schemas;
3. automated tests;
4. accepted manual validation within its recorded scope;
5. exact Git history;
6. normalized Project Memory registries;
7. generated context, indexes, retrieval results, and AI summaries.

The normalized registries and current rendered publication are navigation aids.
They do not override accepted roadmap records, decisions, code, schemas, tests,
accepted validation, or exact Git history. Generated evidence never becomes
authority. A lower tier that disagrees with a higher tier is stale, invalid, or
supporting evidence only. An unresolved same-tier conflict produces `CONFLICT`.

Responses explicitly distinguish implemented from planned; passing automated
tests from accepted live validation; runtime assets from fixtures or training
data; authoritative records from generated evidence; and current evidence from
historical or superseded evidence.

## Freshness and owner decisions

Before answering, record repository root, branch, full HEAD, clean worktree,
empty staging area, and the active task/frontier from
`docs/roadmap/roadmap_index.yaml`. Require current Project Memory status
`FRESH`, zero Plan Integrity blockers, and dependency eligibility. Resolve any
question about task execution through
`docs/project-memory/registries/execution-routing.json`; do not infer routing
from historical records or conversation context. A generated package is current only when
its branch and full bound commit match the required repository state and its
checksums and semantic validation pass. Stale or historical evidence may be
described only when the request permits it and every claim is labeled.

Every frontend/UI/UX consultation must also use
`.agents/skills/writing-assistant-ui-execution/SKILL.md` and the installed
Impeccable guidance in audit mode. That guidance remains generated evidence and
cannot override scope, routing, owner-only decisions, or accepted authority.

Owner-pending state is never resolved by inference. If an answer depends on an
unaccepted owner choice, list the exact decision and return `PARTIAL` or
`INSUFFICIENT_EVIDENCE` as appropriate.

## Fail-closed behavior

Return a refusal or non-answer result when:

- branch or commit binding is stale (`INSUFFICIENT_EVIDENCE`);
- the question requires an unapproved tool, installation, network call, model
  call, server, or external worktree (`OUT_OF_SCOPE` or
  `INSUFFICIENT_EVIDENCE`);
- sources conflict without an accepted resolution (`CONFLICT`);
- requested information is outside the repository or maximum scope
  (`OUT_OF_SCOPE`);
- answering would turn inference, generated output, a candidate, or planning
  notes into project truth (`INSUFFICIENT_EVIDENCE`);
- the request asks the Ask agent to modify authoritative state (`OUT_OF_SCOPE`);
- evidence is only `untrusted`, unknown, or quarantined
  (`INSUFFICIENT_EVIDENCE`);
- required evidence is missing, contradictory, owner-pending, or outside the
  protected-path boundary (`INSUFFICIENT_EVIDENCE`).
- committed execution routing is missing, conflicting, stale, inapplicable,
  owner-only, inactive, or dependency-ineligible (`INSUFFICIENT_EVIDENCE` or
  `OUT_OF_SCOPE`).

The response must state the limitation and recommend the smallest deterministic
read-only check that could resolve it. It must not automatically activate,
close, reorder, rewrite, or amend roadmap tasks; mutate Memory/Canon; promote a
candidate; apply promotion; generate story prose; or treat model output as
truth.
