"""Pure T010B structural mapping contract for a validated NCP import.

The mapper accepts only a successful T010A value, revalidates its exact bytes,
and emits immutable, typed, in-memory structural mappings.  It does not build
or persist candidates, add T010C pointer/hash provenance, settle truth, mutate
project state, call runtimes, or transform source prose.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from backend.story_knowledge.ncp_import_contract import (
    NCP_APP_MAPPING_VERSION,
    NCP_UNKNOWN_FIELD_POLICY,
    SUPPORTED_NCP_SCHEMA_VERSION,
    NcpExternalStatusMetadata,
    NcpImportValidationError,
    NcpImportValidationResult,
    validate_ncp_import_artifact,
)


NCP_MAPPING_CONTRACT_VERSION = "writer-assistant-ncp-structural-mapping.v1"
NCP_MAPPING_CATEGORIES = (
    "ideation",
    "narrative",
    "perspective",
    "player",
    "dynamic",
    "storypoint",
    "storybeat",
    "moment",
    "setting",
    "overview",
    "authorial_intent",
    "metadata",
)
NCP_CATEGORY_STATES = frozenset({"mapped", "present_empty", "omitted"})
NCP_OMISSION_POLICY = "source_absence_or_empty_is_not_deletion"


class NcpMappingValidationError(ValueError):
    """Fail-closed error for an invalid or ambiguous T010B mapping input."""

    def __init__(self, code: str, source_path: tuple[str | int, ...], detail: str) -> None:
        self.code = code
        self.source_path = source_path
        self.detail = detail
        rendered = "/" + "/".join(str(part) for part in source_path)
        super().__init__(f"{code} at {rendered or '/'}: {detail}")


@dataclass(frozen=True)
class NcpMappingDefinition:
    category: str
    app_mapping_type: str
    source_path_templates: tuple[str, ...]
    mapped_field_names: tuple[str, ...]
    structural_child_fields: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "app_mapping_type": self.app_mapping_type,
            "source_path_templates": list(self.source_path_templates),
            "mapped_field_names": list(self.mapped_field_names),
            "structural_child_fields": list(self.structural_child_fields),
            "schema_version": SUPPORTED_NCP_SCHEMA_VERSION,
            "app_mapping_version": NCP_APP_MAPPING_VERSION,
            "omission_policy": NCP_OMISSION_POLICY,
            "candidate_type": None,
        }


NCP_MAPPING_DEFINITIONS = (
    NcpMappingDefinition(
        "ideation",
        "ncp_ideation_mapping",
        ("story.ideation.<kind>[]",),
        ("id", "name", "title", "summary", "description", "type", "kind", "value"),
    ),
    NcpMappingDefinition(
        "narrative",
        "ncp_narrative_mapping",
        ("story.narratives[]",),
        ("id", "title", "status"),
        ("subtext", "storytelling", "metadata"),
    ),
    NcpMappingDefinition(
        "perspective",
        "ncp_perspective_mapping",
        ("story.narratives[].subtext.perspectives[]",),
        ("id", "author_structural_pov", "summary", "storytelling"),
    ),
    NcpMappingDefinition(
        "player",
        "ncp_player_mapping",
        ("story.narratives[].subtext.players[]",),
        (
            "id", "name", "role", "summary", "bio", "storytelling",
            "perspectives", "visual", "audio", "motivations",
        ),
    ),
    NcpMappingDefinition(
        "dynamic",
        "ncp_dynamic_mapping",
        ("story.narratives[].subtext.dynamics[]",),
        ("id", "dynamic", "vector", "summary", "storytelling"),
    ),
    NcpMappingDefinition(
        "storypoint",
        "ncp_storypoint_mapping",
        ("story.narratives[].subtext.storypoints[]",),
        (
            "id", "appreciation", "narrative_function", "illustration",
            "summary", "storytelling", "throughline", "perspectives",
        ),
    ),
    NcpMappingDefinition(
        "storybeat",
        "ncp_storybeat_mapping",
        ("story.narratives[].subtext.storybeats[]",),
        (
            "id", "appreciation", "throughline", "scope", "sequence",
            "summary", "storytelling", "perspectives",
        ),
    ),
    NcpMappingDefinition(
        "moment",
        "ncp_moment_mapping",
        ("story.moments[]",),
        (
            "id", "title", "summary", "synopsis", "setting", "setting_id",
            "timing", "act", "order", "storybeats", "storypoints",
            "narrative_ids",
        ),
        ("imperatives", "metadata"),
    ),
    NcpMappingDefinition(
        "setting",
        "ncp_setting_mapping",
        ("story.settings[]",),
        ("id", "name", "title", "summary", "description", "metadata"),
    ),
    NcpMappingDefinition(
        "overview",
        "ncp_overview_mapping",
        ("story.narratives[].storytelling.overviews[]",),
        ("id", "name", "title", "summary", "description", "type", "kind"),
    ),
    NcpMappingDefinition(
        "authorial_intent",
        "ncp_authorial_intent_mapping",
        ("story.authorial_intent[]", "story.moments[].imperatives[]"),
        ("id", "name", "title", "summary", "description", "type", "kind", "value"),
    ),
    NcpMappingDefinition(
        "metadata",
        "ncp_metadata_mapping",
        (
            "schema_version",
            "story.<metadata-fields>",
            "story.metadata",
            "story.narratives[].metadata",
        ),
        (
            "schema_version", "id", "title", "genre", "logline", "created_at",
            "updated_at", "language", "locale", "version",
        ),
        ("narratives", "ideation", "moments", "settings", "authorial_intent", "metadata"),
    ),
)

_DEFINITION_BY_CATEGORY = {item.category: item for item in NCP_MAPPING_DEFINITIONS}
_OBJECT_ITEM_CATEGORIES = {
    "perspective", "player", "dynamic", "storypoint", "storybeat",
    "moment", "setting", "overview",
}


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _safe_source_scalar(value: object, path: tuple[str | int, ...]) -> None:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise NcpMappingValidationError(
            "invalid_mapping_item", path, "source scalar must be non-empty text without NUL"
        )


@dataclass(frozen=True)
class NcpMappedStructuralRecord:
    mapping_record_id: str
    category: str
    app_mapping_type: str
    source_path: tuple[str | int, ...]
    source_value_json: str
    mapped_field_names: tuple[str, ...]
    preserved_uninterpreted_field_names: tuple[str, ...]
    candidate_record: bool = False
    local_approval: bool = False
    deletion_intent: bool = False

    @property
    def source_value(self) -> object:
        return json.loads(self.source_value_json)

    def to_dict(self) -> dict[str, object]:
        return {
            "mapping_record_id": self.mapping_record_id,
            "category": self.category,
            "app_mapping_type": self.app_mapping_type,
            "source_path": list(self.source_path),
            "source_value": self.source_value,
            "mapped_field_names": list(self.mapped_field_names),
            "preserved_uninterpreted_field_names": list(
                self.preserved_uninterpreted_field_names
            ),
            "candidate_record": self.candidate_record,
            "local_approval": self.local_approval,
            "deletion_intent": self.deletion_intent,
            "json_pointer_provenance": None,
            "source_value_hash": None,
        }


@dataclass(frozen=True)
class NcpMappingCategoryState:
    category: str
    state: str
    record_count: int
    deletion_intent: bool = False
    omission_policy: str = NCP_OMISSION_POLICY

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "state": self.state,
            "record_count": self.record_count,
            "deletion_intent": self.deletion_intent,
            "omission_policy": self.omission_policy,
        }


@dataclass(frozen=True)
class NcpMappingSafetyBoundary:
    in_memory_only: bool = True
    validated_t010a_input_required: bool = True
    candidate_construction_performed: bool = False
    candidate_write_performed: bool = False
    review_write_performed: bool = False
    project_state_write_performed: bool = False
    approval_performed: bool = False
    promotion_performed: bool = False
    apply_promotion_performed: bool = False
    memory_write_performed: bool = False
    canon_write_performed: bool = False
    generated_prose: bool = False
    prose_transformation: bool = False
    live_ncp_execution: bool = False
    node_execution: bool = False
    npm_execution: bool = False
    subprocess_execution: bool = False
    network_execution: bool = False
    model_execution: bool = False
    diagnostic_state_settled: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class NcpStructuralMappingResult:
    mapping_id: str
    mapping_hash: str
    source_validation_id: str
    source_validation_hash: str
    artifact_id: str
    story_id: str
    definitions: tuple[NcpMappingDefinition, ...]
    records: tuple[NcpMappedStructuralRecord, ...]
    category_states: tuple[NcpMappingCategoryState, ...]
    external_narrative_statuses: tuple[NcpExternalStatusMetadata, ...]
    preserved_uninterpreted_top_level_pointers: tuple[str, ...]
    safety_boundary: NcpMappingSafetyBoundary
    contract_version: str = NCP_MAPPING_CONTRACT_VERSION
    ncp_schema_version: str = SUPPORTED_NCP_SCHEMA_VERSION
    app_mapping_version: str = NCP_APP_MAPPING_VERSION
    unknown_field_policy: str = NCP_UNKNOWN_FIELD_POLICY

    def _hash_material(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "ncp_schema_version": self.ncp_schema_version,
            "app_mapping_version": self.app_mapping_version,
            "source_validation_id": self.source_validation_id,
            "source_validation_hash": self.source_validation_hash,
            "artifact_id": self.artifact_id,
            "story_id": self.story_id,
            "definitions": [item.to_dict() for item in self.definitions],
            "records": [item.to_dict() for item in self.records],
            "category_states": [item.to_dict() for item in self.category_states],
            "external_narrative_statuses": [
                item.to_dict() for item in self.external_narrative_statuses
            ],
            "preserved_uninterpreted_top_level_pointers": list(
                self.preserved_uninterpreted_top_level_pointers
            ),
            "unknown_field_policy": self.unknown_field_policy,
            "safety_boundary": self.safety_boundary.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        value = self._hash_material()
        value["mapping_id"] = self.mapping_id
        value["mapping_hash"] = self.mapping_hash
        return value


def _build_record(
    *,
    artifact_id: str,
    category: str,
    source_path: tuple[str | int, ...],
    source_value: object,
) -> NcpMappedStructuralRecord:
    definition = _DEFINITION_BY_CATEGORY[category]
    source_value_json = _canonical_json(source_value)
    if isinstance(source_value, dict):
        recognized = set(definition.mapped_field_names) | set(
            definition.structural_child_fields
        )
        mapped_fields = tuple(
            field for field in definition.mapped_field_names if field in source_value
        )
        uninterpreted = tuple(sorted(set(source_value) - recognized))
    else:
        mapped_fields = ("value",)
        uninterpreted = ()
    identity_material = {
        "artifact_id": artifact_id,
        "app_mapping_version": NCP_APP_MAPPING_VERSION,
        "category": category,
        "source_path": list(source_path),
    }
    digest = hashlib.sha256(_canonical_json(identity_material).encode("utf-8")).hexdigest()
    return NcpMappedStructuralRecord(
        mapping_record_id=f"ncp-map-{category}-{digest[:32]}",
        category=category,
        app_mapping_type=definition.app_mapping_type,
        source_path=source_path,
        source_value_json=source_value_json,
        mapped_field_names=mapped_fields,
        preserved_uninterpreted_field_names=uninterpreted,
    )


def _require_optional_object(
    parent: dict[str, Any], key: str, path: tuple[str | int, ...]
) -> dict[str, Any] | None:
    if key not in parent:
        return None
    value = parent[key]
    if not isinstance(value, dict):
        raise NcpMappingValidationError(
            "malformed_category_shape", path + (key,), "category container must be an object"
        )
    return value


def _require_optional_list(
    parent: dict[str, Any], key: str, path: tuple[str | int, ...]
) -> list[Any] | None:
    if key not in parent:
        return None
    value = parent[key]
    if not isinstance(value, list):
        raise NcpMappingValidationError(
            "malformed_category_shape", path + (key,), "category container must be an array"
        )
    return value


def _append_object_records(
    *,
    artifact_id: str,
    category: str,
    items: list[Any],
    base_path: tuple[str | int, ...],
    records: list[NcpMappedStructuralRecord],
    seen_ids: dict[str, set[str]],
) -> None:
    for index, item in enumerate(items):
        path = base_path + (index,)
        if not isinstance(item, dict):
            raise NcpMappingValidationError(
                "malformed_category_item", path, f"{category} item must be an object"
            )
        identifier = item.get("id")
        _safe_source_scalar(identifier, path + ("id",))
        if identifier in seen_ids[category]:
            raise NcpMappingValidationError(
                "ambiguous_category_id", path + ("id",), f"duplicate {category} ID"
            )
        seen_ids[category].add(identifier)
        records.append(
            _build_record(
                artifact_id=artifact_id,
                category=category,
                source_path=path,
                source_value=item,
            )
        )


def _append_scalar_or_object_records(
    *,
    artifact_id: str,
    category: str,
    items: list[Any],
    base_path: tuple[str | int, ...],
    records: list[NcpMappedStructuralRecord],
) -> None:
    for index, item in enumerate(items):
        path = base_path + (index,)
        if isinstance(item, str):
            _safe_source_scalar(item, path)
        elif not isinstance(item, dict) or not item:
            raise NcpMappingValidationError(
                "malformed_category_item",
                path,
                f"{category} item must be non-empty text or an object",
            )
        records.append(
            _build_record(
                artifact_id=artifact_id,
                category=category,
                source_path=path,
                source_value=item,
            )
        )


def map_validated_ncp_import(
    validated_import: NcpImportValidationResult,
) -> NcpStructuralMappingResult:
    """Map exact T010A-validated bytes into typed T010B structural values."""

    if not isinstance(validated_import, NcpImportValidationResult):
        raise NcpMappingValidationError(
            "validated_t010a_result_required",
            (),
            "mapping accepts only a successful T010A validation result",
        )
    try:
        revalidated = validate_ncp_import_artifact(
            validated_import.artifact.original_bytes,
            project_id=validated_import.project_id,
            source_reference=validated_import.artifact.source_reference,
            media_type=validated_import.artifact.media_type,
        )
    except NcpImportValidationError as exc:
        raise NcpMappingValidationError(
            "t010a_revalidation_failed", (), "exact artifact no longer passes T010A"
        ) from exc
    if revalidated != validated_import:
        raise NcpMappingValidationError(
            "t010a_validation_mismatch",
            (),
            "supplied result does not match deterministic T010A validation",
        )

    parsed = json.loads(revalidated.artifact.original_text)
    story = parsed["story"]
    artifact_id = revalidated.artifact.artifact_id
    records: list[NcpMappedStructuralRecord] = []
    present = {category: False for category in NCP_MAPPING_CATEGORIES}
    seen_ids = {category: set() for category in _OBJECT_ITEM_CATEGORIES}

    present["metadata"] = True
    records.append(
        _build_record(
            artifact_id=artifact_id,
            category="metadata",
            source_path=("schema_version",),
            source_value=parsed["schema_version"],
        )
    )
    records.append(
        _build_record(
            artifact_id=artifact_id,
            category="metadata",
            source_path=("story",),
            source_value=story,
        )
    )
    story_metadata = _require_optional_object(story, "metadata", ("story",))
    if story_metadata is not None:
        records.append(
            _build_record(
                artifact_id=artifact_id,
                category="metadata",
                source_path=("story", "metadata"),
                source_value=story_metadata,
            )
        )

    ideation = _require_optional_object(story, "ideation", ("story",))
    if ideation is not None:
        present["ideation"] = True
        for kind in sorted(ideation):
            values = ideation[kind]
            if not isinstance(values, list):
                raise NcpMappingValidationError(
                    "malformed_category_shape",
                    ("story", "ideation", kind),
                    "ideation kind must contain an array",
                )
            _append_scalar_or_object_records(
                artifact_id=artifact_id,
                category="ideation",
                items=values,
                base_path=("story", "ideation", kind),
                records=records,
            )

    narratives = story["narratives"]
    present["narrative"] = True
    for narrative_index, narrative in enumerate(narratives):
        narrative_path = ("story", "narratives", narrative_index)
        records.append(
            _build_record(
                artifact_id=artifact_id,
                category="narrative",
                source_path=narrative_path,
                source_value=narrative,
            )
        )
        narrative_metadata = _require_optional_object(
            narrative, "metadata", narrative_path
        )
        if narrative_metadata is not None:
            records.append(
                _build_record(
                    artifact_id=artifact_id,
                    category="metadata",
                    source_path=narrative_path + ("metadata",),
                    source_value=narrative_metadata,
                )
            )

        subtext = _require_optional_object(narrative, "subtext", narrative_path)
        if subtext is not None:
            for category in (
                "perspective", "player", "dynamic", "storypoint", "storybeat"
            ):
                container_key = f"{category}s"
                items = _require_optional_list(
                    subtext, container_key, narrative_path + ("subtext",)
                )
                if items is None:
                    continue
                present[category] = True
                _append_object_records(
                    artifact_id=artifact_id,
                    category=category,
                    items=items,
                    base_path=narrative_path + ("subtext", container_key),
                    records=records,
                    seen_ids=seen_ids,
                )

        storytelling = _require_optional_object(
            narrative, "storytelling", narrative_path
        )
        if storytelling is not None:
            overviews = _require_optional_list(
                storytelling, "overviews", narrative_path + ("storytelling",)
            )
            if overviews is not None:
                present["overview"] = True
                _append_object_records(
                    artifact_id=artifact_id,
                    category="overview",
                    items=overviews,
                    base_path=narrative_path + ("storytelling", "overviews"),
                    records=records,
                    seen_ids=seen_ids,
                )

    settings = _require_optional_list(story, "settings", ("story",))
    if settings is not None:
        present["setting"] = True
        _append_object_records(
            artifact_id=artifact_id,
            category="setting",
            items=settings,
            base_path=("story", "settings"),
            records=records,
            seen_ids=seen_ids,
        )

    moments = _require_optional_list(story, "moments", ("story",))
    if moments is not None:
        present["moment"] = True
        _append_object_records(
            artifact_id=artifact_id,
            category="moment",
            items=moments,
            base_path=("story", "moments"),
            records=records,
            seen_ids=seen_ids,
        )
        for moment_index, moment in enumerate(moments):
            imperatives = _require_optional_list(
                moment, "imperatives", ("story", "moments", moment_index)
            )
            if imperatives is None:
                continue
            present["authorial_intent"] = True
            _append_scalar_or_object_records(
                artifact_id=artifact_id,
                category="authorial_intent",
                items=imperatives,
                base_path=("story", "moments", moment_index, "imperatives"),
                records=records,
            )

    authorial_intent = _require_optional_list(
        story, "authorial_intent", ("story",)
    )
    if authorial_intent is not None:
        present["authorial_intent"] = True
        _append_scalar_or_object_records(
            artifact_id=artifact_id,
            category="authorial_intent",
            items=authorial_intent,
            base_path=("story", "authorial_intent"),
            records=records,
        )

    category_rank = {category: index for index, category in enumerate(NCP_MAPPING_CATEGORIES)}
    records.sort(
        key=lambda item: (
            category_rank[item.category],
            tuple(str(part) for part in item.source_path),
        )
    )
    record_counts = {
        category: sum(record.category == category for record in records)
        for category in NCP_MAPPING_CATEGORIES
    }
    states = tuple(
        NcpMappingCategoryState(
            category=category,
            state=(
                "mapped"
                if record_counts[category]
                else "present_empty"
                if present[category]
                else "omitted"
            ),
            record_count=record_counts[category],
        )
        for category in NCP_MAPPING_CATEGORIES
    )
    statuses = revalidated.external_narrative_statuses
    safety = NcpMappingSafetyBoundary()
    provisional = NcpStructuralMappingResult(
        mapping_id="pending",
        mapping_hash="pending",
        source_validation_id=revalidated.validation_id,
        source_validation_hash=revalidated.validation_hash,
        artifact_id=artifact_id,
        story_id=revalidated.story_id,
        definitions=NCP_MAPPING_DEFINITIONS,
        records=tuple(records),
        category_states=states,
        external_narrative_statuses=statuses,
        preserved_uninterpreted_top_level_pointers=(
            revalidated.preserved_uninterpreted_top_level_pointers
        ),
        safety_boundary=safety,
    )
    mapping_hash = hashlib.sha256(
        _canonical_json(provisional._hash_material()).encode("utf-8")
    ).hexdigest()
    return NcpStructuralMappingResult(
        mapping_id=f"ncp-structural-mapping-{mapping_hash[:32]}",
        mapping_hash=mapping_hash,
        source_validation_id=provisional.source_validation_id,
        source_validation_hash=provisional.source_validation_hash,
        artifact_id=provisional.artifact_id,
        story_id=provisional.story_id,
        definitions=provisional.definitions,
        records=provisional.records,
        category_states=provisional.category_states,
        external_narrative_statuses=provisional.external_narrative_statuses,
        preserved_uninterpreted_top_level_pointers=(
            provisional.preserved_uninterpreted_top_level_pointers
        ),
        safety_boundary=provisional.safety_boundary,
    )
