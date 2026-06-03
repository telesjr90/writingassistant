import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.scripts import run_story_check_baseline_eval as baseline_eval


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "story_check"
DATASET_MANIFEST = Path(__file__).resolve().parents[1] / "training" / "data" / "dataset_manifest.json"


def test_harness_import_has_no_side_effects():
    assert callable(baseline_eval.run_offline_fixture_evaluation)
    assert callable(baseline_eval.main)


def test_default_cli_mode_does_not_call_live_ollama(monkeypatch, tmp_path):
    called = False

    def fail_live(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("live Ollama should not be called by default")

    monkeypatch.setattr(baseline_eval, "run_live_ollama_evaluation", fail_live)
    output_path = tmp_path / "report.json"

    exit_code = baseline_eval.main(
        [
            "--fixtures-dir",
            str(FIXTURE_DIR),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert called is False
    assert json.loads(output_path.read_text(encoding="utf-8"))["mode"] == "offline_fixtures"


def test_offline_run_reads_fixtures_and_returns_summary():
    report = baseline_eval.run_offline_fixture_evaluation(FIXTURE_DIR)

    assert report["mode"] == "offline_fixtures"
    assert report["summary"]["total_fixture_count"] == 6
    assert report["summary"]["json_fixture_count"] == 5
    assert report["summary"]["malformed_fixture_count"] == 1
    assert report["summary"]["normalized_output_count"] == 5
    assert report["summary"]["error_count"] == 0


def test_output_report_contains_expected_keys(tmp_path):
    output_path = tmp_path / "story_check_baseline_eval.json"
    report = baseline_eval.run_offline_fixture_evaluation(FIXTURE_DIR)

    baseline_eval.write_report(report, output_path, pretty=True)
    written = json.loads(output_path.read_text(encoding="utf-8"))

    assert {"generated_at", "mode", "fixtures_dir", "summary", "pass_fail", "per_fixture"} <= set(
        written
    )
    assert {
        "json_validity_ok",
        "schema_compliance_ok",
        "refusal_exactness_ok",
        "no_prose_violations_ok",
        "insufficient_evidence_ok",
        "output_guard_ok",
    } <= set(written["pass_fail"])


def test_all_app_12_fixtures_are_represented():
    report = baseline_eval.run_offline_fixture_evaluation(FIXTURE_DIR)
    fixture_names = {item["fixture_name"] for item in report["per_fixture"]}

    assert fixture_names == {
        "valid_rich_story_check.json",
        "minimal_story_check.json",
        "malformed_story_check.txt",
        "refusal_response.json",
        "insufficient_evidence_story_check.json",
        "unsafe_output_story_check.json",
    }


def test_malformed_fixture_reports_fallback_and_parser_warning():
    report = baseline_eval.run_offline_fixture_evaluation(FIXTURE_DIR)
    malformed = _fixture(report, "malformed_story_check.txt")

    assert malformed["fixture_type"] == "malformed"
    assert malformed["fallback_used"] is True
    assert malformed["parser_warning"] == "Failed to parse LLM response"


def test_refusal_fixture_matches_exact_standard_refusal():
    report = baseline_eval.run_offline_fixture_evaluation(FIXTURE_DIR)
    refusal = _fixture(report, "refusal_response.json")

    assert refusal["fixture_type"] == "refusal"
    assert refusal["refusal_exact"] is True
    assert report["pass_fail"]["refusal_exactness_ok"] is True


def test_unsafe_fixture_triggers_output_guard_without_remaining_violation():
    report = baseline_eval.run_offline_fixture_evaluation(FIXTURE_DIR)
    unsafe = _fixture(report, "unsafe_output_story_check.json")

    assert unsafe["output_guard_triggered"] is True
    assert unsafe["no_prose_violation_detected"] is False
    assert report["pass_fail"]["output_guard_ok"] is True
    assert report["pass_fail"]["no_prose_violations_ok"] is True


def test_harness_does_not_write_training_data_or_dataset_manifest(tmp_path):
    before = DATASET_MANIFEST.read_text(encoding="utf-8") if DATASET_MANIFEST.exists() else None
    output_path = tmp_path / "report.json"

    baseline_eval.main(
        [
            "--fixtures-dir",
            str(FIXTURE_DIR),
            "--output",
            str(output_path),
        ]
    )

    assert output_path.exists()
    assert not list((tmp_path / "training").glob("**/*"))
    after = DATASET_MANIFEST.read_text(encoding="utf-8") if DATASET_MANIFEST.exists() else None
    assert after == before


def test_live_mode_is_opt_in(monkeypatch, tmp_path):
    calls = []

    def fake_live(project_name, scene_id):
        calls.append((project_name, scene_id))
        return {
            "generated_at": "2026-06-02T00:00:00+00:00",
            "mode": "live_ollama",
            "summary": {},
            "pass_fail": {},
            "per_fixture": [],
        }

    monkeypatch.setattr(baseline_eval, "run_live_ollama_evaluation", fake_live)
    output_path = tmp_path / "live_report.json"

    baseline_eval.main(
        [
            "--live-ollama",
            "--live-project",
            "example",
            "--live-scene",
            "scene_001",
            "--output",
            str(output_path),
        ]
    )

    assert calls == [("example", "scene_001")]
    assert json.loads(output_path.read_text(encoding="utf-8"))["mode"] == "live_ollama"


def _fixture(report, name):
    return next(item for item in report["per_fixture"] if item["fixture_name"] == name)
