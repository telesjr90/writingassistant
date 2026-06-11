# PHASE7-IMPL-002 — Project Library Scan Backend Report

## 1. Result

**PASS with warning**

All validation commands completed successfully. No defects required fixes.

Warnings observed (acceptable, tests pass):

- `StarletteDeprecationWarning`: `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
- `PydanticDeprecatedSince20`: class-based `Config` on `ProjectCreate` is deprecated (inherited from PHASE7-IMPL-001 compatibility behavior).

No dependency changes were made.

## 2. Date and environment

| Field | Value |
|---|---|
| Date/time | 2026-06-11 00:05:01 UTC |
| Repo path | `/home/tjrpirateking/projects/WritingAssistantApplication` |
| Branch | `main` (tracking `origin/main`) |
| Python command | `.venv-unsloth-clean/bin/python` |

## 3. Files inspected

- `backend/project_manager.py` — scan-first project library helpers (`list_projects`, `load_project_metadata`, private inspection/sorting helpers)
- `backend/main.py` — `GET /api/projects` route and error handling
- `tests/test_project_library.py` — 23 focused tests for helpers and route
- `tests/test_project_creation.py` — regression check via full suite (PHASE7-IMPL-001)
- `AGENTS.md` — safety and task boundaries
- `.cursor/rules/project-boundaries.mdc` — candidate/canon and no-prose boundaries
- `.cursor/rules/workspace-task-safety.mdc` — WORKSPACE preflight requirements

## 4. Files created/modified

| File | Action |
|---|---|
| `backend/project_manager.py` | Modified (+348 lines: project library scan helpers) |
| `backend/main.py` | Modified (+24 lines: `GET /api/projects`) |
| `tests/test_project_library.py` | Created (23 focused tests) |
| `training/reports/phase7_impl_002_project_library_backend_report.md` | Created (this report) |

## 5. Implementation summary

### Scan-first project library helpers

`backend/project_manager.py` adds a scan-first project library layer (PHASE7-IMPL-002 micro-task 1) that never calls Ollama, `analysis_engine`, or Story Check. It does not read or mutate OMI records, memory/canon files, scene prose, training data, or model artifacts. It does not create or update `projects/index.json`.

**Public helpers:**

- `load_project_metadata(project_id, projects_dir=PROJECTS_DIR) -> dict[str, Any]`
- `list_projects(projects_dir=PROJECTS_DIR) -> list[dict[str, Any]]`

**Private helpers:**

- `_is_path_contained_in` — path containment check via `resolve().relative_to()`
- `_project_path_for_id` — safe project path resolution with traversal guard
- `_safe_folder_label` — safe label for unsafe folder names
- `_project_library_warning_record` — uniform warning/invalid record builder
- `_read_project_json` — read and validate `project.json` as JSON object
- `_inspect_project_folder` — per-folder inspection producing valid/warning/invalid records
- `_apply_duplicate_project_id_warnings` — duplicate `project_id` detection across records
- `_strip_internal_library_fields` — removes `_`-prefixed internal fields before API return
- `_sort_project_library_records` — deterministic sort (valid first, then invalid/warning)

### Metadata loading

`load_project_metadata` validates `project_id`, resolves the project path safely, and returns a stripped library record. Missing folders, non-directories, unsafe IDs, and corrupt metadata return warning/invalid records without raising to callers.

### Valid project records

Valid projects return lightweight records with:

- `project_id`, `title`, `created_at`, `updated_at`, `schema_version`, `creation_method`
- `relative_path` (folder name only)
- `status`: `"valid"` (or `"warning"` if symlink or minor metadata issues)
- `warnings`: list (empty for clean projects)

### Invalid/corrupt warning records

Invalid or corrupt projects return records with `status` of `"invalid"` or `"warning"` and descriptive `warnings` entries. Cases covered:

- Unsafe folder names
- Missing `project.json`
- Invalid JSON / non-object JSON
- `project_id` mismatch between folder and `project.json`
- Unsafe or non-string `project_id` in JSON
- Symlink folders (warning)
- Path escape outside `projects_dir` (invalid)
- Unreadable directory entries or JSON files

### Deterministic sorting

`_sort_project_library_records` sorts valid records by `updated_at` descending, then `title` ascending, then `project_id` ascending. Invalid/warning records follow, sorted by `project_id`.

### Duplicate warning behavior

`_apply_duplicate_project_id_warnings` scans `_metadata_project_id` across records. When two or more records share the same metadata `project_id`, all matching records receive an additional `"duplicate project_id: '...'"` warning and `status` is set to `"invalid"`.

### Path containment / symlink escape handling

- `_is_path_contained_in` and `_project_path_for_id` enforce that resolved paths stay inside the resolved `projects_dir`.
- Symlinked folders that resolve outside `projects_dir` produce invalid records with `"project folder resolves outside projects directory"`.
- Symlinked folders inside `projects_dir` produce warning records with `"project folder is a symlink"`.

### GET /api/projects route

`backend/main.py` registers `GET /api/projects` **before** `/api/projects/{project_name}/...` sub-routes to avoid route shadowing.

### Response shape

```json
{"projects": [...], "count": N}
```

`count` equals `len(projects)`.

### Safe error handling

- `ValueError` → HTTP 400 with sanitized detail via `_safe_list_projects_error_detail` (no absolute path leakage)
- `FileNotFoundError` → HTTP 200 with `{"projects": [], "count": 0}`
- Other exceptions → HTTP 500 with `"Failed to list projects"`

`POST /api/projects` is unchanged from PHASE7-IMPL-001.

## 6. Project library behavior

| Behavior | Status |
|---|---|
| `list_projects` scans immediate child directories under `projects_dir` | Yes |
| Does not use `projects/index.json` | Yes |
| Does not create `projects/index.json` | Yes |
| Does not mutate project files | Yes |
| Does not create missing metadata | Yes |
| Valid projects return lightweight records | Yes |
| Invalid/corrupt projects return warning/invalid records without crashing | Yes |
| No absolute path leakage intended | Yes — `relative_path` is folder name only; tests assert no `/home`, `\`, or drive-letter paths |

Non-directory entries under `projects_dir` are skipped (not listed). Missing or non-directory `projects_dir` returns an empty list.

## 7. API route summary

| Item | Detail |
|---|---|
| Endpoint | `GET /api/projects` |
| Handler | `get_projects()` |
| Response | `{"projects": [...], "count": N}` |
| `count` behavior | `count = len(projects)`; includes valid, warning, and invalid records |
| 400 behavior | `ValueError` from `list_projects` → 400 with safe detail; path details redacted |
| `FileNotFoundError` behavior | Returns 200 with `{"projects": [], "count": 0}` |
| 500 behavior | Unexpected exceptions → 500 with `"Failed to list projects"` |
| Route registration order | `GET /api/projects` registered at line 90, before `GET /api/projects/{project_name}/scenes` at line 122 |

## 8. Tests

**File:** `tests/test_project_library.py`

**Count:** 23 focused tests (all passed)

### Helper coverage

| Test class | Coverage |
|---|---|
| `TestListProjectsMissingDir` | Missing `projects_dir` returns `[]` |
| `TestListProjectsValidProject` | Valid project record shape and no path leak |
| `TestListProjectsMissingProjectJson` | Missing `project.json` → invalid |
| `TestListProjectsInvalidJson` | Malformed JSON → invalid |
| `TestListProjectsNonObjectJson` | Array/string JSON → invalid/warning |
| `TestListProjectsMismatchedProjectId` | Folder/JSON ID mismatch → invalid |
| `TestListProjectsUnsafeFolderNames` | Reserved/unsafe folder names → invalid |
| `TestListProjectsSymlink` | Symlink escape outside dir → invalid/warning |
| `TestListProjectsSorting` | Valid sorted by `updated_at` desc; invalid after valid |
| `TestListProjectsDuplicates` | Duplicate metadata `project_id` warnings |
| `TestLoadProjectMetadata` | Valid, unsafe ID, missing, corrupt metadata |

### Route coverage

| Test class | Coverage |
|---|---|
| `TestGetProjectsRoute` | 200 success shape, `FileNotFoundError` empty list, 400 safe detail, 500 generic, route not shadowed |

### Filesystem isolation

All filesystem tests use `tmp_path` pytest fixture. No persistent fixtures under repo `projects/`.

### Symlink escape behavior

`TestListProjectsSymlink.test_symlink_outside_projects_dir_fails_closed` creates a symlink pointing outside `tmp_path` and asserts invalid/warning record without path leak. Skips gracefully if symlinks unsupported.

## 9. Validation

### `py_compile backend/main.py backend/project_manager.py`

```
Exit code: 0 (no errors)
```

### `pytest tests/test_project_library.py -q`

```
23 passed, 3 warnings in 0.59s
```

### `pytest tests -q`

```
233 passed, 3 warnings in 1.40s
```

### `git diff --check`

```
Exit code: 0 (no whitespace errors)
```

### `git diff --stat`

```
 backend/main.py            |  24 ++++
 backend/project_manager.py | 348 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 372 insertions(+)
```

### `git status --short --branch`

```
## main...origin/main
 M backend/main.py
 M backend/project_manager.py
?? tests/test_project_library.py
```

### Warning summary

| Warning | Source | Acceptable |
|---|---|---|
| `StarletteDeprecationWarning` (httpx/testclient) | `fastapi/testclient.py` | Yes |
| `PydanticDeprecatedSince20` (class-based Config) | `backend/main.py:16` `ProjectCreate` | Yes (PHASE7-IMPL-001 inherited) |

No dependency changes made.

## 10. Deferred decisions / next work

- Frontend project selector/library UI remains a future task
- Frontend API wiring remains a future task
- `GET /api/projects/{project_id}` single-project route remains a future task
- Cheap counts (chapters/scenes/notes/materials) remain a future task
- `metadata_status` / `warning_badges` shaping remains a future task
- Project archive/delete remains a future task
- OMI-guided setup remains a future task
- Memory/canon runtime files remain deferred
- Apply-promotion remains unimplemented
- Model/Ollama analysis remains untouched
- Dramatica-specific implementation remains deferred

## 11. Safety confirmations

- No frontend runtime code changed.
- No model/Ollama calls were added.
- No Story Check behavior was changed.
- No OMI records are created by project library scanning.
- No memory/canon files are created by project library scanning.
- No apply-promotion behavior was added.
- No extraction behavior was added.
- No Dramatica-specific logic was added.
- No dataset files were changed.
- No JSONL/training records were created.
- `dataset_manifest.json` was not changed.
- No package/dependency files were changed.
- No training or fine-tuning ran.
- No persistent runtime project fixtures were created under repo `projects/`.
- No staging, commit, or push was performed.
