"""Deterministic cross-adapter semantic guardrails for normalized findings.

The evaluator is deliberately analysis-only.  It snapshots a normalized
finding plus its evidence and emits a separate annotation.  It never rewrites
the finding, selects truth/canon, changes an owner decision, or calls a model.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from typing import Any, Mapping, Sequence


GUARDRAIL_INPUT_SCHEMA_VERSION = "omi-semantic-guardrail-input.v1"
GUARDRAIL_ANNOTATION_SCHEMA_VERSION = "omi-semantic-guardrail-annotation.v1"
GUARDRAIL_CONTRACT_VERSION = "omi-semantic-guardrails.v1"

SEMANTIC_CLASSIFICATIONS = frozenset(
    {
        "supported",
        "unsupported",
        "ambiguous",
        "subject_matter_only",
        "author_intent_dependent",
        "insufficient_evidence",
    }
)

NORMALIZED_EVIDENCE_PRODUCER_ADAPTERS = frozenset({"booknlp", "spacy"})

_FUSION_MUTABLE_FIELDS = frozenset(
    {
        "candidate_fingerprint",
        "evidence_fingerprint",
        "normalized_finding_id",
        "duplicate_of",
        "related_finding_ids",
        "conflict_group_id",
        "uncertainty_label",
    }
)
_OVERCLAIM_ASSERTION_KINDS = frozenset(
    {"assertion", "candidate_observation", "fact", "hypothesis", "observation"}
)
_PERSPECTIVE_RE = re.compile(
    r"\b(?:perspective|main character throughline|influence character throughline|"
    r"overall story throughline|relationship story throughline)\b",
    re.IGNORECASE,
)
_THROUGHLINE_RE = re.compile(r"\bthroughline\b", re.IGNORECASE)
_STORYPOINT_RE = re.compile(
    r"\b(?:story[ -]?point|story goal|story requirements?|story consequences?|"
    r"story forewarnings?|story dividends?|story costs?|story prerequisites?|"
    r"story preconditions?)\b",
    re.IGNORECASE,
)
_AUTHOR_INTENT_RE = re.compile(
    r"\b(?:author(?:ial)? intent|author intended|intended meaning|owner intent)\b",
    re.IGNORECASE,
)
_CONFLICT_CLAIM_RE = re.compile(
    r"\b(?:conflict|source[ -]of[ -]conflict|opposing pressure|resistance)\b",
    re.IGNORECASE,
)
_CONFLICT_MECHANISM_RE = re.compile(
    r"\b(?:because|causes?|creates?|drives?|blocks?|prevents?|opposes?|"
    r"resists?|resistance|pressure|deadline|threat|obstacle|consequence)\b",
    re.IGNORECASE,
)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _immutable_finding_payload(finding: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in finding.items()
        if key not in _FUSION_MUTABLE_FIELDS
    }


def immutable_finding_sha256(finding: Mapping[str, Any]) -> str:
    """Hash the finding fields fusion is not allowed to reinterpret."""

    if not isinstance(finding, Mapping):
        raise ValueError("semantic guardrail finding must be an object")
    return _sha256(_immutable_finding_payload(finding))


def _text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        result: list[str] = []
        for nested in value.values():
            result.extend(_text_values(nested))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        result = []
        for nested in value:
            result.extend(_text_values(nested))
        return result
    return []


def _normalized_tokens(value: Any) -> set[str]:
    return {
        token.strip().lower().replace("-", "_").replace(" ", "_")
        for token in _text_values(value)
        if token.strip()
    }


def _first_non_empty(mapping: Mapping[str, Any], keys: Sequence[str]) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _source_lineage(
    finding: Mapping[str, Any], supplied: Mapping[str, Any] | None
) -> dict[str, Any]:
    provenance = finding.get("provenance")
    provenance = provenance if isinstance(provenance, Mapping) else {}
    supplied = supplied if isinstance(supplied, Mapping) else {}
    identity = supplied.get("source_identity")
    identity = identity if isinstance(identity, Mapping) else {}
    evidence = finding.get("evidence")
    evidence = evidence if isinstance(evidence, list) else []
    evidence_first = evidence[0] if evidence and isinstance(evidence[0], Mapping) else {}
    return {
        "run_id": _first_non_empty(supplied, ("run_id",))
        or _first_non_empty(provenance, ("run_id", "analysis_run_id")),
        "source_id": _first_non_empty(identity, ("source_id", "snapshot_id"))
        or _first_non_empty(supplied, ("source_id", "source_snapshot_id"))
        or _first_non_empty(evidence_first, ("source_id", "snapshot_id"))
        or _first_non_empty(provenance, ("source_id", "source_snapshot_id")),
        "source_hash": _first_non_empty(
            identity, ("content_hash", "source_sha256", "sha256")
        )
        or _first_non_empty(
            supplied, ("source_content_hash", "source_sha256", "source_hash")
        )
        or _first_non_empty(
            evidence_first, ("source_sha256", "content_hash", "source_hash")
        )
        or _first_non_empty(
            provenance, ("source_content_hash", "source_sha256", "source_hash")
        ),
    }


def _approved_context_state(context: Mapping[str, Any] | None) -> bool:
    if not isinstance(context, Mapping):
        return False
    return context.get("approved") is True and (
        context.get("owner_controlled") is True
        or context.get("owner_authored") is True
        or context.get("approved_context") is True
    )


def build_guardrail_input(
    finding: Mapping[str, Any],
    *,
    normalized_evidence: Sequence[Mapping[str, Any]] | None = None,
    source_lineage: Mapping[str, Any] | None = None,
    approved_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an isolated input snapshot for one exact normalized finding."""

    if not isinstance(finding, Mapping):
        raise ValueError("semantic guardrail finding must be an object")
    evidence = list(normalized_evidence) if normalized_evidence is not None else []
    if not all(isinstance(item, Mapping) for item in evidence):
        raise ValueError("semantic guardrail normalized_evidence must contain objects")
    return {
        "schema_version": GUARDRAIL_INPUT_SCHEMA_VERSION,
        "finding": copy.deepcopy(dict(finding)),
        "normalized_evidence": copy.deepcopy([dict(item) for item in evidence]),
        "source_lineage": _source_lineage(finding, source_lineage),
        "approved_context": copy.deepcopy(dict(approved_context or {})),
    }


def _evidence_references(finding: Mapping[str, Any]) -> list[str]:
    references: set[str] = set()
    for field in ("source_refs", "evidence_refs", "source_locator_refs"):
        value = finding.get(field)
        if isinstance(value, list):
            references.update(item for item in value if isinstance(item, str) and item)
    locator = finding.get("source_locator")
    if isinstance(locator, str) and locator:
        references.add(locator)
    evidence = finding.get("evidence")
    if isinstance(evidence, list):
        for item in evidence:
            if not isinstance(item, Mapping):
                continue
            for key in ("evidence_id", "source_locator", "locator", "artifact_file_id"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    references.add(value)
    return sorted(references)


def _original_output_references(finding: Mapping[str, Any]) -> list[str]:
    references: set[str] = set()
    provenance = finding.get("provenance")
    containers = [finding, provenance if isinstance(provenance, Mapping) else {}]
    for container in containers:
        for key in (
            "original_output_ref",
            "original_output_reference",
            "original_output_reference_id",
            "original_output_artifact_id",
        ):
            value = container.get(key)
            if isinstance(value, str) and value:
                references.add(value)
            elif isinstance(value, list):
                references.update(
                    item for item in value if isinstance(item, str) and item
                )
    return sorted(references)


def _signal_values(finding: Mapping[str, Any], key: str) -> set[str]:
    values: list[Any] = [finding.get(key)]
    support_metadata = finding.get("support_metadata")
    if isinstance(support_metadata, Mapping):
        values.append(support_metadata.get(key))
        validator = support_metadata.get("story_check_validator_result")
        if isinstance(validator, Mapping):
            values.append(validator.get(key))
    evidence = finding.get("evidence")
    if isinstance(evidence, list):
        values.extend(item.get(key) for item in evidence if isinstance(item, Mapping))
    return _normalized_tokens(values)


def _lineage_mismatch(
    finding: Mapping[str, Any], lineage: Mapping[str, Any]
) -> bool:
    expected_hash = lineage.get("source_hash")
    expected_id = lineage.get("source_id")
    evidence = finding.get("evidence")
    if not isinstance(evidence, list):
        return False
    for item in evidence:
        if not isinstance(item, Mapping):
            continue
        actual_hash = _first_non_empty(
            item, ("source_sha256", "content_hash", "source_hash")
        )
        actual_id = _first_non_empty(item, ("source_id", "snapshot_id"))
        if expected_hash and actual_hash and actual_hash != expected_hash:
            return True
        if expected_id and actual_id and actual_id != expected_id:
            return True
    return False


def _normalized_evidence_references(
    evidence_inputs: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence_inputs:
        adapter = str(item.get("source_adapter") or "")
        finding_id = str(item.get("normalized_finding_id") or "")
        fingerprint = immutable_finding_sha256(item)
        provenance = item.get("provenance")
        provenance = provenance if isinstance(provenance, Mapping) else {}
        operation_id = str(provenance.get("operation_id") or "")
        key = (adapter, finding_id, fingerprint)
        if key in seen:
            continue
        seen.add(key)
        references.append(
            {
                "source_adapter": adapter,
                "producer_operation_id": operation_id,
                "normalized_finding_id": finding_id,
                "immutable_finding_sha256": fingerprint,
            }
        )
    return sorted(
        references,
        key=lambda item: (
            item["source_adapter"],
            item["normalized_finding_id"],
            item["immutable_finding_sha256"],
        ),
    )


def select_upstream_normalized_evidence(
    findings: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Select evidence-producer outputs, never interpretive findings."""

    if not isinstance(findings, Sequence) or isinstance(findings, (str, bytes)):
        raise ValueError("normalized evidence candidates must be a sequence")
    selected = []
    for finding in findings:
        if not isinstance(finding, Mapping):
            raise ValueError("normalized evidence candidates must contain objects")
        if finding.get("source_adapter") in NORMALIZED_EVIDENCE_PRODUCER_ADAPTERS:
            selected.append(copy.deepcopy(dict(finding)))
    return selected


def _eligible_normalized_evidence(
    finding: Mapping[str, Any],
    evidence_inputs: Sequence[Mapping[str, Any]],
    lineage: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], bool]:
    """Return distinct, same-source evidence-producer outputs and mismatch state."""

    finding_id = str(finding.get("normalized_finding_id") or "")
    finding_hash = immutable_finding_sha256(finding)
    eligible: list[Mapping[str, Any]] = []
    producer_source_mismatch = False
    for item in evidence_inputs:
        if item.get("source_adapter") not in NORMALIZED_EVIDENCE_PRODUCER_ADAPTERS:
            continue
        item_id = str(item.get("normalized_finding_id") or "")
        item_hash = immutable_finding_sha256(item)
        if (item_id and item_id == finding_id) or item_hash == finding_hash:
            continue
        if _lineage_mismatch(item, lineage):
            producer_source_mismatch = True
            continue
        evidence = item.get("evidence")
        if isinstance(evidence, list) and evidence:
            eligible.append(item)
    return eligible, producer_source_mismatch


def _explicit_bool(finding: Mapping[str, Any], keys: Sequence[str]) -> bool:
    containers: list[Mapping[str, Any]] = [finding]
    metadata = finding.get("support_metadata")
    if isinstance(metadata, Mapping):
        containers.append(metadata)
    return any(container.get(key) is True for container in containers for key in keys)


def evaluate_guardrail(guardrail_input: Mapping[str, Any]) -> dict[str, Any]:
    """Classify one finding without changing the input or its nested values."""

    if not isinstance(guardrail_input, Mapping):
        raise ValueError("semantic guardrail input must be an object")
    if guardrail_input.get("schema_version") != GUARDRAIL_INPUT_SCHEMA_VERSION:
        raise ValueError("unsupported semantic guardrail input schema")
    before = _sha256(guardrail_input)
    finding = guardrail_input.get("finding")
    if not isinstance(finding, Mapping):
        raise ValueError("semantic guardrail input finding must be an object")
    evidence_inputs = guardrail_input.get("normalized_evidence")
    if not isinstance(evidence_inputs, list):
        raise ValueError("semantic guardrail normalized_evidence must be a list")
    lineage = guardrail_input.get("source_lineage")
    lineage = lineage if isinstance(lineage, Mapping) else {}
    approved_context = guardrail_input.get("approved_context")
    approved_context = approved_context if isinstance(approved_context, Mapping) else {}

    provenance = finding.get("provenance")
    provenance = provenance if isinstance(provenance, Mapping) else {}
    source_adapter = str(finding.get("source_adapter") or "")
    operation_id = provenance.get("operation_id")
    normalized_finding_id = str(finding.get("normalized_finding_id") or "")
    immutable_hash = immutable_finding_sha256(finding)
    exact_evidence = finding.get("evidence")
    has_evidence = isinstance(exact_evidence, list) and bool(exact_evidence)
    requires_normalized_evidence = (
        source_adapter not in NORMALIZED_EVIDENCE_PRODUCER_ADAPTERS
    )
    if requires_normalized_evidence:
        eligible_normalized_evidence, normalized_evidence_source_mismatch = (
            _eligible_normalized_evidence(finding, evidence_inputs, lineage)
        )
    else:
        eligible_normalized_evidence = []
        normalized_evidence_source_mismatch = False
    has_normalized_evidence = bool(eligible_normalized_evidence)

    verification_states = _signal_values(finding, "verification_state")
    verification_states.update(_signal_values(finding, "story_check_verification_state"))
    validator_outcomes = _signal_values(finding, "outcome")
    uncertainty_states = _signal_values(finding, "uncertainty_label")
    support_states = _normalized_tokens(
        [finding.get("support_label"), finding.get("support"), finding.get("confidence")]
    )
    statement_kind = str(finding.get("statement_kind") or "").strip().lower()
    semantic_text = " ".join(
        str(finding.get(field) or "")
        for field in (
            "candidate_type",
            "label",
            "extracted_claim",
            "statement_kind",
            "raw_finding_id",
        )
    )
    is_question = (
        str(finding.get("candidate_type") or "") == "diagnostic_question"
        or statement_kind == "question"
        or str(finding.get("extracted_claim") or "").rstrip().endswith("?")
    )
    author_intent_required = bool(_AUTHOR_INTENT_RE.search(semantic_text)) or (
        "author_intent_dependent" in uncertainty_states
    ) or _explicit_bool(
        finding,
        ("author_intent_required", "author_intent_dependent"),
    )
    approved_context_present = _approved_context_state(approved_context)
    perspective_claim = bool(_PERSPECTIVE_RE.search(semantic_text))
    throughline_claim = (
        str(finding.get("candidate_type") or "") == "throughline_context"
        or bool(_THROUGHLINE_RE.search(semantic_text))
    )
    storypoint_claim = bool(_STORYPOINT_RE.search(semantic_text))
    conflict_claim = (
        str(finding.get("candidate_type") or "") == "conflict_diagnostic"
        or bool(_CONFLICT_CLAIM_RE.search(semantic_text))
    )
    evidence_text = " ".join(
        " ".join(_text_values(item))
        for item in (exact_evidence if isinstance(exact_evidence, list) else [])
    )
    explicit_subject_only = statement_kind in {"subject", "subject_matter", "topic"} or _explicit_bool(
        finding, ("subject_matter_only", "topic_only")
    )
    conflict_mechanism_present = _explicit_bool(
        finding, ("conflict_mechanism_grounded", "source_of_conflict_grounded")
    ) or bool(_CONFLICT_MECHANISM_RE.search(evidence_text))
    perspective_grounded = _explicit_bool(
        finding, ("perspective_distinguished", "perspective_grounded")
    )
    throughline_grounded = _explicit_bool(
        finding, ("throughline_grounded", "structurally_grounded")
    )
    storypoint_grounded = _explicit_bool(
        finding, ("storypoint_grounded", "story_point_grounded", "structurally_grounded")
    )

    reasons: list[str]
    if source_adapter != str(provenance.get("adapter") or "") or source_adapter != str(
        provenance.get("tool_source") or ""
    ):
        classification = "insufficient_evidence"
        reasons = ["adapter_provenance_mismatch"]
    elif _lineage_mismatch(finding, lineage):
        classification = "insufficient_evidence"
        reasons = ["source_lineage_mismatch"]
    elif "quarantined" in verification_states or "unsupported" in validator_outcomes:
        classification = "unsupported"
        reasons = ["quarantined_or_rejected_grounding"]
    elif verification_states & {"unverified", "unknown", "not_verified"}:
        classification = "insufficient_evidence"
        reasons = ["unverified_grounding"]
    elif requires_normalized_evidence and normalized_evidence_source_mismatch:
        classification = "insufficient_evidence"
        reasons = ["normalized_evidence_source_lineage_mismatch"]
    elif requires_normalized_evidence and not has_normalized_evidence:
        classification = "insufficient_evidence"
        reasons = ["eligible_normalized_evidence_missing"]
    elif not has_evidence:
        classification = "insufficient_evidence"
        reasons = ["finding_evidence_missing"]
    elif (
        "insufficient_evidence" in uncertainty_states
        or "insufficient_evidence_support" in uncertainty_states
        or "insufficient_evidence" in semantic_text.lower().replace(" ", "_")
    ):
        classification = "insufficient_evidence"
        reasons = ["explicit_insufficient_evidence"]
    elif author_intent_required and not approved_context_present:
        classification = "author_intent_dependent"
        reasons = ["eligible_author_intent_or_approved_context_missing"]
    elif conflict_claim and (explicit_subject_only or not conflict_mechanism_present):
        classification = "subject_matter_only"
        reasons = ["subject_evidence_does_not_establish_conflict"]
    elif perspective_claim and not perspective_grounded and is_question:
        classification = "ambiguous"
        reasons = ["perspective_not_distinguished_by_evidence"]
    elif storypoint_claim and not storypoint_grounded:
        classification = "ambiguous" if is_question else "unsupported"
        reasons = ["storypoint_label_not_structurally_grounded"]
    elif throughline_claim and not throughline_grounded:
        classification = "ambiguous" if is_question else "unsupported"
        reasons = ["throughline_label_not_structurally_grounded"]
    elif perspective_claim and not perspective_grounded:
        classification = "ambiguous"
        reasons = ["perspective_not_distinguished_by_evidence"]
    elif is_question:
        classification = "ambiguous"
        reasons = ["diagnostic_question_does_not_select_an_interpretation"]
    elif uncertainty_states & {
        "ambiguous_source_support",
        "requires_owner_review",
        "requires_owner_interpretation",
        "conflict_support",
        "possible_context_only_support",
        "ambiguous",
    }:
        classification = "ambiguous"
        reasons = ["explicit_uncertainty_preserved"]
    else:
        classification = "supported"
        reasons = ["direct_normalized_evidence_support"]
        if "verified" in verification_states or "supported" in validator_outcomes:
            reasons.append("verified_grounding_preserved")
        if author_intent_required and approved_context_present:
            reasons.append("eligible_approved_context_present")

    finding_id = normalized_finding_id or f"guardrail-finding-{immutable_hash[:16]}"
    normalized_evidence_references = _normalized_evidence_references(
        eligible_normalized_evidence
    )
    annotation_material = {
        "finding_id": finding_id,
        "finding_sha256": immutable_hash,
        "source_lineage": dict(lineage),
        "classification": classification,
        "reason_codes": sorted(set(reasons)),
        "normalized_evidence_references": normalized_evidence_references,
        "approved_context_sha256": _sha256(approved_context) if approved_context else None,
    }
    annotation = {
        "schema_version": GUARDRAIL_ANNOTATION_SCHEMA_VERSION,
        "contract_version": GUARDRAIL_CONTRACT_VERSION,
        "annotation_id": f"omi-guardrail-{_sha256(annotation_material)[:24]}",
        "normalized_finding_id": finding_id,
        "immutable_finding_sha256": immutable_hash,
        "source_lineage": copy.deepcopy(dict(lineage)),
        "source_adapter": source_adapter,
        "operation_id": operation_id if isinstance(operation_id, str) else None,
        "evidence_references": _evidence_references(finding),
        "normalized_evidence_references": normalized_evidence_references,
        "normalized_evidence_dependency": {
            "required": requires_normalized_evidence,
            "satisfied": (not requires_normalized_evidence)
            or has_normalized_evidence,
            "supplied_count": len(evidence_inputs),
            "eligible_count": len(eligible_normalized_evidence),
            "eligible_producer_adapters": sorted(
                {
                    str(item.get("source_adapter"))
                    for item in eligible_normalized_evidence
                }
            ),
        },
        "original_output_references": _original_output_references(finding),
        "verification_state": sorted(verification_states),
        "support_state": sorted(support_states | validator_outcomes),
        "uncertainty_state": sorted(uncertainty_states),
        "classification": classification,
        "reason_codes": sorted(set(reasons)),
        "author_intent_or_approved_context": {
            "required": author_intent_required,
            "present": approved_context_present,
        },
        "owner_decision": "not_selected",
        "canon_status": "not_selected",
    }
    if _sha256(guardrail_input) != before:
        raise RuntimeError("semantic guardrail mutated its input")
    return annotation


def validate_guardrail_annotation(
    annotation: Mapping[str, Any], *, finding: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    if not isinstance(annotation, Mapping):
        raise ValueError("semantic guardrail annotation must be an object")
    if annotation.get("schema_version") != GUARDRAIL_ANNOTATION_SCHEMA_VERSION:
        raise ValueError("unsupported semantic guardrail annotation schema")
    if annotation.get("contract_version") != GUARDRAIL_CONTRACT_VERSION:
        raise ValueError("unsupported semantic guardrail contract version")
    if annotation.get("classification") not in SEMANTIC_CLASSIFICATIONS:
        raise ValueError("invalid semantic guardrail classification")
    reason_codes = annotation.get("reason_codes")
    if not isinstance(reason_codes, list) or not reason_codes or not all(
        isinstance(item, str) and item for item in reason_codes
    ):
        raise ValueError("semantic guardrail annotation requires reason codes")
    if annotation.get("owner_decision") != "not_selected":
        raise ValueError("semantic guardrail annotation cannot select an owner decision")
    if annotation.get("canon_status") != "not_selected":
        raise ValueError("semantic guardrail annotation cannot select canon")
    if finding is not None:
        expected_id = finding.get("normalized_finding_id")
        if expected_id and annotation.get("normalized_finding_id") != expected_id:
            raise ValueError("semantic guardrail finding identity mismatch")
        if annotation.get("immutable_finding_sha256") != immutable_finding_sha256(finding):
            raise ValueError("semantic guardrail finding fingerprint mismatch")
    return copy.deepcopy(dict(annotation))


def assess_findings(
    findings: Sequence[Mapping[str, Any]],
    *,
    normalized_evidence: Sequence[Mapping[str, Any]] | None = None,
    source_lineage: Mapping[str, Any] | None = None,
    approved_context: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Assess each finding in order and return a parallel annotation list."""

    if not isinstance(findings, Sequence) or isinstance(findings, (str, bytes)):
        raise ValueError("semantic guardrail findings must be a sequence")
    evidence = list(normalized_evidence) if normalized_evidence is not None else []
    annotations = []
    for finding in findings:
        guardrail_input = build_guardrail_input(
            finding,
            normalized_evidence=evidence,
            source_lineage=source_lineage,
            approved_context=approved_context,
        )
        annotations.append(evaluate_guardrail(guardrail_input))
    return annotations


def assess_retained_story_check_diagnostics(
    original_output: Mapping[str, Any],
    *,
    normalized_evidence: Sequence[Mapping[str, Any]] | None = None,
    source_lineage: Mapping[str, Any] | None = None,
    original_output_reference: str | None = None,
    excluded_diagnostic_ids: Sequence[str] = (),
) -> list[dict[str, Any]]:
    """Assess retained Story Check diagnostics without creating candidates."""

    if not isinstance(original_output, Mapping):
        raise ValueError("Story Check original output must be an object")
    grounding = original_output.get("grounding")
    grounding = grounding if isinstance(grounding, Mapping) else {}
    diagnostics = grounding.get("diagnostics")
    if not isinstance(diagnostics, list):
        return []
    excluded = set(excluded_diagnostic_ids)
    evidence_inputs = list(normalized_evidence or [])
    annotations: list[dict[str, Any]] = []
    for diagnostic in diagnostics:
        if not isinstance(diagnostic, Mapping):
            raise ValueError("Story Check retained diagnostic must be an object")
        diagnostic_id = str(diagnostic.get("diagnostic_id") or "")
        if not diagnostic_id:
            raise ValueError("Story Check retained diagnostic requires diagnostic_id")
        if diagnostic_id in excluded:
            continue
        classification = str(diagnostic.get("classification") or "")
        candidate_type = (
            "diagnostic_question"
            if classification == "question"
            else "story_fact"
            if classification == "factual_warning"
            else "structural_diagnostic"
        )
        raw_evidence = diagnostic.get("evidence")
        raw_evidence = raw_evidence if isinstance(raw_evidence, list) else []
        evidence = []
        for item in raw_evidence:
            if not isinstance(item, Mapping):
                continue
            converted = copy.deepcopy(dict(item))
            if "excerpt" in converted and "source_excerpt" not in converted:
                converted["source_excerpt"] = converted["excerpt"]
            if not converted.get("source_locator"):
                start = converted.get("start_byte")
                end = converted.get("end_byte")
                if isinstance(start, int) and isinstance(end, int):
                    converted["source_locator"] = f"source-bytes:{start}-{end}"
            evidence.append(converted)
        message = str(diagnostic.get("message") or "")
        validator = diagnostic.get("validator_result")
        validator = validator if isinstance(validator, Mapping) else {}
        subject = {
            "candidate_type": candidate_type,
            "label": f"Retained Story Check diagnostic {diagnostic_id}",
            "extracted_claim": message or diagnostic_id,
            "evidence": evidence,
            "source_locator": f"retained-story-check:{diagnostic_id}",
            "provenance": {
                "tool_source": "story_check",
                "adapter": "story_check",
                "support": "retained diagnostic support only",
                "operation_id": "analyze-story-check",
                **(
                    {"original_output_reference_id": original_output_reference}
                    if original_output_reference
                    else {}
                ),
            },
            "source_adapter": "story_check",
            "support_label": "retained diagnostic support only",
            "owner_decision": {"decision": "pending", "approved": False},
            "review_status": "candidate_review_pending",
            "raw_finding_id": f"retained-story-check::{diagnostic_id}",
            "normalized_finding_id": f"retained-story-check::{diagnostic_id}",
            "support_metadata": {
                "story_check_verification_state": diagnostic.get(
                    "verification_state"
                ),
                "story_check_validator_result": copy.deepcopy(dict(validator)),
            },
        }
        guardrail_input = build_guardrail_input(
            subject,
            normalized_evidence=evidence_inputs,
            source_lineage=source_lineage,
        )
        annotation = evaluate_guardrail(guardrail_input)
        diagnostic_hash = _sha256(diagnostic)
        annotation["finding_kind"] = "retained_story_check_diagnostic"
        annotation["diagnostic_id"] = diagnostic_id
        annotation["immutable_diagnostic_sha256"] = diagnostic_hash
        annotation["candidate_transformation_performed"] = False
        annotation["fusion_eligible"] = False
        annotation["annotation_id"] = (
            "omi-guardrail-retained-"
            + _sha256(
                {
                    "diagnostic_id": diagnostic_id,
                    "diagnostic_sha256": diagnostic_hash,
                    "classification": annotation["classification"],
                    "reason_codes": annotation["reason_codes"],
                    "source_lineage": annotation["source_lineage"],
                }
            )[:24]
        )
        annotations.append(annotation)
    return annotations


def validate_guardrail_annotations(
    findings: Sequence[Mapping[str, Any]], annotations: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    if len(findings) != len(annotations):
        raise ValueError("semantic guardrail annotations must parallel findings")
    validated = [
        validate_guardrail_annotation(annotation, finding=finding)
        for finding, annotation in zip(findings, annotations)
    ]
    annotation_ids = [item["annotation_id"] for item in validated]
    if len(annotation_ids) != len(set(annotation_ids)):
        raise ValueError("semantic guardrail annotation IDs must be unique")
    return validated


def guardrail_summary(annotations: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(item.get("classification")) for item in annotations)
    return {
        "annotation_count": len(annotations),
        "classification_counts": {
            classification: counts.get(classification, 0)
            for classification in sorted(SEMANTIC_CLASSIFICATIONS)
        },
        "supported_count": counts.get("supported", 0),
        "non_supported_count": len(annotations) - counts.get("supported", 0),
        "truth_selections": 0,
        "owner_approvals": 0,
    }
