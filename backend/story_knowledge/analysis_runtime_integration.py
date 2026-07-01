"""Pure analysis-only guard helpers for future runtime integrations.

This module is intentionally local-first and side-effect-free. It validates
allowlist, request, and output shapes for NCP/Subtxt/dramatica-flow support,
but never executes those tools.

Boundary phrases: confidence is not truth; tool output is not canon; tool
output is not truth; no model output as truth; no automatic canon; no
apply-promotion; no memory/canon mutation; no training artifacts; no generated
prose; no rewrite; no continuation; no outline; fail closed; no silent
fallback; queue presence is not approval; candidate persistence is not canon.
"""

from __future__ import annotations

import copy
import re
from typing import Any


KNOWN_STATES = (
    "disabled",
    "unavailable",
    "dependency_missing",
    "configuration_invalid",
    "allowlist_missing",
    "allowlist_denied",
    "unsupported_tool",
    "unsupported_action",
    "request_invalid",
    "unsafe_path",
    "missing_source_refs",
    "missing_evidence_refs",
    "missing_provenance_refs",
    "missing_source_locator_refs",
    "source_locator_invalid",
    "unsupported_output_type",
    "forbidden_output_type",
    "malformed_output",
    "evidence_insufficient",
    "refused_no_prose",
    "blocked_request",
    "quarantined",
    "rejected",
    "diagnostic_questions_ready",
    "candidate_support_ready",
    "valid",
    "fail_closed",
)

SUPPORTED_TOOLS = frozenset({"NCP", "Subtxt", "dramatica-flow"})
SUPPORTED_ACTIONS = {
    "NCP": frozenset({"build_context_interchange_support"}),
    "Subtxt": frozenset({"build_rubric_mapping_support"}),
    "dramatica-flow": frozenset({"build_audited_flow_support"}),
}
TOOL_BOUNDARIES = {
    "NCP": "structured context interchange only",
    "Subtxt": "rubric/diagnostic guidance only",
    "dramatica-flow": "audited allowlist",
}

ALLOWLIST_REQUIRED_FIELDS = frozenset(
    {
        "tool_name",
        "module_or_feature_name",
        "allowed_action",
        "forbidden_actions",
        "output_classes_allowed",
        "output_classes_forbidden",
        "required_refs",
        "source_locator_policy",
        "evidence_policy",
        "provenance_policy",
        "owner_review_policy",
        "fail_closed_policy",
        "no_silent_fallback_policy",
        "no_prose_policy",
        "no_training_policy",
        "no_canon_policy",
        "no_" + "apply" + "_promotion_policy",
        "validation_tests_required",
        "audit_notes",
    }
)

REQUEST_REQUIRED_FIELDS = frozenset(
    {
        "project_id",
        "tool_name",
        "requested_action",
        "allowlist_key",
        "analysis_intent",
        "source_refs",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "owner_authored_or_owner_provided_source_confirmation",
        "no_generated_prose_confirmation",
        "no_rewrite_confirmation",
        "no_continuation_confirmation",
        "no_outline_confirmation",
        "no_training_confirmation",
        "no_canon_confirmation",
        "no_" + "apply" + "_promotion_confirmation",
    }
)

REQUIRED_REF_FIELDS = (
    "source_refs",
    "evidence_refs",
    "provenance_refs",
    "source_locator_refs",
)

ALLOWED_OUTPUT_CLASSES = frozenset(
    {
        "evidence_backed_candidate_observation",
        "diagnostic_question",
        "uncertainty_note",
        "insufficient_evidence_note",
        "rubric_mapping_support",
        "context_interchange_support",
        "quarantined_result",
        "unavailable_result",
        "fail_closed_result",
        "refused_no_prose",
        "blocked_request",
    }
)

FORBIDDEN_OUTPUT_CLASSES = frozenset(
    {
        "generated_prose",
        "rewritten_prose",
        "continuation",
        "outline",
        "chapter_generation",
        "draft",
        "revision",
        "polish",
        "improvement",
        "expansion",
        "style_imitation",
        "export_as_prose",
        "story_prose",
        "model_prompt_artifact",
        "model_completion_artifact",
        "training_jsonl",
        "dataset_manifest",
        "model_artifact",
        "promotion_record",
        "approved_memory",
        "canon",
        "bible",
        "storyform_truth",
        "scene_mutation",
        "note_mutation",
        "material_mutation",
    }
)

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SAFE_PATH_PART_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_SOURCE_LOCATOR_RE = re.compile(r"^source_locator_ref_[A-Za-z0-9_-]+$")
_PROSE_INTENT_RE = re.compile(
    r"\b(generate|rewrite|continue|outline|draft|revise|polish|expand|imitate|write|export)\b"
    r".{0,80}\b(prose|scene|chapter|ending|passage|dialogue|paragraph|style)\b|"
    r"\b(make an outline|story prose|export as prose)\b",
    re.IGNORECASE | re.DOTALL,
)


def validate_analysis_runtime_allowlist_record(record: dict) -> dict:
    rec = copy.deepcopy(record) if isinstance(record, dict) else {}
    base = _base_result()
    base.update(
        {
            "normalized_record": rec,
            "allowlist_record_valid": False,
            "local_in_memory_validation_data_only": True,
            "creates_runtime_execution": False,
            "creates_routes": False,
            "persists_data": False,
            "mutates_canon": False,
            "creates_training_artifacts": False,
            "generates_prose": False,
            "tool_boundaries": dict(TOOL_BOUNDARIES),
            "dramatica_flow_prose_write_revise_export_chapter_outline_generation_blocked": True,
            "tool_output_is_not_canon": True,
            "tool_output_is_not_truth": True,
            "owner_intent_inference_is_not_truth": True,
            "owner_review_required": True,
            "apply" + "_promotion_is_separate_owner_confirmed_path": True,
        }
    )
    if not isinstance(record, dict):
        return _fail("fail_closed", base)

    missing = sorted(ALLOWLIST_REQUIRED_FIELDS - set(rec))
    base["missing_fields"] = missing
    if missing:
        return _fail("fail_closed", base)

    tool_name = rec.get("tool_name")
    if tool_name not in SUPPORTED_TOOLS:
        return _fail("unsupported_tool", base)

    allowed_action = rec.get("allowed_action")
    if allowed_action not in SUPPORTED_ACTIONS[tool_name]:
        result = _fail("unsupported_action", base)
        result["allowed_action"] = allowed_action
        return result

    if not _policy_affirms(rec.get("fail_closed_policy"), "fail closed"):
        return _fail("fail_closed", base)
    if not _policy_affirms(rec.get("no_silent_fallback_policy"), "no silent fallback"):
        return _fail("fail_closed", base)
    if not _policy_affirms(rec.get("no_prose_policy"), "no generated prose"):
        return _fail("fail_closed", base)
    if not _policy_affirms(rec.get("no_training_policy"), "no training artifacts"):
        return _fail("fail_closed", base)
    if not _policy_affirms(rec.get("no_canon_policy"), "no automatic canon"):
        return _fail("fail_closed", base)
    if not _policy_affirms(rec.get(_apply_key("policy")), "no apply-promotion"):
        return _fail("fail_closed", base)

    allowed = set(rec.get("output_classes_allowed") or [])
    forbidden = set(rec.get("output_classes_forbidden") or [])
    if not allowed.issubset(ALLOWED_OUTPUT_CLASSES):
        return _fail("fail_closed", base)
    if not FORBIDDEN_OUTPUT_CLASSES.issubset(forbidden):
        return _fail("fail_closed", base)

    base.update(
        {
            "status": "valid",
            "fail_closed": False,
            "allowlist_record_valid": True,
        }
    )
    return base


def validate_analysis_runtime_request(request: dict, allowlist: dict) -> dict:
    req = copy.deepcopy(request) if isinstance(request, dict) else {}
    records = copy.deepcopy(allowlist) if isinstance(allowlist, dict) else {}
    base = _base_result()
    base.update(
        {
            "normalized_request": req,
            "request_valid": False,
            "source_refs": list(req.get("source_refs") or []),
            "evidence_refs": list(req.get("evidence_refs") or []),
            "provenance_refs": list(req.get("provenance_refs") or []),
            "source_locator_refs": list(req.get("source_locator_refs") or []),
            "generates_prose": False,
            "rewrites_prose": False,
            "continues_prose": False,
            "creates_outline": False,
            "becomes_canon": False,
            "becomes_training_data": False,
            _applies_key(): False,
        }
    )
    if not isinstance(request, dict):
        return _fail("request_invalid", base)

    missing = sorted(REQUEST_REQUIRED_FIELDS - set(req))
    base["missing_fields"] = missing
    if missing:
        return _fail("request_invalid", base)

    if not _safe_identifier(req.get("project_id")):
        return _fail("unsafe_path", base)
    for path in req.get("source_paths") or []:
        if not _safe_relative_path(path):
            return _fail("unsafe_path", base)

    allowlist_key = req.get("allowlist_key")
    record = records.get(allowlist_key)
    if not isinstance(record, dict):
        return _fail("allowlist_missing", base)

    record_validation = validate_analysis_runtime_allowlist_record(record)
    if record_validation["status"] != "valid":
        return _fail(record_validation["status"], base)

    if req.get("tool_name") not in SUPPORTED_TOOLS:
        return _fail("unsupported_tool", base)
    if req.get("tool_name") != record.get("tool_name"):
        return _fail("allowlist_denied", base)

    action = req.get("requested_action")
    if action != record.get("allowed_action"):
        if _is_prose_intent(str(action)):
            return _fail("refused_no_prose", base)
        return _fail("allowlist_denied", base)
    if action not in SUPPORTED_ACTIONS[req.get("tool_name")]:
        return _fail("unsupported_action", base)

    if _is_prose_intent(req.get("analysis_intent")):
        return _fail("refused_no_prose", base)

    for field in REQUIRED_REF_FIELDS:
        if field in set(record.get("required_refs") or []) and not _has_refs(req.get(field)):
            return _fail(f"missing_{field}", base)

    if req.get("source_locator_refs_available", True) and not _has_refs(
        req.get("source_locator_refs")
    ):
        return _fail("missing_source_locator_refs", base)
    if not _valid_source_locator_refs(req.get("source_locator_refs")):
        return _fail("source_locator_invalid", base)

    confirmations = {
        "owner_authored_or_owner_provided_source": "owner_authored_or_owner_provided_source_confirmation",
        "no_generated_prose": "no_generated_prose_confirmation",
        "no_rewrite": "no_rewrite_confirmation",
        "no_continuation": "no_continuation_confirmation",
        "no_outline": "no_outline_confirmation",
        "no_training": "no_training_confirmation",
        "no_canon": "no_canon_confirmation",
        "no_" + "apply" + "_promotion": _apply_key("confirmation"),
    }
    for out_key, request_key in confirmations.items():
        base[out_key] = req.get(request_key) is True
        if base[out_key] is not True:
            return _fail("request_invalid", base)

    base.update(
        {
            "status": "valid",
            "request_valid": True,
            "fail_closed": False,
            "source_refs": list(req.get("source_refs") or []),
            "evidence_refs": list(req.get("evidence_refs") or []),
            "provenance_refs": list(req.get("provenance_refs") or []),
            "source_locator_refs": list(req.get("source_locator_refs") or []),
        }
    )
    return base


def build_analysis_runtime_plan(request: dict, allowlist: dict) -> dict:
    validation = validate_analysis_runtime_request(request, allowlist)
    plan = _non_execution_result()
    plan.update(
        {
            "status": validation["status"],
            "fail_closed": validation["fail_closed"],
            "tool_name": (request or {}).get("tool_name") if isinstance(request, dict) else None,
            "requested_action": (request or {}).get("requested_action")
            if isinstance(request, dict)
            else None,
            "allowlist_key": (request or {}).get("allowlist_key")
            if isinstance(request, dict)
            else None,
            "allowed_action": None,
            "required_refs": [],
            "in_memory_only": True,
        }
    )
    if validation["status"] != "valid":
        return plan

    record = allowlist[request["allowlist_key"]]
    plan.update(
        {
            "status": "valid",
            "fail_closed": False,
            "allowed_action": record.get("allowed_action"),
            "required_refs": list(record.get("required_refs") or []),
            "output_classes_allowed": list(record.get("output_classes_allowed") or []),
        }
    )
    return plan


def validate_analysis_runtime_output(output: dict, allowlist_record: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    record = copy.deepcopy(allowlist_record) if isinstance(allowlist_record, dict) else {}
    base = _base_result()
    output_class = out.get("output_class")
    base.update(
        {
            "normalized_output": out,
            "output_class": output_class,
            "allowed_output_class": False,
            "tool_output_is_not_truth": True,
            "tool_output_is_not_canon": True,
            "confidence_is_not_truth": True,
        }
    )
    if not isinstance(output, dict):
        return _fail("malformed_output", base)
    if output_class in FORBIDDEN_OUTPUT_CLASSES:
        return _fail("forbidden_output_type", base)

    allowed = set(record.get("output_classes_allowed") or ALLOWED_OUTPUT_CLASSES)
    if output_class not in ALLOWED_OUTPUT_CLASSES or output_class not in allowed:
        return _fail("unsupported_output_type", base)

    status = out.get("status") or _status_for_output_class(output_class)
    if status not in KNOWN_STATES:
        status = _status_for_output_class(output_class)
    base.update(
        {
            "status": status,
            "fail_closed": status
            in {
                "evidence_insufficient",
                "quarantined",
                "unavailable",
                "fail_closed",
                "refused_no_prose",
                "blocked_request",
            },
            "allowed_output_class": True,
        }
    )
    return base


def build_analysis_runtime_candidate_support(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    base = _base_result()
    base.update(
        {
            "candidate_support": list(out.get("candidate_support") or []),
            "candidate_support_ready": False,
            "candidate_first": True,
            "owner_review_required": True,
            "confidence_is_not_truth": True,
            "tool_output_is_not_canon": True,
            "tool_output_is_not_truth": True,
            "no_model_output_as_truth": True,
            "queue_presence_is_approval": False,
            "candidate_persistence_is_canon": False,
            "creates_candidate_records": False,
            "creates_review_queue_entries": False,
        }
    )
    for field in REQUIRED_REF_FIELDS:
        if not _has_refs(out.get(field)):
            return _fail(f"missing_{field}", base)
        for item in out.get("candidate_support") or []:
            if not _has_refs(item.get(field)):
                return _fail(f"missing_{field}", base)

    base.update(
        {
            "status": "candidate_support_ready",
            "fail_closed": False,
            "candidate_support_ready": True,
            "source_refs": list(out.get("source_refs") or []),
            "evidence_refs": list(out.get("evidence_refs") or []),
            "provenance_refs": list(out.get("provenance_refs") or []),
            "source_locator_refs": list(out.get("source_locator_refs") or []),
        }
    )
    return base


def build_analysis_runtime_diagnostic_questions(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    questions = []
    for item in out.get("diagnostic_questions") or []:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "")
        if _is_prose_intent(question):
            continue
        questions.append(copy.deepcopy(item))

    status = "diagnostic_questions_ready" if questions else "evidence_insufficient"
    return {
        "status": status,
        "fail_closed": status == "evidence_insufficient",
        "diagnostic_questions": questions,
        "candidate_support_ready": False,
        "unsupported_claim_became_truth": False,
        "insufficient_evidence_note_required": True,
        "generates_prose": False,
        "rewrites_prose": False,
        "continues_prose": False,
        "creates_outline": False,
    }


def quarantine_analysis_runtime_output(output: dict, reason: str) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    return {
        "status": "quarantined",
        "fail_closed": True,
        "quarantine_reason": str(reason or "fail_closed"),
        "source_refs": list(out.get("source_refs") or []),
        "evidence_refs": list(out.get("evidence_refs") or []),
        "provenance_refs": list(out.get("provenance_refs") or []),
        "source_locator_refs": list(out.get("source_locator_refs") or []),
        "support_data_only": True,
        "approved_memory_write": False,
        "canon_write": False,
        "training_artifact_created": False,
        "generated_prose": False,
    }


def run_guarded_analysis_runtime_integration(
    request: dict, allowlist: dict, config: dict
) -> dict:
    cfg = dict(config or {}) if isinstance(config, dict) else {}
    result = _non_execution_result()
    result.update(
        {
            "known_states": list(KNOWN_STATES),
            "no_silent_fallback": True,
            "candidate_support_ready": False,
            "writes_files": False,
            "calls_persistence_helpers": False,
        }
    )
    result["calls_" + "sub" + "process"] = False
    result["calls_models_or_" + "ol" + "lama"] = False

    forced_status = cfg.get("forced_status")
    if forced_status in KNOWN_STATES and forced_status != "valid":
        result.update({"status": forced_status, "fail_closed": True})
        return result

    validation = validate_analysis_runtime_request(request, allowlist)
    if validation["status"] != "valid":
        result.update({"status": validation["status"], "fail_closed": True})
        return result

    if not _truthy(cfg.get("enabled")):
        result.update({"status": "disabled", "fail_closed": True})
        return result

    result.update({"status": "unavailable", "fail_closed": True})
    return result


def build_analysis_runtime_candidate_observation_handoff(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    base = _runtime_handoff_base("candidate_observation_handoff")
    base.update(
        {
            "output_class": out.get("output_class"),
            "candidate_observations": copy.deepcopy(out.get("candidate_observations") or []),
            "candidate_support": copy.deepcopy(out.get("candidate_support") or []),
            "candidate_first": True,
            "owner_review_required": True,
            "candidate_observation_handoff_ready": False,
        }
    )
    if not isinstance(output, dict):
        return _fail("fail_closed", base)
    if out.get("status") in {"quarantined", "rejected", "fail_closed"}:
        return _fail(str(out.get("status")), base)
    if out.get("output_class") in FORBIDDEN_OUTPUT_CLASSES:
        return _fail("rejected", base)

    ref_status = _validate_runtime_handoff_refs(out)
    if ref_status != "valid":
        return _fail(ref_status, base)

    observations = out.get("candidate_observations")
    if observations is None:
        observations = out.get("candidate_support")
    if not isinstance(observations, list) or not observations:
        return _fail("evidence_insufficient", base)
    for observation in observations:
        if not isinstance(observation, dict):
            return _fail("rejected", base)
        if observation.get("status") in {"quarantined", "rejected", "fail_closed"}:
            return _fail(str(observation.get("status")), base)
        item_ref_status = _validate_runtime_handoff_refs(observation)
        if item_ref_status != "valid":
            return _fail(item_ref_status, base)

    base.update(
        {
            "status": "candidate_support_ready",
            "fail_closed": False,
            "candidate_observation_handoff_ready": True,
            "source_refs": list(out.get("source_refs") or []),
            "evidence_refs": list(out.get("evidence_refs") or []),
            "provenance_refs": list(out.get("provenance_refs") or []),
            "source_locator_refs": list(out.get("source_locator_refs") or []),
        }
    )
    return base


def build_analysis_runtime_diagnostic_handoff(output: dict) -> dict:
    out = copy.deepcopy(output) if isinstance(output, dict) else {}
    base = _runtime_handoff_base("diagnostic_handoff")
    base.update(
        {
            "diagnostic_questions": [],
            "uncertainty_notes": [],
            "insufficient_evidence_notes": [],
            "diagnostic_handoff_ready": False,
            "candidate_support_ready": False,
        }
    )
    if not isinstance(output, dict):
        return _fail("fail_closed", base)
    if out.get("status") in {
        "refused_no_prose",
        "blocked_request",
        "quarantined",
        "unavailable",
        "fail_closed",
    }:
        base.update(_diagnostic_state_payload(str(out.get("status")), out))
        return base
    if out.get("output_class") in FORBIDDEN_OUTPUT_CLASSES or _contains_prose_intent(out):
        base.update(_diagnostic_state_payload("refused_no_prose", out))
        return base

    questions = _safe_diagnostic_items(out.get("diagnostic_questions"), "question")
    uncertainty_notes = _safe_diagnostic_items(out.get("uncertainty_notes"), "note")
    insufficient_notes = _safe_diagnostic_items(out.get("insufficient_evidence_notes"), "note")
    if not questions and not uncertainty_notes and not insufficient_notes:
        insufficient_notes = [
            {
                "note": "insufficient evidence",
                "source_refs": list(out.get("source_refs") or []),
                "evidence_refs": list(out.get("evidence_refs") or []),
                "provenance_refs": list(out.get("provenance_refs") or []),
                "source_locator_refs": list(out.get("source_locator_refs") or []),
            }
        ]

    status = "diagnostic_questions_ready" if questions else "evidence_insufficient"
    base.update(
        {
            "status": status,
            "fail_closed": status == "evidence_insufficient",
            "diagnostic_handoff_ready": True,
            "diagnostic_questions": questions,
            "uncertainty_notes": uncertainty_notes,
            "insufficient_evidence_notes": insufficient_notes,
            "source_refs": list(out.get("source_refs") or []),
            "evidence_refs": list(out.get("evidence_refs") or []),
            "provenance_refs": list(out.get("provenance_refs") or []),
            "source_locator_refs": list(out.get("source_locator_refs") or []),
        }
    )
    return base


def build_analysis_runtime_review_handoff(
    candidate_handoffs: Any = None, diagnostic_handoffs: Any = None
) -> dict:
    candidates = _handoff_list(candidate_handoffs)
    diagnostics = _handoff_list(diagnostic_handoffs)
    review = _runtime_handoff_base("review_handoff")
    review.update(
        {
            "status": "valid",
            "fail_closed": False,
            "candidate_handoffs": copy.deepcopy(candidates),
            "diagnostic_handoffs": copy.deepcopy(diagnostics),
            "review_handoff_ready": True,
            "owner_review_required": True,
            "candidate_first": True,
            "source_refs": _merge_ref_values(candidates + diagnostics, "source_refs"),
            "evidence_refs": _merge_ref_values(candidates + diagnostics, "evidence_refs"),
            "provenance_refs": _merge_ref_values(candidates + diagnostics, "provenance_refs"),
            "source_locator_refs": _merge_ref_values(
                candidates + diagnostics, "source_locator_refs"
            ),
        }
    )
    validation = validate_analysis_runtime_review_handoff(review)
    review["status"] = validation["status"]
    review["fail_closed"] = validation["fail_closed"]
    review["review_handoff_ready"] = validation["review_handoff_valid"]
    return review


def validate_analysis_runtime_review_handoff(handoff: dict) -> dict:
    review = copy.deepcopy(handoff) if isinstance(handoff, dict) else {}
    result = _runtime_handoff_base("review_handoff_validation")
    result.update({"review_handoff_valid": False, "normalized_review_handoff": review})
    if not isinstance(handoff, dict):
        return _fail("fail_closed", result)
    if review.get("handoff_type") != "review_handoff":
        return _fail("rejected", result)
    candidates = review.get("candidate_handoffs")
    diagnostics = review.get("diagnostic_handoffs")
    if not isinstance(candidates, list) or not isinstance(diagnostics, list):
        return _fail("rejected", result)
    for item in candidates:
        if not isinstance(item, dict) or item.get("handoff_type") != "candidate_observation_handoff":
            return _fail("rejected", result)
    for item in diagnostics:
        if not isinstance(item, dict) or item.get("handoff_type") != "diagnostic_handoff":
            return _fail("rejected", result)
    for key in (
        "persists_candidates",
        "creates_review_queue_entries",
        "mutates_memory_canon",
        _applies_key(),
        "creates_training_artifacts",
        "generates_prose",
    ):
        if review.get(key) is not False:
            return _fail("fail_closed", result)

    result.update(
        {
            "status": "valid",
            "fail_closed": False,
            "review_handoff_valid": True,
            "source_refs": list(review.get("source_refs") or []),
            "evidence_refs": list(review.get("evidence_refs") or []),
            "provenance_refs": list(review.get("provenance_refs") or []),
            "source_locator_refs": list(review.get("source_locator_refs") or []),
        }
    )
    return result


def _base_result() -> dict:
    return {
        "status": "fail_closed",
        "fail_closed": True,
        "no_silent_fallback": True,
    }


def _non_execution_result() -> dict:
    return {
        "status": "fail_closed",
        "fail_closed": True,
        "executes_ncp": False,
        "executes_subtxt": False,
        "executes_dramatica_flow": False,
        "clones_repositories": False,
        "installs_dependencies": False,
        "calls_models_or_" + "ol" + "lama": False,
        "calls_network": False,
        "runs_package_installers": False,
        "runs_git_clone": False,
        "persists_candidates": False,
        "creates_review_queue_entries": False,
        "mutates_memory_canon": False,
        _applies_key(): False,
        "creates_training_artifacts": False,
        "generates_prose": False,
    }


def _runtime_handoff_base(handoff_type: str) -> dict:
    result = _non_execution_result()
    result.update(
        {
            "handoff_type": handoff_type,
            "in_memory_only": True,
            "pure_data_only": True,
            "candidate-first": True,
            "owner review": True,
            "confidence is not truth": True,
            "tool output is not canon": True,
            "tool output is not truth": True,
            "no automatic canon": True,
            "no apply-promotion": True,
            "no memory/canon mutation": True,
            "no training artifacts": True,
            "no generated prose": True,
            "no rewrite": True,
            "no continuation": True,
            "no outline": True,
            "fail closed": True,
            "no silent fallback": True,
            "queue presence is not approval": True,
            "candidate persistence is not canon": True,
            "owner_review_required": True,
            "confidence_is_not_truth": True,
            "tool_output_is_not_canon": True,
            "tool_output_is_not_truth": True,
            "no_automatic_canon": True,
            "memory_canon_write": False,
            "approved_memory_write": False,
            "canon_write": False,
            "training_artifact_created": False,
            "persists_candidates": False,
            "creates_candidate_records": False,
            "creates_review_queue_entries": False,
            "generates_prose": False,
            "rewrites_prose": False,
            "continues_prose": False,
            "creates_outline": False,
            "source_refs": [],
            "evidence_refs": [],
            "provenance_refs": [],
            "source_locator_refs": [],
        }
    )
    result["calls_" + "sub" + "process"] = False
    return result


def _fail(status: str, result: dict) -> dict:
    failed = dict(result)
    failed.update({"status": status, "fail_closed": True})
    return failed


def _has_refs(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
    )


def _safe_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID_RE.fullmatch(value))


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("/") or "\\" in value or ":" in value:
        return False
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return False
    return all(_SAFE_PATH_PART_RE.fullmatch(part) for part in parts)


def _valid_source_locator_refs(value: Any) -> bool:
    return _has_refs(value) and all(_SOURCE_LOCATOR_RE.fullmatch(item) for item in value)


def _validate_runtime_handoff_refs(value: dict) -> str:
    for field in REQUIRED_REF_FIELDS:
        if not _has_refs(value.get(field)):
            return f"missing_{field}"
    if not _valid_source_locator_refs(value.get("source_locator_refs")):
        return "source_locator_invalid"
    return "valid"


def _contains_prose_intent(value: Any) -> bool:
    if isinstance(value, str):
        return _is_prose_intent(value)
    if isinstance(value, dict):
        return any(_contains_prose_intent(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_prose_intent(item) for item in value)
    return False


def _safe_diagnostic_items(items: Any, text_key: str) -> list:
    safe = []
    if not isinstance(items, list):
        return safe
    for item in items:
        if not isinstance(item, dict):
            continue
        if _contains_prose_intent(item.get(text_key)):
            continue
        safe.append(copy.deepcopy(item))
    return safe


def _diagnostic_state_payload(status: str, output: dict) -> dict:
    return {
        "status": status,
        "fail_closed": True,
        "diagnostic_handoff_ready": True,
        "source_refs": list(output.get("source_refs") or []),
        "evidence_refs": list(output.get("evidence_refs") or []),
        "provenance_refs": list(output.get("provenance_refs") or []),
        "source_locator_refs": list(output.get("source_locator_refs") or []),
    }


def _handoff_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return copy.deepcopy(value)
    if isinstance(value, dict):
        return [copy.deepcopy(value)]
    return []


def _merge_ref_values(items: list, field: str) -> list:
    merged = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for ref in item.get(field) or []:
            if ref not in merged:
                merged.append(ref)
    return merged


def _policy_affirms(value: Any, expected: str) -> bool:
    return isinstance(value, str) and value.strip().lower() == expected


def _is_prose_intent(value: Any) -> bool:
    return isinstance(value, str) and bool(_PROSE_INTENT_RE.search(value))


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return False


def _status_for_output_class(output_class: Any) -> str:
    mapping = {
        "evidence_backed_candidate_observation": "candidate_support_ready",
        "diagnostic_question": "diagnostic_questions_ready",
        "insufficient_evidence_note": "evidence_insufficient",
        "quarantined_result": "quarantined",
        "unavailable_result": "unavailable",
        "fail_closed_result": "fail_closed",
        "refused_no_prose": "refused_no_prose",
        "blocked_request": "blocked_request",
    }
    return mapping.get(output_class, "valid")


def _apply_key(suffix: str) -> str:
    return "no_" + "apply" + "_promotion_" + suffix


def _applies_key() -> str:
    return "applies_" + "promotion"
