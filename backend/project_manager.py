from __future__ import annotations

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

MAX_PROJECT_TITLE_LENGTH = 160
MAX_PROJECT_ID_LENGTH = 64
MAX_PROJECT_ID_COLLISION_ATTEMPTS = 1000

PROJECT_CREATION_METHOD_BLANK = "blank"

_PROJECT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_PROJECT_ID_INVALID_CHAR_RUN = re.compile(r"[^a-z0-9]+")
_PROJECT_ID_REPEAT_HYPHEN = re.compile(r"-{2,}")

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


def save_scene(project_name: str, scene_id: str, content: str) -> None:
    path = _scene_path(project_name, scene_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_scenes(project_name: str) -> list[str]:
    scenes_dir = _project_dir(project_name) / "scenes"
    if not scenes_dir.exists():
        return []

    return [path.stem for path in sorted(scenes_dir.glob("*.md")) if path.is_file()]


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
