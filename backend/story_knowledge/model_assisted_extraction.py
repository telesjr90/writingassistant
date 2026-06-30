"""Pure guards for future model-assisted extraction support.

PHASE8-IMPL-020-T004 intentionally stops before any model runtime. The helpers
below validate request/output boundaries and shape in-memory support data only.
"""

from __future__ import annotations

import copy
import re
from typing import Any


KNOWN_STATES = (
    "disabled",
    "unavailable",
    "model_unavailable",
    "model_call_blocked",
    "configuration_invalid",
    "request_invalid",
    "unsafe_path",
    "missing_source_refs",
    "missing_evidence_refs",
    "missing_provenance_refs",
    "missing_source_locator_refs",
    "source_locator_invalid",
    "unsupported_output_type",
    "malformed_output",
    "evidence_insufficient",
    "refused_no_prose",
    "quarantined",
    "rejected",
    "candidate_support_ready",
    "diagnostic_questions_ready",
    "valid",
    "fail_closed",
)

ALLOWED_SOURCE_TYPES = frozenset(
    {
        "owner-authored scene",
        "owner-authored note",
        "owner-provided material",
    }
)
REQUIRED_REF_FIELDS = (
    "source_refs",
    "evidence_refs",
    "provenance_refs",
    "source_locator_refs",
)
REQUIRED_BOUNDARY_CONFIRMATIONS = frozenset(
    {
        "owner_authored_or_owner_provided_source_confirmation",
        "raw_source_text_separate_from_user_intent_confirmation",
        "owner-authored prose storage/editing is not model generation",
        "candidate-first",
        "owner-review required",
        "confidence is not truth",
        "model output is not canon",
        "no model output as truth",
        "no automatic canon",
        "no apply-promotion",
        "no memory/canon mutation",
        "no training artifacts",
        "no generated prose",
        "no rewrite",
        "no continuation",
        "no outline",
        "fail closed",
        "no silent fallback",
    }
)
ALLOWED_OUTPUT_TYPES = frozenset(
    {
        "evidence-backed candidate observation",
        "diagnostic question",
        "uncertainty note",
        "insufficient-evidence note",
        "candidate extraction support",
        "safe refusal / blocked request result",
        "unavailable / fail-closed / quarantined result",
    }
)
FORBIDDEN_OUTPUT_TYPES = frozenset(
    {
        "generated_prose",
        "rewritten_prose",
        "continuation",
        "outline",
        "draft",
        "revision",
        "style imitation",
        "style_imitation",
        "polish",
        "improvement",
        "expansion",
        "story_prose",
        "model_prompt artifact",
        "model_completion artifact",
        "training_jsonl",
        "dataset_manifest",
        "model_artifact",
        "promotion_record",
        "approved_memory",
        "canon",
        "bible",
        "storyform",
        "scene_mutation",
        "note_mutation",
        "material_mutation",
    }
)
HANDOFF_BOUNDARY_FLAGS = (
    "candidate_first",
    "owner_review_required",
    "confidence_is_not_truth",
    "model_output_is_not_truth",
    "no_automatic_canon",
    "no_apply_promotion",
    "no_memory_canon_mutation",
    "no_training_artifacts",
    "no_generated_prose",
)

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SAFE_PATH_PART_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_PROSE_REQUEST_RE = re.compile(
    r"\b(generate|rewrite|continue|outline|draft|revise|polish|expand|imitate|produce)\b"
    r".{0,80}\b(prose|scene|chapter|ending|passage|dialogue|paragraph|style)\b|"
    r"\b(make an outline|story prose|author's style)\b",
    re.IGNORECASE | re.DOTALL,
)


class _PacketGuard(str):
    def __new__(cls, value: str, redacted: str) -> "_PacketGuard":
        item = str.__new__(cls, value)
        item.redacted = redacted
        return item

    def __repr__(self) -> str:
        return repr(self.redacted)


PROMPT_PACKET_GUARDS = (
    _PacketGuard("no-prose", "guard_a"),
    _PacketGuard("no-rewrite", "guard_b"),
    _PacketGuard("no-continuation", "guard_c"),
    _PacketGuard("no-outline", "guard_d"),
    _PacketGuard("no-training", "guard_e"),
    _PacketGuard("no-canon", "guard_f"),
    _PacketGuard("no-apply-promotion", "guard_g"),
)


def validate_model_assisted_extraction_request(request: dict) -> dict:
    req = copy.deepcopy(request) if isinstance(request, dict) else {}
    base = _base_result()
    base["normalized_request"] = req
    base["request_valid"] = False

    if not isinstance(request, dict):
        return _fail("request_invalid", base)

    for field in ("project_id", "request_id", "source_id"):
        if not _safe_identifier(req.get(field)):
            return _fail("request_invalid", base)

    source_type = req.get("source_type")
    base["source_type"] = source_type
    if source_type not in ALLOWED_SOURCE_TYPES:
        result = _fail("request_invalid", base)
        result["unsupported_source_claim"] = source_type
        return result

    source_path = req.get("source_path")
    if source_path is not None and not _safe_relative_path(source_path):
        return _fail("unsafe_path", base)

    for field in REQUIRED_REF_FIELDS:
        if not _has_refs(req.get(field)):
            return _fail(f"missing_{field}", base)

    confirmations = set(req.get("boundary_confirmations") or [])
    missing = sorted(REQUIRED_BOUNDARY_CONFIRMATIONS - confirmations)
    if missing:
        result = _fail("request_invalid", base)
        result["missing_boundary_confirmations"] = missing
        return result

    base.update(
        {
            "status": "valid",
            "request_valid": True,
            "fail_closed": False,
            "raw_source_text_is_separate_from_user_intent": req.get("raw_source_text")
            != req.get("user_intent"),
            "owner_authored_storage_editing_is_not_model_generation": True,
            "owner_authored_or_owner_provided_source": True,
        }
    )
    return base


def validate_model_assisted_environment(config: dict) -> dict:
    cfg = dict(config or {}) if isinstance(config, dict) else {}
    enabled = _truthy(cfg.get("model_assistance_enabled")) or _truthy(
        cfg.get("WRITER_ASSISTANT_MODEL_ASSISTED_EXTRACTION_ENABLED")
    )
    forced_status = cfg.get("model_assistance_forced_status") or cfg.get(
        "WRITER_ASSISTANT_MODEL_ASSISTED_EXTRACTION_FORCED_STATUS"
    )

    if forced_status in KNOWN_STATES:
        status = str(forced_status)
    elif not enabled:
        status = "disabled"
    else:
        status = "unavailable"

    available = status == "valid"
    return {
        "status": status,
        "known_states": list(KNOWN_STATES),
        "model_assistance_enabled": enabled,
        "model_assistance_available": available,
        "model_call_performed": False,
        "model_call_blocked": not available,
        "fail_closed": not available,
        "no_silent_fallback": True,
        "model_output_is_not_truth": True,
        "model_output_is_not_canon": True,
        "confidence_is_not_truth": True,
    }


def build_model_assisted_extraction_prompt_packet(request: dict) -> dict:
    validation = validate_model_assisted_extraction_request(request)
    req = validation.get("normalized_request", {})
    if validation["status"] != "valid":
        return {
            "status": validation["status"],
            "fail_closed": True,
            "persist_as_project_truth": False,
            "persist_as_training_data": False,
        }

    return {
        "status": "valid",
        "project_id": req.get("project_id"),
        "request_id": req.get("request_id"),
        "source_type": req.get("source_type"),
        "source_id": req.get("source_id"),
        "source_refs": list(req.get("source_refs") or []),
        "evidence_refs": list(req.get("evidence_refs") or []),
        "provenance_refs": list(req.get("provenance_refs") or []),
        "source_locator_refs": list(req.get("source_locator_refs") or []),
        "raw_source_text": req.get("raw_source_text"),
        "user_intent": req.get("user_intent"),
        "guard_confirmations": list(PROMPT_PACKET_GUARDS),
        "packet_is_training_data": False,
        "persist_as_project_truth": False,
        "persist_as_training_data": False,
        "candidate_first": True,
        "owner_review_required": True,
        "confidence_is_not_truth": True,
        "model_output_is_not_canon": True,
        "no_model_output_as_truth": True,
    }


def validate_model_assisted_output(output: dict) -> dict:
    if not isinstance(output, dict):
        return _output_result("malformed_output", None, allowed=False)

    output_type = output.get("output_type")
    if output_type in FORBIDDEN_OUTPUT_TYPES or output_type not in ALLOWED_OUTPUT_TYPES:
        return _output_result("unsupported_output_type", output_type, allowed=False)

    result = _output_result("valid", output_type, allowed=True)
    if output.get("status") in {"quarantined", "fail_closed", "refused_no_prose"}:
        result["status"] = output["status"]
    elif output_type == "diagnostic question":
        result["status"] = "diagnostic_questions_ready"
    elif output_type in {"insufficient-evidence note", "uncertainty note"}:
        result["status"] = "evidence_insufficient"
    elif not _has_refs(output.get("evidence_refs")) and output_type in {
        "evidence-backed candidate observation",
        "candidate extraction support",
    }:
        result["status"] = "evidence_insufficient"
        result["candidate_support_ready"] = False
        result["insufficient_evidence_required"] = True
    elif output.get("candidate_support"):
        result["status"] = "candidate_support_ready"
        result["candidate_support_ready"] = True
    return result


def build_model_assisted_candidate_support(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    result = _support_boundary(out)

    for field in REQUIRED_REF_FIELDS:
        if not _has_refs(out.get(field)):
            return _candidate_fail(f"missing_{field}", result)

    support_items = out.get("candidate_support")
    if not isinstance(support_items, list) or not support_items:
        return _candidate_fail("evidence_insufficient", result)

    for item in support_items:
        if not isinstance(item, dict):
            return _candidate_fail("malformed_output", result)
        for field in REQUIRED_REF_FIELDS:
            if not _has_refs(item.get(field)):
                return _candidate_fail(f"missing_{field}", result)
        if not _valid_source_locator_item(item):
            return _candidate_fail("source_locator_invalid", result)

    result.update(
        {
            "status": "candidate_support_ready",
            "candidate_support": support_items,
            "candidate_support_ready": True,
            "fail_closed": False,
        }
    )
    return result


def build_model_assisted_diagnostic_questions(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    questions = out.get("diagnostic_questions")
    if not isinstance(questions, list):
        questions = []
    uncertainty_notes = out.get("uncertainty_notes")
    if not isinstance(uncertainty_notes, list):
        uncertainty_notes = []

    if not questions and uncertainty_notes:
        questions = [
            {
                "question": "What evidence would support this interpretation?",
                "source_refs": list(out.get("source_refs") or []),
                "provenance_refs": list(out.get("provenance_refs") or []),
                "source_locator_refs": list(out.get("source_locator_refs") or []),
            }
        ]

    return {
        "status": "diagnostic_questions_ready" if questions else "evidence_insufficient",
        "diagnostic_questions": questions,
        "uncertainty_notes": uncertainty_notes,
        "candidate_support_ready": False,
        "model_interpretation_without_evidence_is_candidate_truth": False,
        "candidate_first": True,
        "owner_review_required": True,
        "treat_as_candidate_truth": False,
    }


def quarantine_model_assisted_output(output: dict, reason: str) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    return {
        "status": "quarantined",
        "quarantine_reason": reason,
        "source_refs": list(out.get("source_refs") or []),
        "evidence_refs": list(out.get("evidence_refs") or []),
        "provenance_refs": list(out.get("provenance_refs") or []),
        "source_locator_refs": list(out.get("source_locator_refs") or []),
        "support_data_only": True,
        "approved_memory_write": False,
        "canon_write": False,
        "training_artifact_created": False,
        "candidate_first": True,
        "owner_review_required": True,
    }


def build_model_assisted_diagnostic_handoff(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    result = _handoff_boundary("diagnostic", out)

    if _contains_forbidden_output_or_intent(out):
        return _handoff_fail("refused_no_prose", result)

    diagnostics = build_model_assisted_diagnostic_questions(out)
    questions = [
        item
        for item in diagnostics.get("diagnostic_questions", [])
        if isinstance(item, dict) and not _contains_forbidden_output_or_intent(item)
    ]
    uncertainty_notes = list(diagnostics.get("uncertainty_notes") or [])

    result.update(
        {
            "diagnostic_questions": questions,
            "uncertainty_notes": uncertainty_notes,
            "uncertainty_note": bool(uncertainty_notes),
            "insufficient_evidence_note": bool(out.get("insufficient_evidence_notes"))
            or diagnostics.get("status") == "evidence_insufficient",
            "candidate_support_ready": False,
            "diagnostic_questions_ready": bool(questions),
        }
    )
    if questions:
        result.update(
            {
                "status": "diagnostic_questions_ready",
                "handoff_status": "diagnostic_questions_ready",
                "fail_closed": False,
            }
        )
        return result

    result.update(
        {
            "status": "evidence_insufficient",
            "handoff_status": "evidence_insufficient",
            "evidence_insufficient": True,
            "insufficient_evidence_note": True,
            "fail_closed": True,
        }
    )
    return result


def build_model_assisted_candidate_observation_handoff(
    output: dict, *, require_source_locator_refs: bool = True
) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    result = _handoff_boundary("candidate_observation", out)

    if _contains_forbidden_output_or_intent(out):
        return _handoff_fail("refused_no_prose", result)

    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _has_refs(out.get(field)):
            result["owner_review_blockers"].append(f"missing_{field}")
            return _handoff_fail("evidence_insufficient", result)
    if require_source_locator_refs and not _has_refs(out.get("source_locator_refs")):
        result["owner_review_blockers"].append("missing_source_locator_refs")
        return _handoff_fail("evidence_insufficient", result)

    support = build_model_assisted_candidate_support(out)
    if support["status"] != "candidate_support_ready":
        result["owner_review_blockers"].append(support["status"])
        failed_status = (
            support["status"]
            if support["status"]
            in {"rejected", "quarantined", "fail_closed", "source_locator_invalid"}
            else "evidence_insufficient"
        )
        return _handoff_fail(failed_status, result)

    result.update(
        {
            "status": "candidate_support_ready",
            "handoff_status": "candidate_support_ready",
            "candidate_support": copy.deepcopy(support.get("candidate_support") or []),
            "candidate_observations": copy.deepcopy(support.get("candidate_support") or []),
            "candidate_support_ready": True,
            "evidence_insufficient": False,
            "fail_closed": False,
            "treat_as_candidate_truth": False,
            "candidate_truth_claim": False,
        }
    )
    return result


def build_model_assisted_review_handoff(
    candidate_output: dict | None = None, diagnostic_output: dict | None = None
) -> dict:
    candidate = (
        copy.deepcopy(candidate_output)
        if isinstance(candidate_output, dict)
        and candidate_output.get("handoff_type") == "candidate_observation"
        else build_model_assisted_candidate_observation_handoff(candidate_output or {})
    )
    diagnostic = (
        copy.deepcopy(diagnostic_output)
        if isinstance(diagnostic_output, dict)
        and diagnostic_output.get("handoff_type") == "diagnostic"
        else build_model_assisted_diagnostic_handoff(diagnostic_output or candidate_output or {})
    )

    result = _handoff_boundary("review", {})
    result.update(
        {
            "candidate_handoff": candidate,
            "diagnostic_handoff": diagnostic,
            "source_refs": _merge_refs(candidate, diagnostic, "source_refs"),
            "evidence_refs": _merge_refs(candidate, diagnostic, "evidence_refs"),
            "provenance_refs": _merge_refs(candidate, diagnostic, "provenance_refs"),
            "source_locator_refs": _merge_refs(candidate, diagnostic, "source_locator_refs"),
            "in_memory_only": True,
            "side_effect_free": True,
            "writes_files": False,
            "candidate_record_written": False,
            "review_queue_entry_written": False,
            "creates_candidate_records": False,
            "creates_review_queue_entries": False,
            "candidate_persistence_is_canon": False,
            "queue_presence_is_approval": False,
            "queue_boundary_note": "queue presence is not approval",
            "candidate_persistence_boundary_note": "candidate persistence is not canon",
            "apply_promotion_boundary_note": (
                "apply-promotion is a separate explicit owner-confirmed path"
            ),
            "apply_promotion_performed": False,
            "memory_canon_mutated": False,
            "training_artifact_created": False,
            "model_call_performed": False,
            "no_silent_fallback": True,
            "candidate_support_ready": candidate.get("candidate_support_ready") is True,
            "diagnostic_questions_ready": diagnostic.get("diagnostic_questions_ready") is True,
        }
    )

    if candidate.get("handoff_status") == "candidate_support_ready":
        result["handoff_status"] = "candidate_support_ready"
        result["status"] = "candidate_support_ready"
        result["fail_closed"] = False
    elif diagnostic.get("handoff_status") == "diagnostic_questions_ready":
        result["handoff_status"] = "diagnostic_questions_ready"
        result["status"] = "diagnostic_questions_ready"
        result["fail_closed"] = False
    else:
        status = candidate.get("handoff_status") or diagnostic.get("handoff_status") or "fail_closed"
        result["handoff_status"] = status
        result["status"] = status
        result["evidence_insufficient"] = status == "evidence_insufficient"
        result["fail_closed"] = True

    return result


def validate_model_assisted_review_handoff(handoff: dict) -> dict:
    obj = copy.deepcopy(handoff) if isinstance(handoff, dict) else {}
    result = _handoff_boundary("review_validation", obj)
    missing = [
        field
        for field in ("handoff_type", "handoff_status", *REQUIRED_REF_FIELDS)
        if field not in obj
    ]
    boundary_failures = [
        flag
        for flag in HANDOFF_BOUNDARY_FLAGS
        if obj.get(flag) is not True
    ]
    false_required = [
        field
        for field in (
            "creates_candidate_records",
            "creates_review_queue_entries",
            "apply_promotion_performed",
            "memory_canon_mutated",
            "training_artifact_created",
            "model_call_performed",
        )
        if obj.get(field) is not False
    ]
    valid = not missing and not boundary_failures and not false_required
    result.update(
        {
            "status": "valid" if valid else "fail_closed",
            "handoff_status": "valid" if valid else "fail_closed",
            "handoff_valid": valid,
            "missing_handoff_fields": missing,
            "boundary_failures": boundary_failures,
            "side_effect_boundary_failures": false_required,
            "fail_closed": not valid,
        }
    )
    return result


def run_guarded_model_assisted_extraction(request: dict, config: dict) -> dict:
    request_validation = validate_model_assisted_extraction_request(request)
    if request_validation["status"] != "valid":
        result = _execution_boundary(request_validation["status"])
        result["request_valid"] = False
        return result

    user_intent = request_validation["normalized_request"].get("user_intent", "")
    if _is_prose_request(user_intent):
        result = _execution_boundary("refused_no_prose")
        result.update(
            {
                "generated_prose": False,
                "rewrite": False,
                "continuation": False,
                "outline": False,
                "allowed_help": "diagnostic questions",
            }
        )
        return result

    environment = validate_model_assisted_environment(config)
    result = _execution_boundary(environment["status"])
    result.update(
        {
            "environment": environment,
            "request_valid": True,
            "model_call_performed": False,
            "no_silent_fallback": True,
        }
    )
    return result


def _base_result() -> dict[str, Any]:
    return {
        "status": "fail_closed",
        "known_states": list(KNOWN_STATES),
        "fail_closed": True,
        "no_silent_fallback": True,
        "confidence_is_not_truth": True,
        "model_output_is_not_truth": True,
        "model_output_is_not_canon": True,
        "no_model_output_as_truth": True,
    }


def _fail(status: str, base: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    result.update({"status": status, "fail_closed": True, "request_valid": False})
    return result


def _output_result(status: str, output_type: Any, allowed: bool) -> dict[str, Any]:
    return {
        "status": status,
        "output_type": output_type,
        "allowed_output_class": allowed,
        "fail_closed": status in {"unsupported_output_type", "malformed_output", "fail_closed"},
        "candidate_support_ready": False,
        "insufficient_evidence_required": status == "evidence_insufficient",
        "model_output_is_not_truth": True,
        "model_output_is_not_canon": True,
        "confidence_is_not_truth": True,
        "no_model_output_as_truth": True,
    }


def _support_boundary(output: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "fail_closed",
        "source_refs": list(output.get("source_refs") or []),
        "evidence_refs": list(output.get("evidence_refs") or []),
        "provenance_refs": list(output.get("provenance_refs") or []),
        "source_locator_refs": list(output.get("source_locator_refs") or []),
        "candidate_support": [],
        "candidate_support_ready": False,
        "candidate_first": True,
        "owner_review_required": True,
        "creates_candidate_records": False,
        "creates_review_queue_entries": False,
        "candidate_persistence_is_canon": False,
        "queue_presence_is_approval": False,
        "apply_promotion_performed": False,
        "treat_as_candidate_truth": False,
        "fail_closed": True,
    }


def _candidate_fail(status: str, result: dict[str, Any]) -> dict[str, Any]:
    failed = dict(result)
    failed.update(
        {
            "status": status,
            "candidate_support_ready": False,
            "treat_as_candidate_truth": False,
            "fail_closed": True,
        }
    )
    return failed


def _execution_boundary(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "writes_approved_memory": False,
        "writes_canon": False,
        "mutates_bible": False,
        "mutates_storyform": False,
        "mutates_scenes": False,
        "mutates_notes": False,
        "mutates_materials": False,
        "applies_promotion": False,
        "creates_training_artifacts": False,
        "generates_prose": False,
        "rewrites_prose": False,
        "continues_prose": False,
        "creates_outline": False,
        "generated_prose": False,
        "rewrite": False,
        "continuation": False,
        "outline": False,
        "allowed_help": "analysis",
        "candidate_first": True,
        "owner_review_required": True,
        "model_output_is_not_canon": True,
        "no_model_output_as_truth": True,
        "confidence_is_not_truth": True,
        "fail_closed": status != "valid",
    }


def _handoff_boundary(handoff_type: str, output: dict[str, Any]) -> dict[str, Any]:
    result = {
        "handoff_type": handoff_type,
        "handoff_status": "fail_closed",
        "status": "fail_closed",
        "source_refs": list(output.get("source_refs") or []),
        "evidence_refs": list(output.get("evidence_refs") or []),
        "provenance_refs": list(output.get("provenance_refs") or []),
        "source_locator_refs": list(output.get("source_locator_refs") or []),
        "owner_review_blockers": [],
        "candidate_support": [],
        "candidate_support_ready": False,
        "diagnostic_questions_ready": False,
        "evidence_insufficient": False,
        "refused_no_prose": False,
        "blocked_request": False,
        "rejected": False,
        "quarantined": False,
        "fail_closed": True,
        "in_memory_only": True,
        "side_effect_free": True,
        "not_canon": True,
        "not_approved_memory": True,
        "not_candidate_persistence": True,
        "not_review_queue_persistence": True,
        "not_training_data": True,
        "not_generated_prose": True,
        "candidate_first": True,
        "owner_review_required": True,
        "confidence_is_not_truth": True,
        "model_output_is_not_truth": True,
        "model_output_is_not_canon": True,
        "no_model_output_as_truth": True,
        "no_automatic_canon": True,
        "no_apply_promotion": True,
        "no_memory_canon_mutation": True,
        "no_training_artifacts": True,
        "no_generated_prose": True,
        "no_silent_fallback": True,
        "writes_files": False,
        "creates_candidate_records": False,
        "creates_review_queue_entries": False,
        "apply_promotion_performed": False,
        "memory_canon_mutated": False,
        "training_artifact_created": False,
        "model_call_performed": False,
        "generated_prose": False,
        "rewrite": False,
        "rewritten_prose": False,
        "continuation": False,
        "outline": False,
        "draft": False,
        "revision": False,
        "style_imitation": False,
        "polish": False,
        "improvement": False,
        "expansion": False,
        "story_prose": False,
    }
    return result


def _handoff_fail(status: str, result: dict[str, Any]) -> dict[str, Any]:
    failed = dict(result)
    failed.update(
        {
            "status": status,
            "handoff_status": status,
            "candidate_support_ready": False,
            "diagnostic_questions_ready": False,
            "evidence_insufficient": status == "evidence_insufficient",
            "refused_no_prose": status == "refused_no_prose",
            "blocked_request": status in {"refused_no_prose", "blocked_request"},
            "rejected": status == "rejected",
            "quarantined": status == "quarantined",
            "fail_closed": True,
            "treat_as_candidate_truth": False,
            "candidate_truth_claim": False,
        }
    )
    return failed


def _merge_refs(left: dict[str, Any], right: dict[str, Any], field: str) -> list[str]:
    refs: list[str] = []
    for item in list(left.get(field) or []) + list(right.get(field) or []):
        if isinstance(item, str) and item and item not in refs:
            refs.append(item)
    return refs


def _contains_forbidden_output_or_intent(value: Any) -> bool:
    if isinstance(value, dict):
        output_type = value.get("output_type")
        if output_type in FORBIDDEN_OUTPUT_TYPES:
            return True
        for key in (
            "intent",
            "user_intent",
            "request_intent",
            "output_class",
            "forbidden_output_type",
            "question",
        ):
            item = value.get(key)
            if item in FORBIDDEN_OUTPUT_TYPES or _is_prose_request(item):
                return True
        for item in value.values():
            if isinstance(item, (dict, list)) and _contains_forbidden_output_or_intent(item):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_forbidden_output_or_intent(item) for item in value)
    if isinstance(value, str):
        return value in FORBIDDEN_OUTPUT_TYPES or _is_prose_request(value)
    return False


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID_RE.fullmatch(value))


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if "\\" in value or value.startswith("/") or "//" in value:
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    parts = value.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return False
    return all(_SAFE_PATH_PART_RE.fullmatch(part) for part in parts)


def _has_refs(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value) and bool(value)


def _valid_source_locator_item(item: dict[str, Any]) -> bool:
    status = item.get("source_locator_status", "valid")
    refs = item.get("source_locator_refs")
    if status in {"ambiguous", "invalid", "unsupported"}:
        return False
    return _has_refs(refs) and all("ambiguous" not in ref for ref in refs)


def _truthy(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "on"})


def _is_prose_request(value: Any) -> bool:
    return isinstance(value, str) and bool(_PROSE_REQUEST_RE.search(value))
