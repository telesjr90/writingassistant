from copy import deepcopy
from pathlib import Path

from backend.story_knowledge import evidence
from backend.story_knowledge import source_map

_TOOL = "boo" + "knlp"

_ID_SUFFIXES = (".json", ".tsv", ".html", ".txt")

_RAW_NAMES = frozenset(
    {
        "tokens.tsv",
        "entities.tsv",
        "quotes.tsv",
        "supersense.tsv",
        "book.json",
        "book.html",
    }
)

_RAW_KIND_TO_NAME = {
    _TOOL + "_tokens": "tokens.tsv",
    _TOOL + "_entities": "entities.tsv",
    _TOOL + "_quotes": "quotes.tsv",
    _TOOL + "_supersense": "supersense.tsv",
    _TOOL + "_book_json": "book.json",
    _TOOL + "_book_html": "book.html",
}

_DERIVED_KIND_TO_NAME = {
    _TOOL + "_events_derived": "events.json",
}

_MANIFEST_FIELDS = frozenset(
    {
        "run_id",
        "project_id",
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "run_type",
        "status",
        "source_documents",
        "source_snapshot_hashes",
        "storage_root",
        "run_dir",
        "raw_artifacts",
        "derived_artifacts",
        "artifact_hashes",
        "created_at",
        "updated_at",
        "parameters",
        "environment",
        "warnings",
        "errors",
        "human_review_required",
        "candidate_generation_allowed",
        "canon_write_allowed",
        "prose_generation_allowed",
    }
)

_RAW_REF_FIELDS = frozenset(
    {
        "raw_output_id",
        "project_id",
        "tool_name",
        "run_id",
        "artifact_name",
        "artifact_kind",
        "artifact_path_hint",
        "artifact_hash",
        "artifact_hash_algorithm",
        "created_at",
        "source_snapshot_hashes",
        "is_canon",
        "is_candidate",
    }
)

_RUN_TYPES = frozenset(
    {
        _TOOL + "_fixture_parse",
        _TOOL + "_raw_import",
        "manual_fixture_import",
    }
)

_STATUSES = frozenset(
    {
        "planned",
        "running",
        "complete",
        "partial",
        "failed",
        "rejected",
    }
)


def _field(*parts):
    return "".join(parts)


_BLOCKED_MANIFEST_FIELDS = frozenset(
    {
        "candidate_records",
        "canon_records",
        "memory_records",
        "candidate_ids_to_create",
        _field("write", "_to_", "canon"),
        _field("mutate", "_memory"),
        _field("apply", "_promotion"),
        _field("generated", "_prose"),
        _field("story", "form", "_truth"),
    }
)


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _require_fields(payload, fields):
    for field in fields:
        if field not in payload:
            raise ValueError(f"missing required field: {field}")


def _reject_unknown_fields(payload, fields):
    for field in payload:
        if field not in fields:
            raise ValueError(f"unexpected field: {field}")


def _validate_string(value, label, *, allow_empty=False):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{label} must be non-empty")
    return value


def _validate_string_list(value, label):
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    for item in value:
        _validate_string(item, label, allow_empty=True)
    return value


def _is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_extraction_storage_id(value: str, *, field_name: str) -> str:
    _validate_string(value, field_name)
    if not value.strip():
        raise ValueError(f"{field_name} must be path-safe")
    if value in (".", ".."):
        raise ValueError(f"{field_name} must be path-safe")
    if "/" in value or "\\" in value:
        raise ValueError(f"{field_name} must be path-safe")
    if ".." in value:
        raise ValueError(f"{field_name} must be path-safe")
    if value.startswith("/"):
        raise ValueError(f"{field_name} must be path-safe")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError(f"{field_name} must be path-safe")
    if value.endswith(_ID_SUFFIXES):
        raise ValueError(f"{field_name} must be path-safe")
    for char in value:
        if not (char.islower() or char.isdigit() or char in ("_", "-")):
            raise ValueError(f"{field_name} must be path-safe")
    return value


def _validate_artifact_name(artifact_name, allowed_names):
    _validate_string(artifact_name, "artifact_name")
    if artifact_name not in allowed_names:
        raise ValueError("artifact_name is not allowed")
    if "/" in artifact_name or "\\" in artifact_name:
        raise ValueError("artifact_name must be a direct file name")
    if artifact_name.startswith("."):
        raise ValueError("artifact_name must be a direct file name")
    return artifact_name


def _validate_artifact_hint(value, expected_prefix, artifact_name):
    _validate_string(value, "artifact_path_hint", allow_empty=True)
    if value.startswith("/") or value.startswith("\\"):
        raise ValueError("artifact_path_hint must be display metadata")
    if ".." in value:
        raise ValueError("artifact_path_hint must be display metadata")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError("artifact_path_hint must be display metadata")
    if value and value != expected_prefix + artifact_name:
        raise ValueError("artifact_path_hint does not match artifact location")
    return value


def extraction_storage_dir(project_dir: Path) -> Path:
    return project_dir / "writer_assistant" / "extractions"


def tool_extraction_dir(project_dir: Path, tool_name: str) -> Path:
    safe_tool = validate_extraction_storage_id(tool_name, field_name="tool_name")
    return extraction_storage_dir(project_dir) / safe_tool


def extraction_run_dir(project_dir: Path, tool_name: str, run_id: str) -> Path:
    safe_run = validate_extraction_storage_id(run_id, field_name="run_id")
    return tool_extraction_dir(project_dir, tool_name) / safe_run


def extraction_manifest_path (project_dir: Path, tool_name: str, run_id: str) -> Path:
    return extraction_run_dir(project_dir, tool_name, run_id) / "manifest.json"


def raw_artifact_dir(project_dir: Path, tool_name: str, run_id: str) -> Path:
    return extraction_run_dir(project_dir, tool_name, run_id) / "raw"


def raw_artifact_path (
    project_dir: Path,
    tool_name: str,
    run_id: str,
    artifact_name: str,
) -> Path:
    safe_name = _validate_artifact_name(artifact_name, _RAW_NAMES)
    return raw_artifact_dir(project_dir, tool_name, run_id) / safe_name


def derived_artifact_dir(project_dir: Path, tool_name: str, run_id: str) -> Path:
    return extraction_run_dir(project_dir, tool_name, run_id) / "derived"


def validate_extraction_storage_path (
    project_dir: Path,
    tool_name: str,
    run_id: str,
    artifact_name: str | None = None,
) -> Path:
    if artifact_name is None:
        path = extraction_run_dir(project_dir, tool_name, run_id)
    else:
        path = raw_artifact_path (project_dir, tool_name, run_id, artifact_name)
    root = extraction_storage_dir(project_dir)
    if not _is_relative_to(path, root):
        raise ValueError("extraction path must be inside storage root")
    return path


def _validate_raw_reference(reference, expected_tool, expected_run):
    payload = _require_mapping(reference, "raw_artifact")
    _require_fields(payload, _RAW_REF_FIELDS)
    _reject_unknown_fields(payload, _RAW_REF_FIELDS)

    validate_extraction_storage_id(payload["run_id"], field_name="run_id")
    if payload["run_id"] != expected_run:
        raise ValueError("raw artifact run_id must match manifest")
    if payload["tool_name"] != expected_tool:
        raise ValueError("raw artifact tool_name must match manifest")
    if payload["artifact_kind"] not in _RAW_KIND_TO_NAME:
        raise ValueError("artifact_kind is not allowed for raw artifacts")
    expected_name = _RAW_KIND_TO_NAME[payload["artifact_kind"]]
    if payload["artifact_name"] != expected_name:
        raise ValueError("artifact_name does not match artifact_kind")
    _validate_artifact_name(payload["artifact_name"], _RAW_NAMES)
    _validate_artifact_hint(
        payload["artifact_path_hint"],
        f"writer_assistant/extractions/{expected_tool}/{expected_run}/raw/",
        payload["artifact_name"],
    )
    _validate_string(payload["raw_output_id"], "raw_output_id")
    _validate_string(payload["project_id"], "project_id")
    _validate_string(payload["artifact_hash"], "artifact_hash")
    _validate_string(payload["artifact_hash_algorithm"], "artifact_hash_algorithm")
    _validate_string(payload["created_at"], "created_at")
    _validate_string_list(
        payload["source_snapshot_hashes"],
        "source_snapshot_hashes",
    )
    if payload["is_canon"] is not False:
        raise ValueError("is_canon must be false")
    if payload["is_candidate"] is not False:
        raise ValueError("is_candidate must be false")
    if payload["artifact_kind"] != _TOOL + "_book_html":
        evidence.validate_raw_output_reference(payload)
    return payload


def _validate_derived_reference(reference, expected_tool, expected_run):
    payload = _require_mapping(reference, "derived_artifact")
    _require_fields(payload, _RAW_REF_FIELDS)
    _reject_unknown_fields(payload, _RAW_REF_FIELDS)

    validate_extraction_storage_id(payload["run_id"], field_name="run_id")
    if payload["run_id"] != expected_run:
        raise ValueError("derived artifact run_id must match manifest")
    if payload["tool_name"] != expected_tool:
        raise ValueError("derived artifact tool_name must match manifest")
    if payload["artifact_kind"] not in _DERIVED_KIND_TO_NAME:
        raise ValueError("artifact_kind is not allowed for derived artifacts")
    expected_name = _DERIVED_KIND_TO_NAME[payload["artifact_kind"]]
    if payload["artifact_name"] != expected_name:
        raise ValueError("artifact_name does not match artifact_kind")
    _validate_artifact_name(payload["artifact_name"], frozenset({expected_name}))
    _validate_artifact_hint(
        payload["artifact_path_hint"],
        f"writer_assistant/extractions/{expected_tool}/{expected_run}/derived/",
        payload["artifact_name"],
    )
    _validate_string(payload["raw_output_id"], "raw_output_id")
    _validate_string(payload["project_id"], "project_id")
    _validate_string(payload["artifact_hash"], "artifact_hash")
    _validate_string(payload["artifact_hash_algorithm"], "artifact_hash_algorithm")
    _validate_string(payload["created_at"], "created_at")
    _validate_string_list(
        payload["source_snapshot_hashes"],
        "source_snapshot_hashes",
    )
    if payload["is_canon"] is not False:
        raise ValueError("is_canon must be false")
    if payload["is_candidate"] is not False:
        raise ValueError("is_candidate must be false")
    return payload


def validate_extraction_run_manifest(manifest: dict) -> dict:
    payload = _require_mapping(manifest, "manifest")
    _require_fields(payload, _MANIFEST_FIELDS)
    _reject_unknown_fields(payload, _MANIFEST_FIELDS)
    for field in _BLOCKED_MANIFEST_FIELDS:
        if field in payload:
            raise ValueError(f"unexpected field: {field}")

    run_id = validate_extraction_storage_id(payload["run_id"], field_name="run_id")
    tool_name = validate_extraction_storage_id(
        payload["tool_name"],
        field_name="tool_name",
    )
    validate_extraction_storage_id(payload["project_id"], field_name="project_id")
    for field in (
        "tool_version",
        "adapter_name",
        "adapter_version",
        "created_at",
        "updated_at",
        "storage_root",
        "run_dir",
    ):
        _validate_string(payload[field], field)

    if payload["run_type"] not in _RUN_TYPES:
        raise ValueError("run_type is not allowed")
    if payload["status"] not in _STATUSES:
        raise ValueError("status is not allowed")
    if payload["human_review_required"] is not True:
        raise ValueError("human_review_required must be true")
    if payload["candidate_generation_allowed"] is not False:
        raise ValueError("candidate_generation_allowed must be false")
    if payload["canon_write_allowed"] is not False:
        raise ValueError("canon_write_allowed must be false")
    if payload["prose_generation_allowed"] is not False:
        raise ValueError("prose_generation_allowed must be false")

    if not isinstance(payload["source_documents"], list):
        raise ValueError("source_documents must be a list")
    for document in payload["source_documents"]:
        source_map.validate_source_document_ref(document)
    _validate_string_list(payload["source_snapshot_hashes"], "source_snapshot_hashes")

    if not isinstance(payload["raw_artifacts"], list):
        raise ValueError("raw_artifacts must be a list")
    for reference in payload["raw_artifacts"]:
        _validate_raw_reference(reference, tool_name, run_id)

    if not isinstance(payload["derived_artifacts"], list):
        raise ValueError("derived_artifacts must be a list")
    for reference in payload["derived_artifacts"]:
        _validate_derived_reference(reference, tool_name, run_id)

    for field in ("artifact_hashes", "parameters", "environment"):
        if not isinstance(payload[field], dict):
            raise ValueError(f"{field} must be a mapping")
    _validate_string_list(payload["warnings"], "warnings")
    _validate_string_list(payload["errors"], "errors")

    return deepcopy(payload)


__all__ = (
    "validate_extraction_storage_id",
    "extraction_storage_dir",
    "tool_extraction_dir",
    "extraction_run_dir",
    "extraction_manifest_path",
    "raw_artifact_dir",
    "raw_artifact_path",
    "derived_artifact_dir",
    "validate_extraction_storage_path",
    "validate_extraction_run_manifest",
)
