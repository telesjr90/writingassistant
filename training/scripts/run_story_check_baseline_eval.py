from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend import analysis_normalizer, guardrails


FIXTURE_EXTENSIONS = {".json", ".txt"}
DEFAULT_FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "story_check"
DEFAULT_LIVE_PROJECT = "example"
DEFAULT_LIVE_SCENE = "scene_001"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate Story Check app fixtures through the current normalizer and "
            "output guard. Offline fixture evaluation is the default."
        )
    )
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=DEFAULT_FIXTURES_DIR,
        help="Directory containing Story Check app-level fixtures.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to write the JSON evaluation report.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON report.",
    )
    parser.add_argument(
        "--live-ollama",
        action="store_true",
        help="Opt in to a live Ollama Story Check smoke outside pytest.",
    )
    parser.add_argument(
        "--live-project",
        default=DEFAULT_LIVE_PROJECT,
        help="Project name for --live-ollama.",
    )
    parser.add_argument(
        "--live-scene",
        default=DEFAULT_LIVE_SCENE,
        help="Scene id for --live-ollama.",
    )
    return parser.parse_args(argv)


def run_offline_fixture_evaluation(fixtures_dir: Path) -> dict[str, Any]:
    fixture_paths = [
        path
        for path in sorted(fixtures_dir.iterdir())
        if path.is_file() and path.suffix.lower() in FIXTURE_EXTENSIONS
    ]
    per_fixture = [_evaluate_fixture(path) for path in fixture_paths]
    summary = _build_summary(per_fixture)

    return {
        "generated_at": _utc_timestamp(),
        "mode": "offline_fixtures",
        "fixtures_dir": str(fixtures_dir),
        "summary": summary,
        "pass_fail": _build_pass_fail(summary),
        "per_fixture": per_fixture,
    }


def run_live_ollama_evaluation(project_name: str, scene_id: str) -> dict[str, Any]:
    from backend.analysis_engine import run_story_check

    result = run_story_check(project_name, scene_id)
    diagnostics = result.get("diagnostics") if isinstance(result, dict) else {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    no_prose_violation = _contains_unsafe_output(result)

    return {
        "generated_at": _utc_timestamp(),
        "mode": "live_ollama",
        "live_ollama_requested": True,
        "environment": {
            "analysis_mode": os.environ.get("ANALYSIS_MODE"),
            "ollama_base_url": os.environ.get("OLLAMA_BASE_URL"),
            "ollama_model": os.environ.get("OLLAMA_MODEL"),
        },
        "summary": {
            "total_fixture_count": 0,
            "json_fixture_count": 0,
            "malformed_fixture_count": 0,
            "normalized_output_count": 1 if isinstance(result, dict) and "error" not in result else 0,
            "json_validity_count": 0,
            "schema_valid_count": 1 if diagnostics.get("schema_valid") is True else 0,
            "schema_applicable_count": 1,
            "fallback_count": 0,
            "parser_warning_count": 1 if diagnostics.get("parser_warning") else 0,
            "refusal_exact_match_count": 0,
            "refusal_fixture_count": 0,
            "insufficient_evidence_preservation_count": (
                1 if isinstance(result.get("insufficient_evidence"), list) else 0
            )
            if isinstance(result, dict)
            else 0,
            "insufficient_evidence_applicable_count": 1,
            "output_guard_triggered_count": 1 if diagnostics.get("output_guard_triggered") else 0,
            "output_guard_applicable_count": 1,
            "no_prose_violation_count": 1 if no_prose_violation else 0,
            "evidence_preservation_count": 0,
            "evidence_applicable_count": 0,
            "error_count": 1 if isinstance(result, dict) and "error" in result else 0,
        },
        "pass_fail": {
            "json_validity_ok": True,
            "schema_compliance_ok": diagnostics.get("schema_valid") is True,
            "refusal_exactness_ok": True,
            "no_prose_violations_ok": not no_prose_violation,
            "insufficient_evidence_ok": isinstance(result, dict)
            and isinstance(result.get("insufficient_evidence"), list),
            "output_guard_ok": not no_prose_violation,
        },
        "per_fixture": [
            {
                "fixture_name": f"live:{project_name}/{scene_id}",
                "fixture_type": "live_ollama",
                "status": "error" if isinstance(result, dict) and "error" in result else "ok",
                "schema_valid": diagnostics.get("schema_valid"),
                "parser_warning": diagnostics.get("parser_warning"),
                "fallback_used": False,
                "refusal_exact": None,
                "output_guard_triggered": diagnostics.get("output_guard_triggered", False),
                "no_prose_violation_detected": no_prose_violation,
                "notes": ["Live Ollama evaluation was explicitly requested."],
            }
        ],
    }


def write_report(report: dict[str, Any], output_path: Path, *, pretty: bool = False) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if pretty else None
    output_path.write_text(json.dumps(report, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")


def _evaluate_fixture(path: Path) -> dict[str, Any]:
    notes: list[str] = []
    fixture_type = _fixture_type(path)
    raw_text = path.read_text(encoding="utf-8")
    json_valid = False
    parsed: Any | None = None
    json_error: str | None = None

    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(raw_text)
            json_valid = True
        except json.JSONDecodeError as exc:
            json_error = f"{exc.msg} at line {exc.lineno}, column {exc.colno}"
            notes.append(f"Invalid JSON: {json_error}")

    if fixture_type == "refusal":
        expected = guardrails.refusal_response()
        refusal_exact = parsed == expected
        if not refusal_exact:
            notes.append("Refusal fixture does not exactly match standard response.")
        return _fixture_result(
            path,
            fixture_type=fixture_type,
            status="ok" if refusal_exact else "failed",
            json_valid=json_valid,
            refusal_exact=refusal_exact,
            notes=notes,
        )

    raw_output = parsed if json_valid else raw_text
    normalized = analysis_normalizer.normalize_story_check_output(raw_output)
    sanitized = guardrails.sanitize_story_check_output(normalized)
    diagnostics = sanitized.get("diagnostics") if isinstance(sanitized, dict) else {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}

    parser_warning = diagnostics.get("parser_warning")
    fallback_used = bool(parser_warning)
    output_guard_triggered = diagnostics.get("output_guard_triggered") is True
    no_prose_violation = _contains_unsafe_output(sanitized)
    schema_valid = diagnostics.get("schema_valid")
    insufficient_preserved = _has_insufficient_evidence(sanitized)
    evidence_preserved = _evidence_preserved(parsed, sanitized) if isinstance(parsed, dict) else None

    if json_error:
        notes.append("Fixture is intentionally evaluated through malformed fallback.")
    if no_prose_violation:
        notes.append("Unsafe prose-generation marker remained after sanitization.")
    if evidence_preserved is False:
        notes.append("Evidence array changed during sanitization.")

    status = "ok"
    if no_prose_violation or evidence_preserved is False:
        status = "failed"

    return _fixture_result(
        path,
        fixture_type=fixture_type,
        status=status,
        json_valid=json_valid,
        schema_valid=schema_valid,
        parser_warning=parser_warning,
        fallback_used=fallback_used,
        output_guard_triggered=output_guard_triggered,
        no_prose_violation_detected=no_prose_violation,
        insufficient_evidence_preserved=insufficient_preserved,
        evidence_preserved=evidence_preserved,
        notes=notes,
    )


def _fixture_result(
    path: Path,
    *,
    fixture_type: str,
    status: str,
    json_valid: bool,
    schema_valid: bool | None = None,
    parser_warning: str | None = None,
    fallback_used: bool = False,
    refusal_exact: bool | None = None,
    output_guard_triggered: bool = False,
    no_prose_violation_detected: bool = False,
    insufficient_evidence_preserved: bool | None = None,
    evidence_preserved: bool | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "fixture_name": path.name,
        "fixture_type": fixture_type,
        "status": status,
        "json_valid": json_valid,
        "schema_valid": schema_valid,
        "parser_warning": parser_warning,
        "fallback_used": fallback_used,
        "refusal_exact": refusal_exact,
        "output_guard_triggered": output_guard_triggered,
        "no_prose_violation_detected": no_prose_violation_detected,
        "insufficient_evidence_preserved": insufficient_evidence_preserved,
        "evidence_preserved": evidence_preserved,
        "notes": notes or [],
    }


def _build_summary(per_fixture: list[dict[str, Any]]) -> dict[str, int]:
    schema_applicable = [
        item
        for item in per_fixture
        if item["fixture_type"] in {"rich", "unsafe_output", "insufficient_evidence"}
    ]
    refusal_fixtures = [item for item in per_fixture if item["fixture_type"] == "refusal"]
    insufficient_applicable = [
        item
        for item in per_fixture
        if item["fixture_type"] in {"rich", "malformed", "insufficient_evidence", "unsafe_output"}
    ]
    output_guard_applicable = [
        item for item in per_fixture if item["fixture_type"] == "unsafe_output"
    ]
    evidence_applicable = [item for item in per_fixture if item.get("evidence_preserved") is not None]

    return {
        "total_fixture_count": len(per_fixture),
        "json_fixture_count": sum(1 for item in per_fixture if item["fixture_name"].endswith(".json")),
        "malformed_fixture_count": sum(1 for item in per_fixture if item["fixture_type"] == "malformed"),
        "normalized_output_count": sum(1 for item in per_fixture if item["fixture_type"] != "refusal"),
        "json_validity_count": sum(1 for item in per_fixture if item["json_valid"]),
        "schema_valid_count": sum(1 for item in schema_applicable if item.get("schema_valid") is True),
        "schema_applicable_count": len(schema_applicable),
        "fallback_count": sum(1 for item in per_fixture if item["fallback_used"]),
        "parser_warning_count": sum(1 for item in per_fixture if item["parser_warning"]),
        "refusal_exact_match_count": sum(1 for item in refusal_fixtures if item["refusal_exact"] is True),
        "refusal_fixture_count": len(refusal_fixtures),
        "insufficient_evidence_preservation_count": sum(
            1 for item in insufficient_applicable if item.get("insufficient_evidence_preserved") is True
        ),
        "insufficient_evidence_applicable_count": len(insufficient_applicable),
        "output_guard_triggered_count": sum(1 for item in per_fixture if item["output_guard_triggered"]),
        "output_guard_applicable_count": len(output_guard_applicable),
        "no_prose_violation_count": sum(
            1 for item in per_fixture if item["no_prose_violation_detected"]
        ),
        "evidence_preservation_count": sum(
            1 for item in evidence_applicable if item.get("evidence_preserved") is True
        ),
        "evidence_applicable_count": len(evidence_applicable),
        "error_count": sum(1 for item in per_fixture if item["status"] != "ok"),
    }


def _build_pass_fail(summary: dict[str, int]) -> dict[str, bool]:
    return {
        "json_validity_ok": summary["json_validity_count"] == summary["json_fixture_count"],
        "schema_compliance_ok": summary["schema_valid_count"] == summary["schema_applicable_count"],
        "refusal_exactness_ok": summary["refusal_exact_match_count"] == summary["refusal_fixture_count"],
        "no_prose_violations_ok": summary["no_prose_violation_count"] == 0,
        "insufficient_evidence_ok": (
            summary["insufficient_evidence_preservation_count"]
            == summary["insufficient_evidence_applicable_count"]
        ),
        "output_guard_ok": (
            summary["output_guard_triggered_count"] == summary["output_guard_applicable_count"]
        ),
    }


def _fixture_type(path: Path) -> str:
    name = path.name
    if name == "malformed_story_check.txt":
        return "malformed"
    if name == "refusal_response.json":
        return "refusal"
    if name == "minimal_story_check.json":
        return "minimal"
    if name == "unsafe_output_story_check.json":
        return "unsafe_output"
    if name == "insufficient_evidence_story_check.json":
        return "insufficient_evidence"
    if name == "valid_rich_story_check.json":
        return "rich"
    return "unknown"


def _has_insufficient_evidence(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("insufficient_evidence"), list)


def _contains_unsafe_output(value: Any, path: tuple[str, ...] = ()) -> bool:
    if isinstance(value, str):
        if guardrails.is_evidence_path(path):
            return False
        return guardrails.output_text_appears_unsafe(value)
    if isinstance(value, list):
        return any(_contains_unsafe_output(item, path) for item in value)
    if isinstance(value, dict):
        return any(_contains_unsafe_output(item, path + (str(key),)) for key, item in value.items())
    return False


def _evidence_preserved(original: dict[str, Any], sanitized: dict[str, Any]) -> bool | None:
    original_evidence = _collect_evidence(original)
    if not original_evidence:
        return None
    return original_evidence == _collect_evidence(sanitized)


def _collect_evidence(value: Any) -> list[str]:
    evidence: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "evidence" and isinstance(item, list):
                evidence.extend(text for text in item if isinstance(text, str))
            else:
                evidence.extend(_collect_evidence(item))
    elif isinstance(value, list):
        for item in value:
            evidence.extend(_collect_evidence(item))
    return evidence


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.live_ollama:
        report = run_live_ollama_evaluation(args.live_project, args.live_scene)
    else:
        report = run_offline_fixture_evaluation(args.fixtures_dir)
    write_report(report, args.output, pretty=args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
