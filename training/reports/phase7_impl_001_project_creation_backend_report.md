# PHASE7-IMPL-001 — Project Creation and Safe Project Metadata Backend Report

## 1. Result

**PASS with warning**

All validation commands completed successfully. Focused project-creation tests and the full test suite passed. The only warnings observed are upstream dependency deprecations (`StarletteDeprecationWarning` from FastAPI/Starlette TestClient and `PydanticDeprecatedSince20` from the v1-compatible `class Config` on `ProjectCreate`). No dependency changes were made.

## 2. Date and environment

| Item | Value |
|------|-------|
| Date/time | 2026-06-10 22:30:13 UTC |
| Repo path | `/home/tjrpirateking/projects/WritingAssistantApplication` |
| Branch | `main` |
| Python command | `.venv-unsloth-clean/bin/python` |
| Pydantic version | 2.13.4 (from prior probe) |

## 3. Files inspected

- `backend/project_manager.py` — blank-project creation helpers, ID derivation/validation, collision resolution, safe path guard, `project.json` write
- `backend/main.py` — `ProjectCreate` model, `POST /api/projects` route, safe error detail helper
- `tests/test_project_creation.py` — 34 focused tests for helpers, creation behavior, route responses, and safety non-creation checks
- `docs/roadmap/project_creation_flow_spec.md` (referenced in code comments)
- `docs/roadmap/project_file_model.md` (referenced in code comments)

## 4. Files created/modified

- `backend/project_manager.py` (modified)
- `backend/main.py` (modified)
- `tests/test_project_creation.py` (created)
- `training/reports/phase7_impl_001_project_creation_backend_report.md` (created)

## 5. Implementation summary

### Title validation

- `_validate_project_title()` requires a non-blank string after strip, max 160 characters (`MAX_PROJECT_TITLE_LENGTH`).
- Blank or whitespace-only titles raise `ValueError("Project title must not be blank")`.
- Non-string titles raise `TypeError`.

### Project ID derivation

- `derive_project_id(title)` validates the title, NFKD-normalizes and ASCII-folds Unicode, lowercases, replaces unsafe character runs with hyphens, collapses repeated hyphens, strips leading/trailing `-_. `, truncates to 64 chars, and rejects titles that normalize to an empty ID.

### Project ID validation

- `validate_project_id(project_id)` rejects empty IDs, absolute paths, `.` / `..`, path separators, Windows drive-letter paths, reserved IDs, and IDs not matching `^[a-z0-9][a-z0-9_-]{0,63}$`.

### Collision handling

- `resolve_project_id_with_collision(base_project_id, projects_dir)` returns the base ID when unused; otherwise appends `-2`, `-3`, … up to `MAX_PROJECT_ID_COLLISION_ATTEMPTS` (1000). Existing folders are never overwritten.

### Safe path guard

- `create_project()` resolves `projects_dir` and the target project path, then requires `project_path.relative_to(resolved_root)` to succeed before creating directories.

### project.json creation

- Writes metadata with `project_id`, `title`, `created_at`, `updated_at`, `schema_version` (`0.1.0`), `creation_method` (`blank`), and `owner_approved_truth_policy` via atomic temp-file replace (`overwrite=False`).

### POST /api/projects route

- New route `POST /api/projects` calls `project_manager.create_project(title=payload.title)` and returns the created metadata dict on success (HTTP 200).

### Title-only request body

- `ProjectCreate` accepts only `title: str`. Extra fields (including client-supplied `project_id`) are forbidden.

### Safe error handling

- `ValueError` → HTTP 400 with message from `_safe_create_project_error_detail()` (path-related messages sanitized to `"Unable to create project with the given title"`).
- `FileExistsError` → HTTP 409 `"Project already exists"`.
- Other exceptions → HTTP 500 `"Failed to create project"` (no internal details leaked).

## 6. Project ID strategy

### Normalization

- Title is stripped; Unicode NFKD + ASCII fold; lowercase; punctuation/space runs become single hyphens; repeated hyphens collapsed; edge hyphens/underscores/dots/spaces stripped.

### Slug strategy

- Derived slug must match lowercase alphanumeric start with optional hyphens/underscores, max 64 characters.

### Rejected unsafe IDs

- Absolute paths, `.`, `..`, `/`, `\`, Windows drive paths (`c:…`), uppercase, leading hyphen, spaces, and pattern violations.

### Reserved IDs

- Includes `.`, `..`, `index`, `new`, `create`, `api`, `projects`, `project`, `memory`, `omi`, `scenes`, `chapters`, `notes`, `materials`, Windows device names (`con`, `prn`, `aux`, `nul`, `com1`–`com9`, `lpt1`–`lpt9`).

### Collision suffix behavior

- When `projects/{base_id}/` exists, tries `base_id-2`, `base_id-3`, … without modifying existing directories.

## 7. Project files created by blank project creation

Blank project creation creates:

- `projects/{project_id}/`
- `project.json`
- Configured workspace core folders (`WORKSPACE_CORE_FOLDERS`):
  - `chapters/`
  - `scenes/`
  - `scene_metadata/`
  - `notes/`
  - `note_metadata/`
  - `materials/`
  - `material_metadata/`

## 8. Files intentionally not created

Blank project creation intentionally does **not** create:

- `bible.json`
- `storyform.json`
- OMI records
- memory/canon files
- scene prose files
- generated summaries
- generated ideas
- generated analysis
- candidates
- model artifacts
- training/dataset artifacts

## 9. API route summary

| Item | Detail |
|------|--------|
| Endpoint | `POST /api/projects` |
| Request body | `{"title": "..."}` |
| Response | Created metadata dict (`project_id`, `title`, timestamps, `schema_version`, `creation_method`, `owner_approved_truth_policy`) |
| 400 behavior | Validation/normalization failures; safe generic message for path-safety errors |
| 409 behavior | `"Project already exists"` when target directory already exists |
| 500 behavior | `"Failed to create project"` for unexpected failures |
| Client `project_id` | **Not accepted** — extra fields rejected (`422` via Pydantic `extra="forbid"`) |
| `ProjectCreate` config | Uses v1-compatible `class Config: extra = "forbid"` (not `ConfigDict`) for full-suite compatibility with fake-module pollution from other route tests |

## 10. Tests

### File

- `tests/test_project_creation.py`

### Coverage summary

- **34 focused tests** total
- **Helper function coverage:** `derive_project_id`, `validate_project_id`, `resolve_project_id_with_collision`, `create_project`
- **Route behavior coverage:** success (200), `ValueError` (400), path-safety sanitization (400), `FileExistsError` (409), unexpected error (500), rejected extra `project_id` field (422), `ProjectCreate` extra-field validation
- **Safety non-creation checks:** no `bible.json`, `storyform.json`, `omi/`, `memory/`, or scene `.md` files after creation

### Micro-Task 3B full-suite compatibility fix

- Removed/avoided Pydantic `ConfigDict` dependency on `ProjectCreate`
- Cleared fake `fastapi` / `pydantic` modules from `sys.modules` before importing real FastAPI/Pydantic (pollution from `test_context_routes.py` during collection)
- Reloaded `backend.project_manager` and `backend.main` before route tests

## 11. Validation

### Commands and results

```text
pwd
/home/tjrpirateking/projects/WritingAssistantApplication

git rev-parse --show-toplevel
/home/tjrpirateking/projects/WritingAssistantApplication

git branch --show-current
main

.venv-unsloth-clean/bin/python -m py_compile backend/main.py backend/project_manager.py
py_compile: OK

.venv-unsloth-clean/bin/python -m pytest tests/test_project_creation.py -q
34 passed, 3 warnings in 0.77s

.venv-unsloth-clean/bin/python -m pytest tests -q
210 passed, 2 warnings in 1.39s

git diff --check
(no whitespace errors)

git diff --stat
 backend/main.py            |  29 ++++++
 backend/project_manager.py | 218 +++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 247 insertions(+)

git status --short --branch
## main...origin/main
 M backend/main.py
 M backend/project_manager.py
?? tests/test_project_creation.py
```

### Warnings (expected only)

- `StarletteDeprecationWarning`: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
- `PydanticDeprecatedSince20`: Support for class-based `config` is deprecated on `ProjectCreate` in `backend/main.py`.

### Dependency changes

- None

## 12. Deferred decisions / next work

- Project selector/library route and UI remain future tasks
- Frontend project creation wiring remains a future task
- `GET /api/projects` list route remains a future task unless planned separately
- OMI-guided setup remains a future task
- Memory/canon runtime files remain deferred
- Apply-promotion remains unimplemented
- Model/Ollama analysis remains untouched
- Dramatica-specific implementation remains deferred
- Future cleanup may revisit Pydantic config style once test fake-module pollution is removed

## 13. Safety confirmations

- No frontend runtime code changed.
- No model/Ollama calls were added.
- No Story Check behavior was changed.
- No OMI records are created by project creation.
- No memory/canon files are created by project creation.
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
