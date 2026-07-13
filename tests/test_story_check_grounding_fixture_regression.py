"""T002D deterministic fixture regressions for committed Story Check grounding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from backend.story_check_grounding_contract import build_story_check_source_snapshot
from backend.story_check_grounding_integration import (
    StoryCheckGroundingIntegrationError,
    ground_story_check_result,
)


FIXTURE_PATH = Path("tests/fixtures/story_check/grounding_regression_t002d.json")
OFFSET_BASIS = "utf-8-bytes-zero-based-half-open"


@pytest.fixture(scope="module")
def fixture_data() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def source_snapshot(data: dict, content_key: str = "source_content_lf"):
    return build_story_check_source_snapshot(
        project_id=data["project_id"],
        source_type="scene",
        source_id=data["source_id"],
        source_content=data[content_key],
    )


def evidence(source, case: dict, **overrides) -> dict:
    value = {
        "source_id": source.source_id,
        "source_sha256": source.source_sha256,
        "start_byte": case["start_byte"],
        "end_byte": case["end_byte"],
        "excerpt": case["excerpt"],
        "offset_basis": OFFSET_BASIS,
    }
    value.update(overrides)
    return value


def explicit_diagnostic(case: dict, evidence_items: list[dict]) -> dict:
    return {
        "diagnostic_id": case["diagnostic_id"],
        "classification": "factual_warning",
        "message": case["message"],
        "evidence": evidence_items,
    }


def grounded(payload: dict, source) -> dict:
    return ground_story_check_result(payload, source)["grounding"]


def test_exact_source_identity_ascii_unicode_lf_and_crlf(fixture_data):
    expected = fixture_data["expected_identity"]
    lf = source_snapshot(fixture_data)
    crlf = source_snapshot(fixture_data, "source_content_crlf")

    assert lf.source_sha256 == expected["lf_sha256"]
    assert lf.utf8_byte_length == expected["lf_utf8_byte_length"]
    assert crlf.source_sha256 == expected["crlf_sha256"]
    assert crlf.utf8_byte_length == expected["crlf_utf8_byte_length"]
    assert lf.source_sha256 == hashlib.sha256(lf.source_content.encode("utf-8")).hexdigest()
    assert crlf.source_sha256 == hashlib.sha256(crlf.source_content.encode("utf-8")).hexdigest()
    assert lf.source_sha256 != crlf.source_sha256

    unicode_bytes = "雨-café".encode("utf-8")
    start = lf.source_content.encode("utf-8").index(unicode_bytes)
    assert (start, start + len(unicode_bytes)) == (107, 116)
    assert lf.source_content.encode("utf-8")[107:116].decode("utf-8") == "雨-café"


def test_supported_unsupported_and_missing_factual_warnings(fixture_data):
    source = source_snapshot(fixture_data)
    supported = fixture_data["supported"]
    unsupported = fixture_data["unsupported"]
    missing = fixture_data["missing_evidence"]
    payload = {
        "grounding_diagnostics": [
            explicit_diagnostic(supported, [evidence(source, supported)]),
            explicit_diagnostic(unsupported, [evidence(source, unsupported)]),
            explicit_diagnostic(missing, []),
        ]
    }

    diagnostics = grounded(payload, source)["diagnostics"]
    assert [item["diagnostic_id"] for item in diagnostics] == [
        "supported-location",
        "unsupported-location",
        "missing-object",
    ]
    assert diagnostics[0]["verification_state"] == "verified"
    assert diagnostics[0]["validator_result"]["outcome"] == "supported"
    assert diagnostics[0]["evidence"] == [evidence(source, supported)]
    assert diagnostics[1]["verification_state"] == "quarantined"
    assert diagnostics[1]["validator_result"]["outcome"] == "unsupported"
    assert diagnostics[2]["verification_state"] == "quarantined"
    assert diagnostics[2]["validator_result"]["reason_codes"] == ["evidence_absent"]
    assert all(item["verification_state"] != "verified" for item in diagnostics[1:])


@pytest.mark.parametrize(
    "overrides",
    [
        {"start_byte": -1, "end_byte": 4},
        {"start_byte": 47, "end_byte": 25},
        {"start_byte": 0, "end_byte": 999},
        {"start_byte": 107, "end_byte": 108, "excerpt": ""},
        {"excerpt": "LOCATION_TOKEN=LOC-OTHER"},
    ],
    ids=["negative", "reversed", "outside", "split-multibyte", "excerpt-mismatch"],
)
def test_malformed_evidence_never_verifies(fixture_data, overrides):
    source = source_snapshot(fixture_data)
    case = fixture_data["supported"]
    result = grounded(
        {"grounding_diagnostics": [explicit_diagnostic(case, [evidence(source, case, **overrides)])]},
        source,
    )["diagnostics"][0]
    assert result["verification_state"] == "quarantined"
    assert result["validator_result"]["outcome"] != "supported"
    assert result["evidence"] == []


@pytest.mark.parametrize(
    ("identity", "reason"),
    [
        ({"source_id": "different-scene"}, "story_check_source_id_mismatch"),
        ({"source_sha256": "0" * 64}, "story_check_source_hash_mismatch"),
    ],
)
def test_envelope_source_mismatch_fails_closed(fixture_data, identity, reason):
    with pytest.raises(StoryCheckGroundingIntegrationError, match=reason):
        ground_story_check_result(
            {"source_identity": identity, "grounding_diagnostics": []},
            source_snapshot(fixture_data),
        )


def test_non_factual_diagnostics_are_retained_unverified(fixture_data):
    result = grounded(
        {"grounding_diagnostics": fixture_data["non_factual"]},
        source_snapshot(fixture_data),
    )
    assert [item["classification"] for item in result["diagnostics"]] == [
        "structural_diagnostic",
        "question",
        "observation",
    ]
    assert all(item["verification_state"] == "unverified" for item in result["diagnostics"])
    assert all(
        item["validator_result"]["outcome"] == "not_applicable"
        for item in result["diagnostics"]
    )


def test_legacy_malformed_and_unknown_producer_states_never_default_verified(fixture_data):
    source = source_snapshot(fixture_data)
    legacy = grounded({"warnings": ["[Factual] No envelope evidence."]}, source)
    malformed = grounded(
        {
            "warnings": ["[Factual] Malformed envelope fallback."],
            "grounding_diagnostics": [{"message": 7, "verification_state": "verified"}],
        },
        source,
    )
    unknown = grounded(
        {
            "grounding_diagnostics": [
                {
                    "diagnostic_id": "unknown-state",
                    "classification": "factual_warning",
                    "message": "Unknown producer state.",
                    "verification_state": "future_state",
                }
            ]
        },
        source,
    )
    for result in (legacy, malformed, unknown):
        assert result["diagnostics"]
        assert all(item["verification_state"] != "verified" for item in result["diagnostics"])


def test_fixture_execution_is_deterministic_and_has_no_persistence_effect(fixture_data, tmp_path):
    source = source_snapshot(fixture_data)
    supported = fixture_data["supported"]
    payload = {
        "grounding_diagnostics": [
            explicit_diagnostic(supported, [evidence(source, supported)]),
            *fixture_data["non_factual"],
        ]
    }
    state_files = {
        "scene.md": fixture_data["source_content_lf"],
        "candidates.json": "[]\n",
        "review-queue.json": "[]\n",
        "promotions.json": "[]\n",
        "apply-promotions.json": "[]\n",
        "memory-canon.json": "{}\n",
        "bible.json": "{}\n",
        "storyform.json": "{}\n",
    }
    for name, content in state_files.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    before = {path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())}

    results = [grounded(payload, source) for _ in range(5)]

    assert all(result == results[0] for result in results[1:])
    assert [item["diagnostic_id"] for item in results[0]["diagnostics"]] == [
        "supported-location",
        "structural-1",
        "question-1",
        "observation-1",
    ]
    assert json.dumps(results[0], ensure_ascii=False, sort_keys=True) == json.dumps(
        results[-1], ensure_ascii=False, sort_keys=True
    )
    after = {path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())}
    assert after == before
