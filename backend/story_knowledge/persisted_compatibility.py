"""Read-only schema detection and compatibility projection for T003G.

This module deliberately has no write or migration API.  It detects legacy,
new, mixed, malformed, and deleted inputs and returns defensive projections;
owner-visible stored bytes are never rewritten.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from backend.story_knowledge import (
    candidate_record,
    evidence,
    raw_artifacts,
    raw_extraction_storage,
    review_queue_storage,
)
from backend.story_knowledge.analysis_run_manifest import (
    ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION,
    analysis_run_manifest_from_dict,
)
from backend.story_knowledge.evidence_ledger import (
    EVIDENCE_LEDGER_EVENT_VERSION,
    EVIDENCE_RECORD_VERSION,
    validate_ledger_event_v1,
    validate_deletion_tombstone,
    validate_evidence_record_v1,
)
from backend.story_knowledge.promotion_apply_events import EVENT_VERSION as PROMOTION_EVENT_VERSION


COMPATIBILITY_POLICY = "compatible-reads-only-no-physical-migration"
RECORD_KINDS = frozenset(
    {
        "candidate",
        "raw_artifact",
        "grouped_review",
        "promotion_audit",
        "analysis_manifest",
        "evidence_record",
        "ledger_event",
    }
)


def _declared_versions(value: dict[str, Any]) -> tuple[str, ...]:
    versions = []
    for field in ("schema_version", "contract_version", "record_version", "event_version"):
        candidate = value.get(field)
        if isinstance(candidate, (str, int)):
            versions.append(str(candidate))
    return tuple(versions)


def detect_persisted_version(value: Any, *, record_kind: str) -> dict[str, Any]:
    if record_kind not in RECORD_KINDS:
        raise ValueError("unknown persisted record kind")
    if isinstance(value, list):
        if not value:
            return {"state": "legacy", "versions": [], "record_kind": record_kind}
        states = [detect_persisted_version(item, record_kind=record_kind) for item in value]
        versions = sorted({version for state in states for version in state["versions"]})
        if any(state["state"] == "malformed" for state in states):
            state = "malformed"
        elif len({state["state"] for state in states}) > 1 or len(versions) > 1:
            state = "mixed"
        else:
            state = states[0]["state"]
        return {"state": state, "versions": versions, "record_kind": record_kind}
    if not isinstance(value, dict):
        return {"state": "malformed", "versions": [], "record_kind": record_kind}
    versions = list(_declared_versions(value))
    if value.get("deletion_state") == "deleted" or value.get("status") == "deleted":
        return {"state": "deleted", "versions": versions, "record_kind": record_kind}
    if len(set(versions)) > 1 and record_kind not in {"promotion_audit"}:
        return {"state": "mixed", "versions": sorted(set(versions)), "record_kind": record_kind}
    known_new = {
        raw_artifacts.IMMUTABLE_RAW_ARTIFACT_VERSION,
        ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION,
        EVIDENCE_RECORD_VERSION,
        EVIDENCE_LEDGER_EVENT_VERSION,
        PROMOTION_EVENT_VERSION,
    }
    if record_kind == "grouped_review" and "review_version" in value:
        versions.append(str(value["review_version"]))
        state = "new"
    elif any(version in known_new for version in versions):
        state = "new"
    elif versions:
        state = "legacy"
    else:
        state = "legacy"
    return {"state": state, "versions": versions, "record_kind": record_kind}


def _validate_analysis_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("contract_version") == ANALYSIS_RUN_MANIFEST_CONTRACT_VERSION:
        return analysis_run_manifest_from_dict(value).to_dict()
    return raw_extraction_storage.validate_extraction_run_manifest(value)


def _validate_promotion_audit(
    value: dict[str, Any], *, predecessor: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate either the established legacy record or current v2 event."""

    if "event_version" in value or "object_kind" in value:
        from backend.story_knowledge.apply_contract import canonical_json_bytes
        from backend.story_knowledge.promotion_apply_events import _validate_event_semantics

        if value.get("event_version") != PROMOTION_EVENT_VERSION:
            raise ValueError("unsupported promotion audit event variant")
        checked = copy.deepcopy(value)
        try:
            _validate_event_semantics(checked)
        except Exception as exc:
            raise ValueError("malformed promotion audit event") from exc
        expected_previous = (
            None
            if predecessor is None
            else hashlib.sha256(canonical_json_bytes(predecessor)).hexdigest()
        )
        if checked["previous_event_hash"] != expected_previous:
            raise ValueError("promotion audit predecessor hash mismatch")
        if checked["sequence"] != (1 if predecessor is None else predecessor["sequence"] + 1):
            raise ValueError("promotion audit sequence is not contiguous")
        return checked

    from backend.story_knowledge.apply_promotion import validate_promotion_audit_record

    validation = validate_promotion_audit_record(value)
    if validation.get("validation_status") != "valid":
        raise ValueError("malformed legacy promotion audit record")
    return validation["record"]


def _validate_one(value: dict[str, Any], record_kind: str) -> dict[str, Any]:
    if record_kind == "candidate":
        return candidate_record.validate_candidate_record(value)
    if record_kind == "raw_artifact":
        if value.get("deletion_state") == "deleted":
            return validate_deletion_tombstone(value)
        if value.get("schema_version") == raw_artifacts.IMMUTABLE_RAW_ARTIFACT_VERSION:
            return raw_artifacts.validate_raw_artifact_integrity(value)
        return raw_artifacts.validate_raw_artifact_manifest(value)
    if record_kind == "grouped_review":
        return review_queue_storage.validate_review_queue_entry(value)
    if record_kind == "promotion_audit":
        return _validate_promotion_audit(value)
    if record_kind == "analysis_manifest":
        return _validate_analysis_manifest(value)
    if record_kind == "evidence_record":
        if value.get("schema_version") == EVIDENCE_RECORD_VERSION:
            return validate_evidence_record_v1(value)
        return evidence.validate_evidence_record(value)
    if record_kind == "ledger_event":
        return validate_ledger_event_v1(value, predecessor=None)
    raise ValueError("unknown persisted record kind")


def read_compatible_record(value: Any, *, record_kind: str) -> dict[str, Any]:
    """Return a deterministic defensive projection, never a migration."""

    detection = detect_persisted_version(value, record_kind=record_kind)
    if detection["state"] == "malformed":
        raise ValueError("malformed persisted data; no repair or migration performed")
    if isinstance(value, list):
        records = []
        predecessor = None
        promotion_predecessor = None
        for item in value:
            if record_kind == "ledger_event":
                validated = validate_ledger_event_v1(item, predecessor=predecessor)
                predecessor = validated
                records.append(validated)
            elif record_kind == "promotion_audit":
                is_current = isinstance(item, dict) and (
                    "event_version" in item or "object_kind" in item
                )
                validated = _validate_promotion_audit(
                    item,
                    predecessor=promotion_predecessor if is_current else None,
                )
                if is_current:
                    promotion_predecessor = validated
                records.append(validated)
            else:
                records.append(_validate_one(item, record_kind))
        return {
            "compatibility_policy": COMPATIBILITY_POLICY,
            "version_state": detection["state"],
            "versions": detection["versions"],
            "records": records,
            "physical_migration_performed": False,
            "stored_input_mutated": False,
        }
    record = _validate_one(value, record_kind)
    return {
        "compatibility_policy": COMPATIBILITY_POLICY,
        "version_state": detection["state"],
        "versions": detection["versions"],
        "record": record,
        "physical_migration_performed": False,
        "stored_input_mutated": False,
    }


__all__ = [
    "COMPATIBILITY_POLICY",
    "RECORD_KINDS",
    "detect_persisted_version",
    "read_compatible_record",
]
