import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.analysis_normalizer import (
    extract_json_object,
    fallback_story_check_response,
    normalize_story_check_output,
    validate_story_check_schema,
)


def rich_story_check_payload():
    return {
        "task": "story_check",
        "coherence_score": 7,
        "throughline_alignment": {
            "overall_story": {
                "present": True,
                "evidence": ["Public pressure blocks the group."],
                "concerns": [],
            },
            "main_character": {
                "present": False,
                "evidence": [],
                "concerns": ["Main Character evidence is not supplied."],
            },
            "influence_character": {
                "present": False,
                "evidence": [],
                "concerns": ["Influence Character evidence is not supplied."],
            },
            "relationship_story": {
                "present": False,
                "evidence": [],
                "concerns": ["Relationship Story evidence is not supplied."],
            },
        },
        "theme_drift": {
            "status": "insufficient_evidence",
            "reason": "The approved Issue is not supplied.",
        },
        "character_consistency": {
            "status": "insufficient_evidence",
            "reason": "Approved character context is incomplete.",
        },
        "warnings": ["[Factual] Approved context is incomplete."],
        "suggestions": ["What owner-approved evidence is missing?"],
        "insufficient_evidence": [
            "Influence Character evidence is not supplied.",
            "Relationship Story evidence is not supplied.",
        ],
    }


def test_valid_minimal_json_string_normalizes_for_current_ui():
    report = normalize_story_check_output(
        json.dumps(
            {
                "coherence_score": 6,
                "warnings": ["Missing approved context."],
                "suggestions": ["What evidence is missing?"],
            }
        )
    )

    assert report["task"] == "story_check"
    assert report["coherence_score"] == 6
    assert report["warnings"] == ["[Factual] Missing approved context."]
    assert report["suggestions"] == ["What evidence is missing?"]
    assert report["diagnostics"]["legacy_small_schema"] is True


def test_valid_rich_story_check_json_preserves_rich_fields():
    payload = rich_story_check_payload()

    report = normalize_story_check_output(json.dumps(payload))

    assert report["coherence_score"] == 7
    assert report["throughline_alignment"] == payload["throughline_alignment"]
    assert report["theme_drift"] == payload["theme_drift"]
    assert report["character_consistency"] == payload["character_consistency"]
    assert report["insufficient_evidence"] == payload["insufficient_evidence"]
    assert report["diagnostics"]["schema_valid"] is True


def test_malformed_json_returns_stable_fallback():
    report = normalize_story_check_output("not json")

    assert report == fallback_story_check_response("Failed to parse LLM response", raw_content="not json")


def test_top_level_array_and_string_return_fallback():
    array_report = normalize_story_check_output('[{"coherence_score": 5}]')
    string_report = normalize_story_check_output('"not an object"')

    assert array_report["coherence_score"] == 0
    assert string_report["coherence_score"] == 0
    assert array_report["insufficient_evidence"] == ["A valid JSON Story Check response was not available."]
    assert string_report["insufficient_evidence"] == ["A valid JSON Story Check response was not available."]


def test_score_defaults_and_clamps():
    assert normalize_story_check_output({})["coherence_score"] == 0
    assert normalize_story_check_output({"coherence_score": 12})["coherence_score"] == 10
    assert normalize_story_check_output({"coherence_score": -2})["coherence_score"] == 0


def test_warnings_and_suggestions_are_lists_capped_and_filtered():
    report = normalize_story_check_output(
        {
            "coherence_score": 5,
            "warnings": ["one", 2, "", "three", "four", "five", "six"],
            "suggestions": [
                "What evidence is missing?",
                3,
                "Where is the approved context?",
                "Rewrite this paragraph?",
                "How should unresolved fields be marked?",
                "Which claim needs owner approval?",
                "What remains unknown?",
            ],
        }
    )

    assert report["warnings"] == [
        "[Factual] one",
        "[Factual] 2",
        "[Factual] three",
        "[Factual] four",
        "[Factual] five",
    ]
    assert report["suggestions"] == [
        "What evidence is missing?",
        "Where is the approved context?",
        "How should unresolved fields be marked?",
        "Which claim needs owner approval?",
        "What remains unknown?",
    ]


def test_schema_validation_errors_are_captured_in_diagnostics():
    payload = rich_story_check_payload()
    payload.pop("throughline_alignment")

    report = normalize_story_check_output(payload)

    assert report["diagnostics"]["schema_valid"] is False
    assert any("throughline_alignment" in error for error in report["diagnostics"]["schema_errors"])


def test_raw_content_is_preserved_as_diagnostics_not_truth():
    report = normalize_story_check_output(
        {"coherence_score": 4, "warnings": [], "suggestions": []},
        raw_content="raw model text",
    )

    assert report["raw_diagnostics"] == {"raw_content": "raw model text"}
    assert "raw model text" not in report.get("insufficient_evidence", [])


def test_normalizer_does_not_invent_ic_or_rs_evidence():
    payload = rich_story_check_payload()
    payload["throughline_alignment"]["influence_character"]["evidence"] = []
    payload["throughline_alignment"]["relationship_story"]["evidence"] = []

    report = normalize_story_check_output(payload)

    assert report["throughline_alignment"]["influence_character"]["present"] is False
    assert report["throughline_alignment"]["influence_character"]["evidence"] == []
    assert report["throughline_alignment"]["relationship_story"]["present"] is False
    assert report["throughline_alignment"]["relationship_story"]["evidence"] == []


def test_extract_json_object_rejects_ambiguous_multiple_objects():
    assert extract_json_object('{"a": 1} {"b": 2}') is None


def test_validate_story_check_schema_reports_valid_payload():
    valid, errors = validate_story_check_schema(rich_story_check_payload())

    assert valid is True
    assert errors == []
