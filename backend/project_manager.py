from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = REPO_ROOT / "projects"


# Project creation primitives (PHASE7-IMPL-001) follow
# `docs/roadmap/project_creation_flow_spec.md` and the
# `docs/roadmap/project_file_model.md` `project.json` shape. They never
# create story prose, generated summaries, candidates, OMI records,
# memory/canon files, training data, or model artifacts.
PROJECT_SCHEMA_VERSION = "0.1.0"
SCENE_METADATA_VERSION = 1
CHAPTER_METADATA_VERSION = 1
NOTE_METADATA_VERSION = 1
MATERIAL_METADATA_VERSION = 1

MAX_PROJECT_TITLE_LENGTH = 160
MAX_PROJECT_ID_LENGTH = 64
MAX_PROJECT_ID_COLLISION_ATTEMPTS = 1000
MAX_DOCUMENT_ID_LENGTH = 64

PROJECT_CREATION_METHOD_BLANK = "blank"

_PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_PROJECT_ID_INVALID_CHAR_RUN = re.compile(r"[^a-z0-9]+")
_PROJECT_ID_REPEAT_HYPHEN = re.compile(r"-{2,}")
_DOCUMENT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]{0,63}$")

# Reserved names follow `project_creation_flow_spec.md` §6 plus the
# Windows reserved device names that would be unsafe on case-insensitive
# host filesystems.
RESERVED_PROJECT_IDS: frozenset[str] = frozenset(
    {
        ".",
        "..",
        "index",
        "new",
        "create",
        "api",
        "projects",
        "project",
        "memory",
        "omi",
        "scenes",
        "chapters",
        "notes",
        "materials",
        "con",
        "prn",
        "aux",
        "nul",
    }
    | {f"com{i}" for i in range(1, 10)}
    | {f"lpt{i}" for i in range(1, 10)}
)

RESERVED_DOCUMENT_IDS: frozenset[str] = frozenset(
    RESERVED_PROJECT_IDS
    | {
        "project_json",
        "bible",
        "storyform",
        "chapters",
        "scenes",
        "scene_metadata",
        "notes",
        "note_metadata",
        "materials",
        "material_metadata",
    }
)

# Hybrid core-folder creation per `project_creation_flow_spec.md` §8 and
# `project_workspace_foundation_spec.md` §8. Memory, OMI, bible, and
# storyform files are intentionally not created at blank-project
# creation time and remain lazy per the WORKSPACE-026 decision sweep.
WORKSPACE_CORE_FOLDERS: tuple[str, ...] = (
    "chapters",
    "scenes",
    "scene_metadata",
    "notes",
    "note_metadata",
    "materials",
    "material_metadata",
)

STANDARD_REFUSAL_MESSAGE = (
    "I can analyze structure and ask diagnostic questions, "
    "but I cannot write or rewrite story prose."
)

OWNER_APPROVED_TRUTH_POLICY: dict[str, Any] = {
    "durable_truth_requires_owner_approval": True,
    "candidate_outputs_do_not_promote_automatically": True,
    "ai_prose_generation_prohibited": True,
    "standard_refusal_message": STANDARD_REFUSAL_MESSAGE,
}


# ---------------------------------------------------------------------------
# Project creation helpers (PHASE7-IMPL-001)
# These never call Ollama, analysis_engine, or Story Check.
# They never create bible.json, storyform.json, OMI records, memory/canon
# files, generated summaries, candidates, training data, or model artifacts.
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_project_title(title: str) -> str:
    if not isinstance(title, str):
        raise TypeError("Project title must be a string")
    stripped = title.strip()
    if not stripped:
        raise ValueError("Project title must not be blank")
    if len(stripped) > MAX_PROJECT_TITLE_LENGTH:
        raise ValueError(
            f"Project title must not exceed {MAX_PROJECT_TITLE_LENGTH} characters"
        )
    return stripped


def derive_project_id(title: str) -> str:
    validated_title = _validate_project_title(title)
    # Unicode normalize to NFKD then ASCII-fold
    normalized = unicodedata.normalize("NFKD", validated_title)
    ascii_folded = normalized.encode("ascii", errors="ignore").decode("ascii")
    lowered = ascii_folded.lower()
    # Replace runs of unsafe characters with a single hyphen
    slugged = _PROJECT_ID_INVALID_CHAR_RUN.sub("-", lowered)
    # Collapse repeated hyphens
    slugged = _PROJECT_ID_REPEAT_HYPHEN.sub("-", slugged)
    # Strip leading/trailing hyphens, underscores, spaces, and dots
    slugged = slugged.strip("-_. ")
    if not slugged:
        raise ValueError(
            f"Project title {title!r} produces an empty project ID after normalization"
        )
    # Truncate to the length limit before final validation
    slugged = slugged[:MAX_PROJECT_ID_LENGTH].strip("-_. ")
    if not slugged:
        raise ValueError(
            f"Project title {title!r} produces an empty project ID after truncation"
        )
    return validate_project_id(slugged)


def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str) or not project_id:
        raise ValueError("Project ID must be a non-empty string")
    if Path(project_id).is_absolute():
        raise ValueError(f"Project ID must not be an absolute path: {project_id!r}")
    if ".." in project_id or project_id == ".":
        raise ValueError(f"Project ID must not contain path traversal: {project_id!r}")
    if "/" in project_id or "\\" in project_id:
        raise ValueError(f"Project ID must not contain path separators: {project_id!r}")
    # Windows drive letter (e.g. "c:")
    if len(project_id) >= 2 and project_id[1] == ":" and project_id[0].isalpha():
        raise ValueError(f"Project ID must not be a Windows drive path: {project_id!r}")
    if project_id.lower() in RESERVED_PROJECT_IDS:
        raise ValueError(f"Project ID is reserved: {project_id!r}")
    if not _PROJECT_ID_PATTERN.match(project_id):
        raise ValueError(
            f"Project ID {project_id!r} does not match the required pattern "
            f"(lowercase alphanumeric start, hyphens/underscores allowed, "
            f"max {MAX_PROJECT_ID_LENGTH} chars)"
        )
    return project_id


def resolve_project_id_with_collision(
    base_project_id: str,
    projects_dir: Path = PROJECTS_DIR,
) -> str:
    validate_project_id(base_project_id)
    if not (projects_dir / base_project_id).exists():
        return base_project_id
    for attempt in range(2, MAX_PROJECT_ID_COLLISION_ATTEMPTS + 2):
        candidate = f"{base_project_id}-{attempt}"
        if len(candidate) > MAX_PROJECT_ID_LENGTH:
            raise ValueError(
                f"Cannot resolve collision for project ID {base_project_id!r}: "
                "suffix would exceed maximum ID length"
            )
        if not (projects_dir / candidate).exists():
            return candidate
    raise ValueError(
        f"Cannot create project {base_project_id!r}: "
        f"all {MAX_PROJECT_ID_COLLISION_ATTEMPTS} collision attempts are taken"
    )


def create_project(
    title: str,
    projects_dir: Path = PROJECTS_DIR,
) -> dict[str, Any]:
    validated_title = _validate_project_title(title)
    base_id = derive_project_id(validated_title)
    project_id = resolve_project_id_with_collision(base_id, projects_dir)

    resolved_root = projects_dir.resolve()
    project_path = (projects_dir / project_id).resolve()

    # Path-safety guard: final project path must be inside the resolved projects root
    try:
        project_path.relative_to(resolved_root)
    except ValueError:
        raise ValueError(
            f"Project path {project_path} is not inside the projects directory "
            f"{resolved_root}"
        )

    if project_path.exists():
        raise FileExistsError(f"Project directory already exists: {project_path}")

    project_path.mkdir(parents=True, exist_ok=False)
    for folder in WORKSPACE_CORE_FOLDERS:
        (project_path / folder).mkdir(exist_ok=False)

    timestamp = _utc_now_iso()
    metadata: dict[str, Any] = {
        "project_id": project_id,
        "title": validated_title,
        "created_at": timestamp,
        "updated_at": timestamp,
        "schema_version": PROJECT_SCHEMA_VERSION,
        "creation_method": PROJECT_CREATION_METHOD_BLANK,
        "owner_approved_truth_policy": OWNER_APPROVED_TRUTH_POLICY,
    }

    _write_json_object(project_path / "project.json", metadata, "project.json", overwrite=False)

    return metadata


# ---------------------------------------------------------------------------
# End project creation helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Project library scan helpers (PHASE7-IMPL-002 micro-task 1)
# Scan-first listing for a future GET /api/projects route. These helpers never
# call Ollama, analysis_engine, or Story Check. They never read or mutate OMI
# records, memory/canon files, scene prose, training data, or model artifacts.
# They do not create or update projects/index.json.
# ---------------------------------------------------------------------------


def _is_path_contained_in(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (OSError, ValueError):
        return False


def _project_path_for_id(project_id: str, projects_dir: Path) -> Path:
    validate_project_id(project_id)
    resolved_root = projects_dir.resolve()
    project_path = (projects_dir / project_id).resolve()
    try:
        project_path.relative_to(resolved_root)
    except ValueError:
        raise ValueError(
            f"Project path for {project_id!r} is not inside the projects directory"
        )
    return project_path


def _safe_folder_label(folder_name: str) -> str:
    try:
        return validate_project_id(folder_name)
    except ValueError:
        if (
            folder_name
            and "/" not in folder_name
            and "\\" not in folder_name
            and folder_name not in {".", ".."}
            and not Path(folder_name).is_absolute()
        ):
            return folder_name[:MAX_PROJECT_ID_LENGTH]
        return "invalid-folder"


def _project_library_warning_record(
    folder_name: str,
    *,
    status: str = "invalid",
    warnings: list[str],
    project_id: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "project_id": project_id if project_id is not None else _safe_folder_label(folder_name),
        "status": status,
        "warnings": warnings,
    }
    for key, value in extra.items():
        if value is not None:
            record[key] = value
    return record


def _read_project_json(project_path: Path) -> dict[str, Any]:
    json_path = project_path / "project.json"
    if not json_path.exists():
        raise FileNotFoundError("project.json is missing")
    if not json_path.is_file():
        raise ValueError("project.json is not a file")

    with json_path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("project.json must contain a JSON object")

    return data


def _inspect_project_folder(folder_name: str, projects_dir: Path) -> dict[str, Any]:
    try:
        validate_project_id(folder_name)
    except ValueError:
        return _project_library_warning_record(
            folder_name,
            status="invalid",
            warnings=["unsafe folder name"],
        )

    entry_path = projects_dir / folder_name
    resolved_root = projects_dir.resolve()

    try:
        resolved_entry = entry_path.resolve(strict=False)
    except OSError:
        return _project_library_warning_record(
            folder_name,
            status="warning",
            warnings=["unreadable project folder"],
            project_id=folder_name,
        )

    if not _is_path_contained_in(resolved_entry, resolved_root):
        return _project_library_warning_record(
            folder_name,
            status="invalid",
            warnings=["project folder resolves outside projects directory"],
            project_id=folder_name,
        )

    warnings: list[str] = []
    if entry_path.is_symlink():
        warnings.append("project folder is a symlink")

    if not resolved_entry.is_dir():
        return _project_library_warning_record(
            folder_name,
            status="invalid",
            warnings=["project folder is not a directory"],
            project_id=folder_name,
        )

    json_path = resolved_entry / "project.json"
    if not json_path.exists():
        return _project_library_warning_record(
            folder_name,
            status="invalid",
            warnings=["missing project.json"],
            project_id=folder_name,
            relative_path=folder_name,
        )

    try:
        metadata = _read_project_json(resolved_entry)
    except json.JSONDecodeError:
        return _project_library_warning_record(
            folder_name,
            status="invalid",
            warnings=["project.json contains invalid JSON"],
            project_id=folder_name,
            relative_path=folder_name,
        )
    except (OSError, ValueError):
        return _project_library_warning_record(
            folder_name,
            status="warning",
            warnings=["unreadable project.json"],
            project_id=folder_name,
            relative_path=folder_name,
        )

    json_project_id = metadata.get("project_id")
    metadata_project_id = folder_name
    if json_project_id is not None:
        if not isinstance(json_project_id, str):
            return _project_library_warning_record(
                folder_name,
                status="invalid",
                warnings=["project.json project_id must be a string"],
                project_id=folder_name,
                relative_path=folder_name,
            )
        try:
            validate_project_id(json_project_id)
        except ValueError:
            return _project_library_warning_record(
                folder_name,
                status="invalid",
                warnings=["project.json project_id is unsafe"],
                project_id=folder_name,
                relative_path=folder_name,
            )
        metadata_project_id = json_project_id
        if json_project_id != folder_name:
            return _project_library_warning_record(
                folder_name,
                status="invalid",
                warnings=["project_id mismatch between folder and project.json"],
                project_id=folder_name,
                relative_path=folder_name,
                title=metadata.get("title")
                if isinstance(metadata.get("title"), str)
                else None,
                _metadata_project_id=metadata_project_id,
            )

    title = metadata.get("title")
    if title is not None and not isinstance(title, str):
        warnings.append("project.json title must be a string")
        title = folder_name
    elif not title:
        title = folder_name

    record: dict[str, Any] = {
        "project_id": folder_name,
        "title": title,
        "created_at": metadata.get("created_at"),
        "updated_at": metadata.get("updated_at"),
        "schema_version": metadata.get("schema_version"),
        "creation_method": metadata.get("creation_method"),
        "relative_path": folder_name,
        "status": "valid",
        "warnings": list(warnings),
        "_metadata_project_id": metadata_project_id,
    }
    if warnings:
        record["status"] = "warning"
    return record


def _apply_duplicate_project_id_warnings(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    metadata_id_to_indices: dict[str, list[int]] = {}
    for index, record in enumerate(records):
        metadata_project_id = record.get("_metadata_project_id")
        if not isinstance(metadata_project_id, str):
            continue
        metadata_id_to_indices.setdefault(metadata_project_id, []).append(index)

    for metadata_project_id, indices in metadata_id_to_indices.items():
        if len(indices) < 2:
            continue
        for index in indices:
            updated = dict(records[index])
            updated_warnings = list(updated.get("warnings", []))
            updated_warnings.append(
                f"duplicate project_id: {metadata_project_id!r}"
            )
            updated["warnings"] = updated_warnings
            updated["status"] = "invalid"
            records[index] = updated

    return records


def _strip_internal_library_fields(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def _sort_project_library_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    valid_records = [record for record in records if record.get("status") == "valid"]
    other_records = [record for record in records if record.get("status") != "valid"]

    valid_records.sort(key=lambda record: (record.get("project_id") or "").lower())
    valid_records.sort(key=lambda record: (record.get("title") or "").lower())
    valid_records.sort(
        key=lambda record: record.get("updated_at")
        if isinstance(record.get("updated_at"), str)
        else "",
        reverse=True,
    )
    other_records.sort(key=lambda record: (record.get("project_id") or "").lower())

    return valid_records + other_records


def load_project_metadata(
    project_id: str,
    projects_dir: Path = PROJECTS_DIR,
) -> dict[str, Any]:
    try:
        validate_project_id(project_id)
    except ValueError:
        return _strip_internal_library_fields(
            _project_library_warning_record(
                project_id,
                status="invalid",
                warnings=["unsafe project_id"],
            )
        )

    try:
        project_path = _project_path_for_id(project_id, projects_dir)
    except ValueError:
        return _strip_internal_library_fields(
            _project_library_warning_record(
                project_id,
                status="invalid",
                warnings=["unsafe project path"],
                project_id=project_id,
            )
        )

    if not project_path.exists():
        return _strip_internal_library_fields(
            _project_library_warning_record(
                project_id,
                status="invalid",
                warnings=["project folder does not exist"],
                project_id=project_id,
            )
        )

    if not project_path.is_dir():
        return _strip_internal_library_fields(
            _project_library_warning_record(
                project_id,
                status="invalid",
                warnings=["project path is not a directory"],
                project_id=project_id,
            )
        )

    return _strip_internal_library_fields(
        _inspect_project_folder(project_id, projects_dir)
    )


def list_projects(projects_dir: Path = PROJECTS_DIR) -> list[dict[str, Any]]:
    if not projects_dir.exists() or not projects_dir.is_dir():
        return []

    records: list[dict[str, Any]] = []
    try:
        child_entries = list(projects_dir.iterdir())
    except OSError:
        return []

    for entry in sorted(child_entries, key=lambda path: path.name.lower()):
        try:
            if not entry.is_dir():
                continue
        except OSError:
            records.append(
                _project_library_warning_record(
                    entry.name,
                    status="warning",
                    warnings=["unreadable directory entry"],
                )
            )
            continue

        records.append(_inspect_project_folder(entry.name, projects_dir))

    records = _apply_duplicate_project_id_warnings(records)
    records = _sort_project_library_records(records)
    return [_strip_internal_library_fields(record) for record in records]


# ---------------------------------------------------------------------------
# End project library scan helpers
# ---------------------------------------------------------------------------


OMI_CANDIDATE_TYPES = {
    "planning_note",
    "project_bible_candidate",
    "storyform_context_candidate",
    "scene_prompt_context_candidate",
    "template_starter_candidate",
}

OMI_DESTINATIONS = {
    "planning_notes",
    "project_bible_candidate",
    "storyform_context_candidate",
    "scene_prompt_context_candidate",
    "template_starter_candidate",
    "discard",
}

OMI_BLOCKED_DESTINATIONS = {
    "scene_prose",
    "chapter",
    "dialogue",
    "rewrite",
    "continuation",
    "final_story_text",
}

OMI_PROMOTION_TARGETS = {
    "bible.json",
    "owner_memory.json",
    "planning_notes",
    "storyform.json",
}

OMI_PROMOTION_BLOCKED_TARGETS = OMI_BLOCKED_DESTINATIONS | {
    "scenes",
    "scene",
    "story",
    "story_text",
}

OMI_PROMOTION_RECORD_STATUS = "ready_for_manual_application"

OMI_OWNER_DECISIONS = {"pending", "approve", "reject", "needs_revision"}

OMI_STATUSES = {"draft", "candidate", "owner_review", "approved", "rejected", "archived"}

OMI_STATUS_TRANSITIONS = {
    "draft": {"owner_review", "archived"},
    "candidate": {"owner_review", "archived"},
    "owner_review": {"approved", "rejected", "candidate"},
    "approved": {"owner_review", "archived"},
    "rejected": {"owner_review", "archived"},
    "archived": set(),
}

OMI_EXTRACTED_CANDIDATE_TYPES = frozenset(
    {
        "character",
        "location",
        "timeline_event",
        "relationship",
        "organization",
        "object",
        "plot_thread",
        "story_fact",
        "open_question",
        "storyform_context",
    }
)

OMI_EXTRACTION_STATUSES = frozenset({"succeeded", "empty", "fail_closed"})
OMI_EXTRACTED_CANDIDATE_STATUSES = frozenset(
    {
        "candidate",
        "review_pending",
        "owner_review",
        "candidate_review_pending",
    }
)
OMI_EXTRACTED_CANDIDATE_DEFAULT_STATUS = "candidate_review_pending"
OMI_EXTRACTION_SUPPORT_LABEL = "support strength only"
OMI_DETERMINISTIC_EXTRACTOR_NAME = "omi_deterministic_marker_extractor"
OMI_DETERMINISTIC_EXTRACTOR_VERSION = "phase8-impl-023-t004"
OMI_EXPLICIT_MARKER_CANDIDATE_TYPES = {
    "character": "character",
    "location": "location",
    "organization": "organization",
    "object": "object",
    "timeline event": "timeline_event",
    "relationship": "relationship",
    "plot thread": "plot_thread",
    "story fact": "story_fact",
    "open question": "open_question",
    "storyform context": "storyform_context",
}
OMI_EXPLICIT_MARKER_PATTERN = re.compile(
    r"^\s*(?P<marker>"
    + "|".join(re.escape(marker) for marker in OMI_EXPLICIT_MARKER_CANDIDATE_TYPES)
    + r")\s*:\s*(?P<claim>.+?)\s*$",
    re.IGNORECASE,
)
OMI_EXTRACTED_ENTITY_NAME_TYPES = frozenset(
    {"character", "location", "organization", "object"}
)


def _safe_path_component(value: str, label: str) -> str:
    if not value:
        raise ValueError(f"{label} must not be empty")

    path = Path(value)
    if path.is_absolute() or path.parts != (value,) or value in {".", ".."}:
        raise ValueError(f"{label} must be a single path component")

    return value


def _project_dir(project_name: str) -> Path:
    safe_name = _safe_path_component(project_name, "project_name")
    return PROJECTS_DIR / safe_name


def _scene_path(project_name: str, scene_id: str) -> Path:
    safe_scene_id = _safe_path_component(scene_id, "scene_id")
    return _project_dir(project_name) / "scenes" / f"{safe_scene_id}.md"


def _scene_metadata_path(project_name: str, scene_id: str) -> Path:
    safe_scene_id = _safe_path_component(scene_id, "scene_id")
    return _project_dir(project_name) / "scene_metadata" / f"{safe_scene_id}.json"


def _chapter_metadata_path(project_name: str, chapter_id: str) -> Path:
    safe_chapter_id = _safe_path_component(chapter_id, "chapter_id")
    return _project_dir(project_name) / "chapters" / f"{safe_chapter_id}.json"


def _safe_document_id(value: str, label: str) -> str:
    safe_value = _safe_path_component(value, label)
    if "\\" in safe_value or ":" in safe_value:
        raise ValueError(f"{label} must be a safe document ID")
    if safe_value.startswith("."):
        raise ValueError(f"{label} must not start with a dot")
    if len(safe_value) > MAX_DOCUMENT_ID_LENGTH:
        raise ValueError(f"{label} must not exceed {MAX_DOCUMENT_ID_LENGTH} characters")
    if not _DOCUMENT_ID_PATTERN.fullmatch(safe_value):
        raise ValueError(f"{label} must contain only lowercase letters, digits, and underscores")
    if safe_value.lower() in RESERVED_DOCUMENT_IDS:
        raise ValueError(f"{label} is reserved")
    return safe_value


def _note_path(project_name: str, note_id: str) -> Path:
    safe_note_id = _safe_document_id(note_id, "note_id")
    return _project_dir(project_name) / "notes" / f"{safe_note_id}.md"


def _note_metadata_path(project_name: str, note_id: str) -> Path:
    safe_note_id = _safe_document_id(note_id, "note_id")
    return _project_dir(project_name) / "note_metadata" / f"{safe_note_id}.json"


def _material_path(project_name: str, material_id: str) -> Path:
    safe_material_id = _safe_document_id(material_id, "material_id")
    return _project_dir(project_name) / "materials" / f"{safe_material_id}.md"


def _material_metadata_path(project_name: str, material_id: str) -> Path:
    safe_material_id = _safe_document_id(material_id, "material_id")
    return _project_dir(project_name) / "material_metadata" / f"{safe_material_id}.json"


def _json_path(project_name: str, filename: str) -> Path:
    return _project_dir(project_name) / filename


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_after(previous_timestamp: str | None) -> str:
    current_timestamp = _utc_now()
    if not previous_timestamp or current_timestamp > previous_timestamp:
        return current_timestamp

    try:
        previous = datetime.fromisoformat(previous_timestamp.replace("Z", "+00:00"))
    except ValueError:
        return current_timestamp

    return (
        (previous + timedelta(seconds=1))
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _new_record_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _omi_dir(project_name: str) -> Path:
    return _project_dir(project_name) / "omi"


def _omi_index_path(project_name: str) -> Path:
    return _omi_dir(project_name) / "index.json"


def _omi_record_path(project_name: str, folder_name: str, record_id: str, label: str) -> Path:
    safe_id = _safe_path_component(record_id, label)
    return _omi_dir(project_name) / folder_name / f"{safe_id}.json"


def _load_json_object(project_name: str, filename: str, label: str) -> dict[str, Any]:
    path = _json_path(project_name, filename)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{label} file must contain a JSON object: {path}")

    return data


def _save_json_object(project_name: str, filename: str, data: dict[str, Any], label: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{label} data must be a JSON object")

    path = _json_path(project_name, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_json_object(path: Path, data: dict[str, Any], label: str, *, overwrite: bool) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{label} data must be a JSON object")
    if path.exists() and not overwrite:
        raise FileExistsError(f"{label} already exists: {path.name}")

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")

    try:
        temp_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _load_json_object_from_path(path: Path, label: str) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{label} file must contain a JSON object: {path}")

    return data


def _default_omi_index(project_name: str) -> dict[str, Any]:
    return {
        "project_id": project_name,
        "idea_ids": [],
        "candidate_ids": [],
        "promotion_ids": [],
        "last_updated": None,
    }


def _normalise_omi_index(project_name: str, index: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(index, dict):
        raise ValueError("OMI index data must be a JSON object")

    return {
        "project_id": project_name,
        "idea_ids": sorted(set(index.get("idea_ids", []))),
        "candidate_ids": sorted(set(index.get("candidate_ids", []))),
        "promotion_ids": sorted(set(index.get("promotion_ids", []))),
        "last_updated": index.get("last_updated"),
    }


def _default_omi_provenance(
    *,
    source_type: str = "owner_input",
    source_path: str | None = None,
    source_label: str = "Manual OMI entry",
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_path": source_path,
        "source_label": source_label,
        "created_by": "owner",
        "tool": "app",
        "model": None,
        "prompt_id": None,
        "timestamp": _utc_now(),
        "source_hash": None,
        "snapshot_hash": None,
        "confidence": None,
        "notes": [],
    }


def _normalise_provenance(
    provenance: dict[str, Any] | None,
    *,
    source_path: str | None,
    source_label: str,
) -> dict[str, Any]:
    if provenance is None:
        return _default_omi_provenance(source_path=source_path, source_label=source_label)
    if not isinstance(provenance, dict):
        raise ValueError("OMI provenance must be a JSON object")

    merged = _default_omi_provenance(source_path=source_path, source_label=source_label)
    merged.update(provenance)
    merged.setdefault("timestamp", _utc_now())
    return merged


def _default_owner_decision() -> dict[str, Any]:
    return {
        "decision": "pending",
        "approved": False,
        "approval_confirmed": False,
        "decided_by": None,
        "decided_at": None,
        "notes": "",
    }


def _validate_omi_destination(destination: str) -> str:
    if destination in OMI_BLOCKED_DESTINATIONS or destination not in OMI_DESTINATIONS:
        raise ValueError(f"Unsupported OMI destination: {destination}")
    return destination


def _validate_omi_candidate_type(candidate_type: str) -> str:
    if candidate_type not in OMI_CANDIDATE_TYPES:
        raise ValueError(f"Unsupported OMI candidate_type: {candidate_type}")
    return candidate_type


def validate_omi_owner_decision(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("OMI owner_decision must be a JSON object")

    decision = value.get("decision", "pending")
    if decision not in OMI_OWNER_DECISIONS:
        raise ValueError(f"Unsupported OMI owner_decision: {decision}")

    approval_confirmed = bool(value.get("approval_confirmed", value.get("approved", False)))
    if decision == "approve" and not approval_confirmed:
        raise ValueError("OMI approve decision requires approval_confirmed true")

    notes = value.get("notes", "")
    if not isinstance(notes, str):
        raise ValueError("OMI owner_decision notes must be a string")

    decided_by = value.get("decided_by")
    if decided_by is not None and not isinstance(decided_by, str):
        raise ValueError("OMI owner_decision decided_by must be a string")

    decided_at = value.get("decided_at")
    if decided_at is not None and not isinstance(decided_at, str):
        raise ValueError("OMI owner_decision decided_at must be a string or null")

    return {
        "decision": decision,
        "approved": decision == "approve" and approval_confirmed,
        "approval_confirmed": approval_confirmed,
        "decided_by": decided_by,
        "decided_at": decided_at,
        "notes": notes,
    }


def _status_from_decision(
    current_status: str,
    owner_decision: dict[str, Any],
    requested_status: str | None,
) -> str:
    decision = owner_decision["decision"]
    default_status = {
        "approve": "approved",
        "reject": "rejected",
        "needs_revision": "candidate",
    }.get(decision, current_status)
    next_status = requested_status or default_status

    expected_status = {
        "approve": "approved",
        "reject": "rejected",
        "needs_revision": "candidate",
    }.get(decision)
    if expected_status is not None and next_status != expected_status:
        raise ValueError(
            f"OMI {decision} decision requires status {expected_status}"
        )

    return next_status


def validate_omi_status_transition(current_status: str, next_status: str) -> str:
    if next_status == "promoted":
        raise ValueError("OMI promoted status is reserved for the future promotion gate")
    if current_status not in OMI_STATUSES:
        raise ValueError(f"Unsupported current OMI status: {current_status}")
    if next_status not in OMI_STATUSES:
        raise ValueError(f"Unsupported OMI status: {next_status}")
    if next_status == current_status:
        return next_status
    if next_status not in OMI_STATUS_TRANSITIONS[current_status]:
        raise ValueError(f"Invalid OMI status transition: {current_status} -> {next_status}")
    return next_status


def validate_omi_destination(destination: str) -> str:
    return _validate_omi_destination(destination)


def validate_omi_extracted_candidate_type(candidate_type: str) -> str:
    if candidate_type not in OMI_EXTRACTED_CANDIDATE_TYPES:
        raise ValueError(f"Unsupported OMI extracted candidate_type: {candidate_type}")
    return candidate_type


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _validate_omi_extracted_candidate_evidence(evidence: Any) -> list[dict[str, Any]]:
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("OMI extracted candidate evidence must be a non-empty array")

    normalized: list[dict[str, Any]] = []
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("OMI extracted candidate evidence items must be JSON objects")
        source_excerpt = item.get("source_excerpt", item.get("excerpt"))
        source_locator = item.get("source_locator", item.get("locator"))
        if not (
            isinstance(source_excerpt, str)
            and source_excerpt.strip()
            or isinstance(source_locator, str)
            and source_locator.strip()
        ):
            raise ValueError(
                "OMI extracted candidate evidence requires source_excerpt or source_locator"
            )
        normalized.append(dict(item))
    return normalized


def validate_omi_extracted_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ValueError("OMI extracted candidate must be a JSON object")

    normalized = dict(candidate)
    normalized["candidate_type"] = validate_omi_extracted_candidate_type(
        normalized.get("candidate_type")
    )

    label = normalized.get("label") or normalized.get("name")
    normalized["label"] = _require_non_empty_string(label, "OMI extracted candidate label")
    normalized["extracted_claim"] = _require_non_empty_string(
        normalized.get("extracted_claim"),
        "OMI extracted candidate extracted_claim",
    )
    normalized["evidence"] = _validate_omi_extracted_candidate_evidence(
        normalized.get("evidence")
    )

    provenance = normalized.get("provenance")
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("OMI extracted candidate provenance must be a non-empty JSON object")
    if provenance.get("model") is not None:
        raise ValueError("OMI extraction provenance model must be null for deterministic MVP")
    if provenance.get("prompt_id") is not None:
        raise ValueError("OMI extraction provenance prompt_id must be null")
    normalized["provenance"] = dict(provenance)

    status = normalized.get("status", OMI_EXTRACTED_CANDIDATE_DEFAULT_STATUS)
    if status in {"approved", "promoted", "canon"}:
        raise ValueError("OMI extracted candidate status must not imply approval or canon")
    if status not in OMI_EXTRACTED_CANDIDATE_STATUSES:
        raise ValueError(f"Unsupported OMI extracted candidate status: {status}")
    normalized["status"] = status

    owner_decision = normalized.get("owner_decision") or _default_owner_decision()
    owner_decision = validate_omi_owner_decision(owner_decision)
    if owner_decision.get("decision") != "pending" or owner_decision.get("approved"):
        raise ValueError("OMI extracted candidate owner_decision must remain pending")
    normalized["owner_decision"] = owner_decision

    for support_key in ("support_strength", "confidence"):
        if support_key not in normalized:
            continue
        support_label = str(
            normalized.get("support_label")
            or normalized.get("support_strength_label")
            or normalized.get("confidence_label")
            or ""
        ).lower()
        if "support" not in support_label or "truth" in support_label:
            raise ValueError(
                "OMI extracted candidate support/confidence must be labeled as support, not truth"
            )

    return normalized


def _validate_omi_promotion_target(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"OMI promotion {label} must be a non-empty string")

    normalized = value.strip()
    path = Path(normalized)
    lower_value = normalized.lower()

    if (
        path.is_absolute()
        or ".." in path.parts
        or normalized in {".", ".."}
        or any(part in OMI_PROMOTION_BLOCKED_TARGETS for part in path.parts)
    ):
        raise ValueError(f"Unsupported OMI promotion {label}: {value}")

    if lower_value not in OMI_PROMOTION_TARGETS:
        raise ValueError(f"Unsupported OMI promotion {label}: {value}")

    return normalized


def _candidate_promotion_blockers(candidate: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    owner_decision = candidate.get("owner_decision")

    if candidate.get("status") != "approved":
        blockers.append("candidate status must be approved")

    if not isinstance(owner_decision, dict):
        blockers.append("owner decision required")
    else:
        if owner_decision.get("decision") != "approve":
            blockers.append("owner decision must be approve")
        if owner_decision.get("approval_confirmed") is not True:
            blockers.append("owner approval confirmation required")

    destination = candidate.get("destination")
    try:
        _validate_omi_destination(destination)
    except (TypeError, ValueError):
        blockers.append("allowed destination required")
    else:
        if destination == "discard":
            blockers.append("discard destination cannot be promoted")

    if not isinstance(candidate.get("provenance"), dict) or not candidate.get("provenance"):
        blockers.append("provenance required")

    if not isinstance(candidate.get("candidate_content"), dict):
        blockers.append("candidate_content must be a JSON object")

    return blockers


def is_omi_candidate_promotion_ready(candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        return {"ready": False, "blocked_reasons": ["candidate record required"]}

    blockers = _candidate_promotion_blockers(candidate)
    return {"ready": len(blockers) == 0, "blocked_reasons": blockers}


def _finalize_owner_decision(owner_decision: dict[str, Any], timestamp: str) -> dict[str, Any]:
    finalized = dict(owner_decision)
    if finalized["decision"] == "pending":
        finalized["approved"] = False
        finalized["approval_confirmed"] = False
        finalized["decided_by"] = finalized.get("decided_by")
        finalized["decided_at"] = None
    else:
        finalized["decided_by"] = "owner"
        finalized["decided_at"] = timestamp
    return finalized


def load_bible(project_name: str) -> dict[str, Any]:
    return _load_json_object(project_name, "bible.json", "Bible")


def save_bible(project_name: str, data: dict[str, Any]) -> None:
    _save_json_object(project_name, "bible.json", data, "Bible")


def load_storyform_json(project_name: str) -> dict[str, Any]:
    return _load_json_object(project_name, "storyform.json", "Storyform")


def save_storyform_json(project_name: str, data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("Storyform data must be a JSON object")

    try:
        from .storyform import Storyform
    except ImportError:  # pragma: no cover - supports direct module execution
        from storyform import Storyform

    Storyform.validate_data(data)
    _save_json_object(project_name, "storyform.json", data, "Storyform")


def load_scene(project_name: str, scene_id: str) -> str:
    return _scene_path(project_name, scene_id).read_text(encoding="utf-8")


def _scene_content_path_value(scene_id: str) -> str:
    safe_scene_id = _safe_path_component(scene_id, "scene_id")
    return f"scenes/{safe_scene_id}.md"


def _note_content_path_value(note_id: str) -> str:
    safe_note_id = _safe_document_id(note_id, "note_id")
    return f"notes/{safe_note_id}.md"


def _material_content_path_value(material_id: str) -> str:
    safe_material_id = _safe_document_id(material_id, "material_id")
    return f"materials/{safe_material_id}.md"


def _copy_metadata_payload(value: dict[str, Any] | None, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} metadata must be a JSON object")
    return dict(value)


def _string_or_none(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string or null")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must contain only strings")
    return list(value)


def _safe_scene_id_list(value: Any) -> list[str]:
    return [
        _safe_path_component(scene_id, "scene_id")
        for scene_id in _string_list(value, "scene_ids")
    ]


def _safe_component_list(value: Any, label: str, item_label: str) -> list[str]:
    safe_values: list[str] = []
    for item in _string_list(value, label):
        safe_values.append(_safe_document_id(item, item_label))
    return safe_values


def _safe_string_or_none(value: Any, label: str) -> str | None:
    value = _string_or_none(value, label)
    if value is None:
        return None
    return _safe_document_id(value, label)


def _relative_reference_path_or_none(value: Any, label: str) -> str | None:
    value = _string_or_none(value, label)
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise ValueError(f"{label} must be a safe relative reference path")
    return value


def _metadata_object(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return dict(value)


def _normalise_document_link_fields(record: dict[str, Any]) -> None:
    record["tags"] = _string_list(record.get("tags"), "tags")
    record["linked_chapter_ids"] = _safe_component_list(
        record.get("linked_chapter_ids"),
        "linked_chapter_ids",
        "chapter_id",
    )
    record["linked_scene_ids"] = _safe_component_list(
        record.get("linked_scene_ids"),
        "linked_scene_ids",
        "scene_id",
    )
    record["linked_candidate_ids"] = _safe_component_list(
        record.get("linked_candidate_ids"),
        "linked_candidate_ids",
        "candidate_id",
    )
    record["linked_memory_record_ids"] = _safe_component_list(
        record.get("linked_memory_record_ids"),
        "linked_memory_record_ids",
        "memory_record_id",
    )
    record["provenance"] = _metadata_object(record.get("provenance"), "provenance")


def _normalise_note_link_fields(record: dict[str, Any]) -> None:
    _normalise_document_link_fields(record)
    record["summary_candidate_id"] = _safe_string_or_none(
        record.get("summary_candidate_id"),
        "summary_candidate_id",
    )


def _normalise_material_metadata_fields(record: dict[str, Any]) -> None:
    _normalise_document_link_fields(record)
    record["source_kind"] = record.get("source_kind", "owner_text")
    if not isinstance(record["source_kind"], str):
        raise ValueError("source_kind must be a string")
    record["source_url"] = _string_or_none(record.get("source_url"), "source_url")
    record["source_citation"] = _string_or_none(
        record.get("source_citation"),
        "source_citation",
    )
    record["local_reference_path"] = _relative_reference_path_or_none(
        record.get("local_reference_path"),
        "local_reference_path",
    )
    record["license_status"] = record.get("license_status", "owner_provided")
    if not isinstance(record["license_status"], str):
        raise ValueError("license_status must be a string")
    record["usage_restrictions"] = _string_list(
        record.get("usage_restrictions"),
        "usage_restrictions",
    )
    record["source_warnings"] = _string_list(
        record.get("source_warnings"),
        "source_warnings",
    )


def _normalise_note_metadata_read(
    project_name: str,
    note_id: str,
    metadata: dict[str, Any],
    *,
    metadata_exists: bool,
) -> dict[str, Any]:
    safe_note_id = _safe_document_id(note_id, "note_id")
    normalized = dict(metadata)
    normalized.setdefault("metadata_version", NOTE_METADATA_VERSION)
    normalized.setdefault("title", "")
    normalized.setdefault("note_type", "general")
    normalized.setdefault("status", "draft")
    normalized.setdefault("tags", [])
    normalized.setdefault("linked_chapter_ids", [])
    normalized.setdefault("linked_scene_ids", [])
    normalized.setdefault("linked_candidate_ids", [])
    normalized.setdefault("linked_memory_record_ids", [])
    normalized.setdefault("created_at", None)
    normalized.setdefault("updated_at", None)
    normalized.setdefault("word_count", 0)
    normalized.setdefault("owner_notes", "")
    normalized.setdefault("summary_candidate_id", None)
    normalized.setdefault("approved_navigation_summary", None)
    normalized.setdefault(
        "provenance",
        {"created_by": "owner", "creation_method": "manual", "source": "manual"},
    )
    normalized["project_id"] = project_name
    normalized["note_id"] = safe_note_id
    normalized["content_path"] = _note_content_path_value(safe_note_id)
    normalized["metadata_exists"] = metadata_exists
    normalized["metadata_path"] = (
        f"note_metadata/{safe_note_id}.json" if metadata_exists else None
    )
    _normalise_note_link_fields(normalized)
    return normalized


def _normalise_note_metadata_write(
    project_name: str,
    note_id: str,
    metadata: dict[str, Any] | None,
    *,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    safe_note_id = _safe_document_id(note_id, "note_id")
    payload = _copy_metadata_payload(metadata, "Note")
    previous = dict(existing or {})
    record = dict(previous)
    record.update(payload)

    for field in ("project_id", "note_id", "content_path", "metadata_exists", "metadata_path"):
        record.pop(field, None)

    timestamp = _utc_after(_string_or_none(previous.get("updated_at"), "updated_at"))
    created_at = _string_or_none(previous.get("created_at"), "created_at") or timestamp

    record.setdefault("title", "")
    record.setdefault("note_type", "general")
    record.setdefault("status", "draft")
    record.setdefault("tags", [])
    record.setdefault("linked_chapter_ids", [])
    record.setdefault("linked_scene_ids", [])
    record.setdefault("linked_candidate_ids", [])
    record.setdefault("linked_memory_record_ids", [])
    record.setdefault("word_count", 0)
    record.setdefault("owner_notes", "")
    record.setdefault("summary_candidate_id", None)
    record.setdefault("approved_navigation_summary", None)
    record.setdefault(
        "provenance",
        {"created_by": "owner", "creation_method": "manual", "source": "manual"},
    )

    if not isinstance(record["title"], str):
        raise ValueError("title must be a string")
    if not isinstance(record["note_type"], str):
        raise ValueError("note_type must be a string")
    if not isinstance(record["status"], str):
        raise ValueError("status must be a string")
    if not isinstance(record["owner_notes"], str):
        raise ValueError("owner_notes must be a string")
    if not isinstance(record["word_count"], int):
        raise ValueError("word_count must be an integer")

    record["metadata_version"] = NOTE_METADATA_VERSION
    record["project_id"] = project_name
    record["note_id"] = safe_note_id
    record["content_path"] = _note_content_path_value(safe_note_id)
    record["created_at"] = created_at
    record["updated_at"] = timestamp
    _normalise_note_link_fields(record)
    return record


def _normalise_material_metadata_read(
    project_name: str,
    material_id: str,
    metadata: dict[str, Any],
    *,
    metadata_exists: bool,
) -> dict[str, Any]:
    safe_material_id = _safe_document_id(material_id, "material_id")
    normalized = dict(metadata)
    normalized.setdefault("metadata_version", MATERIAL_METADATA_VERSION)
    normalized.setdefault("title", "")
    normalized.setdefault("material_type", "text_reference")
    normalized.setdefault("status", "draft")
    normalized.setdefault("tags", [])
    normalized.setdefault("source_kind", "owner_text")
    normalized.setdefault("source_url", None)
    normalized.setdefault("source_citation", None)
    normalized.setdefault("local_reference_path", None)
    normalized.setdefault("linked_chapter_ids", [])
    normalized.setdefault("linked_scene_ids", [])
    normalized.setdefault("linked_candidate_ids", [])
    normalized.setdefault("linked_memory_record_ids", [])
    normalized.setdefault("created_at", None)
    normalized.setdefault("updated_at", None)
    normalized.setdefault("owner_notes", "")
    normalized.setdefault(
        "provenance",
        {"created_by": "owner", "creation_method": "manual", "source": "manual"},
    )
    normalized.setdefault("license_status", "owner_provided")
    normalized.setdefault("usage_restrictions", [])
    normalized.setdefault("source_warnings", [])
    normalized["project_id"] = project_name
    normalized["material_id"] = safe_material_id
    normalized["content_path"] = _material_content_path_value(safe_material_id)
    normalized["metadata_exists"] = metadata_exists
    normalized["metadata_path"] = (
        f"material_metadata/{safe_material_id}.json" if metadata_exists else None
    )
    _normalise_material_metadata_fields(normalized)
    return normalized


def _normalise_material_metadata_write(
    project_name: str,
    material_id: str,
    metadata: dict[str, Any] | None,
    *,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    safe_material_id = _safe_document_id(material_id, "material_id")
    payload = _copy_metadata_payload(metadata, "Material")
    previous = dict(existing or {})
    record = dict(previous)
    record.update(payload)

    for field in (
        "project_id",
        "material_id",
        "content_path",
        "metadata_exists",
        "metadata_path",
    ):
        record.pop(field, None)

    timestamp = _utc_after(_string_or_none(previous.get("updated_at"), "updated_at"))
    created_at = _string_or_none(previous.get("created_at"), "created_at") or timestamp

    record.setdefault("title", "")
    record.setdefault("material_type", "text_reference")
    record.setdefault("status", "draft")
    record.setdefault("tags", [])
    record.setdefault("source_kind", "owner_text")
    record.setdefault("source_url", None)
    record.setdefault("source_citation", None)
    record.setdefault("local_reference_path", None)
    record.setdefault("linked_chapter_ids", [])
    record.setdefault("linked_scene_ids", [])
    record.setdefault("linked_candidate_ids", [])
    record.setdefault("linked_memory_record_ids", [])
    record.setdefault("owner_notes", "")
    record.setdefault(
        "provenance",
        {"created_by": "owner", "creation_method": "manual", "source": "manual"},
    )
    record.setdefault("license_status", "owner_provided")
    record.setdefault("usage_restrictions", [])
    record.setdefault("source_warnings", [])

    if not isinstance(record["title"], str):
        raise ValueError("title must be a string")
    if not isinstance(record["material_type"], str):
        raise ValueError("material_type must be a string")
    if not isinstance(record["status"], str):
        raise ValueError("status must be a string")
    if not isinstance(record["owner_notes"], str):
        raise ValueError("owner_notes must be a string")

    record["metadata_version"] = MATERIAL_METADATA_VERSION
    record["project_id"] = project_name
    record["material_id"] = safe_material_id
    record["content_path"] = _material_content_path_value(safe_material_id)
    record["created_at"] = created_at
    record["updated_at"] = timestamp
    _normalise_material_metadata_fields(record)
    return record


def _normalise_scene_metadata_read(
    project_name: str,
    scene_id: str,
    metadata: dict[str, Any],
    *,
    metadata_exists: bool,
) -> dict[str, Any]:
    safe_scene_id = _safe_path_component(scene_id, "scene_id")
    content_path = _scene_content_path_value(safe_scene_id)
    normalized = dict(metadata)
    normalized.setdefault("metadata_version", SCENE_METADATA_VERSION)
    normalized.setdefault("chapter_id", None)
    normalized.setdefault("title", "")
    normalized.setdefault("order_index", None)
    normalized["project_id"] = project_name
    normalized["scene_id"] = safe_scene_id
    normalized["content_path"] = content_path
    normalized["metadata_exists"] = metadata_exists
    normalized["metadata_path"] = (
        f"scene_metadata/{safe_scene_id}.json" if metadata_exists else None
    )
    return normalized


def _normalise_scene_metadata_write(
    project_name: str,
    scene_id: str,
    metadata: dict[str, Any] | None,
    *,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    safe_scene_id = _safe_path_component(scene_id, "scene_id")
    payload = _copy_metadata_payload(metadata, "Scene")
    previous = dict(existing or {})
    record = dict(previous)
    record.update(payload)

    if "order_index" not in record and "order" in record:
        record["order_index"] = record["order"]
    record.pop("order", None)
    record.pop("schema_version", None)
    record.pop("metadata_exists", None)
    record.pop("metadata_path", None)

    chapter_id = record.get("chapter_id")
    if chapter_id is not None:
        record["chapter_id"] = _safe_path_component(chapter_id, "chapter_id")

    timestamp = _utc_after(_string_or_none(previous.get("updated_at"), "updated_at"))
    created_at = _string_or_none(previous.get("created_at"), "created_at") or timestamp

    record.setdefault("title", "")
    record.setdefault("status", "draft")
    record.setdefault("owner_notes", "")
    record.setdefault("pov_character_id", None)
    record.setdefault("location_ids", [])
    record.setdefault("timeline_position", None)
    record.setdefault("order_index", None)
    record.setdefault("word_count", 0)
    record.setdefault("summary_candidate_id", None)
    record.setdefault("approved_navigation_summary", None)
    record.setdefault("tags", [])
    record.setdefault(
        "provenance",
        {"created_by": "owner", "creation_method": "manual", "source": "manual"},
    )

    record["metadata_version"] = SCENE_METADATA_VERSION
    record["project_id"] = project_name
    record["scene_id"] = safe_scene_id
    record["content_path"] = _scene_content_path_value(safe_scene_id)
    record["created_at"] = created_at
    record["updated_at"] = timestamp
    record["location_ids"] = _string_list(record.get("location_ids"), "location_ids")
    record["tags"] = _string_list(record.get("tags"), "tags")
    record["provenance"] = _metadata_object(record.get("provenance"), "provenance")
    return record


def _normalise_chapter_metadata_write(
    project_name: str,
    chapter_id: str,
    metadata: dict[str, Any] | None,
    *,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    safe_chapter_id = _safe_path_component(chapter_id, "chapter_id")
    payload = _copy_metadata_payload(metadata, "Chapter")
    previous = dict(existing or {})
    record = dict(previous)
    record.update(payload)

    if "order_index" not in record and "order" in record:
        record["order_index"] = record["order"]
    record.pop("order", None)
    record.pop("schema_version", None)

    timestamp = _utc_after(_string_or_none(previous.get("updated_at"), "updated_at"))
    created_at = _string_or_none(previous.get("created_at"), "created_at") or timestamp

    record.setdefault("title", "")
    record.setdefault("order_index", 0)
    record.setdefault("status", "draft")
    record.setdefault("scene_ids", [])
    record.setdefault("owner_notes", "")
    record.setdefault("owner_metadata", {})
    record.setdefault("summary_candidate_id", None)
    record.setdefault("approved_navigation_summary", None)
    record.setdefault("tags", [])
    record.setdefault(
        "provenance",
        {"created_by": "owner", "creation_method": "manual", "source": "manual"},
    )

    record["metadata_version"] = CHAPTER_METADATA_VERSION
    record["project_id"] = project_name
    record["chapter_id"] = safe_chapter_id
    record["created_at"] = created_at
    record["updated_at"] = timestamp
    record["scene_ids"] = _safe_scene_id_list(record.get("scene_ids"))
    record["owner_metadata"] = _metadata_object(
        record.get("owner_metadata"),
        "owner_metadata",
    )
    record["tags"] = _string_list(record.get("tags"), "tags")
    record["provenance"] = _metadata_object(record.get("provenance"), "provenance")
    return record


def _normalise_chapter_metadata_read(
    project_name: str,
    chapter_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    safe_chapter_id = _safe_path_component(chapter_id, "chapter_id")
    normalized = dict(metadata)
    normalized.setdefault("metadata_version", CHAPTER_METADATA_VERSION)
    normalized.setdefault("title", "")
    normalized.setdefault("order_index", 0)
    normalized.setdefault("status", "draft")
    normalized.setdefault("scene_ids", [])
    normalized.setdefault("owner_notes", "")
    normalized.setdefault("owner_metadata", {})
    normalized.setdefault("summary_candidate_id", None)
    normalized.setdefault("approved_navigation_summary", None)
    normalized.setdefault("tags", [])
    normalized["project_id"] = project_name
    normalized["chapter_id"] = safe_chapter_id
    normalized["scene_ids"] = _safe_scene_id_list(normalized.get("scene_ids"))
    normalized["owner_metadata"] = _metadata_object(
        normalized.get("owner_metadata"),
        "owner_metadata",
    )
    normalized["tags"] = _string_list(normalized.get("tags"), "tags")
    return normalized


def load_scene_metadata(project_name: str, scene_id: str) -> dict[str, Any]:
    scene_path = _scene_path(project_name, scene_id)
    if not scene_path.exists():
        raise FileNotFoundError(scene_path)

    metadata_path = _scene_metadata_path(project_name, scene_id)
    if not metadata_path.exists():
        return _normalise_scene_metadata_read(
            project_name,
            scene_id,
            {},
            metadata_exists=False,
        )

    metadata = _load_json_object_from_path(metadata_path, "Scene metadata")
    return _normalise_scene_metadata_read(
        project_name,
        scene_id,
        metadata,
        metadata_exists=True,
    )


def create_scene_metadata(
    project_name: str,
    scene_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scene_path = _scene_path(project_name, scene_id)
    if not scene_path.exists():
        raise FileNotFoundError(scene_path)

    record = _normalise_scene_metadata_write(
        project_name,
        scene_id,
        metadata,
        existing=None,
    )
    _write_json_object(
        _scene_metadata_path(project_name, scene_id),
        record,
        "Scene metadata",
        overwrite=False,
    )
    return load_scene_metadata(project_name, scene_id)


def update_scene_metadata(
    project_name: str,
    scene_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    scene_path = _scene_path(project_name, scene_id)
    if not scene_path.exists():
        raise FileNotFoundError(scene_path)

    metadata_path = _scene_metadata_path(project_name, scene_id)
    existing = _load_json_object_from_path(metadata_path, "Scene metadata")
    record = _normalise_scene_metadata_write(
        project_name,
        scene_id,
        metadata,
        existing=existing,
    )
    _write_json_object(
        metadata_path,
        record,
        "Scene metadata",
        overwrite=True,
    )
    return load_scene_metadata(project_name, scene_id)


def load_scene_record(project_name: str, scene_id: str) -> dict[str, Any]:
    return {
        "scene_id": _safe_path_component(scene_id, "scene_id"),
        "content": load_scene(project_name, scene_id),
        "metadata": load_scene_metadata(project_name, scene_id),
    }


def save_scene(project_name: str, scene_id: str, content: str) -> None:
    path = _scene_path(project_name, scene_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_scenes(project_name: str) -> list[str]:
    scenes_dir = _project_dir(project_name) / "scenes"
    if not scenes_dir.exists():
        return []

    return [path.stem for path in sorted(scenes_dir.glob("*.md")) if path.is_file()]


def list_scene_metadata(project_name: str) -> list[dict[str, Any]]:
    return [
        load_scene_metadata(project_name, scene_id)
        for scene_id in list_scenes(project_name)
    ]


def load_note(project_name: str, note_id: str) -> str:
    return _note_path(project_name, note_id).read_text(encoding="utf-8")


def save_note(project_name: str, note_id: str, content: str) -> None:
    path = _note_path(project_name, note_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_notes(project_name: str) -> list[str]:
    notes_dir = _project_dir(project_name) / "notes"
    if not notes_dir.exists():
        return []

    return [path.stem for path in sorted(notes_dir.glob("*.md")) if path.is_file()]


def load_note_metadata(project_name: str, note_id: str) -> dict[str, Any]:
    note_path = _note_path(project_name, note_id)
    if not note_path.exists():
        raise FileNotFoundError(note_path)

    metadata_path = _note_metadata_path(project_name, note_id)
    if not metadata_path.exists():
        return _normalise_note_metadata_read(
            project_name,
            note_id,
            {},
            metadata_exists=False,
        )

    metadata = _load_json_object_from_path(metadata_path, "Note metadata")
    return _normalise_note_metadata_read(
        project_name,
        note_id,
        metadata,
        metadata_exists=True,
    )


def create_note_metadata(
    project_name: str,
    note_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    note_path = _note_path(project_name, note_id)
    if not note_path.exists():
        raise FileNotFoundError(note_path)

    record = _normalise_note_metadata_write(
        project_name,
        note_id,
        metadata,
        existing=None,
    )
    _write_json_object(
        _note_metadata_path(project_name, note_id),
        record,
        "Note metadata",
        overwrite=False,
    )
    return load_note_metadata(project_name, note_id)


def update_note_metadata(
    project_name: str,
    note_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    note_path = _note_path(project_name, note_id)
    if not note_path.exists():
        raise FileNotFoundError(note_path)

    metadata_path = _note_metadata_path(project_name, note_id)
    existing = _load_json_object_from_path(metadata_path, "Note metadata")
    record = _normalise_note_metadata_write(
        project_name,
        note_id,
        metadata,
        existing=existing,
    )
    _write_json_object(metadata_path, record, "Note metadata", overwrite=True)
    return load_note_metadata(project_name, note_id)


def list_note_metadata(project_name: str) -> list[dict[str, Any]]:
    return [
        load_note_metadata(project_name, note_id)
        for note_id in list_notes(project_name)
    ]


def load_material(project_name: str, material_id: str) -> str:
    return _material_path(project_name, material_id).read_text(encoding="utf-8")


def save_material(project_name: str, material_id: str, content: str) -> None:
    path = _material_path(project_name, material_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_materials(project_name: str) -> list[str]:
    materials_dir = _project_dir(project_name) / "materials"
    if not materials_dir.exists():
        return []

    return [path.stem for path in sorted(materials_dir.glob("*.md")) if path.is_file()]


def load_material_metadata(project_name: str, material_id: str) -> dict[str, Any]:
    material_path = _material_path(project_name, material_id)
    if not material_path.exists():
        raise FileNotFoundError(material_path)

    metadata_path = _material_metadata_path(project_name, material_id)
    if not metadata_path.exists():
        return _normalise_material_metadata_read(
            project_name,
            material_id,
            {},
            metadata_exists=False,
        )

    metadata = _load_json_object_from_path(metadata_path, "Material metadata")
    return _normalise_material_metadata_read(
        project_name,
        material_id,
        metadata,
        metadata_exists=True,
    )


def create_material_metadata(
    project_name: str,
    material_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    material_path = _material_path(project_name, material_id)
    if not material_path.exists():
        raise FileNotFoundError(material_path)

    record = _normalise_material_metadata_write(
        project_name,
        material_id,
        metadata,
        existing=None,
    )
    _write_json_object(
        _material_metadata_path(project_name, material_id),
        record,
        "Material metadata",
        overwrite=False,
    )
    return load_material_metadata(project_name, material_id)


def update_material_metadata(
    project_name: str,
    material_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    material_path = _material_path(project_name, material_id)
    if not material_path.exists():
        raise FileNotFoundError(material_path)

    metadata_path = _material_metadata_path(project_name, material_id)
    existing = _load_json_object_from_path(metadata_path, "Material metadata")
    record = _normalise_material_metadata_write(
        project_name,
        material_id,
        metadata,
        existing=existing,
    )
    _write_json_object(metadata_path, record, "Material metadata", overwrite=True)
    return load_material_metadata(project_name, material_id)


def list_material_metadata(project_name: str) -> list[dict[str, Any]]:
    return [
        load_material_metadata(project_name, material_id)
        for material_id in list_materials(project_name)
    ]


def load_chapter_metadata(project_name: str, chapter_id: str) -> dict[str, Any]:
    path = _chapter_metadata_path(project_name, chapter_id)
    metadata = _load_json_object_from_path(path, "Chapter metadata")
    return _normalise_chapter_metadata_read(project_name, chapter_id, metadata)


def create_chapter_metadata(
    project_name: str,
    chapter_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = _normalise_chapter_metadata_write(
        project_name,
        chapter_id,
        metadata,
        existing=None,
    )
    _write_json_object(
        _chapter_metadata_path(project_name, chapter_id),
        record,
        "Chapter metadata",
        overwrite=False,
    )
    return load_chapter_metadata(project_name, chapter_id)


def update_chapter_metadata(
    project_name: str,
    chapter_id: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    path = _chapter_metadata_path(project_name, chapter_id)
    existing = _load_json_object_from_path(path, "Chapter metadata")
    record = _normalise_chapter_metadata_write(
        project_name,
        chapter_id,
        metadata,
        existing=existing,
    )
    _write_json_object(path, record, "Chapter metadata", overwrite=True)
    return load_chapter_metadata(project_name, chapter_id)


def ensure_omi_storage(project_name: str) -> None:
    omi_dir = _omi_dir(project_name)
    (omi_dir / "ideas").mkdir(parents=True, exist_ok=True)
    (omi_dir / "candidates").mkdir(parents=True, exist_ok=True)
    (omi_dir / "promotions").mkdir(parents=True, exist_ok=True)


def load_omi_index(project_name: str) -> dict[str, Any]:
    path = _omi_index_path(project_name)
    if not path.exists():
        return _default_omi_index(project_name)

    return _normalise_omi_index(
        project_name,
        _load_json_object_from_path(path, "OMI index"),
    )


def save_omi_index(project_name: str, index: dict[str, Any]) -> None:
    ensure_omi_storage(project_name)
    normalized = _normalise_omi_index(project_name, index)
    normalized["last_updated"] = normalized.get("last_updated") or _utc_now()
    _write_json_object(_omi_index_path(project_name), normalized, "OMI index", overwrite=True)


def create_omi_idea(
    project_name: str,
    raw_idea: str,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(raw_idea, str) or not raw_idea.strip():
        raise ValueError("OMI raw_idea must not be empty")

    ensure_omi_storage(project_name)
    idea_id = _new_record_id("idea")
    timestamp = _utc_now()
    idea = {
        "idea_id": idea_id,
        "project_id": project_name,
        "raw_idea": raw_idea.strip(),
        "status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
        "provenance": _normalise_provenance(
            provenance,
            source_path=None,
            source_label="Manual OMI raw idea",
        ),
        "owner_decision": _default_owner_decision(),
        "linked_candidate_ids": [],
    }

    _write_json_object(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        idea,
        "OMI idea",
        overwrite=False,
    )

    index = load_omi_index(project_name)
    index["idea_ids"] = sorted(set(index.get("idea_ids", [])) | {idea_id})
    index["last_updated"] = timestamp
    save_omi_index(project_name, index)

    return idea


def list_omi_ideas(project_name: str) -> list[dict[str, Any]]:
    index = load_omi_index(project_name)
    ideas: list[dict[str, Any]] = []

    for idea_id in index.get("idea_ids", []):
        try:
            ideas.append(load_omi_idea(project_name, idea_id))
        except FileNotFoundError:
            continue

    return ideas


def load_omi_idea(project_name: str, idea_id: str) -> dict[str, Any]:
    return _load_json_object_from_path(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        "OMI idea",
    )


def _omi_raw_idea_source_locator(source_idea_id: str | None) -> str:
    if source_idea_id:
        return f"omi/ideas/{source_idea_id}.json#raw_idea"
    return "request.raw_idea"


def _raw_idea_sha256(raw_idea: str) -> str:
    return hashlib.sha256(raw_idea.encode("utf-8")).hexdigest()


def _omi_extraction_provenance(
    *,
    raw_idea: str,
    source_idea_id: str | None,
    request_provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extraction_provenance = {
        "source_type": "omi_raw_idea",
        "source_idea_id": source_idea_id,
        "source_locator": _omi_raw_idea_source_locator(source_idea_id),
        "source_author": "owner",
        "owner_authored": True,
        "extractor_name": OMI_DETERMINISTIC_EXTRACTOR_NAME,
        "extractor_version": OMI_DETERMINISTIC_EXTRACTOR_VERSION,
        "tool": "deterministic_marker_rules",
        "model": None,
        "prompt_id": None,
        "timestamp": _utc_now(),
        "source_hash": _raw_idea_sha256(raw_idea),
        "snapshot_hash": _raw_idea_sha256(raw_idea),
    }
    if request_provenance:
        extraction_provenance["request_provenance"] = dict(request_provenance)
    return extraction_provenance


def _omi_empty_extraction_result(
    project_name: str,
    *,
    raw_idea: str,
    source_idea_id: str | None,
    extraction_status: str,
    explanation: str,
    persist_candidates: bool,
    request_provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if extraction_status not in OMI_EXTRACTION_STATUSES - {"succeeded"}:
        raise ValueError(f"Unsupported empty OMI extraction status: {extraction_status}")

    return {
        "schema_version": 1,
        "project_id": project_name,
        "extraction_status": extraction_status,
        "status": extraction_status,
        "explanation": explanation,
        "source_idea_id": source_idea_id,
        "source_locator": _omi_raw_idea_source_locator(source_idea_id),
        "raw_idea_hash": _raw_idea_sha256(raw_idea),
        "candidate_types": sorted(OMI_EXTRACTED_CANDIDATE_TYPES),
        "candidates": [],
        "candidate_count": 0,
        "persist_candidates": persist_candidates,
        "persisted_candidate_ids": [],
        "persistence_status": (
            "no_candidates_persisted"
            if persist_candidates
            else "not_requested"
        ),
        "provenance": _omi_extraction_provenance(
            raw_idea=raw_idea,
            source_idea_id=source_idea_id,
            request_provenance=request_provenance,
        ),
        "safety": {
            "candidate_persistence_is_not_canon": True,
            "queue_presence_is_not_approval": True,
            "confidence_is_not_truth": True,
            "no_memory_canon_mutation": True,
            "no_promotion_records_created": True,
            "no_apply_promotion": True,
            "no_model_call": True,
            "no_story_check_call": True,
            "no_generated_prose": True,
        },
    }


def _omi_extraction_safety_flags() -> dict[str, bool]:
    return {
        "candidate_persistence_is_not_canon": True,
        "queue_presence_is_not_approval": True,
        "confidence_is_not_truth": True,
        "no_memory_canon_mutation": True,
        "no_promotion_records_created": True,
        "no_apply_promotion": True,
        "no_model_call": True,
        "no_story_check_call": True,
        "no_generated_prose": True,
    }


def _omi_marker_label_from_claim(claim: str) -> str:
    label = claim.strip()
    if len(label) > 1:
        label = label.rstrip(".")
    return label.strip()


def _omi_extracted_candidate_destination(candidate_type: str) -> str:
    if candidate_type == "storyform_context":
        return "storyform_context_candidate"
    if candidate_type in {"character", "location", "organization", "object", "story_fact"}:
        return "project_bible_candidate"
    return "planning_notes"


def _omi_extracted_candidate_container_type(candidate_type: str) -> str:
    if candidate_type == "storyform_context":
        return "storyform_context_candidate"
    if candidate_type in {"character", "location", "organization", "object", "story_fact"}:
        return "project_bible_candidate"
    return "planning_note"


def _build_omi_marker_candidate(
    *,
    candidate_type: str,
    marker_label: str,
    claim: str,
    source_excerpt: str,
    source_locator: str,
    line_number: int,
    char_start: int,
    char_end: int,
    line_char_start: int,
    line_char_end: int,
    raw_idea: str,
    source_idea_id: str | None,
    base_provenance: dict[str, Any],
) -> dict[str, Any] | None:
    label = _omi_marker_label_from_claim(claim)
    if not label:
        return None

    evidence = [
        {
            "source_type": "omi_raw_idea",
            "source_idea_id": source_idea_id,
            "source_excerpt": source_excerpt,
            "source_locator": source_locator,
            "line_number": line_number,
            "char_start": char_start,
            "char_end": char_end,
            "line_char_start": line_char_start,
            "line_char_end": line_char_end,
            "source_hash": _raw_idea_sha256(raw_idea),
            "owner_authored": True,
        }
    ]
    candidate_provenance = dict(base_provenance)
    candidate_provenance.update(
        {
            "candidate_type": candidate_type,
            "marker": marker_label,
            "line_number": line_number,
            "char_start": char_start,
            "char_end": char_end,
        }
    )
    candidate = {
        "candidate_type": candidate_type,
        "label": label,
        "extracted_claim": claim.strip(),
        "evidence": evidence,
        "provenance": candidate_provenance,
        "status": OMI_EXTRACTED_CANDIDATE_DEFAULT_STATUS,
        "owner_decision": _default_owner_decision(),
        "support_strength": "explicit_owner_marker",
        "support_label": OMI_EXTRACTION_SUPPORT_LABEL,
    }
    if candidate_type in OMI_EXTRACTED_ENTITY_NAME_TYPES:
        candidate["name"] = label
    return validate_omi_extracted_candidate(candidate)


def _extract_omi_candidates_by_markers(
    raw_idea: str,
    *,
    source_idea_id: str | None,
    request_provenance: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    base_provenance = _omi_extraction_provenance(
        raw_idea=raw_idea,
        source_idea_id=source_idea_id,
        request_provenance=request_provenance,
    )
    base_locator = _omi_raw_idea_source_locator(source_idea_id)
    candidates: list[dict[str, Any]] = []
    offset = 0

    for line_number, raw_line in enumerate(raw_idea.splitlines(keepends=True), start=1):
        line_text = raw_line.rstrip("\r\n")
        stripped_line = line_text.strip()
        line_start = offset
        offset += len(raw_line)
        if not stripped_line:
            continue

        match = OMI_EXPLICIT_MARKER_PATTERN.match(line_text)
        if match is None:
            continue

        claim = match.group("claim").strip()
        if not claim:
            continue

        marker = match.group("marker").casefold()
        candidate_type = OMI_EXPLICIT_MARKER_CANDIDATE_TYPES[marker]
        leading_ws = len(line_text) - len(line_text.lstrip())
        trailing_ws_end = len(line_text.rstrip())
        char_start = line_start + leading_ws
        char_end = line_start + trailing_ws_end
        source_locator = f"{base_locator}:L{line_number}:C{char_start}-{char_end}"
        candidate = _build_omi_marker_candidate(
            candidate_type=candidate_type,
            marker_label=match.group("marker"),
            claim=claim,
            source_excerpt=stripped_line,
            source_locator=source_locator,
            line_number=line_number,
            char_start=char_start,
            char_end=char_end,
            line_char_start=leading_ws,
            line_char_end=trailing_ws_end,
            raw_idea=raw_idea,
            source_idea_id=source_idea_id,
            base_provenance=base_provenance,
        )
        if candidate is not None:
            candidates.append(candidate)

    return candidates


def _omi_extracted_candidate_content(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "deterministic_omi_extraction",
        "extracted_candidate_type": candidate["candidate_type"],
        "label": candidate["label"],
        "extracted_claim": candidate["extracted_claim"],
        "evidence": candidate["evidence"],
        "provenance": candidate["provenance"],
        "owner_decision": candidate["owner_decision"],
        "status": candidate["status"],
        "support_strength": candidate.get("support_strength"),
        "support_label": candidate.get("support_label"),
        "candidate_first": True,
        "canon": False,
        "approved": False,
    }


def _persist_omi_extracted_candidates(
    project_name: str,
    *,
    source_idea_id: str | None,
    candidates: list[dict[str, Any]],
) -> tuple[list[str], str]:
    if not candidates:
        return [], "no_candidates_persisted"
    if source_idea_id is None:
        return [], "source_idea_required"

    persisted_candidate_ids: list[str] = []
    for candidate in candidates:
        persisted = create_omi_candidate(
            project_name,
            source_idea_id,
            _omi_extracted_candidate_container_type(candidate["candidate_type"]),
            _omi_extracted_candidate_content(candidate),
            _omi_extracted_candidate_destination(candidate["candidate_type"]),
            provenance=candidate["provenance"],
            evidence=candidate["evidence"],
        )
        persisted_candidate_ids.append(persisted["candidate_id"])

    return persisted_candidate_ids, "persisted"


def _omi_success_extraction_result(
    project_name: str,
    *,
    raw_idea: str,
    source_idea_id: str | None,
    candidates: list[dict[str, Any]],
    persist_candidates: bool,
    persisted_candidate_ids: list[str],
    persistence_status: str,
    request_provenance: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project_id": project_name,
        "extraction_status": "succeeded",
        "status": "succeeded",
        "explanation": (
            "Deterministic marker extraction found evidence-backed candidates "
            "for owner review."
        ),
        "source_idea_id": source_idea_id,
        "source_locator": _omi_raw_idea_source_locator(source_idea_id),
        "raw_idea_hash": _raw_idea_sha256(raw_idea),
        "candidate_types": sorted(OMI_EXTRACTED_CANDIDATE_TYPES),
        "candidates": candidates,
        "candidate_count": len(candidates),
        "persist_candidates": persist_candidates,
        "persisted_candidate_ids": persisted_candidate_ids,
        "persistence_status": persistence_status,
        "provenance": _omi_extraction_provenance(
            raw_idea=raw_idea,
            source_idea_id=source_idea_id,
            request_provenance=request_provenance,
        ),
        "safety": _omi_extraction_safety_flags(),
    }


def extract_omi_candidates_from_raw_idea(
    project_name: str,
    raw_idea: str,
    *,
    source_idea_id: str | None = None,
    persist_candidates: bool = False,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _safe_path_component(project_name, "project_name")
    if not isinstance(raw_idea, str):
        raise ValueError("OMI extraction raw_idea must be a string")
    if provenance is not None and not isinstance(provenance, dict):
        raise ValueError("OMI extraction provenance must be a JSON object")

    source_idea: dict[str, Any] | None = None
    if source_idea_id is not None:
        _safe_path_component(source_idea_id, "source_idea_id")
        source_idea = load_omi_idea(project_name, source_idea_id)

    submitted_raw_idea = raw_idea.strip()
    if source_idea is not None:
        source_raw_idea = source_idea.get("raw_idea")
        if not isinstance(source_raw_idea, str) or not source_raw_idea.strip():
            return _omi_empty_extraction_result(
                project_name,
                raw_idea="",
                source_idea_id=source_idea_id,
                extraction_status="fail_closed",
                explanation=(
                    "The referenced OMI idea has no usable raw idea text; "
                    "no evidence-backed candidates were extracted or persisted."
                ),
                persist_candidates=persist_candidates,
                request_provenance=provenance,
            )
        if submitted_raw_idea and submitted_raw_idea != source_raw_idea.strip():
            return _omi_empty_extraction_result(
                project_name,
                raw_idea=submitted_raw_idea,
                source_idea_id=source_idea_id,
                extraction_status="fail_closed",
                explanation=(
                    "The submitted raw idea does not match the referenced OMI idea "
                    "snapshot; no candidates were extracted or persisted."
                ),
                persist_candidates=persist_candidates,
                request_provenance=provenance,
            )
        submitted_raw_idea = source_raw_idea.strip()

    if not submitted_raw_idea:
        return _omi_empty_extraction_result(
            project_name,
            raw_idea="",
            source_idea_id=source_idea_id,
            extraction_status="empty",
            explanation=(
                "No raw idea text was provided; no evidence-backed candidates "
                "were extracted or persisted."
            ),
            persist_candidates=persist_candidates,
            request_provenance=provenance,
        )

    candidates = _extract_omi_candidates_by_markers(
        submitted_raw_idea,
        source_idea_id=source_idea_id,
        request_provenance=provenance,
    )
    if not candidates:
        return _omi_empty_extraction_result(
            project_name,
            raw_idea=submitted_raw_idea,
            source_idea_id=source_idea_id,
            extraction_status="fail_closed",
            explanation=(
                "No supported explicit OMI extraction markers with evidence were "
                "found; no candidates were extracted or persisted."
            ),
            persist_candidates=persist_candidates,
            request_provenance=provenance,
        )

    if persist_candidates:
        persisted_candidate_ids, persistence_status = _persist_omi_extracted_candidates(
            project_name,
            source_idea_id=source_idea_id,
            candidates=candidates,
        )
    else:
        persisted_candidate_ids = []
        persistence_status = "not_requested"

    return _omi_success_extraction_result(
        project_name,
        raw_idea=submitted_raw_idea,
        source_idea_id=source_idea_id,
        candidates=candidates,
        persist_candidates=persist_candidates,
        persisted_candidate_ids=persisted_candidate_ids,
        persistence_status=persistence_status,
        request_provenance=provenance,
    )


def create_omi_candidate(
    project_name: str,
    idea_id: str,
    candidate_type: str,
    candidate_content: dict[str, Any],
    destination: str,
    provenance: dict[str, Any] | None = None,
    evidence: list[Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(candidate_content, dict):
        raise ValueError("OMI candidate_content must be a JSON object")
    if evidence is not None and not isinstance(evidence, list):
        raise ValueError("OMI evidence must be a JSON array")

    _validate_omi_candidate_type(candidate_type)
    _validate_omi_destination(destination)
    idea = load_omi_idea(project_name, idea_id)

    ensure_omi_storage(project_name)
    candidate_id = _new_record_id("candidate")
    timestamp = _utc_now()
    candidate = {
        "candidate_id": candidate_id,
        "project_id": project_name,
        "idea_id": idea_id,
        "candidate_type": candidate_type,
        "candidate_content": candidate_content,
        "status": "candidate",
        "destination": destination,
        "provenance": _normalise_provenance(
            provenance,
            source_path=f"omi/ideas/{idea_id}.json",
            source_label="Manual OMI candidate",
        ),
        "evidence": evidence or [],
        "owner_decision": _default_owner_decision(),
        "promotion_status": {
            "eligible": False,
            "promotion_id": None,
            "blocked_reasons": [
                "owner approval required",
                "final confirmation required",
            ],
        },
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    _write_json_object(
        _omi_record_path(project_name, "candidates", candidate_id, "candidate_id"),
        candidate,
        "OMI candidate",
        overwrite=False,
    )

    idea["linked_candidate_ids"] = sorted(
        set(idea.get("linked_candidate_ids", [])) | {candidate_id}
    )
    idea["updated_at"] = timestamp
    _write_json_object(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        idea,
        "OMI idea",
        overwrite=True,
    )

    index = load_omi_index(project_name)
    index["idea_ids"] = sorted(set(index.get("idea_ids", [])) | {idea_id})
    index["candidate_ids"] = sorted(set(index.get("candidate_ids", [])) | {candidate_id})
    index["last_updated"] = timestamp
    save_omi_index(project_name, index)

    return candidate


def list_omi_candidates(
    project_name: str,
    idea_id: str | None = None,
) -> list[dict[str, Any]]:
    if idea_id is not None:
        _safe_path_component(idea_id, "idea_id")

    index = load_omi_index(project_name)
    candidates: list[dict[str, Any]] = []

    for candidate_id in index.get("candidate_ids", []):
        try:
            candidate = load_omi_candidate(project_name, candidate_id)
        except FileNotFoundError:
            continue
        if idea_id is None or candidate.get("idea_id") == idea_id:
            candidates.append(candidate)

    return candidates


def load_omi_candidate(project_name: str, candidate_id: str) -> dict[str, Any]:
    return _load_json_object_from_path(
        _omi_record_path(project_name, "candidates", candidate_id, "candidate_id"),
        "OMI candidate",
    )


def load_omi_promotion(project_name: str, promotion_id: str) -> dict[str, Any]:
    return _load_json_object_from_path(
        _omi_record_path(project_name, "promotions", promotion_id, "promotion_id"),
        "OMI promotion",
    )


def list_omi_promotions(
    project_name: str,
    candidate_id: str | None = None,
) -> list[dict[str, Any]]:
    if candidate_id is not None:
        _safe_path_component(candidate_id, "candidate_id")

    index = load_omi_index(project_name)
    promotions: list[dict[str, Any]] = []

    for promotion_id in index.get("promotion_ids", []):
        try:
            promotion = load_omi_promotion(project_name, promotion_id)
        except FileNotFoundError:
            continue
        if candidate_id is None or promotion.get("candidate_id") == candidate_id:
            promotions.append(promotion)

    return promotions


def validate_omi_promotion_request(
    project_name: str,
    candidate_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("OMI promotion request must be a JSON object")

    candidate = load_omi_candidate(project_name, candidate_id)
    readiness = is_omi_candidate_promotion_ready(candidate)
    if not readiness["ready"]:
        raise ValueError(
            "OMI candidate is not promotion ready: "
            + "; ".join(readiness["blocked_reasons"])
        )

    if payload.get("final_confirmation") is not True:
        raise ValueError("OMI promotion requires final_confirmation true")

    target_file = _validate_omi_promotion_target(payload.get("target_file"), "target_file")
    target_path = _validate_omi_promotion_target(payload.get("target_path"), "target_path")
    if target_file is None and target_path is None:
        raise ValueError("OMI promotion requires target_file or target_path")

    provenance = payload.get("provenance")
    if provenance is not None and not isinstance(provenance, dict):
        raise ValueError("OMI promotion provenance must be a JSON object")

    evidence = payload.get("evidence")
    if evidence is not None and not isinstance(evidence, list):
        raise ValueError("OMI promotion evidence must be a JSON array")

    return {
        "candidate": candidate,
        "target_file": target_file,
        "target_path": target_path,
        "provenance": provenance,
        "evidence": evidence,
    }


def create_omi_promotion_record(
    project_name: str,
    candidate_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    validated = validate_omi_promotion_request(project_name, candidate_id, payload)
    candidate = validated["candidate"]

    ensure_omi_storage(project_name)
    promotion_id = _new_record_id("promotion")
    timestamp = _utc_now()
    promotion = {
        "promotion_id": promotion_id,
        "project_id": project_name,
        "candidate_id": candidate_id,
        "destination": candidate["destination"],
        "owner_approval": {
            "decision": candidate["owner_decision"]["decision"],
            "approved": candidate["owner_decision"]["approved"],
            "approval_confirmed": candidate["owner_decision"]["approval_confirmed"],
            "decided_by": candidate["owner_decision"].get("decided_by"),
            "decided_at": candidate["owner_decision"].get("decided_at"),
            "final_confirmation": True,
        },
        "provenance": {
            "candidate": candidate["provenance"],
            "promotion_request": _normalise_provenance(
                validated["provenance"],
                source_path=f"omi/candidates/{candidate_id}.json",
                source_label="Manual OMI promotion record",
            ),
        },
        "evidence": validated["evidence"] if validated["evidence"] is not None else candidate.get("evidence", []),
        "source_snapshot": json.loads(json.dumps(candidate)),
        "target_file": validated["target_file"],
        "target_path": validated["target_path"],
        "created_at": timestamp,
        "confirmed_at": timestamp,
        "status": OMI_PROMOTION_RECORD_STATUS,
    }

    _write_json_object(
        _omi_record_path(project_name, "promotions", promotion_id, "promotion_id"),
        promotion,
        "OMI promotion",
        overwrite=False,
    )

    index = load_omi_index(project_name)
    index["candidate_ids"] = sorted(set(index.get("candidate_ids", [])) | {candidate_id})
    index["promotion_ids"] = sorted(set(index.get("promotion_ids", [])) | {promotion_id})
    index["last_updated"] = timestamp
    save_omi_index(project_name, index)

    return promotion


def update_omi_idea_decision(
    project_name: str,
    idea_id: str,
    owner_decision: dict[str, Any],
    status: str | None = None,
) -> dict[str, Any]:
    idea = load_omi_idea(project_name, idea_id)
    normalized_decision = validate_omi_owner_decision(owner_decision)
    next_status = _status_from_decision(
        idea.get("status", "draft"),
        normalized_decision,
        status,
    )
    validate_omi_status_transition(idea.get("status", "draft"), next_status)

    timestamp = _utc_after(idea.get("updated_at"))
    idea["owner_decision"] = _finalize_owner_decision(normalized_decision, timestamp)
    idea["status"] = next_status
    idea["updated_at"] = timestamp

    _write_json_object(
        _omi_record_path(project_name, "ideas", idea_id, "idea_id"),
        idea,
        "OMI idea",
        overwrite=True,
    )
    return idea


def update_omi_candidate_decision(
    project_name: str,
    candidate_id: str,
    owner_decision: dict[str, Any],
    status: str | None = None,
    destination: str | None = None,
) -> dict[str, Any]:
    candidate = load_omi_candidate(project_name, candidate_id)
    normalized_decision = validate_omi_owner_decision(owner_decision)
    next_status = _status_from_decision(
        candidate.get("status", "candidate"),
        normalized_decision,
        status,
    )
    validate_omi_status_transition(candidate.get("status", "candidate"), next_status)
    next_destination = (
        _validate_omi_destination(destination)
        if destination is not None
        else candidate.get("destination")
    )

    timestamp = _utc_after(candidate.get("updated_at"))
    candidate["owner_decision"] = _finalize_owner_decision(normalized_decision, timestamp)
    candidate["status"] = next_status
    candidate["destination"] = next_destination
    candidate["updated_at"] = timestamp
    candidate["promotion_status"] = {
        "eligible": False,
        "promotion_id": None,
        "blocked_reasons": [
            "promotion gate enforcement pending",
            "final confirmation required",
        ],
    }

    _write_json_object(
        _omi_record_path(project_name, "candidates", candidate_id, "candidate_id"),
        candidate,
        "OMI candidate",
        overwrite=True,
    )
    return candidate


def get_omi_summary(project_name: str) -> dict[str, Any]:
    return {
        "index": load_omi_index(project_name),
        "ideas": list_omi_ideas(project_name),
        "candidates": list_omi_candidates(project_name),
        "promotions": list_omi_promotions(project_name),
    }
