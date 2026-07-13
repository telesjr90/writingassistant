"""Live Story Check grounding integration over the T002A/T002B contracts.

The integration is additive: legacy Story Check fields remain available while a
deterministic ``grounding`` envelope carries exact source identity and validated
diagnostics.  It performs no I/O, persistence, candidate creation, promotion,
Memory/Canon mutation, or prose generation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

try:
    from .story_check_grounding_contract import (
        STORY_CHECK_OFFSET_BASIS,
        StoryCheckDiagnosticClassification,
        StoryCheckDiagnosticResult,
        StoryCheckEvidenceReference,
        StoryCheckSourceSnapshot,
    )
    from .story_check_grounding_validator import (
        build_validated_story_check_diagnostic,
    )
except ImportError:  # pragma: no cover - supports direct execution from backend/
    from story_check_grounding_contract import (
        STORY_CHECK_OFFSET_BASIS,
        StoryCheckDiagnosticClassification,
        StoryCheckDiagnosticResult,
        StoryCheckEvidenceReference,
        StoryCheckSourceSnapshot,
    )
    from story_check_grounding_validator import build_validated_story_check_diagnostic


class StoryCheckGroundingIntegrationError(ValueError):
    """Raised when a Story Check response envelope names another source."""


_THROUGHLINE_KEYS = (
    "overall_story",
    "main_character",
    "influence_character",
    "relationship_story",
)
_CLASSIFICATIONS = frozenset(item.value for item in StoryCheckDiagnosticClassification)


def _envelope_source_identity(result: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if "source_id" in result or "source_sha256" in result:
        return result
    for value in (
        result.get("source_identity"),
        result.get("grounding_source_identity"),
        result.get("grounding", {}).get("source_identity")
        if isinstance(result.get("grounding"), Mapping)
        else None,
    ):
        if isinstance(value, Mapping):
            return value
    return None


def _validate_envelope_source(
    result: Mapping[str, Any], snapshot: StoryCheckSourceSnapshot
) -> None:
    identity = _envelope_source_identity(result)
    if identity is None:
        return

    source_id = identity.get("source_id")
    source_hash = identity.get("source_sha256")
    if source_id is not None and source_id != snapshot.source_id:
        raise StoryCheckGroundingIntegrationError(
            "story_check_source_id_mismatch: response does not match selected source"
        )
    if source_hash is not None and source_hash != snapshot.source_sha256:
        raise StoryCheckGroundingIntegrationError(
            "story_check_source_hash_mismatch: response does not match submitted source"
        )


def _classification(value: Any, *, fallback: str) -> str:
    return value if isinstance(value, str) and value in _CLASSIFICATIONS else fallback


def _untrusted_evidence(value: Any) -> object:
    """Retain untrusted fields for T002B to validate without repairing them."""

    required = {
        "source_id",
        "source_sha256",
        "start_byte",
        "end_byte",
        "excerpt",
    }
    if not isinstance(value, Mapping) or not required <= set(value):
        return value
    reference = object.__new__(StoryCheckEvidenceReference)
    fields = {
        "source_id": value.get("source_id"),
        "source_sha256": value.get("source_sha256"),
        "start_byte": value.get("start_byte"),
        "end_byte": value.get("end_byte"),
        "excerpt": value.get("excerpt"),
        "offset_basis": value.get("offset_basis", STORY_CHECK_OFFSET_BASIS),
    }
    for name, field_value in fields.items():
        object.__setattr__(reference, name, field_value)
    return reference


def _explicit_diagnostics(result: Mapping[str, Any]) -> list[dict[str, Any]] | None:
    raw_items = result.get("grounding_diagnostics")
    if not isinstance(raw_items, list):
        return None

    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, Mapping) or not isinstance(raw_item.get("message"), str):
            continue
        raw_evidence = raw_item.get("evidence")
        evidence: Sequence[Any]
        if "evidence" not in raw_item:
            evidence = ()
        elif isinstance(raw_evidence, list):
            evidence = tuple(_untrusted_evidence(item) for item in raw_evidence)
        else:
            evidence = (_untrusted_evidence(raw_evidence),)
        diagnostic_id = raw_item.get("diagnostic_id")
        if not isinstance(diagnostic_id, str):
            diagnostic_id = f"grounded-{index:03d}"
        items.append(
            {
                "diagnostic_id": diagnostic_id,
                "classification": _classification(
                    raw_item.get("classification"), fallback="observation"
                ),
                "message": raw_item["message"],
                "evidence": evidence,
                "grounding_applicable": raw_item.get("grounding_applicable"),
                "producer_version": raw_item.get("producer_version"),
            }
        )
    return items


def _append_strings(
    target: list[dict[str, Any]],
    values: Any,
    *,
    id_prefix: str,
    classification: str,
) -> None:
    if not isinstance(values, list):
        return
    for value in values:
        if not isinstance(value, str):
            continue
        target.append(
            {
                "diagnostic_id": f"{id_prefix}-{len(target) + 1:03d}",
                "classification": classification,
                "message": value,
                "evidence": (),
            }
        )


def _legacy_diagnostics(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    warnings = result.get("warnings")
    if isinstance(warnings, list):
        for warning in warnings:
            if not isinstance(warning, str):
                continue
            classification = (
                "factual_warning"
                if warning.startswith("[Factual]")
                else "structural_diagnostic"
            )
            items.append(
                {
                    "diagnostic_id": f"warning-{len(items) + 1:03d}",
                    "classification": classification,
                    "message": warning,
                    "evidence": (),
                }
            )

    _append_strings(
        items,
        result.get("suggestions"),
        id_prefix="question",
        classification="question",
    )

    throughlines = result.get("throughline_alignment")
    if isinstance(throughlines, Mapping):
        for key in _THROUGHLINE_KEYS:
            value = throughlines.get(key)
            if not isinstance(value, Mapping):
                continue
            _append_strings(
                items,
                value.get("evidence"),
                id_prefix=f"{key}-observation",
                classification="observation",
            )
            _append_strings(
                items,
                value.get("concerns"),
                id_prefix=f"{key}-concern",
                classification="structural_diagnostic",
            )

    for field_name in ("theme_drift", "character_consistency"):
        value = result.get(field_name)
        reason = value.get("reason") if isinstance(value, Mapping) else None
        if isinstance(reason, str):
            items.append(
                {
                    "diagnostic_id": f"{field_name}-{len(items) + 1:03d}",
                    "classification": "structural_diagnostic",
                    "message": reason,
                    "evidence": (),
                }
            )

    _append_strings(
        items,
        result.get("insufficient_evidence"),
        id_prefix="insufficient-evidence",
        classification="observation",
    )
    return items


def ground_story_check_result(
    result: Mapping[str, Any], snapshot: StoryCheckSourceSnapshot
) -> dict[str, Any]:
    """Attach a deterministic T002A result to one legacy Story Check result."""

    if not isinstance(result, Mapping):
        raise StoryCheckGroundingIntegrationError(
            "story_check_result_malformed: expected a JSON object"
        )
    if not isinstance(snapshot, StoryCheckSourceSnapshot):
        raise StoryCheckGroundingIntegrationError(
            "story_check_source_snapshot_missing: exact source is required"
        )

    _validate_envelope_source(result, snapshot)
    raw_items = _explicit_diagnostics(result)
    items = raw_items if raw_items else _legacy_diagnostics(result)
    diagnostics = []
    for item in items:
        grounding_applicable = item.get("grounding_applicable")
        if type(grounding_applicable) is not bool:
            grounding_applicable = None
        producer_version = item.get("producer_version")
        if not isinstance(producer_version, str):
            producer_version = None
        diagnostics.append(
            build_validated_story_check_diagnostic(
                snapshot,
                item["diagnostic_id"],
                item["classification"],
                item["message"],
                item["evidence"],
                grounding_applicable=grounding_applicable,
                producer_version=producer_version,
            )
        )

    grounded = StoryCheckDiagnosticResult(snapshot.identity, diagnostics).to_dict()
    grounded["status"] = "completed"
    response = dict(result)
    response["grounding"] = grounded
    return response


def build_story_check_grounding_failure(
    snapshot: StoryCheckSourceSnapshot, reason: str
) -> dict[str, Any]:
    """Return a bounded fail-closed envelope for an envelope-level mismatch."""

    grounded = StoryCheckDiagnosticResult(snapshot.identity, ()).to_dict()
    grounded.update(
        {
            "status": "failed_closed",
            "reason_codes": [reason.split(":", 1)[0]],
        }
    )
    return {"error": reason, "grounding": grounded}


__all__ = [
    "StoryCheckGroundingIntegrationError",
    "build_story_check_grounding_failure",
    "ground_story_check_result",
]
