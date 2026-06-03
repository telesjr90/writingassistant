import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import guardrails
from backend.analysis_normalizer import (
    MISSING_JSON_EVIDENCE,
    normalize_story_check_output,
    validate_story_check_schema,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "story_check"
JSON_FIXTURES = [
    "valid_rich_story_check.json",
    "minimal_story_check.json",
    "refusal_response.json",
    "insufficient_evidence_story_check.json",
    "unsafe_output_story_check.json",
]
FORBIDDEN_FIXTURE_MARKERS = (
    "Once upon a time",
    "Chapter 1",
    "generated scene",
    "replacement paragraph",
    "new scene text",
)


def load_json_fixture(name):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_json_fixtures_load_successfully():
    for fixture_name in JSON_FIXTURES:
        assert isinstance(load_json_fixture(fixture_name), dict), fixture_name


def test_valid_rich_fixture_normalizes_to_schema_valid_output():
    report = normalize_story_check_output(load_json_fixture("valid_rich_story_check.json"))

    assert report["task"] == "story_check"
    assert report["diagnostics"]["schema_valid"] is True
    assert {"overall_story", "main_character", "influence_character", "relationship_story"} == set(
        report["throughline_alignment"]
    )
    valid, errors = validate_story_check_schema(
        {
            "task": report["task"],
            "coherence_score": report["coherence_score"],
            "throughline_alignment": report["throughline_alignment"],
            "theme_drift": report["theme_drift"],
            "character_consistency": report["character_consistency"],
            "warnings": report["warnings"],
            "suggestions": report["suggestions"],
            "insufficient_evidence": report["insufficient_evidence"],
        }
    )
    assert valid is True
    assert errors == []


def test_minimal_fixture_normalizes_to_ui_compatible_output():
    report = normalize_story_check_output(load_json_fixture("minimal_story_check.json"))

    assert report["task"] == "story_check"
    assert report["coherence_score"] == 5
    assert report["warnings"] == ["[Factual] Approved context is incomplete."]
    assert report["suggestions"] == ["What evidence is missing?"]
    assert report["diagnostics"]["legacy_small_schema"] is True


def test_malformed_fixture_normalizes_to_deterministic_fallback():
    malformed = (FIXTURE_DIR / "malformed_story_check.txt").read_text(encoding="utf-8")

    report = normalize_story_check_output(malformed)

    assert report["task"] == "story_check"
    assert report["coherence_score"] == 0
    assert report["warnings"] == ["[Factual] Failed to parse LLM response"]
    assert report["suggestions"] == []
    assert report["insufficient_evidence"] == [MISSING_JSON_EVIDENCE]


def test_refusal_fixture_matches_standard_message():
    refusal = load_json_fixture("refusal_response.json")

    assert refusal == guardrails.refusal_response()
    assert refusal["message"] == guardrails.STANDARD_REFUSAL_MESSAGE


def test_insufficient_evidence_fixture_preserves_unresolved_fields():
    report = normalize_story_check_output(
        load_json_fixture("insufficient_evidence_story_check.json")
    )

    assert report["diagnostics"]["schema_valid"] is True
    assert "CIPS is unresolved." in report["insufficient_evidence"]
    assert "Dynamics are unresolved." in report["insufficient_evidence"]
    assert report["throughline_alignment"]["influence_character"]["present"] is False
    assert report["throughline_alignment"]["relationship_story"]["evidence"] == []


def test_unsafe_output_fixture_is_sanitized_and_preserves_evidence():
    report = normalize_story_check_output(load_json_fixture("unsafe_output_story_check.json"))
    sanitized = guardrails.sanitize_story_check_output(report)
    serialized = json.dumps(sanitized)

    assert sanitized["diagnostics"]["output_guard_triggered"] is True
    assert sanitized["throughline_alignment"]["overall_story"]["evidence"] == [
        "continue this chapter"
    ]
    assert "Rewrite the scene" not in serialized
    assert "polished paragraph" not in serialized
    assert "What owner-approved evidence is missing?" in sanitized["suggestions"]


def test_fixture_readme_declares_not_training_data():
    readme = (FIXTURE_DIR / "README.md").read_text(encoding="utf-8")

    assert "not training data" in readme
    assert "dataset_manifest.json" in readme
    assert "must not contain generated story prose" in readme


def test_fixtures_are_not_training_data_paths():
    for path in FIXTURE_DIR.iterdir():
        assert "training/data" not in path.as_posix()


def test_fixtures_do_not_contain_forbidden_long_prose_markers():
    for path in FIXTURE_DIR.iterdir():
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for marker in FORBIDDEN_FIXTURE_MARKERS:
                assert marker not in text, f"{marker} found in {path.name}"
