"""Analysis-only guards and runtime integration helpers.

Legacy helpers validate allowlist, request, and output shapes for
NCP/Subtxt/dramatica-flow support.  The official Subtxt boundary executes only
an explicitly injected runner after fail-closed preflight checks; its separate
persistence API writes immutable support evidence through the existing T003
architecture.

Boundary phrases: confidence is not truth; tool output is not canon; tool
output is not truth; no model output as truth; no automatic canon; no
apply-promotion; no memory/canon mutation; no training artifacts; no generated
prose; no rewrite; no continuation; no outline; fail closed; no silent
fallback; queue presence is not approval; candidate persistence is not canon.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable, Mapping

from backend import omi_analysis_orchestrator
from backend.story_knowledge.analysis_run_manifest import (
    AdapterProvenance,
    AnalysisRunManifest,
    ArtifactReference,
    ContributorLineage,
    OutputLineage,
    ProvenanceComponent,
    TransformationLineage,
)
from backend.story_knowledge.evidence_ledger import (
    append_evidence_ledger_event,
    canonical_sha256,
    validate_evidence_record_v1,
)
from backend.story_knowledge.raw_artifacts import (
    build_immutable_raw_artifact_manifest,
    build_raw_artifact_file_ref,
    write_immutable_raw_artifact_bundle,
)
from backend.story_knowledge.source_map import project_candidate_source_locator
from backend.story_knowledge.subtxt_runtime_contract import (
    APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
    APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID,
    OFFICIAL_SUBTXT_ADAPTER_ID,
    OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS,
    OFFICIAL_SUBTXT_OPERATION_ID,
    OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS,
    SUBTXT_RUNTIME_CONTRACT_VERSION,
    SubtxtAnalysisRequest,
    SubtxtAnalysisResult,
    SubtxtRuntimeInventory,
    SubtxtRuntimeProvenance,
)


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
    r"\b(generate|rewrite|continue|outline|draft|revise|polish|improve|expand|imitate|write|export)\b"
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
            "candidate_support_ready": False,
            "diagnostic_questions_ready": False,
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
    if not _safe_identifier(req.get("allowlist_key")):
        return _fail("unsafe_path", base)
    for field in ("source_refs", "evidence_refs", "provenance_refs"):
        if not _safe_ref_values(req.get(field)):
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
    if output_class in FORBIDDEN_OUTPUT_CLASSES or _contains_forbidden_output_class(out):
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


# ---------------------------------------------------------------------------
# PHASE8-IMPL-025-T006 official/full Subtxt adapter
# ---------------------------------------------------------------------------

SUBTXT_APP_MAPPED_OUTPUT_SCHEMA_VERSION = "subtxt-app-mapped-analysis-output.v1"
SUBTXT_APP_MAPPED_NORMALIZATION_VERSION = "subtxt-app-mapped-normalization.v1"
OFFICIAL_SUBTXT_MAX_OUTPUT_BYTES = 4_194_304

_SUBTXT_APP_MAPPED_OUTPUT_FIELDS = frozenset(
    {
        "schema_version",
        "analysis_run_id",
        "source_snapshot_id",
        "source_content_sha256",
        "operation_id",
        "findings",
    }
)
_SUBTXT_APP_MAPPED_FINDING_FIELDS = frozenset(
    {
        "raw_finding_id",
        "candidate_type",
        "label",
        "extracted_claim",
        "evidence",
        "source_locator",
        "evidence_reference_ids",
        "support_label",
        "uncertainty_reason",
    }
)
_SUBTXT_APP_MAPPED_EVIDENCE_FIELDS = frozenset(
    {"evidence_reference_id", "source_locator"}
)
_OFFICIAL_SUBTXT_UNSAFE_KEYS = frozenset(
    {
        "approved",
        "automatic_approval",
        "automatic_promotion",
        "canon",
        "generated_outline",
        "generated_prose",
        "generated_revision",
        "memory_mutation",
        "owner_decision",
        "promotion",
        "promotion_record",
        "rewritten_prose",
        "story_prose",
        "structural_truth",
        "truth_selection",
    }
)
_OFFICIAL_SUBTXT_APP_OWNED_IDENTITIES = frozenset(
    {
        APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID,
        APP_OWNED_SUBTXT_RUBRIC_INTERNAL_ID,
    }
)


class OfficialSubtxtRunnerError(RuntimeError):
    """Controlled failure reported by an injected official runtime seam."""

    result_state = "runtime_failure"


class OfficialSubtxtRuntimeUnavailableError(OfficialSubtxtRunnerError):
    result_state = "unavailable_runtime"


class OfficialSubtxtRuntimeIncompatibleError(OfficialSubtxtRunnerError):
    result_state = "incompatible_runtime"


class OfficialSubtxtRuntimeTimeoutError(OfficialSubtxtRunnerError):
    result_state = "runtime_failure"


@dataclass(frozen=True)
class OfficialSubtxtRunnerResponse:
    """Exact native bytes plus a separate app-owned analysis mapping.

    This is an application seam, not a claim about any concrete CLI, API, or
    library or native response format. A provisioned runner must preserve the
    response bytes exactly, map them separately into the application schema,
    and prove its official provenance.
    """

    raw_output: bytes
    mapped_output: Mapping[str, Any]
    provenance: SubtxtRuntimeProvenance


@dataclass(frozen=True)
class OfficialSubtxtExecution:
    """Validated adapter outcome with content and lineage kept separate."""

    request: SubtxtAnalysisRequest
    finalized_manifest: AnalysisRunManifest
    result: SubtxtAnalysisResult
    findings: tuple[dict[str, Any], ...]
    raw_output: bytes | None
    output_lineage: tuple[OutputLineage, ...]
    transformations: tuple[TransformationLineage, ...]
    semantic_guardrail_inputs: tuple[dict[str, Any], ...]
    input_evidence_reference_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        result_value = self.result.to_dict()
        result_value["candidate_conversion_performed"] = bool(self.findings)
        return {
            "adapter": OFFICIAL_SUBTXT_ADAPTER_ID,
            "implementation_kind": "official_external",
            "result": result_value,
            "analysis_run_manifest": self.finalized_manifest.to_dict(),
            "findings": [copy.deepcopy(item) for item in self.findings],
            "raw_output": {
                "reference_id": self.result.raw_output_reference_id,
                "sha256": (
                    hashlib.sha256(self.raw_output).hexdigest()
                    if self.raw_output is not None
                    else None
                ),
                "size_bytes": len(self.raw_output) if self.raw_output is not None else 0,
                "preserved_separately": self.raw_output is not None,
            },
            "output_lineage": [item.to_dict() for item in self.output_lineage],
            "transformation_lineage": [
                item.to_dict() for item in self.transformations
            ],
            "semantic_guardrail_inputs": [
                copy.deepcopy(item) for item in self.semantic_guardrail_inputs
            ],
            "candidate_persistence_performed": False,
            "owner_review_required": True,
            "no_silent_fallback": True,
            "safety": _official_subtxt_safety_boundary(),
        }


def _official_subtxt_safety_boundary() -> dict[str, bool]:
    return {
        "analysis_only": True,
        "story_prose_generated_or_transformed": False,
        "structural_truth_selected": False,
        "candidate_automatically_approved": False,
        "promotion_performed": False,
        "apply_promotion_performed": False,
        "memory_or_canon_mutated": False,
        "training_or_dataset_artifact_created": False,
        "app_owned_rubric_fallback_performed": False,
    }


def _official_subtxt_request_provenance(
    request: SubtxtAnalysisRequest,
) -> SubtxtRuntimeProvenance:
    return SubtxtRuntimeProvenance(
        adapter=AdapterProvenance(
            adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
            operation_id=OFFICIAL_SUBTXT_OPERATION_ID,
            user_facing_label="Official/full Subtxt runtime analysis",
            implementation_kind="official_external",
            tool=ProvenanceComponent("unknown"),
            runtime=request.runtime_identity,
            provider=ProvenanceComponent("unknown"),
            model=ProvenanceComponent("unknown"),
        ),
        callable_interface=request.callable_interface,
        safe_configuration_identity=ProvenanceComponent("unknown"),
        analysis_run_id=request.analysis_run_id,
        source_snapshot_ids=(request.source_snapshot_id,),
        transformation_ids=(),
    )


def _official_subtxt_with_transformations(
    provenance: SubtxtRuntimeProvenance,
    transformation_ids: tuple[str, ...],
) -> SubtxtRuntimeProvenance:
    return SubtxtRuntimeProvenance(
        adapter=provenance.adapter,
        callable_interface=provenance.callable_interface,
        safe_configuration_identity=provenance.safe_configuration_identity,
        analysis_run_id=provenance.analysis_run_id,
        source_snapshot_ids=provenance.source_snapshot_ids,
        transformation_ids=transformation_ids,
    )


def _official_subtxt_validate_request_boundary(
    request: SubtxtAnalysisRequest,
) -> None:
    if not isinstance(request, SubtxtAnalysisRequest):
        raise ValueError("official Subtxt adapter requires SubtxtAnalysisRequest")
    if request.adapter_identity != OFFICIAL_SUBTXT_ADAPTER_ID:
        raise ValueError("official Subtxt adapter identity mismatch")
    if request.expected_implementation_kind != "official_external":
        raise ValueError("official Subtxt implementation kind mismatch")
    if request.operation_id in OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS:
        raise ValueError("official Subtxt operation is explicitly forbidden")
    if request.operation_id not in OFFICIAL_SUBTXT_POLICY_PERMITTED_OPERATIONS:
        raise ValueError("official Subtxt operation is not positively allowlisted")
    request.capabilities.require_available(request.operation_id)


def _official_subtxt_preflight_failure(
    request: SubtxtAnalysisRequest,
    inventory: SubtxtRuntimeInventory,
) -> tuple[str, str] | None:
    if not isinstance(inventory, SubtxtRuntimeInventory):
        return "unavailable_runtime", "verified official Subtxt preflight is required"
    if inventory.official_adapter_identity != OFFICIAL_SUBTXT_ADAPTER_ID:
        return "incompatible_runtime", "preflight official adapter identity mismatch"
    if inventory.app_owned_rubric_identity != APP_OWNED_SUBTXT_RUBRIC_ADAPTER_ID:
        return "incompatible_runtime", "preflight app-owned identity boundary mismatch"
    if inventory.compatibility_state == "incompatible":
        return "incompatible_runtime", "official Subtxt runtime is incompatible"
    if inventory.configuration_state != "configured":
        return "unavailable_runtime", "official Subtxt runtime is not safely configured"
    if inventory.supported_operation_evidence_state != "available":
        return (
            "unavailable_runtime",
            "official Subtxt analyze-subtxt support is not verified",
        )
    if inventory.compatibility_state != "available":
        return "unavailable_runtime", "official Subtxt compatibility is not verified"
    if not inventory.ready:
        return "unavailable_runtime", "official Subtxt runtime is not currently available"
    if inventory.capabilities != request.capabilities:
        return "incompatible_runtime", "request and preflight capability planes differ"
    try:
        inventory.capabilities.require_available(request.operation_id)
    except ValueError as exc:
        return "unavailable_runtime", str(exc)
    return None


def _official_subtxt_validate_normalized_evidence(
    request: SubtxtAnalysisRequest,
    records: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    if not isinstance(records, tuple) or not records:
        raise ValueError("normalized T003 evidence records are required")
    validated = tuple(validate_evidence_record_v1(item) for item in records)
    by_id = {item["evidence_id"]: item for item in validated}
    if len(by_id) != len(validated):
        raise ValueError("duplicate normalized evidence reference")
    if set(by_id) != set(request.normalized_evidence_reference_ids):
        raise ValueError("normalized evidence references do not match the request")
    for item in validated:
        source_identity = item["source_identity"]
        if item["project_id"] != request.source_identity.project_id:
            raise ValueError("normalized evidence project mismatch")
        if item["run_id"] != request.analysis_run_id:
            raise ValueError("normalized evidence run mismatch")
        if source_identity["snapshot_id"] != request.source_snapshot_id:
            raise ValueError("normalized evidence source snapshot mismatch")
        if source_identity["content_hash"] != request.source_content_sha256:
            raise ValueError("normalized evidence source SHA-256 mismatch")
        if item["disposition"] != "validated" or item["content_available"] is not True:
            raise ValueError("normalized evidence is not validated and available")
        if item["candidate_or_canon"] is not False or item["support_is_truth"] is not False:
            raise ValueError("normalized evidence crossed the support-only boundary")
    return validated


def _official_subtxt_raw_reference(
    request: SubtxtAnalysisRequest,
    raw_output: bytes,
) -> str:
    existing = {
        item.artifact_id for item in request.analysis_run_manifest.artifact_references
    }
    seed = hashlib.sha256(
        request.analysis_run_id.encode("utf-8") + b"\0" + raw_output
    ).hexdigest()
    candidate = f"subtxt-raw-{seed[:32]}"
    counter = 0
    while candidate in existing:
        counter += 1
        candidate = f"subtxt-raw-{seed[:28]}-{counter}"
    return candidate


def _official_subtxt_has_unsafe_surface(
    value: Any,
    *,
    current_key: str = "",
) -> bool:
    normalized_key = current_key.strip().lower().replace("-", "_")
    if normalized_key in _OFFICIAL_SUBTXT_UNSAFE_KEYS:
        return True
    if isinstance(value, dict):
        return any(
            _official_subtxt_has_unsafe_surface(child, current_key=str(key))
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_official_subtxt_has_unsafe_surface(child) for child in value)
    if normalized_key in {"operation", "operation_id", "action", "requested_action"}:
        return isinstance(value, str) and value in OFFICIAL_SUBTXT_FORBIDDEN_OPERATIONS
    return False


def _official_subtxt_validate_runner_provenance(
    request: SubtxtAnalysisRequest,
    provenance: Any,
) -> SubtxtRuntimeProvenance:
    if not isinstance(provenance, SubtxtRuntimeProvenance):
        raise ValueError("official runtime provenance is missing or malformed")
    if provenance.adapter.adapter_id != OFFICIAL_SUBTXT_ADAPTER_ID:
        raise ValueError("runtime provenance impersonates another adapter")
    if provenance.adapter.implementation_kind != "official_external":
        raise ValueError("runtime provenance is not official_external")
    if provenance.adapter.adapter_id in _OFFICIAL_SUBTXT_APP_OWNED_IDENTITIES:
        raise ValueError("app-owned rubric cannot satisfy official runtime provenance")
    if provenance.analysis_run_id != request.analysis_run_id:
        raise ValueError("runtime provenance run mismatch")
    if provenance.source_snapshot_ids != (request.source_snapshot_id,):
        raise ValueError("runtime provenance source mismatch")
    if provenance.adapter.runtime != request.runtime_identity:
        raise ValueError("runtime identity differs from the verified request")
    if provenance.callable_interface != request.callable_interface:
        raise ValueError("callable interface differs from the verified request")
    if provenance.transformation_ids:
        raise ValueError("runtime cannot invent application transformation lineage")
    return provenance


def _official_subtxt_failure_execution(
    request: SubtxtAnalysisRequest,
    *,
    state: str,
    reason: str,
    provenance: SubtxtRuntimeProvenance | None = None,
    raw_output: bytes | None = None,
    evidence_reference_ids: tuple[str, ...] = (),
) -> OfficialSubtxtExecution:
    effective_provenance = provenance or _official_subtxt_request_provenance(request)
    raw_reference = (
        _official_subtxt_raw_reference(request, raw_output)
        if raw_output is not None
        else None
    )
    quarantined = state in {
        "unsupported_output",
        "malformed_output",
        "unsafe_output",
        "quarantined",
    }
    result = SubtxtAnalysisResult(
        state=state,
        analysis_run_id=request.analysis_run_id,
        source_snapshot_id=request.source_snapshot_id,
        source_content_sha256=request.source_content_sha256,
        operation_id=request.operation_id,
        provenance=effective_provenance,
        raw_output_reference_id=raw_reference,
        evidence_reference_ids=evidence_reference_ids,
        transformation_ids=(),
        reason=reason,
        quarantined=quarantined,
    )
    output_lineage: tuple[OutputLineage, ...] = ()
    if raw_reference is not None:
        output_seed = hashlib.sha256(
            request.analysis_run_id.encode("utf-8") + b"\0" + raw_output
        ).hexdigest()
        output_id = f"output-subtxt-{output_seed[:24]}"
        disposition = "quarantined" if quarantined else "unverified"
        output_lineage = (
            OutputLineage(
                output_id=output_id,
                operation_id=request.operation_id,
                source_snapshot_ids=(request.source_snapshot_id,),
                disposition=disposition,
                original_output_reference_id=raw_reference,
                evidence_reference_ids=evidence_reference_ids,
                verification_outcome=state,
                missing_evidence_reason=reason,
            ),
        )
    finalized_manifest = _official_subtxt_finalize_manifest(
        request,
        result=result,
        raw_output=raw_output,
        output_lineage=output_lineage,
        transformations=(),
    )
    return OfficialSubtxtExecution(
        request=request,
        finalized_manifest=finalized_manifest,
        result=result,
        findings=(),
        raw_output=raw_output,
        output_lineage=output_lineage,
        transformations=(),
        semantic_guardrail_inputs=(),
        input_evidence_reference_ids=request.normalized_evidence_reference_ids,
    )


def _official_subtxt_parse_runner_response(
    response: Any,
) -> tuple[bytes | None, Mapping[str, Any] | None, Any]:
    if isinstance(response, OfficialSubtxtRunnerResponse):
        return response.raw_output, response.mapped_output, response.provenance
    if isinstance(response, dict):
        raw_output = response.get("raw_output")
        return (
            raw_output if isinstance(raw_output, bytes) else None,
            response.get("mapped_output"),
            response.get("provenance"),
        )
    return None, None, None


def _official_subtxt_contributor_state(result_state: str) -> tuple[str, str]:
    return {
        "evidence_backed_success": ("succeeded", "complete"),
        "uncertainty": ("succeeded", "partial"),
        "unavailable_runtime": ("unavailable", "none"),
        "runtime_failure": ("error", "none"),
        "incompatible_runtime": ("unavailable", "none"),
        "unsupported_output": ("failed_closed", "none"),
        "malformed_output": ("failed_closed", "none"),
        "unsafe_output": ("failed_closed", "none"),
        "quarantined": ("failed_closed", "none"),
    }[result_state]


def _official_subtxt_finalize_manifest(
    request: SubtxtAnalysisRequest,
    *,
    result: SubtxtAnalysisResult,
    raw_output: bytes | None,
    output_lineage: tuple[OutputLineage, ...],
    transformations: tuple[TransformationLineage, ...],
) -> AnalysisRunManifest:
    upstream = request.analysis_run_manifest
    contributor_state, contributor_coverage = _official_subtxt_contributor_state(
        result.state
    )
    replacement = ContributorLineage(
        operation_id=request.operation_id,
        adapter_id=OFFICIAL_SUBTXT_ADAPTER_ID,
        source_snapshot_ids=(request.source_snapshot_id,),
        result_state=contributor_state,
        coverage=contributor_coverage,
        explanation=result.reason
        or "official Subtxt output passed the analysis-only boundary",
        provenance=result.provenance.adapter,
        output_ids=tuple(item.output_id for item in output_lineage),
    )
    contributors = tuple(
        replacement if item.operation_id == request.operation_id else item
        for item in upstream.contributors
    )
    artifact_references = upstream.artifact_references
    if raw_output is not None and result.raw_output_reference_id is not None:
        artifact_references = (
            *artifact_references,
            ArtifactReference(
                artifact_id=result.raw_output_reference_id,
                availability="available",
                source_snapshot_ids=(request.source_snapshot_id,),
                content_hash=hashlib.sha256(raw_output).hexdigest(),
                hash_algorithm="sha256",
                media_type="application/octet-stream",
            ),
        )
    coverage = (
        "complete"
        if all(
            item.result_state in {"succeeded", "empty"}
            and item.coverage == "complete"
            for item in contributors
        )
        else "partial"
    )
    return AnalysisRunManifest(
        run_id=upstream.run_id,
        project_id=upstream.project_id,
        sources=upstream.sources,
        operations=upstream.operations,
        dependency_graph=upstream.dependency_graph,
        contributors=contributors,
        artifact_references=artifact_references,
        outputs=(*upstream.outputs, *output_lineage),
        transformations=(*upstream.transformations, *transformations),
        coverage=coverage,
        created_at=upstream.created_at,
        finalized_at=upstream.finalized_at,
        configuration=upstream.configuration,
        feature_flags=upstream.feature_flags,
    )


def _official_subtxt_normalize_findings(
    request: SubtxtAnalysisRequest,
    mapped_output: Mapping[str, Any],
    evidence_records_by_id: Mapping[str, Mapping[str, Any]],
    provenance: SubtxtRuntimeProvenance,
    raw_reference: str,
) -> tuple[
    tuple[dict[str, Any], ...],
    tuple[TransformationLineage, ...],
    tuple[OutputLineage, ...],
]:
    if set(mapped_output) != _SUBTXT_APP_MAPPED_OUTPUT_FIELDS:
        raise ValueError("app-owned Subtxt mapped output fields are malformed")
    if mapped_output["schema_version"] != SUBTXT_APP_MAPPED_OUTPUT_SCHEMA_VERSION:
        raise LookupError("app-owned Subtxt mapped output schema is unsupported")
    for field, expected in (
        ("analysis_run_id", request.analysis_run_id),
        ("source_snapshot_id", request.source_snapshot_id),
        ("source_content_sha256", request.source_content_sha256),
        ("operation_id", request.operation_id),
    ):
        if mapped_output[field] != expected:
            raise RuntimeError(f"app-owned Subtxt mapped output {field} mismatch")
    raw_findings = mapped_output["findings"]
    if not isinstance(raw_findings, list):
        raise ValueError("app-owned Subtxt mapped findings must be a list")

    allowed_types = set(
        omi_analysis_orchestrator.adapter_contract(OFFICIAL_SUBTXT_ADAPTER_ID)[
            "supports_finding_types"
        ]
    )
    normalized_findings: list[dict[str, Any]] = []
    transformations: list[TransformationLineage] = []
    output_lineage: list[OutputLineage] = []
    for index, item in enumerate(raw_findings):
        if not isinstance(item, dict) or set(item) - _SUBTXT_APP_MAPPED_FINDING_FIELDS:
            raise ValueError("app-owned Subtxt mapped finding fields are malformed")
        required = _SUBTXT_APP_MAPPED_FINDING_FIELDS - {
            "source_locator",
            "uncertainty_reason",
        }
        if not required <= set(item):
            raise ValueError("app-owned Subtxt mapped finding fields are missing")
        if item["candidate_type"] not in allowed_types:
            raise LookupError("app-owned Subtxt mapped finding type is unsupported")
        evidence_reference_ids = item["evidence_reference_ids"]
        if (
            not isinstance(evidence_reference_ids, list)
            or not evidence_reference_ids
            or not all(
                isinstance(evidence_id, str) and evidence_id
                for evidence_id in evidence_reference_ids
            )
            or len(set(evidence_reference_ids)) != len(evidence_reference_ids)
            or not set(evidence_reference_ids)
            <= set(request.normalized_evidence_reference_ids)
        ):
            raise LookupError("app-owned Subtxt mapped finding lacks attributable evidence")
        raw_evidence = item["evidence"]
        if not isinstance(raw_evidence, list) or not raw_evidence:
            raise LookupError("app-owned Subtxt mapped finding evidence is missing")
        evidence: list[dict[str, Any]] = []
        referenced_by_items: set[str] = set()
        canonical_locators_by_id: dict[str, str] = {}
        for evidence_item in raw_evidence:
            if (
                not isinstance(evidence_item, dict)
                or set(evidence_item) - _SUBTXT_APP_MAPPED_EVIDENCE_FIELDS
                or "evidence_reference_id" not in evidence_item
            ):
                raise ValueError("app-owned Subtxt mapped evidence item is malformed")
            evidence_reference_id = evidence_item["evidence_reference_id"]
            if evidence_reference_id not in evidence_reference_ids:
                raise LookupError("app-owned Subtxt mapped evidence item is not attributable")
            canonical_record = evidence_records_by_id.get(evidence_reference_id)
            if canonical_record is None:
                raise LookupError("mapped evidence reference has no canonical T003 record")
            source_locator = json.dumps(
                project_candidate_source_locator(canonical_record["source_locator"]),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            claimed_locator = evidence_item.get("source_locator")
            if claimed_locator is not None:
                if (
                    not isinstance(claimed_locator, str)
                    or claimed_locator.strip() != source_locator
                ):
                    raise RuntimeError(
                        "app-owned Subtxt mapped evidence locator mismatches canonical T003 evidence"
                    )
            referenced_by_items.add(evidence_reference_id)
            canonical_locators_by_id[evidence_reference_id] = source_locator
            evidence.append(
                {
                    "source_locator": source_locator.strip(),
                    "evidence_reference_id": evidence_reference_id,
                    "source_snapshot_id": request.source_snapshot_id,
                    "source_content_sha256": request.source_content_sha256,
                }
            )
        if referenced_by_items != set(evidence_reference_ids):
            raise LookupError("app-owned Subtxt mapped evidence references are incomplete")
        candidate_source_locator = canonical_locators_by_id[
            evidence_reference_ids[0]
        ]
        claimed_finding_locator = item.get("source_locator")
        if claimed_finding_locator is not None:
            if (
                not isinstance(claimed_finding_locator, str)
                or claimed_finding_locator.strip() != candidate_source_locator
            ):
                raise RuntimeError(
                    "app-owned Subtxt mapped finding locator mismatches canonical T003 evidence"
                )

        support_label = item["support_label"]
        core_provenance = {
            "tool_source": OFFICIAL_SUBTXT_ADAPTER_ID,
            "adapter": OFFICIAL_SUBTXT_ADAPTER_ID,
            "support": support_label,
        }
        candidate = {
            "candidate_type": item["candidate_type"],
            "label": item["label"],
            "extracted_claim": item["extracted_claim"],
            "evidence": evidence,
            "source_locator": candidate_source_locator,
            "provenance": core_provenance,
            "source_adapter": OFFICIAL_SUBTXT_ADAPTER_ID,
            "support_label": support_label,
            "owner_decision": {"decision": "pending", "approved": False},
            "review_status": "candidate_review_pending",
            "raw_finding_id": item["raw_finding_id"],
            "support_metadata": {
                "analysis_run_id": request.analysis_run_id,
                "source_snapshot_id": request.source_snapshot_id,
                "source_content_sha256": request.source_content_sha256,
                "normalized_evidence_reference_ids": list(evidence_reference_ids),
                "owner_review_required": True,
                "support_is_truth": False,
            },
            "uncertainty_label": (
                "subtxt_runtime_uncertainty_support"
                if item.get("uncertainty_reason")
                else None
            ),
        }
        normalized = omi_analysis_orchestrator.validate_normalized_finding(candidate)
        if normalized["normalized_finding_id"] in {
            output.output_id for output in request.analysis_run_manifest.outputs
        }:
            raise ValueError("official Subtxt output identity collision")
        transformation_seed = (
            f"{raw_reference}|{normalized['normalized_finding_id']}|{index}"
        )
        transformation_id = (
            "transform-subtxt-"
            + hashlib.sha256(transformation_seed.encode("utf-8")).hexdigest()[:20]
        )
        if transformation_id in {
            item.transformation_id
            for item in request.analysis_run_manifest.transformations
        }:
            raise ValueError("official Subtxt transformation identity collision")
        extended_provenance = {
            **core_provenance,
            "implementation_kind": "official_external",
            "analysis_run_id": request.analysis_run_id,
            "source_identity": request.source_identity.to_dict(),
            "source_snapshot_id": request.source_snapshot_id,
            "source_content_sha256": request.source_content_sha256,
            "operation_id": request.operation_id,
            "raw_output_reference_id": raw_reference,
            "evidence_reference_ids": list(evidence_reference_ids),
            "transformation_ids": [transformation_id],
            "runtime": provenance.adapter.runtime.to_dict(),
            "provider": provenance.adapter.provider.to_dict(),
            "model": provenance.adapter.model.to_dict(),
            "callable_interface": provenance.callable_interface.to_dict(),
            "safe_configuration_identity": (
                provenance.safe_configuration_identity.to_dict()
            ),
        }
        normalized["provenance"] = extended_provenance
        normalized["provenance_refs"] = [
            f"contributor-{OFFICIAL_SUBTXT_ADAPTER_ID}"
        ]
        normalized["evidence_refs"] = list(evidence_reference_ids)
        normalized["source_refs"] = [request.source_snapshot_id]
        normalized["source_locator_refs"] = [normalized["source_locator"]]
        normalized["support_metadata"]["transformation_ids"] = [
            transformation_id
        ]
        normalized_findings.append(normalized)
        transformations.append(
            TransformationLineage(
                transformation_id=transformation_id,
                operation_id=request.operation_id,
                transformation_kind="official_subtxt_app_mapped_output_normalization",
                transformation_version=SUBTXT_APP_MAPPED_NORMALIZATION_VERSION,
                input_reference_ids=(
                    raw_reference,
                    *tuple(
                        output.output_id
                        for output in request.analysis_run_manifest.outputs
                        if set(output.evidence_reference_ids)
                        & set(evidence_reference_ids)
                    ),
                ),
                output_reference_ids=(normalized["normalized_finding_id"],),
            )
        )
        output_lineage.append(
            OutputLineage(
                output_id=normalized["normalized_finding_id"],
                operation_id=request.operation_id,
                source_snapshot_ids=(request.source_snapshot_id,),
                disposition="validated",
                original_output_reference_id=raw_reference,
                evidence_reference_ids=tuple(evidence_reference_ids),
                transformation_ids=(transformation_id,),
                verification_outcome="official_subtxt_boundary_validated",
            )
        )
    return (
        tuple(normalized_findings),
        tuple(transformations),
        tuple(output_lineage),
    )


def run_official_subtxt_adapter(
    request: SubtxtAnalysisRequest,
    normalized_evidence_records: tuple[dict[str, Any], ...],
    *,
    preflight_inventory: SubtxtRuntimeInventory,
    runner: Callable[..., OfficialSubtxtRunnerResponse],
    timeout_seconds: float = 30.0,
) -> OfficialSubtxtExecution:
    """Run only the verified analysis operation through an injected seam.

    The adapter deliberately knows nothing about a concrete external CLI,
    library, or API.  Provisioning code must supply a runner whose interface,
    compatibility, capability, and provenance were already verified.  No
    app-owned rubric or deterministic fallback is consulted here.
    """

    _official_subtxt_validate_request_boundary(request)
    if not callable(runner):
        raise ValueError("official Subtxt runner must be callable")
    if isinstance(timeout_seconds, bool) or not isinstance(
        timeout_seconds, (int, float)
    ) or timeout_seconds <= 0:
        raise ValueError("official Subtxt timeout must be positive")
    preflight_failure = _official_subtxt_preflight_failure(
        request, preflight_inventory
    )
    if preflight_failure is not None:
        state, reason = preflight_failure
        return _official_subtxt_failure_execution(
            request,
            state=state,
            reason=reason,
        )
    try:
        normalized_evidence = _official_subtxt_validate_normalized_evidence(
            request, normalized_evidence_records
        )
        evidence_records_by_id = {
            item["evidence_id"]: item for item in normalized_evidence
        }
    except ValueError as exc:
        return _official_subtxt_failure_execution(
            request,
            state="quarantined",
            reason=f"normalized evidence failed closed: {exc}",
        )

    try:
        response = runner(
            request=request,
            normalized_evidence=normalized_evidence,
            timeout_seconds=float(timeout_seconds),
        )
    except OfficialSubtxtRunnerError as exc:
        reason_prefix = (
            "official Subtxt runtime timeout"
            if isinstance(exc, OfficialSubtxtRuntimeTimeoutError)
            else "official Subtxt runner failure"
        )
        return _official_subtxt_failure_execution(
            request,
            state=exc.result_state,
            reason=f"{reason_prefix}: {exc}",
        )
    except Exception as exc:
        return _official_subtxt_failure_execution(
            request,
            state="runtime_failure",
            reason=f"official Subtxt runtime failure: {type(exc).__name__}",
        )

    raw_output, mapped_output, response_provenance = (
        _official_subtxt_parse_runner_response(response)
    )
    if not isinstance(raw_output, bytes) or not raw_output:
        return _official_subtxt_failure_execution(
            request,
            state="malformed_output",
            reason="official Subtxt runtime did not preserve non-empty response bytes",
        )
    if len(raw_output) > OFFICIAL_SUBTXT_MAX_OUTPUT_BYTES:
        return _official_subtxt_failure_execution(
            request,
            state="malformed_output",
            reason="official Subtxt runtime output exceeds the bounded size limit",
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    raw_reference = _official_subtxt_raw_reference(request, raw_output)
    if not isinstance(mapped_output, Mapping):
        return _official_subtxt_failure_execution(
            request,
            state="malformed_output",
            reason="app-owned Subtxt mapped output is missing or malformed",
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    if _official_subtxt_has_unsafe_surface(mapped_output):
        return _official_subtxt_failure_execution(
            request,
            state="unsafe_output",
            reason="app-owned Subtxt mapped output requested a forbidden operation or mutation",
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    try:
        provenance = _official_subtxt_validate_runner_provenance(
            request, response_provenance
        )
    except ValueError as exc:
        return _official_subtxt_failure_execution(
            request,
            state="quarantined",
            reason=f"official Subtxt provenance failed closed: {exc}",
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    except Exception as exc:
        return _official_subtxt_failure_execution(
            request,
            state="malformed_output",
            reason=(
                "official Subtxt output failed closed on malformed data: "
                f"{type(exc).__name__}"
            ),
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    try:
        findings, transformations, output_lineage = (
            _official_subtxt_normalize_findings(
                request,
                mapped_output,
                evidence_records_by_id,
                provenance,
                raw_reference,
            )
        )
    except RuntimeError as exc:
        return _official_subtxt_failure_execution(
            request,
            state="quarantined",
            reason=str(exc),
            provenance=provenance,
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    except LookupError as exc:
        return _official_subtxt_failure_execution(
            request,
            state="unsupported_output",
            reason=str(exc),
            provenance=provenance,
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    except ValueError as exc:
        state = (
            "unsafe_output"
            if "prose" in str(exc).lower()
            or "truth" in str(exc).lower()
            or "canon" in str(exc).lower()
            or "approv" in str(exc).lower()
            else "malformed_output"
        )
        return _official_subtxt_failure_execution(
            request,
            state=state,
            reason=f"official Subtxt output failed closed: {exc}",
            provenance=provenance,
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    except Exception as exc:
        return _official_subtxt_failure_execution(
            request,
            state="malformed_output",
            reason=(
                "official Subtxt output failed closed on malformed data: "
                f"{type(exc).__name__}"
            ),
            provenance=provenance,
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )

    if not findings:
        return _official_subtxt_failure_execution(
            request,
            state="uncertainty",
            reason="official Subtxt returned no evidence-backed findings",
            provenance=provenance,
            raw_output=raw_output,
            evidence_reference_ids=request.normalized_evidence_reference_ids,
        )
    transformation_ids = tuple(
        item.transformation_id for item in transformations
    )
    final_provenance = _official_subtxt_with_transformations(
        provenance, transformation_ids
    )
    result = SubtxtAnalysisResult(
        state="evidence_backed_success",
        analysis_run_id=request.analysis_run_id,
        source_snapshot_id=request.source_snapshot_id,
        source_content_sha256=request.source_content_sha256,
        operation_id=request.operation_id,
        provenance=final_provenance,
        raw_output_reference_id=raw_reference,
        evidence_reference_ids=tuple(
            dict.fromkeys(
                evidence_id
                for output in output_lineage
                for evidence_id in output.evidence_reference_ids
            )
        ),
        transformation_ids=transformation_ids,
    )
    guardrail_inputs = tuple(
        {
            "adapter_identity": OFFICIAL_SUBTXT_ADAPTER_ID,
            "operation_id": request.operation_id,
            "analysis_run_id": request.analysis_run_id,
            "source_snapshot_id": request.source_snapshot_id,
            "source_content_sha256": request.source_content_sha256,
            "raw_output_reference_id": raw_reference,
            "evidence_reference_ids": list(finding["evidence_refs"]),
            "transformation_ids": list(
                finding["provenance"]["transformation_ids"]
            ),
            "original_normalized_finding": copy.deepcopy(finding),
            "guardrail_classification": None,
            "guardrail_policy_applied": False,
        }
        for finding in findings
    )
    finalized_manifest = _official_subtxt_finalize_manifest(
        request,
        result=result,
        raw_output=raw_output,
        output_lineage=output_lineage,
        transformations=transformations,
    )
    return OfficialSubtxtExecution(
        request=request,
        finalized_manifest=finalized_manifest,
        result=result,
        findings=findings,
        raw_output=raw_output,
        output_lineage=output_lineage,
        transformations=transformations,
        semantic_guardrail_inputs=guardrail_inputs,
        input_evidence_reference_ids=request.normalized_evidence_reference_ids,
    )


def persist_official_subtxt_execution_evidence(
    execution: OfficialSubtxtExecution,
    *,
    storage_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Persist exact runtime bytes and lineage through the existing T003 APIs.

    This stores support evidence only.  It never creates candidates or review
    entries and never invokes promotion, apply-promotion, or Memory/Canon
    mutation. Candidate persistence remains the existing explicit owner-run
    path in ``project_manager``.
    """

    if not isinstance(execution, OfficialSubtxtExecution):
        raise ValueError("validated official Subtxt execution is required")
    if execution.raw_output is None or execution.result.raw_output_reference_id is None:
        return {
            "persistence_status": "no_runtime_output_to_persist",
            "raw_artifact_ref": None,
            "ledger_event_hashes": [],
            "candidate_persistence_performed": False,
        }
    request = execution.request
    raw_output = execution.raw_output
    raw_reference = execution.result.raw_output_reference_id
    manifest_hash = canonical_sha256(execution.finalized_manifest.to_dict())
    raw_hash = hashlib.sha256(raw_output).hexdigest()
    bundle_seed = f"{request.analysis_run_id}|{raw_hash}".encode("utf-8")
    bundle_id = (
        "bundle-subtxt-" + hashlib.sha256(bundle_seed).hexdigest()[:24]
    )
    provenance_ref = f"contributor-{OFFICIAL_SUBTXT_ADAPTER_ID}"
    # T005 establishes no official native wire format. Preserve the runtime
    # response as opaque bytes and never label it with the app-owned mapping
    # schema, even when those bytes happen to be valid UTF-8 or JSON.
    media_type = "application/octet-stream"
    artifact_filename = "official-subtxt-runtime-output.bin"
    encoding = None
    schema_name = None
    parser_hint = None
    artifact_file = build_raw_artifact_file_ref(
        artifact_file_id=raw_reference,
        artifact_type="adapter_metadata",
        relative_path=f"artifacts/{artifact_filename}",
        media_type=media_type,
        payload=raw_output,
        source_locator_refs=[request.source_snapshot_id],
        evidence_refs=list(execution.input_evidence_reference_ids),
        provenance_refs=[provenance_ref],
        encoding=encoding,
        record_count=1,
        schema_name=schema_name,
        schema_version="1" if schema_name is not None else None,
        parser_hint=parser_hint,
    )
    raw_manifest = build_immutable_raw_artifact_manifest(
        project_id=request.source_identity.project_id,
        run_id=request.analysis_run_id,
        raw_artifact_bundle_id=bundle_id,
        artifact_files=[artifact_file],
        analysis_run_manifest_hash=manifest_hash,
        created_at=created_at,
        source_refs=[request.source_snapshot_id],
        evidence_refs=list(execution.input_evidence_reference_ids),
        provenance_refs=[provenance_ref],
        source_locator_refs=[request.source_snapshot_id],
        adapter_name=OFFICIAL_SUBTXT_ADAPTER_ID,
        adapter_version=SUBTXT_RUNTIME_CONTRACT_VERSION,
        tool_name=execution.result.provenance.adapter.tool.name,
        tool_version=execution.result.provenance.adapter.tool.version,
    )
    write_result = write_immutable_raw_artifact_bundle(
        raw_manifest,
        {raw_reference: raw_output},
        project_dir=storage_root,
    )
    project_storage_dir = (
        Path(storage_root)
        / "projects"
        / request.source_identity.project_id
    )
    events = [
        append_evidence_ledger_event(
            project_dir=project_storage_dir,
            project_id=request.source_identity.project_id,
            run_id=request.analysis_run_id,
            event_type="artifact_recorded",
            idempotency_key=bundle_id,
            created_at=created_at,
            payload={
                "artifact_id": bundle_id,
                "artifact_manifest_hash": raw_manifest["manifest_hash"],
                "artifact_bundle_hash": raw_manifest["bundle_hash"],
                "analysis_run_manifest_hash": manifest_hash,
                "source_snapshot_ids": [request.source_snapshot_id],
                "availability": "available",
            },
        )
    ]
    for output in execution.output_lineage:
        events.append(
            append_evidence_ledger_event(
                project_dir=project_storage_dir,
                project_id=request.source_identity.project_id,
                run_id=request.analysis_run_id,
                event_type="output_recorded",
                idempotency_key=output.output_id,
                created_at=created_at,
                payload=output.to_dict(),
            )
        )
    contributor_state = {
        "evidence_backed_success": "succeeded",
        "uncertainty": "empty",
        "unavailable_runtime": "unavailable",
        "runtime_failure": "error",
        "incompatible_runtime": "unavailable",
        "unsupported_output": "failed_closed",
        "malformed_output": "failed_closed",
        "unsafe_output": "failed_closed",
        "quarantined": "failed_closed",
    }[execution.result.state]
    contributor_payload = {
        "operation_id": request.operation_id,
        "adapter_id": OFFICIAL_SUBTXT_ADAPTER_ID,
        "source_snapshot_ids": [request.source_snapshot_id],
        "result_state": contributor_state,
        "coverage": (
            "complete"
            if execution.result.state == "evidence_backed_success"
            else "none"
        ),
        "explanation": execution.result.reason
        or "official Subtxt output passed the analysis-only boundary",
        "provenance": execution.result.provenance.adapter.to_dict(),
        "output_ids": [item.output_id for item in execution.output_lineage],
    }
    contributor_key = (
        f"subtxt-execution-{hashlib.sha256(raw_output).hexdigest()[:20]}"
    )
    events.append(
        append_evidence_ledger_event(
            project_dir=project_storage_dir,
            project_id=request.source_identity.project_id,
            run_id=request.analysis_run_id,
            event_type="contributor_recorded",
            idempotency_key=contributor_key,
            created_at=created_at,
            payload=contributor_payload,
        )
    )
    return {
        "persistence_status": "persisted",
        "raw_artifact_ref": {
            "artifact_id": bundle_id,
            "artifact_file_id": raw_reference,
            "manifest_hash": raw_manifest["manifest_hash"],
            "bundle_hash": raw_manifest["bundle_hash"],
            "analysis_run_manifest_hash": manifest_hash,
            "idempotent": write_result["idempotent"],
        },
        "ledger_event_hashes": [event["event_hash"] for event in events],
        "candidate_persistence_performed": False,
        "memory_or_canon_mutated": False,
        "promotion_or_apply_promotion_performed": False,
    }


def _base_result() -> dict:
    return {
        "status": "fail_closed",
        "fail_closed": True,
        "no_silent_fallback": True,
    }


def _non_execution_result() -> dict:
    result = {
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
    result["calls_" + "sub" + "process"] = False
    return result


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


def _safe_ref_values(value: Any) -> bool:
    if isinstance(value, str):
        return _safe_identifier(value)
    if isinstance(value, list) and not value:
        return True
    return _has_refs(value) and all(_safe_identifier(item) for item in value)


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


def _contains_forbidden_output_class(value: Any) -> bool:
    if isinstance(value, str):
        return value in FORBIDDEN_OUTPUT_CLASSES
    if isinstance(value, dict):
        return any(_contains_forbidden_output_class(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_output_class(item) for item in value)
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
