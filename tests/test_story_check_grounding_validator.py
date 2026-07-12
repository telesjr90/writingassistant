import json
from pathlib import Path

import pytest

from backend.story_check_grounding_contract import (
    STORY_CHECK_OFFSET_BASIS,
    StoryCheckContractValidationError,
    StoryCheckEvidenceReference,
    build_story_check_evidence_reference,
    build_story_check_source_snapshot,
)
from backend.story_check_grounding_validator import (
    STORY_CHECK_GROUNDING_REASON_CODES,
    build_validated_story_check_diagnostic,
    normalize_story_check_grounding_text,
    validate_story_check_grounding,
)


def snapshot(text="The archive key is beneath the blue ledger.", **overrides):
    values = {
        "project_id": "example",
        "source_type": "scene",
        "source_id": "scene_001",
        "source_content": text,
    }
    values.update(overrides)
    return build_story_check_source_snapshot(**values)


def evidence(source, excerpt):
    source_bytes = source.source_content.encode("utf-8")
    excerpt_bytes = excerpt.encode("utf-8")
    start = source_bytes.index(excerpt_bytes)
    return build_story_check_evidence_reference(
        source, start, start + len(excerpt_bytes), excerpt
    )


def validate(source, message, items=(), classification="factual_warning", **kwargs):
    return validate_story_check_grounding(
        source, classification, message, items, **kwargs
    )


def forged_evidence(source, *, start=0, end=3, excerpt="bad"):
    item = object.__new__(StoryCheckEvidenceReference)
    values = {
        "source_id": source.source_id,
        "source_sha256": source.source_sha256,
        "start_byte": start,
        "end_byte": end,
        "excerpt": excerpt,
        "offset_basis": STORY_CHECK_OFFSET_BASIS,
    }
    for name, value in values.items():
        object.__setattr__(item, name, value)
    return item


def test_exact_ascii_evidence_support_is_verified():
    source = snapshot("alpha beta")
    item = evidence(source, "alpha beta")
    result, state = validate(source, "alpha beta", (item,))
    assert result.outcome.value == "supported"
    assert state.value == "verified"
    assert result.reason_codes == ("exact_evidence_matched",)
    assert result.direct_evidence_matched is True


def test_multibyte_utf8_evidence_support_and_exact_identity():
    source = snapshot("A café 雨 ends")
    item = evidence(source, "café 雨")
    result, state = validate(source.identity, "café 雨", (item,))
    assert (item.start_byte, item.end_byte) == (2, 11)
    assert result.outcome.value == "supported"
    assert state.value == "verified"


def test_source_id_mismatch_is_quarantined():
    selected = snapshot("alpha", source_id="selected")
    other = snapshot("alpha", source_id="other")
    result, state = validate(selected, "alpha", (evidence(other, "alpha"),))
    assert result.outcome.value == "source_mismatch"
    assert result.reason_codes == ("source_id_mismatch",)
    assert state.value == "quarantined"


def test_source_hash_mismatch_is_quarantined():
    selected = snapshot("alpha")
    changed = snapshot("changed")
    result, state = validate(selected, "changed", (evidence(changed, "changed"),))
    assert result.outcome.value == "source_mismatch"
    assert result.reason_codes == ("source_hash_mismatch",)
    assert state.value == "quarantined"


def test_source_id_and_hash_reason_order_is_stable():
    selected = snapshot("alpha", source_id="selected")
    other = snapshot("other", source_id="other")
    first = validate(selected, "other", (evidence(other, "other"),))[0]
    second = validate(selected, "other", (evidence(other, "other"),))[0]
    assert first.reason_codes == (
        "source_id_mismatch",
        "source_hash_mismatch",
    )
    assert second.reason_codes == first.reason_codes


def test_excerpt_mismatch_and_invalid_byte_ranges_fail_closed():
    source = snapshot("alpha")
    mismatch = forged_evidence(source, start=0, end=5, excerpt="ALPHA")
    mismatch_result, mismatch_state = validate(source, "alpha", (mismatch,))
    assert mismatch_result.reason_codes == ("evidence_invalid", "excerpt_mismatch")
    assert mismatch_state.value == "quarantined"

    invalid = forged_evidence(source, start=-1, end=99, excerpt="alpha")
    invalid_result, invalid_state = validate(source, "alpha", (invalid,))
    assert invalid_result.reason_codes == ("evidence_invalid",)
    assert invalid_state.value == "quarantined"


def test_evidence_absent_factual_warning_is_unsupported_and_quarantined():
    result, state = validate(snapshot(), "Missing key")
    assert result.outcome.value == "unsupported"
    assert result.reason_codes == ("evidence_absent",)
    assert state.value == "quarantined"


def test_valid_evidence_that_does_not_support_claim_is_quarantined():
    source = snapshot("The key is present.")
    item = evidence(source, "The key is present.")
    result, state = validate(source, "The key is absent.", (item,))
    assert result.outcome.value == "unsupported"
    assert result.reason_codes == (
        "exact_evidence_matched",
        "claim_not_supported_by_evidence",
    )
    assert result.direct_evidence_matched is True
    assert state.value == "quarantined"


def test_case_whitespace_and_documented_punctuation_normalization():
    source = snapshot("MARA\u2019S  KEY\u2014IS HERE")
    item = evidence(source, "MARA\u2019S  KEY\u2014IS HERE")
    claim = "mara's\nkey-is here"
    result, state = validate(source, claim, (item,))
    assert normalize_story_check_grounding_text(claim) == "mara's key-is here"
    assert result.outcome.value == "supported"
    assert result.reason_codes == (
        "exact_evidence_matched",
        "normalized_comparison_matched",
    )
    assert result.normalized_claim == result.normalized_source
    assert state.value == "verified"


@pytest.mark.parametrize(
    ("claim", "source_text"),
    [
        ("Wait!", "Wait."),
        ("archive key", "vault key"),
        ("The key is missing", "The key is absent"),
        ("color", "colour"),
    ],
)
def test_other_punctuation_fuzzy_and_synonym_inference_are_not_used(
    claim, source_text
):
    source = snapshot(source_text)
    result, state = validate(source, claim, (evidence(source, source_text),))
    assert result.outcome.value == "unsupported"
    assert state.value == "quarantined"


def test_factual_warning_not_run_cannot_be_verified_or_not_applicable():
    source = snapshot("alpha")
    result, state = validate(
        source,
        "alpha",
        (evidence(source, "alpha"),),
        validation_performed=False,
    )
    assert result.outcome.value == "not_run"
    assert result.reason_codes == ("validation_not_run",)
    assert state.value == "unverified"

    overridden, overridden_state = validate(
        source, "alpha", grounding_applicable=False
    )
    assert overridden.outcome.value == "not_run"
    assert overridden_state.value == "unverified"


@pytest.mark.parametrize(
    "classification", ["structural_diagnostic", "question", "observation"]
)
def test_non_factual_not_applicable_is_preserved_unverified(classification):
    result, state = validate(
        snapshot(), "Useful diagnostic", classification=classification
    )
    assert result.outcome.value == "not_applicable"
    assert result.reason_codes == ("validation_not_applicable",)
    assert state.value == "unverified"


def test_non_factual_supported_evidence_when_explicitly_applicable():
    source = snapshot("Is the key here?")
    item = evidence(source, "Is the key here?")
    result, state = validate(
        source,
        "Is the key here?",
        (item,),
        classification="question",
        grounding_applicable=True,
    )
    assert result.outcome.value == "supported"
    assert state.value == "verified"


def test_non_factual_invalid_or_mismatched_claimed_evidence_is_quarantined():
    source = snapshot("alpha")
    invalid = forged_evidence(source, start=0, end=5, excerpt="ALPHA")
    invalid_result, invalid_state = validate(
        source, "Observation", (invalid,), classification="observation"
    )
    assert invalid_result.reason_codes == ("evidence_invalid", "excerpt_mismatch")
    assert invalid_state.value == "quarantined"

    other = snapshot("alpha", source_id="other")
    mismatch_result, mismatch_state = validate(
        source,
        "Observation",
        (evidence(other, "alpha"),),
        classification="observation",
    )
    assert mismatch_result.outcome.value == "source_mismatch"
    assert mismatch_state.value == "quarantined"


def test_builder_preserves_exact_message_excerpt_and_source_text():
    source_text = "  café\r\nkey  "
    message = "café\r\nkey"
    source = snapshot(source_text)
    item = evidence(source, message)
    before_source = source.to_dict()
    before_evidence = item.to_dict()
    diagnostic = build_validated_story_check_diagnostic(
        source,
        "diag-1",
        "factual_warning",
        message,
        (item,),
    )
    assert diagnostic.message == message
    assert diagnostic.evidence[0].excerpt == message
    assert source.source_content == source_text
    assert source.to_dict() == before_source
    assert item.to_dict() == before_evidence


def test_builder_quarantines_invalid_claimed_evidence_without_repair():
    source = snapshot("alpha")
    bad = forged_evidence(source, start=0, end=5, excerpt="ALPHA")
    diagnostic = build_validated_story_check_diagnostic(
        source, "diag-1", "factual_warning", "alpha", (bad,)
    )
    assert diagnostic.verification_state.value == "quarantined"
    assert diagnostic.evidence == ()
    assert diagnostic.validator_result.reason_codes == (
        "evidence_invalid",
        "excerpt_mismatch",
    )


def test_repeated_calls_and_serialization_are_deterministic():
    source = snapshot("Alpha  beta")
    item = evidence(source, "Alpha  beta")
    first = build_validated_story_check_diagnostic(
        source, "diag-1", "factual_warning", "alpha beta", (item,)
    )
    second = build_validated_story_check_diagnostic(
        source, "diag-1", "factual_warning", "alpha beta", (item,)
    )
    assert first.to_dict() == second.to_dict()
    assert first.to_json() == second.to_json()
    assert json.loads(first.to_json()) == first.to_dict()
    assert tuple(first.validator_result.reason_codes) == (
        "exact_evidence_matched",
        "normalized_comparison_matched",
    )


def test_reason_codes_are_closed_and_every_emitted_code_is_declared():
    assert STORY_CHECK_GROUNDING_REASON_CODES == {
        "exact_evidence_matched",
        "normalized_comparison_matched",
        "evidence_absent",
        "evidence_invalid",
        "excerpt_mismatch",
        "claim_not_supported_by_evidence",
        "source_id_mismatch",
        "source_hash_mismatch",
        "validation_not_applicable",
        "validation_not_run",
    }


def test_validator_has_no_filesystem_network_model_tool_or_persistence_effects(tmp_path):
    before = list(tmp_path.iterdir())
    source = snapshot("alpha")
    item = evidence(source, "alpha")
    validate(source, "alpha", (item,))
    assert list(tmp_path.iterdir()) == before

    module_text = Path("backend/story_check_grounding_validator.py").read_text(
        encoding="utf-8"
    )
    for prohibited in (
        "import os",
        "import socket",
        "import requests",
        "import subprocess",
        "analysis_engine",
        "project_manager",
        "ollama",
        "open(",
        "write_text",
        "write_bytes",
    ):
        assert prohibited not in module_text.lower()


def test_invalid_public_inputs_use_t002a_contract_error():
    with pytest.raises(StoryCheckContractValidationError):
        validate_story_check_grounding(snapshot(), "made_up", "claim")
    with pytest.raises(StoryCheckContractValidationError):
        validate_story_check_grounding(snapshot(), "factual_warning", 1)  # type: ignore[arg-type]
    with pytest.raises(StoryCheckContractValidationError):
        validate_story_check_grounding(snapshot(), "factual_warning", "claim", "bad")  # type: ignore[arg-type]
