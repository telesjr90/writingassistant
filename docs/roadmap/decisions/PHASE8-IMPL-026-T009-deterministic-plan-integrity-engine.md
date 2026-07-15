# PHASE8-IMPL-026-T009 — Deterministic Plan Integrity Engine

## Result

T009: **complete/PASS**.

T009 implements a Python-standard-library-only deterministic engine that
compares accepted tracked plan records with bounded tracked implementation
evidence. Its output is always `generated_evidence`; it cannot mutate roadmap,
registries, tasks, Memory/Canon, candidates, promotions, or story prose.

## Q151 classification model

- `matching`: current accepted plan and current implementation evidence agree,
  required evidence exists, and no unresolved higher-authority contradiction
  exists.
- `diverging`: current accepted plan and implementation evidence make
  incompatible claims about the same bounded subject.
- `superseded`: a historical claim is explicitly replaced by a later accepted
  record with traceable reciprocal supersession.
- `conflicting`: current equal or unresolved authority sources disagree and no
  accepted resolution exists.
- `insufficient_evidence`: required evidence is absent, malformed, stale,
  unavailable, unbound, or below the required trust level.

Confidence is a deterministic description of exact input completeness. It
never converts `insufficient_evidence` into `matching` and never implies truth,
approval, promotion, or owner acceptance.

## Readiness model

- `READY`: no unresolved blocking, error, critical, required conflict, or
  required insufficient-evidence finding.
- `READY_WITH_ADVISORIES`: only nonblocking information or warnings remain.
- `BLOCKED`: at least one deterministic blocking condition exists.

Blocking conditions cover dirty or staged input; branch/commit mismatch;
registry validation failure; malformed authoritative input; application
frontier drift; PHASE8-IMPL-025 activation; dependency cycles or missing
prerequisites; completed tasks without required evidence; authoritative
conflicts; required insufficient evidence; invalid locators or hashes;
generated evidence claiming authority; and malformed output packages.

## Delivered implementation

- `scripts/project_memory/plan_integrity.py` provides `load_plan_inputs`,
  `load_implementation_inputs`, `build_comparisons`,
  `run_plan_integrity_checks`, `derive_readiness`, deterministic Q151
  classification, confidence-basis, ordering, dependency-cycle, exact overlap,
  evidence, and product-boundary checks.
- `scripts/project_memory/build_plan_integrity_report.py` provides
  `build_plan_integrity_package` and `validate_plan_integrity_package`, plus a
  direct CLI that works from the repository root or another current working
  directory when `--repo-root` is supplied.
- The single Project Memory schema bundle adds only Plan Integrity comparison,
  finding, evidence-locator, confidence-basis, readiness, report, and generated
  package metadata definitions.
- The exact eleven-file package is atomic, refuses overwrite, cleans partial
  output after failure, validates registries first, requires clean HEAD and
  empty staging, binds every comparison to branch/full commit, and validates
  exact inventory, JSON, checksums, authority, and semantic bindings before
  publication.

## Rule groups

The engine implements bounded checks for task-state convergence; decision and
supersession integrity; dependency and delivery integrity; evidence and
traceability integrity; exact duplicate and exact overlap integrity; product
boundary integrity; and consolidated readiness. Duplicate/overlap checks use
exact IDs, ownership paths, titles, and relationship sets only. Similarity
alone never supports a semantic-duplication claim.

## Preserved state and boundaries

- T006/T007 remain owner-deferred, contingent, planned, inactive, and
  unimplemented.
- T008 remains complete/PASS.
- T010 is next, planned/inactive; no reviewer agent is implemented or run.
- T011 remains planned/inactive.
- The application frontier remains `PHASE8-IMPL-024-T003A`.
- PHASE8-IMPL-025 remains published/planned and inactive.
- Q151 is resolved by this decision. Q152–Q154 remain open.
- No retrieval tool, external context tool, network call, model call, package
  installation, external worktree access, roadmap mutation, registry mutation,
  Memory/Canon mutation, promotion, apply-promotion, or generated story prose
  is part of the engine or its tests.
