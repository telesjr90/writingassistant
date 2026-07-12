"""Focused T002C Story Check engine/normalizer/route integration tests.

No test calls a model, creates candidates, persists analysis, promotes output,
mutates Memory/Canon, or generates story prose.
"""

from __future__ import annotations

import hashlib

import pytest

from backend import analysis_engine, main
from backend.story_check_grounding_contract import build_story_check_source_snapshot
from backend.story_check_grounding_integration import (
    StoryCheckGroundingIntegrationError,
    ground_story_check_result,
)


def snapshot(text: str = "The archive key is beneath the blue ledger."):
    return build_story_check_source_snapshot(
        project_id="example",
        source_type="scene",
        source_id="scene_001",
        source_content=text,
    )


def evidence(source, excerpt: str, **overrides):
    source_bytes = source.source_content.encode("utf-8")
    excerpt_bytes = excerpt.encode("utf-8")
    start = source_bytes.index(excerpt_bytes)
    value = {
        "source_id": source.source_id,
        "source_sha256": source.source_sha256,
        "start_byte": start,
        "end_byte": start + len(excerpt_bytes),
        "excerpt": excerpt,
        "offset_basis": "utf-8-bytes-zero-based-half-open",
    }
    value.update(overrides)
    return value


def explicit_result(message, evidence_items=(), **overrides):
    diagnostic = {
        "diagnostic_id": "warning-001",
        "classification": "factual_warning",
        "message": message,
        "evidence": list(evidence_items),
    }
    diagnostic.update(overrides)
    return {"warnings": [message], "grounding_diagnostics": [diagnostic]}


def grounded_diagnostic(result, message):
    return next(
        item for item in result["grounding"]["diagnostics"]
        if item["message"] == message
    )


def test_engine_builds_exact_server_source_identity_and_ignores_false_client_hash(monkeypatch):
    source_text = "first line\r\nsecond line 雨"
    monkeypatch.setattr(analysis_engine.project_manager, "load_scene", lambda *_: source_text)
    monkeypatch.setattr(analysis_engine.analysis_modes, "get_analysis_mode", lambda: "mock")
    monkeypatch.setattr(
        analysis_engine,
        "_load_mock_story_check_response",
        lambda: {
            "warnings": ["[Factual] Unsupported warning."],
            "suggestions": [],
            "client_source_sha256": "0" * 64,
        },
    )

    result = analysis_engine.run_story_check("example", "scene_001")
    identity = result["grounding"]["source_identity"]

    assert identity["project_id"] == "example"
    assert identity["source_id"] == "scene_001"
    assert identity["source_type"] == "scene"
    assert identity["source_sha256"] == hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    assert identity["source_sha256"] != result["client_source_sha256"]
    assert identity["utf8_byte_length"] == len(source_text.encode("utf-8"))
    assert identity["hash_algorithm"] == "sha256"
    assert identity["hash_basis"] == "utf-8-exact"
    assert not identity["source_id"].startswith("/")


def test_lf_and_crlf_sources_have_different_server_hashes():
    lf = snapshot("first\nsecond")
    crlf = snapshot("first\r\nsecond")
    assert lf.source_sha256 != crlf.source_sha256
    assert lf.utf8_byte_length + 1 == crlf.utf8_byte_length


def test_supported_factual_warning_serializes_verified_with_exact_text_and_evidence():
    source = snapshot("The archive key is beneath the blue ledger.")
    message = source.source_content
    result = ground_story_check_result(
        explicit_result(message, [evidence(source, message)]), source
    )
    diagnostic = grounded_diagnostic(result, message)

    assert diagnostic["verification_state"] == "verified"
    assert diagnostic["validator_result"]["outcome"] == "supported"
    assert diagnostic["validator_result"]["reason_codes"] == ["exact_evidence_matched"]
    assert diagnostic["message"] == message
    assert diagnostic["evidence"][0]["excerpt"] == message
    assert diagnostic["evidence"][0]["source_id"] == "scene_001"


def test_unsupported_and_evidence_absent_factual_warnings_are_quarantined():
    source = snapshot("The archive key is present.")
    unsupported = "The archive key is absent."
    with_evidence = ground_story_check_result(
        explicit_result(unsupported, [evidence(source, source.source_content)]), source
    )
    without_evidence = ground_story_check_result(
        {"warnings": ["[Factual] No direct evidence was returned."]}, source
    )

    first = grounded_diagnostic(with_evidence, unsupported)
    second = grounded_diagnostic(
        without_evidence, "[Factual] No direct evidence was returned."
    )
    assert first["verification_state"] == "quarantined"
    assert first["validator_result"]["outcome"] == "unsupported"
    assert second["verification_state"] == "quarantined"
    assert second["validator_result"]["reason_codes"] == ["evidence_absent"]


@pytest.mark.parametrize(
    ("identity", "reason"),
    [
        ({"source_id": "scene_002"}, "story_check_source_id_mismatch"),
        ({"source_sha256": "f" * 64}, "story_check_source_hash_mismatch"),
    ],
)
def test_envelope_source_mismatch_fails_closed(identity, reason):
    source = snapshot()
    with pytest.raises(StoryCheckGroundingIntegrationError, match=reason):
        ground_story_check_result({"source_identity": identity, "warnings": []}, source)


def test_flat_normalized_result_source_mismatch_also_fails_closed():
    with pytest.raises(
        StoryCheckGroundingIntegrationError, match="story_check_source_id_mismatch"
    ):
        ground_story_check_result(
            {"source_id": "scene_002", "warnings": []}, snapshot()
        )


def test_individual_source_id_and_hash_mismatch_is_quarantined_in_stable_order():
    source = snapshot("exact claim")
    mismatched = evidence(
        source,
        "exact claim",
        source_id="scene_002",
        source_sha256="a" * 64,
    )
    result = ground_story_check_result(
        explicit_result("exact claim", [mismatched]), source
    )
    diagnostic = grounded_diagnostic(result, "exact claim")

    assert diagnostic["verification_state"] == "quarantined"
    assert diagnostic["validator_result"]["outcome"] == "source_mismatch"
    assert diagnostic["validator_result"]["reason_codes"] == [
        "source_id_mismatch",
        "source_hash_mismatch",
    ]
    assert diagnostic["evidence"] == []


def test_invalid_excerpt_or_range_cannot_remain_verified():
    source = snapshot("exact claim")
    invalid = evidence(source, "exact claim", end_byte=4)
    invalid["excerpt"] = "wrong"
    result = ground_story_check_result(explicit_result("exact claim", [invalid]), source)
    diagnostic = grounded_diagnostic(result, "exact claim")

    assert diagnostic["verification_state"] == "quarantined"
    assert diagnostic["validator_result"]["outcome"] == "unsupported"
    assert diagnostic["validator_result"]["reason_codes"] == [
        "evidence_invalid",
        "excerpt_mismatch",
    ]
    assert diagnostic["evidence"] == []


def test_structural_questions_and_observations_remain_visible_unverified():
    result = ground_story_check_result(
        {
            "warnings": ["[Character] Motivation changes without setup."],
            "suggestions": ["What evidence supports the change?"],
            "insufficient_evidence": ["The motive is not established."],
        },
        snapshot(),
    )
    diagnostics = result["grounding"]["diagnostics"]

    assert [item["message"] for item in diagnostics] == [
        "[Character] Motivation changes without setup.",
        "What evidence supports the change?",
        "The motive is not established.",
    ]
    assert [item["classification"] for item in diagnostics] == [
        "structural_diagnostic",
        "question",
        "observation",
    ]
    assert all(item["verification_state"] == "unverified" for item in diagnostics)
    assert all(
        item["validator_result"]["outcome"] == "not_applicable"
        for item in diagnostics
    )


def test_diagnostic_order_and_serialization_are_deterministic():
    payload = {
        "warnings": ["[Factual] One", "[Character] Two"],
        "suggestions": ["Three?"],
        "insufficient_evidence": ["Four"],
    }
    source = snapshot()
    first = ground_story_check_result(payload, source)["grounding"]
    second = ground_story_check_result(payload, source)["grounding"]
    assert first == second
    assert [item["message"] for item in first["diagnostics"]] == [
        "[Factual] One",
        "[Character] Two",
        "Three?",
        "Four",
    ]


def test_malformed_grounding_data_falls_back_to_safe_legacy_classification():
    message = "[Factual] Legacy warning remains visible."
    result = ground_story_check_result(
        {
            "warnings": [message],
            "grounding_diagnostics": [{"message": 123, "verification_state": "verified"}],
        },
        snapshot(),
    )
    diagnostic = grounded_diagnostic(result, message)
    assert diagnostic["verification_state"] == "quarantined"
    assert diagnostic["validator_result"]["outcome"] == "unsupported"


def test_engine_envelope_mismatch_returns_failed_closed_grounding(monkeypatch):
    source_text = "exact source"
    monkeypatch.setattr(analysis_engine.project_manager, "load_scene", lambda *_: source_text)
    monkeypatch.setattr(analysis_engine.analysis_modes, "get_analysis_mode", lambda: "mock")
    monkeypatch.setattr(
        analysis_engine,
        "_load_mock_story_check_response",
        lambda: {"source_identity": {"source_id": "other"}, "warnings": []},
    )

    result = analysis_engine.run_story_check("example", "scene_001")
    assert result["grounding"]["status"] == "failed_closed"
    assert result["grounding"]["reason_codes"] == ["story_check_source_id_mismatch"]
    assert "error" in result


def test_current_route_seam_returns_grounded_engine_response_unchanged(monkeypatch):
    payload = ground_story_check_result(
        {"warnings": ["[Factual] Unsupported."]}, snapshot()
    )
    monkeypatch.setattr(main._analysis_module, "run_story_check", lambda *_: payload)
    assert main.story_check("example", "scene_001") is payload


def test_engine_grounding_path_has_no_candidate_persistence_or_canon_side_effect(monkeypatch):
    source_text = "owner-authored analysis source"
    monkeypatch.setattr(analysis_engine.project_manager, "load_scene", lambda *_: source_text)
    monkeypatch.setattr(analysis_engine.analysis_modes, "get_analysis_mode", lambda: "mock")
    monkeypatch.setattr(
        analysis_engine,
        "_load_mock_story_check_response",
        lambda: {"warnings": [], "suggestions": ["What is unresolved?"]},
    )

    for name in (
        "save_scene",
        "create_omi_candidate",
        "create_omi_promotion",
        "apply_omi_promotion",
        "save_bible",
        "save_storyform_json",
    ):
        if hasattr(analysis_engine.project_manager, name):
            monkeypatch.setattr(
                analysis_engine.project_manager,
                name,
                lambda *args, _name=name, **kwargs: (_ for _ in ()).throw(
                    AssertionError(f"unexpected side effect: {_name}")
                ),
            )

    result = analysis_engine.run_story_check("example", "scene_001")
    assert result["grounding"]["status"] == "completed"
    assert result["grounding"]["boundary"] == {
        "analytical_output": True,
        "non_canon": True,
        "owner_approved": False,
    }
