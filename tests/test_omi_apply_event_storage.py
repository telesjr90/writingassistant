"""Phase 2 tests for deterministic v2 apply-promotion event storage."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import pytest

from backend.story_knowledge.apply_contract import ApplyContractError, canonical_json_bytes, canonical_sha256
from backend.story_knowledge.promotion_apply_events import (
    MAX_EVENT_BYTES,
    append_event,
    event_id_preimage,
    event_scope_hash,
    find_events,
    scan_event_chain,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
KEY = "11111111-1111-4111-8111-111111111111"
OPERATION = "prep_" + "c" * 64


def _owner() -> dict:
    return {
        "actor_type": "owner",
        "owner_id": "owner_a",
        "display_name": "Local Owner",
        "identity_source": "project_local_owner_config",
        "config_version": 1,
        "config_hash": HASH_A,
    }


def _draft_content(*, rationale: str = "Supersede the reviewed draft.") -> dict:
    return {
        "preparation_id": OPERATION,
        "preparation_scope_hash": HASH_A,
        "superseded_revision": 1,
        "superseding_revision": 2,
        "superseded_draft_scope_hash": HASH_A,
        "superseding_draft_scope_hash": HASH_B,
        "authoritative_owner_actor": _owner(),
        "rationale": rationale,
    }


def _sealed_content() -> dict:
    return {
        "preparation_id": OPERATION,
        "preparation_scope_hash": HASH_A,
        "superseded_revision": 1,
        "superseding_revision": 2,
        "sealed_contract_hash": HASH_A,
        "superseding_draft_scope_hash": HASH_B,
        "authoritative_owner_actor": _owner(),
        "rationale": "Supersede the explicitly sealed contract.",
    }


def _append(project: Path, *, event_type: str = "draft_superseded", content: dict | None = None):
    project.mkdir(exist_ok=True)
    return append_event(
        project,
        event_type=event_type,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
        revision=2,
        idempotency_key=KEY,
        operation_identity=OPERATION,
        created_at="2030-01-01T00:00:00Z" if event_type == "draft_superseded" else "2030-01-01T00:01:00Z",
        content=content or (_draft_content() if event_type == "draft_superseded" else _sealed_content()),
    )


def _assert_code(code: str, callback) -> None:
    with pytest.raises(ApplyContractError) as exc_info:
        callback()
    assert exc_info.value.code == code


def test_event_ids_filenames_content_hashes_and_chain_are_deterministic(tmp_path: Path) -> None:
    project = tmp_path / "project"
    first = _append(project).event
    second = _append(project, event_type="contract_superseded").event

    assert first["sequence"] == 1
    assert first["event_id"] == canonical_sha256(event_id_preimage(first))
    assert first["event_filename"] == f"000000000001_{first['event_id']}.json"
    assert len(first["event_filename"]) == 82
    first_without_content_hash = {key: value for key, value in first.items() if key != "event_content_hash"}
    assert first["event_content_hash"] == canonical_sha256(first_without_content_hash)
    assert second["sequence"] == 2
    assert second["previous_event_hash"] == hashlib.sha256(canonical_json_bytes(first)).hexdigest()
    assert second["event_filename"].startswith("000000000002_")

    chain = scan_event_chain(project, project_id="project_a", promotion_id="promotion_a")
    assert chain.events == (first, second)
    assert chain.temporary_residue == ()


def test_event_replay_is_exact_and_scope_conflicts_do_not_write(tmp_path: Path) -> None:
    project = tmp_path / "project"
    initial = _append(project)
    event_path = project / initial.event["event_path"]
    before = event_path.read_bytes()
    before_entries = tuple(event_path.parent.iterdir())

    replay = _append(project)
    assert replay.replayed is True
    assert replay.event == initial.event
    assert event_path.read_bytes() == before
    assert tuple(event_path.parent.iterdir()) == before_entries

    _assert_code(
        "APPLY_EVENT_IDEMPOTENCY_SCOPE_CONFLICT",
        lambda: _append(project, content=_draft_content(rationale="Different owner decision.")),
    )
    assert tuple(event_path.parent.iterdir()) == before_entries


def test_event_type_is_part_of_idempotency_uniqueness_for_one_logical_operation(tmp_path: Path) -> None:
    project = tmp_path / "project"
    draft = _append(project).event
    sealed = _append(project, event_type="contract_superseded").event

    assert draft["operation_identity"] == sealed["operation_identity"]
    assert draft["idempotency_key"] == sealed["idempotency_key"]
    assert draft["event_type"] != sealed["event_type"]
    assert draft["event_id"] != sealed["event_id"]
    assert len(find_events(
        project,
        project_id="project_a",
        promotion_id="promotion_a",
        operation_identity=OPERATION,
        idempotency_key=KEY,
    )) == 2


def test_recomputed_event_with_invalid_variant_semantics_is_malformed(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    operation_identity = "apply_" + "d" * 32
    content = {
        "apply_id": operation_identity,
        "intent_event_id": HASH_A,
        "outcome": "not_committed",
        "error_code": "destination_matches_before_state",
    }
    publication = append_event(
        project,
        event_type="apply_failed_before_commit",
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
        revision=1,
        idempotency_key=KEY,
        operation_identity=operation_identity,
        created_at="2030-01-01T00:00:00Z",
        content=content,
    )
    original_path = project / publication.event["event_path"]
    malformed = copy.deepcopy(publication.event)
    malformed["outcome"] = "committed"
    malformed["event_scope_hash"] = event_scope_hash(
        event_type=malformed["event_type"],
        project_id=malformed["project_id"],
        promotion_id=malformed["promotion_id"],
        candidate_id=malformed["candidate_id"],
        revision=malformed["revision"],
        idempotency_key=malformed["idempotency_key"],
        operation_identity=malformed["operation_identity"],
        content={field: malformed[field] for field in content},
    )
    malformed["event_id"] = canonical_sha256(event_id_preimage(malformed))
    malformed["event_filename"] = (
        f"000000000001_{malformed['event_id']}.json"
    )
    malformed["event_path"] = (
        "writer_assistant/promotion_audits/promotion_a/events/"
        + malformed["event_filename"]
    )
    malformed_without_hash = {
        key: value
        for key, value in malformed.items()
        if key != "event_content_hash"
    }
    malformed["event_content_hash"] = canonical_sha256(
        malformed_without_hash
    )
    malformed_path = original_path.with_name(malformed["event_filename"])
    original_path.rename(malformed_path)
    malformed_path.write_bytes(canonical_json_bytes(malformed))

    _assert_code(
        "APPLY_EVENT_MALFORMED",
        lambda: scan_event_chain(
            project, project_id="project_a", promotion_id="promotion_a"
        ),
    )


def test_draft_and_sealed_supersession_events_are_closed_and_distinct(tmp_path: Path) -> None:
    project = tmp_path / "project"
    draft = _append(project).event
    sealed = _append(project, event_type="contract_superseded").event

    assert "sealed_contract_hash" not in draft
    assert sealed["sealed_contract_hash"] == HASH_A
    invalid_draft = _draft_content()
    invalid_draft["sealed_contract_hash"] = HASH_A
    _assert_code("SCHEMA_UNKNOWN_FIELD", lambda: _append(tmp_path / "other", content=invalid_draft))


def test_lookup_validates_the_entire_chain_before_returning_matches(tmp_path: Path) -> None:
    project = tmp_path / "project"
    first = _append(project).event
    _append(project, event_type="contract_superseded")
    first_path = project / first["event_path"]
    changed = copy.deepcopy(first)
    changed["rationale"] = "Tampered after publication."
    first_path.write_bytes(canonical_json_bytes(changed))

    _assert_code(
        "APPLY_EVENT_CONTENT_HASH_MISMATCH",
        lambda: find_events(
            project,
            project_id="project_a",
            promotion_id="promotion_a",
            event_type="contract_superseded",
        ),
    )


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda event: event.update(event_content_hash=HASH_A), "APPLY_EVENT_CONTENT_HASH_MISMATCH"),
        (lambda event: event.update(previous_event_hash=HASH_A), "APPLY_EVENT_PREVIOUS_HASH_MISMATCH"),
        (lambda event: event.update(event_version="promotion_apply_event.v1"), "APPLY_EVENT_UNSUPPORTED_VERSION"),
        (lambda event: event.update(event_type="unknown_event"), "APPLY_EVENT_UNKNOWN_TYPE"),
    ],
)
def test_corrupt_event_documents_block_without_repair(tmp_path: Path, mutation, code: str) -> None:
    project = tmp_path / "project"
    publication = _append(project)
    path = project / publication.event["event_path"]
    event = copy.deepcopy(publication.event)
    mutation(event)
    path.write_bytes(canonical_json_bytes(event))
    before = path.read_bytes()

    _assert_code(code, lambda: scan_event_chain(project, project_id="project_a", promotion_id="promotion_a"))
    assert path.read_bytes() == before


def test_sequence_gaps_duplicate_sequence_and_malformed_names_block(tmp_path: Path) -> None:
    gap_project = tmp_path / "gap"
    event = _append(gap_project).event
    path = gap_project / event["event_path"]
    path.rename(path.with_name(path.name.replace("000000000001", "000000000002")))
    _assert_code(
        "APPLY_EVENT_SEQUENCE_GAP",
        lambda: scan_event_chain(gap_project, project_id="project_a", promotion_id="promotion_a"),
    )

    duplicate_project = tmp_path / "duplicate"
    original = _append(duplicate_project).event
    original_path = duplicate_project / original["event_path"]
    duplicate_path = original_path.with_name(f"000000000001_{HASH_A}.json")
    duplicate_path.write_bytes(original_path.read_bytes())
    _assert_code(
        "APPLY_EVENT_DUPLICATE_SEQUENCE",
        lambda: scan_event_chain(duplicate_project, project_id="project_a", promotion_id="promotion_a"),
    )

    malformed_project = tmp_path / "malformed"
    malformed_project.mkdir()
    event_dir = malformed_project / "writer_assistant" / "promotion_audits" / "promotion_a" / "events"
    event_dir.mkdir(parents=True)
    (event_dir / "not-an-event.json").write_text("{}", encoding="utf-8")
    _assert_code(
        "APPLY_EVENT_MALFORMED",
        lambda: scan_event_chain(malformed_project, project_id="project_a", promotion_id="promotion_a"),
    )


def test_temporary_residue_is_diagnostic_and_does_not_consume_sequence(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    event_dir = project / "writer_assistant" / "promotion_audits" / "promotion_a" / "events"
    event_dir.mkdir(parents=True)
    residue = ".tmp-22222222-2222-4222-8222-222222222222"
    (event_dir / residue).write_text("diagnostic residue", encoding="utf-8")

    chain = scan_event_chain(project, project_id="project_a", promotion_id="promotion_a")
    assert chain.events == ()
    assert chain.temporary_residue == (residue,)
    assert _append(project).event["sequence"] == 1


def test_oversized_event_is_rejected_before_publication(tmp_path: Path) -> None:
    project = tmp_path / "project"
    huge = _draft_content(rationale="x" * MAX_EVENT_BYTES)
    _assert_code("AUDIT_EVENT_TOO_LARGE", lambda: _append(project, content=huge))
    assert not (project / "writer_assistant").exists()
