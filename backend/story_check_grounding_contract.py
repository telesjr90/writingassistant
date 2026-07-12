"""Pure Story Check source-grounding and diagnostic data contracts.

This module defines values only.  It does not load projects, invoke Story Check,
call a model or tool, persist results, or mutate project state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from pathlib import PurePosixPath, PureWindowsPath
import re
from typing import Any, Sequence


STORY_CHECK_HASH_ALGORITHM = "sha256"
STORY_CHECK_HASH_BASIS = "utf-8-exact"
STORY_CHECK_OFFSET_BASIS = "utf-8-bytes-zero-based-half-open"
STORY_CHECK_CONTRACT_VERSION = "story-check-grounding-contract.v1"
STORY_CHECK_SOURCE_KIND = "owner-authored source"

_DIAGNOSTIC_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_REASON_CODE_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")


class StoryCheckContractValidationError(ValueError):
    """Raised when a Story Check grounding value violates the contract."""


class StoryCheckSourceType(str, Enum):
    SCENE = "scene"


class StoryCheckDiagnosticClassification(str, Enum):
    FACTUAL_WARNING = "factual_warning"
    STRUCTURAL_DIAGNOSTIC = "structural_diagnostic"
    QUESTION = "question"
    OBSERVATION = "observation"


class StoryCheckValidatorOutcome(str, Enum):
    NOT_RUN = "not_run"
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    SOURCE_MISMATCH = "source_mismatch"
    NOT_APPLICABLE = "not_applicable"


class StoryCheckVerificationState(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    QUARANTINED = "quarantined"


def _require_string(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise StoryCheckContractValidationError(f"{field_name} must be a string")
    if not allow_empty and not value:
        raise StoryCheckContractValidationError(f"{field_name} must not be empty")
    if "\x00" in value:
        raise StoryCheckContractValidationError(f"{field_name} must not contain NUL")
    return value


def _require_non_absolute_identifier(value: object, field_name: str) -> str:
    identifier = _require_string(value, field_name)
    if PurePosixPath(identifier).is_absolute() or PureWindowsPath(identifier).is_absolute():
        raise StoryCheckContractValidationError(
            f"{field_name} must not be an absolute filesystem path"
        )
    return identifier


def _enum_value(enum_type: type[Enum], value: object, field_name: str) -> Any:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(member.value for member in enum_type)
        raise StoryCheckContractValidationError(
            f"{field_name} must be one of: {allowed}"
        ) from exc


class _StoryCheckSerializable:
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )


def compute_story_check_source_sha256(source_text: str) -> str:
    """Return SHA-256 of the exact string encoded directly as UTF-8."""

    text = _require_string(source_text, "source_text", allow_empty=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True, init=False)
class StoryCheckSourceSnapshot(_StoryCheckSerializable):
    project_id: str
    source_type: StoryCheckSourceType
    source_kind: str
    source_id: str
    source_content: str
    source_sha256: str
    utf8_byte_length: int
    hash_algorithm: str
    hash_basis: str

    def __init__(
        self,
        project_id: str,
        source_type: StoryCheckSourceType | str,
        source_id: str,
        source_content: str,
        *,
        source_kind: str = STORY_CHECK_SOURCE_KIND,
    ) -> None:
        project = _require_non_absolute_identifier(project_id, "project_id")
        checked_source_id = _require_non_absolute_identifier(source_id, "source_id")
        checked_source_type = _enum_value(
            StoryCheckSourceType, source_type, "source_type"
        )
        checked_source_kind = _require_string(source_kind, "source_kind")
        content = _require_string(source_content, "source_content", allow_empty=True)
        encoded = content.encode("utf-8")

        object.__setattr__(self, "project_id", project)
        object.__setattr__(self, "source_type", checked_source_type)
        object.__setattr__(self, "source_kind", checked_source_kind)
        object.__setattr__(self, "source_id", checked_source_id)
        object.__setattr__(self, "source_content", content)
        object.__setattr__(self, "source_sha256", hashlib.sha256(encoded).hexdigest())
        object.__setattr__(self, "utf8_byte_length", len(encoded))
        object.__setattr__(self, "hash_algorithm", STORY_CHECK_HASH_ALGORITHM)
        object.__setattr__(self, "hash_basis", STORY_CHECK_HASH_BASIS)

    @property
    def identity(self) -> "StoryCheckSourceIdentity":
        return StoryCheckSourceIdentity._from_snapshot(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "source_type": self.source_type.value,
            "source_kind": self.source_kind,
            "source_id": self.source_id,
            "source_content": self.source_content,
            "source_sha256": self.source_sha256,
            "utf8_byte_length": self.utf8_byte_length,
            "hash_algorithm": self.hash_algorithm,
            "hash_basis": self.hash_basis,
        }


def build_story_check_source_snapshot(
    project_id: str,
    source_type: StoryCheckSourceType | str,
    source_id: str,
    source_content: str,
    *,
    source_kind: str = STORY_CHECK_SOURCE_KIND,
) -> StoryCheckSourceSnapshot:
    return StoryCheckSourceSnapshot(
        project_id=project_id,
        source_type=source_type,
        source_id=source_id,
        source_content=source_content,
        source_kind=source_kind,
    )


@dataclass(frozen=True, init=False)
class StoryCheckSourceIdentity(_StoryCheckSerializable):
    project_id: str
    source_type: StoryCheckSourceType
    source_kind: str
    source_id: str
    source_sha256: str
    utf8_byte_length: int
    hash_algorithm: str
    hash_basis: str

    @classmethod
    def _from_snapshot(
        cls, snapshot: StoryCheckSourceSnapshot
    ) -> "StoryCheckSourceIdentity":
        if not isinstance(snapshot, StoryCheckSourceSnapshot):
            raise StoryCheckContractValidationError(
                "identity requires a StoryCheckSourceSnapshot"
            )
        identity = object.__new__(cls)
        for field_name in (
            "project_id",
            "source_type",
            "source_kind",
            "source_id",
            "source_sha256",
            "utf8_byte_length",
            "hash_algorithm",
            "hash_basis",
        ):
            object.__setattr__(identity, field_name, getattr(snapshot, field_name))
        return identity

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "source_type": self.source_type.value,
            "source_kind": self.source_kind,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "utf8_byte_length": self.utf8_byte_length,
            "hash_algorithm": self.hash_algorithm,
            "hash_basis": self.hash_basis,
        }


@dataclass(frozen=True, init=False)
class StoryCheckEvidenceReference(_StoryCheckSerializable):
    source_id: str
    source_sha256: str
    start_byte: int
    end_byte: int
    excerpt: str
    offset_basis: str

    def __init__(
        self,
        snapshot: StoryCheckSourceSnapshot,
        start_byte: int,
        end_byte: int,
        excerpt: str,
        *,
        source_id: str | None = None,
        source_sha256: str | None = None,
        offset_basis: str = STORY_CHECK_OFFSET_BASIS,
    ) -> None:
        if not isinstance(snapshot, StoryCheckSourceSnapshot):
            raise StoryCheckContractValidationError(
                "evidence requires a StoryCheckSourceSnapshot"
            )
        if type(start_byte) is not int or start_byte < 0:
            raise StoryCheckContractValidationError(
                "start_byte must be a non-negative integer"
            )
        if type(end_byte) is not int or end_byte <= start_byte:
            raise StoryCheckContractValidationError(
                "end_byte must be an integer greater than start_byte"
            )
        if end_byte > snapshot.utf8_byte_length:
            raise StoryCheckContractValidationError(
                "end_byte exceeds the exact UTF-8 source byte length"
            )
        checked_excerpt = _require_string(excerpt, "excerpt", allow_empty=True)
        if offset_basis != STORY_CHECK_OFFSET_BASIS:
            raise StoryCheckContractValidationError("unsupported evidence offset_basis")
        if source_id is not None and source_id != snapshot.source_id:
            raise StoryCheckContractValidationError("evidence source_id mismatch")
        if source_sha256 is not None and source_sha256 != snapshot.source_sha256:
            raise StoryCheckContractValidationError("evidence source_sha256 mismatch")

        source_bytes = snapshot.source_content.encode("utf-8")
        try:
            decoded = source_bytes[start_byte:end_byte].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise StoryCheckContractValidationError(
                "evidence byte range splits a UTF-8 character"
            ) from exc
        if decoded != checked_excerpt:
            raise StoryCheckContractValidationError(
                "evidence excerpt does not exactly match the UTF-8 byte range"
            )

        object.__setattr__(self, "source_id", snapshot.source_id)
        object.__setattr__(self, "source_sha256", snapshot.source_sha256)
        object.__setattr__(self, "start_byte", start_byte)
        object.__setattr__(self, "end_byte", end_byte)
        object.__setattr__(self, "excerpt", checked_excerpt)
        object.__setattr__(self, "offset_basis", STORY_CHECK_OFFSET_BASIS)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "start_byte": self.start_byte,
            "end_byte": self.end_byte,
            "excerpt": self.excerpt,
            "offset_basis": self.offset_basis,
        }


def build_story_check_evidence_reference(
    snapshot: StoryCheckSourceSnapshot,
    start_byte: int,
    end_byte: int,
    excerpt: str,
    *,
    source_id: str | None = None,
    source_sha256: str | None = None,
) -> StoryCheckEvidenceReference:
    return StoryCheckEvidenceReference(
        snapshot=snapshot,
        start_byte=start_byte,
        end_byte=end_byte,
        excerpt=excerpt,
        source_id=source_id,
        source_sha256=source_sha256,
    )


@dataclass(frozen=True)
class StoryCheckValidatorResult(_StoryCheckSerializable):
    validator_id: str
    validator_version: str
    outcome: StoryCheckValidatorOutcome | str
    reason_codes: tuple[str, ...]
    comparison_method: str
    normalized_claim: str | None = None
    normalized_source: str | None = None
    direct_evidence_matched: bool = False
    detail: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "validator_id", _require_string(self.validator_id, "validator_id")
        )
        object.__setattr__(
            self,
            "validator_version",
            _require_string(self.validator_version, "validator_version"),
        )
        object.__setattr__(
            self,
            "outcome",
            _enum_value(StoryCheckValidatorOutcome, self.outcome, "outcome"),
        )
        if not isinstance(self.reason_codes, tuple):
            raise StoryCheckContractValidationError("reason_codes must be an ordered tuple")
        if not self.reason_codes:
            raise StoryCheckContractValidationError("reason_codes must not be empty")
        if len(self.reason_codes) > 16 or len(set(self.reason_codes)) != len(
            self.reason_codes
        ):
            raise StoryCheckContractValidationError(
                "reason_codes must be unique and contain at most 16 items"
            )
        for reason_code in self.reason_codes:
            if not isinstance(reason_code, str) or not _REASON_CODE_PATTERN.fullmatch(
                reason_code
            ):
                raise StoryCheckContractValidationError(
                    "reason_codes must be lowercase machine-readable identifiers"
                )
        object.__setattr__(
            self,
            "comparison_method",
            _require_string(self.comparison_method, "comparison_method"),
        )
        for field_name in ("normalized_claim", "normalized_source", "detail"):
            value = getattr(self, field_name)
            if value is not None:
                checked = _require_string(value, field_name, allow_empty=True)
                limit = 512 if field_name == "detail" else 4096
                if len(checked) > limit:
                    raise StoryCheckContractValidationError(
                        f"{field_name} exceeds its bounded length"
                    )
        if type(self.direct_evidence_matched) is not bool:
            raise StoryCheckContractValidationError(
                "direct_evidence_matched must be a Boolean"
            )
        if (
            self.outcome
            in {
                StoryCheckValidatorOutcome.NOT_RUN,
                StoryCheckValidatorOutcome.NOT_APPLICABLE,
                StoryCheckValidatorOutcome.SOURCE_MISMATCH,
            }
            and self.direct_evidence_matched
        ):
            raise StoryCheckContractValidationError(
                "validator outcome cannot claim a direct evidence match"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "validator_id": self.validator_id,
            "validator_version": self.validator_version,
            "outcome": self.outcome.value,
            "reason_codes": list(self.reason_codes),
            "comparison_method": self.comparison_method,
            "normalized_claim": self.normalized_claim,
            "normalized_source": self.normalized_source,
            "direct_evidence_matched": self.direct_evidence_matched,
            "detail": self.detail,
        }


@dataclass(frozen=True, init=False)
class StoryCheckDiagnostic(_StoryCheckSerializable):
    diagnostic_id: str
    classification: StoryCheckDiagnosticClassification
    message: str
    source_identity: StoryCheckSourceIdentity
    verification_state: StoryCheckVerificationState
    validator_result: StoryCheckValidatorResult
    evidence: tuple[StoryCheckEvidenceReference, ...]
    producer: str
    producer_version: str | None

    def __init__(
        self,
        diagnostic_id: str,
        classification: StoryCheckDiagnosticClassification | str,
        message: str,
        source_identity: StoryCheckSourceIdentity,
        verification_state: StoryCheckVerificationState | str,
        validator_result: StoryCheckValidatorResult,
        evidence: Sequence[StoryCheckEvidenceReference] = (),
        *,
        producer: str = "story_check",
        producer_version: str | None = None,
    ) -> None:
        checked_id = _require_string(diagnostic_id, "diagnostic_id")
        if not _DIAGNOSTIC_ID_PATTERN.fullmatch(checked_id):
            raise StoryCheckContractValidationError(
                "diagnostic_id must be a bounded stable identifier"
            )
        checked_classification = _enum_value(
            StoryCheckDiagnosticClassification, classification, "classification"
        )
        checked_message = _require_string(message, "message", allow_empty=True)
        if not isinstance(source_identity, StoryCheckSourceIdentity):
            raise StoryCheckContractValidationError(
                "source_identity must be a StoryCheckSourceIdentity"
            )
        checked_state = _enum_value(
            StoryCheckVerificationState, verification_state, "verification_state"
        )
        if not isinstance(validator_result, StoryCheckValidatorResult):
            raise StoryCheckContractValidationError(
                "validator_result must be a StoryCheckValidatorResult"
            )
        if isinstance(evidence, (str, bytes)):
            raise StoryCheckContractValidationError(
                "evidence must be an ordered sequence of evidence references"
            )
        evidence_items = tuple(evidence)
        for reference in evidence_items:
            if not isinstance(reference, StoryCheckEvidenceReference):
                raise StoryCheckContractValidationError(
                    "evidence contains an invalid reference"
                )
            if reference.source_id != source_identity.source_id:
                raise StoryCheckContractValidationError("diagnostic evidence source_id mismatch")
            if reference.source_sha256 != source_identity.source_sha256:
                raise StoryCheckContractValidationError(
                    "diagnostic evidence source_sha256 mismatch"
                )
        checked_producer = _require_string(producer, "producer")
        checked_producer_version = None
        if producer_version is not None:
            checked_producer_version = _require_string(
                producer_version, "producer_version"
            )

        self._validate_state(
            checked_classification,
            checked_state,
            validator_result,
            evidence_items,
        )

        object.__setattr__(self, "diagnostic_id", checked_id)
        object.__setattr__(self, "classification", checked_classification)
        object.__setattr__(self, "message", checked_message)
        object.__setattr__(self, "source_identity", source_identity)
        object.__setattr__(self, "verification_state", checked_state)
        object.__setattr__(self, "validator_result", validator_result)
        object.__setattr__(self, "evidence", evidence_items)
        object.__setattr__(self, "producer", checked_producer)
        object.__setattr__(self, "producer_version", checked_producer_version)

    @staticmethod
    def _validate_state(
        classification: StoryCheckDiagnosticClassification,
        state: StoryCheckVerificationState,
        validator: StoryCheckValidatorResult,
        evidence: tuple[StoryCheckEvidenceReference, ...],
    ) -> None:
        outcome = validator.outcome
        if outcome == StoryCheckValidatorOutcome.SOURCE_MISMATCH:
            if state != StoryCheckVerificationState.QUARANTINED:
                raise StoryCheckContractValidationError(
                    "source mismatch diagnostics must be quarantined"
                )
            return

        if state == StoryCheckVerificationState.VERIFIED:
            if outcome != StoryCheckValidatorOutcome.SUPPORTED:
                raise StoryCheckContractValidationError(
                    "verified diagnostics require a supported validator outcome"
                )
            if not evidence or not validator.direct_evidence_matched:
                raise StoryCheckContractValidationError(
                    "verified diagnostics require valid matched direct evidence"
                )

        if classification == StoryCheckDiagnosticClassification.FACTUAL_WARNING:
            if outcome == StoryCheckValidatorOutcome.UNSUPPORTED:
                if state != StoryCheckVerificationState.QUARANTINED:
                    raise StoryCheckContractValidationError(
                        "unsupported factual warnings must be quarantined"
                    )
            if outcome == StoryCheckValidatorOutcome.SUPPORTED and not evidence:
                if state != StoryCheckVerificationState.QUARANTINED:
                    raise StoryCheckContractValidationError(
                        "factual warnings claiming support without evidence must be quarantined"
                    )
            if outcome == StoryCheckValidatorOutcome.SUPPORTED and not (
                validator.direct_evidence_matched
            ):
                if state != StoryCheckVerificationState.QUARANTINED:
                    raise StoryCheckContractValidationError(
                        "factual warnings without a direct evidence match must be quarantined"
                    )
            if outcome in {
                StoryCheckValidatorOutcome.NOT_RUN,
                StoryCheckValidatorOutcome.NOT_APPLICABLE,
            } and state == StoryCheckVerificationState.VERIFIED:
                raise StoryCheckContractValidationError(
                    "unvalidated factual warnings cannot be verified"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagnostic_id": self.diagnostic_id,
            "classification": self.classification.value,
            "message": self.message,
            "source_identity": self.source_identity.to_dict(),
            "verification_state": self.verification_state.value,
            "validator_result": self.validator_result.to_dict(),
            "evidence": [reference.to_dict() for reference in self.evidence],
            "producer": self.producer,
            "producer_version": self.producer_version,
        }


@dataclass(frozen=True, init=False)
class StoryCheckDiagnosticResult(_StoryCheckSerializable):
    source_identity: StoryCheckSourceIdentity
    diagnostics: tuple[StoryCheckDiagnostic, ...]
    contract_version: str
    analytical_output: bool
    non_canon: bool
    owner_approved: bool

    def __init__(
        self,
        source_identity: StoryCheckSourceIdentity,
        diagnostics: Sequence[StoryCheckDiagnostic],
    ) -> None:
        if not isinstance(source_identity, StoryCheckSourceIdentity):
            raise StoryCheckContractValidationError(
                "result source_identity must be a StoryCheckSourceIdentity"
            )
        if isinstance(diagnostics, (str, bytes)):
            raise StoryCheckContractValidationError(
                "diagnostics must be an ordered sequence"
            )
        ordered_diagnostics = tuple(diagnostics)
        for diagnostic in ordered_diagnostics:
            if not isinstance(diagnostic, StoryCheckDiagnostic):
                raise StoryCheckContractValidationError(
                    "result contains an invalid diagnostic"
                )
            if diagnostic.source_identity != source_identity:
                raise StoryCheckContractValidationError(
                    "result diagnostics must match the exact Story Check source identity"
                )

        object.__setattr__(self, "source_identity", source_identity)
        object.__setattr__(self, "diagnostics", ordered_diagnostics)
        object.__setattr__(self, "contract_version", STORY_CHECK_CONTRACT_VERSION)
        object.__setattr__(self, "analytical_output", True)
        object.__setattr__(self, "non_canon", True)
        object.__setattr__(self, "owner_approved", False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_identity": self.source_identity.to_dict(),
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
            "contract_version": self.contract_version,
            "boundary": {
                "analytical_output": self.analytical_output,
                "non_canon": self.non_canon,
                "owner_approved": self.owner_approved,
            },
        }


__all__ = [
    "STORY_CHECK_CONTRACT_VERSION",
    "STORY_CHECK_HASH_ALGORITHM",
    "STORY_CHECK_HASH_BASIS",
    "STORY_CHECK_OFFSET_BASIS",
    "StoryCheckContractValidationError",
    "StoryCheckDiagnostic",
    "StoryCheckDiagnosticClassification",
    "StoryCheckDiagnosticResult",
    "StoryCheckEvidenceReference",
    "StoryCheckSourceIdentity",
    "StoryCheckSourceSnapshot",
    "StoryCheckSourceType",
    "StoryCheckValidatorOutcome",
    "StoryCheckValidatorResult",
    "StoryCheckVerificationState",
    "build_story_check_evidence_reference",
    "build_story_check_source_snapshot",
    "compute_story_check_source_sha256",
]
