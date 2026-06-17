"""Contract tests for future Writer Assistant Core candidate record validation helpers.

T004 is expected to implement `backend.story_knowledge.candidate_record` with:
- validate_candidate_record(record) -> dict
- validate_source_locator(locator) -> dict
- validate_evidence_item(item) -> dict
- validate_provenance(provenance) -> dict

Storage path construction is deferred to T005.
"""

import inspect

import pytest

from backend.story_knowledge import candidate_record
from backend.story_knowledge import candidate_schema

# ---------------------------------------------------------------------------
# Contract constants (aligned with PHASE8-IMPL-002-T002 decision)
# ---------------------------------------------------------------------------

CANDIDATE_RECORD_REQUIRED_FIELDS = frozenset(
    {
        "candidate_id",
        "project_id",
        "candidate_type",
        "status",
        "target_category",
        "source_locator",
        "evidence",
        "provenance",
        "owner_decision",
        "destination",
        "confidence",
        "created_at",
        "updated_at",
    }
)

FORBIDDEN_CANDIDATE_TYPES = frozenset(
    {
        "generated_prose",
        "rewrite",
        "continuation",
        "style_imitation",
        "prose_improvement",
        "summary_as_canon",
        "apply_promotion",
    }
)

ALLOWED_SOURCE_DOCUMENT_TYPES = frozenset(
    {
        "scene",
        "note",
        "material",
        "bible",
        "storyform",
        "omi",
    }
)

FORBIDDEN_LOCATOR_FIELDS = frozenset(
    {
        "path",
        "absolute_path",
        "training_path",
        "dataset_path",
        "external_file_path",
        "external_book_path",
        "training_file_path",
        "dataset_manifest_path",
        "absolute_filesystem_path",
    }
)

STORED_STATUS_VALUES = frozenset(
    {
        "candidate",
        "owner_review",
        "approved",
        "rejected",
        "needs_revision",
        "archived",
    }
)

FORBIDDEN_STORED_STATUS_VALUES = frozenset({"promoted"})

STORED_OWNER_DECISION_VALUES = frozenset(
    {
        "undecided",
        "approve",
        "reject",
        "needs_revision",
        "archive",
    }
)

FORBIDDEN_OWNER_DECISION_VALUES = frozenset({"promote"})

FORBIDDEN_DESTINATION_VALUES = frozenset(
    {
        "apply_promotion",
        "auto_promote",
        "write_to_canon",
        "mutate_memory",
        "rewrite_scene",
    }
)

ALLOWED_PROVENANCE_ORIGINS = frozenset(
    {
        "manual",
        "extractor",
        "model_assisted",
        "imported",
    }
)

FORBIDDEN_PROVENANCE_RUNTIME_FIELDS = frozenset(
    {
        "ollama_request",
        "model_prompt",
        "model_output_path",
    }
)

UNSAFE_ID_VALUES = (
    "../escape",
    "..",
    "/absolute",
    "C:\\escape",
    "folder/name",
    "folder\\name",
    "",
    "   ",
)

FORBIDDEN_SOURCE_TERMS = (
    "ollama",
    "requests",
    "httpx",
    "analysis_engine",
    "story_check",
    "openai",
    "spacy",
    "gliner",
    "booknlp",
    "training",
    "apply_promotion",
    "write_to_canon",
    "mutate_memory",
    "rewrite_scene",
)

# Future storage path expectation (T005 scope; documented only, not tested here).
FUTURE_STORAGE_PATH_PATTERN = (
    "projects/{project_id}/writer_assistant/candidates/{candidate_id}.json"
)


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def build_valid_source_locator(**overrides):
    locator = {
        "project_id": "example",
        "source_document_type": "scene",
        "source_document_id": "scene_001",
        "section_id": None,
        "chapter_id": None,
        "scene_id": "scene_001",
        "line_start": None,
        "line_end": None,
        "char_start": None,
        "char_end": None,
        "source_hash": None,
    }
    locator.update(overrides)
    return locator


def build_valid_evidence_item(**overrides):
    item = {
        "evidence_id": "evidence_001",
        "source_locator": build_valid_source_locator(),
        "source_text_excerpt": "",
        "summary": "",
        "supports_claim": "",
        "confidence": 0.5,
        "notes": "",
    }
    item.update(overrides)
    return item


def build_valid_provenance(**overrides):
    provenance = {
        "origin": "manual",
        "extraction_method": "owner_entry",
        "timestamp": "2026-06-16T00:00:00Z",
        "human_review_required": True,
    }
    provenance.update(overrides)
    return provenance


def build_valid_candidate_record(**overrides):
    record = {
        "candidate_id": "core_candidate_scene_001_character_001",
        "project_id": "example",
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": build_valid_source_locator(),
        "evidence": [],
        "provenance": build_valid_provenance(),
        "owner_decision": "undecided",
        "destination": "omi_candidate_only",
        "confidence": 0.0,
        "created_at": "2026-06-16T00:00:00Z",
        "updated_at": "2026-06-16T00:00:00Z",
    }
    record.update(overrides)
    return record


def assert_validation_rejects(validator, payload, *, match=None):
    with pytest.raises(ValueError, match=match):
        validator(payload)


# ---------------------------------------------------------------------------
# Candidate record required-field contract
# ---------------------------------------------------------------------------


def test_validate_candidate_record_accepts_valid_fixture():
    record = build_valid_candidate_record()
    result = candidate_record.validate_candidate_record(record)
    assert result == record or isinstance(result, dict)


@pytest.mark.parametrize("missing_field", sorted(CANDIDATE_RECORD_REQUIRED_FIELDS))
def test_validate_candidate_record_rejects_missing_required_field(missing_field):
    record = build_valid_candidate_record()
    del record[missing_field]
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match=missing_field,
    )


# ---------------------------------------------------------------------------
# Candidate type contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "candidate_type", sorted(candidate_schema.CORE_CANDIDATE_TYPES)
)
def test_validate_candidate_record_accepts_core_candidate_types(candidate_type):
    target_category = candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES[
        candidate_type
    ]
    record = build_valid_candidate_record(
        candidate_type=candidate_type,
        target_category=target_category,
    )
    result = candidate_record.validate_candidate_record(record)
    assert result["candidate_type"] == candidate_type


@pytest.mark.parametrize("forbidden_type", sorted(FORBIDDEN_CANDIDATE_TYPES))
def test_validate_candidate_record_rejects_forbidden_candidate_types(
    forbidden_type,
):
    record = build_valid_candidate_record(candidate_type=forbidden_type)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="candidate_type",
    )


def test_validate_candidate_record_rejects_unknown_candidate_type():
    record = build_valid_candidate_record(candidate_type="unknown_type_xyz")
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="candidate_type",
    )


# ---------------------------------------------------------------------------
# Target category alignment contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("candidate_type", "expected_category"),
    sorted(candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES.items()),
)
def test_validate_candidate_record_accepts_aligned_target_category(
    candidate_type,
    expected_category,
):
    record = build_valid_candidate_record(
        candidate_type=candidate_type,
        target_category=expected_category,
    )
    result = candidate_record.validate_candidate_record(record)
    assert result["target_category"] == expected_category


def test_validate_candidate_record_rejects_mismatched_target_category():
    record = build_valid_candidate_record(
        candidate_type="character_candidate",
        target_category="timeline",
    )
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="target_category",
    )


def test_target_category_does_not_imply_approved_truth():
    for target_category in candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES.values():
        assert "canon" not in target_category
        assert not target_category.startswith("approved_")


# ---------------------------------------------------------------------------
# Source locator contract
# ---------------------------------------------------------------------------


def test_validate_source_locator_accepts_valid_fixture():
    locator = build_valid_source_locator()
    result = candidate_record.validate_source_locator(locator)
    assert result == locator or isinstance(result, dict)


@pytest.mark.parametrize("required_field", ("project_id", "source_document_type", "source_document_id"))
def test_validate_source_locator_rejects_missing_required_field(required_field):
    locator = build_valid_source_locator()
    del locator[required_field]
    assert_validation_rejects(
        candidate_record.validate_source_locator,
        locator,
        match=required_field,
    )


@pytest.mark.parametrize("document_type", sorted(ALLOWED_SOURCE_DOCUMENT_TYPES))
def test_validate_source_locator_accepts_allowed_document_types(document_type):
    locator = build_valid_source_locator(source_document_type=document_type)
    result = candidate_record.validate_source_locator(locator)
    assert result["source_document_type"] == document_type


def test_validate_source_locator_rejects_unknown_document_type():
    locator = build_valid_source_locator(source_document_type="external_file")
    assert_validation_rejects(
        candidate_record.validate_source_locator,
        locator,
        match="source_document_type",
    )


@pytest.mark.parametrize("forbidden_field", sorted(FORBIDDEN_LOCATOR_FIELDS))
def test_validate_source_locator_rejects_forbidden_path_fields(forbidden_field):
    locator = build_valid_source_locator(**{forbidden_field: "/etc/passwd"})
    assert_validation_rejects(
        candidate_record.validate_source_locator,
        locator,
        match=forbidden_field,
    )


def test_validate_source_locator_rejects_arbitrary_filesystem_path_values():
    locator = build_valid_source_locator(
        source_document_id="/var/tmp/owner_scene.md",
    )
    assert_validation_rejects(
        candidate_record.validate_source_locator,
        locator,
        match="source_document_id",
    )


# ---------------------------------------------------------------------------
# Evidence contract
# ---------------------------------------------------------------------------


def test_validate_candidate_record_allows_empty_evidence_list():
    record = build_valid_candidate_record(evidence=[])
    result = candidate_record.validate_candidate_record(record)
    assert result["evidence"] == []


def test_validate_evidence_item_accepts_valid_fixture():
    item = build_valid_evidence_item()
    result = candidate_record.validate_evidence_item(item)
    assert result == item or isinstance(result, dict)


def test_validate_evidence_item_rejects_missing_source_locator():
    item = build_valid_evidence_item()
    del item["source_locator"]
    assert_validation_rejects(
        candidate_record.validate_evidence_item,
        item,
        match="source_locator",
    )


def test_validate_evidence_item_rejects_missing_confidence():
    item = build_valid_evidence_item()
    del item["confidence"]
    assert_validation_rejects(
        candidate_record.validate_evidence_item,
        item,
        match="confidence",
    )


@pytest.mark.parametrize("confidence", (0.0, 0.5, 1.0))
def test_validate_evidence_item_accepts_in_range_confidence(confidence):
    item = build_valid_evidence_item(confidence=confidence)
    result = candidate_record.validate_evidence_item(item)
    assert result["confidence"] == confidence


@pytest.mark.parametrize("confidence", (-0.1, 1.1, 2.0))
def test_validate_evidence_item_rejects_out_of_range_confidence(confidence):
    item = build_valid_evidence_item(confidence=confidence)
    assert_validation_rejects(
        candidate_record.validate_evidence_item,
        item,
        match="confidence",
    )


def test_evidence_excerpt_fields_are_owner_authored_support_only():
    """Excerpt fields, when present, must validate as owner-authored support metadata."""
    item = build_valid_evidence_item(
        source_text_excerpt="owner-authored excerpt placeholder",
        summary="owner-authored summary label",
        supports_claim="structural claim label",
    )
    result = candidate_record.validate_evidence_item(item)
    assert result["source_text_excerpt"] == "owner-authored excerpt placeholder"
    assert result["summary"] == "owner-authored summary label"
    assert result["supports_claim"] == "structural claim label"


def test_validate_candidate_record_rejects_non_list_evidence():
    record = build_valid_candidate_record(evidence="not-a-list")
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="evidence",
    )


# ---------------------------------------------------------------------------
# Provenance contract
# ---------------------------------------------------------------------------


def test_validate_provenance_accepts_valid_fixture():
    provenance = build_valid_provenance()
    result = candidate_record.validate_provenance(provenance)
    assert result == provenance or isinstance(result, dict)


@pytest.mark.parametrize(
    "required_field",
    ("origin", "extraction_method", "timestamp", "human_review_required"),
)
def test_validate_provenance_rejects_missing_required_field(required_field):
    provenance = build_valid_provenance()
    del provenance[required_field]
    assert_validation_rejects(
        candidate_record.validate_provenance,
        provenance,
        match=required_field,
    )


@pytest.mark.parametrize("origin", sorted(ALLOWED_PROVENANCE_ORIGINS))
def test_validate_provenance_accepts_allowed_origins(origin):
    provenance = build_valid_provenance(origin=origin)
    result = candidate_record.validate_provenance(provenance)
    assert result["origin"] == origin


def test_model_assisted_provenance_validates_without_runtime_call_fields():
    provenance = build_valid_provenance(
        origin="model_assisted",
        extraction_method="future_model_adapter",
    )
    result = candidate_record.validate_provenance(provenance)
    assert result["origin"] == "model_assisted"
    for forbidden_field in FORBIDDEN_PROVENANCE_RUNTIME_FIELDS:
        assert forbidden_field not in result


@pytest.mark.parametrize(
    "forbidden_field", sorted(FORBIDDEN_PROVENANCE_RUNTIME_FIELDS)
)
def test_validate_provenance_rejects_runtime_call_artifacts(forbidden_field):
    provenance = build_valid_provenance(**{forbidden_field: "runtime-artifact"})
    assert_validation_rejects(
        candidate_record.validate_provenance,
        provenance,
        match=forbidden_field,
    )


# ---------------------------------------------------------------------------
# Confidence and uncertainty contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("confidence", (0.0, 0.25, 1.0))
def test_validate_candidate_record_accepts_in_range_confidence(confidence):
    record = build_valid_candidate_record(confidence=confidence)
    result = candidate_record.validate_candidate_record(record)
    assert result["confidence"] == confidence


@pytest.mark.parametrize("confidence", (-0.01, 1.01, "high"))
def test_validate_candidate_record_rejects_invalid_confidence(confidence):
    record = build_valid_candidate_record(confidence=confidence)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="confidence",
    )


def test_validate_candidate_record_allows_omitted_uncertainty():
    record = build_valid_candidate_record()
    record.pop("uncertainty", None)
    result = candidate_record.validate_candidate_record(record)
    assert "uncertainty" not in result or result.get("uncertainty") is None


def test_validate_candidate_record_accepts_string_uncertainty():
    record = build_valid_candidate_record(uncertainty="needs owner review")
    result = candidate_record.validate_candidate_record(record)
    assert result["uncertainty"] == "needs owner review"


def test_validate_candidate_record_accepts_list_uncertainty():
    record = build_valid_candidate_record(
        uncertainty=["ambiguous source", "low evidence count"],
    )
    result = candidate_record.validate_candidate_record(record)
    assert result["uncertainty"] == ["ambiguous source", "low evidence count"]


@pytest.mark.parametrize("invalid_uncertainty", (123, {"reason": "x"}, [1, 2]))
def test_validate_candidate_record_rejects_invalid_uncertainty_shapes(
    invalid_uncertainty,
):
    record = build_valid_candidate_record(uncertainty=invalid_uncertainty)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="uncertainty",
    )


# ---------------------------------------------------------------------------
# Status, owner decision, and destination contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", sorted(STORED_STATUS_VALUES))
def test_validate_candidate_record_accepts_allowed_status_values(status):
    record = build_valid_candidate_record(status=status)
    result = candidate_record.validate_candidate_record(record)
    assert result["status"] == status


@pytest.mark.parametrize("forbidden_status", sorted(FORBIDDEN_STORED_STATUS_VALUES))
def test_validate_candidate_record_rejects_forbidden_promoted_status(
    forbidden_status,
):
    record = build_valid_candidate_record(status=forbidden_status)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="status",
    )


def test_approved_status_is_candidate_review_state_not_durable_truth():
    record = build_valid_candidate_record(status="approved")
    result = candidate_record.validate_candidate_record(record)
    assert result["status"] == "approved"
    assert result["destination"] != "write_to_canon"
    assert result["owner_decision"] != "promote"


@pytest.mark.parametrize("decision", sorted(STORED_OWNER_DECISION_VALUES))
def test_validate_candidate_record_accepts_allowed_owner_decisions(decision):
    record = build_valid_candidate_record(owner_decision=decision)
    result = candidate_record.validate_candidate_record(record)
    assert result["owner_decision"] == decision


@pytest.mark.parametrize(
    "forbidden_decision", sorted(FORBIDDEN_OWNER_DECISION_VALUES)
)
def test_validate_candidate_record_rejects_forbidden_promote_owner_decision(
    forbidden_decision,
):
    record = build_valid_candidate_record(owner_decision=forbidden_decision)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="owner_decision",
    )


def test_owner_decision_alone_does_not_imply_mutation():
    record = build_valid_candidate_record(owner_decision="approve")
    result = candidate_record.validate_candidate_record(record)
    assert result["owner_decision"] == "approve"
    assert result["status"] != "promoted"


@pytest.mark.parametrize(
    "destination", sorted(candidate_schema.CORE_DESTINATION_VALUES)
)
def test_validate_candidate_record_accepts_core_destination_values(destination):
    record = build_valid_candidate_record(destination=destination)
    result = candidate_record.validate_candidate_record(record)
    assert result["destination"] == destination


@pytest.mark.parametrize(
    "forbidden_destination", sorted(FORBIDDEN_DESTINATION_VALUES)
)
def test_validate_candidate_record_rejects_forbidden_destinations(
    forbidden_destination,
):
    record = build_valid_candidate_record(destination=forbidden_destination)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="destination",
    )


# ---------------------------------------------------------------------------
# Path-safety contract (IDs validated via validate_candidate_record)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_candidate_record_rejects_unsafe_candidate_id(unsafe_value):
    record = build_valid_candidate_record(candidate_id=unsafe_value)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="candidate_id",
    )


@pytest.mark.parametrize("unsafe_value", UNSAFE_ID_VALUES)
def test_validate_candidate_record_rejects_unsafe_project_id(unsafe_value):
    record = build_valid_candidate_record(project_id=unsafe_value)
    assert_validation_rejects(
        candidate_record.validate_candidate_record,
        record,
        match="project_id",
    )


def test_validate_candidate_record_accepts_path_safe_candidate_id():
    record = build_valid_candidate_record(
        candidate_id="core_candidate_scene_001_character_001",
    )
    result = candidate_record.validate_candidate_record(record)
    assert result["candidate_id"] == "core_candidate_scene_001_character_001"


# ---------------------------------------------------------------------------
# Source-level boundary contract (future helper module)
# ---------------------------------------------------------------------------


def test_candidate_record_module_source_has_no_forbidden_runtime_dependencies():
    module_source = inspect.getsource(candidate_record).lower()
    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source
