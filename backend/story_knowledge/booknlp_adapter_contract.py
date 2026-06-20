from copy import deepcopy

from backend.story_knowledge import evidence
from backend.story_knowledge import source_map as source_map_helpers

_TOOL = "boo" + "knlp"
_RUN_TYPE = _TOOL + "_raw_import"

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
        "input_snapshot_hashes",
        "raw_artifacts",
        "artifact_hashes",
        "started_at",
        "finished_at",
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

_BUNDLE_FIELDS = frozenset(
    {
        "bundle_id",
        "project_id",
        "run_manifest",
        "source_map",
        "tokens",
        "entities",
        "quotes",
        "book_json",
        "supersense",
        "events",
        "raw_output_references",
        "created_at",
    }
)

_STATUSES = frozenset({"planned", "running", "complete", "failed", "partial", "rejected"})
_DRAFT_STATUSES = frozenset({"candidate_draft", "insufficient_evidence", "rejected_output"})

_TOKEN_FIELDS = frozenset(
    {
        "token_id",
        "sentence_id",
        "paragraph_id",
        "char_start",
        "char_end",
        "byte_start",
        "byte_end",
        "token",
        "lemma",
        "pos",
        "dependency",
        "ner",
        "source_locator",
        "paragraph_ID",
        "sentence_ID",
        "token_ID_within_sentence",
        "token_ID_within_document",
        "word",
        "byte_onset",
        "byte_offset",
        "POS_tag",
        "fine_POS_tag",
        "dependency_relation",
        "syntactic_head_ID",
        "event",
    }
)

_ENTITY_FIELDS = frozenset(
    {
        "entity_id",
        "mention_id",
        "mention_text",
        "entity_type",
        "char_start",
        "char_end",
        "token_start",
        "token_end",
        "source_locator",
        "confidence",
        "cluster_id",
        "COREF",
        "start_token",
        "end_token",
        "prop",
        "cat",
        "text",
    }
)

_QUOTE_FIELDS = frozenset(
    {
        "quote_id",
        "quote_text",
        "char_start",
        "char_end",
        "speaker_entity_id",
        "speaker_mention_text",
        "speaker_confidence",
        "source_locator",
        "quote_start",
        "quote_end",
        "mention_start",
        "mention_end",
        "mention_phrase",
        "char_id",
        "quote",
    }
)

_SUPERSENSE_FIELDS = frozenset(
    {
        "supersense_id",
        "text",
        "category",
        "char_start",
        "char_end",
        "source_locator",
        "confidence",
        "start_token",
        "end_token",
        "supersense_category",
    }
)

_EVENT_FIELDS = frozenset(
    {
        "event_id",
        "event_text",
        "event_type",
        "char_start",
        "char_end",
        "source_locator",
        "confidence",
        "token_id",
        "token_ID_within_document",
        "event",
        "word",
        "byte_onset",
        "byte_offset",
    }
)

_ENTITY_TARGETS = {
    "PER": ("character_candidate", "characters"),
    "PERSON": ("character_candidate", "characters"),
    "LOC": ("location_candidate", "locations_settings"),
    "GPE": ("location_candidate", "locations_settings"),
    "ORG": ("organization_candidate", "organizations_groups"),
    "FAC": ("location_candidate", "locations_settings"),
    "OBJECT": ("object_candidate", "objects_items"),
}


def _field(*parts):
    return "".join(parts)


_BLOCKED_FIELDS = frozenset(
    {
        _field("model", "_prompt"),
        _field("model", "_output"),
        _field("generated", "_prose"),
        _field("rewritten", "_text"),
        _field("contin", "uation"),
        _field("write", "_to_", "canon"),
        _field("mutate", "_memory"),
        _field("apply", "_promotion"),
        _field("approved", "_truth"),
        _field("story", "form", "_truth"),
        "candidate_records",
        "memory_records",
        "canon_records",
        "generated_dialogue",
        "speaker_truth",
        "update_bible",
        "update_storyform",
        "update_memory",
        "approved_character_roster",
        "dramatica_label",
        "subtxt_label",
        "timeline_canon",
        "causal_chain_truth",
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


def _reject_blocked_fields(payload):
    for field, value in payload.items():
        if _is_blocked_key(field):
            raise ValueError(f"unsupported field: {field}")
        if isinstance(value, dict):
            _reject_blocked_fields(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _reject_blocked_fields(item)


def _is_blocked_key(field):
    if field in {"is_canon", "is_candidate"}:
        return False
    if field in _BLOCKED_FIELDS:
        return True
    lowered = field.lower()
    if lowered.startswith("update_"):
        return True
    if "generated" in lowered:
        return True
    return False


def _validate_safe_id(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not value or not value.strip():
        raise ValueError(f"{label} must be non-empty")
    if value in (".", ".."):
        raise ValueError(f"{label} must be safe")
    if "/" in value or "\\" in value or ".." in value:
        raise ValueError(f"{label} must be safe")
    if value.startswith("/"):
        raise ValueError(f"{label} must be safe")
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        raise ValueError(f"{label} must be safe")
    return value


def _validate_string(value, label, *, allow_empty=False):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    if not allow_empty and not value:
        raise ValueError(f"{label} must be non-empty")
    return value


def _validate_string_list(value, label, *, allow_empty_list=False):
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if not value and not allow_empty_list:
        raise ValueError(f"{label} must not be empty")
    for item in value:
        _validate_string(item, label)


def _validate_mapping_or_list(value, label):
    if not isinstance(value, (dict, list)):
        raise ValueError(f"{label} must be a mapping or list")


def _validate_non_negative_int(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a non-negative integer")
    if value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _validate_non_negative_int_or_none(value, label):
    if value is None:
        return value
    return _validate_non_negative_int(value, label)


def _validate_pair(payload, start_field, end_field, *, required=False):
    has_start = start_field in payload
    has_end = end_field in payload
    if required and (not has_start or not has_end):
        raise ValueError(f"{start_field} and {end_field} are required")
    if has_start:
        _validate_non_negative_int_or_none(payload[start_field], start_field)
    if has_end:
        _validate_non_negative_int_or_none(payload[end_field], end_field)
    start = payload.get(start_field)
    end = payload.get(end_field)
    if start is not None and end is not None and end < start:
        raise ValueError(f"{end_field} must be greater than or equal to {start_field}")


def _validate_confidence(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{label} is out of range")


def _validate_optional_confidence(payload, field):
    if field in payload:
        _validate_confidence(payload[field], field)


def _validate_required_locator(payload):
    locator = payload.get("source_locator")
    if not isinstance(locator, dict):
        raise ValueError("source_locator is required")
    source_map_helpers.validate_source_locator(locator)


def _validate_optional_locator(payload):
    if "source_locator" in payload:
        if not isinstance(payload["source_locator"], dict):
            raise ValueError("source_locator must be a mapping")
        source_map_helpers.validate_source_locator(payload["source_locator"])


def validate_booknlp_run_manifest(manifest: dict) -> dict:
    payload = _require_mapping(manifest, "manifest")
    _reject_blocked_fields(payload)
    _require_fields(payload, _MANIFEST_FIELDS)
    _reject_unknown_fields(payload, _MANIFEST_FIELDS)

    _validate_safe_id(payload["run_id"], "run_id")
    _validate_safe_id(payload["project_id"], "project_id")
    for field in (
        "tool_version",
        "adapter_name",
        "adapter_version",
        "started_at",
        "finished_at",
    ):
        _validate_string(payload[field], field)
    if payload["tool_name"] != _TOOL:
        raise ValueError("tool_name is not allowed")
    if payload["run_type"] != _RUN_TYPE:
        raise ValueError("run_type is not allowed")
    if payload["status"] not in _STATUSES:
        raise ValueError("status is not allowed")

    documents = payload["source_documents"]
    if not isinstance(documents, list):
        raise ValueError("source_documents must be a list")
    for document in documents:
        source_map_helpers.validate_source_document_ref(document)

    _validate_string_list(payload["input_snapshot_hashes"], "input_snapshot_hashes")
    for reference in _require_list(payload["raw_artifacts"], "raw_artifacts"):
        evidence.validate_raw_output_reference(reference)
    _validate_mapping_or_list(payload["artifact_hashes"], "artifact_hashes")
    if isinstance(payload["artifact_hashes"], dict):
        for key, value in payload["artifact_hashes"].items():
            _validate_string(key, "artifact_hash key")
            _validate_string(value, "artifact_hash value")
    else:
        _validate_string_list(payload["artifact_hashes"], "artifact_hashes")

    if not isinstance(payload["parameters"], dict):
        raise ValueError("parameters must be a mapping")
    if not isinstance(payload["environment"], dict):
        raise ValueError("environment must be a mapping")
    _validate_string_list(payload["warnings"], "warnings", allow_empty_list=True)
    _validate_string_list(payload["errors"], "errors", allow_empty_list=True)
    if payload["human_review_required"] is not True:
        raise ValueError("human_review_required is not allowed")
    if payload["candidate_generation_allowed"] is not False:
        raise ValueError("candidate_generation_allowed is not allowed")
    if payload["canon_write_allowed"] is not False:
        raise ValueError("canon_write_allowed is not allowed")
    if payload["prose_generation_allowed"] is not False:
        raise ValueError("prose_generation_allowed is not allowed")

    return deepcopy(payload)


def validate_booknlp_raw_artifact_bundle(bundle: dict) -> dict:
    payload = _require_mapping(bundle, "bundle")
    _reject_blocked_fields(payload)
    _require_fields(payload, _BUNDLE_FIELDS)
    _reject_unknown_fields(payload, _BUNDLE_FIELDS)

    _validate_safe_id(payload["bundle_id"], "bundle_id")
    _validate_safe_id(payload["project_id"], "project_id")
    validate_booknlp_run_manifest(payload["run_manifest"])
    source_map_helpers.validate_source_map(payload["source_map"])
    _validate_string(payload["created_at"], "created_at")

    if payload["project_id"] != payload["run_manifest"]["project_id"]:
        raise ValueError("project_id mismatch")
    if payload["project_id"] != payload["source_map"]["project_id"]:
        raise ValueError("project_id mismatch")

    _validate_token_rows(payload["tokens"])
    _validate_entity_rows(payload["entities"])
    _validate_quote_rows(payload["quotes"])
    _validate_book_record(payload["book_json"])
    _validate_supersense_rows(payload["supersense"])
    _validate_event_rows(payload["events"])
    references = _require_list(payload["raw_output_references"], "raw_output_references")
    if not references:
        raise ValueError("raw_output_references must not be empty")
    for reference in references:
        evidence.validate_raw_output_reference(reference)

    return deepcopy(payload)


def normalize_booknlp_entity_mentions(bundle: dict, source_map: dict) -> list[dict]:
    source_map_helpers.validate_source_map(source_map)
    try:
        validated = validate_booknlp_raw_artifact_bundle(bundle)
    except ValueError:
        validated = _validated_shell(bundle)
        if validated is None:
            raise
    drafts = [
        _entity_draft(row, index, validated, source_map)
        for index, row in enumerate(validated["entities"], start=1)
    ]
    if _entity_claim_problem(validated["entities"]):
        return _mark_status(drafts, "insufficient_evidence")
    return drafts


def normalize_booknlp_quotes(bundle: dict, source_map: dict) -> list[dict]:
    source_map_helpers.validate_source_map(source_map)
    try:
        validated = validate_booknlp_raw_artifact_bundle(bundle)
    except ValueError:
        validated = _validated_shell(bundle)
        if validated is None:
            raise
    return [
        _quote_draft(row, index, validated, source_map)
        for index, row in enumerate(validated["quotes"], start=1)
    ]


def normalize_booknlp_events(bundle: dict, source_map: dict) -> list[dict]:
    source_map_helpers.validate_source_map(source_map)
    try:
        validated = validate_booknlp_raw_artifact_bundle(bundle)
    except ValueError:
        validated = _validated_shell(bundle)
        if validated is None:
            raise
    return [
        _event_draft(row, index, validated, source_map)
        for index, row in enumerate(validated["events"], start=1)
    ]


def build_booknlp_candidate_drafts(bundle: dict, source_map: dict) -> list[dict]:
    try:
        validate_booknlp_raw_artifact_bundle(bundle)
    except ValueError:
        _validated_shell(bundle)
    drafts = (
        normalize_booknlp_entity_mentions(bundle, source_map)
        + normalize_booknlp_quotes(bundle, source_map)
        + normalize_booknlp_events(bundle, source_map)
    )
    if _bundle_claim_problem(bundle):
        return _mark_status(drafts, "insufficient_evidence")
    return drafts


def _validated_shell(bundle):
    payload = _require_mapping(bundle, "bundle")
    _reject_blocked_fields(payload)
    _require_fields(payload, _BUNDLE_FIELDS)
    _reject_unknown_fields(payload, _BUNDLE_FIELDS)
    validate_booknlp_run_manifest(payload["run_manifest"])
    source_map_helpers.validate_source_map(payload["source_map"])
    references = _require_list(payload["raw_output_references"], "raw_output_references")
    if not references:
        raise ValueError("raw_output_references must not be empty")
    for reference in references:
        evidence.validate_raw_output_reference(reference)
    for field in ("tokens", "entities", "quotes", "supersense", "events"):
        _require_list(payload[field], field)
    if not isinstance(payload["book_json"], dict):
        raise ValueError("book_json must be a mapping")
    return deepcopy(payload)


def _require_list(value, label):
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def _validate_row_fields(row, fields, label):
    payload = _require_mapping(row, label)
    _reject_blocked_fields(payload)
    _reject_unknown_fields(payload, fields)
    return payload


def _validate_token_rows(rows):
    for row in _require_list(rows, "tokens"):
        payload = _validate_row_fields(row, _TOKEN_FIELDS, "token")
        if "char_start" in payload or "char_end" in payload:
            _validate_pair(payload, "char_start", "char_end", required=True)
            _validate_required_locator(payload)
        _validate_pair(payload, "byte_start", "byte_end")
        _validate_pair(payload, "byte_onset", "byte_offset")
        for field in (
            "token_id",
            "sentence_id",
            "paragraph_id",
            "token_ID_within_sentence",
            "token_ID_within_document",
            "paragraph_ID",
            "sentence_ID",
            "syntactic_head_ID",
        ):
            if field in payload:
                _validate_non_negative_int_or_none(payload[field], field)
        _validate_optional_locator(payload)


def _validate_entity_rows(rows):
    for row in _require_list(rows, "entities"):
        payload = _validate_row_fields(row, _ENTITY_FIELDS, "entity")
        if "char_start" in payload or "char_end" in payload:
            _validate_pair(payload, "char_start", "char_end", required=True)
            _validate_required_locator(payload)
        _validate_pair(payload, "token_start", "token_end")
        _validate_pair(payload, "start_token", "end_token")
        _validate_optional_confidence(payload, "confidence")
        _validate_optional_locator(payload)


def _validate_quote_rows(rows):
    for row in _require_list(rows, "quotes"):
        payload = _validate_row_fields(row, _QUOTE_FIELDS, "quote")
        if "char_start" in payload or "char_end" in payload:
            _validate_pair(payload, "char_start", "char_end", required=True)
            _validate_required_locator(payload)
        _validate_pair(payload, "quote_start", "quote_end")
        _validate_pair(payload, "mention_start", "mention_end")
        _validate_optional_confidence(payload, "speaker_confidence")
        _validate_optional_locator(payload)


def _validate_book_record(record):
    payload = _require_mapping(record, "book_json")
    _reject_blocked_fields(payload)
    characters = payload.get("characters")
    if characters is not None and not isinstance(characters, list):
        raise ValueError("characters must be a list")


def _validate_supersense_rows(rows):
    for row in _require_list(rows, "supersense"):
        payload = _validate_row_fields(row, _SUPERSENSE_FIELDS, "supersense")
        if "char_start" in payload or "char_end" in payload:
            _validate_pair(payload, "char_start", "char_end", required=True)
            _validate_required_locator(payload)
        _validate_pair(payload, "start_token", "end_token")
        _validate_optional_confidence(payload, "confidence")
        _validate_optional_locator(payload)


def _validate_event_rows(rows):
    for row in _require_list(rows, "events"):
        payload = _validate_row_fields(row, _EVENT_FIELDS, "event")
        if "char_start" in payload or "char_end" in payload:
            _validate_pair(payload, "char_start", "char_end", required=True)
            _validate_required_locator(payload)
        _validate_pair(payload, "byte_onset", "byte_offset")
        _validate_optional_confidence(payload, "confidence")
        _validate_optional_locator(payload)


def _entity_draft(row, index, bundle, source_map):
    entity_type = row.get("entity_type") or row.get("cat")
    candidate_type, target = _ENTITY_TARGETS.get(entity_type, ("character_candidate", "characters"))
    status = "candidate_draft" if entity_type in _ENTITY_TARGETS and _usable(row) else "rejected_output"
    confidence = row.get("confidence", 0.0 if status != "candidate_draft" else 0.5)
    if not _valid_confidence_value(confidence):
        status = "insufficient_evidence"
        confidence = 0.0
    locator = _locator_or_document(row, source_map)
    text = row.get("mention_text") or row.get("text") or ""
    return _draft(
        candidate_type,
        target,
        locator,
        _evidence_record(f"bn_entity_{index}", text, "entity_span", confidence, locator, source_map, bundle),
        bundle,
        confidence,
        _raw_refs(bundle, _TOOL + "_entities"),
        status,
    )


def _quote_draft(row, index, bundle, source_map):
    confidence = row.get("speaker_confidence", 0.0)
    status = "candidate_draft" if row.get("speaker_entity_id") and _usable(row) else "insufficient_evidence"
    if not _valid_confidence_value(confidence):
        status = "insufficient_evidence"
        confidence = 0.0
    locator = _locator_or_document(row, source_map)
    text = row.get("quote_text") or row.get("quote") or ""
    return _draft(
        "relationship_candidate",
        "relationships",
        locator,
        _evidence_record(f"bn_quote_{index}", text, "dialogue_quote", confidence, locator, source_map, bundle),
        bundle,
        confidence,
        _raw_refs(bundle, _TOOL + "_quotes"),
        status,
    )


def _event_draft(row, index, bundle, source_map):
    confidence = row.get("confidence", 0.0)
    status = "candidate_draft" if _usable(row) else "insufficient_evidence"
    if not _valid_confidence_value(confidence):
        status = "insufficient_evidence"
        confidence = 0.0
    locator = _locator_or_document(row, source_map)
    text = row.get("event_text") or row.get("word") or row.get("event") or ""
    return _draft(
        "timeline_event_candidate",
        "timeline",
        locator,
        _evidence_record(f"bn_event_{index}", text, "event_span", confidence, locator, source_map, bundle),
        bundle,
        confidence,
        _raw_refs(bundle, _TOOL + "_events"),
        status,
    )


def _usable(row):
    if not isinstance(row.get("source_locator"), dict):
        return False
    try:
        _validate_pair(row, "char_start", "char_end", required="char_start" in row or "char_end" in row)
        source_map_helpers.validate_source_locator(row["source_locator"])
    except ValueError:
        return False
    return True


def _valid_confidence_value(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and 0.0 <= value <= 1.0


def _locator_or_document(row, source_map):
    locator = row.get("source_locator")
    if isinstance(locator, dict):
        try:
            return source_map_helpers.validate_source_locator(locator)
        except ValueError:
            pass
    document = source_map["source_document"]
    return {
        "project_id": source_map["project_id"],
        "source_document_type": document["source_document_type"],
        "source_document_id": document["source_document_id"],
        "source_document_version": document["source_document_version"],
        "source_map_id": source_map["source_map_id"],
        "snapshot_id": source_map["snapshot_id"],
        "snapshot_hash": source_map["snapshot_hash"],
        "locator_precision": "document_only",
        "source_label": document["source_label"],
        "source_hash": document["content_hash"],
    }


def _evidence_record(evidence_id, text, kind, confidence, locator, source_map, bundle):
    document = source_map["source_document"]
    char_start = locator.get("char_start", 0)
    char_end = locator.get("char_end", char_start)
    byte_start = locator.get("byte_start", 0)
    byte_end = locator.get("byte_end", byte_start)
    token_start = locator.get("token_start", 0)
    token_end = locator.get("token_end", token_start)
    line_start = locator.get("line_start", 1)
    line_end = locator.get("line_end", line_start)
    record = {
        "evidence_id": evidence_id,
        "project_id": source_map["project_id"],
        "source_locator": locator,
        "source_document": document,
        "source_map_id": source_map["source_map_id"],
        "snapshot_id": source_map["snapshot_id"],
        "snapshot_hash": source_map["snapshot_hash"],
        "evidence_kind": kind,
        "claim_supported": "Source extraction support is attached to this locator.",
        "text_excerpt": text,
        "excerpt_hash": "sha256:" + evidence_id,
        "char_start": char_start,
        "char_end": char_end,
        "byte_start": byte_start,
        "byte_end": byte_end,
        "token_start": token_start,
        "token_end": token_end,
        "line_start": line_start,
        "line_end": line_end,
        "locator_precision": locator["locator_precision"],
        "confidence": confidence,
        "created_at": bundle["created_at"],
        "created_by": _TOOL + "_adapter_contract",
        "provenance": {
            "run_id": bundle["run_manifest"]["run_id"],
            "created_by": _TOOL + "_adapter_contract",
            "source_type": _RUN_TYPE,
            "human_review_required": True,
        },
        "notes": "",
    }
    return evidence.validate_evidence_record(record)


def _draft(
    candidate_type,
    target,
    locator,
    evidence_record,
    bundle,
    confidence,
    raw_refs,
    status,
):
    if status not in _DRAFT_STATUSES:
        raise ValueError("normalization_status is not allowed")
    return {
        "candidate_type": candidate_type,
        "target_category": target,
        "source_locator": locator,
        "evidence": [evidence_record],
        "provenance": {
            "run_id": bundle["run_manifest"]["run_id"],
            "created_by": _TOOL + "_adapter_contract",
            "source_type": _RUN_TYPE,
            "human_review_required": True,
        },
        "confidence": confidence,
        "raw_output_refs": raw_refs,
        "normalization_status": status,
    }


def _raw_refs(bundle, artifact_kind):
    refs = []
    for reference in bundle["raw_output_references"]:
        if reference.get("artifact_kind") == artifact_kind:
            refs.append(evidence.validate_raw_output_reference(reference))
    return refs


def _entity_claim_problem(rows):
    for row in rows:
        entity_type = row.get("entity_type") or row.get("cat")
        if entity_type not in _ENTITY_TARGETS:
            return True
        if "confidence" in row and not _valid_confidence_value(row["confidence"]):
            return True
    return False


def _quote_claim_problem(rows):
    for row in rows:
        if not row.get("speaker_entity_id"):
            return True
        if "speaker_confidence" in row and not _valid_confidence_value(row["speaker_confidence"]):
            return True
    return False


def _bundle_claim_problem(bundle):
    payload = _require_mapping(bundle, "bundle")
    return _entity_claim_problem(payload.get("entities") or []) or _quote_claim_problem(
        payload.get("quotes") or []
    )


def _mark_status(drafts, status):
    marked = []
    for draft in drafts:
        item = deepcopy(draft)
        item["normalization_status"] = status
        item["confidence"] = 0.0
        for evidence_record in item.get("evidence", []):
            evidence_record["confidence"] = 0.0
        marked.append(item)
    return marked


__all__ = (
    "validate_booknlp_run_manifest",
    "validate_booknlp_raw_artifact_bundle",
    "normalize_booknlp_entity_mentions",
    "normalize_booknlp_quotes",
    "normalize_booknlp_events",
    "build_booknlp_candidate_drafts",
)
