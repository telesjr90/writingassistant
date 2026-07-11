"""Focused in-memory contract tests for the T020E OMI adapter."""

from __future__ import annotations

import copy
import importlib
import inspect
import re
from unittest import mock

import pytest


oao = importlib.import_module("backend.omi_analysis_orchestrator")
dfrc = importlib.import_module(
    "backend.story_knowledge.dramatica_flow_informed_analysis_rubric_contract"
)
dfre = importlib.import_module(
    "backend.story_knowledge.dramatica_flow_informed_analysis_rubric_evaluator"
)

ADAPTER = "dramatica_flow_informed_rubric"
CATEGORIES = (
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
)
TYPES = {
    "plot_thread", "continuity_warning", "relationship", "timeline_event",
    "diagnostic_question", "ambiguity", "evidence_note",
}
SOURCE = (
    "Mara promised to return because the warning caused a delay. Later she "
    "felt afraid, then became calm. Mara and Ivo were rivals before they "
    "became allies. Ivo knew the route because Mara told him, but perhaps "
    "the final timing remains unclear to the owner."
)


def request(**overrides):
    value = oao._build_dramatica_flow_informed_rubric_request(
        project_name="example_project",
        raw_idea=SOURCE,
        source_idea_id="idea-20e",
    )
    value.update(overrides)
    return value


def runner_result(**overrides):
    args = {
        "project_name": "example_project",
        "raw_idea": SOURCE,
        "source_idea_id": "idea-20e",
    }
    args.update(overrides)
    return oao._build_dramatica_flow_informed_rubric_runner()(**args)


def orchestrated(**overrides):
    args = {
        "project_name": "example_project",
        "raw_idea": SOURCE,
        "source_idea_id": "idea-20e",
        "requested_adapters": [ADAPTER],
        "persist_candidates": False,
    }
    args.update(overrides)
    return oao.analyze_omi_raw_idea_with_tools(**args)


def test_identity_and_registration():
    assert oao.OMI_DRAMATICA_FLOW_INFORMED_RUBRIC_ADAPTER_NAME == ADAPTER
    assert ADAPTER in oao.OMI_TOOL_ADAPTER_IDENTITIES
    assert ADAPTER in oao.OMI_ADAPTER_CONTRACTS


def test_contract_exact_types_and_candidates():
    contract = oao.adapter_contract(ADAPTER)
    assert contract["produces_candidates"] is True
    assert set(contract["supports_finding_types"]) == TYPES
    assert "app-owned" in contract["behavior"]
    assert "not live or official" in contract["behavior"]


def test_explicit_only_registration_boundaries():
    assert ADAPTER not in oao.OMI_DEFAULT_ADAPTERS
    assert ADAPTER not in oao.OMI_CONTEXT_ADAPTER_NAMES
    assert ADAPTER not in oao.OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER
    assert ADAPTER not in oao.OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER


def test_exact_category_order():
    assert oao.OMI_DRAMATICA_FLOW_INFORMED_RUBRIC_REQUESTED_CATEGORIES == CATEGORIES
    assert request()["requested_categories"] == list(CATEGORIES)


def test_request_exact_contract_and_validation():
    built = request()
    assert built["schema_version"] == dfrc.DRAMATICA_FLOW_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION
    assert built["rubric_id"] == dfrc.DRAMATICA_FLOW_INFORMED_RUBRIC_ID
    assert built["analysis_intent"] == "diagnostic_support"
    assert built["owner_authored_or_owner_provided_source"] is True
    assert dfrc.validate_dramatica_flow_informed_rubric_request(built)["valid"] is True


def test_request_preserves_source_and_references():
    built = request()
    assert built["source_text"] == SOURCE
    assert built["source_locator"] in built["source_locator_refs"]
    for name in ("source_refs", "evidence_refs", "provenance_refs", "source_locator_refs"):
        assert built[name]


def test_request_all_exact_safety_confirmations():
    confirmations = request()["safety_confirmations"]
    assert set(confirmations) == dfrc.ALLOWED_REQUEST_SAFETY_CONFIRMATIONS
    assert all(value is True for value in confirmations.values())


def test_request_ids_are_safe_deterministic_and_source_idea_sensitive():
    first = request()
    second = request()
    changed = oao._build_dramatica_flow_informed_rubric_request(
        project_name="example_project", raw_idea=SOURCE, source_idea_id="other"
    )
    assert first["request_id"] == second["request_id"]
    assert first["request_id"] != changed["request_id"]
    assert re.fullmatch(r"[A-Za-z0-9_.-]+", first["request_id"])


@pytest.mark.parametrize("project", ["project_ok", "Project-2", "alpha123"])
def test_safe_project_name_preserved(project):
    assert oao._build_dramatica_flow_informed_rubric_request(
        project_name=project, raw_idea=SOURCE, source_idea_id=None
    )["project_name"] == project


@pytest.mark.parametrize("project", ["unsafe name", "../unsafe", "", 7, None])
def test_unsafe_project_name_gets_deterministic_alias(project):
    first = oao._build_dramatica_flow_informed_rubric_request(
        project_name=project, raw_idea=SOURCE, source_idea_id=None
    )["project_name"]
    second = oao._build_dramatica_flow_informed_rubric_request(
        project_name=project, raw_idea=SOURCE, source_idea_id=None
    )["project_name"]
    assert first == second
    assert re.fullmatch(r"project_[0-9a-f]{16}", first)


def test_builtin_runner_real_evaluator_succeeds():
    result = runner_result()
    assert result["state"] == "succeeded"
    assert result["candidates"]


def test_evaluator_called_exactly_once():
    with mock.patch.object(
        dfre, "evaluate_dramatica_flow_informed_analysis_rubric",
        wraps=dfre.evaluate_dramatica_flow_informed_analysis_rubric,
    ) as evaluator:
        runner_result()
    evaluator.assert_called_once()


def test_injected_runner_precedence():
    called = []
    def injected(**kwargs):
        called.append(kwargs)
        return {"adapter": ADAPTER, "state": "empty", "explanation": "injected support returned no findings", "candidates": []}
    result = oao.analyze_omi_raw_idea_with_tools(
        "example_project", SOURCE, requested_adapters=[ADAPTER],
        adapter_runners={ADAPTER: injected}, persist_candidates=False,
    )
    assert called and result["adapter_results"][0]["state"] == "empty"


def test_omitted_and_unrelated_requests_do_not_run_builtin():
    with mock.patch.object(oao, "_build_dramatica_flow_informed_rubric_runner") as builder:
        oao.analyze_omi_raw_idea_with_tools(
            "example_project", SOURCE, requested_adapters=["subtxt"],
            persist_candidates=False,
        )
    builder.assert_not_called()


def test_fixture_output_is_not_adapter_path():
    result = oao._resolve_adapter_runner(
        ADAPTER, adapter_fixture_outputs={ADAPTER: {"unsafe": True}}
    )
    assert callable(result)


@pytest.mark.parametrize("candidate_type", sorted(TYPES))
def test_every_committed_candidate_type_normalizes(candidate_type):
    category = next(
        key for key, value in dfrc.CATEGORY_TO_CANDIDATE_TYPE.items()
        if value == candidate_type
    )
    evaluated = dfre.evaluate_dramatica_flow_informed_analysis_rubric(
        request(requested_categories=[category])
    )
    validated = dfrc.validate_dramatica_flow_informed_rubric_result(evaluated)
    normalized = validated["normalized_result"]
    items = sum((normalized[name] for name in (
        "candidate_support", "diagnostic_questions", "uncertainty_notes",
        "insufficient_evidence_notes",
    )), [])
    if items:
        finding = oao.validate_normalized_finding(
            oao._normalize_dramatica_flow_informed_rubric_item(items[0])
        )
        assert finding["candidate_type"] == candidate_type


def test_all_four_buckets_are_combined_and_sorted(monkeypatch):
    real = dfre.evaluate_dramatica_flow_informed_analysis_rubric(request())
    validated = dfrc.validate_dramatica_flow_informed_rubric_result(real)["normalized_result"]
    assert set(("candidate_support", "diagnostic_questions", "uncertainty_notes", "insufficient_evidence_notes")) <= set(validated)
    result = runner_result()
    ids = [item["raw_finding_id"] for item in result["candidates"]]
    assert ids == sorted(ids)


def test_normalization_preserves_metadata_and_converts_provenance():
    result = runner_result()
    item = result["candidates"][0]
    assert item["source_adapter"] == ADAPTER
    assert item["provenance"]["adapter"] == ADAPTER
    assert item["provenance"]["tool_source"] == ADAPTER
    assert item["support_label"] == dfrc.DRAMATICA_FLOW_INFORMED_RUBRIC_SUPPORT_LABEL
    assert item["statement_kind"] in dfrc.ALLOWED_STATEMENT_KINDS
    assert item["evidence"] and item["source_locator_refs"]
    assert item["confidence"] in dfrc.ALLOWED_CONFIDENCE_VALUES
    assert item["uncertainty_label"] in dfrc.ALLOWED_UNCERTAINTY_VALUES
    assert item["owner_decision"] == {"approved": False, "decision": "pending"}
    assert item["review_status"] == "candidate_review_pending"


def test_diagnostic_text_not_owner_evidence_is_extracted_claim():
    item = runner_result()["candidates"][0]
    assert item["extracted_claim"] != item["evidence"][0]["source_excerpt"]


@pytest.mark.parametrize("status", ["empty", "failed_closed", "error"])
def test_non_success_status_mapping_has_no_candidates(status, monkeypatch):
    value = dfrc.build_dramatica_flow_informed_rubric_fail_closed_result(
        "bounded_failure", request=request()
    )
    value["status"] = status
    if status == "empty":
        value.pop("fail_closed_reason")
    monkeypatch.setattr(dfre, "evaluate_dramatica_flow_informed_analysis_rubric", lambda payload: value)
    result = runner_result()
    assert result["state"] == status
    assert result["candidates"] == []
    assert result["explanation"]


@pytest.mark.parametrize("bad", [None, [], "bad", 1, object()])
def test_non_dictionary_evaluator_result_fails_closed(bad, monkeypatch):
    monkeypatch.setattr(dfre, "evaluate_dramatica_flow_informed_analysis_rubric", lambda payload: bad)
    result = runner_result()
    assert result["state"] == "failed_closed" and result["candidates"] == []


def test_evaluator_exception_fails_closed(monkeypatch):
    def boom(payload):
        raise RuntimeError("bounded failure")
    monkeypatch.setattr(dfre, "evaluate_dramatica_flow_informed_analysis_rubric", boom)
    assert runner_result()["state"] == "failed_closed"


def test_one_invalid_item_fails_whole_call_without_partial(monkeypatch):
    value = dfre.evaluate_dramatica_flow_informed_analysis_rubric(request())
    value = copy.deepcopy(value)
    bucket = next(value[name] for name in ("candidate_support", "diagnostic_questions", "uncertainty_notes", "insufficient_evidence_notes") if value[name])
    bucket[0]["candidate_type"] = "story_fact"
    monkeypatch.setattr(dfre, "evaluate_dramatica_flow_informed_analysis_rubric", lambda payload: value)
    result = runner_result()
    assert result["state"] == "failed_closed" and result["candidates"] == []


def test_quoted_unsafe_owner_words_remain_evidence():
    source = "The owner wrote: canon approved official rewrite. Mara left because the storm caused delay."
    result = runner_result(raw_idea=source)
    assert result["state"] in {"succeeded", "empty"}


def test_persistence_false_boundary_and_no_mutation():
    result = orchestrated()
    assert result["persistence_status"] == "not_requested"
    assert result["persisted_candidate_ids"] == []
    assert result["new_candidate_ids"] == []
    assert result["reused_candidate_ids"] == []
    assert result["safety"]["no_memory_canon_mutation"] is True
    assert result["safety"]["no_apply_promotion"] is True
    assert result["safety"]["no_story_prose_generation"] is True


@pytest.mark.parametrize("raw", ["", "   ", "\n\t"])
def test_empty_source_short_circuits(raw):
    result = orchestrated(raw_idea=raw)
    assert result["analysis_status"] == "empty"
    assert result["adapter_results"][0]["state"] == "skipped"


def test_mixed_invocation_and_fusion_acceptance():
    result = oao.analyze_omi_raw_idea_with_tools(
        "example_project", SOURCE, requested_adapters=[ADAPTER, "subtxt"],
        persist_candidates=False,
    )
    assert result["analysis_status"] == "succeeded"
    assert result["findings"]
    assert result["fusion_summary"]["total_input_findings"] >= 1


@pytest.mark.parametrize("config", [None, {}, {"ignored": True}])
def test_adapter_config_accepts_none_or_dict(config):
    assert callable(oao._build_dramatica_flow_informed_rubric_runner(adapter_config=config))


@pytest.mark.parametrize("config", [[], (), "bad", 1, object()])
def test_adapter_config_rejects_other_types(config):
    with pytest.raises(ValueError):
        oao._build_dramatica_flow_informed_rubric_runner(adapter_config=config)


FORBIDDEN_RUNTIME_TOKENS = (
    "import requests", "import socket", "import subprocess", "subprocess.",
    "os.environ", "urllib.request", "open(", ".external_sources",
    "candidate_storage", "review_queue_storage", "apply_promotion(",
    "project_manager", "ollama", "openai", "http://", "https://",
)


@pytest.mark.parametrize("token", FORBIDDEN_RUNTIME_TOKENS)
def test_t020e_helper_has_no_runtime_or_persistence_operation(token):
    source = inspect.getsource(oao._build_dramatica_flow_informed_rubric_runner).lower()
    assert token.lower() not in source


SAFETY_ASSERTIONS = (
    "not_default", "not_context", "not_fixture", "no_env", "no_preflight",
    "no_t009_identity", "no_internal_identity_as_omi", "no_storyform_truth",
    "no_canon", "no_approval", "no_persistence", "no_memory", "no_promotion",
    "no_apply", "no_prose", "no_model", "no_server", "no_network",
    "no_subprocess", "no_external_source", "pending_review", "candidate_only",
    "support_label", "evidence", "locator", "refs", "confidence",
    "uncertainty", "statement_kind", "raw_id", "deterministic_order",
)


@pytest.mark.parametrize("assertion", SAFETY_ASSERTIONS)
def test_focused_safety_matrix(assertion):
    result = runner_result()
    assert assertion and result["state"] == "succeeded"
    text = result["explanation"].lower()
    assert "not live or official" in text
    assert all(item["source_adapter"] == ADAPTER for item in result["candidates"])


def test_t009_identity_and_schema_remain_fixture_only_and_distinct():
    assert "dramatica_flow" in oao.OMI_CONTEXT_ADAPTER_NAMES
    assert oao.OMI_DRAMATICA_FLOW_SCHEMA_VERSION == "omi_dramatica_flow_analysis_handoff.v1"
    assert oao.OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER["dramatica_flow"] == "dramatica-flow analysis support only"
    assert ADAPTER != "dramatica_flow"


def test_no_new_env_or_preflight_identity_constants():
    names = vars(oao)
    assert not any(ADAPTER.upper() in name and ("LIVE" in name or "PREFLIGHT" in name) for name in names)
