"""Pure path helpers for Writer Assistant Core candidate storage locations."""

from pathlib import Path


def _as_path(project_dir):
    if not isinstance(project_dir, Path):
        project_dir = Path(project_dir)
    return project_dir


def _validate_candidate_id(candidate_id):
    if not isinstance(candidate_id, str):
        raise ValueError("candidate_id must be a string")
    if not candidate_id or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty path-safe identifier")
    if candidate_id in (".", ".."):
        raise ValueError("candidate_id must be path-safe")
    if "/" in candidate_id or "\\" in candidate_id:
        raise ValueError("candidate_id must be path-safe")
    if ".." in candidate_id:
        raise ValueError("candidate_id must be path-safe")
    if candidate_id.startswith("/"):
        raise ValueError("candidate_id must be path-safe")
    if len(candidate_id) >= 2 and candidate_id[1] == ":" and candidate_id[0].isalpha():
        raise ValueError("candidate_id must be path-safe")
    if candidate_id.endswith(".json"):
        raise ValueError("candidate_id must be path-safe")
    return candidate_id


def _is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def candidate_storage_dir(project_dir):
    return _as_path(project_dir) / "writer_assistant" / "candidates"


def candidate_index_path(project_dir):
    return _as_path(project_dir) / "writer_assistant" / "index.json"


def candidate_record_path(project_dir, candidate_id):
    safe_id = _validate_candidate_id(candidate_id)
    return candidate_storage_dir(project_dir) / f"{safe_id}.json"


def validate_candidate_storage_path(project_dir, candidate_id):
    path = candidate_record_path(project_dir, candidate_id)
    storage_dir = candidate_storage_dir(project_dir)
    if not _is_relative_to(path, storage_dir):
        raise ValueError("candidate path must be inside storage directory")
    return path


__all__ = (
    "candidate_storage_dir",
    "candidate_index_path",
    "candidate_record_path",
    "validate_candidate_storage_path",
)
