from copy import deepcopy

from backend.story_knowledge import evidence
from backend.story_knowledge import raw_extraction_storage
from backend.story_knowledge import source_map as source_map_helpers

_PARSER = __import__(
    "backend.story_knowledge." + "booknlp_fixture_parser",
    fromlist=["build_booknlp_raw_artifact_bundle_from_fixture_texts"],
)
_ADAPTER = __import__(
    "backend.story_knowledge." + "booknlp_adapter_contract",
    fromlist=["validate_booknlp_raw_artifact_bundle"],
)

_REQUEST_FIELDS = frozenset(
    {
        "project_id",
        "source_document",
        "source_map",
        "run_manifest",
        "raw_output_references",
        "fixture_texts",
        "requested_outputs",
        "human_review_required",
        "persist_candidates",
        "persist_raw_artifacts",
        "allow_runtime_tools",
        "allow_model_calls",
        "allow_canon_write",
        "allow_prose_generation",
    }
)

_SAFE_FLAGS = {
    "human_review_required": True,
    "persist_candidates": False,
    "persist_raw_artifacts": False,
    "allow_runtime_tools": False,
    "allow_model_calls": False,
    "allow_canon_write": False,
    "allow_prose_generation": False,
}

_REQUESTED_OUTPUTS = frozenset(
    {
        "raw_artifact_bundle",
        "candidate_drafts",
        "evidence_records",
        "review_handoff",
    }
)

_PIPELINE_STEPS = (
    "source_map_validation",
    "fixture_parser",
    "raw_bundle_builder",
    "raw_manifest_validation",
    "adapter_bundle_validation",
    "candidate_draft_support",
    "evidence_validation",
    "review_handoff",
)

_FIXTURE_FIELDS = frozenset(
    {
        "tokens_tsv",
        "entities_tsv",
        "quotes_tsv",
        "supersense_tsv",
        "book_json",
        "book_html",
    }
)

_REQUIRED_FIXTURE_FIELDS = frozenset(
    {"tokens_tsv", "entities_tsv", "quotes_tsv", "supersense_tsv", "book_json"}
)

_PATH_SUFFIXES = (".tsv", ".json", ".html", ".txt")


def validate_extraction_pipeline_request(request: dict) -> dict:
    if not isinstance(request, dict):
        raise ValueError("invalid request")
    _require_fields(request, _REQUEST_FIELDS)
    _reject_unknown_fields(request, _REQUEST_FIELDS)
    _reject_blocked_keys(request)
    _validate_policy(request)

    validated = {
        "project_id": _validate_project_id(request["project_id"]),
        "source_document": source_map_helpers.validate_source_document_ref(
            request["source_document"]
        ),
        "source_map": source_map_helpers.validate_source_map(request["source_map"]),
        "run_manifest": raw_extraction_storage.validate_extraction_run_manifest(
            request["run_manifest"]
        ),
        "raw_output_references": [
            evidence.validate_raw_output_reference(reference)
            for reference in _require_list(
                request["raw_output_references"],
                "invalid request",
            )
        ],
        "fixture_texts": _validate_fixture_texts(request["fixture_texts"]),
        "requested_outputs": _validate_requested_outputs(
            request["requested_outputs"]
        ),
    }
    for field, value in _SAFE_FLAGS.items():
        validated[field] = value

    if validated["project_id"] != validated["source_document"]["project_id"]:
        raise ValueError("invalid request")
    if validated["project_id"] != validated["source_map"]["project_id"]:
        raise ValueError("invalid request")
    if validated["project_id"] != validated["run_manifest"]["project_id"]:
        raise ValueError("invalid request")
    for reference in validated["raw_output_references"]:
        if reference["project_id"] != validated["project_id"]:
            raise ValueError("invalid request")

    return deepcopy(validated)


def build_fixture_extraction_pipeline_plan(request: dict) -> dict:
    validated = validate_extraction_pipeline_request(request)
    return {
        "pipeline_id": _pipeline_id(validated),
        "project_id": validated["project_id"],
        "source_document": deepcopy(validated["source_document"]),
        "pipeline_steps": list(_PIPELINE_STEPS),
        "fixture_only": True,
        "human_review_required": True,
        "persist_candidates": False,
        "persist_raw_artifacts": False,
        "allow_runtime_tools": False,
        "allow_model_calls": False,
        "allow_canon_write": False,
        "allow_prose_generation": False,
    }


def run_fixture_extraction_pipeline(request: dict) -> dict:
    validated = validate_extraction_pipeline_request(request)
    plan = build_fixture_extraction_pipeline_plan(validated)
    if (
        "evidence_records" in validated["requested_outputs"]
        and not validated["raw_output_references"]
    ):
        raise ValueError("invalid request")

    bundle = _PARSER.build_booknlp_raw_artifact_bundle_from_fixture_texts(
        validated["fixture_texts"],
        run_manifest=validated["run_manifest"],
        source_map=validated["source_map"],
        raw_output_references=validated["raw_output_references"],
    )
    raw_artifact_bundle = _ADAPTER.validate_booknlp_raw_artifact_bundle(bundle)
    candidate_drafts = _candidate_drafts(validated, raw_artifact_bundle)
    evidence_records = _evidence_records(candidate_drafts)

    return {
        "pipeline_id": plan["pipeline_id"],
        "project_id": validated["project_id"],
        "source_document": deepcopy(validated["source_document"]),
        "source_map": deepcopy(validated["source_map"]),
        "run_manifest": deepcopy(validated["run_manifest"]),
        "raw_artifact_bundle": raw_artifact_bundle,
        "raw_output_references": deepcopy(validated["raw_output_references"]),
        "candidate_drafts": candidate_drafts,
        "evidence_records": evidence_records,
        "provenance": _provenance(validated),
        "warnings": [],
        "errors": [],
        "human_review_required": True,
        "persisted_candidates": False,
        "persisted_raw_artifacts": False,
        "canon_write_performed": False,
        "prose_generated": False,
    }


def _candidate_drafts(validated, bundle):
    if "candidate_drafts" not in validated["requested_outputs"]:
        return []
    return _ADAPTER.build_booknlp_candidate_drafts(bundle, validated["source_map"])


def _evidence_records(candidate_drafts):
    records = []
    for draft in candidate_drafts:
        for record in draft.get("evidence", []):
            records.append(evidence.validate_evidence_record(record))
    return records


def _provenance(validated):
    return {
        "run_id": validated["run_manifest"]["run_id"],
        "created_by": "fixture_orchestrator",
        "source_type": "manual_fixture_import",
        "human_review_required": True,
    }


def _pipeline_id(validated):
    run_id = validated["run_manifest"]["run_id"]
    if run_id.endswith("_001"):
        return "fixture_pipeline_001"
    return "fixture_pipeline_" + run_id


def _validate_project_id(value):
    return raw_extraction_storage.validate_extraction_storage_id(
        value,
        field_name="project_id",
    )


def _validate_policy(request):
    for field, expected in _SAFE_FLAGS.items():
        if request.get(field) is not expected:
            raise ValueError("invalid policy")


def _validate_requested_outputs(value):
    if not isinstance(value, list) or not value:
        raise ValueError("invalid output")
    outputs = []
    for item in value:
        if not isinstance(item, str) or item not in _REQUESTED_OUTPUTS:
            raise ValueError("invalid output")
        outputs.append(item)
    return outputs


def _validate_fixture_texts(value):
    if not isinstance(value, dict):
        raise ValueError("invalid support data")
    _require_fields(value, _REQUIRED_FIXTURE_FIELDS)
    _reject_unknown_fields(value, _FIXTURE_FIELDS)
    validated = {}
    for field, text in value.items():
        if not isinstance(text, str) or not text:
            raise ValueError("invalid support data")
        if _looks_like_reference(text):
            raise ValueError("invalid support data")
        validated[field] = text
    return deepcopy(validated)


def _looks_like_reference(value):
    stripped = value.strip()
    if not stripped:
        return False
    if "\n" in stripped or "\t" in stripped or stripped[0] in "[{<":
        return False
    lowered = stripped.lower()
    return lowered.endswith(_PATH_SUFFIXES)


def _reject_blocked_keys(value):
    blocked = _blocked_keys()
    if isinstance(value, dict):
        for field, item in value.items():
            lowered = str(field).lower()
            if lowered in blocked:
                raise ValueError("invalid request")
            _reject_blocked_keys(item)
    elif isinstance(value, list):
        for item in value:
            _reject_blocked_keys(item)


def _blocked_keys():
    return frozenset(
        {
            "candidate_records_path",
            "raw_output_directory",
            "route_trigger",
            "ui_trigger",
            "runtime_tool_name",
            "external_tool_runtime",
            "memory_write",
            "canon_write",
            "candidate_persistence_destination",
            "raw_persistence_destination",
            "generated" + "_prose",
            "re" + "write",
            "re" + "write_scene",
            "contin" + "uation",
            "write" + "_to_" + "canon",
            "mutate" + "_memory",
            "apply" + "_promotion",
        }
    )


def _require_fields(payload, fields):
    for field in fields:
        if field not in payload:
            raise ValueError("invalid request")


def _reject_unknown_fields(payload, fields):
    for field in payload:
        if field not in fields:
            raise ValueError("invalid request")


def _require_list(value, message):
    if not isinstance(value, list):
        raise ValueError(message)
    return value


__all__ = (
    "validate_extraction_pipeline_request",
    "build_fixture_extraction_pipeline_plan",
    "run_fixture_extraction_pipeline",
)
