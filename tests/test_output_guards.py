import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import guardrails


def base_story_check_output():
    return {
        "task": "story_check",
        "coherence_score": 6,
        "warnings": ["[Factual] Approved context is incomplete."],
        "suggestions": ["What owner-approved evidence is missing?"],
        "throughline_alignment": {
            "overall_story": {
                "present": True,
                "evidence": ['The note says "continue this chapter."'],
                "concerns": ["Overall Story pressure is visible."],
            },
            "main_character": {"present": False, "evidence": [], "concerns": []},
            "influence_character": {"present": False, "evidence": [], "concerns": []},
            "relationship_story": {"present": False, "evidence": [], "concerns": []},
        },
        "theme_drift": {"status": "insufficient_evidence", "reason": "Approved Issue is absent."},
        "character_consistency": {
            "status": "insufficient_evidence",
            "reason": "Approved character context is incomplete.",
        },
        "insufficient_evidence": ["Influence Character evidence is not supplied."],
        "diagnostics": {"task": "story_check", "schema_valid": True},
    }


def test_unsafe_suggestion_is_removed_and_guard_is_marked():
    output = base_story_check_output()
    output["suggestions"] = [
        "Rewrite the scene so the queen says [blocked].",
        "What owner-approved evidence is missing?",
    ]

    sanitized = guardrails.sanitize_story_check_output(output)

    assert sanitized["suggestions"] == ["What owner-approved evidence is missing?"]
    assert sanitized["diagnostics"]["output_guard_triggered"] is True
    assert "Rewrite the scene" not in json.dumps(sanitized)
    assert any("Output guard removed" in warning for warning in sanitized["warnings"])


def test_unsafe_warning_and_reason_are_sanitized():
    output = base_story_check_output()
    output["warnings"] = ["[Factual] Here is a polished paragraph: [blocked]."]
    output["theme_drift"]["reason"] = "Here is a polished paragraph: [blocked]."

    sanitized = guardrails.sanitize_story_check_output(output)

    serialized = json.dumps(sanitized)
    assert "polished paragraph" not in serialized
    assert sanitized["theme_drift"]["reason"] == guardrails.OUTPUT_GUARD_NOTE
    assert sanitized["diagnostics"]["output_guard_triggered"] is True
    assert sanitized["diagnostics"]["output_guard_removed_count"] == 2


def test_severe_prose_output_returns_safe_story_check_fallback():
    output = base_story_check_output()
    output["warnings"] = ["[Factual] New dialogue: [blocked]."]
    output["theme_drift"]["reason"] = "Continue the scene with [blocked]."
    output["character_consistency"]["reason"] = "Drafted paragraph: [blocked]."

    sanitized = guardrails.sanitize_story_check_output(output)

    serialized = json.dumps(sanitized)
    assert sanitized["task"] == "story_check"
    assert sanitized["coherence_score"] == 0
    assert sanitized["diagnostics"]["output_guard_triggered"] is True
    assert sanitized["diagnostics"]["output_guard_severity"] == "severe"
    assert sanitized["diagnostics"]["message"] == guardrails.STANDARD_REFUSAL_MESSAGE
    assert "New dialogue" not in serialized
    assert "Drafted paragraph" not in serialized


def test_evidence_spans_are_preserved_even_when_story_like():
    output = base_story_check_output()

    sanitized = guardrails.sanitize_story_check_output(output)

    assert sanitized["throughline_alignment"]["overall_story"]["evidence"] == [
        'The note says "continue this chapter."'
    ]
    assert sanitized["diagnostics"]["output_guard_triggered"] is False


def test_analysis_only_suggestions_and_insufficient_evidence_are_preserved():
    output = base_story_check_output()
    output["suggestions"] = [
        "Clarify whether this scene belongs to the Overall Story or Main Character throughline.",
        "Add evidence before making an Influence Character claim.",
    ]

    sanitized = guardrails.sanitize_story_check_output(output)

    assert sanitized["suggestions"] == output["suggestions"]
    assert sanitized["insufficient_evidence"] == [
        "Influence Character evidence is not supplied."
    ]
    assert sanitized["diagnostics"]["output_guard_triggered"] is False


def test_unsafe_raw_diagnostics_are_not_exposed():
    output = base_story_check_output()
    output["raw_diagnostics"] = {"raw_content": "Here is a rewritten version: [blocked]."}

    sanitized = guardrails.sanitize_story_check_output(output)

    assert sanitized["raw_diagnostics"]["raw_content"] == guardrails.OUTPUT_GUARD_NOTE
    assert "rewritten version" not in json.dumps(sanitized)
