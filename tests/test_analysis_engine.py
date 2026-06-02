import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import analysis_engine, guardrails
from backend.analysis_engine import _ollama_chat_url, _parse_story_check_response


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


def test_default_ollama_base_url_builds_chat_endpoint(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)

    assert _ollama_chat_url() == "http://localhost:11434/api/chat"


def test_custom_ollama_base_url_builds_chat_endpoint(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://172.25.144.1:11434")

    assert _ollama_chat_url() == "http://172.25.144.1:11434/api/chat"


def test_custom_ollama_base_url_strips_trailing_slash(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://172.25.144.1:11434/")

    assert _ollama_chat_url() == "http://172.25.144.1:11434/api/chat"


def test_run_story_check_mock_mode_returns_rich_schema_compatible_report(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "mock")

    def fail_post(*args, **kwargs):
        raise AssertionError("mock mode must not call Ollama")

    monkeypatch.setattr(analysis_engine.requests, "post", fail_post)

    report = analysis_engine.run_story_check("example", "scene_001")

    assert report["task"] == "story_check"
    assert report["coherence_score"] == 7
    assert {"overall_story", "main_character", "influence_character", "relationship_story"} == set(
        report["throughline_alignment"]
    )
    assert report["theme_drift"]["status"] == "insufficient_evidence"
    assert report["character_consistency"]["status"] == "consistent"
    assert report["diagnostics"]["schema_valid"] is True
    assert report["diagnostics"]["analysis_mode"] == "mock"
    assert report["diagnostics"]["candidate_only"] is True
    assert report["diagnostics"]["mutates_project_truth"] is False


def test_mock_story_check_output_keeps_unsupported_throughlines_unproven(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "mock")

    report = analysis_engine.run_story_check("example", "scene_001")
    alignment = report["throughline_alignment"]

    assert alignment["main_character"]["present"] is False
    assert alignment["main_character"]["evidence"] == []
    assert alignment["influence_character"]["present"] is False
    assert alignment["influence_character"]["evidence"] == []
    assert alignment["relationship_story"]["present"] is False
    assert alignment["relationship_story"]["evidence"] == []
    assert any("CIPS and dynamics are unresolved" in item for item in report["insufficient_evidence"])
    assert guardrails.output_appears_to_contain_prose_generation(report) is False


def test_mock_story_check_output_does_not_mutate_project_files(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "mock")
    project_files = [
        Path("projects/example/bible.json"),
        Path("projects/example/storyform.json"),
        Path("projects/example/project.json"),
        Path("projects/example/scenes/scene_001.md"),
    ]
    before = {path: path.read_text(encoding="utf-8") for path in project_files}

    analysis_engine.run_story_check("example", "scene_001")

    after = {path: path.read_text(encoding="utf-8") for path in project_files}
    assert after == before


def test_run_story_check_ollama_baseline_uses_mocked_post_and_normalizer(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "ollama_baseline")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://example.test:11434/")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "message": {
                    "content": json.dumps(
                        {
                            "coherence_score": 6,
                            "warnings": ["Missing approved context."],
                            "suggestions": ["What evidence is missing?"],
                        }
                    )
                }
            }

    captured = {}

    def fake_post(url, *, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(analysis_engine.requests, "post", fake_post)

    report = analysis_engine.run_story_check("example", "scene_001")

    assert captured["url"] == "http://example.test:11434/api/chat"
    assert captured["json"]["model"] == "test-model"
    assert captured["json"]["format"] == "json"
    assert captured["json"]["think"] is False
    assert captured["json"]["options"]["temperature"] == 0
    assert captured["json"]["options"]["num_predict"] == 2048
    assert captured["json"]["stream"] is False
    assert report["coherence_score"] == 6
    assert report["warnings"] == ["[Factual] Missing approved context."]
    assert report["diagnostics"]["legacy_small_schema"] is True


def test_run_story_check_missing_analysis_mode_uses_ollama_baseline(monkeypatch):
    monkeypatch.delenv("ANALYSIS_MODE", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": json.dumps(rich_story_check_payload())}}

    captured = {}

    def fake_post(url, *, json, timeout):
        captured["url"] = url
        captured["model"] = json["model"]
        return FakeResponse()

    monkeypatch.setattr(analysis_engine.requests, "post", fake_post)

    report = analysis_engine.run_story_check("example", "scene_001")

    assert captured["url"] == "http://localhost:11434/api/chat"
    assert captured["model"] == "qwen3:8b"
    assert report["diagnostics"]["schema_valid"] is True


def test_run_story_check_invalid_analysis_mode_returns_stable_error(monkeypatch):
    monkeypatch.setenv("ANALYSIS_MODE", "invalid")

    report = analysis_engine.run_story_check("example", "scene_001")

    assert report == {"error": "Invalid ANALYSIS_MODE 'invalid'. Expected one of: mock, ollama_baseline."}
