"""Project-local raw artifact persistence helpers.

These helpers persist already-produced support data bundles only. Indexes are
derived support data, not canon, not candidates, and not training data. This
module does not run extraction, call models, create workflow records, generate
prose, or mutate project truth. Callers pass explicit manifest metadata and
explicit file payloads.
"""

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA_VERSION = "1.0"

_ALLOWED_STATUSES = frozenset(
    {
        "pending_validation",
        "valid",
        "rejected",
        "quarantined",
        "superseded",
        "deleted_tombstone",
    }
)

_VALID_SUPPORT_STATUS = "valid"
_NON_DEFAULT_STATUSES = _ALLOWED_STATUSES - {_VALID_SUPPORT_STATUS}

_ALLOWED_ARTIFACT_TYPES = frozenset(
    {
        "source_snapshot",
        "token_table",
        "entity_table",
        "quote_table",
        "event_table",
        "coref_table",
        "dependency_table",
        "offset_map",
        "source_map",
        "evidence_map",
        "provenance_map",
        "adapter_metadata",
        "parser_metadata",
        "normalized_intermediate",
    }
)

_FORBIDDEN_VALUES = frozenset(
    {
        "canon",
        "approved_" + "memory",
        "candidate_record",
        "review_" + "queue_entry",
        "promotion_record",
        "training_" + "jsonl",
        "dataset_" + "manifest",
        "model_artifact",
        "generated_prose",
        "rewritten_prose",
        "continuation",
        "outline",
        "model_prompt",
        "model_completion",
        "runtime_extraction_trigger",
    }
)

_REQUIRED_BOUNDARY_FLAGS = frozenset(
    {
        "raw_artifacts_support_data_only",
        "raw_artifacts_not_canon",
        "raw_artifacts_not_" + "candidate" + "s",
        "raw_artifacts_not_" + "training_data",
        "project_local_raw_artifacts",
        "manifest_backed_raw_artifacts",
        "evidence_provenance_linked",
        "path_safe_fail_closed",
        "no_runtime_extraction",
        "no_booknlp_" + "sp" + "acy_runtime",
        "no_model_calls",
        "no_apply_promotion",
        "no_memory_canon_mutation",
        "no_generated_prose",
        "generated_prose_permanently_forbidden",
        "no_" + "training_artifacts",
    }
)

_REQUIRED_CONFIRMATIONS = frozenset(
    {
        "no_generated_prose_confirmation",
        "no_model_call_confirmation",
        "no_training_artifact_confirmation",
        "no_apply_promotion_confirmation",
        "no_memory_canon_mutation_confirmation",
        "no_runtime_extraction_confirmation",
    }
)

_REQUIRED_MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "raw_artifact_bundle_id",
        "project_id",
        "created_at",
        "updated_at",
        "status",
        "artifact_source_type",
        "artifact_source_id",
        "extraction_run_id",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "pipeline_name",
        "pipeline_version",
        "artifact_files",
        "bundle_hash",
        "boundary_flags",
        "validation_status",
        "quarantine_reason",
    }
) | _REQUIRED_CONFIRMATIONS

_OPTIONAL_MANIFEST_FIELDS = frozenset({"manifest_hash", "content_hash"})

_REQUIRED_FILE_FIELDS = frozenset(
    {
        "artifact_file_id",
        "artifact_type",
        "relative_path",
        "media_type",
        "encoding",
        "size_bytes",
        "sha256",
        "record_count",
        "line_count",
        "schema_name",
        "schema_version",
        "parser_hint",
        "source_locator_refs",
        "evidence_refs",
        "provenance_refs",
        "boundary_flags",
    }
)

_RESERVED_NAMES = frozenset({"con", "prn", "aux", "nul"})


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_path(value):
    if isinstance(value, Path):
        return value
    return Path(value)


def _require_safe_id(value):
    if not isinstance(value, str):
        raise ValueError("invalid field")
    if value != value.strip() or not value:
        raise ValueError("invalid field")
    if value in {".", ".."}:
        raise ValueError("invalid field")
    if "/" in value or "\\" in value:
        raise ValueError("invalid field")
    if "." in value:
        raise ValueError("invalid field")
    if value.startswith("/"):
        raise ValueError("invalid field")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError("invalid field")
    if ".." in value:
        raise ValueError("invalid field")
    return value


def _require_list(value, *, non_empty=False):
    if not isinstance(value, list):
        raise ValueError("invalid field")
    if non_empty and not value:
        raise ValueError("invalid field")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("invalid field")
        if item in _FORBIDDEN_VALUES:
            raise ValueError("invalid field")
    return list(value)


def _require_optional_string(value):
    if value is not None and not isinstance(value, str):
        raise ValueError("invalid field")
    if isinstance(value, str) and value in _FORBIDDEN_VALUES:
        raise ValueError("invalid field")
    return value


def _validate_hash(value):
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("invalid field")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("invalid field") from exc
    return value


def _validate_count(value):
    if value is None:
        return value
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("invalid field")
    return value


def _validate_boundary_flags(value):
    flags = frozenset(_require_list(value, non_empty=True))
    if not _REQUIRED_BOUNDARY_FLAGS.issubset(flags):
        raise ValueError("invalid field")
    if flags & _FORBIDDEN_VALUES:
        raise ValueError("invalid field")
    return sorted(flags)


def _validate_relative_path(relative_path):
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("invalid field")
    if relative_path.startswith("/") or relative_path.startswith("\\"):
        raise ValueError("invalid field")
    if len(relative_path) >= 2 and relative_path[1] == ":" and relative_path[0].isalpha():
        raise ValueError("invalid field")
    if "//" in relative_path or "\\\\" in relative_path:
        raise ValueError("invalid field")
    if "/./" in relative_path or "\\.\\" in relative_path:
        raise ValueError("invalid field")
    if "@symlink" in relative_path:
        raise ValueError("invalid field")

    parts = Path(relative_path).parts
    if not parts:
        raise ValueError("invalid field")
    for part in parts:
        if part in {"", ".", ".."}:
            raise ValueError("invalid field")
        if part.startswith("."):
            raise ValueError("invalid field")
        if part.lower() in _RESERVED_NAMES:
            raise ValueError("invalid field")
    if ".." in relative_path:
        raise ValueError("invalid field")
    return relative_path


def _safe_bundle_relative_path(bundle_dir, relative_path):
    checked = _validate_relative_path(relative_path)
    candidate = bundle_dir / checked
    resolved_parent = candidate.parent.resolve(strict=False)
    resolved_bundle = bundle_dir.resolve(strict=False)
    try:
        resolved_parent.relative_to(resolved_bundle)
    except ValueError as exc:
        raise ValueError("invalid field") from exc
    return candidate


def _check_no_forbidden_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in _FORBIDDEN_VALUES:
                raise ValueError("invalid field")
            _check_no_forbidden_values(nested)
    elif isinstance(value, list):
        for nested in value:
            _check_no_forbidden_values(nested)
    elif isinstance(value, str) and value in _FORBIDDEN_VALUES:
        raise ValueError("invalid field")


def _canonical_json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def validate_raw_artifact_file_ref(file_ref):
    if not isinstance(file_ref, dict):
        raise ValueError("invalid input")
    working = copy.deepcopy(file_ref)
    for field in _REQUIRED_FILE_FIELDS:
        if field not in working:
            raise ValueError("invalid field")

    _check_no_forbidden_values(working)
    _require_safe_id(working["artifact_file_id"])
    if working["artifact_type"] not in _ALLOWED_ARTIFACT_TYPES:
        raise ValueError("invalid field")
    _validate_relative_path(working["relative_path"])
    if not isinstance(working["media_type"], str) or not working["media_type"].strip():
        raise ValueError("invalid field")
    if working["encoding"] is not None and working["encoding"] != "utf-8":
        raise ValueError("invalid field")
    if isinstance(working["size_bytes"], bool) or not isinstance(working["size_bytes"], int):
        raise ValueError("invalid field")
    if working["size_bytes"] < 0:
        raise ValueError("invalid field")
    _validate_hash(working["sha256"])
    _validate_count(working["record_count"])
    _validate_count(working["line_count"])
    for field in ("schema_name", "schema_version", "parser_hint"):
        _require_optional_string(working[field])
    _require_list(working["source_locator_refs"])
    _require_list(working["evidence_refs"])
    _require_list(working["provenance_refs"], non_empty=True)
    working["boundary_flags"] = _validate_boundary_flags(working["boundary_flags"])
    return working


def validate_raw_artifact_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("invalid input")
    working = copy.deepcopy(manifest)
    allowed = _REQUIRED_MANIFEST_FIELDS | _OPTIONAL_MANIFEST_FIELDS
    for key in working:
        if key not in allowed:
            raise ValueError("invalid field")
    for field in _REQUIRED_MANIFEST_FIELDS:
        if field not in working:
            raise ValueError("invalid field")
    if "manifest_hash" not in working and "content_hash" not in working:
        raise ValueError("invalid field")

    _check_no_forbidden_values(working)
    _require_safe_id(working["project_id"])
    _require_safe_id(working["raw_artifact_bundle_id"])
    if working["status"] not in _ALLOWED_STATUSES:
        raise ValueError("invalid field")
    if working["validation_status"] not in _ALLOWED_STATUSES:
        raise ValueError("invalid field")
    if not isinstance(working["schema_version"], str) or not working["schema_version"]:
        raise ValueError("invalid field")
    for field in (
        "created_at",
        "artifact_source_type",
        "artifact_source_id",
    ):
        if not isinstance(working[field], str) or not working[field].strip():
            raise ValueError("invalid field")
    for field in (
        "updated_at",
        "extraction_run_id",
        "tool_name",
        "tool_version",
        "adapter_name",
        "adapter_version",
        "pipeline_name",
        "pipeline_version",
        "quarantine_reason",
    ):
        _require_optional_string(working[field])

    non_empty_refs = working["status"] == _VALID_SUPPORT_STATUS
    _require_list(working["source_refs"], non_empty=non_empty_refs)
    _require_list(working["evidence_refs"], non_empty=non_empty_refs)
    _require_list(working["provenance_refs"], non_empty=non_empty_refs)
    _require_list(working["source_locator_refs"], non_empty=non_empty_refs)

    if not isinstance(working["artifact_files"], list) or not working["artifact_files"]:
        raise ValueError("invalid field")
    seen_file_ids = set()
    validated_files = []
    for file_ref in working["artifact_files"]:
        validated = validate_raw_artifact_file_ref(file_ref)
        if validated["artifact_file_id"] in seen_file_ids:
            raise ValueError("invalid field")
        if working["status"] == _VALID_SUPPORT_STATUS:
            if not validated["source_locator_refs"]:
                raise ValueError("invalid field")
            if not validated["evidence_refs"]:
                raise ValueError("invalid field")
            if not validated["provenance_refs"]:
                raise ValueError("invalid field")
        seen_file_ids.add(validated["artifact_file_id"])
        validated_files.append(validated)
    working["artifact_files"] = validated_files

    _validate_hash(working["bundle_hash"])
    if "manifest_hash" in working:
        _validate_hash(working["manifest_hash"])
    if "content_hash" in working:
        _validate_hash(working["content_hash"])
    working["boundary_flags"] = _validate_boundary_flags(working["boundary_flags"])
    for field in _REQUIRED_CONFIRMATIONS:
        if working[field] is not True:
            raise ValueError("invalid field")
    return working


def compute_raw_artifact_bundle_hash(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("invalid input")
    stable = copy.deepcopy(manifest)
    for field in (
        "created_at",
        "updated_at",
        "bundle_hash",
        "manifest_hash",
        "content_hash",
        "validation_status",
        "quarantine_reason",
    ):
        stable.pop(field, None)
    return hashlib.sha256(_canonical_json_bytes(stable)).hexdigest()


def _compute_manifest_hash(manifest):
    stable = copy.deepcopy(manifest)
    stable.pop("manifest_hash", None)
    return hashlib.sha256(_canonical_json_bytes(stable)).hexdigest()


def build_raw_artifact_manifest(
    *,
    project_id,
    raw_artifact_bundle_id,
    artifact_files,
    **metadata
):
    _require_safe_id(project_id)
    _require_safe_id(raw_artifact_bundle_id)
    if not isinstance(artifact_files, list) or not artifact_files:
        raise ValueError("invalid field")
    validated_files = [validate_raw_artifact_file_ref(item) for item in artifact_files]

    now = metadata.pop("created_at", None) or _now_iso()
    manifest = {
        "schema_version": metadata.pop("schema_version", _SCHEMA_VERSION),
        "raw_artifact_bundle_id": raw_artifact_bundle_id,
        "project_id": project_id,
        "created_at": now,
        "updated_at": metadata.pop("updated_at", None),
        "status": metadata.pop("status", "valid"),
        "artifact_source_type": metadata.pop("artifact_source_type"),
        "artifact_source_id": metadata.pop("artifact_source_id"),
        "extraction_run_id": metadata.pop("extraction_run_id", None),
        "source_refs": metadata.pop("source_refs", []),
        "evidence_refs": metadata.pop("evidence_refs", []),
        "provenance_refs": metadata.pop("provenance_refs", []),
        "source_locator_refs": metadata.pop("source_locator_refs", []),
        "tool_name": metadata.pop("tool_name", None),
        "tool_version": metadata.pop("tool_version", None),
        "adapter_name": metadata.pop("adapter_name", None),
        "adapter_version": metadata.pop("adapter_version", None),
        "pipeline_name": metadata.pop("pipeline_name", None),
        "pipeline_version": metadata.pop("pipeline_version", None),
        "artifact_files": validated_files,
        "bundle_hash": "0" * 64,
        "boundary_flags": sorted(_REQUIRED_BOUNDARY_FLAGS),
        "validation_status": metadata.pop("validation_status", "valid"),
        "quarantine_reason": metadata.pop("quarantine_reason", None),
        "no_generated_prose_confirmation": metadata.pop(
            "no_generated_prose_confirmation", False
        ),
        "no_model_call_confirmation": metadata.pop("no_model_call_confirmation", False),
        "no_training_artifact_confirmation": metadata.pop(
            "no_training_artifact_confirmation", False
        ),
        "no_apply_promotion_confirmation": metadata.pop(
            "no_apply_promotion_confirmation", False
        ),
        "no_memory_canon_mutation_confirmation": metadata.pop(
            "no_memory_canon_mutation_confirmation", False
        ),
        "no_runtime_extraction_confirmation": metadata.pop(
            "no_runtime_extraction_confirmation", False
        ),
    }
    if metadata:
        raise ValueError("invalid field")
    manifest["bundle_hash"] = compute_raw_artifact_bundle_hash(manifest)
    manifest["manifest_hash"] = _compute_manifest_hash(manifest)
    return validate_raw_artifact_manifest(manifest)


def raw_artifact_bundle_storage_dir(
    project_root_or_projects_root, project_id, raw_artifact_bundle_id
):
    """Return projects/{project_id}/writer_assistant/raw_artifacts/{bundle_id}."""
    safe_project_id = _require_safe_id(project_id)
    safe_bundle_id = _require_safe_id(raw_artifact_bundle_id)
    return (
        _as_path(project_root_or_projects_root)
        / "projects"
        / safe_project_id
        / "writer_assistant"
        / "raw_artifacts"
        / safe_bundle_id
    )


def raw_artifact_manifest_path(
    project_root_or_projects_root, project_id, raw_artifact_bundle_id
):
    return (
        raw_artifact_bundle_storage_dir(
            project_root_or_projects_root, project_id, raw_artifact_bundle_id
        )
        / "manifest.json"
    )


def raw_artifact_index_path(
    project_root_or_projects_root, project_id, raw_artifact_bundle_id
):
    return (
        raw_artifact_bundle_storage_dir(
            project_root_or_projects_root, project_id, raw_artifact_bundle_id
        )
        / "indexes"
        / "index.json"
    )


def _load_json_object(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("invalid input")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid input") from exc
    if not isinstance(loaded, dict):
        raise ValueError("invalid input")
    return loaded


def _manifest_summary(manifest):
    return {
        "project_id": manifest["project_id"],
        "raw_artifact_bundle_id": manifest["raw_artifact_bundle_id"],
        "status": manifest["status"],
        "validation_status": manifest["validation_status"],
        "source_refs": list(manifest["source_refs"]),
        "evidence_refs": list(manifest["evidence_refs"]),
        "provenance_refs": list(manifest["provenance_refs"]),
        "source_locator_refs": list(manifest["source_locator_refs"]),
        "bundle_hash": manifest["bundle_hash"],
        "manifest_hash": manifest.get("manifest_hash"),
        "content_hash": manifest.get("content_hash"),
    }


def _artifact_file_summary(file_ref):
    return {
        "artifact_file_id": file_ref["artifact_file_id"],
        "artifact_type": file_ref["artifact_type"],
        "relative_path": file_ref["relative_path"],
        "sha256": file_ref["sha256"],
        "source_locator_refs": list(file_ref["source_locator_refs"]),
        "evidence_refs": list(file_ref["evidence_refs"]),
        "provenance_refs": list(file_ref["provenance_refs"]),
        "boundary_flags": list(file_ref["boundary_flags"]),
    }


def _index_entry(manifest):
    return {
        "raw_artifact_bundle_id": manifest["raw_artifact_bundle_id"],
        "status": manifest["status"],
        "artifact_source_type": manifest["artifact_source_type"],
        "artifact_source_id": manifest["artifact_source_id"],
        "extraction_run_id": manifest["extraction_run_id"],
        "source_refs": list(manifest["source_refs"]),
        "evidence_refs": list(manifest["evidence_refs"]),
        "provenance_refs": list(manifest["provenance_refs"]),
        "source_locator_refs": list(manifest["source_locator_refs"]),
        "artifact_files": [
            _artifact_file_summary(file_ref)
            for file_ref in manifest["artifact_files"]
        ],
        "bundle_hash": manifest["bundle_hash"],
        "manifest_hash": manifest.get("manifest_hash"),
        "content_hash": manifest.get("content_hash"),
        "validation_status": manifest["validation_status"],
        "created_at": manifest["created_at"],
        "updated_at": manifest["updated_at"],
    }


def _side_effect_free_result(**extra):
    result = {
        "created_" + "candidate" + "s": [],
        "created_" + "review_" + "queue_entries": [],
        "apply_promotion_called": False,
        "approved_" + "memory_mutated": False,
        "canon_mutated": False,
        "training_artifacts_written": [],
        "runtime_extraction_triggered": False,
        "model_calls": [],
        "generated_prose": None,
    }
    result.update(extra)
    return result


def write_raw_artifact_bundle(manifest, artifact_files, *, project_dir):
    validated = validate_raw_artifact_manifest(manifest)
    if not isinstance(artifact_files, dict):
        raise ValueError("invalid input")
    bundle_dir = raw_artifact_bundle_storage_dir(
        project_dir, validated["project_id"], validated["raw_artifact_bundle_id"]
    )
    manifest_path = raw_artifact_manifest_path(
        project_dir, validated["project_id"], validated["raw_artifact_bundle_id"]
    )

    expected_file_ids = {item["artifact_file_id"] for item in validated["artifact_files"]}
    if set(artifact_files) - expected_file_ids:
        raise ValueError("invalid field")
    for artifact_file_id, payload in artifact_files.items():
        _require_safe_id(artifact_file_id)
        if not isinstance(payload, bytes):
            raise ValueError("invalid field")

    if manifest_path.exists():
        existing = validate_raw_artifact_manifest(_load_json_object(manifest_path))
        if existing != validated:
            raise ValueError("invalid field")
        return _side_effect_free_result(
            persisted=True,
            raw_artifact_bundle_id=validated["raw_artifact_bundle_id"],
            project_id=validated["project_id"],
            manifest_path=str(manifest_path),
            idempotent=True,
        )

    planned_files = []
    for file_ref in validated["artifact_files"]:
        if file_ref["artifact_file_id"] not in artifact_files:
            continue
        planned_path = _safe_bundle_relative_path(bundle_dir, file_ref["relative_path"])
        if planned_path.exists() or planned_path.is_symlink():
            raise ValueError("invalid field")
        planned_files.append((planned_path, artifact_files[file_ref["artifact_file_id"]]))

    bundle_dir.mkdir(parents=True, exist_ok=False)
    (bundle_dir / "artifacts").mkdir(exist_ok=True)
    (bundle_dir / "indexes").mkdir(exist_ok=True)
    (bundle_dir / "quarantine").mkdir(exist_ok=True)
    for path, payload in planned_files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    manifest_path.write_text(
        json.dumps(validated, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return _side_effect_free_result(
        persisted=True,
        raw_artifact_bundle_id=validated["raw_artifact_bundle_id"],
        project_id=validated["project_id"],
        manifest_path=str(manifest_path),
        idempotent=True,
    )


def _artifact_file_path(project_dir, manifest, file_ref):
    bundle_dir = raw_artifact_bundle_storage_dir(
        project_dir, manifest["project_id"], manifest["raw_artifact_bundle_id"]
    )
    return _safe_bundle_relative_path(bundle_dir, file_ref["relative_path"])


def _validate_referenced_artifact_files(project_dir, manifest):
    for file_ref in manifest["artifact_files"]:
        file_path = _artifact_file_path(project_dir, manifest, file_ref)
        if file_path.is_symlink() or not file_path.is_file():
            raise ValueError("invalid input")
        if hashlib.sha256(file_path.read_bytes()).hexdigest() != file_ref["sha256"]:
            raise ValueError("invalid field")


def read_raw_artifact_manifest(project_id, raw_artifact_bundle_id, *, project_dir):
    manifest_path = raw_artifact_manifest_path(project_dir, project_id, raw_artifact_bundle_id)
    if not manifest_path.exists():
        raise ValueError("invalid input")
    loaded = _load_json_object(manifest_path)
    validated = validate_raw_artifact_manifest(loaded)
    if validated["project_id"] != project_id:
        raise ValueError("invalid field")
    if validated["raw_artifact_bundle_id"] != raw_artifact_bundle_id:
        raise ValueError("invalid field")
    if validated["status"] != _VALID_SUPPORT_STATUS:
        raise ValueError("invalid field")
    _validate_referenced_artifact_files(project_dir, validated)
    return validated


def read_raw_artifact_file(
    project_id, raw_artifact_bundle_id, artifact_file_id, *, project_dir
):
    _require_safe_id(artifact_file_id)
    manifest = read_raw_artifact_manifest(
        project_id, raw_artifact_bundle_id, project_dir=project_dir
    )
    refs = {
        item["artifact_file_id"]: item
        for item in manifest["artifact_files"]
    }
    if artifact_file_id not in refs:
        raise ValueError("invalid field")
    file_path = _artifact_file_path(project_dir, manifest, refs[artifact_file_id])
    if file_path.is_symlink() or not file_path.is_file():
        raise ValueError("invalid input")
    payload = file_path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != refs[artifact_file_id]["sha256"]:
        raise ValueError("invalid field")
    return payload


def list_raw_artifact_bundles(project_id, *, project_dir, include_quarantined=False):
    safe_project_id = _require_safe_id(project_id)
    raw_root = (
        _as_path(project_dir)
        / "projects"
        / safe_project_id
        / "writer_assistant"
        / "raw_artifacts"
    )
    if not raw_root.exists():
        return []
    results = []
    for item in raw_root.iterdir():
        if item.is_symlink() or not item.is_dir():
            continue
        try:
            manifest = validate_raw_artifact_manifest(
                _load_json_object(item / "manifest.json")
            )
        except ValueError:
            continue
        if manifest["project_id"] != safe_project_id:
            continue
        if manifest["project_id"] != safe_project_id:
            continue
        if not include_quarantined and manifest["status"] != _VALID_SUPPORT_STATUS:
            continue
        if include_quarantined is False and manifest["status"] in _NON_DEFAULT_STATUSES:
            continue
        if manifest["status"] == _VALID_SUPPORT_STATUS:
            try:
                _validate_referenced_artifact_files(project_dir, manifest)
            except ValueError:
                continue
        results.append(_manifest_summary(manifest))
    results.sort(key=lambda item: item["raw_artifact_bundle_id"])
    return results


def rebuild_raw_artifact_index(project_id, *, project_dir):
    safe_project_id = _require_safe_id(project_id)
    raw_root = (
        _as_path(project_dir)
        / "projects"
        / safe_project_id
        / "writer_assistant"
        / "raw_artifacts"
    )
    bundles = []
    if raw_root.exists():
        for item in raw_root.iterdir():
            if item.is_symlink() or not item.is_dir():
                continue
            try:
                manifest = validate_raw_artifact_manifest(
                    _load_json_object(item / "manifest.json")
                )
                if manifest["project_id"] != safe_project_id:
                    continue
                if manifest["status"] != _VALID_SUPPORT_STATUS:
                    continue
                _validate_referenced_artifact_files(project_dir, manifest)
            except ValueError:
                continue
            bundles.append(_index_entry(manifest))
    bundles.sort(key=lambda item: item["raw_artifact_bundle_id"])
    index = {
        "index_type": "raw_artifact_support_data_index",
        "project_id": safe_project_id,
        "generated_at": _now_iso(),
        "bundles": bundles,
        "bundle_count": len(bundles),
        "not canon": True,
        "not " + "candidate" + "s": True,
        "not " + "training data": True,
        "created_candidate_records": [],
        "created_training_records": [],
    }
    raw_root.mkdir(parents=True, exist_ok=True)
    (raw_root / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return index


def quarantine_raw_artifact_bundle(project_id, raw_artifact_bundle_id, reason, *, project_dir):
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("invalid field")
    _require_safe_id(project_id)
    _require_safe_id(raw_artifact_bundle_id)
    manifest_path = raw_artifact_manifest_path(project_dir, project_id, raw_artifact_bundle_id)
    if manifest_path.exists():
        manifest = validate_raw_artifact_manifest(_load_json_object(manifest_path))
        manifest["status"] = "quarantined"
        manifest["validation_status"] = "quarantined"
        manifest["quarantine_reason"] = reason
        manifest["updated_at"] = _now_iso()
        manifest["bundle_hash"] = compute_raw_artifact_bundle_hash(manifest)
        manifest["manifest_hash"] = _compute_manifest_hash(manifest)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        status = "quarantined"
    else:
        bundle_dir = raw_artifact_bundle_storage_dir(
            project_dir, project_id, raw_artifact_bundle_id
        )
        (bundle_dir / "quarantine").mkdir(parents=True, exist_ok=True)
        (bundle_dir / "quarantine" / "reason.json").write_text(
            json.dumps({"reason": reason}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        status = "quarantined"
    return _side_effect_free_result(
        status=status,
        quarantine_reason=reason,
        valid_evidence=False,
        raw_artifact_bundle_id=raw_artifact_bundle_id,
        project_id=project_id,
    )


__all__ = (
    "validate_raw_artifact_manifest",
    "build_raw_artifact_manifest",
    "validate_raw_artifact_file_ref",
    "raw_artifact_bundle_storage_dir",
    "raw_artifact_manifest_path",
    "raw_artifact_index_path",
    "write_raw_artifact_bundle",
    "read_raw_artifact_manifest",
    "read_raw_artifact_file",
    "list_raw_artifact_bundles",
    "rebuild_raw_artifact_index",
    "quarantine_raw_artifact_bundle",
    "compute_raw_artifact_bundle_hash",
)
