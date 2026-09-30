"""Pure read-only causal, timeline, and thread diagnostic contracts.

The builders in this module consume an already validated T009A project
diagnostic context and emit deterministic support-only records.  They perform
no I/O, persistence, runtime execution, promotion, project mutation, or story
prose generation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from backend.story_knowledge.project_diagnostic_context import (
    PROJECT_DIAGNOSTIC_CONTEXT_VERSION,
    SUPPORT_CLASSIFICATIONS,
    UNCERTAINTY_CLASSIFICATIONS,
    validate_project_diagnostic_context,
)


PROJECT_NARRATIVE_DIAGNOSTIC_VERSION = "project-narrative-diagnostic.v1"
PROJECT_DIAGNOSTIC_CONTEXT_REFERENCE_VERSION = (
    "project-diagnostic-context-reference.v1"
)

DIAGNOSTIC_KINDS = frozenset(
    {"causal_continuity", "chronology_timeline", "thread_activity"}
)
CAUSAL_ASSESSMENTS = frozenset(
    {
        "supported_link",
        "potential_gap",
        "conflict",
        "ambiguous",
        "insufficient_evidence",
    }
)
TIMELINE_ASSESSMENTS = frozenset(
    {"supported_ordering", "conflict", "ambiguous", "insufficient_evidence"}
)
THREAD_ACTIVITY_CLASSIFICATIONS = frozenset({"active", "inactive", "uncertain"})

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_AUTHORITATIVE_BOUNDARY = {
    "mode": "read_only_non_authoritative",
    "truth_status": "not_settled",
    "canon_status": "not_selected",
    "world_state_status": "not_settled",
    "chronology_status": "not_canonical",
    "causality_status": "not_canonical",
    "thread_status": "diagnostic_only",
    "relationship_status": "not_settled",
    "emotional_status": "not_settled",
    "author_intent_status": "not_inferred",
    "approved_memory_status": "not_established",
    "owner_control": "required",
}
_BEHAVIOR_BOUNDARY = {
    "persistence": "none",
    "runtime_execution": "none",
    "story_prose_output": "forbidden",
    "promotion": "none",
    "apply_promotion": "none",
    "memory_canon_mutation": "none",
}


class ProjectNarrativeDiagnosticValidationError(ValueError):
    """Raised when a narrative diagnostic is unsafe or unsupported."""


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _fail(message: str, exc: Exception | None = None) -> None:
    error = ProjectNarrativeDiagnosticValidationError(message)
    if exc is None:
        raise error
    raise error from exc


def _closed_object(
    value: Any,
    *,
    required: set[str],
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != required:
        _fail(f"{label} fields are not closed")
    return copy.deepcopy(dict(value))


def _safe_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value) or ".." in value:
        _fail(f"{label} must be a safe identifier")
    return value


def _id_list(value: Any, label: str, *, non_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (non_empty and not value):
        qualifier = "non-empty " if non_empty else ""
        _fail(f"{label} must be a {qualifier}list")
    checked = [_safe_id(item, label) for item in value]
    if len(checked) != len(set(checked)):
        _fail(f"{label} contains duplicates")
    return sorted(checked)


def _snapshot_id(source: Mapping[str, Any]) -> str:
    if "source_snapshot" in source:
        return source["source_snapshot"]["identity"]["snapshot_id"]
    return source["source_identity"]["snapshot_id"]


def _context_indexes(context: Mapping[str, Any]) -> dict[str, Any]:
    try:
        validated = validate_project_diagnostic_context(context)
    except (TypeError, ValueError) as exc:
        _fail("diagnostic requires a valid T009A project context", exc)
    return {
        "context": validated,
        "source_ids": {_snapshot_id(source) for source in validated["sources"]},
        "evidence": {
            record["evidence_id"]: record for record in validated["evidence_records"]
        },
        "support": {
            reference["support_reference_id"]: reference
            for reference in validated["diagnostic_support_references"]
        },
        "approved": {
            snapshot["context_snapshot_id"]: snapshot
            for snapshot in validated["approved_context_snapshots"]
        },
    }


def _diagnostic_payload(kind: str, payload: Any) -> dict[str, Any]:
    if kind == "causal_continuity":
        item = _closed_object(
            payload,
            required={"cause_event_ref", "effect_event_ref", "assessment"},
            label="causal diagnostic payload",
        )
        _safe_id(item["cause_event_ref"], "cause_event_ref")
        _safe_id(item["effect_event_ref"], "effect_event_ref")
        if item["cause_event_ref"] == item["effect_event_ref"]:
            _fail("causal diagnostic requires distinct event references")
        if item["assessment"] not in CAUSAL_ASSESSMENTS:
            _fail("causal assessment is not allowed")
        return item
    if kind == "chronology_timeline":
        item = _closed_object(
            payload,
            required={"earlier_event_ref", "later_event_ref", "assessment"},
            label="timeline diagnostic payload",
        )
        _safe_id(item["earlier_event_ref"], "earlier_event_ref")
        _safe_id(item["later_event_ref"], "later_event_ref")
        if item["earlier_event_ref"] == item["later_event_ref"]:
            _fail("timeline diagnostic requires distinct event references")
        if item["assessment"] not in TIMELINE_ASSESSMENTS:
            _fail("timeline assessment is not allowed")
        return item
    if kind == "thread_activity":
        item = _closed_object(
            payload,
            required={"thread_ref", "activity_classification"},
            label="thread diagnostic payload",
        )
        _safe_id(item["thread_ref"], "thread_ref")
        if item["activity_classification"] not in THREAD_ACTIVITY_CLASSIFICATIONS:
            _fail("thread activity classification is not allowed")
        return item
    _fail("diagnostic_kind is not allowed")


def _derive_lineage(
    indexes: Mapping[str, Any],
    evidence_ids: Sequence[str],
    support_ids: Sequence[str],
    approved_ids: Sequence[str],
) -> dict[str, list[str]]:
    run_ids = {indexes["evidence"][item]["run_id"] for item in evidence_ids}
    provenance_ids: set[str] = set()
    for support_id in support_ids:
        support = indexes["support"][support_id]
        run_ids.add(support["run_id"])
        provenance_ids.update(support["provenance_reference_ids"])
    for approved_id in approved_ids:
        approved = indexes["approved"][approved_id]["approved_record"]
        provenance_ids.update(
            reference["provenance_id"] for reference in approved["provenance_refs"]
        )
    return {
        "run_ids": sorted(run_ids),
        "provenance_reference_ids": sorted(provenance_ids),
    }


def _enforce_support_semantics(
    *,
    kind: str,
    payload: Mapping[str, Any],
    evidence_ids: Sequence[str],
    support_classification: str,
    uncertainty_classification: str,
) -> None:
    assessment = payload.get("assessment")
    assertive = assessment in {
        "supported_link",
        "potential_gap",
        "conflict",
        "supported_ordering",
    }
    if assertive and not evidence_ids:
        _fail("assertive causal or timeline diagnostics require evidence")
    if assessment == "conflict" and uncertainty_classification != "conflicting":
        _fail("conflict diagnostics require conflicting uncertainty")
    if assessment == "ambiguous" and uncertainty_classification != "ambiguous":
        _fail("ambiguous diagnostics require ambiguous uncertainty")
    if assessment == "insufficient_evidence" and (
        support_classification != "insufficient_evidence"
        or uncertainty_classification != "insufficient_evidence"
    ):
        _fail("insufficient-evidence diagnostics require explicit uncertainty")

    if kind != "thread_activity":
        return
    activity = payload["activity_classification"]
    if activity in {"active", "inactive"}:
        if not evidence_ids:
            _fail("active or inactive thread classification requires evidence")
        if support_classification != "supported":
            _fail("active or inactive thread classification requires supported evidence")
    elif not evidence_ids and (
        support_classification != "insufficient_evidence"
        or uncertainty_classification != "insufficient_evidence"
    ):
        _fail("unsupported thread activity requires explicit uncertainty")
    elif evidence_ids and uncertainty_classification not in {
        "ambiguous",
        "conflicting",
        "insufficient_evidence",
    }:
        _fail("uncertain thread activity requires an explicit uncertainty class")


def build_project_narrative_diagnostic(
    *,
    context: Mapping[str, Any],
    diagnostic_kind: str,
    source_snapshot_ids: Sequence[str],
    payload: Mapping[str, Any],
    evidence_reference_ids: Sequence[str] = (),
    diagnostic_support_reference_ids: Sequence[str] = (),
    approved_context_snapshot_ids: Sequence[str] = (),
    support_classification: str,
    uncertainty_classification: str,
) -> dict[str, Any]:
    """Build one deterministic diagnostic from references already in T009A."""

    indexes = _context_indexes(context)
    validated_context = indexes["context"]
    context_hash = hashlib.sha256(_canonical_json_bytes(validated_context)).hexdigest()
    record = {
        "schema_version": PROJECT_NARRATIVE_DIAGNOSTIC_VERSION,
        "diagnostic_id": "pending",
        "diagnostic_kind": diagnostic_kind,
        "project_id": validated_context["project_id"],
        "context_reference": {
            "schema_version": PROJECT_DIAGNOSTIC_CONTEXT_REFERENCE_VERSION,
            "context_schema_version": PROJECT_DIAGNOSTIC_CONTEXT_VERSION,
            "project_id": validated_context["project_id"],
            "context_sha256": context_hash,
        },
        "source_snapshot_ids": list(source_snapshot_ids),
        "evidence_reference_ids": list(evidence_reference_ids),
        "diagnostic_support_reference_ids": list(
            diagnostic_support_reference_ids
        ),
        "approved_context_snapshot_ids": list(approved_context_snapshot_ids),
        "lineage": {"run_ids": [], "provenance_reference_ids": []},
        "support_classification": support_classification,
        "uncertainty_classification": uncertainty_classification,
        "payload": copy.deepcopy(dict(payload)),
        "authority": copy.deepcopy(_AUTHORITATIVE_BOUNDARY),
        "behavior": copy.deepcopy(_BEHAVIOR_BOUNDARY),
    }
    try:
        record["lineage"] = _derive_lineage(
            indexes,
            list(evidence_reference_ids),
            list(diagnostic_support_reference_ids),
            list(approved_context_snapshot_ids),
        )
    except KeyError as exc:
        _fail("diagnostic basis contains an unknown context reference", exc)
    normalized = _validate_without_id(record, indexes)
    material = copy.deepcopy(normalized)
    material.pop("diagnostic_id")
    normalized["diagnostic_id"] = (
        "narrative-diagnostic-"
        + hashlib.sha256(_canonical_json_bytes(material)).hexdigest()
    )
    return validate_project_narrative_diagnostic(normalized, validated_context)


def build_causal_continuity_diagnostic(
    *,
    context: Mapping[str, Any],
    source_snapshot_ids: Sequence[str],
    cause_event_ref: str,
    effect_event_ref: str,
    assessment: str,
    evidence_reference_ids: Sequence[str] = (),
    diagnostic_support_reference_ids: Sequence[str] = (),
    approved_context_snapshot_ids: Sequence[str] = (),
    support_classification: str,
    uncertainty_classification: str,
) -> dict[str, Any]:
    return build_project_narrative_diagnostic(
        context=context,
        diagnostic_kind="causal_continuity",
        source_snapshot_ids=source_snapshot_ids,
        payload={
            "cause_event_ref": cause_event_ref,
            "effect_event_ref": effect_event_ref,
            "assessment": assessment,
        },
        evidence_reference_ids=evidence_reference_ids,
        diagnostic_support_reference_ids=diagnostic_support_reference_ids,
        approved_context_snapshot_ids=approved_context_snapshot_ids,
        support_classification=support_classification,
        uncertainty_classification=uncertainty_classification,
    )


def build_timeline_diagnostic(
    *,
    context: Mapping[str, Any],
    source_snapshot_ids: Sequence[str],
    earlier_event_ref: str,
    later_event_ref: str,
    assessment: str,
    evidence_reference_ids: Sequence[str] = (),
    diagnostic_support_reference_ids: Sequence[str] = (),
    approved_context_snapshot_ids: Sequence[str] = (),
    support_classification: str,
    uncertainty_classification: str,
) -> dict[str, Any]:
    return build_project_narrative_diagnostic(
        context=context,
        diagnostic_kind="chronology_timeline",
        source_snapshot_ids=source_snapshot_ids,
        payload={
            "earlier_event_ref": earlier_event_ref,
            "later_event_ref": later_event_ref,
            "assessment": assessment,
        },
        evidence_reference_ids=evidence_reference_ids,
        diagnostic_support_reference_ids=diagnostic_support_reference_ids,
        approved_context_snapshot_ids=approved_context_snapshot_ids,
        support_classification=support_classification,
        uncertainty_classification=uncertainty_classification,
    )


def build_thread_activity_diagnostic(
    *,
    context: Mapping[str, Any],
    source_snapshot_ids: Sequence[str],
    thread_ref: str,
    activity_classification: str,
    evidence_reference_ids: Sequence[str] = (),
    diagnostic_support_reference_ids: Sequence[str] = (),
    approved_context_snapshot_ids: Sequence[str] = (),
    support_classification: str,
    uncertainty_classification: str,
) -> dict[str, Any]:
    return build_project_narrative_diagnostic(
        context=context,
        diagnostic_kind="thread_activity",
        source_snapshot_ids=source_snapshot_ids,
        payload={
            "thread_ref": thread_ref,
            "activity_classification": activity_classification,
        },
        evidence_reference_ids=evidence_reference_ids,
        diagnostic_support_reference_ids=diagnostic_support_reference_ids,
        approved_context_snapshot_ids=approved_context_snapshot_ids,
        support_classification=support_classification,
        uncertainty_classification=uncertainty_classification,
    )


def _validate_without_id(
    value: Any, indexes: Mapping[str, Any]
) -> dict[str, Any]:
    item = _closed_object(
        value,
        required={
            "schema_version",
            "diagnostic_id",
            "diagnostic_kind",
            "project_id",
            "context_reference",
            "source_snapshot_ids",
            "evidence_reference_ids",
            "diagnostic_support_reference_ids",
            "approved_context_snapshot_ids",
            "lineage",
            "support_classification",
            "uncertainty_classification",
            "payload",
            "authority",
            "behavior",
        },
        label="project narrative diagnostic",
    )
    if item["schema_version"] != PROJECT_NARRATIVE_DIAGNOSTIC_VERSION:
        _fail("unsupported project narrative diagnostic schema_version")
    if item["diagnostic_kind"] not in DIAGNOSTIC_KINDS:
        _fail("diagnostic_kind is not allowed")
    context = indexes["context"]
    if item["project_id"] != context["project_id"]:
        _fail("diagnostic project_id does not match its context")

    context_reference = _closed_object(
        item["context_reference"],
        required={
            "schema_version",
            "context_schema_version",
            "project_id",
            "context_sha256",
        },
        label="diagnostic context reference",
    )
    expected_hash = hashlib.sha256(_canonical_json_bytes(context)).hexdigest()
    if (
        context_reference["schema_version"]
        != PROJECT_DIAGNOSTIC_CONTEXT_REFERENCE_VERSION
        or context_reference["context_schema_version"]
        != PROJECT_DIAGNOSTIC_CONTEXT_VERSION
        or context_reference["project_id"] != context["project_id"]
        or not isinstance(context_reference["context_sha256"], str)
        or not _SHA256.fullmatch(context_reference["context_sha256"])
        or context_reference["context_sha256"] != expected_hash
    ):
        _fail("diagnostic context reference does not match the T009A context")

    source_ids = _id_list(
        item["source_snapshot_ids"], "source_snapshot_ids", non_empty=True
    )
    if not set(source_ids) <= indexes["source_ids"]:
        _fail("diagnostic references an unknown source snapshot")
    evidence_ids = _id_list(item["evidence_reference_ids"], "evidence_reference_ids")
    if not set(evidence_ids) <= set(indexes["evidence"]):
        _fail("diagnostic references unknown evidence")
    support_ids = _id_list(
        item["diagnostic_support_reference_ids"],
        "diagnostic_support_reference_ids",
    )
    if not set(support_ids) <= set(indexes["support"]):
        _fail("diagnostic references unknown support")
    approved_ids = _id_list(
        item["approved_context_snapshot_ids"], "approved_context_snapshot_ids"
    )
    if not set(approved_ids) <= set(indexes["approved"]):
        _fail("diagnostic references unknown approved context")

    for evidence_id in evidence_ids:
        snapshot_id = indexes["evidence"][evidence_id]["source_identity"][
            "snapshot_id"
        ]
        if snapshot_id not in source_ids:
            _fail("diagnostic evidence crosses an undeclared source boundary")
    for support_id in support_ids:
        if not set(indexes["support"][support_id]["source_snapshot_ids"]) <= set(
            source_ids
        ):
            _fail("diagnostic support crosses an undeclared source boundary")
    for approved_id in approved_ids:
        if not set(indexes["approved"][approved_id]["source_snapshot_ids"]) <= set(
            source_ids
        ):
            _fail("approved context crosses an undeclared source boundary")

    if item["support_classification"] not in SUPPORT_CLASSIFICATIONS:
        _fail("support_classification is not allowed")
    if item["uncertainty_classification"] not in UNCERTAINTY_CLASSIFICATIONS:
        _fail("uncertainty_classification is not allowed")
    payload = _diagnostic_payload(item["diagnostic_kind"], item["payload"])
    _enforce_support_semantics(
        kind=item["diagnostic_kind"],
        payload=payload,
        evidence_ids=evidence_ids,
        support_classification=item["support_classification"],
        uncertainty_classification=item["uncertainty_classification"],
    )

    lineage = _closed_object(
        item["lineage"],
        required={"run_ids", "provenance_reference_ids"},
        label="diagnostic lineage",
    )
    expected_lineage = _derive_lineage(indexes, evidence_ids, support_ids, approved_ids)
    if lineage != expected_lineage:
        _fail("diagnostic run/provenance lineage does not match its basis")
    if item["authority"] != _AUTHORITATIVE_BOUNDARY:
        _fail("diagnostic authority cannot be weakened")
    if item["behavior"] != _BEHAVIOR_BOUNDARY:
        _fail("diagnostic behavior cannot be weakened")

    item["context_reference"] = context_reference
    item["source_snapshot_ids"] = source_ids
    item["evidence_reference_ids"] = evidence_ids
    item["diagnostic_support_reference_ids"] = support_ids
    item["approved_context_snapshot_ids"] = approved_ids
    item["lineage"] = expected_lineage
    item["payload"] = payload
    return item


def validate_project_narrative_diagnostic(
    value: Any, context: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate one closed record against its exact T009A context."""

    indexes = _context_indexes(context)
    item = _validate_without_id(value, indexes)
    _safe_id(item["diagnostic_id"], "diagnostic_id")
    material = copy.deepcopy(item)
    material.pop("diagnostic_id")
    expected_id = (
        "narrative-diagnostic-"
        + hashlib.sha256(_canonical_json_bytes(material)).hexdigest()
    )
    if item["diagnostic_id"] != expected_id:
        _fail("diagnostic_id does not match deterministic diagnostic content")
    return item


def serialize_project_narrative_diagnostic(
    value: Any, context: Mapping[str, Any]
) -> str:
    """Return stable canonical JSON after full context-bound validation."""

    return _canonical_json_bytes(
        validate_project_narrative_diagnostic(value, context)
    ).decode("utf-8")


__all__ = (
    "PROJECT_NARRATIVE_DIAGNOSTIC_VERSION",
    "PROJECT_DIAGNOSTIC_CONTEXT_REFERENCE_VERSION",
    "DIAGNOSTIC_KINDS",
    "CAUSAL_ASSESSMENTS",
    "TIMELINE_ASSESSMENTS",
    "THREAD_ACTIVITY_CLASSIFICATIONS",
    "ProjectNarrativeDiagnosticValidationError",
    "build_project_narrative_diagnostic",
    "build_causal_continuity_diagnostic",
    "build_timeline_diagnostic",
    "build_thread_activity_diagnostic",
    "validate_project_narrative_diagnostic",
    "serialize_project_narrative_diagnostic",
)
