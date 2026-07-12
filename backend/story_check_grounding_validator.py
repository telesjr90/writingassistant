"""Pure deterministic grounding validation for Story Check diagnostics.

Comparison normalization is deliberately conservative and is used only for
claim/evidence comparison.  It applies Unicode NFC normalization, Unicode
case-folding, collapses Unicode whitespace to one ASCII space, and maps curly
quotes plus Unicode dash variants to their ASCII comparison forms.  Every
other punctuation character remains significant.  No fuzzy matching,
stemming, synonym expansion, semantic model, or generated paraphrase is used.

The module performs no I/O and never mutates its inputs.  Exact source text,
diagnostic messages, and evidence excerpts remain owned by the T002A contract.
"""

from __future__ import annotations

from collections.abc import Sequence
import unicodedata

from .story_check_grounding_contract import (
    StoryCheckContractValidationError,
    StoryCheckDiagnostic,
    StoryCheckDiagnosticClassification,
    StoryCheckEvidenceReference,
    StoryCheckSourceIdentity,
    StoryCheckSourceSnapshot,
    StoryCheckValidatorOutcome,
    StoryCheckValidatorResult,
    StoryCheckVerificationState,
)


STORY_CHECK_GROUNDING_VALIDATOR_ID = "story_check_grounding_validator"
STORY_CHECK_GROUNDING_VALIDATOR_VERSION = "1"
STORY_CHECK_GROUNDING_COMPARISON_METHOD = (
    "unicode_nfc_casefold_whitespace_punctuation_v1"
)

REASON_EXACT_EVIDENCE_MATCHED = "exact_evidence_matched"
REASON_NORMALIZED_COMPARISON_MATCHED = "normalized_comparison_matched"
REASON_EVIDENCE_ABSENT = "evidence_absent"
REASON_EVIDENCE_INVALID = "evidence_invalid"
REASON_EXCERPT_MISMATCH = "excerpt_mismatch"
REASON_CLAIM_NOT_SUPPORTED = "claim_not_supported_by_evidence"
REASON_SOURCE_ID_MISMATCH = "source_id_mismatch"
REASON_SOURCE_HASH_MISMATCH = "source_hash_mismatch"
REASON_VALIDATION_NOT_APPLICABLE = "validation_not_applicable"
REASON_VALIDATION_NOT_RUN = "validation_not_run"

STORY_CHECK_GROUNDING_REASON_CODES = frozenset(
    {
        REASON_EXACT_EVIDENCE_MATCHED,
        REASON_NORMALIZED_COMPARISON_MATCHED,
        REASON_EVIDENCE_ABSENT,
        REASON_EVIDENCE_INVALID,
        REASON_EXCERPT_MISMATCH,
        REASON_CLAIM_NOT_SUPPORTED,
        REASON_SOURCE_ID_MISMATCH,
        REASON_SOURCE_HASH_MISMATCH,
        REASON_VALIDATION_NOT_APPLICABLE,
        REASON_VALIDATION_NOT_RUN,
    }
)

_REASON_ORDER = (
    REASON_EXACT_EVIDENCE_MATCHED,
    REASON_NORMALIZED_COMPARISON_MATCHED,
    REASON_EVIDENCE_ABSENT,
    REASON_EVIDENCE_INVALID,
    REASON_EXCERPT_MISMATCH,
    REASON_CLAIM_NOT_SUPPORTED,
    REASON_SOURCE_ID_MISMATCH,
    REASON_SOURCE_HASH_MISMATCH,
    REASON_VALIDATION_NOT_APPLICABLE,
    REASON_VALIDATION_NOT_RUN,
)

_COMPARISON_PUNCTUATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201b": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201f": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2212": "-",
    }
)


def normalize_story_check_grounding_text(value: str) -> str:
    """Return the stable comparison-only representation of ``value``."""

    if not isinstance(value, str):
        raise StoryCheckContractValidationError("comparison text must be a string")
    if "\x00" in value:
        raise StoryCheckContractValidationError("comparison text must not contain NUL")
    normalized = unicodedata.normalize("NFC", value).casefold()
    normalized = normalized.translate(_COMPARISON_PUNCTUATION)
    return " ".join(normalized.split())


def _ordered_reasons(reasons: set[str]) -> tuple[str, ...]:
    return tuple(reason for reason in _REASON_ORDER if reason in reasons)


def _bounded_representation(value: str) -> str | None:
    return value if len(value) <= 4096 else None


def _coerce_source_identity(
    source: StoryCheckSourceSnapshot | StoryCheckSourceIdentity,
) -> StoryCheckSourceIdentity:
    if isinstance(source, StoryCheckSourceSnapshot):
        return source.identity
    if isinstance(source, StoryCheckSourceIdentity):
        return source
    raise StoryCheckContractValidationError(
        "source must be a StoryCheckSourceSnapshot or StoryCheckSourceIdentity"
    )


def _coerce_classification(
    classification: StoryCheckDiagnosticClassification | str,
) -> StoryCheckDiagnosticClassification:
    try:
        return StoryCheckDiagnosticClassification(classification)
    except (TypeError, ValueError) as exc:
        raise StoryCheckContractValidationError(
            "classification must be a T002A StoryCheckDiagnosticClassification"
        ) from exc


def _coerce_evidence(
    evidence: Sequence[StoryCheckEvidenceReference],
) -> tuple[object, ...]:
    if isinstance(evidence, (str, bytes)) or not isinstance(evidence, Sequence):
        raise StoryCheckContractValidationError(
            "evidence must be an ordered sequence of T002A evidence references"
        )
    return tuple(evidence)


def _validate_reference_against_snapshot(
    snapshot: StoryCheckSourceSnapshot,
    reference: StoryCheckEvidenceReference,
) -> tuple[StoryCheckEvidenceReference | None, set[str]]:
    """Re-run T002A construction so no evidence field is repaired or trusted."""

    try:
        checked = StoryCheckEvidenceReference(
            snapshot,
            reference.start_byte,
            reference.end_byte,
            reference.excerpt,
            source_id=reference.source_id,
            source_sha256=reference.source_sha256,
            offset_basis=reference.offset_basis,
        )
    except (AttributeError, StoryCheckContractValidationError) as exc:
        reasons = {REASON_EVIDENCE_INVALID}
        if "excerpt does not exactly match" in str(exc):
            reasons.add(REASON_EXCERPT_MISMATCH)
        return None, reasons
    return checked, set()


def _evaluate_story_check_grounding(
    source: StoryCheckSourceSnapshot | StoryCheckSourceIdentity,
    classification: StoryCheckDiagnosticClassification | str,
    diagnostic_text: str,
    evidence: Sequence[StoryCheckEvidenceReference],
    *,
    validation_performed: bool,
    grounding_applicable: bool | None,
) -> tuple[
    StoryCheckValidatorResult,
    StoryCheckVerificationState,
    tuple[StoryCheckEvidenceReference, ...],
]:
    identity = _coerce_source_identity(source)
    checked_classification = _coerce_classification(classification)
    if not isinstance(diagnostic_text, str):
        raise StoryCheckContractValidationError("diagnostic_text must be a string")
    if "\x00" in diagnostic_text:
        raise StoryCheckContractValidationError("diagnostic_text must not contain NUL")
    if type(validation_performed) is not bool:
        raise StoryCheckContractValidationError("validation_performed must be a Boolean")
    if grounding_applicable is not None and type(grounding_applicable) is not bool:
        raise StoryCheckContractValidationError(
            "grounding_applicable must be a Boolean or None"
        )
    proposed = _coerce_evidence(evidence)

    factual = (
        checked_classification
        == StoryCheckDiagnosticClassification.FACTUAL_WARNING
    )
    applicable = factual if grounding_applicable is None else grounding_applicable

    # Claimed evidence is always checked before an applicability/not-run
    # outcome.  A caller cannot hide mismatched or malformed claimed evidence
    # behind those states.
    mismatch_reasons: set[str] = set()
    for reference in proposed:
        if not isinstance(reference, StoryCheckEvidenceReference):
            continue
        try:
            if reference.source_id != identity.source_id:
                mismatch_reasons.add(REASON_SOURCE_ID_MISMATCH)
            if reference.source_sha256 != identity.source_sha256:
                mismatch_reasons.add(REASON_SOURCE_HASH_MISMATCH)
        except AttributeError:
            continue
    if mismatch_reasons:
        result = StoryCheckValidatorResult(
            validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
            validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
            outcome=StoryCheckValidatorOutcome.SOURCE_MISMATCH,
            reason_codes=_ordered_reasons(mismatch_reasons),
            comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
        )
        return result, StoryCheckVerificationState.QUARANTINED, ()

    validated: list[StoryCheckEvidenceReference] = []
    invalid_reasons: set[str] = set()
    for reference in proposed:
        if not isinstance(reference, StoryCheckEvidenceReference):
            invalid_reasons.add(REASON_EVIDENCE_INVALID)
            continue
        if isinstance(source, StoryCheckSourceSnapshot):
            checked, reasons = _validate_reference_against_snapshot(source, reference)
            invalid_reasons.update(reasons)
            if checked is not None:
                validated.append(checked)
        else:
            # A genuine T002A value was already verified at construction.  Its
            # source identity was checked immediately above.
            validated.append(reference)

    if invalid_reasons:
        result = StoryCheckValidatorResult(
            validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
            validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
            outcome=StoryCheckValidatorOutcome.UNSUPPORTED,
            reason_codes=_ordered_reasons(invalid_reasons),
            comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
        )
        return result, StoryCheckVerificationState.QUARANTINED, ()

    if not validation_performed:
        result = StoryCheckValidatorResult(
            validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
            validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
            outcome=StoryCheckValidatorOutcome.NOT_RUN,
            reason_codes=(REASON_VALIDATION_NOT_RUN,),
            comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
        )
        return result, StoryCheckVerificationState.UNVERIFIED, tuple(validated)

    if not applicable and not factual:
        result = StoryCheckValidatorResult(
            validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
            validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
            outcome=StoryCheckValidatorOutcome.NOT_APPLICABLE,
            reason_codes=(REASON_VALIDATION_NOT_APPLICABLE,),
            comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
        )
        return result, StoryCheckVerificationState.UNVERIFIED, tuple(validated)

    # A factual warning is always applicable.  An explicit false override may
    # skip the comparison, but never produces T002A's NOT_APPLICABLE outcome.
    if factual and not applicable:
        result = StoryCheckValidatorResult(
            validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
            validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
            outcome=StoryCheckValidatorOutcome.NOT_RUN,
            reason_codes=(REASON_VALIDATION_NOT_RUN,),
            comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
        )
        return result, StoryCheckVerificationState.UNVERIFIED, tuple(validated)

    if not proposed:
        result = StoryCheckValidatorResult(
            validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
            validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
            outcome=StoryCheckValidatorOutcome.UNSUPPORTED,
            reason_codes=(REASON_EVIDENCE_ABSENT,),
            comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
            normalized_claim=_bounded_representation(
                normalize_story_check_grounding_text(diagnostic_text)
            ),
            normalized_source="",
        )
        return result, StoryCheckVerificationState.QUARANTINED, ()

    normalized_claim = normalize_story_check_grounding_text(diagnostic_text)
    normalized_excerpts = [
        normalize_story_check_grounding_text(reference.excerpt)
        for reference in validated
    ]
    normalized_source = "\n".join(normalized_excerpts)
    exact_match = any(
        diagnostic_text == reference.excerpt for reference in validated
    )
    normalized_match = any(
        normalized_claim == normalized_excerpt
        for normalized_excerpt in normalized_excerpts
    )
    reasons = {REASON_EXACT_EVIDENCE_MATCHED}
    if normalized_match and not exact_match:
        reasons.add(REASON_NORMALIZED_COMPARISON_MATCHED)

    if normalized_match:
        outcome = StoryCheckValidatorOutcome.SUPPORTED
        state = StoryCheckVerificationState.VERIFIED
    else:
        outcome = StoryCheckValidatorOutcome.UNSUPPORTED
        state = StoryCheckVerificationState.QUARANTINED
        reasons.add(REASON_CLAIM_NOT_SUPPORTED)

    result = StoryCheckValidatorResult(
        validator_id=STORY_CHECK_GROUNDING_VALIDATOR_ID,
        validator_version=STORY_CHECK_GROUNDING_VALIDATOR_VERSION,
        outcome=outcome,
        reason_codes=_ordered_reasons(reasons),
        comparison_method=STORY_CHECK_GROUNDING_COMPARISON_METHOD,
        normalized_claim=_bounded_representation(normalized_claim),
        normalized_source=_bounded_representation(normalized_source),
        direct_evidence_matched=True,
    )
    return result, state, tuple(validated)


def validate_story_check_grounding(
    source: StoryCheckSourceSnapshot | StoryCheckSourceIdentity,
    classification: StoryCheckDiagnosticClassification | str,
    diagnostic_text: str,
    evidence: Sequence[StoryCheckEvidenceReference] = (),
    *,
    validation_performed: bool = True,
    grounding_applicable: bool | None = None,
) -> tuple[StoryCheckValidatorResult, StoryCheckVerificationState]:
    """Validate one unchanged diagnostic claim against proposed T002A evidence.

    Non-factual classifications default to ``not_applicable``.  Pass
    ``grounding_applicable=True`` to ground one against direct evidence.
    ``validation_performed=False`` is the only ordinary path to ``not_run``.
    """

    result, state, _ = _evaluate_story_check_grounding(
        source,
        classification,
        diagnostic_text,
        evidence,
        validation_performed=validation_performed,
        grounding_applicable=grounding_applicable,
    )
    return result, state


def build_validated_story_check_diagnostic(
    source: StoryCheckSourceSnapshot | StoryCheckSourceIdentity,
    diagnostic_id: str,
    classification: StoryCheckDiagnosticClassification | str,
    message: str,
    evidence: Sequence[StoryCheckEvidenceReference] = (),
    *,
    validation_performed: bool = True,
    grounding_applicable: bool | None = None,
    producer: str = "story_check",
    producer_version: str | None = None,
) -> StoryCheckDiagnostic:
    """Construct a T002A diagnostic using only evidence that validated exactly."""

    identity = _coerce_source_identity(source)
    result, state, validated_evidence = _evaluate_story_check_grounding(
        source,
        classification,
        message,
        evidence,
        validation_performed=validation_performed,
        grounding_applicable=grounding_applicable,
    )
    return StoryCheckDiagnostic(
        diagnostic_id=diagnostic_id,
        classification=classification,
        message=message,
        source_identity=identity,
        verification_state=state,
        validator_result=result,
        evidence=validated_evidence,
        producer=producer,
        producer_version=producer_version,
    )


__all__ = [
    "STORY_CHECK_GROUNDING_COMPARISON_METHOD",
    "STORY_CHECK_GROUNDING_REASON_CODES",
    "STORY_CHECK_GROUNDING_VALIDATOR_ID",
    "STORY_CHECK_GROUNDING_VALIDATOR_VERSION",
    "build_validated_story_check_diagnostic",
    "normalize_story_check_grounding_text",
    "validate_story_check_grounding",
]
