"""Focused in-memory tests for PHASE8-IMPL-023-T020D."""

from __future__ import annotations

import copy
import inspect
import re
import socket
import subprocess
from typing import Any

import pytest

from backend import omi_analysis_orchestrator as orchestrator
from backend.story_knowledge import analysis_runtime_integration as runtime_contract
from backend.story_knowledge import dramatica_flow_informed_analysis_rubric_contract as contract
from backend.story_knowledge import dramatica_flow_informed_analysis_rubric_evaluator as evaluator
from backend.story_knowledge import subtxt_informed_semantic_rubric_contract as subtxt_contract
from backend.story_knowledge import subtxt_informed_semantic_rubric_evaluator as subtxt_evaluator


def _request(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION,
        "rubric_id": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "request_id": "request_t020d_1",
        "project_name": "owner_project",
        "source_text": (
            "Mara promised to return because the warning caused a delay. "
            "Later her former ally became a rival. She felt relieved after "
            "Jon told her the concealed route had reopened."
        ),
        "source_locator": "source_locator_ref_owner_1",
        "source_refs": ["source_ref_owner_1"],
        "evidence_refs": ["evidence_ref_owner_1"],
        "provenance_refs": ["provenance_ref_owner_1"],
        "source_locator_refs": ["source_locator_ref_owner_1"],
        "requested_categories": [
            "causal_chain_diagnostic",
            "narrative_commitment_lifecycle_diagnostic",
            "emotional_state_consistency",
            "relationship_delta_diagnostic",
            "timeline_thread_activity_diagnostic",
            "information_boundary_diagnostic",
            "multidimensional_diagnostic_question",
            "ambiguity",
            "insufficient_evidence",
            "owner_review_question",
        ],
        "analysis_intent": "diagnostic_support",
        "owner_authored_or_owner_provided_source": True,
        "safety_confirmations": {
            key: True for key in contract.ALLOWED_REQUEST_SAFETY_CONFIRMATIONS
        },
    }
    value.update(overrides)
    return value


def _items(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for bucket in (
            "candidate_support", "diagnostic_questions", "uncertainty_notes",
            "insufficient_evidence_notes",
        )
        for item in result[bucket]
    ]


def _item_for(result: dict[str, Any], category: str) -> dict[str, Any] | None:
    return next((item for item in _items(result) if item["category"] == category), None)


def _evaluate_one(category: str, source_text: str) -> dict[str, Any]:
    return evaluator.evaluate_dramatica_flow_informed_analysis_rubric(
        _request(source_text=source_text, requested_categories=[category])
    )


def test_version_is_exact():
    assert evaluator.DRAMATICA_FLOW_INFORMED_RUBRIC_EVALUATOR_VERSION == (
        "app_owned_dramatica_flow_informed_rubric_evaluator.v1"
    )


def test_exact_public_evaluator_callable():
    owned = [
        name for name in dir(evaluator)
        if not name.startswith("_")
        and callable(getattr(evaluator, name))
        and getattr(getattr(evaluator, name), "__module__", None) == evaluator.__name__
    ]
    assert owned == ["evaluate_dramatica_flow_informed_analysis_rubric"]


def test_public_evaluator_accepts_object():
    assert isinstance(evaluator.evaluate_dramatica_flow_informed_analysis_rubric(object()), dict)


def test_valid_request_produces_contract_valid_result():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert result["status"] == "succeeded"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is True


def test_request_validator_is_used(monkeypatch):
    monkeypatch.setattr(
        evaluator, "validate_dramatica_flow_informed_rubric_request",
        lambda _value: {"status": "fail_closed"},
    )
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert result["fail_closed_reason"] == "request_validation_failed"


def test_invalid_request_fails_closed_and_validates():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(
        _request(analysis_intent="not_diagnostic")
    )
    assert result["status"] == "failed_closed"
    assert result["fail_closed_reason"] == "request_validation_failed"
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is True


@pytest.mark.parametrize("value", [None, "text", 1, [], object()])
def test_non_dictionary_request_fails_closed(value):
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(value)
    assert result["fail_closed_reason"] == "request_validation_failed"


def test_generated_result_validation_failure_fails_closed(monkeypatch):
    monkeypatch.setattr(
        evaluator, "validate_dramatica_flow_informed_rubric_result",
        lambda _value: {"status": "fail_closed"},
    )
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert result["fail_closed_reason"] == "result_validation_failed"


def test_unexpected_failure_fails_closed(monkeypatch):
    monkeypatch.setattr(evaluator, "_split_evidence_spans", lambda _value: (_ for _ in ()).throw(RuntimeError()))
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert result["fail_closed_reason"] == "unexpected_evaluator_failure"


def test_valid_input_is_not_mutated():
    request = _request()
    before = copy.deepcopy(request)
    evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    assert request == before


def test_invalid_input_is_not_mutated():
    request = {"bad": ["value"]}
    before = copy.deepcopy(request)
    evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    assert request == before


def test_result_is_deterministic():
    request = _request()
    assert evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request) == (
        evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    )


def test_requested_category_order_is_preserved_within_bucket():
    request = _request(
        source_text="Later the delay caused concern because the route closed.",
        requested_categories=["timeline_thread_activity_diagnostic", "causal_chain_diagnostic"],
    )
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    assert [item["category"] for item in result["candidate_support"]] == request["requested_categories"]


def test_source_span_order_selects_first_qualifying_span():
    source = "Because rain fell, the road closed. Therefore the ferry stopped."
    item = _item_for(_evaluate_one("causal_chain_diagnostic", source), "causal_chain_diagnostic")
    assert item["evidence"][0]["source_excerpt"] == "Because rain fell, the road closed."


def test_first_qualifying_span_wins_over_later_dual_signal():
    source = "Because rain fell, the road closed. Therefore the flood caused a delay."
    item = _item_for(_evaluate_one("causal_chain_diagnostic", source), "causal_chain_diagnostic")
    assert item["confidence"] == "low_support"


@pytest.mark.parametrize("category", sorted(contract.ALLOWED_CATEGORIES))
def test_at_most_one_item_per_category(category):
    source = (
        "Because rain caused delay. Because wind caused delay. Mara promised and later fulfilled it. "
        "She was afraid and became afraid. Her ally became a rival. Later the thread returned. "
        "Jon knew because Mara told him. Maybe this is unclear."
    )
    result = _evaluate_one(category, source)
    assert sum(item["category"] == category for item in _items(result)) <= 1


_POSITIVE_CASES = [
    ("causal_chain_diagnostic", "Rain fell because the clouds gathered."),
    ("narrative_commitment_lifecycle_diagnostic", "Mara promised to return before dawn."),
    ("emotional_state_consistency", "Mara was anxious at the gate."),
    ("relationship_delta_diagnostic", "Her former ally waited nearby."),
    ("timeline_thread_activity_diagnostic", "Later the northern thread returned."),
    ("information_boundary_diagnostic", "Jon learned the route from Mara."),
    ("multidimensional_diagnostic_question", "Later Mara learned the hidden route."),
    ("ambiguity", "Perhaps the warning refers to another crossing."),
    ("insufficient_evidence", "A brief note."),
    ("owner_review_question", "Plain owner source with no diagnostic cue."),
]


@pytest.mark.parametrize(("category", "source"), _POSITIVE_CASES)
def test_each_category_has_independent_positive_fixture(category, source):
    assert _item_for(_evaluate_one(category, source), category) is not None


_NEGATIVE_CASES = [
    ("causal_chain_diagnostic", "Mara crossed the quiet courtyard."),
    ("narrative_commitment_lifecycle_diagnostic", "Mara crossed the quiet courtyard."),
    ("emotional_state_consistency", "Mara crossed the quiet courtyard."),
    ("relationship_delta_diagnostic", "Mara crossed the quiet courtyard."),
    ("timeline_thread_activity_diagnostic", "Mara crossed the quiet courtyard."),
    ("information_boundary_diagnostic", "Mara crossed the quiet courtyard."),
    ("multidimensional_diagnostic_question", "Later Mara crossed the courtyard."),
    ("ambiguity", "Mara crossed the quiet courtyard."),
]


@pytest.mark.parametrize(("category", "source"), _NEGATIVE_CASES)
def test_signal_categories_have_independent_negative_fixture(category, source):
    result = _evaluate_one(category, source)
    assert result["status"] == "empty"
    assert _item_for(result, category) is None


def test_insufficient_evidence_negative_fixture_with_substantive_support():
    source = "Mara crossed the river because the storm caused the bridge to close before the evening patrol arrived."
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(
        _request(source_text=source, requested_categories=["causal_chain_diagnostic", "insufficient_evidence"])
    )
    assert _item_for(result, "causal_chain_diagnostic") is not None
    assert _item_for(result, "insufficient_evidence") is None


def test_owner_review_negative_fixture_is_invalid_empty_source():
    result = _evaluate_one("owner_review_question", "")
    assert result["status"] == "failed_closed"
    assert _item_for(result, "owner_review_question") is None


@pytest.mark.parametrize(
    ("category", "source"),
    [
        ("causal_chain_diagnostic", "The choice consequently changed the route."),
        ("narrative_commitment_lifecycle_diagnostic", "The obligation remains unfinished."),
        ("emotional_state_consistency", "Her mood shifted and she grew angry."),
        ("relationship_delta_diagnostic", "The partners drifted apart."),
        ("timeline_thread_activity_diagnostic", "Meanwhile the delayed thread resumed."),
        ("information_boundary_diagnostic", "He deduced the answer without being told."),
        ("ambiguity", "The account contains conflicting accounts."),
    ],
)
def test_original_cue_family_variants_are_bounded_and_testable(category, source):
    assert _item_for(_evaluate_one(category, source), category) is not None


@pytest.mark.parametrize("category", sorted(contract.ALLOWED_CATEGORIES))
def test_exact_contract_mappings(category):
    source = dict(_POSITIVE_CASES)[category]
    item = _item_for(_evaluate_one(category, source), category)
    assert item["candidate_type"] == contract.CATEGORY_TO_CANDIDATE_TYPE[category]
    assert item["statement_kind"] == contract.CATEGORY_TO_STATEMENT_KIND[category]


@pytest.mark.parametrize(
    ("category", "bucket"),
    [
        ("causal_chain_diagnostic", "candidate_support"),
        ("owner_review_question", "diagnostic_questions"),
        ("ambiguity", "uncertainty_notes"),
        ("insufficient_evidence", "insufficient_evidence_notes"),
    ],
)
def test_correct_bucket_placement(category, bucket):
    source = dict(_POSITIVE_CASES)[category]
    result = _evaluate_one(category, source)
    assert result[bucket][0]["category"] == category


def test_every_evidence_excerpt_is_exact_source_substring():
    request = _request(source_text="First line: Mara promised.\r\nLater Jon learned the route; perhaps too late.")
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    assert all(item["evidence"][0]["source_excerpt"] in request["source_text"] for item in _items(result))


def test_evidence_text_is_not_diagnostic_text():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert all(item["evidence"][0]["source_excerpt"] != item["diagnostic_text"] for item in _items(result))


@pytest.mark.parametrize("field", ["source_refs", "evidence_refs", "provenance_refs", "source_locator_refs"])
def test_top_level_and_item_references_are_preserved(field):
    request = _request()
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    assert result[field] == request[field]
    assert all(item[field] == request[field] for item in _items(result))


def test_locator_is_preserved_on_items_and_evidence():
    request = _request()
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(request)
    assert all(item["source_locator"] == request["source_locator"] for item in _items(result))
    assert all(item["evidence"][0]["source_locator"] == request["source_locator"] for item in _items(result))


def test_exact_app_owned_provenance_and_label():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    expected = {
        "tool_source": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "adapter": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID,
        "support": contract.DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL,
        "executes_dramatica_flow": False,
        "official_dramatica_flow_output": False,
    }
    assert result["provenance"] == expected
    assert all(item["provenance"] == expected for item in _items(result))
    assert all(item["support_label"] == contract.DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL for item in _items(result))


def test_owner_decision_and_review_status_are_pending():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert all(item["owner_decision"] == {"approved": False, "decision": "pending"} for item in _items(result))
    assert all(item["review_status"] == "candidate_review_pending" for item in _items(result))


def test_all_result_operation_flags_are_false():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert set(result["safety"]) == set(contract.OPERATION_FLAGS)
    assert all(value is False for value in result["safety"].values())


@pytest.mark.parametrize("flag", sorted(contract.ITEM_OPERATION_FLAGS))
def test_all_item_operation_flags_are_false(flag):
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert all(item[flag] is False for item in _items(result))


def test_high_support_is_never_emitted():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert all(item["confidence"] != "high_support" for item in _items(result))


@pytest.mark.parametrize(
    ("category", "source"),
    [
        ("causal_chain_diagnostic", "Therefore the storm caused a delay."),
        ("narrative_commitment_lifecycle_diagnostic", "The promise was fulfilled."),
        ("emotional_state_consistency", "She was bitter and then turned bitter."),
        ("relationship_delta_diagnostic", "Her ally became a rival."),
        ("timeline_thread_activity_diagnostic", "Later the thread returned."),
        ("information_boundary_diagnostic", "Jon learned the route when Mara told him."),
    ],
)
def test_medium_support_requires_two_independent_signals(category, source):
    item = _item_for(_evaluate_one(category, source), category)
    assert item["confidence"] == "medium_support"


@pytest.mark.parametrize(("category", "source"), _POSITIVE_CASES)
def test_confidence_and_uncertainty_values_are_contract_allowed(category, source):
    item = _item_for(_evaluate_one(category, source), category)
    assert item["confidence"] in contract.ALLOWED_CONFIDENCE_VALUES
    assert item["uncertainty_label"] in contract.ALLOWED_UNCERTAINTY_VALUES


def test_questions_require_owner_interpretation():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    questions = result["diagnostic_questions"]
    assert questions and all(item["uncertainty_label"] == "requires_owner_interpretation" for item in questions)


def test_ambiguity_uses_exact_uncertainty_value():
    item = _item_for(_evaluate_one("ambiguity", "Maybe the route is open."), "ambiguity")
    assert item["uncertainty_label"] == "ambiguity"


def test_insufficient_evidence_uses_exact_uncertainty_value():
    item = _item_for(_evaluate_one("insufficient_evidence", "Short note."), "insufficient_evidence")
    assert item["uncertainty_label"] == "insufficient_evidence"


def test_conflicting_substantive_signal_uses_conflicting_support():
    item = _item_for(
        _evaluate_one("causal_chain_diagnostic", "Because the gate closed, but also the report says it opened."),
        "causal_chain_diagnostic",
    )
    assert item["uncertainty_label"] == "conflicting_support"


@pytest.mark.parametrize("source", ["Plain words.", "Owner source without signal but with enough words for a useful diagnostic review question today."])
def test_owner_review_question_always_emits_for_valid_non_empty_source(source):
    assert _item_for(_evaluate_one("owner_review_question", source), "owner_review_question") is not None


def test_multidimensional_question_requires_two_dimensions_in_one_span():
    positive = _evaluate_one("multidimensional_diagnostic_question", "Later Mara learned the secret.")
    negative = _evaluate_one("multidimensional_diagnostic_question", "Later Mara crossed the bridge.")
    assert _item_for(positive, "multidimensional_diagnostic_question") is not None
    assert negative["status"] == "empty"


@pytest.mark.parametrize("word_count", [1, 5, 11])
def test_materially_short_threshold_below_twelve_words(word_count):
    source = " ".join(["plain"] * word_count)
    assert _item_for(_evaluate_one("insufficient_evidence", source), "insufficient_evidence") is not None


def test_twelve_words_without_substantive_match_still_insufficient():
    source = "one two three four five six seven eight nine ten eleven twelve"
    assert _item_for(_evaluate_one("insufficient_evidence", source), "insufficient_evidence") is not None


def test_insufficient_not_emitted_merely_for_one_unmatched_category():
    source = "Mara crossed because the storm caused the bridge closure before the patrol reached the river bank."
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(
        _request(source_text=source, requested_categories=["causal_chain_diagnostic", "emotional_state_consistency", "insufficient_evidence"])
    )
    assert _item_for(result, "causal_chain_diagnostic") is not None
    assert _item_for(result, "emotional_state_consistency") is None
    assert _item_for(result, "insufficient_evidence") is None


def test_normal_no_match_returns_empty_not_error():
    result = _evaluate_one("causal_chain_diagnostic", "Mara crossed the courtyard quietly.")
    assert result["status"] == "empty"
    assert "fail_closed_reason" not in result


def test_quoted_unsafe_words_are_allowed_only_as_owner_evidence():
    source = 'Mara wrote "official model server final truth" and maybe doubted the phrase.'
    result = _evaluate_one("ambiguity", source)
    assert result["status"] == "succeeded"
    assert _item_for(result, "ambiguity")["evidence"][0]["source_excerpt"] in source


def test_generated_text_remains_contract_safe():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert contract.validate_dramatica_flow_informed_rubric_result(result)["valid"] is True


def test_all_question_text_ends_with_question_mark():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert result["diagnostic_questions"]
    assert all(item["diagnostic_text"].endswith("?") for item in result["diagnostic_questions"])


def _allowlist() -> dict[str, Any]:
    return {
        "output_classes_allowed": ["rubric_mapping_support"],
        "required_refs": ["source_refs", "evidence_refs", "provenance_refs", "source_locator_refs"],
    }


def test_succeeded_shape_is_generic_runtime_compatible():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())
    assert runtime_contract.validate_analysis_runtime_output(result, _allowlist())["allowed_output_class"] is True


def test_failed_closed_shape_is_generic_runtime_compatible():
    result = evaluator.evaluate_dramatica_flow_informed_analysis_rubric({"bad": True})
    assert runtime_contract.validate_analysis_runtime_output(result, _allowlist())["allowed_output_class"] is True


def test_module_imports_only_standard_library_and_t020c_contract():
    imports = set(re.findall(r"^(?:from|import)\s+([\w.]+)", inspect.getsource(evaluator), re.MULTILINE))
    assert imports <= {
        "__future__", "copy", "re", "typing",
        "backend.story_knowledge.dramatica_flow_informed_analysis_rubric_contract",
    }


@pytest.mark.parametrize(
    "token",
    [
        "import os", "os.environ", "getenv(", "import pathlib", "open(",
        "import subprocess", "import socket", "import requests", "import urllib",
        "import openai", "import ollama", "candidate_storage", "project_manager",
        "review_queue_storage", "apply_promotion(", ".external_sources",
    ],
)
def test_module_has_no_forbidden_dependency_or_side_effect_token(token):
    assert token not in inspect.getsource(evaluator)


def test_runtime_does_not_call_shell_or_network(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError()))
    monkeypatch.setattr(subprocess, "Popen", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError()))
    monkeypatch.setattr(socket, "socket", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError()))
    assert evaluator.evaluate_dramatica_flow_informed_analysis_rubric(_request())["status"] == "succeeded"


def test_t020e_omi_adapter_registration_is_explicit_only_and_distinct():
    adapter = "dramatica_flow_informed_rubric"
    assert adapter in orchestrator.OMI_TOOL_ADAPTER_IDENTITIES
    assert adapter in orchestrator.OMI_ADAPTER_CONTRACTS
    assert adapter not in orchestrator.OMI_DEFAULT_ADAPTERS
    assert adapter not in orchestrator.OMI_CONTEXT_ADAPTER_NAMES
    assert adapter != "dramatica_flow"
    assert "dramatica_flow" in orchestrator.OMI_TOOL_ADAPTER_IDENTITIES
    assert contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID == (
        "app_owned_dramatica_flow_informed_rubric"
    )
    assert callable(evaluator.evaluate_dramatica_flow_informed_analysis_rubric)
    assert evaluator.evaluate_dramatica_flow_informed_analysis_rubric(
        _request()
    )["status"] == "succeeded"
    assert "not live or official dramatica-flow output" in (
        orchestrator.OMI_ADAPTER_CONTRACTS[adapter]["behavior"]
    )


def test_t009_fixture_identity_is_preserved():
    assert "fixture-only" in orchestrator.OMI_ADAPTER_CONTRACTS["dramatica_flow"]["behavior"]
    assert contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID != "dramatica_flow"


def test_t020c_contract_regression_identity_and_validator():
    assert contract.DRAMATICA_FLOW_INFORMED_RUBRIC_ID == "app_owned_dramatica_flow_informed_rubric"
    assert contract.validate_dramatica_flow_informed_rubric_request(_request())["valid"] is True


def test_t019d_evaluator_regression():
    request = {
        "schema_version": subtxt_contract.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION,
        "rubric_id": subtxt_contract.SUBTXT_INFORMED_RUBRIC_ID,
        "request_id": "request_t019d_regression",
        "project_name": "owner_project",
        "source_text": "Mara wants the key, but a rival blocks her path.",
        "source_locator": "source_locator_ref_t019d",
        "source_refs": ["source_ref_t019d"],
        "evidence_refs": ["evidence_ref_t019d"],
        "provenance_refs": ["provenance_ref_t019d"],
        "source_locator_refs": ["source_locator_ref_t019d"],
        "requested_categories": ["structural_diagnostic"],
        "analysis_intent": "diagnostic_support",
        "owner_authored_or_owner_provided_source": True,
        "safety_confirmations": {key: True for key in subtxt_contract.ALLOWED_REQUEST_SAFETY_CONFIRMATIONS},
    }
    result = subtxt_evaluator.evaluate_subtxt_informed_semantic_rubric(request)
    assert subtxt_contract.validate_subtxt_informed_rubric_result(result)["valid"] is True
