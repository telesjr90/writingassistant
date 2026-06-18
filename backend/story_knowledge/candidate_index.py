import json
from pathlib import Path

from backend.story_knowledge import candidate_persistence
from backend.story_knowledge import candidate_storage

INDEX_SCHEMA_VERSION = 1
INDEX_KIND = "writer_assistant_candidate_index"
INDEX_SOURCE = "writer_assistant_candidates"
INDEX_SOURCE_OF_TRUTH = "writer_assistant/candidates"

_SUMMARY_FIELDS = (
    "candidate_id",
    "candidate_type",
    "status",
    "destination",
    "confidence",
    "source_document_ids",
    "evidence_count",
    "provenance_kind",
    "created_at",
    "updated_at",
)


def _empty_index() -> dict:
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "kind": INDEX_KIND,
        "source": INDEX_SOURCE,
        "candidate_count": 0,
        "candidate_ids": [],
        "candidates": [],
        "generated_from": {
            "source_of_truth": INDEX_SOURCE_OF_TRUTH,
            "index_is_derived": True,
        },
    }


def _candidate_summary(record: dict) -> dict:
    source_document_ids = set()
    locator = record.get("source_locator") or {}
    if locator.get("source_document_id"):
        source_document_ids.add(locator["source_document_id"])
    for item in record.get("evidence") or []:
        item_locator = item.get("source_locator") or {}
        if item_locator.get("source_document_id"):
            source_document_ids.add(item_locator["source_document_id"])
    return {
        "candidate_id": record["candidate_id"],
        "candidate_type": record["candidate_type"],
        "status": record["status"],
        "destination": record["destination"],
        "confidence": record["confidence"],
        "source_document_ids": sorted(source_document_ids),
        "evidence_count": len(record.get("evidence") or []),
        "provenance_kind": record["provenance"]["origin"],
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
    }


def _validate_sorted_string_list(values, label):
    if not isinstance(values, list):
        raise ValueError(f"{label} must be a list")
    previous = None
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"{label} must contain strings")
        if previous is not None and value < previous:
            raise ValueError(f"{label} must be sorted")
        previous = value
    return values


def _validate_candidate_summary(summary: dict) -> dict:
    if not isinstance(summary, dict):
        raise ValueError("candidate summary must be an object")
    for field in _SUMMARY_FIELDS:
        if field not in summary:
            raise ValueError(f"candidate summary missing {field}")
    _validate_sorted_string_list(summary["source_document_ids"], "source_document_ids")
    return summary


def _validate_candidate_index(index: dict) -> dict:
    if not isinstance(index, dict):
        raise ValueError("candidate index must be an object")

    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ValueError("candidate index schema_version is invalid")

    if index.get("kind") != INDEX_KIND:
        raise ValueError("candidate index kind is invalid")

    if index.get("source") != INDEX_SOURCE:
        raise ValueError("candidate index source is invalid")

    candidate_ids = index.get("candidate_ids")
    candidates = index.get("candidates")
    candidate_count = index.get("candidate_count")

    if not isinstance(candidate_count, int):
        raise ValueError("candidate_count must be an integer")

    candidate_ids = _validate_sorted_string_list(candidate_ids, "candidate_ids")

    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")

    if candidate_count != len(candidate_ids):
        raise ValueError("candidate_count does not match candidate_ids")

    if candidate_count != len(candidates):
        raise ValueError("candidate_count does not match candidates")

    previous = None
    summary_ids = []
    for summary in candidates:
        _validate_candidate_summary(summary)
        candidate_id = summary["candidate_id"]
        if previous is not None and candidate_id < previous:
            raise ValueError("candidates must be sorted by candidate_id")
        previous = candidate_id
        summary_ids.append(candidate_id)

    if summary_ids != candidate_ids:
        raise ValueError("candidate_ids must match candidate summaries")

    generated_from = index.get("generated_from")
    if not isinstance(generated_from, dict):
        raise ValueError("generated_from must be an object")
    if generated_from.get("index_is_derived") is not True:
        raise ValueError("generated_from.index_is_derived must be true")
    if generated_from.get("source_of_truth") != INDEX_SOURCE_OF_TRUTH:
        raise ValueError("generated_from.source_of_truth is invalid")

    return index


def _load_index(path: Path) -> dict:
    raw_text = path.read_text(encoding="utf-8")
    try:
        loaded = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("candidate index JSON is invalid") from exc
    if not isinstance(loaded, dict):
        raise ValueError("candidate index JSON must be an object")
    return _validate_candidate_index(loaded)


def _write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_candidate_index(project_dir: Path) -> dict:
    records = candidate_persistence.list_candidate_records(project_dir)
    if not records:
        return _empty_index()

    summaries = [_candidate_summary(record) for record in records]
    summaries.sort(key=lambda item: item["candidate_id"])
    candidate_ids = [item["candidate_id"] for item in summaries]

    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "kind": INDEX_KIND,
        "source": INDEX_SOURCE,
        "candidate_count": len(candidate_ids),
        "candidate_ids": candidate_ids,
        "candidates": summaries,
        "generated_from": {
            "source_of_truth": INDEX_SOURCE_OF_TRUTH,
            "index_is_derived": True,
        },
    }


def write_candidate_index(project_dir: Path) -> dict:
    index = build_candidate_index(project_dir)
    _validate_candidate_index(index)
    index_path = candidate_storage.candidate_index_path(project_dir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(index_path, index)
    return index


def read_candidate_index(project_dir: Path) -> dict:
    index_path = candidate_storage.candidate_index_path(project_dir)
    if not index_path.is_file():
        raise FileNotFoundError("candidate index file is missing")
    return _load_index(index_path)


__all__ = (
    "INDEX_SCHEMA_VERSION",
    "INDEX_KIND",
    "INDEX_SOURCE",
    "INDEX_SOURCE_OF_TRUTH",
    "build_candidate_index",
    "write_candidate_index",
    "read_candidate_index",
)
