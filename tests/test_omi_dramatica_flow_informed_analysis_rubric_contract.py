"""Focused T020C tests for the app-owned analysis-rubric contract."""

from __future__ import annotations

import copy
import inspect

import pytest

from backend.story_knowledge import dramatica_flow_informed_analysis_rubric_contract as contract
from backend.story_knowledge.analysis_runtime_integration import (
    validate_analysis_runtime_output,
)
from backend.story_knowledge import subtxt_informed_semantic_rubric_contract as t019c


def _provenance():
    return {
        "tool_source": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "adapter": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "support": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
    }


def _request():
    return {
        "schema_version": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION,
        "rubric_id": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "request_id": "request_1",
        "project_name": "owner_project",
        "source_text": "Mara chooses the river route because the bridge is closed.",
        "source_locator": "source_locator_ref_1",
        "source_refs": ["source_ref_1"],
        "evidence_refs": ["evidence_ref_1"],
        "provenance_refs": ["provenance_ref_1"],
        "source_locator_refs": ["source_locator_ref_1"],
        "requested_categories": list(contract.ALLOWED_CATEGORIES),
        "analysis_intent": "diagnostic_support",
        "owner_authored_or_owner_provided_source": True,
        "safety_confirmations": {
            key: True for key in contract.ALLOWED_REQUEST_SAFETY_CONFIRMATIONS
        },
    }


def _item(category="causal_chain_diagnostic", item_id="item_1"):
    question = category in contract.QUESTION_CATEGORIES
    uncertainty = {
        "ambiguity": "ambiguity",
        "insufficient_evidence": "insufficient_evidence",
    }.get(category, "requires_owner_interpretation" if question else "null")
    return {
        "item_id": item_id,
        "category": category,
        "candidate_type": contract.CATEGORY_TO_CANDIDATE_TYPE[category],
        "label": "Evidence-linked diagnostic",
        "diagnostic_text": (
            "What evidence needs the owner's interpretation?"
            if question
            else "The supplied evidence supports a bounded diagnostic observation."
        ),
        "statement_kind": contract.CATEGORY_TO_STATEMENT_KIND[category],
        "evidence": [
            {
                "source_excerpt": "Mara chooses the river route.",
                "source_locator": "source_locator_ref_1",
            }
        ],
        "source_locator": "source_locator_ref_1",
        "source_refs": ["source_ref_1"],
        "evidence_refs": ["evidence_ref_1"],
        "provenance_refs": ["provenance_ref_1"],
        "source_locator_refs": ["source_locator_ref_1"],
        "provenance": _provenance(),
        "support_label": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "confidence": "low_support" if question else "medium_support",
        "uncertainty_label": uncertainty,
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
        "calls_model_provider_server": False,
        "reads_external_source_runtime": False,
        "uses_external_project_state": False,
    }


def _result(category="causal_chain_diagnostic"):
    result = {
        "schema_version": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "output_class": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "succeeded",
        "display_label": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": _provenance(),
        "source_refs": ["source_ref_1"],
        "evidence_refs": ["evidence_ref_1"],
        "provenance_refs": ["provenance_ref_1"],
        "source_locator_refs": ["source_locator_ref_1"],
        "candidate_support": [],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": {flag: False for flag in contract.OPERATION_FLAGS},
    }
    bucket = (
        "diagnostic_questions" if category in contract.QUESTION_CATEGORIES
        else "uncertainty_notes" if category == "ambiguity"
        else "insufficient_evidence_notes" if category == "insufficient_evidence"
        else "candidate_support"
    )
    result[bucket] = [_item(category)]
    return result


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION", "omi_app_owned_dramatica_flow_informed_rubric_request.v1"),
        ("DRAMATICA_FLOW_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION", "omi_app_owned_dramatica_flow_informed_rubric_result.v1"),
        ("DRAMATICA_FLOW_INFORMED_RUBRIC_ID", "app_owned_dramatica_flow_informed_rubric"),
        ("DRAMATICA_FLOW_INFORMED_RUBRIC_OUTPUT_CLASS", "rubric_mapping_support"),
        ("DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL", "App-owned dramatica-flow-informed diagnostic support"),
    ],
)
def test_public_identity_constants(name, expected):
    assert getattr(contract, name) == expected


@pytest.mark.parametrize(
    "name",
    [
        "validate_dramatica_flow_informed_rubric_request",
        "validate_dramatica_flow_informed_rubric_result",
        "build_dramatica_flow_informed_rubric_fail_closed_result",
    ],
)
def test_public_apis_are_callable(name):
    assert callable(getattr(contract, name))


@pytest.mark.parametrize("category", sorted(contract.ALLOWED_CATEGORIES))
def test_categories_have_complete_mappings(category):
    assert contract.CATEGORY_TO_CANDIDATE_TYPE[category] in contract.ALLOWED_CANDIDATE_TYPES
    assert contract.CATEGORY_TO_STATEMENT_KIND[category] in contract.ALLOWED_STATEMENT_KINDS


def test_category_partitions_are_exact_and_disjoint():
    assert contract.QUESTION_CATEGORIES.isdisjoint(contract.NON_QUESTION_CATEGORIES)
    assert contract.QUESTION_CATEGORIES | contract.NON_QUESTION_CATEGORIES == contract.ALLOWED_CATEGORIES


@pytest.mark.parametrize(
    "forbidden",
    ["OS", "MC", "IC", "RS", "domain", "concern", "issue", "problem", "solution", "approach", "dynamic", "signpost"],
)
def test_no_storyform_structural_category_or_mapping(forbidden):
    values = set(contract.ALLOWED_CATEGORIES) | set(contract.ALLOWED_CANDIDATE_TYPES)
    assert forbidden.lower() not in {value.lower() for value in values}


def test_high_support_is_not_allowed():
    assert "high_support" not in contract.ALLOWED_CONFIDENCE_VALUES


def test_valid_request_normalizes_without_mutating_caller():
    request = _request()
    original = copy.deepcopy(request)
    validation = contract.validate_dramatica_flow_informed_rubric_request(request)
    assert validation["valid"] is True
    assert validation["normalized_request"] == original
    validation["normalized_request"]["source_refs"].append("changed")
    assert request == original


@pytest.mark.parametrize("field", sorted(contract.REQUEST_REQUIRED_FIELDS))
def test_request_rejects_each_missing_required_field(field):
    request = _request()
    request.pop(field)
    assert contract.validate_dramatica_flow_informed_rubric_request(request)["fail_closed"] is True


def test_request_rejects_unexpected_field():
    request = _request()
    request["extra"] = False
    assert contract.validate_dramatica_flow_informed_rubric_request(request)["valid"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "omi_dramatica_flow_analysis_handoff.v1"),
        ("rubric_id", "dramatica_flow"),
        ("rubric_id", "dramatica-flow"),
        ("request_id", "bad id"),
        ("project_name", "bad/project"),
        ("source_text", ""),
        ("source_locator", "bad locator"),
        ("analysis_intent", "generation"),
        ("owner_authored_or_owner_provided_source", False),
        ("requested_categories", []),
        ("requested_categories", ["ambiguity", "ambiguity"]),
        ("requested_categories", ["storyform"]),
        ("source_refs", []),
        ("evidence_refs", ["bad ref"]),
        ("provenance_refs", ["dup", "dup"]),
        ("source_locator_refs", ["locator_1"]),
    ],
)
def test_request_rejects_malformed_values(field, value):
    request = _request()
    request[field] = value
    assert contract.validate_dramatica_flow_informed_rubric_request(request)["valid"] is False


@pytest.mark.parametrize("key", sorted(contract.ALLOWED_REQUEST_SAFETY_CONFIRMATIONS))
def test_request_requires_every_safety_confirmation_true(key):
    request = _request()
    request["safety_confirmations"][key] = False
    assert contract.validate_dramatica_flow_informed_rubric_request(request)["fail_closed"] is True


def test_request_rejects_extra_safety_confirmation():
    request = _request()
    request["safety_confirmations"]["extra"] = True
    assert contract.validate_dramatica_flow_informed_rubric_request(request)["valid"] is False


def test_owner_source_text_is_exempt_from_unsafe_output_scan():
    request = _request()
    request["source_text"] = "The owner wrote: final canon chapter rewrite and Storyform OS."
    assert contract.validate_dramatica_flow_informed_rubric_request(request)["valid"] is True


@pytest.mark.parametrize("category", sorted(contract.ALLOWED_CATEGORIES))
def test_each_category_validates_in_its_exact_bucket(category):
    assert contract.validate_dramatica_flow_informed_rubric_result(_result(category))["valid"] is True


def test_valid_result_is_deep_copied_and_caller_is_not_mutated():
    result = _result()
    original = copy.deepcopy(result)
    validation = contract.validate_dramatica_flow_informed_rubric_result(result)
    validation["normalized_result"]["source_refs"].append("changed")
    assert result == original


@pytest.mark.parametrize("status", ["empty", "failed_closed", "error"])
def test_non_success_statuses_require_empty_buckets(status):
    result = _result()
    result["status"] = status
    if status in {"failed_closed", "error"}:
        result["fail_closed_reason"] = "invalid input"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize("status", ["empty", "failed_closed", "error"])
def test_empty_non_success_envelopes_validate(status):
    result = _result()
    result["status"] = status
    result["candidate_support"] = []
    if status in {"failed_closed", "error"}:
        result["fail_closed_reason"] = "invalid input"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is True


def test_succeeded_requires_a_finding():
    result = _result()
    result["candidate_support"] = []
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize("field", sorted(contract.RESULT_REQUIRED_FIELDS))
def test_result_rejects_each_missing_required_field(field):
    result = _result()
    result.pop(field)
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["fail_closed"] is True


@pytest.mark.parametrize("field", sorted(contract.ITEM_REQUIRED_FIELDS))
def test_item_rejects_each_missing_required_field(field):
    result = _result()
    result["candidate_support"][0].pop(field)
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


def test_result_and_item_reject_unexpected_fields():
    result = _result()
    result["extra"] = "x"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False
    result = _result()
    result["candidate_support"][0]["extra"] = "x"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize("flag", contract.OPERATION_FLAGS)
def test_every_top_level_operation_flag_is_hard_false(flag):
    result = _result()
    result["safety"][flag] = True
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["fail_closed"] is True


@pytest.mark.parametrize("flag", contract.ITEM_OPERATION_FLAGS)
def test_every_item_operation_flag_is_hard_false(flag):
    result = _result()
    result["candidate_support"][0][flag] = True
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["fail_closed"] is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("rubric_id", "dramatica_flow"),
        ("rubric_id", "dramatica-flow"),
        ("schema_version", "omi_dramatica_flow_analysis_handoff.v1"),
        ("display_label", "dramatica-flow analysis support only"),
        ("output_class", "official_output"),
        ("status", "approved"),
    ],
)
def test_result_rejects_identity_substitution(field, value):
    result = _result()
    result[field] = value
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize("provenance_field", ["tool_source", "adapter", "support", "executes_dramatica_flow", "official_dramatica_flow_output"])
def test_item_and_top_level_provenance_are_exact(provenance_field):
    result = _result()
    replacement = True if provenance_field.startswith(("executes", "official")) else "dramatica_flow"
    result["provenance"][provenance_field] = replacement
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False
    result = _result()
    result["candidate_support"][0]["provenance"][provenance_field] = replacement
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize("confidence", ["high_support", "truth", "certain", ""])
def test_result_rejects_forbidden_or_unknown_confidence(confidence):
    result = _result()
    result["candidate_support"][0]["confidence"] = confidence
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize(
    ("category", "uncertainty"),
    [("ambiguity", "null"), ("insufficient_evidence", "null"), ("owner_review_question", "ambiguity"), ("causal_chain_diagnostic", "insufficient_evidence")],
)
def test_uncertainty_must_match_category(category, uncertainty):
    result = _result(category)
    bucket = next(name for name in ("candidate_support", "diagnostic_questions", "uncertainty_notes", "insufficient_evidence_notes") if result[name])
    result[bucket][0]["uncertainty_label"] = uncertainty
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("owner_decision", {"approved": True, "decision": "pending"}),
        ("owner_decision", {"approved": False, "decision": "approve"}),
        ("review_status", "approved"),
    ],
)
def test_owner_decision_and_review_status_remain_pending(field, value):
    result = _result()
    result["candidate_support"][0][field] = value
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


def test_evidence_has_exact_fields_matching_locator():
    result = _result()
    result["candidate_support"][0]["evidence"][0]["extra"] = "x"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False
    result = _result()
    result["candidate_support"][0]["evidence"][0]["source_locator"] = "source_locator_ref_2"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


def test_evidence_excerpt_may_quote_owner_unsafe_words():
    result = _result()
    result["candidate_support"][0]["evidence"][0]["source_excerpt"] = "final canon chapter rewrite Storyform OS official output"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is True


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "This is final truth", "Canon confirmed", "Approved output", "Promote it",
        "Storyform OS classification", "MC domain", "IC concern", "RS issue",
        "The problem and solution", "Use this approach dynamic", "Official dramatica-flow output",
        "Live dramatica flow execution", "Dramatica-flow confirmed this", "Writer Agent output",
        "Architect Agent result", "Auditor Agent finding", "Reviser Agent suggestion",
        "Generate prose", "Writing instruction", "Rewrite the scene", "Continue the story",
        "Create an outline", "Draft a chapter", "Polish the passage", "Improve the ending",
        "Expand the paragraph", "Revision requested", "Imitate the style", "Export the story",
        "Call the model", "Use a provider", "Call the API", "Start the server",
        "Use external project authority", "Read a snapshot", "Persist candidates",
        "Create review queue", "Mutate Memory Canon", "Apply promotion", "Training artifact",
    ],
)
def test_recursive_unsafe_values_fail_closed_without_sanitization(unsafe_text):
    result = _result()
    result["candidate_support"][0]["diagnostic_text"] = unsafe_text
    validation = contract.validate_dramatica_flow_informed_rubric_result(result)
    assert validation["fail_closed"] is True
    assert validation["normalized_result"]["candidate_support"][0]["diagnostic_text"] == unsafe_text


def test_recursive_unsafe_nested_value_is_rejected():
    result = _result()
    result["candidate_support"][0]["owner_decision"]["decision"] = "official output"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is False


@pytest.mark.parametrize("reason", [None, 4, "", "official output", "call model server", "final truth"])
def test_fail_closed_builder_sanitizes_unsafe_or_invalid_reason(reason):
    built = contract.build_dramatica_flow_informed_rubric_fail_closed_result(reason, request=_request())
    assert built["fail_closed_reason"] == "unsafe_or_invalid_input"
    assert built["status"] == "failed_closed"
    assert not any(built[bucket] for bucket in ("candidate_support", "diagnostic_questions", "uncertainty_notes", "insufficient_evidence_notes"))
    assert contract.validate_dramatica_flow_informed_rubric_result(built)["valid"] is True


def test_fail_closed_builder_preserves_only_validated_safe_refs_and_never_source_text():
    request = _request()
    request["evidence_refs"] = ["bad ref"]
    built = contract.build_dramatica_flow_informed_rubric_fail_closed_result("invalid input", request=request)
    assert built["source_refs"] == ["source_ref_1"]
    assert built["evidence_refs"] == []
    assert "source_text" not in built
    request["source_refs"].append("later")
    assert built["source_refs"] == ["source_ref_1"]


def test_fail_closed_builder_never_raises_for_malformed_input():
    built = contract.build_dramatica_flow_informed_rubric_fail_closed_result(object(), request={"source_refs": object()})
    assert built["rubric_id"] == contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID
    assert all(value is False for value in built["safety"].values())


def test_normalized_success_is_generic_runtime_compatible():
    normalized = contract.validate_dramatica_flow_informed_rubric_result(_result())["normalized_result"]
    allowlist_record = {"output_classes_allowed": ["rubric_mapping_support"]}
    compatibility = validate_analysis_runtime_output(normalized, allowlist_record)
    assert compatibility["allowed_output_class"] is True
    assert compatibility["output_class"] == "rubric_mapping_support"


def test_contract_has_no_io_runtime_or_persistence_dependencies():
    source = inspect.getsource(contract)
    forbidden_imports = ("import os", "import pathlib", "import subprocess", "import socket", "import requests", "import urllib", "import dramatica")
    assert not any(token in source for token in forbidden_imports)
    assert contract.__dict__.get("open") is None


def test_t009_fixture_identity_remains_separate_and_unchanged():
    from backend import omi_analysis_orchestrator as orchestrator

    adapter = orchestrator.OMI_ADAPTER_CONTRACTS["dramatica_flow"]
    assert "fixture-only" in adapter["behavior"]
    assert "dramatica_flow" != contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID


def test_t019c_identity_and_public_contract_remain_unchanged():
    assert t019c.SUBTXT_INFORMED_RUBRIC_ID == "app_owned_subtxt_informed_rubric"
    assert t019c.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION == "omi_app_owned_subtxt_informed_rubric_request.v1"
    assert t019c.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL == "App-owned Subtxt-informed diagnostic support"
