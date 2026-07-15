# PHASE8-IMPL-026-T003A — Deterministic Repository Scanners and Snapshot-Builder Implementation

## Decision

```
PHASE8-IMPL-026-T003 (Deterministic scanners and convergence) is decomposed into
T003A (scanner implementation and testing) and T003B (clean-HEAD snapshot,
convergence validation, and T003 closeout). T003A implements the standard-library-only
deterministic scanner suite and snapshot builder but does not create a final
publication snapshot from the dirty implementation worktree.

Standard-library-only implementation. No external dependencies, no context tools,
no AI models, no MCP servers, no package installs.
```

## Result

Complete/PASS.

## T003 Decomposition

### T003A — Deterministic repository scanners and snapshot-builder implementation

T003A implements and tests the scanner suite, snapshot builder, convergence
vocabulary, and finding codes. It validates all output contracts against
temporary Git repositories. It does not create a final publication snapshot
because the worktree contains uncommitted T003A changes.

### T003B — Clean-HEAD snapshot, convergence validation, and T003 closeout

T003B begins only after T003A is committed. It runs the scanner against a clean
committed HEAD, creates the first generated evidence under
`.codex-context/project-memory/`, validates the evidence package and repository
convergence, and closes T003.

At the end of T003A:
- T003 is `in_progress`
- T003A is `complete/PASS`
- T003B is the next Project Memory task
- No final snapshot exists under `.codex-context/project-memory/`

## Scanner Modules

### `scripts/project_memory/repository_state.py`

Deterministic repository-state scanner. Collects:
- Resolved repository root
- Branch, full 40-character HEAD, HEAD subject
- Staged state, clean/dirty state
- Modified paths, untracked paths (`--untracked-files=all`)
- Tracked-file inventory (`git ls-files`)
- Registered worktrees (`git worktree list --porcelain`)
- Current timestamp (caller-supplied)
- Scanner name and version

Uses only read-only Git commands. Never modifies the index, files, or other
worktrees. Never follows symlinks outside the repository. Never accesses the
network.

Also provides:
- `collect_source_inventory()` — Hashes tracked registry sources, roadmap
  files, and scanner implementation files using SHA-256
- `parse_roadmap_state()` — Parses `roadmap_index.yaml` and extracts frontier,
  task status, and PHASE8-IMPL-026 task information
- `validate_source_locators()` — Validates registry source locators against
  the filesystem: path safety, existence, line ranges, protected paths
- `hash_file()` — SHA-256 hash of a repository-relative regular file

### `scripts/project_memory/convergence.py`

Deterministic convergence checker. Produces structured findings with:
- Stable finding ID
- Finding code from a fixed vocabulary
- Severity (info, warning, error, critical)
- Title, explanation, affected record IDs, source locators
- Authority context, deterministic evidence
- Whether it blocks current snapshot publication
- Whether owner review is required
- Suggested next action (as a proposal, not an automatic edit)

Finding codes (20):
- `registry_validation_failed`, `source_missing`, `source_not_tracked`
- `source_excluded`, `source_locator_invalid`, `source_line_range_invalid`
- `task_missing_from_roadmap`, `task_status_mismatch`
- `decision_missing`, `decision_status_mismatch`
- `frontier_mismatch`, `planned_parent_activated_unexpectedly`
- `accepted_evidence_missing`, `generated_evidence_unavailable`
- `source_hash_conflict`, `supersession_conflict`, `dependency_conflict`
- `working_tree_dirty`, `staging_not_empty`, `snapshot_not_commit_bound`

Convergence results:
- `PASS` — No findings requiring owner attention or repair
- `PASS_WITH_FINDINGS` — Warnings or non-blocking errors detected
- `BLOCKED` — Critical errors, worktree dirty, registries invalid, frontier
  silently changed, PHASE8-IMPL-025 unexpectedly activated

Findings are sorted deterministically by severity rank, code, affected record
ID, and stable finding ID.

### `scripts/project_memory/build_snapshot.py`

Snapshot builder CLI and library. Builds a complete generated snapshot package:
```text
.codex-context/project-memory/
  <TASK_ID>/
    <RUN_ID>/
      run-metadata.json
      repository-state.json
      roadmap-state.json
      registry-validation.json
      source-inventory.json
      source-hashes.json
      convergence-findings.json
      snapshot.json
      summary.md
      FILE-INVENTORY.txt
      SHA256SUMS
```

CLI:
```bash
python3 scripts/project_memory/build_snapshot.py \
  --repo-root . \
  --output-root .codex-context/project-memory \
  --task-id PHASE8-IMPL-026-T003B
```

Options: `--repo-root`, `--output-root`, `--task-id`, `--run-id`,
`--generated-at`, `--require-clean`, `--nonpublication`, `--json`,
`--registries-dir`.

## Generated Snapshot Package Contract

- `snapshot.json` — Conforms to T002 GeneratedSnapshotManifest; authority_class
  fixed to `generated_evidence`
- `run-metadata.json` — Command, repo root, branch, HEAD, subject, task ID,
  run ID, generated time, Python version, platform, scanner versions,
  clean/staged state, output directory, exclusions, no-network/no-model/
  no-external-tool declarations
- `repository-state.json` — Full repository state
- `roadmap-state.json` — Parsed roadmap_index.yaml state
- `registry-validation.json` — Registry validation results
- `source-inventory.json` — Source inventory and hashes
- `source-hashes.json` — Source file SHA-256 hashes
- `convergence-findings.json` — Structured convergence findings
- `summary.md` — Human-readable generated evidence summary
- `FILE-INVENTORY.txt` — Every generated file in stable lexical order
- `SHA256SUMS` — SHA-256 of every generated package file except SHA256SUMS itself

## Clean-HEAD Publication Rule

Publication snapshots require:
- Clean worktree (no modified files)
- Empty staging area
- `--require-clean` (default true)
- No `--nonpublication` flag

A dirty-worktree testing mode (`--nonpublication`) creates output marked:
- `publication_eligible: false`
- `freshness_state: nonpublication` (or `dirty`)
- `authority_class: generated_evidence`
- `snapshot_not_commit_bound` finding

There is no casual `--allow-dirty` publication path.

## Atomic Output and Safety

The builder:
1. Resolves and validates the output root
2. Creates output in a temporary sibling directory
3. Writes and validates every JSON file
4. Calculates hashes
5. Atomically renames the completed directory into place
6. Refuses to overwrite an existing run directory
7. Removes incomplete temporary output after failure
8. Never modifies tracked registry or roadmap sources
9. Never writes outside the selected output root
10. Rejects symlinked output paths that escape the repository
11. Refuses an output root inside tracked authority directories
   (`docs/project-memory/`, `docs/roadmap/`, `scripts/`, `tests/`,
   `backend/`, `frontend/`, `.agents/`, `.opencode/`, `.github/`,
   `.claude/`, `.cursor/`)

## Source Hashing and Exclusion Rules

Hashed: tracked registry sources, authoritative roadmap files, scanner
implementation files, repository-relative locator-referenced files.

Not hashed: `.git/`, virtual environments, `node_modules/`, caches,
generated build output, environment files, secrets, unrelated binaries,
`projects/*/omi/**`.

Protected paths are not read; a finding is produced instead.

## Determinism

Given the same commit, same registry files, same explicit run ID, same
explicit generated time, and same platform-normalized inputs, the semantic
JSON outputs and file ordering are identical.

Absolute local paths do not appear in source records or snapshot evidence
except where explicitly identified as nonportable runtime metadata.

## Validator Change

A minimal refactor to `validate_registries.py` allows the `validate()`
function to use the `registries_dir` parameter for the manifest path as
well as the registry files. The existing CLI remains compatible, all
existing T002 tests remain green, no validation rule is weakened, and no
dependency is introduced.

## README Update

Updated `docs/project-memory/README.md` to document:
- Deterministic scanner purpose
- T003A/T003B split
- Scanner modules
- Convergence results
- Publication requirements
- Generated output structure
- Clean-HEAD requirement
- Command that T003B will run
- Why generated snapshots remain non-authoritative
- Known limitations
- Next task T003B

Does not claim that the first publication snapshot exists yet.

## Test Results

68 tests pass:
- `tests/project_memory/test_validate_registries.py` — 20 passed (T002)
- `tests/project_memory/test_repository_state.py` — 20 passed
- `tests/project_memory/test_convergence.py` — 11 passed
- `tests/project_memory/test_build_snapshot.py` — 17 passed

All tests use temporary Git repositories. No real repository files are mutated.

## Application Frontier (unchanged)

PHASE8-IMPL-024-T003A — Context-availability/readiness contract for Bible,
storyform, and storyform-context.

## PHASE8-IMPL-025 Status (unchanged)

Published/planned and inactive.

## Next Task

PHASE8-IMPL-026-T003B — Clean-HEAD snapshot, convergence validation, and
T003 closeout.

## No Live Publication Snapshot

No final snapshot was created under `.codex-context/project-memory/`.
T003B will create the first commit-bound generated snapshot.

## No External Tools

No external context tool, AI model, package, MCP server, renderer, index,
or agent was installed or used.

## Validation

```bash
python3 -m py_compile \
  scripts/project_memory/__init__.py \
  scripts/project_memory/validate_registries.py \
  scripts/project_memory/repository_state.py \
  scripts/project_memory/convergence.py \
  scripts/project_memory/build_snapshot.py

python3 scripts/project_memory/validate_registries.py
python3 scripts/project_memory/validate_registries.py --json

python3 -m pytest \
  tests/project_memory/test_validate_registries.py \
  tests/project_memory/test_repository_state.py \
  tests/project_memory/test_convergence.py \
  tests/project_memory/test_build_snapshot.py \
  -q -p no:cacheprovider

python3 -m json.tool docs/project-memory/schemas/project-memory.schema.json >/dev/null

find docs/project-memory/registries -maxdepth 1 -type f -name '*.json' -print0 | \
  while IFS= read -r -d '' file; do python3 -m json.tool "$file" >/dev/null; done

python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-026.enrichment.json >/dev/null
python3 -m json.tool docs/roadmap/roadmap_index.yaml >/dev/null
python3 scripts/validate_roadmap.py
python3 scripts/check_enrichment.py
```
