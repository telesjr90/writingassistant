import copy
import json
from pathlib import Path

from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_storage


def _as_path(project_dir):
    if isinstance(project_dir, Path):
        return project_dir
    return Path(project_dir)


def _candidate_path(project_dir, candidate_id):
    return candidate_storage.candidate_record_path(_as_path(project_dir), candidate_id)


def _validated_record_copy(record):
    validated = candidate_record.validate_candidate_record(record)
    return copy.deepcopy(validated)


def write_candidate_record(project_dir, record):
    validated = _validated_record_copy(record)
    candidate_path = _candidate_path(project_dir, validated["candidate_id"])
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(
        json.dumps(validated, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return copy.deepcopy(validated)


def read_candidate_record(project_dir, candidate_id):
    candidate_path = _candidate_path(project_dir, candidate_id)
    raw_text = candidate_path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("candidate record JSON is invalid") from exc
    if not isinstance(loaded, dict):
        raise ValueError("candidate record JSON must be an object")
    validated = candidate_record.validate_candidate_record(loaded)
    if validated["candidate_id"] != candidate_id:
        raise ValueError("candidate_id does not match requested record")
    return copy.deepcopy(validated)


def list_candidate_records(project_dir):
    storage_dir = candidate_storage.candidate_storage_dir(_as_path(project_dir))
    if not storage_dir.exists():
        return []

    records = []
    for entry in storage_dir.iterdir():
        if not entry.is_file():
            continue
        if entry.suffix != ".json":
            continue

        raw_text = entry.read_text(encoding="utf-8")
        try:
            loaded = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError("candidate record JSON is invalid") from exc
        if not isinstance(loaded, dict):
            raise ValueError("candidate record JSON must be an object")
        validated = candidate_record.validate_candidate_record(loaded)
        if entry.stem != validated["candidate_id"]:
            raise ValueError("candidate filename does not match record candidate_id")
        expected_path = _candidate_path(project_dir, validated["candidate_id"])
        if expected_path != entry:
            raise ValueError("candidate path must be inside storage directory")
        records.append(copy.deepcopy(validated))

    records.sort(key=lambda item: item["candidate_id"])
    return records


__all__ = ("write_candidate_record", "read_candidate_record", "list_candidate_records")
