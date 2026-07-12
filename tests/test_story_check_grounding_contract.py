import hashlib
import json
from pathlib import Path

import pytest

from backend.story_check_grounding_contract import (
    STORY_CHECK_HASH_BASIS,
    STORY_CHECK_OFFSET_BASIS,
    StoryCheckContractValidationError,
    StoryCheckDiagnostic,
    StoryCheckDiagnosticClassification,
    StoryCheckDiagnosticResult,
    StoryCheckEvidenceReference,
    StoryCheckValidatorResult,
    build_story_check_evidence_reference,
    build_story_check_source_snapshot,
    compute_story_check_source_sha256,
)


def snapshot(text: str = "The pea was beneath twenty mattresses.", **overrides):
    values = {
        "project_id": "example",
        "source_type": "scene",
        "source_id": "scene_001",
        "source_content": text,
    }
    values.update(overrides)
    return build_story_check_source_snapshot(**values)


def validator(
    outcome: str,
    *,
    matched: bool = False,
    reason_code: str | None = None,
) -> StoryCheckValidatorResult:
    return StoryCheckValidatorResult(
        validator_id="story_check_grounding_validator",
        validator_version="1",
        outcome=outcome,
        reason_codes=(reason_code or outcome,),
        comparison_method="exact_utf8_evidence",
        normalized_claim=None,
        normalized_source=None,
        direct_evidence_matched=matched,
    )


def evidence(source=None, excerpt="pea"):
    source = source or snapshot()
    source_bytes = source.source_content.encode("utf-8")
    excerpt_bytes = excerpt.encode("utf-8")
    start = source_bytes.index(excerpt_bytes)
    return build_story_check_evidence_reference(
        source, start, start + len(excerpt_bytes), excerpt
    )


def diagnostic(
    source=None,
    *,
    classification="observation",
    state="unverified",
    outcome="not_run",
    evidence_items=(),
    matched=False,
    diagnostic_id="diag-1",
    message="Exact diagnostic text.  ",
):
    source = source or snapshot()
    return StoryCheckDiagnostic(
        diagnostic_id=diagnostic_id,
        classification=classification,
        message=message,
        source_identity=source.identity,
        verification_state=state,
        validator_result=validator(outcome, matched=matched),
        evidence=evidence_items,
    )


@pytest.mark.parametrize(
    "text",
    [
        "ordinary UTF-8 text",
        "",
        "  leading and trailing  ",
        "first\n\nthird",
        "café — 雨",
    ],
)
def test_exact_source_hash_matches_direct_sha256(text):
    assert compute_story_check_source_sha256(text) == hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("line one\nline two", "line one\r\nline two"),
        ("é", "e\u0301"),
        ("Wait.", "Wait!"),
        ("last line", "last line\n"),
        (" leading", "leading"),
    ],
)
def test_byte_level_source_differences_change_hash(left, right):
    assert compute_story_check_source_sha256(left) != compute_story_check_source_sha256(
        right
    )


def test_hash_helper_is_deterministic_lowercase_hex_and_rejects_non_string():
    first = compute_story_check_source_sha256("Repeat me")
    assert first == compute_story_check_source_sha256("Repeat me")
    assert len(first) == 64
    assert first == first.lower()
    assert set(first) <= set("0123456789abcdef")
    with pytest.raises(StoryCheckContractValidationError):
        compute_story_check_source_sha256(123)  # type: ignore[arg-type]


def test_snapshot_preserves_exact_content_and_builds_content_identity():
    text = "  café\r\n\r\nend\n"
    source = snapshot(text)
    identity = source.identity

    assert source.source_content == text
    assert source.utf8_byte_length == len(text.encode("utf-8"))
    assert source.source_sha256 == compute_story_check_source_sha256(text)
    assert source.hash_algorithm == "sha256"
    assert source.hash_basis == STORY_CHECK_HASH_BASIS
    assert source.project_id == "example"
    assert source.source_id == "scene_001"
    assert source.source_type.value == "scene"
    assert identity.source_id == source.source_id
    assert identity.source_type.value == "scene"
    assert "source_content" not in identity.to_dict()
    assert text not in identity.to_json()


def test_snapshot_cannot_accept_caller_supplied_hash_and_rejects_absolute_ids():
    with pytest.raises(TypeError):
        build_story_check_source_snapshot(
            "example",
            "scene",
            "scene_001",
            "content",
            source_sha256="0" * 64,  # type: ignore[call-arg]
        )
    with pytest.raises(StoryCheckContractValidationError):
        snapshot(project_id="/home/owner/project")
    with pytest.raises(StoryCheckContractValidationError):
        snapshot(source_id=r"C:\owner\scene.md")


def test_snapshot_serialization_contains_no_absolute_path_metadata():
    serialized = snapshot().to_dict()
    assert all(not key.endswith("path") for key in serialized)
    assert "/home/" not in json.dumps(serialized)


def test_valid_ascii_evidence_uses_zero_based_half_open_bytes():
    source = snapshot("alpha beta")
    reference = StoryCheckEvidenceReference(source, 6, 10, "beta")
    assert reference.start_byte == 6
    assert reference.end_byte == 10
    assert reference.offset_basis == STORY_CHECK_OFFSET_BASIS
    assert source.source_content.encode("utf-8")[6:10].decode("utf-8") == "beta"


def test_valid_multibyte_evidence_uses_utf8_byte_offsets():
    source = snapshot("A café 雨 ends")
    reference = evidence(source, "café 雨")
    assert reference.start_byte == 2
    assert reference.end_byte == 11
    assert reference.excerpt == "café 雨"


@pytest.mark.parametrize(
    ("start", "end", "excerpt"),
    [
        (-1, 1, "a"),
        (1, 1, ""),
        (0, 99, "alpha beta"),
    ],
)
def test_invalid_evidence_bounds_are_rejected(start, end, excerpt):
    with pytest.raises(StoryCheckContractValidationError):
        StoryCheckEvidenceReference(snapshot("alpha beta"), start, end, excerpt)


def test_range_splitting_multibyte_character_is_rejected():
    with pytest.raises(StoryCheckContractValidationError, match="UTF-8 character"):
        StoryCheckEvidenceReference(snapshot("é"), 0, 1, "")


def test_excerpt_mismatch_is_rejected_without_correction():
    with pytest.raises(StoryCheckContractValidationError, match="exactly match"):
        StoryCheckEvidenceReference(snapshot("alpha beta"), 0, 5, "ALPHA")


def test_evidence_source_id_and_hash_mismatches_are_rejected():
    source = snapshot("alpha beta")
    with pytest.raises(StoryCheckContractValidationError, match="source_id mismatch"):
        build_story_check_evidence_reference(
            source, 0, 5, "alpha", source_id="scene_002"
        )
    with pytest.raises(StoryCheckContractValidationError, match="source_sha256 mismatch"):
        build_story_check_evidence_reference(
            source, 0, 5, "alpha", source_sha256="0" * 64
        )


@pytest.mark.parametrize(
    "classification",
    ["factual_warning", "structural_diagnostic", "question", "observation"],
)
def test_closed_diagnostic_classifications_are_accepted(classification):
    assert diagnostic(classification=classification).classification.value == classification


def test_arbitrary_diagnostic_classification_is_rejected():
    with pytest.raises(StoryCheckContractValidationError):
        diagnostic(classification="confident_fact")


def test_supported_factual_warning_with_valid_evidence_may_be_verified():
    source = snapshot()
    item = evidence(source)
    result = diagnostic(
        source,
        classification="factual_warning",
        state="verified",
        outcome="supported",
        evidence_items=(item,),
        matched=True,
    )
    assert result.verification_state.value == "verified"


@pytest.mark.parametrize(
    ("outcome", "matched"),
    [("supported", True), ("not_run", False), ("not_applicable", False)],
)
def test_factual_warning_without_required_validation_cannot_be_verified(
    outcome, matched
):
    with pytest.raises(StoryCheckContractValidationError):
        diagnostic(
            classification="factual_warning",
            state="verified",
            outcome=outcome,
            matched=matched,
        )


def test_unsupported_factual_warning_must_be_quarantined():
    with pytest.raises(StoryCheckContractValidationError):
        diagnostic(
            classification="factual_warning",
            state="unverified",
            outcome="unsupported",
        )
    quarantined = diagnostic(
        classification="factual_warning",
        state="quarantined",
        outcome="unsupported",
    )
    assert quarantined.verification_state.value == "quarantined"


def test_source_mismatch_must_be_quarantined_for_every_classification():
    with pytest.raises(StoryCheckContractValidationError):
        diagnostic(state="unverified", outcome="source_mismatch")
    assert (
        diagnostic(state="quarantined", outcome="source_mismatch")
        .verification_state.value
        == "quarantined"
    )


def test_invalid_evidence_cannot_coexist_with_verified_state():
    source = snapshot("alpha beta")
    with pytest.raises(StoryCheckContractValidationError):
        bad_evidence = StoryCheckEvidenceReference(source, 0, 5, "wrong")
        diagnostic(
            source,
            classification="factual_warning",
            state="verified",
            outcome="supported",
            evidence_items=(bad_evidence,),
            matched=True,
        )


@pytest.mark.parametrize("classification", ["structural_diagnostic", "question", "observation"])
def test_non_factual_diagnostic_may_be_unverified_when_not_applicable(classification):
    result = diagnostic(classification=classification, outcome="not_applicable")
    assert result.verification_state.value == "unverified"


def test_envelope_rejects_mixed_source_diagnostics():
    first = snapshot("first", source_id="scene_001")
    second = snapshot("second", source_id="scene_002")
    with pytest.raises(StoryCheckContractValidationError, match="exact Story Check source"):
        StoryCheckDiagnosticResult(first.identity, [diagnostic(second)])


def test_envelope_rejects_same_id_with_different_source_hash():
    first = snapshot("first")
    changed = snapshot("changed")
    with pytest.raises(StoryCheckContractValidationError):
        StoryCheckDiagnosticResult(first.identity, [diagnostic(changed)])


def test_deterministic_serialization_preserves_order_and_exact_strings():
    source = snapshot("alpha  beta\n")
    item = evidence(source, "alpha  beta")
    message = "Exact  diagnostic\ntext.  "
    first = diagnostic(
        source,
        classification="factual_warning",
        state="verified",
        outcome="supported",
        evidence_items=(item,),
        matched=True,
        diagnostic_id="diag-1",
        message=message,
    )
    second = diagnostic(source, diagnostic_id="diag-2", message="Second")
    result = StoryCheckDiagnosticResult(source.identity, [first, second])

    assert result.to_json() == result.to_json()
    serialized = result.to_dict()
    assert [item["diagnostic_id"] for item in serialized["diagnostics"]] == [
        "diag-1",
        "diag-2",
    ]
    assert serialized["diagnostics"][0]["message"] == message
    assert serialized["diagnostics"][0]["evidence"][0]["excerpt"] == "alpha  beta"
    assert json.loads(result.to_json()) == serialized


def test_result_boundary_is_analysis_only_non_canon_and_not_owner_approved():
    source = snapshot()
    serialized = StoryCheckDiagnosticResult(
        source.identity, [diagnostic(source)]
    ).to_dict()
    assert serialized["boundary"] == {
        "analytical_output": True,
        "non_canon": True,
        "owner_approved": False,
    }
    forbidden_keys = {
        "canon_status",
        "approval",
        "promotion",
        "promotion_eligibility",
        "apply_promotion",
        "mutation",
        "memory",
    }
    assert not forbidden_keys.intersection(serialized)


def test_unknown_fields_are_rejected_and_contract_has_no_external_side_effects(tmp_path):
    before = list(tmp_path.iterdir())
    with pytest.raises(TypeError):
        build_story_check_source_snapshot(
            "example", "scene", "scene_001", "text", unknown=True  # type: ignore[call-arg]
        )

    source = snapshot("text")
    result = StoryCheckDiagnosticResult(source.identity, [diagnostic(source)])
    result.to_json()

    assert list(tmp_path.iterdir()) == before
    module_text = Path(
        "backend/story_check_grounding_contract.py"
    ).read_text(encoding="utf-8")
    for prohibited_import in (
        "import requests",
        "import socket",
        "import subprocess",
        "project_manager",
        "analysis_engine",
    ):
        assert prohibited_import not in module_text
