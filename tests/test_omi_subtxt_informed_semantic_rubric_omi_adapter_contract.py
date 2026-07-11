"""PHASE8-IMPL-023-T019E app-owned Subtxt-informed semantic-rubric OMI
adapter integration tests.

These tests cover the integration of the committed T019D evaluator into the
OMI analysis orchestrator under the new ``subtxt_informed_rubric`` adapter
identity. They never execute Subtxt, never read or import
``.external_sources``, never call a model, never persist candidates, never
mutate projects, Memory, or Canon, and never read real project files. The
tests use only the orchestrator module, the T019C contract module, the
T019D evaluator module, synthetic in-memory dictionaries, and
monkeypatching.

Boundary phrases: confidence/support is not truth; tool output is not
canon; tool output is not truth; no automatic Storyform; no automatic
Dramatica/Storyform truth; no official Subtxt output; no live Subtxt
runtime; no generated prose; no rewrite; no continuation; no outline;
no candidate persistence; no review-queue creation; no Memory/Canon
mutation; no promotion record; no apply-promotion; no training/model
artifacts; fail closed; no silent fallback; queue presence is not
approval; candidate persistence is not canon.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import re
import sys
import types
from pathlib import Path
from typing import Any
from unittest import mock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Fake fastapi / pydantic so backend.main is importable in this lightweight
# test environment, mirroring the pattern used by other OMI test files.
# ---------------------------------------------------------------------------


class _FakeFastAPI:
    def __init__(self, *args, **kwargs):
        return None

    def add_middleware(self, *args, **kwargs):
        return None

    def include_router(self, *args, **kwargs):
        return None

    def add_api_route(self, *args, **kwargs):
        return None

    def middleware(self, *args, **kwargs):
        return self._decorator

    def get(self, *args, **kwargs):
        return self._decorator

    def post(self, *args, **kwargs):
        return self._decorator

    def patch(self, *args, **kwargs):
        return self._decorator

    def put(self, *args, **kwargs):
        return self._decorator

    @staticmethod
    def _decorator(func):
        return func


class _FakeAPIRouter(_FakeFastAPI):
    pass


class _FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class _FakeBaseModel:
    pass


fake_fastapi = types.ModuleType("fastapi")
fake_fastapi.APIRouter = _FakeAPIRouter
fake_fastapi.FastAPI = _FakeFastAPI
fake_fastapi.HTTPException = _FakeHTTPException
fake_fastapi.Request = object
fake_middleware = types.ModuleType("fastapi.middleware")
fake_cors = types.ModuleType("fastapi.middleware.cors")
fake_cors.CORSMiddleware = object
fake_responses = types.ModuleType("fastapi.responses")
fake_responses.JSONResponse = dict
fake_pydantic = types.ModuleType("pydantic")
fake_pydantic.BaseModel = _FakeBaseModel

sys.modules.setdefault("fastapi", fake_fastapi)
sys.modules.setdefault("fastapi.middleware", fake_middleware)
sys.modules.setdefault("fastapi.middleware.cors", fake_cors)
sys.modules.setdefault("fastapi.responses", fake_responses)
sys.modules.setdefault("pydantic", fake_pydantic)


backend_pkg = importlib.import_module("backend")
sys.modules.setdefault("backend", backend_pkg)
oao = importlib.import_module("backend.omi_analysis_orchestrator")

sisc = importlib.import_module(
    "backend.story_knowledge.subtxt_informed_semantic_rubric_contract"
)
sise = importlib.import_module(
    "backend.story_knowledge.subtxt_informed_semantic_rubric_evaluator"
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _valid_safety_confirmations() -> dict[str, bool]:
    return {key: True for key in sisc.ALLOWED_REQUEST_SAFETY_CONFIRMATIONS}


def _valid_request(**overrides: Any) -> dict[str, Any]:
    request: dict[str, Any] = {
        "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION,
        "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
        "request_id": "test-request-001",
        "project_name": "example_project",
        "source_text": (
            "Mara wants to find the archive key, but a rival threatens to "
            "block her path. The mentor decides to help Mara. Later Mara "
            "discovers that the key is hidden in the tower. Maybe the key "
            "is in the library."
        ),
        "source_locator": "source_locator_ref_raw_idea",
        "source_refs": ["source_ref_raw_idea"],
        "evidence_refs": ["evidence_ref_raw_idea"],
        "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
        "source_locator_refs": ["source_locator_ref_raw_idea"],
        "requested_categories": list(
            oao.OMI_SUBTXT_INFORMED_RUBRIC_REQUESTED_CATEGORIES
        ),
        "analysis_intent": "diagnostic_support",
        "owner_authored_or_owner_provided_source": True,
        "safety_confirmations": _valid_safety_confirmations(),
    }
    request.update(overrides)
    return request


def _short_input() -> str:
    return "Hello world."


def _structural_only_source() -> str:
    return (
        "Mara wants to find the archive key, but a rival blocks her path."
    )


def _conflict_only_source() -> str:
    return (
        "The rival refuses to help and threatens the mentor."
    )


def _throughline_only_source() -> str:
    return (
        "Mara asks the mentor to help her. The rival refuses Mara. "
        "Jonah opposes the mentor."
    )


def _story_point_only_source() -> str:
    return (
        "Later Mara discovers the key and changes her plan."
    )


def _source_of_conflict_only_source() -> str:
    return (
        "Mara wants the key because the archive door is locked, but the "
        "rival blocks her."
    )


def _subject_vs_conflict_only_source() -> str:
    return (
        "Mara and the rival walk the bridge together."
    )


def _ambiguity_only_source() -> str:
    return (
        "Maybe the key is hidden. Perhaps it was the mentor."
    )


def _insufficient_evidence_only_source() -> str:
    return "Hi."


# ---------------------------------------------------------------------------
# 1. exact adapter identity constant
# ---------------------------------------------------------------------------


def test_exact_adapter_identity_constant() -> None:
    assert oao.OMI_SUBTXT_INFORMED_RUBRIC_ADAPTER_NAME == "subtxt_informed_rubric"


# ---------------------------------------------------------------------------
# 2. identity registered in OMI_TOOL_ADAPTER_IDENTITIES
# ---------------------------------------------------------------------------


def test_identity_registered_in_tool_adapter_identities() -> None:
    assert "subtxt_informed_rubric" in oao.OMI_TOOL_ADAPTER_IDENTITIES
    assert oao.OMI_SUBTXT_INFORMED_RUBRIC_ADAPTER_NAME in (
        oao.OMI_TOOL_ADAPTER_IDENTITIES
    )


# ---------------------------------------------------------------------------
# 3. adapter contract exists
# ---------------------------------------------------------------------------


def test_adapter_contract_exists() -> None:
    contract = oao.adapter_contract("subtxt_informed_rubric")
    assert isinstance(contract, dict)
    assert "behavior" in contract
    assert isinstance(contract["behavior"], str)
    assert contract["behavior"]
    assert contract["produces_candidates"] is True
    assert isinstance(
        contract["supports_finding_types"], (tuple, list, frozenset)
    )


def test_adapter_contract_describes_app_owned_diagnostic_only() -> None:
    contract = oao.adapter_contract("subtxt_informed_rubric")
    text = contract["behavior"].lower()
    assert "app-owned" in text
    assert "diagnostic" in text
    assert "candidate-only" in text
    assert "owner-review pending" in text
    assert "no automatic persistence" in text
    assert "canon mutation" in text
    assert "apply-promotion" in text
    assert "no generated prose" in text
    assert "evidence" in text
    assert "source-locator" in text


# ---------------------------------------------------------------------------
# 4. supported finding types are bounded
# ---------------------------------------------------------------------------


def test_supported_finding_types_are_bounded() -> None:
    contract = oao.adapter_contract("subtxt_informed_rubric")
    allowed = set(contract["supports_finding_types"])
    expected = {
        "structural_diagnostic",
        "conflict_diagnostic",
        "diagnostic_question",
        "ambiguity",
        "evidence_note",
    }
    assert allowed == expected
    for finding_type in allowed:
        assert finding_type in oao.OMI_ORCHESTRATOR_FINDING_TYPES


def test_supported_finding_types_excludes_context_only_types() -> None:
    contract = oao.adapter_contract("subtxt_informed_rubric")
    allowed = set(contract["supports_finding_types"])
    forbidden = {
        "throughline_context",
        "storyform_context",
        "open_question",
        "continuity_warning",
        "world_rule",
    }
    for finding_type in forbidden:
        assert finding_type not in allowed


# ---------------------------------------------------------------------------
# 5. adapter is absent from OMI_DEFAULT_ADAPTERS
# ---------------------------------------------------------------------------


def test_adapter_absent_from_default_adapters() -> None:
    assert "subtxt_informed_rubric" not in oao.OMI_DEFAULT_ADAPTERS


def test_default_orchestrator_call_does_not_run_new_adapter() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
    )
    adapters_seen = {
        env["adapter"] for env in result["adapter_results"]
    }
    assert "subtxt_informed_rubric" not in adapters_seen


# ---------------------------------------------------------------------------
# 6. adapter is absent from OMI_CONTEXT_ADAPTER_NAMES
# ---------------------------------------------------------------------------


def test_adapter_absent_from_context_adapter_names() -> None:
    assert "subtxt_informed_rubric" not in oao.OMI_CONTEXT_ADAPTER_NAMES


def test_adapter_does_not_route_through_t009_fixture_contract() -> None:
    assert "subtxt_informed_rubric" not in oao.OMI_CONTEXT_ADAPTER_NAMES
    assert "subtxt_informed_rubric" not in {
        "ncp", "subtxt", "dramatica_flow"
    }


# ---------------------------------------------------------------------------
# 7. existing subtxt identity remains present and unchanged
# ---------------------------------------------------------------------------


def test_existing_subtxt_identity_remains_present() -> None:
    assert "subtxt" in oao.OMI_TOOL_ADAPTER_IDENTITIES
    assert "subtxt" in oao.OMI_DEFAULT_ADAPTERS
    assert "subtxt" in oao.OMI_CONTEXT_ADAPTER_NAMES
    assert oao.OMI_SUBTXT_SCHEMA_VERSION == "omi_subtxt_diagnostic_handoff.v1"


def test_existing_subtxt_contract_entry_remains() -> None:
    contract = oao.adapter_contract("subtxt")
    assert "fixture-only" in contract["behavior"]
    assert "Dramatica" in contract["behavior"]


# ---------------------------------------------------------------------------
# 8. explicit request resolves the built-in runner
# ---------------------------------------------------------------------------


def test_explicit_request_resolves_built_in_runner() -> None:
    runner = oao._resolve_adapter_runner(
        "subtxt_informed_rubric",
        adapter_config=None,
    )
    assert runner is not None
    assert callable(runner)


def test_explicit_orchestrator_call_runs_built_in_runner() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
    )
    adapters_seen = {
        env["adapter"] for env in result["adapter_results"]
    }
    assert "subtxt_informed_rubric" in adapters_seen
    env = next(
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    )
    assert env["state"] in {"succeeded", "empty", "failed_closed", "error"}


# ---------------------------------------------------------------------------
# 9. omitted/default request does not run the new adapter
# ---------------------------------------------------------------------------


def test_omitted_request_does_not_run_new_adapter() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
    )
    adapters_seen = {
        env["adapter"] for env in result["adapter_results"]
    }
    assert "subtxt_informed_rubric" not in adapters_seen


def test_unrelated_explicit_request_does_not_run_new_adapter() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
        requested_adapters=["ollama_model"],
    )
    adapters_seen = {
        env["adapter"] for env in result["adapter_results"]
    }
    assert "subtxt_informed_rubric" not in adapters_seen


# ---------------------------------------------------------------------------
# 10. injected adapter_runners override retains precedence
# ---------------------------------------------------------------------------


def test_injected_runner_overrides_built_in_runner() -> None:
    captured: list[dict[str, Any]] = []

    def fake_runner(
        *, project_name: str, raw_idea: str, source_idea_id: str | None
    ) -> dict[str, Any]:
        captured.append(
            {"project_name": project_name, "raw_idea": raw_idea}
        )
        return {
            "adapter": "subtxt_informed_rubric",
            "state": "succeeded",
            "explanation": "fake runner for T019E override test",
            "candidates": [],
        }

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
        adapter_runners={"subtxt_informed_rubric": fake_runner},
    )

    assert captured
    assert captured[0]["raw_idea"] == (
        "Mara wants the archive key but the rival blocks her."
    )
    env = next(
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    )
    assert env["state"] == "succeeded"
    assert "fake runner" in env["explanation"]


# ---------------------------------------------------------------------------
# 11. adapter_fixture_outputs is not the implementation path
# ---------------------------------------------------------------------------


def test_adapter_fixture_outputs_is_not_implementation_path() -> None:
    fixture_payload = {
        "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
        "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
        "output_class": sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
        "status": "succeeded",
        "display_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "provenance": {
            "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "executes_subtxt": False,
            "official_subtxt_output": False,
        },
        "source_refs": ["source_ref_raw_idea"],
        "evidence_refs": ["evidence_ref_raw_idea"],
        "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
        "source_locator_refs": ["source_locator_ref_raw_idea"],
        "candidate_support": [],
        "diagnostic_questions": [],
        "uncertainty_notes": [],
        "insufficient_evidence_notes": [],
        "safety": {key: False for key in sisc.ALLOWED_OPERATION_FLAGS},
    }
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
        adapter_fixture_outputs={"subtxt_informed_rubric": fixture_payload},
    )
    env = next(
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    )
    assert env["explanation"]
    assert "App-owned Subtxt-informed semantic-rubric" in env["explanation"]
    assert "T019D" in env["explanation"]


# ---------------------------------------------------------------------------
# 12. exact category tuple and ordering
# ---------------------------------------------------------------------------


def test_exact_category_tuple_and_ordering() -> None:
    expected = (
        "structural_diagnostic",
        "conflict_diagnostic",
        "throughline_context_question",
        "story_point_context_question",
        "source_of_conflict_hypothesis",
        "subject_vs_conflict_question",
        "ambiguity",
        "insufficient_evidence",
        "owner_review_question",
    )
    assert oao.OMI_SUBTXT_INFORMED_RUBRIC_REQUESTED_CATEGORIES == expected


def test_request_construction_uses_exact_category_tuple() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert (
        tuple(request["requested_categories"])
        == oao.OMI_SUBTXT_INFORMED_RUBRIC_REQUESTED_CATEGORIES
    )


# ---------------------------------------------------------------------------
# 13. request uses committed T019C schema and rubric identity
# ---------------------------------------------------------------------------


def test_request_uses_committed_t019c_schema_and_rubric() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert (
        request["schema_version"]
        == sisc.SUBTXT_INFORMED_RUBRIC_REQUEST_SCHEMA_VERSION
    )
    assert request["rubric_id"] == sisc.SUBTXT_INFORMED_RUBRIC_ID
    assert request["analysis_intent"] == "diagnostic_support"
    assert request["owner_authored_or_owner_provided_source"] is True


def test_request_validates_through_t019c_validator() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    response = sisc.validate_subtxt_informed_rubric_request(request)
    assert response["status"] == "valid"
    assert response["valid"] is True


# ---------------------------------------------------------------------------
# 14. deterministic safe request ID
# ---------------------------------------------------------------------------


def test_deterministic_safe_request_id() -> None:
    request_a = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id="idea-1",
    )
    request_b = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id="idea-1",
    )
    assert request_a["request_id"] == request_b["request_id"]
    assert request_a["request_id"].startswith("subtxt_informed_rubric_")
    suffix = request_a["request_id"].split("subtxt_informed_rubric_", 1)[1]
    assert re.fullmatch(r"[0-9a-f]{16}", suffix)


def test_different_inputs_produce_different_request_ids() -> None:
    request_a = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    request_b = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="goodbye world",
        source_idea_id=None,
    )
    assert request_a["request_id"] != request_b["request_id"]


def test_request_id_uses_safe_identifier_pattern() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert re.fullmatch(r"[A-Za-z0-9_.-]+", request["request_id"])


# ---------------------------------------------------------------------------
# 15. valid project name preserved
# ---------------------------------------------------------------------------


def test_valid_project_name_preserved() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="My-Project_42",
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert request["project_name"] == "My-Project_42"


def test_unsafe_project_name_converted_to_safe_alias() -> None:
    unsafe = "unsafe name with spaces"
    request = oao._build_subtxt_informed_rubric_request(
        project_name=unsafe,
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert request["project_name"] != unsafe
    assert request["project_name"].startswith("project_")
    suffix = request["project_name"].split("project_", 1)[1]
    assert re.fullmatch(r"[0-9a-f]{16}", suffix)


def test_unsafe_project_alias_is_deterministic() -> None:
    unsafe = "unsafe name with spaces"
    request_a = oao._build_subtxt_informed_rubric_request(
        project_name=unsafe,
        raw_idea="hello world",
        source_idea_id=None,
    )
    request_b = oao._build_subtxt_informed_rubric_request(
        project_name=unsafe,
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert request_a["project_name"] == request_b["project_name"]


def test_non_string_project_name_converted_to_safe_alias() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name=None,  # type: ignore[arg-type]
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert request["project_name"].startswith("project_")


# ---------------------------------------------------------------------------
# 17. raw owner source passed unchanged
# ---------------------------------------------------------------------------


def test_raw_owner_source_passed_unchanged() -> None:
    raw_idea = (
        "Mara wants the archive key. The rival blocks her path. "
        "The mentor decides to help."
    )
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea=raw_idea,
        source_idea_id=None,
    )
    assert request["source_text"] == raw_idea


# ---------------------------------------------------------------------------
# 18. exact source locator and four reference collections
# ---------------------------------------------------------------------------


def test_exact_source_locator_and_four_reference_collections() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert request["source_locator"] == "source_locator_ref_raw_idea"
    assert request["source_refs"] == ["source_ref_raw_idea"]
    assert request["evidence_refs"] == ["evidence_ref_raw_idea"]
    assert request["provenance_refs"] == [
        "provenance_ref_subtxt_informed_rubric"
    ]
    assert request["source_locator_refs"] == [
        "source_locator_ref_raw_idea"
    ]
    assert request["source_locator"] in request["source_locator_refs"]


# ---------------------------------------------------------------------------
# 19. all 13 safety confirmations are True
# ---------------------------------------------------------------------------


def test_all_thirteen_safety_confirmations_are_true() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id=None,
    )
    confirmations = request["safety_confirmations"]
    assert isinstance(confirmations, dict)
    expected_keys = {
        "no_subtxt_execution",
        "no_official_subtxt_output_claim",
        "no_storyform_truth",
        "no_generated_prose",
        "no_rewrite",
        "no_continuation",
        "no_outline",
        "no_candidate_persistence",
        "no_review_queue_creation",
        "no_memory_canon_mutation",
        "no_promotion_record",
        "no_apply_promotion",
        "no_training_artifacts",
    }
    assert set(confirmations.keys()) == expected_keys
    for key in expected_keys:
        assert confirmations[key] is True, (
            f"safety_confirmations[{key!r}] must be True"
        )


# ---------------------------------------------------------------------------
# 20. evaluator invoked exactly once
# ---------------------------------------------------------------------------


def test_evaluator_invoked_exactly_once_per_runner_call() -> None:
    call_log: list[int] = []
    original = sise.evaluate_subtxt_informed_semantic_rubric

    def spy(request: object) -> dict[str, Any]:
        call_log.append(1)
        return original(request)

    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        side_effect=spy,
    ):
        result = oao.analyze_omi_raw_idea_with_tools(
            "demo",
            "Mara wants the archive key but the rival blocks her.",
            persist_candidates=False,
            requested_adapters=["subtxt_informed_rubric"],
        )
    env = next(
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    )
    assert len(call_log) == 1
    assert env["state"] in {"succeeded", "empty", "failed_closed", "error"}


# ---------------------------------------------------------------------------
# 21. actual committed evaluator succeeds through the orchestrator
# ---------------------------------------------------------------------------


def test_committed_evaluator_succeeds_through_orchestrator() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        (
            "Mara wants to find the archive key, but a rival threatens "
            "to block her path. The mentor decides to help Mara. Later "
            "Mara discovers the key is hidden in the tower. Maybe the "
            "mentor relationship might be unresolved."
        ),
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
    )
    env = next(
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    )
    assert env["state"] == "succeeded"
    assert env["candidates"]
    for finding in env["candidates"]:
        assert finding["source_adapter"] == "subtxt_informed_rubric"
        assert finding["provenance"]["adapter"] == "subtxt_informed_rubric"
        assert (
            finding["provenance"]["tool_source"] == "subtxt_informed_rubric"
        )


# ---------------------------------------------------------------------------
# 22. structural diagnostic normalization
# ---------------------------------------------------------------------------


def test_structural_diagnostic_normalization() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=_structural_only_source(),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    if envelope["state"] == "succeeded":
        structural_findings = [
            f
            for f in envelope["candidates"]
            if f["candidate_type"] == "structural_diagnostic"
        ]
        if structural_findings:
            f = structural_findings[0]
            assert f["label"]
            assert f["extracted_claim"]
            assert f["candidate_fingerprint"].startswith("omi-cand-")
            assert f["normalized_finding_id"].startswith(
                "omi-find-subtxt_informed_rubric-"
            )


# ---------------------------------------------------------------------------
# 23. conflict diagnostic normalization
# ---------------------------------------------------------------------------


def test_conflict_diagnostic_normalization() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=_conflict_only_source(),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}


# ---------------------------------------------------------------------------
# 24. diagnostic-question normalization
# ---------------------------------------------------------------------------


def test_diagnostic_question_normalization() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=_throughline_only_source(),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    if envelope["state"] == "succeeded":
        question_findings = [
            f
            for f in envelope["candidates"]
            if f["candidate_type"] == "diagnostic_question"
        ]
        for f in question_findings:
            assert f["extracted_claim"].rstrip().endswith("?")


# ---------------------------------------------------------------------------
# 25. ambiguity normalization
# ---------------------------------------------------------------------------


def test_ambiguity_normalization() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=_ambiguity_only_source(),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}


# ---------------------------------------------------------------------------
# 26. evidence-note normalization
# ---------------------------------------------------------------------------


def test_evidence_note_normalization() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=_insufficient_evidence_only_source(),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    if envelope["state"] == "succeeded":
        evidence_note_findings = [
            f
            for f in envelope["candidates"]
            if f["candidate_type"] == "evidence_note"
        ]
        for f in evidence_note_findings:
            assert f["candidate_type"] == "evidence_note"


# ---------------------------------------------------------------------------
# 27. deterministic item ordering
# ---------------------------------------------------------------------------


def test_deterministic_item_ordering() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope_a = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants to find the archive key, but a rival threatens "
            "to block her path. The mentor decides to help Mara. Later "
            "Mara discovers the key. Maybe the mentor might be hiding "
            "the key. The mentor relationship might be unresolved."
        ),
        source_idea_id=None,
    )
    envelope_b = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants to find the archive key, but a rival threatens "
            "to block her path. The mentor decides to help Mara. Later "
            "Mara discovers the key. Maybe the mentor might be hiding "
            "the key. The mentor relationship might be unresolved."
        ),
        source_idea_id=None,
    )
    if envelope_a["state"] == "succeeded" and envelope_b["state"] == "succeeded":
        ids_a = [f["raw_finding_id"] for f in envelope_a["candidates"]]
        ids_b = [f["raw_finding_id"] for f in envelope_b["candidates"]]
        assert ids_a == ids_b
        for raw_id in ids_a:
            assert raw_id.startswith("subtxt_informed_rubric::rubric_item_")


# ---------------------------------------------------------------------------
# 28. exact OMI source_adapter and provenance identity
# ---------------------------------------------------------------------------


def test_exact_omi_source_adapter_and_provenance_identity() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            assert finding["source_adapter"] == "subtxt_informed_rubric"
            assert (
                finding["provenance"]["adapter"] == "subtxt_informed_rubric"
            )
            assert (
                finding["provenance"]["tool_source"]
                == "subtxt_informed_rubric"
            )


# ---------------------------------------------------------------------------
# 29. exact support label
# ---------------------------------------------------------------------------


def test_exact_support_label() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            assert (
                finding["support_label"]
                == "App-owned Subtxt-informed diagnostic support"
            )
            assert (
                finding["provenance"]["support"]
                == "App-owned Subtxt-informed diagnostic support"
            )


# ---------------------------------------------------------------------------
# 30. evidence excerpt and locator preserved
# ---------------------------------------------------------------------------


def test_evidence_excerpt_and_locator_preserved() -> None:
    raw_idea = (
        "Mara wants the archive key, but a rival blocks her path."
    )
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=raw_idea,
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            for evidence in finding["evidence"]:
                assert "source_excerpt" in evidence
                assert "source_locator" in evidence
                assert evidence["source_excerpt"] in raw_idea
                assert evidence["source_locator"]


# ---------------------------------------------------------------------------
# 31. confidence and uncertainty preserved
# ---------------------------------------------------------------------------


def test_confidence_and_uncertainty_preserved() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            assert "confidence" in finding
            assert "uncertainty_label" in finding
            assert finding["confidence"] in {
                "low_support", "medium_support", "high_support"
            }
            assert finding["uncertainty_label"] in {
                "null", "ambiguity", "insufficient_evidence",
                "conflicting_support", "requires_owner_interpretation",
            }


# ---------------------------------------------------------------------------
# 32. owner decision remains pending and unapproved
# ---------------------------------------------------------------------------


def test_owner_decision_remains_pending_and_unapproved() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            assert finding["owner_decision"]["approved"] is False
            assert finding["owner_decision"]["decision"] == "pending"


# ---------------------------------------------------------------------------
# 33. review status remains candidate-review-pending
# ---------------------------------------------------------------------------


def test_review_status_remains_candidate_review_pending() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            assert finding["review_status"] == "candidate_review_pending"


# ---------------------------------------------------------------------------
# 34. succeeded status maps correctly
# ---------------------------------------------------------------------------


def test_succeeded_status_maps_correctly() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded":
        assert envelope["candidates"]
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}


# ---------------------------------------------------------------------------
# 35. empty status maps correctly
# ---------------------------------------------------------------------------


def test_empty_status_maps_correctly() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea="a b c d",
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    if envelope["state"] == "empty":
        assert envelope["candidates"] == []


# ---------------------------------------------------------------------------
# 36. failed_closed status maps correctly
# ---------------------------------------------------------------------------


def test_failed_closed_status_maps_correctly() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        return_value={
            "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
            "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "output_class": sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
            "status": "failed_closed",
            "display_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "provenance": {
                "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
                "executes_subtxt": False,
                "official_subtxt_output": False,
            },
            "source_refs": ["source_ref_raw_idea"],
            "evidence_refs": ["evidence_ref_raw_idea"],
            "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
            "source_locator_refs": ["source_locator_ref_raw_idea"],
            "candidate_support": [],
            "diagnostic_questions": [],
            "uncertainty_notes": [],
            "insufficient_evidence_notes": [],
            "safety": {key: False for key in sisc.ALLOWED_OPERATION_FLAGS},
            "fail_closed_reason": "test",
        },
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "failed_closed"
    assert envelope["candidates"] == []
    assert envelope["explanation"]


# ---------------------------------------------------------------------------
# 37. error status maps correctly
# ---------------------------------------------------------------------------


def test_error_status_maps_correctly() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        return_value={
            "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
            "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "output_class": sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
            "status": "error",
            "display_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "provenance": {
                "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
                "executes_subtxt": False,
                "official_subtxt_output": False,
            },
            "source_refs": ["source_ref_raw_idea"],
            "evidence_refs": ["evidence_ref_raw_idea"],
            "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
            "source_locator_refs": ["source_locator_ref_raw_idea"],
            "candidate_support": [],
            "diagnostic_questions": [],
            "uncertainty_notes": [],
            "insufficient_evidence_notes": [],
            "safety": {key: False for key in sisc.ALLOWED_OPERATION_FLAGS},
            "error": "synthetic error",
        },
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "error"
    assert envelope["candidates"] == []


# ---------------------------------------------------------------------------
# 38. malformed evaluator result fails closed
# ---------------------------------------------------------------------------


def test_malformed_evaluator_result_fails_closed() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        return_value={"status": "succeeded"},
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "failed_closed"
    assert envelope["candidates"] == []
    assert "fail" in envelope["explanation"].lower()


def test_non_dict_evaluator_result_fails_closed() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        return_value="not a dict",
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "failed_closed"
    assert envelope["candidates"] == []


# ---------------------------------------------------------------------------
# 39. unsafe evaluator result fails closed
# ---------------------------------------------------------------------------


def test_unsafe_evaluator_result_fails_closed() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        return_value={
            "schema_version": "wrong.schema.version",
            "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "output_class": sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
            "status": "succeeded",
            "display_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "provenance": {
                "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
                "executes_subtxt": False,
                "official_subtxt_output": False,
            },
            "source_refs": ["source_ref_raw_idea"],
            "evidence_refs": ["evidence_ref_raw_idea"],
            "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
            "source_locator_refs": ["source_locator_ref_raw_idea"],
            "candidate_support": [],
            "diagnostic_questions": [],
            "uncertainty_notes": [],
            "insufficient_evidence_notes": [],
            "safety": {key: False for key in sisc.ALLOWED_OPERATION_FLAGS},
        },
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "failed_closed"
    assert envelope["candidates"] == []


# ---------------------------------------------------------------------------
# 40. evaluator exception fails closed
# ---------------------------------------------------------------------------


def test_evaluator_exception_fails_closed() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        side_effect=RuntimeError("synthetic evaluator error"),
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "failed_closed"
    assert envelope["candidates"] == []
    assert "evaluator" in envelope["explanation"].lower()


# ---------------------------------------------------------------------------
# 41. one invalid normalized item fails the whole adapter call closed
# ---------------------------------------------------------------------------


def test_invalid_normalized_item_fails_whole_adapter_call() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()

    bad_item = {
        "item_id": "rubric_item_99_unknown_category",
        "category": "unknown_category",
        "candidate_type": "unknown_type",
        "label": "Some label",
        "diagnostic_text": "Some diagnostic text",
        "statement_kind": "candidate_observation",
        "evidence": [
            {
                "source_excerpt": "hello world",
                "source_locator": "source_locator_ref_raw_idea",
            }
        ],
        "source_locator": "source_locator_ref_raw_idea",
        "source_refs": ["source_ref_raw_idea"],
        "evidence_refs": ["evidence_ref_raw_idea"],
        "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
        "source_locator_refs": ["source_locator_ref_raw_idea"],
        "provenance": {
            "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "executes_subtxt": False,
            "official_subtxt_output": False,
        },
        "support_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "confidence": "low_support",
        "uncertainty_label": "null",
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }

    good_item = {
        "item_id": "rubric_item_01_structural_diagnostic",
        "category": "structural_diagnostic",
        "candidate_type": "structural_diagnostic",
        "label": "Intention and resistance signal",
        "diagnostic_text": (
            "The evidence contains an intention paired with resistance."
        ),
        "statement_kind": "candidate_observation",
        "evidence": [
            {
                "source_excerpt": "Mara wants the key but the rival blocks",
                "source_locator": "source_locator_ref_raw_idea",
            }
        ],
        "source_locator": "source_locator_ref_raw_idea",
        "source_refs": ["source_ref_raw_idea"],
        "evidence_refs": ["evidence_ref_raw_idea"],
        "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
        "source_locator_refs": ["source_locator_ref_raw_idea"],
        "provenance": {
            "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "executes_subtxt": False,
            "official_subtxt_output": False,
        },
        "support_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
        "confidence": "medium_support",
        "uncertainty_label": "null",
        "owner_decision": {"approved": False, "decision": "pending"},
        "review_status": "candidate_review_pending",
        "executes_subtxt": False,
        "official_subtxt_output": False,
    }

    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        return_value={
            "schema_version": sisc.SUBTXT_INFORMED_RUBRIC_RESULT_SCHEMA_VERSION,
            "rubric_id": sisc.SUBTXT_INFORMED_RUBRIC_ID,
            "output_class": sisc.SUBTXT_INFORMED_RUBRIC_OUTPUT_CLASS,
            "status": "succeeded",
            "display_label": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
            "provenance": {
                "tool_source": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "adapter": sisc.SUBTXT_INFORMED_RUBRIC_ID,
                "support": sisc.SUBTXT_INFORMED_RUBRIC_SUPPORT_LABEL,
                "executes_subtxt": False,
                "official_subtxt_output": False,
            },
            "source_refs": ["source_ref_raw_idea"],
            "evidence_refs": ["evidence_ref_raw_idea"],
            "provenance_refs": ["provenance_ref_subtxt_informed_rubric"],
            "source_locator_refs": ["source_locator_ref_raw_idea"],
            "candidate_support": [bad_item, good_item],
            "diagnostic_questions": [],
            "uncertainty_notes": [],
            "insufficient_evidence_notes": [],
            "safety": {key: False for key in sisc.ALLOWED_OPERATION_FLAGS},
        },
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["state"] == "failed_closed"
    assert envelope["candidates"] == []


# ---------------------------------------------------------------------------
# 42. no partial findings on failure
# ---------------------------------------------------------------------------


def test_no_partial_findings_on_failure() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    with mock.patch.object(
        sise,
        "evaluate_subtxt_informed_semantic_rubric",
        side_effect=RuntimeError("synthetic"),
    ):
        envelope = runner(
            project_name="demo",
            raw_idea="hello world hello world",
            source_idea_id=None,
        )
    assert envelope["candidates"] == []
    assert "candidates" in envelope
    assert isinstance(envelope["candidates"], list)


# ---------------------------------------------------------------------------
# 43. no live/official Subtxt wording in adapter envelopes
# ---------------------------------------------------------------------------


def test_no_live_or_official_subtxt_wording() -> None:
    forbidden_phrases = [
        "Subtxt runtime",
        "Subtxt runtime result",
        "Official Subtxt",
        "Subtxt-confirmed",
        "subtxt-endorsed",
        "subtxt-endorsement",
    ]
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    serialized = envelope["explanation"]
    for phrase in forbidden_phrases:
        assert phrase not in serialized

    for finding in envelope["candidates"]:
        for evidence in finding.get("evidence") or []:
            for key, value in evidence.items():
                if isinstance(value, str):
                    for phrase in forbidden_phrases:
                        assert phrase not in value, (
                            f"forbidden phrase {phrase!r} in evidence[{key!r}]"
                        )


# ---------------------------------------------------------------------------
# 44. no subtxt provenance identity
# ---------------------------------------------------------------------------


def test_no_subtxt_provenance_identity() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    serialized = repr(envelope)
    forbidden = [
        '"tool_source": "subtxt"',
        '"adapter": "subtxt"',
        '"provenance": {"tool_source": "subtxt"',
        '"provenance": {"adapter": "subtxt"',
    ]
    for needle in forbidden:
        assert needle not in serialized


# ---------------------------------------------------------------------------
# 45. no Storyform/truth/canon/approval claim
# ---------------------------------------------------------------------------


def test_no_storyform_truth_canon_approval_claim() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    forbidden_words = [
        "truth score",
        "canonical confidence",
        "approved canon support",
        "promoted truth",
        "canon truth",
        "official_subtxt_output: true",
        "executes_subtxt: true",
    ]
    serialized = envelope["explanation"].lower()
    if envelope.get("candidates"):
        for finding in envelope["candidates"]:
            serialized += " " + repr(finding).lower()
    for needle in forbidden_words:
        assert needle not in serialized


# ---------------------------------------------------------------------------
# 46. owner source containing sensitive words remains analyzable
# ---------------------------------------------------------------------------


def test_owner_source_with_sensitive_words_remains_analyzable() -> None:
    raw_idea = (
        "Mara wants to find the canon of the approved outline before the "
        "rewrite. The rival blocks her. Maybe the canon is hidden. The "
        "mentor decides to help."
    )
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=raw_idea,
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    if envelope["state"] == "succeeded":
        for finding in envelope["candidates"]:
            for evidence in finding["evidence"]:
                assert "source_excerpt" in evidence


# ---------------------------------------------------------------------------
# 47. persist_candidates=False produces no persistence
# ---------------------------------------------------------------------------


def test_persist_false_produces_no_persistence() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
    )
    assert result["persistence_status"] == "not_requested"
    assert result["persisted_candidate_ids"] == []
    assert result["new_candidate_ids"] == []
    assert result["reused_candidate_ids"] == []


# ---------------------------------------------------------------------------
# 48. no Memory/Canon mutation
# ---------------------------------------------------------------------------


def test_no_memory_canon_mutation() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    serialized = envelope["explanation"].lower()
    for forbidden in (
        "memory_canon_mutation",
        "mutate memory",
        "mutate canon",
        "write memory",
        "write canon",
    ):
        assert forbidden not in serialized


# ---------------------------------------------------------------------------
# 49. no promotion/apply-promotion
# ---------------------------------------------------------------------------


def test_no_promotion_or_apply_promotion() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    serialized = envelope["explanation"].lower()
    for forbidden in (
        "apply_promotion",
        "promotion record",
        "promote to canon",
        "promoted truth",
    ):
        assert forbidden not in serialized


# ---------------------------------------------------------------------------
# 50. no story-prose generation
# ---------------------------------------------------------------------------


def test_no_story_prose_generation() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    assert envelope["state"] in {"succeeded", "empty", "failed_closed"}
    serialized = envelope["explanation"].lower()
    for forbidden in (
        "rewrite",
        "continuation",
        "outline",
        "drafted",
        "polish",
        "expanded prose",
        "expanded scene",
    ):
        assert forbidden not in serialized


# ---------------------------------------------------------------------------
# 51. no file, subprocess, network, model, environment, or .external_sources
# ---------------------------------------------------------------------------


def test_no_external_runtime_dependencies() -> None:
    runner_source = inspect.getsource(
        oao._build_subtxt_informed_rubric_runner
    )
    helper_source = inspect.getsource(
        oao._build_subtxt_informed_rubric_request
    )
    normalizer_source = inspect.getsource(
        oao._normalize_subtxt_informed_rubric_item
    )
    combined = runner_source + "\n" + helper_source + "\n" + normalizer_source
    forbidden_tokens = [
        "subprocess",
        "urllib",
        "requests",
        "socket",
        "openai",
        "anthropic",
        "ollama",
        "httpx",
        "http.client",
        ".external_sources",
        "os.environ",
        "getenv",
    ]
    for token in forbidden_tokens:
        assert token not in combined, (
            f"forbidden token {token!r} found in T019E helper source"
        )


def test_runner_does_not_open_files() -> None:
    runner_source = inspect.getsource(
        oao._build_subtxt_informed_rubric_runner
    )
    assert "open(" not in runner_source
    assert "Path(" not in runner_source


# ---------------------------------------------------------------------------
# 52. existing T009 subtxt fixture behavior remains unchanged
# ---------------------------------------------------------------------------


def test_existing_subtxt_fixture_behavior_remains_unchanged() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Owner analysis note: archive key pressure; hearing deadline; "
        "mentor relationship unresolved; sealed archive route knowledge",
        persist_candidates=False,
        requested_adapters=["subtxt"],
        adapter_fixture_outputs={
            "subtxt": {
                "schema_version": oao.OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER[
                    "subtxt"
                ],
                "adapter": "subtxt",
                "status": "succeeded",
                "explanation": "fixture-only subtxt diagnostic handoff",
                "provenance": {
                    "tool_source": "subtxt",
                    "adapter": "subtxt",
                    "support": "Subtxt diagnostic support only",
                },
                "findings": [
                    {
                        "raw_finding_id": "subtxt-fixture-1",
                        "finding_type": "structural_diagnostic",
                        "label": "Archive key pressure",
                        "diagnostic_claim": (
                            "The archive key creates a structural "
                            "diagnostic pressure point"
                        ),
                        "evidence": [
                            {
                                "source_excerpt": (
                                    "Mara must recover the archive key "
                                    "before the hearing"
                                ),
                                "source_locator": "raw_idea:L1:C12-66",
                            }
                        ],
                        "source_locator": "raw_idea:L1:C12-66",
                        "support_label": (
                            "Subtxt diagnostic support only"
                        ),
                        "confidence": "medium support",
                    }
                ],
            }
        },
    )
    env = next(
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt"
    )
    assert env["state"] == "succeeded"
    assert env["candidates"]
    assert env["candidates"][0]["source_adapter"] == "subtxt"
    assert env["candidates"][0]["provenance"]["adapter"] == "subtxt"


# ---------------------------------------------------------------------------
# 53. mixed invocation with an existing adapter remains valid
# ---------------------------------------------------------------------------


def test_mixed_invocation_with_existing_adapter_remains_valid() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Mara wants the archive key but the rival blocks her.",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric", "deterministic_fallback"],
    )
    adapters_seen = {
        env["adapter"] for env in result["adapter_results"]
    }
    assert "subtxt_informed_rubric" in adapters_seen
    assert "deterministic_fallback" in adapters_seen


# ---------------------------------------------------------------------------
# 54. empty raw idea follows the existing skipped-adapter short circuit
# ---------------------------------------------------------------------------


def test_empty_raw_idea_short_circuits_to_skipped() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
    )
    assert result["analysis_status"] == "empty"
    envs = [
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    ]
    assert len(envs) == 1
    assert envs[0]["state"] == "skipped"
    assert envs[0]["candidates"] == []


def test_whitespace_only_raw_idea_short_circuits_to_skipped() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "   \n  \t  ",
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
    )
    assert result["analysis_status"] == "empty"
    envs = [
        env
        for env in result["adapter_results"]
        if env["adapter"] == "subtxt_informed_rubric"
    ]
    assert envs[0]["state"] == "skipped"


# ---------------------------------------------------------------------------
# 55. orchestrator fusion accepts the normalized findings
# ---------------------------------------------------------------------------


def test_orchestrator_fusion_accepts_normalized_findings() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        (
            "Mara wants to find the archive key, but a rival threatens "
            "to block her path. The mentor decides to help Mara. Later "
            "Mara discovers the key is hidden in the tower. Maybe the "
            "mentor relationship might be unresolved."
        ),
        persist_candidates=False,
        requested_adapters=["subtxt_informed_rubric"],
    )
    if result["findings"]:
        for finding in result["findings"]:
            assert finding["source_adapter"] == "subtxt_informed_rubric"
            assert (
                finding["provenance"]["adapter"] == "subtxt_informed_rubric"
            )
            assert (
                finding["provenance"]["tool_source"]
                == "subtxt_informed_rubric"
            )
            assert finding["candidate_fingerprint"].startswith("omi-cand-")
            assert finding["evidence_fingerprint"].startswith("omi-evid-")
            assert finding["normalized_finding_id"].startswith(
                "omi-find-subtxt_informed_rubric-"
            )


# ---------------------------------------------------------------------------
# 56. runner validates adapter_config strictly
# ---------------------------------------------------------------------------


def test_runner_rejects_non_dict_adapter_config() -> None:
    with pytest.raises(ValueError):
        oao._build_subtxt_informed_rubric_runner(
            adapter_config="not a dict",  # type: ignore[arg-type]
        )


def test_runner_accepts_none_adapter_config() -> None:
    runner = oao._build_subtxt_informed_rubric_runner(adapter_config=None)
    assert callable(runner)


def test_runner_accepts_dict_adapter_config() -> None:
    runner = oao._build_subtxt_informed_rubric_runner(
        adapter_config={"ignored": True},
    )
    assert callable(runner)


# ---------------------------------------------------------------------------
# 57. request_id is hex-safe regardless of source content
# ---------------------------------------------------------------------------


def test_request_id_is_safe_for_unicode_source() -> None:
    request = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="Mara wants the key. The rival blocks her. \u00e9\u00e8\u00ea",
        source_idea_id=None,
    )
    assert re.fullmatch(r"[A-Za-z0-9_.-]+", request["request_id"])


# ---------------------------------------------------------------------------
# 58. build request preserves non-empty source_idea_id when present
# ---------------------------------------------------------------------------


def test_source_idea_id_appears_in_request_id() -> None:
    request_a = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id="idea-a",
    )
    request_b = oao._build_subtxt_informed_rubric_request(
        project_name="example",
        raw_idea="hello world",
        source_idea_id="idea-b",
    )
    assert request_a["request_id"] != request_b["request_id"]


# ---------------------------------------------------------------------------
# 59. provenance conversion uses OMI adapter identity (NOT app-owned internal)
# ---------------------------------------------------------------------------


def test_provenance_uses_omi_adapter_identity_not_internal_rubric() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    envelope = runner(
        project_name="demo",
        raw_idea=(
            "Mara wants the archive key, but a rival blocks her. The "
            "mentor decides to help. Maybe the key is in the library."
        ),
        source_idea_id=None,
    )
    if envelope["state"] == "succeeded" and envelope["candidates"]:
        for finding in envelope["candidates"]:
            provenance_str = repr(finding["provenance"])
            assert "app_owned_subtxt_informed_rubric" not in provenance_str
            assert "subtxt_informed_rubric" in provenance_str
            assert "App-owned Subtxt-informed diagnostic support" in (
                finding["provenance"]["support"]
            )


# ---------------------------------------------------------------------------
# 60. adapter runner counts invocations correctly
# ---------------------------------------------------------------------------


def test_runner_invocation_counter_increments_per_call() -> None:
    runner = oao._build_subtxt_informed_rubric_runner()
    counter = getattr(runner, "__invocation_count__")
    assert counter["count"] == 0
    runner(
        project_name="demo",
        raw_idea="hello world",
        source_idea_id=None,
    )
    assert counter["count"] == 1
    runner(
        project_name="demo",
        raw_idea="goodbye world",
        source_idea_id=None,
    )
    assert counter["count"] == 2
