"""Phase 1 contract tests for canonical JSON, owner identity, and approved records."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    MAX_APPROVED_RECORD_BYTES,
    build_preparation_artifact,
    build_revision,
    build_sealed_revision,
    canonical_json_bytes,
    canonical_sha256,
    draft_scope_hash,
    load_preparation_artifact,
    preparation_id,
    preparation_scope_hash,
    publish_preparation_artifact,
    publish_revision_from_preparation,
    recover_preparation_revision,
    strict_json_loads,
)
from backend.story_knowledge.approved_records import (
    ALL_APPROVED_DESTINATION_TYPES,
    ORDINARY_APPROVED_DESTINATION_TYPES,
    approved_record_material,
    approved_record_relative_path,
    build_approved_record,
    commit_approved_record,
    load_approved_record,
    validate_record_operation,
)
from backend.story_knowledge.owner_identity import (
    load_local_owner_identity,
    owner_config_path,
    validate_owner_config,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def _fact() -> dict:
    return {
        "field": "status",
        "value": "reviewed",
        "evidence_ref_ids": ["evidence_1"],
        "provenance_ref_ids": ["provenance_1"],
    }


def _record_ref(key: str) -> dict:
    return {
        "destination_type": "approved_character",
        "destination_key": key,
        "record_version": 1,
        "content_hash": HASH_B,
    }


def _payload(destination_type: str) -> dict:
    facts = [_fact()]
    if destination_type == "approved_character":
        return {"payload_type": destination_type, "display_name": "Record A", "facts": facts}
    if destination_type == "approved_location":
        return {"payload_type": destination_type, "display_name": "Place A", "facts": facts}
    if destination_type == "approved_timeline_event":
        return {"payload_type": destination_type, "event_label": "Event A", "facts": facts}
    if destination_type == "approved_relationship":
        return {
            "payload_type": destination_type,
            "relationship_label": "Relationship A",
            "endpoint_refs": [_record_ref("record_a"), _record_ref("record_b")],
            "facts": facts,
        }
    if destination_type == "approved_organization":
        return {"payload_type": destination_type, "display_name": "Group A", "facts": facts}
    if destination_type == "approved_object":
        return {"payload_type": destination_type, "display_name": "Object A", "facts": facts}
    if destination_type == "approved_plot_thread":
        return {"payload_type": destination_type, "thread_label": "Thread A", "facts": facts}
    if destination_type == "approved_continuity_record":
        return {"payload_type": destination_type, "continuity_label": "Continuity A", "facts": facts}
    if destination_type == "approved_open_question":
        return {"payload_type": destination_type, "question_text": "Question A?", "facts": []}
    if destination_type == "approved_memory_index":
        return {"payload_type": destination_type, "entries": []}
    raise AssertionError(destination_type)


def _record(
    *,
    destination_type: str = "approved_character",
    destination_key: str = "record_a",
    record_version: int = 1,
) -> dict:
    return {
        "schema_version": "approved_record.v1",
        "record_version": record_version,
        "project_id": "project_a",
        "destination_type": destination_type,
        "destination_key": destination_key,
        "source_candidate_id": "candidate_a",
        "source_promotion_id": "promotion_a",
        "source_candidate_snapshot_hash": HASH_A,
        "payload": _payload(destination_type),
        "evidence_refs": [
            {
                "ref_id": "evidence_1",
                "locator_id": "locator_1",
                "content_hash": HASH_B,
            }
        ],
        "provenance_refs": [
            {
                "provenance_id": "provenance_1",
                "source_kind": "owner_input",
                "source_id": "source_a",
                "locator_id": "locator_1",
                "content_hash": HASH_B,
            }
        ],
        "source_locators": [
            {
                "locator_id": "locator_1",
                "locator_kind": "source_ref",
                "locator": "owner-source-a",
                "content_hash": HASH_B,
            }
        ],
    }


def _assert_code(code: str, callback) -> None:
    with pytest.raises(ApplyContractError) as exc_info:
        callback()
    assert exc_info.value.code == code


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b'{"a":1,"a":2}', "JSON_DUPLICATE_KEY"),
        (b'{"value":NaN}', "JSON_NON_FINITE_NUMBER"),
        (b'{"value":Infinity}', "JSON_NON_FINITE_NUMBER"),
        (b'{"value":1e309}', "JSON_NON_FINITE_NUMBER"),
        (b'{"value":9007199254740992}', "JSON_UNSAFE_NUMBER"),
        (b'"\\ud800"', "JSON_INVALID_SURROGATE"),
        (b"\xff", "JSON_INVALID_UTF8"),
        (b"\xef\xbb\xbf{}", "JSON_BOM_FORBIDDEN"),
    ],
)
def test_strict_json_rejects_ambiguous_or_unsafe_input(raw: bytes, code: str) -> None:
    _assert_code(code, lambda: strict_json_loads(raw))


def test_strict_json_raw_size_and_depth_bounds_are_inclusive() -> None:
    assert strict_json_loads(b"{}", max_bytes=2) == {}
    _assert_code("REQUEST_TOO_LARGE", lambda: strict_json_loads(b"{}", max_bytes=1))

    depth_32: object = 0
    for _ in range(32):
        depth_32 = [depth_32]
    canonical_json_bytes(depth_32)

    depth_33 = [depth_32]
    _assert_code("JSON_MAXIMUM_DEPTH_EXCEEDED", lambda: canonical_json_bytes(depth_33))
    _assert_code(
        "JSON_MAXIMUM_DEPTH_EXCEEDED",
        lambda: strict_json_loads(json.dumps(depth_33).encode("utf-8")),
    )


def test_canonical_json_is_deterministic_compact_and_round_trippable() -> None:
    value = {"é": "kept", "c": 1e-7, "b": 1.0, "a": -0.0, "array": [3, 2, 1]}
    expected = b'{"a":0,"array":[3,2,1],"b":1,"c":1e-7,"\xc3\xa9":"kept"}'

    assert canonical_json_bytes(value) == expected
    assert canonical_json_bytes(strict_json_loads(expected)) == expected
    assert canonical_sha256(value) == hashlib.sha256(expected).hexdigest()
    assert not expected.endswith(b"\n")


def test_canonical_json_preserves_unicode_without_normalization() -> None:
    composed = {"value": "é"}
    decomposed = {"value": "e\u0301"}

    assert canonical_json_bytes(composed) != canonical_json_bytes(decomposed)
    assert strict_json_loads(canonical_json_bytes(composed)) == composed
    assert strict_json_loads(canonical_json_bytes(decomposed)) == decomposed


def test_local_owner_identity_is_read_only_closed_and_server_authoritative(tmp_path: Path) -> None:
    project_dir = tmp_path / "project_a"
    path = owner_config_path(project_dir)
    path.parent.mkdir(parents=True)
    config = {
        "schema_version": "local_owner_identity.v1",
        "project_id": "project_a",
        "owner_id": "owner_a",
        "display_name": "Local Owner",
        "config_version": 3,
        "updated_at": "2030-01-01T00:00:00Z",
    }
    path.write_text(json.dumps(config), encoding="utf-8")
    before = path.read_bytes()

    identity = load_local_owner_identity(project_dir, project_id="project_a")

    assert identity == {
        "actor_type": "owner",
        "owner_id": "owner_a",
        "display_name": "Local Owner",
        "identity_source": "project_local_owner_config",
        "config_version": 3,
        "config_hash": canonical_sha256(config),
    }
    assert path.read_bytes() == before

    client_augmented = {**config, "actor_type": "owner"}
    _assert_code(
        "SCHEMA_UNKNOWN_FIELD",
        lambda: validate_owner_config(client_augmented, project_id="project_a"),
    )
    _assert_code(
        "OWNER_CONFIGURATION_PROJECT_MISMATCH",
        lambda: validate_owner_config(config, project_id="project_b"),
    )


def test_local_owner_identity_rejects_missing_symlinked_and_hardlinked_config(tmp_path: Path) -> None:
    missing_project = tmp_path / "missing"
    missing_project.mkdir()
    _assert_code(
        "OWNER_CONFIGURATION_REQUIRED",
        lambda: load_local_owner_identity(missing_project, project_id="missing"),
    )

    target_project = tmp_path / "target_project"
    target_path = owner_config_path(target_project)
    target_path.parent.mkdir(parents=True)
    target_path.write_text("{}", encoding="utf-8")

    symlink_project = tmp_path / "symlink_project"
    symlink_config = owner_config_path(symlink_project)
    symlink_config.parent.mkdir(parents=True)
    symlink_config.symlink_to(target_path)
    _assert_code(
        "OWNER_CONFIGURATION_UNSAFE",
        lambda: load_local_owner_identity(symlink_project, project_id="symlink_project"),
    )

    hardlink_project = tmp_path / "hardlink_project"
    hardlink_config = owner_config_path(hardlink_project)
    hardlink_config.parent.mkdir(parents=True)
    hardlink_config.hardlink_to(target_path)
    _assert_code(
        "OWNER_CONFIGURATION_UNSAFE",
        lambda: load_local_owner_identity(hardlink_project, project_id="hardlink_project"),
    )


@pytest.mark.parametrize("destination_type", sorted(ORDINARY_APPROVED_DESTINATION_TYPES))
def test_all_ordinary_destination_payload_schemas_are_closed(destination_type: str) -> None:
    material = approved_record_material(_record(destination_type=destination_type))
    assert material.record["destination_type"] == destination_type
    assert material.record["payload"]["payload_type"] == destination_type
    assert material.approved_record_hash == hashlib.sha256(material.canonical_bytes).hexdigest()
    assert material.approved_record_size == len(material.canonical_bytes)

    extra = _record(destination_type=destination_type)
    extra["payload"]["unexpected"] = True
    _assert_code("SCHEMA_UNKNOWN_FIELD", lambda: approved_record_material(extra))


def test_complete_approved_record_schema_is_closed_and_hashes_the_envelope() -> None:
    base = approved_record_material(_record())
    changed_version = approved_record_material(_record(record_version=2))
    changed_destination = approved_record_material(_record(destination_key="record_b"))
    with_note = _record()
    with_note["owner_note"] = "Owner note"
    changed_note = approved_record_material(with_note)

    assert len(
        {
            base.approved_record_hash,
            changed_version.approved_record_hash,
            changed_destination.approved_record_hash,
            changed_note.approved_record_hash,
        }
    ) == 4

    extra = _record()
    extra["authoritative_owner_actor"] = {"owner_id": "client_value"}
    _assert_code("SCHEMA_UNKNOWN_FIELD", lambda: approved_record_material(extra))

    wrong_payload = _record()
    wrong_payload["payload"]["payload_type"] = "approved_location"
    _assert_code("APPROVED_PAYLOAD_TYPE_MISMATCH", lambda: approved_record_material(wrong_payload))


def test_build_approved_record_does_not_retain_runtime_or_owner_fields() -> None:
    source = _record()
    built = build_approved_record(
        record_version=1,
        project_id=source["project_id"],
        destination_type=source["destination_type"],
        destination_key=source["destination_key"],
        source_candidate_id=source["source_candidate_id"],
        source_promotion_id=source["source_promotion_id"],
        source_candidate_snapshot_hash=source["source_candidate_snapshot_hash"],
        payload=source["payload"],
        evidence_refs=source["evidence_refs"],
        provenance_refs=source["provenance_refs"],
        source_locators=source["source_locators"],
    )

    assert set(built.record) == {
        "schema_version",
        "record_version",
        "project_id",
        "destination_type",
        "destination_key",
        "source_candidate_id",
        "source_promotion_id",
        "source_candidate_snapshot_hash",
        "payload",
        "evidence_refs",
        "provenance_refs",
        "source_locators",
    }
    assert b"owner_actor" not in built.canonical_bytes
    assert b"created_at" not in built.canonical_bytes


def test_approved_memory_index_schema_is_readable_but_ordinary_apply_is_forbidden() -> None:
    record = _record(destination_type="approved_memory_index")
    assert "approved_memory_index" in ALL_APPROVED_DESTINATION_TYPES

    _assert_code(
        "APPROVED_MEMORY_INDEX_ORDINARY_WRITE_FORBIDDEN",
        lambda: approved_record_material(record),
    )
    reserved = approved_record_material(record, ordinary=False)
    assert reserved.record["payload"] == {"payload_type": "approved_memory_index", "entries": []}
    _assert_code(
        "APPROVED_MEMORY_INDEX_ORDINARY_WRITE_FORBIDDEN",
        lambda: approved_record_relative_path("approved_memory_index", "index"),
    )


def test_approved_record_path_is_sole_typed_root() -> None:
    assert approved_record_relative_path("approved_character", "record_a").as_posix() == (
        "writer_assistant/approved_memory/approved_character/record_a.json"
    )
    _assert_code(
        "INVALID_SAFE_ID",
        lambda: approved_record_relative_path("approved_character", "../record_a"),
    )
    _assert_code(
        "APPROVED_DESTINATION_TYPE_INVALID",
        lambda: approved_record_relative_path("memory", "record_a"),
    )


def test_explicit_create_and_update_version_rules_never_infer_operation() -> None:
    version_1 = _record(record_version=1)
    version_2 = _record(record_version=2)

    assert validate_record_operation("create", version_1, before_record=None).record == version_1
    assert validate_record_operation("update", version_2, before_record=version_1).record == version_2
    _assert_code(
        "CREATE_REQUIRES_ABSENT_BEFORE_STATE",
        lambda: validate_record_operation("create", version_1, before_record=version_1),
    )
    _assert_code(
        "CREATE_RECORD_VERSION_INVALID",
        lambda: validate_record_operation("create", version_2, before_record=None),
    )
    _assert_code(
        "UPDATE_REQUIRES_PRESENT_BEFORE_STATE",
        lambda: validate_record_operation("update", version_2, before_record=None),
    )
    _assert_code(
        "UPDATE_RECORD_VERSION_INVALID",
        lambda: validate_record_operation("update", version_1, before_record=version_1),
    )
    _assert_code(
        "APPLY_OPERATION_INVALID",
        lambda: validate_record_operation("infer", version_1, before_record=None),
    )


def test_atomic_approved_record_create_and_update_recheck_exact_before_state(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project_a"
    project.mkdir()
    version_1 = _record(record_version=1)
    created = commit_approved_record(
        project,
        operation="create",
        before_record=None,
        proposed_record=version_1,
    )
    destination = project / approved_record_relative_path(
        "approved_character", "record_a"
    )
    assert destination.read_bytes() == canonical_json_bytes(version_1)
    assert load_approved_record(destination) == created

    version_2 = _record(record_version=2)
    version_2["payload"]["display_name"] = "Record A updated by owner"
    updated = commit_approved_record(
        project,
        operation="update",
        before_record=version_1,
        proposed_record=version_2,
    )
    assert updated.record == version_2
    assert destination.read_bytes() == canonical_json_bytes(version_2)

    stale_version_2 = _record(record_version=2)
    stale_version_2["payload"]["display_name"] = "Must not overwrite"
    before_rejection = destination.read_bytes()
    _assert_code(
        "APPLY_CONTRACT_BEFORE_STATE_CHANGED",
        lambda: commit_approved_record(
            project,
            operation="update",
            before_record=version_1,
            proposed_record=stale_version_2,
        ),
    )
    assert destination.read_bytes() == before_rejection


def _record_at_exact_size() -> dict:
    record = _record()
    record["evidence_refs"] = [
        {"ref_id": f"evidence_{index}", "locator_id": f"locator_{index}"}
        for index in range(128)
    ]
    base_size = len(canonical_json_bytes(record))
    empty_note_record = copy.deepcopy(record)
    empty_note_record["evidence_refs"][0]["note"] = ""
    note_overhead = len(canonical_json_bytes(empty_note_record)) - base_size
    needed = MAX_APPROVED_RECORD_BYTES - base_size

    selected_count = next(
        count
        for count in range(1, 129)
        if count * note_overhead <= needed <= count * (note_overhead + 2048)
    )
    remaining_characters = needed - selected_count * note_overhead
    for index in range(selected_count):
        length = min(2048, remaining_characters)
        record["evidence_refs"][index]["note"] = "x" * length
        remaining_characters -= length
    assert remaining_characters == 0
    assert len(canonical_json_bytes(record)) == MAX_APPROVED_RECORD_BYTES
    return record


def test_complete_approved_record_size_limit_accepts_exact_and_rejects_plus_one(tmp_path: Path) -> None:
    exact = _record_at_exact_size()
    exact_material = approved_record_material(exact)
    assert exact_material.approved_record_size == MAX_APPROVED_RECORD_BYTES

    destination = tmp_path / "record.json"
    destination.write_bytes(exact_material.canonical_bytes)
    assert load_approved_record(destination).approved_record_hash == exact_material.approved_record_hash

    oversized = copy.deepcopy(exact)
    adjustable = next(ref for ref in oversized["evidence_refs"] if len(ref.get("note", "")) < 2048)
    adjustable["note"] = adjustable.get("note", "") + "x"
    _assert_code("APPROVED_RECORD_TOO_LARGE", lambda: approved_record_material(oversized))


def test_load_approved_record_requires_exact_canonical_bytes(tmp_path: Path) -> None:
    record = _record()
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    _assert_code("APPROVED_RECORD_NONCANONICAL", lambda: load_approved_record(path))


def _owner() -> dict:
    return {
        "actor_type": "owner",
        "owner_id": "owner_a",
        "display_name": "Local Owner",
        "identity_source": "project_local_owner_config",
        "config_version": 3,
        "config_hash": HASH_B,
    }


def _revision(*, number: int = 1, prepared_at: str = "2030-01-01T00:00:00Z") -> dict:
    record = approved_record_material(_record(record_version=1))
    before = {
        "state": "absent",
        "path": "writer_assistant/approved_memory/approved_character/record_a.json",
        "record_version": None,
        "content_hash": None,
        "content": None,
        "observed_at": "2030-01-01T00:00:00Z",
        "snapshot_token": HASH_A,
    }
    return build_revision(
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
        revision=number,
        supersedes_revision=None if number == 1 else number - 1,
        prepared_by=_owner(),
        prepared_at=prepared_at,
        operation="create",
        destination={
            "approved_destination_type": "approved_character",
            "destination_key": "record_a",
            "destination_path": before["path"],
        },
        source_candidate_snapshot_hash=HASH_A,
        evidence_refs=record.record["evidence_refs"],
        provenance_refs=record.record["provenance_refs"],
        source_locators=record.record["source_locators"],
        proposed_approved_record=record.record,
        approved_record_hash=record.approved_record_hash,
        approved_record_size=record.approved_record_size,
        duplicate_resolution={
            "state": "unresolved",
            "rationale": "Owner review remains required.",
            "evidence_refs": [],
            "reviewed_candidate_ids": [],
            "reviewed_approved_records": [],
            "resolved_by": None,
            "resolved_at": None,
            "resolution_scope_hash": None,
        },
        dependency_resolution={
            "state": "unresolved",
            "dependencies": [],
            "rationale": "Owner review remains required.",
            "evidence_ref_ids": [],
            "resolved_by": None,
            "resolved_at": None,
            "resolution_scope_hash": None,
        },
        before_state=before,
    )


def _preparation(revision: dict | None = None, *, key: str = "11111111-1111-4111-8111-111111111111"):
    revision = revision or _revision()
    request_hash = canonical_sha256({"request": "owner prepared"})
    scope_hash = preparation_scope_hash(
        project_id="project_a",
        promotion_id="promotion_a",
        requested_operation="create",
        approved_destination_type="approved_character",
        destination_key="record_a",
        canonical_request_body_hash=request_hash,
        expected_latest_revision=None if revision["revision"] == 1 else revision["revision"] - 1,
        expected_latest_draft_scope_hash=None if revision["revision"] == 1 else HASH_B,
    )
    material = build_preparation_artifact(
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
        idempotency_key=key,
        preparation_scope_hash_value=scope_hash,
        canonical_request_body_hash=request_hash,
        prior_lineage_expectations={
            "expected_state": "no_contract" if revision["revision"] == 1 else "draft_active",
            "expected_latest_revision": None if revision["revision"] == 1 else revision["revision"] - 1,
            "expected_latest_draft_scope_hash": None if revision["revision"] == 1 else HASH_B,
            "expected_active_sealed_revision": None,
            "expected_active_sealed_contract_hash": None,
        },
        supersession_kind="none" if revision["revision"] == 1 else "draft",
        revision=revision,
        artifact_created_at="2030-01-01T00:00:00Z",
    )
    return material, scope_hash


def test_c1_and_c2_bind_the_accepted_complete_objects_deterministically() -> None:
    revision = _revision()
    assert revision["draft_scope_hash"] == draft_scope_hash(revision)

    changed_derived = copy.deepcopy(revision)
    changed_derived["approved_record_hash"] = HASH_A
    assert draft_scope_hash(changed_derived) == revision["draft_scope_hash"]

    approval = {
        "owner_actor": _owner(),
        "project_id": "project_a",
        "promotion_id": "promotion_a",
        "revision": 1,
        "draft_scope_hash": revision["draft_scope_hash"],
        "before_state_snapshot_token": HASH_A,
        "approval_method": "explicit_apply_contract_approval",
        "approved_at": "2030-01-01T00:01:00Z",
    }
    sealed = build_sealed_revision(revision, approval, HASH_B)
    preimage = {key: value for key, value in sealed.items() if key != "sealed_contract_hash"}
    assert sealed["sealed_contract_hash"] == canonical_sha256(preimage)
    changed_approval = copy.deepcopy(approval)
    changed_approval["approved_at"] = "2030-01-01T00:02:00Z"
    assert build_sealed_revision(revision, changed_approval, HASH_B)["sealed_contract_hash"] != sealed["sealed_contract_hash"]


def test_preparation_id_scope_and_artifact_retain_exact_revision_bytes() -> None:
    material, scope_hash = _preparation()
    expected_id = preparation_id(
        "project_a", "promotion_a", "11111111-1111-4111-8111-111111111111"
    )
    assert material.artifact["preparation_id"] == expected_id
    assert material.artifact["preparation_scope_hash"] == scope_hash
    assert material.revision_bytes == canonical_json_bytes(material.artifact["revision"])
    assert material.artifact["revision_canonical_hash"] == hashlib.sha256(material.revision_bytes).hexdigest()
    assert material.artifact["revision_canonical_size"] == len(material.revision_bytes)
    assert not material.artifact["revision_canonical_bytes_b64url"].endswith("=")


def test_preparation_publication_is_immutable_idempotent_and_recovers_without_authority(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    material, scope_hash = _preparation()

    assert publish_preparation_artifact(project, material) is False
    assert publish_preparation_artifact(project, material) is True
    loaded = load_preparation_artifact(
        project,
        project_id="project_a",
        promotion_id="promotion_a",
        idempotency_key=material.artifact["idempotency_key"],
    )
    assert loaded.artifact_bytes == material.artifact_bytes

    # Mutable authority changes after artifact publication. Recovery has no input
    # for it and must publish the retained bytes exactly.
    authority = project / "writer_assistant" / "config" / "local_owner.json"
    authority.parent.mkdir(parents=True)
    authority.write_text('{"changed":"after-crash"}', encoding="utf-8")
    recovered, existing = recover_preparation_revision(
        project,
        project_id="project_a",
        promotion_id="promotion_a",
        idempotency_key=material.artifact["idempotency_key"],
        expected_preparation_scope_hash=scope_hash,
    )
    assert existing is False
    revision_path = project / recovered.artifact["revision_path"]
    assert revision_path.read_bytes() == material.revision_bytes
    assert recover_preparation_revision(
        project,
        project_id="project_a",
        promotion_id="promotion_a",
        idempotency_key=material.artifact["idempotency_key"],
        expected_preparation_scope_hash=scope_hash,
    )[1] is True


def test_preparation_scope_corruption_and_revision_collision_block_without_overwrite(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    material, scope_hash = _preparation()
    publish_preparation_artifact(project, material)

    _assert_code(
        "APPLY_CONTRACT_PREPARATION_SCOPE_CONFLICT",
        lambda: recover_preparation_revision(
            project,
            project_id="project_a",
            promotion_id="promotion_a",
            idempotency_key=material.artifact["idempotency_key"],
            expected_preparation_scope_hash=HASH_A,
        ),
    )
    revision_path = project / material.artifact["revision_path"]
    revision_path.write_bytes(b"{}")
    before = revision_path.read_bytes()
    _assert_code(
        "APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT",
        lambda: publish_revision_from_preparation(project, material),
    )
    assert revision_path.read_bytes() == before

    artifact_path = project / material.artifact["preparation_path"]
    corrupt = json.loads(artifact_path.read_text(encoding="utf-8"))
    corrupt["revision_canonical_hash"] = HASH_A
    artifact_path.write_bytes(canonical_json_bytes(corrupt))
    _assert_code(
        "APPLY_CONTRACT_PREPARATION_HASH_MISMATCH",
        lambda: load_preparation_artifact(
            project,
            project_id="project_a",
            promotion_id="promotion_a",
            idempotency_key=material.artifact["idempotency_key"],
        ),
    )


def test_numbered_revision_publication_is_contiguous_and_no_overwrite(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    second, _ = _preparation(
        _revision(number=2), key="22222222-2222-4222-8222-222222222222"
    )
    _assert_code(
        "APPLY_CONTRACT_PREPARATION_REVISION_CONFLICT",
        lambda: publish_revision_from_preparation(project, second),
    )

    first, _ = _preparation()
    assert publish_revision_from_preparation(project, first) is False
    assert publish_revision_from_preparation(project, second) is False
    assert publish_revision_from_preparation(project, second) is True
