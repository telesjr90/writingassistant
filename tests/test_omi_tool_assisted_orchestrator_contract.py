"""Tests for PHASE8-IMPL-023-T005: OMI AI/tool-assisted orchestrator contract.

These tests verify the orchestrator contract and adapter-boundary scaffold
**without** performing any real Ollama/model/Story Check/BookNLP/spaCy/
NCP/Subtxt/dramatica-flow runtime call, without mutating Memory/Canon, without
running or enabling apply-promotion, and without generating story prose.

Tests in this file exercise the orchestrator through stub/mock adapters
plus the real ``deterministic_fallback`` wiring to the existing T004
deterministic marker extractor (which is fallback/safety baseline only).

Boundaries:

  - analysis-only
  - candidate-first, evidence/provenance-backed, owner-controlled
  - candidate persistence is not canon; queue presence is not approval
  - support/confidence is support only, not truth
  - tool/model output is never canon/approval
  - no Memory/Canon mutation
  - no apply-promotion
  - no story prose generation, no rewrite, no continuation, no drafting,
    no polish, no improvement, no expansion, no imitation, no revision
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Adapter stub adapters used by several tests
# ---------------------------------------------------------------------------


REQUIRED_ADAPTERS = {
    "ollama_model",
    "story_check",
    "booknlp",
    "spacy",
    "ncp",
    "subtxt",
    "dramatica_flow",
    "deterministic_fallback",
}


def _stub_valid_finding(
    *,
    candidate_type: str = "character",
    label: str = "Test Character Alpha",
    extracted_claim: str = (
        "Test Character Alpha appears in the raw idea as the primary "
        "investigator of the lost object."
    ),
    source_adapter: str = "ollama_model",
    support_label: str = "stub adapter support strength only",
) -> dict:
    return {
        "candidate_type": candidate_type,
        "label": label,
        "extracted_claim": extracted_claim,
        "evidence": [
            {
                "source_excerpt": "Test Character Alpha walks into the library.",
                "source_locator": "raw_idea:3",
            }
        ],
        "source_locator": "raw_idea:3",
        "provenance": {
            "tool_source": source_adapter,
            "adapter": source_adapter,
            "support": "stub adapter support strength only",
        },
        "source_adapter": source_adapter,
        "support_label": support_label,
        "owner_decision": {"decision": "pending", "approved": False},
        "review_status": "candidate_review_pending",
        "raw_finding_id": "stub-finding-1",
    }


# ---------------------------------------------------------------------------
# Test 1: orchestrator declares required adapter identities
# ---------------------------------------------------------------------------


def test_orchestrator_declares_required_adapter_identities() -> None:
    assert oao.OMI_TOOL_ADAPTER_IDENTITIES == REQUIRED_ADAPTERS

    # adapter_contract validates identities
    for identity in REQUIRED_ADAPTERS:
        contract = oao.adapter_contract(identity)
        assert contract["behavior"]
        assert isinstance(contract["produces_candidates"], bool)
        assert isinstance(contract["supports_finding_types"], (tuple, list, frozenset))

    # Unknown identity raises
    with pytest.raises(ValueError):
        oao.adapter_contract("not_a_real_adapter")


def test_orchestrator_declares_adapter_result_states() -> None:
    expected_states = {
        "succeeded",
        "empty",
        "skipped",
        "unavailable",
        "failed_closed",
        "error",
    }
    assert oao.OMI_ADAPTER_RESULT_STATES == expected_states


# ---------------------------------------------------------------------------
# Test 2: unimplemented adapters fail closed without fake candidates
# ---------------------------------------------------------------------------


def test_unimplemented_adapters_fail_closed_without_fake_candidates() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "A short non-empty raw idea without supported marker lines.",
        persist_candidates=False,
        allow_deterministic_fallback=False,
    )

    # All 7 AI/tool adapters are stubbed at T005; every one is unavailable
    # with an explanation, and the orchestrator returns fail_closed.
    adapters_seen = {env["adapter"] for env in result["adapter_results"]}
    assert "ollama_model" in adapters_seen
    assert "story_check" in adapters_seen
    assert "booknlp" in adapters_seen
    assert "spacy" in adapters_seen
    assert "ncp" in adapters_seen
    assert "subtxt" in adapters_seen
    assert "dramatica_flow" in adapters_seen

    # No fake findings were produced.
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []

    for env in result["adapter_results"]:
        assert env["state"] != "succeeded"
        assert env["candidates"] == []
        assert env["explanation"]


def test_stub_adapter_result_rejects_succeeded_state() -> None:
    # stub helpers must never pretend an unimplemented adapter succeeded
    with pytest.raises(ValueError):
        oao.stub_adapter_result("ollama_model", state="succeeded")
    # stub helpers reject unknown identities
    with pytest.raises(ValueError):
        oao.stub_adapter_result("not_a_real_adapter", state="unavailable")


def test_adapter_envelope_validates_state_and_candidates_shape() -> None:
    # State must be one of OMI_ADAPTER_RESULT_STATES
    with pytest.raises(ValueError):
        oao.validate_adapter_result(
            {
                "adapter": "ollama_model",
                "state": "not_a_state",
                "explanation": "x",
                "candidates": [],
            }
        )
    # Non-succeeded states must carry empty candidate list
    with pytest.raises(ValueError):
        oao.validate_adapter_result(
            {
                "adapter": "ollama_model",
                "state": "unavailable",
                "explanation": "x",
                "candidates": [_stub_valid_finding()],
            }
        )
    # succeeded without findings is allowed at envelope shape level
    ok = oao.validate_adapter_result(
        {
            "adapter": "ollama_model",
            "state": "succeeded",
            "explanation": "ok",
            "candidates": [],
        }
    )
    assert ok["state"] == "succeeded"
    # succeeded with findings is valid
    ok2 = oao.validate_adapter_result(
        {
            "adapter": "ollama_model",
            "state": "succeeded",
            "explanation": "ok",
            "candidates": [_stub_valid_finding()],
        }
    )
    assert ok2["state"] == "succeeded"
    assert len(ok2["candidates"]) == 1


# ---------------------------------------------------------------------------
# Test 3: normalized findings require evidence, source_locator, provenance
# ---------------------------------------------------------------------------


def test_normalized_findings_require_evidence_source_locator_and_provenance() -> None:
    finding = _stub_valid_finding()
    normalized = oao.validate_normalized_finding(finding)
    assert normalized["evidence"]
    assert normalized["source_locator"]
    assert normalized["provenance"]["tool_source"]
    assert normalized["provenance"]["adapter"]
    assert normalized["provenance"]["support"]

    # Empty evidence is rejected
    bad = dict(finding)
    bad["evidence"] = []
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad)

    # Evidence item without source_excerpt/source_locator is rejected
    bad2 = dict(finding)
    bad2["evidence"] = [{"note": "no locator here"}]
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad2)

    # Missing source_locator is rejected
    bad3 = dict(finding)
    bad3["source_locator"] = ""
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad3)

    # Provenance missing required fields is rejected
    bad4 = dict(finding)
    bad4["provenance"] = {"tool_source": "stub_adapter", "adapter": "stub_adapter"}
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad4)


def test_normalized_finding_rejects_unknown_candidate_type() -> None:
    bad = _stub_valid_finding(candidate_type="story_prose_output")
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad)


def test_normalized_finding_requires_source_adapter_match_provenance() -> None:
    bad = _stub_valid_finding()
    bad["source_adapter"] = "different_adapter"
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad)


# ---------------------------------------------------------------------------
# Test 4: unsafe prose output is rejected
# ---------------------------------------------------------------------------


def test_unsafe_prose_output_is_rejected() -> None:
    finding = _stub_valid_finding(
        extracted_claim=(
            "Meanwhile the room grew dark as the rain hammered the windows "
            "and the candles flickered one by one down the long hallway."
        )
    )
    with pytest.raises(ValueError) as exc_info:
        oao.validate_normalized_finding(finding)
    assert "prose" in str(exc_info.value).lower() or "failed_closed" in str(
        exc_info.value
    ).lower()

    # Orchestrator-level: prose-shaped raw_idea fails closed before any run
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Meanwhile the room grew dark as the rain hammered the windows and "
        "the candles flickered one by one down the long hallway, which seemed "
        "to stretch for miles into the night and beyond.",
        persist_candidates=True,
        allow_deterministic_fallback=True,
    )
    assert result["analysis_status"] == "fail_closed"
    assert result["findings"] == []
    assert result["persisted_candidate_ids"] == []


def test_prose_guard_helper_detects_narrative_shapes() -> None:
    assert oao.is_prose_like_text(
        '"Stop!" he shouted, brandishing the lantern at the figure.'
    )
    assert oao.is_prose_like_text(
        "Meanwhile the room grew dark and the rain hammered the windows "
        "and the candles flickered one by one down the long hallway."
    )
    assert not oao.is_prose_like_text("Character: Test Character Alpha.")
    assert not oao.is_prose_like_text("Test Character Alpha")


# ---------------------------------------------------------------------------
# Test 5: stub adapter candidate is normalized as candidate, never as canon
# ---------------------------------------------------------------------------


def test_stub_adapter_candidate_is_normalized_as_candidate_only_not_canon() -> None:
    # Drive the orchestrator with a synthetic adapter-result envelope that
    # succeeded with one valid candidate through the test-only runner
    # injection point.
    captured: list[dict] = []

    def fake_runner(*, project_name, raw_idea, source_idea_id):
        captured.append({"project_name": project_name})
        return {
            "adapter": "ollama_model",
            "state": "succeeded",
            "explanation": "fake runner for tests",
            "candidates": [_stub_valid_finding(source_adapter="ollama_model")],
        }

    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Raw idea under analysis with character mention by name.",
        persist_candidates=False,
        requested_adapters=["ollama_model"],
        adapter_runners={"ollama_model": fake_runner},
    )

    assert captured, "fake runner should have been invoked exactly once"
    assert result["analysis_status"] == "succeeded"
    assert len(result["findings"]) == 1
    normalized = result["findings"][0]

    # Finding is review-pending, never approved/canon/promoted
    assert normalized["owner_decision"]["decision"] == "pending"
    assert normalized["owner_decision"]["approved"] is False
    assert normalized["review_status"] == "candidate_review_pending"

    # Required fields are all present
    for required in oao.OMI_NORMALIZED_FINDING_REQUIRED_FIELDS:
        assert required in normalized, f"missing {required}"
    assert normalized["candidate_fingerprint"].startswith("omi-cand-")

    # persisted_candidate_ids stays empty because persist_candidates=False
    assert result["persisted_candidate_ids"] == []


# ---------------------------------------------------------------------------
# Test 6: support/confidence is not truth
# ---------------------------------------------------------------------------


def test_tool_output_support_confidence_is_not_truth() -> None:
    finding = _stub_valid_finding(support_label="truth score 0.99 — confirmed_fact")
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(finding)

    canonical = _stub_valid_finding(support_label="canonical confidence score")
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(canonical)

    approved = _stub_valid_finding(support_label="approved canon support")
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(approved)

    promoted = _stub_valid_finding(support_label="promoted truth reading")
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(promoted)

    # Provenance.support also rejects truth-shaped labels
    bad_prov = _stub_valid_finding()
    bad_prov["provenance"] = {
        "tool_source": "stub_adapter",
        "adapter": "stub_adapter",
        "support": "canonical truth score",
    }
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad_prov)

    # A label containing the word "support" without truth labels is fine.
    ok = oao.validate_normalized_finding(_stub_valid_finding())
    assert ok["support_label"]


def test_normalized_finding_rejects_auto_approved_owner_decision() -> None:
    bad = _stub_valid_finding()
    bad["owner_decision"] = {"decision": "approve", "approved": True}
    with pytest.raises(ValueError):
        oao.validate_normalized_finding(bad)


def test_is_truth_label_helper_distinguishes_support_from_truth() -> None:
    assert oao.is_truth_label("canonical truth score")
    assert oao.is_truth_label("approved fact")
    assert oao.is_truth_label("promoted to canon")
    assert not oao.is_truth_label("support strength only")
    assert not oao.is_truth_label("deterministic fallback support")


# ---------------------------------------------------------------------------
# Test 7: orchestrator does not call real tools by default
# ---------------------------------------------------------------------------


def test_orchestrator_does_not_call_real_tools_by_default() -> None:
    import backend.project_manager as project_manager

    # Stub the inner project_manager call to assert it is NEVER invoked
    # from this orchestrator path with persist_candidates=False.
    original_extract = project_manager.extract_omi_candidates_from_raw_idea
    call_log: list[dict] = []

    def spy_extract(project_name, raw_idea, **kwargs):
        call_log.append({"project_name": project_name, "raw_idea": raw_idea})
        return original_extract(project_name, raw_idea, **kwargs)

    project_manager.extract_omi_candidates_from_raw_idea = spy_extract
    try:
        result = oao.analyze_omi_raw_idea_with_tools(
            "demo",
            "Plain non-empty raw idea without markers.",
            persist_candidates=False,
            allow_deterministic_fallback=False,
        )
    finally:
        project_manager.extract_omi_candidates_from_raw_idea = original_extract

    assert result["analysis_status"] == "fail_closed"
    assert call_log == [], (
        "deterministic_fallback is opt-in; the orchestrator must NOT call "
        "extract_omi_candidates_from_raw_idea unless "
        "allow_deterministic_fallback=True"
    )


def test_deterministic_fallback_is_wired_only_when_opted_in() -> None:
    import backend.project_manager as project_manager

    original_extract = project_manager.extract_omi_candidates_from_raw_idea
    call_log: list[dict] = []

    def spy_extract(project_name, raw_idea, **kwargs):
        call_log.append({"project_name": project_name})
        return original_extract(project_name, raw_idea, **kwargs)

    project_manager.extract_omi_candidates_from_raw_idea = spy_extract
    try:
        oao.analyze_omi_raw_idea_with_tools(
            "demo",
            "Plain non-empty raw idea without markers.",
            persist_candidates=False,
            allow_deterministic_fallback=False,
        )
        assert call_log == [], "deterministic_fallback must not run by default"

        oao.analyze_omi_raw_idea_with_tools(
            "demo",
            "Plain non-empty raw idea without markers.",
            persist_candidates=False,
            allow_deterministic_fallback=True,
        )
        # deterministic_fallback wired ONCE even though persist_candidates=False
        # (orchestrator runs the fallback to discover findings).
        assert len(call_log) == 1
    finally:
        project_manager.extract_omi_candidates_from_raw_idea = original_extract


# ---------------------------------------------------------------------------
# Test 8: deterministic_fallback is marked fallback-only
# ---------------------------------------------------------------------------


def test_deterministic_fallback_is_marked_fallback_only() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "\n".join(
            [
                "Character: Test Character Alpha.",
                "Location: Test Location Beta.",
                "Organization: Test Group Gamma.",
            ]
        ),
        persist_candidates=False,
        allow_deterministic_fallback=True,
    )

    fallback_envs = [
        env for env in result["adapter_results"]
        if env["adapter"] == "deterministic_fallback"
    ]
    assert len(fallback_envs) == 1
    fallback_env = fallback_envs[0]
    assert fallback_env["adapter"] == "deterministic_fallback"
    assert fallback_env.get("fallback_only") is True, (
        "deterministic_fallback must be marked fallback_only at the "
        "adapter-envelope level"
    )
    assert "fallback" in fallback_env["explanation"].lower() or "baseline" in (
        fallback_env["explanation"].lower()
    )

    for finding in result["findings"]:
        if finding.get("fallback_marker"):
            assert finding["source_adapter"] == "deterministic_fallback"
            assert "support" in finding["support_label"].lower()
            assert finding["review_status"] == "candidate_review_pending"
            assert finding["owner_decision"]["decision"] == "pending"
            assert finding["owner_decision"]["approved"] is False


def test_deterministic_fallback_returns_empty_for_unsupported_input() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Plain prose-style raw idea with no explicit markers like this one.",
        persist_candidates=False,
        allow_deterministic_fallback=True,
    )

    fallback_envs = [
        env for env in result["adapter_results"]
        if env["adapter"] == "deterministic_fallback"
    ]
    assert len(fallback_envs) == 1
    fallback_env = fallback_envs[0]
    assert fallback_env["state"] in {"succeeded", "empty", "fail_closed"}
    if fallback_env["state"] != "succeeded":
        # Empty / fail_closed is fine; either way orchestrator never invents
        # candidates, which is what matters.
        assert fallback_env["candidates"] == []
        assert result["findings"] == []
        assert result["persisted_candidate_ids"] == []


# ---------------------------------------------------------------------------
# Additional safety boundary tests
# ---------------------------------------------------------------------------


def test_orchestrator_rejects_empty_project_name() -> None:
    with pytest.raises(ValueError):
        oao.analyze_omi_raw_idea_with_tools("", "non-empty idea")
    with pytest.raises(ValueError):
        oao.analyze_omi_raw_idea_with_tools("  ", "non-empty idea")


def test_orchestrator_rejects_non_string_raw_idea() -> None:
    with pytest.raises(ValueError):
        oao.analyze_omi_raw_idea_with_tools("demo", None)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        oao.analyze_omi_raw_idea_with_tools("demo", 123)  # type: ignore[arg-type]


def test_orchestrator_rejects_non_bool_persist_candidates() -> None:
    with pytest.raises(ValueError):
        oao.analyze_omi_raw_idea_with_tools(
            "demo", "non-empty", persist_candidates="yes"  # type: ignore[arg-type]
        )


def test_orchestrator_rejects_unknown_requested_adapter() -> None:
    with pytest.raises(ValueError):
        oao.analyze_omi_raw_idea_with_tools(
            "demo",
            "non-empty raw idea",
            requested_adapters=["fake_llm_adapter"],
        )


def test_safety_envelope_is_static_and_safe() -> None:
    envelope = oao.build_orchestrator_safety_envelope()
    assert envelope["no_prose"] is True
    assert envelope["no_memory_canon_mutation"] is True
    assert envelope["no_apply_promotion"] is True
    assert envelope["no_canon_promotion"] is True
    assert envelope["no_real_tool_calls"] is True
    assert envelope["no_package_installs"] is True
    assert envelope["no_story_prose_generation"] is True
    assert envelope["candidate_presence_is_not_canon"] is True
    assert envelope["queue_presence_is_not_approval"] is True
    assert envelope["support_is_not_truth"] is True
    assert envelope["tool_output_is_not_canon"] is True


def test_orchestrator_returns_static_fusion_contract_envelope() -> None:
    result = oao.analyze_omi_raw_idea_with_tools(
        "demo",
        "Plain raw idea.",
        persist_candidates=False,
        allow_deterministic_fallback=False,
    )

    fusion_contract = result["fusion_contract"]
    for field in oao.OMI_FUSION_FINDING_FIELDS:
        assert field in fusion_contract, (
            f"fusion_contract missing field '{field}'; T010 fills these "
            f"with normalized IDs, fingerprints, dedupe/conflict links"
        )


def test_fingerprint_helpers_are_deterministic() -> None:
    a1 = oao.candidate_fingerprint("character", "Alice", "Investigator finding.")
    a2 = oao.candidate_fingerprint("character", "Alice", "Investigator finding.")
    assert a1 == a2

    b1 = oao.candidate_fingerprint("character", "Bob", "Investigator finding.")
    assert b1 != a1

    e1 = oao.evidence_fingerprint(
        [{"source_excerpt": "Alice walked into the library.", "source_locator": "raw_idea:1"}]
    )
    e2 = oao.evidence_fingerprint(
        [{"source_locator": "raw_idea:1", "source_excerpt": "Alice walked into the library."}]
    )
    assert e1 == e2

    n1 = oao.normalized_finding_id("ollama_model", "raw-1", a1)
    n2 = oao.normalized_finding_id("ollama_model", "raw-1", a1)
    assert n1 == n2
    n3 = oao.normalized_finding_id("booknlp", "raw-1", a1)
    assert n3 != n1


def test_existing_omi_extraction_routes_still_work() -> None:
    # Regression: adding the orchestrator module must not break the existing
    # POST /api/projects/{project_name}/omi/extractions route at the
    # module/import level. The route still calls the deterministic marker
    # extractor; that path is unchanged.
    import backend.main as main  # noqa: F401

    assert hasattr(main, "extract_omi_candidates")
    assert hasattr(main, "OMIExtractionRequest")
    assert hasattr(main, "OMIExtractionResponse")
    assert hasattr(main, "OMIExtractedCandidate")
