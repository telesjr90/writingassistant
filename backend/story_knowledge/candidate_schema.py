from types import MappingProxyType


CORE_CANDIDATE_TYPES = frozenset(
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
        "scene_event_causality_review_candidate",
    }
)

CORE_CANDIDATE_REQUIRED_FIELDS = frozenset(
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

CORE_SOURCE_LOCATOR_FIELDS = frozenset(
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

CORE_EVIDENCE_FIELDS = frozenset(
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

CORE_PROVENANCE_FIELDS = frozenset(
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

CORE_CANDIDATE_STATUS_VALUES = frozenset(
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

CORE_OWNER_DECISION_VALUES = frozenset(
    {
        "undecided",
        "approve",
        "reject",
        "needs_revision",
        "archive",
        "promote",
    }
)

CORE_DESTINATION_VALUES = frozenset(
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

CORE_CANDIDATE_TARGET_CATEGORIES = MappingProxyType(
    {
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
)

__all__ = (
    "CORE_CANDIDATE_TYPES",
    "CORE_CANDIDATE_REQUIRED_FIELDS",
    "CORE_SOURCE_LOCATOR_FIELDS",
    "CORE_EVIDENCE_FIELDS",
    "CORE_PROVENANCE_FIELDS",
    "CORE_CANDIDATE_STATUS_VALUES",
    "CORE_OWNER_DECISION_VALUES",
    "CORE_DESTINATION_VALUES",
    "CORE_CANDIDATE_TARGET_CATEGORIES",
)
