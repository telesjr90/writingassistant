import inspect
from types import MappingProxyType

from backend.story_knowledge import candidate_schema


EXPECTED_CORE_CANDIDATE_TYPES = frozenset(
    {
        "character_candidate",
        "location_candidate",
        "object_candidate",
        "organization_candidate",
        "timeline_event_candidate",
        "relationship_candidate",
        "plot_thread_candidate",
        "navigation_summary_candidate",
        "continuity_warning_candidate",
        "contradiction_candidate",
        "annotation_candidate",
        "open_question_candidate",
        # WORKSPACE-024 documents scene/event/action/causality review as a
        # required approved-memory category; the exact runtime split is deferred.
        "scene_event_causality_review_candidate",
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

EXPECTED_REQUIRED_FIELDS = frozenset(
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
    }
)

EXPECTED_SOURCE_LOCATOR_FIELDS = frozenset(
    {
        "project_id",
        "source_document_type",
        "source_document_id",
        "section_id",
        "chapter_id",
        "scene_id",
        "start_offset",
        "end_offset",
        "line_start",
        "line_end",
        "source_hash",
    }
)

FORBIDDEN_SOURCE_LOCATOR_FIELDS = frozenset(
    {
        "external_book_path",
        "training_file_path",
        "dataset_manifest_path",
        "absolute_filesystem_path",
    }
)

EXPECTED_EVIDENCE_FIELDS = frozenset(
    {
        "evidence_id",
        "source_locator",
        "source_text_excerpt",
        "summary",
        "supports_claim",
        "confidence",
        "notes",
    }
)

EXPECTED_PROVENANCE_FIELDS = frozenset(
    {
        "created_by",
        "source_type",
        "extraction_method",
        "origin",
        "timestamp",
        "updated_at",
        "source_hash",
        "snapshot_hash",
        "human_review_required",
        "owner_reviewed",
        "license_status",
    }
)

EXPECTED_STATUS_VALUES = frozenset(
    {
        "candidate",
        "owner_review",
        "approved",
        "rejected",
        "needs_revision",
        "archived",
        "promoted",
    }
)

EXPECTED_OWNER_DECISION_VALUES = frozenset(
    {
        "undecided",
        "approve",
        "reject",
        "needs_revision",
        "archive",
        "promote",
    }
)

EXPECTED_DESTINATION_VALUES = frozenset(
    {
        "omi_candidate_only",
        "project_memory_candidate",
        "character_memory_candidate",
        "location_memory_candidate",
        "object_memory_candidate",
        "organization_memory_candidate",
        "timeline_memory_candidate",
        "relationship_memory_candidate",
        "plot_thread_memory_candidate",
        "summary_index_candidate",
        "annotation_index_candidate",
        "open_question_index_candidate",
        "contradiction_memory_candidate",
        "discard",
    }
)

FORBIDDEN_DESTINATION_VALUES = frozenset(
    {
        "apply_promotion",
        "auto_promote",
        "write_to_canon",
        "mutate_memory",
        "rewrite_scene",
    }
)

EXPECTED_TARGET_CATEGORIES = {
    "character_candidate": "characters",
    "location_candidate": "locations_settings",
    "object_candidate": "objects_items",
    "organization_candidate": "organizations_groups",
    "timeline_event_candidate": "timeline",
    "relationship_candidate": "relationships",
    "plot_thread_candidate": "plot_threads",
    "navigation_summary_candidate": "navigation_summaries",
    "continuity_warning_candidate": "continuity_consistency",
    "contradiction_candidate": "contradictions",
    "annotation_candidate": "annotations_evidence_provenance",
    "open_question_candidate": "open_questions",
    "scene_event_causality_review_candidate": "scene_event_causality_review",
}

FORBIDDEN_SOURCE_TERMS = (
    "ollama",
    "requests",
    "httpx",
    "analysis_engine",
    "story-check",
    "story_check",
    "generate",
    "rewrite",
    "apply_promotion",
    "memory/",
    "canon",
    "openai",
    "spacy",
    "gliner",
    "booknlp",
    "training",
)


def _assert_constant_collection(value, *, name):
    assert isinstance(value, (tuple, frozenset)), f"{name} should be immutable"
    assert all(isinstance(item, str) for item in value), f"{name} must contain strings"
    assert len(value) == len(set(value)), f"{name} must not contain duplicates"
    return frozenset(value)


def _assert_constant_mapping(value, *, name):
    assert isinstance(
        value, (dict, MappingProxyType)
    ), f"{name} should be mapping metadata"
    assert value, f"{name} must not be empty"
    assert all(isinstance(key, str) for key in value), f"{name} keys must be strings"
    assert all(isinstance(item, str) for item in value.values()), (
        f"{name} values must be strings"
    )
    return dict(value)


def test_core_candidate_type_constants_are_stable_and_candidate_only():
    candidate_types = _assert_constant_collection(
        candidate_schema.CORE_CANDIDATE_TYPES,
        name="CORE_CANDIDATE_TYPES",
    )

    assert EXPECTED_CORE_CANDIDATE_TYPES <= candidate_types
    assert candidate_types.isdisjoint(FORBIDDEN_CANDIDATE_TYPES)


def test_required_base_fields_lock_identity_review_and_uncertainty_contract():
    required_fields = _assert_constant_collection(
        candidate_schema.CORE_CANDIDATE_REQUIRED_FIELDS,
        name="CORE_CANDIDATE_REQUIRED_FIELDS",
    )

    assert EXPECTED_REQUIRED_FIELDS <= required_fields


def test_source_locator_fields_are_project_local_and_do_not_require_external_files():
    source_locator_fields = _assert_constant_collection(
        candidate_schema.CORE_SOURCE_LOCATOR_FIELDS,
        name="CORE_SOURCE_LOCATOR_FIELDS",
    )

    assert EXPECTED_SOURCE_LOCATOR_FIELDS <= source_locator_fields
    assert source_locator_fields.isdisjoint(FORBIDDEN_SOURCE_LOCATOR_FIELDS)


def test_evidence_and_provenance_contract_is_explicit_before_extraction_runtime():
    evidence_fields = _assert_constant_collection(
        candidate_schema.CORE_EVIDENCE_FIELDS,
        name="CORE_EVIDENCE_FIELDS",
    )
    provenance_fields = _assert_constant_collection(
        candidate_schema.CORE_PROVENANCE_FIELDS,
        name="CORE_PROVENANCE_FIELDS",
    )

    assert EXPECTED_EVIDENCE_FIELDS <= evidence_fields
    assert EXPECTED_PROVENANCE_FIELDS <= provenance_fields


def test_lifecycle_decision_and_destination_values_are_candidate_safe():
    status_values = _assert_constant_collection(
        candidate_schema.CORE_CANDIDATE_STATUS_VALUES,
        name="CORE_CANDIDATE_STATUS_VALUES",
    )
    decision_values = _assert_constant_collection(
        candidate_schema.CORE_OWNER_DECISION_VALUES,
        name="CORE_OWNER_DECISION_VALUES",
    )
    destination_values = _assert_constant_collection(
        candidate_schema.CORE_DESTINATION_VALUES,
        name="CORE_DESTINATION_VALUES",
    )

    assert EXPECTED_STATUS_VALUES <= status_values
    assert EXPECTED_OWNER_DECISION_VALUES <= decision_values
    assert EXPECTED_DESTINATION_VALUES <= destination_values
    assert destination_values.isdisjoint(FORBIDDEN_DESTINATION_VALUES)


def test_candidate_types_map_to_review_or_memory_categories_without_approval_claims():
    target_categories = _assert_constant_mapping(
        candidate_schema.CORE_CANDIDATE_TARGET_CATEGORIES,
        name="CORE_CANDIDATE_TARGET_CATEGORIES",
    )

    assert set(EXPECTED_TARGET_CATEGORIES) <= set(target_categories)
    for candidate_type, target_category in EXPECTED_TARGET_CATEGORIES.items():
        assert target_categories[candidate_type] == target_category

    forbidden_fragments = ("approved_", "canon", "apply_promotion", "auto_promote")
    for target_category in target_categories.values():
        assert not any(fragment in target_category for fragment in forbidden_fragments)


def test_candidate_schema_module_source_has_no_runtime_or_generation_dependencies():
    module_source = inspect.getsource(candidate_schema).lower()

    for forbidden_term in FORBIDDEN_SOURCE_TERMS:
        assert forbidden_term not in module_source
