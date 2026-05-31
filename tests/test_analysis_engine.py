import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.analysis_engine import _parse_story_check_response


def rich_story_check_payload():
    return {
        "task": "story_check",
        "coherence_score": 7,
        "throughline_alignment": {
            "overall_story": {
                "present": True,
                "evidence": ["The scene shows the group blocked by a public deadline."],
                "concerns": [],
            },
            "main_character": {
                "present": True,
                "evidence": ["The protagonist weighs a familiar personal pressure."],
                "concerns": [],
            },
            "influence_character": {
                "present": False,
                "evidence": [],
                "concerns": ["No clear counter-pressure from the approved Influence Character appears."],
            },
            "relationship_story": {
                "present": False,
                "evidence": [],
                "concerns": ["No relationship-specific conflict is visible in the supplied scene."],
            },
        },
        "theme_drift": {
            "status": "mild",
            "reason": "The conflict touches the approved problem but does not clearly pressure the issue.",
        },
        "character_consistency": {
            "status": "consistent",
            "reason": "The protagonist's behavior does not contradict the supplied bible facts.",
        },
        "warnings": ["[Character] Influence Character pressure is not visible in this scene."],
        "suggestions": [
            "What evidence would make the Influence Character pressure concrete in this scene?"
        ],
        "insufficient_evidence": [
            "Relationship Story evidence is not present in the supplied scene text."
        ],
    }


def test_valid_rich_story_check_output_parses_to_ui_compatible_fields():
    report = _parse_story_check_response(json.dumps(rich_story_check_payload()))

    assert report["coherence_score"] == 7
    assert report["warnings"] == ["[Character] Influence Character pressure is not visible in this scene."]
    assert report["suggestions"] == [
        "What evidence would make the Influence Character pressure concrete in this scene?"
    ]
    assert report["diagnostics"]["task"] == "story_check"
    assert report["diagnostics"]["schema_valid"] is True
    assert report["diagnostics"]["insufficient_evidence"] == [
        "Relationship Story evidence is not present in the supplied scene text."
    ]


def test_legacy_small_story_check_output_still_normalizes():
    content = json.dumps(
        {
            "coherence_score": 6,
            "warnings": ["Missing Influence Character pressure."],
            "suggestions": ["What would reveal the missing pressure?"],
        }
    )

    report = _parse_story_check_response(content)

    assert report["coherence_score"] == 6
    assert report["warnings"] == ["[Factual] Missing Influence Character pressure."]
    assert report["suggestions"] == ["What would reveal the missing pressure?"]
    assert report["diagnostics"]["legacy_small_schema"] is True


def test_malformed_story_check_output_is_safe_ui_compatible_fallback():
    report = _parse_story_check_response("not json")

    assert report["coherence_score"] == 0
    assert report["warnings"] == ["[Factual] Failed to parse LLM response"]
    assert report["suggestions"] == []
    assert report["diagnostics"]["schema_valid"] is False
    assert "raw_diagnostics" in report


def test_rich_output_schema_errors_are_preserved_without_breaking_ui_fields():
    payload = rich_story_check_payload()
    payload.pop("throughline_alignment")

    report = _parse_story_check_response(json.dumps(payload))

    assert report["coherence_score"] == 7
    assert all(warning.startswith(("[Plot/Temporal]", "[Character]", "[Worldbuilding]", "[Factual]", "[Stylistic]")) for warning in report["warnings"])
    assert report["diagnostics"]["schema_valid"] is False
    assert any("throughline_alignment" in error for error in report["diagnostics"]["schema_errors"])


def test_suggestions_remain_questions_and_prose_requests_are_dropped():
    payload = rich_story_check_payload()
    payload["suggestions"] = [
        "Rewrite the scene with sharper dialogue?",
        "What approved storyform evidence is missing?",
        "Add a better ending.",
    ]

    report = _parse_story_check_response(json.dumps(payload))

    assert report["suggestions"] == ["What approved storyform evidence is missing?"]
