"""Phase 3 tests for apply-promotion runtime locks and final challenges."""

from __future__ import annotations

import fcntl
import hashlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from backend.story_knowledge import apply_promotion
from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    canonical_json_bytes,
)
from backend.story_knowledge.approved_records import load_approved_record
from backend.story_knowledge.promotion_apply_runtime import (
    CHALLENGE_SECURITY_CLASSIFICATION,
    ApplyPromotionRuntimeManager,
    FinalChallengeRegistry,
)


HASH_A = "a" * 64
HASH_B = "b" * 64
KEY_A = "11111111-1111-4111-8111-111111111111"
KEY_B = "22222222-2222-4222-8222-222222222222"


def _assert_code(code: str, callback) -> None:
    with pytest.raises(ApplyContractError) as exc_info:
        callback()
    assert exc_info.value.code == code


def _runtime_layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    runtime = tmp_path / "runtime"
    projects = tmp_path / "projects"
    project = projects / "project_a"
    runtime.mkdir(mode=0o700)
    projects.mkdir()
    project.mkdir()
    return runtime, projects, project


def _snapshot_tree(root: Path) -> tuple:
    if not root.exists():
        return ()
    result = []
    for path in sorted((root, *root.rglob("*")), key=lambda item: item.as_posix()):
        metadata = os.lstat(path)
        relative = path.relative_to(root).as_posix() if path != root else "."
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        result.append(
            (
                relative,
                metadata.st_mode,
                metadata.st_size,
                metadata.st_mtime_ns,
                content_hash,
            )
        )
    return tuple(result)


def test_runtime_requires_absolute_safe_external_server_owned_directory(tmp_path: Path) -> None:
    runtime, projects, _ = _runtime_layout(tmp_path)
    _assert_code(
        "RUNTIME_DIRECTORY_REQUIRED",
        lambda: ApplyPromotionRuntimeManager(runtime_dir="relative", projects_dir=projects).start(),
    )

    runtime.chmod(0o750)
    _assert_code(
        "RUNTIME_DIRECTORY_UNSAFE",
        lambda: ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start(),
    )
    runtime.chmod(0o700)

    linked_runtime = tmp_path / "linked-runtime"
    linked_runtime.symlink_to(runtime, target_is_directory=True)
    _assert_code(
        "RUNTIME_DIRECTORY_UNSAFE",
        lambda: ApplyPromotionRuntimeManager(runtime_dir=linked_runtime, projects_dir=projects).start(),
    )

    nested_runtime = projects / "project_a" / "runtime"
    nested_runtime.mkdir(mode=0o700)
    _assert_code(
        "RUNTIME_DIRECTORY_UNSAFE",
        lambda: ApplyPromotionRuntimeManager(runtime_dir=nested_runtime, projects_dir=projects).start(),
    )


def test_worker_count_and_process_lifetime_lease_fail_closed(tmp_path: Path) -> None:
    runtime, projects, _ = _runtime_layout(tmp_path)
    _assert_code(
        "UNSUPPORTED_MULTI_WORKER_DEPLOYMENT",
        lambda: ApplyPromotionRuntimeManager(
            runtime_dir=runtime, projects_dir=projects, worker_count=2
        ).start(),
    )

    first = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    second = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects)
    try:
        _assert_code("UNSUPPORTED_MULTI_WORKER_DEPLOYMENT", second.start)
    finally:
        first.close()

    restarted = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    lease = runtime / "backend-single-worker.lock"
    resource_files = tuple((runtime / "approved-store-locks").iterdir())
    try:
        assert lease.read_bytes() == b""
        assert stat_mode(lease) == 0o600
        assert len(resource_files) == 1
        assert resource_files[0].read_bytes() == b""
        assert stat_mode(resource_files[0]) == 0o600
    finally:
        restarted.close()


def test_environment_configuration_requires_runtime_and_all_worker_counts_equal_one(
    tmp_path: Path,
) -> None:
    _, projects, _ = _runtime_layout(tmp_path)
    _assert_code(
        "RUNTIME_DIRECTORY_REQUIRED",
        lambda: ApplyPromotionRuntimeManager.from_environment(
            projects_dir=projects, environ={}
        ),
    )
    _assert_code(
        "UNSUPPORTED_MULTI_WORKER_DEPLOYMENT",
        lambda: ApplyPromotionRuntimeManager.from_environment(
            projects_dir=projects,
            environ={
                "WRITING_ASSISTANT_RUNTIME_DIR": str(tmp_path / "runtime"),
                "WEB_CONCURRENCY": "2",
            },
        ),
    )
    manager = ApplyPromotionRuntimeManager.from_environment(
        projects_dir=projects,
        environ={
            "WRITING_ASSISTANT_RUNTIME_DIR": str(tmp_path / "runtime"),
            "WEB_CONCURRENCY": "1",
            "UVICORN_WORKERS": "01",
        },
    ).start()
    manager.close()


def stat_mode(path: Path) -> int:
    return os.stat(path, follow_symlinks=False).st_mode & 0o777


def test_project_lock_key_registration_and_retained_restart_identity(tmp_path: Path) -> None:
    runtime, projects, project = _runtime_layout(tmp_path)
    manager = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    expected_key = hashlib.sha256(str(project.resolve()).encode("utf-8")).hexdigest()
    expected = runtime / "approved-store-locks" / f"approved-store-{expected_key}.lock"
    try:
        assert expected.exists()
        assert manager.register_project(project) == expected
        before = _snapshot_tree(runtime)
    finally:
        manager.close()

    restarted = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    try:
        assert restarted.register_project(project) == expected
        assert _snapshot_tree(runtime) == before
    finally:
        restarted.close()


def test_shared_readers_coexist_and_exclusive_contention_is_nonblocking(tmp_path: Path) -> None:
    runtime, projects, project = _runtime_layout(tmp_path)
    manager = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    try:
        with manager.shared(project):
            with manager.shared(project):
                _assert_code("APPROVED_STORE_APPLY_LOCKED", lambda: manager.exclusive(project).__enter__())
        with manager.exclusive(project):
            _assert_code("APPROVED_STORE_APPLY_LOCKED", lambda: manager.shared(project).__enter__())
    finally:
        manager.close()


def test_kernel_lock_conflict_is_nonblocking(tmp_path: Path) -> None:
    runtime, projects, project = _runtime_layout(tmp_path)
    manager = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    lock_path = manager.register_project(project)
    external_fd = os.open(lock_path, os.O_RDWR)
    try:
        fcntl.flock(external_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _assert_code("APPROVED_STORE_APPLY_LOCKED", lambda: manager.shared(project).__enter__())
    finally:
        fcntl.flock(external_fd, fcntl.LOCK_UN)
        os.close(external_fd)
        manager.close()


def test_get_lock_lookup_is_zero_write_and_never_registers_missing_project(tmp_path: Path) -> None:
    runtime, projects, project = _runtime_layout(tmp_path)
    manager = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    try:
        runtime_before = _snapshot_tree(runtime)
        project_before = _snapshot_tree(project)
        with manager.shared(project):
            pass
        assert _snapshot_tree(runtime) == runtime_before
        assert _snapshot_tree(project) == project_before

        late_project = projects / "late_project"
        late_project.mkdir()
        runtime_before_missing = _snapshot_tree(runtime)
        project_before_missing = _snapshot_tree(late_project)
        _assert_code("RUNTIME_LOCK_UNAVAILABLE", lambda: manager.shared(late_project).__enter__())
        assert _snapshot_tree(runtime) == runtime_before_missing
        assert _snapshot_tree(late_project) == project_before_missing
    finally:
        manager.close()


def test_runtime_disappearance_or_resource_replacement_blocks_without_recreation(tmp_path: Path) -> None:
    runtime, projects, project = _runtime_layout(tmp_path)
    manager = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    moved_runtime = tmp_path / "runtime-moved"
    runtime.rename(moved_runtime)
    try:
        _assert_code("RUNTIME_LOCK_UNAVAILABLE", lambda: manager.shared(project).__enter__())
        assert not runtime.exists()
    finally:
        manager.close()


def test_process_lease_path_replacement_blocks_project_acquisition(tmp_path: Path) -> None:
    runtime, projects, project = _runtime_layout(tmp_path)
    manager = ApplyPromotionRuntimeManager(runtime_dir=runtime, projects_dir=projects).start()
    lease = runtime / "backend-single-worker.lock"
    moved_lease = runtime / "original-lease"
    lease.rename(moved_lease)
    lease.touch(mode=0o600)
    try:
        _assert_code("RUNTIME_LOCK_UNAVAILABLE", lambda: manager.shared(project).__enter__())
        assert lease.read_bytes() == b""
        assert moved_lease.read_bytes() == b""
    finally:
        manager.close()


class _Clock:
    def __init__(self) -> None:
        self.monotonic = 100.0
        self.wall = datetime(2030, 1, 1, tzinfo=timezone.utc)

    def monotonic_now(self) -> float:
        return self.monotonic

    def wall_now(self) -> datetime:
        return self.wall

    def advance(self, seconds: float) -> None:
        self.monotonic += seconds
        self.wall = self.wall.replace(microsecond=0) + timedelta(seconds=seconds)


class _Random:
    def __init__(self) -> None:
        self.counter = 1

    def __call__(self, size: int) -> bytes:
        value = bytes([self.counter]) * size
        self.counter += 1
        return value


def _owner() -> dict:
    return {
        "actor_type": "owner",
        "owner_id": "owner_a",
        "display_name": "Local Owner",
        "identity_source": "project_local_owner_config",
        "config_version": 1,
        "config_hash": HASH_A,
    }


def _registry(*, capacity: int = 1024, boot_id: str = "0123456789abcdef"):
    clock = _Clock()
    registry = FinalChallengeRegistry(
        capacity=capacity,
        boot_id=boot_id,
        monotonic_clock=clock.monotonic_now,
        wall_clock=clock.wall_now,
        random_bytes=_Random(),
    )
    return registry, clock


def _issue(registry: FinalChallengeRegistry, *, key: str = KEY_A, token: str = HASH_B):
    return registry.issue(
        project_id="project_a",
        promotion_id="promotion_a",
        revision=1,
        sealed_contract_hash=HASH_A,
        before_state_snapshot_token=token,
        operation="create",
        destination_path="writer_assistant/approved_memory/approved_character/record_a.json",
        authoritative_owner_actor=_owner(),
        idempotency_key=key,
    )


def test_challenge_issue_exact_replay_scope_conflict_and_replacement() -> None:
    registry, _ = _registry()
    first = _issue(registry)
    replay = _issue(registry)

    assert first["replayed"] is False
    assert replay == {**first, "replayed": True}
    assert first["challenge_id"] == first["challenge_scope"]["challenge_id"]
    assert first["challenge_id"].startswith("challenge_0123456789abcdef_")
    assert len(first["challenge_nonce"]) == 43
    assert first["challenge_scope"]["issued_at"] == "2030-01-01T00:00:00Z"
    assert first["challenge_scope"]["expires_at"] == "2030-01-01T00:02:00Z"
    assert "credential" not in first

    _assert_code("IDEMPOTENCY_PAYLOAD_CONFLICT", lambda: _issue(registry, token=HASH_A))
    replacement = _issue(registry, key=KEY_B)
    assert replacement["challenge_id"] != first["challenge_id"]
    assert registry.status(first["challenge_id"]) == "replaced"
    _assert_code(
        "FINAL_CHALLENGE_REPLACED",
        lambda: registry.begin_consumption(
            challenge_id=first["challenge_id"],
            challenge_response=HASH_A,
            expected_challenge_scope=first["challenge_scope"],
        ),
    )


def test_challenge_expiry_uses_exact_monotonic_120_second_boundary() -> None:
    registry, clock = _registry()
    issued = _issue(registry)
    clock.advance(119.999)
    assert registry.status(issued["challenge_id"]) == "outstanding"
    clock.advance(0.001)
    assert registry.status(issued["challenge_id"]) == "expired"
    _assert_code(
        "FINAL_CHALLENGE_EXPIRED",
        lambda: registry.begin_consumption(
            challenge_id=issued["challenge_id"],
            challenge_response=HASH_A,
            expected_challenge_scope=issued["challenge_scope"],
        ),
    )


def test_challenge_response_consumption_is_single_use() -> None:
    registry, _ = _registry()
    issued = _issue(registry)
    response = registry.expected_response(issued["challenge_nonce"], issued["challenge_scope"])

    _assert_code(
        "FINAL_CHALLENGE_RESPONSE_INVALID",
        lambda: registry.begin_consumption(
            challenge_id=issued["challenge_id"],
            challenge_response=HASH_A,
            expected_challenge_scope=issued["challenge_scope"],
        ),
    )
    accepted_scope = registry.begin_consumption(
        challenge_id=issued["challenge_id"],
        challenge_response=response,
        expected_challenge_scope=issued["challenge_scope"],
    )
    assert accepted_scope == issued["challenge_scope"]
    registry.complete_consumption(issued["challenge_id"])
    assert registry.status(issued["challenge_id"]) == "consumed"
    _assert_code(
        "FINAL_CHALLENGE_CONSUMED",
        lambda: registry.begin_consumption(
            challenge_id=issued["challenge_id"],
            challenge_response=response,
            expected_challenge_scope=issued["challenge_scope"],
        ),
    )


def test_challenge_restart_unknown_capacity_and_tombstone_retention() -> None:
    registry, clock = _registry(capacity=1)
    issued = _issue(registry)
    _assert_code("CHALLENGE_REGISTRY_CAPACITY", lambda: _issue(registry, key=KEY_B))
    assert registry.status(issued["challenge_id"]) == "outstanding"

    restarted, _ = _registry(capacity=1, boot_id="fedcba9876543210")
    _assert_code(
        "FINAL_CHALLENGE_REQUIRED_AFTER_RESTART",
        lambda: restarted.begin_consumption(
            challenge_id=issued["challenge_id"],
            challenge_response=HASH_A,
            expected_challenge_scope=issued["challenge_scope"],
        ),
    )
    current_boot_unknown = "challenge_0123456789abcdef_" + "f" * 64
    _assert_code(
        "FINAL_CHALLENGE_UNKNOWN",
        lambda: registry.begin_consumption(
            challenge_id=current_boot_unknown,
            challenge_response=HASH_A,
            expected_challenge_scope=issued["challenge_scope"],
        ),
    )

    clock.advance(120)
    assert registry.status(issued["challenge_id"]) == "expired"
    assert len(registry) == 1
    clock.advance(600)
    assert len(registry) == 0
    assert _issue(registry, key=KEY_B)["replayed"] is False


def test_challenge_is_explicitly_anti_replay_not_authentication_and_writes_no_files(tmp_path: Path) -> None:
    registry, _ = _registry()
    before = _snapshot_tree(tmp_path)
    issued = _issue(registry)
    after = _snapshot_tree(tmp_path)

    assert before == after
    assert CHALLENGE_SECURITY_CLASSIFICATION == {
        "purpose": "anti-replay_explicit_confirmation_evidence",
        "authentication": False,
        "identity_proof": False,
        "session": False,
        "credential": False,
    }
    assert canonical_json_bytes(issued["challenge_scope"])


def _phase4_context(tmp_path: Path):
    project = tmp_path / "project_a"
    project.mkdir()
    candidate = {
        "candidate_id": "candidate_a",
        "project_id": "project_a",
        "evidence": [{"claim": "Owner supplied evidence", "locator": "planning-note-1"}],
        "provenance": {
            "source_type": "owner_input",
            "source_path": "omi/ideas/idea_a.json",
            "source_label": "Owner planning note",
        },
    }
    promotion = {
        "promotion_id": "promotion_a",
        "project_id": "project_a",
        "candidate_id": "candidate_a",
        "source_snapshot": candidate,
        "evidence": candidate["evidence"],
        "provenance": {
            "candidate": candidate["provenance"],
            "promotion_request": {
                "source_type": "owner_input",
                "source_path": "omi/candidates/candidate_a.json",
                "source_label": "Owner promotion request",
            },
        },
    }
    owner = _owner()
    return project, promotion, candidate, owner


def _prepare_body(*, key: str = KEY_A, operation: str = "create") -> dict:
    duplicate_state = "distinct_record" if operation == "create" else "update_existing"
    return {
        "idempotency_key": key,
        "expected_latest_revision": None,
        "expected_latest_draft_scope_hash": None,
        "operation": operation,
        "approved_destination_type": "approved_character",
        "destination_key": "character_a",
        "payload": {
            "payload_type": "approved_character",
            "display_name": "Owner-defined character",
            "facts": [
                {
                    "field": "role",
                    "value": "Owner-defined role",
                    "evidence_ref_ids": ["evidence_1"],
                    "provenance_ref_ids": ["provenance_1"],
                }
            ],
        },
        "duplicate_resolution": {
            "state": duplicate_state,
            "rationale": "The owner reviewed the candidate against existing records.",
            "evidence_ref_ids": ["evidence_1"],
            "reviewed_candidate_ids": ["candidate_a"],
            "reviewed_approved_records": [],
        },
        "dependency_resolution": {
            "state": "none_declared",
            "dependencies": [],
            "rationale": "The owner confirmed that no dependencies are declared.",
            "evidence_ref_ids": ["evidence_1"],
        },
        "supersession": None,
    }


def _approval_body(prepared: dict, *, key: str = KEY_B) -> dict:
    return {
        "idempotency_key": key,
        "expected_latest_revision": prepared["revision"],
        "expected_latest_draft_scope_hash": prepared["draft_scope_hash"],
        "before_state_snapshot_token": prepared["before_state"]["snapshot_token"],
        "confirmed": True,
        "approval_method": "explicit_apply_contract_approval",
    }


def test_phase4_prepare_read_approve_challenge_revoke_and_audit(tmp_path: Path) -> None:
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    body = _prepare_body()
    prepared_response, status = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=body,
    )
    assert status == 201
    assert prepared_response["revision_path"].endswith("revision_1.json")
    assert prepared_response["replayed"] is False

    replay, replay_status = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=body,
    )
    assert replay_status == 200
    assert replay == {**prepared_response, "replayed": True}

    before_read = _snapshot_tree(project)
    view = apply_promotion.read_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        selected_revision=1,
    )
    assert _snapshot_tree(project) == before_read
    assert view["lineage"]["state"] == "draft_active"
    revision = view["selected_revision"]
    assert revision["prepared_by"] == owner
    assert revision["destination"]["destination_path"] == (
        "writer_assistant/approved_memory/approved_character/character_a.json"
    )

    approval, approval_status = apply_promotion.approve_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        revision_number=1,
        body=_approval_body(revision),
    )
    assert approval_status == 201
    assert approval["sealed_revision_path"].endswith("sealed_revision_1.json")
    replayed_approval, replayed_approval_status = apply_promotion.approve_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        revision_number=1,
        body=_approval_body(revision),
    )
    assert replayed_approval_status == 200
    assert replayed_approval == {**approval, "replayed": True}

    registry, _ = _registry()
    project_before_challenge = _snapshot_tree(project)
    challenge, challenge_status = apply_promotion.issue_final_challenge(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        registry=registry,
        body={
            "revision": 1,
            "sealed_contract_hash": approval["sealed_contract_hash"],
            "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
            "idempotency_key": "33333333-3333-4333-8333-333333333333",
        },
    )
    assert challenge_status == 201
    assert "credential" not in challenge
    assert _snapshot_tree(project) == project_before_challenge

    revocation_body = {
        "idempotency_key": "44444444-4444-4444-8444-444444444444",
        "revision": 1,
        "sealed_contract_hash": approval["sealed_contract_hash"],
        "rationale": "The owner explicitly revoked this sealed contract.",
        "confirmed": True,
        "method": "explicit_contract_revocation",
    }
    revoked, revoked_status = apply_promotion.revoke_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        revision_number=1,
        body=revocation_body,
    )
    assert revoked_status == 201
    replayed_revocation, replayed_revocation_status = apply_promotion.revoke_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        revision_number=1,
        body=revocation_body,
    )
    assert replayed_revocation_status == 200
    assert replayed_revocation == {**revoked, "replayed": True}

    before_audit = _snapshot_tree(project)
    audit = apply_promotion.read_apply_audit(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
    )
    assert _snapshot_tree(project) == before_audit
    assert audit["lineage_state"] == "revoked"
    assert [entry["event"]["sequence"] for entry in audit["entries"]] == list(
        range(1, len(audit["entries"]) + 1)
    )


def test_phase6_revision_without_required_preparation_artifact_blocks_lineage(
    tmp_path: Path,
) -> None:
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    prepared, _ = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=_prepare_body(),
    )
    (project / prepared["preparation_path"]).unlink()

    _assert_code(
        "APPLY_CONTRACT_PREPARATION_ARTIFACT_MISSING",
        lambda: apply_promotion.derive_apply_contract_lineage(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            candidate_id="candidate_a",
        ),
    )


def test_phase4_same_key_recovers_incomplete_preparation_from_retained_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    body = _prepare_body()
    real_append = apply_promotion.append_event
    calls = 0

    def fail_first_event(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("simulated crash after immutable revision publication")
        return real_append(*args, **kwargs)

    monkeypatch.setattr(apply_promotion, "append_event", fail_first_event)
    with pytest.raises(OSError):
        apply_promotion.prepare_apply_contract(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            owner=owner,
            body=body,
        )
    revision_bytes = (project / "writer_assistant/apply_contracts/promotion_a/revision_1.json").read_bytes()
    monkeypatch.setattr(apply_promotion, "append_event", real_append)
    recovered, status = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion={**promotion, "evidence": [{"changed": "authority must not be reread"}]},
        candidate=candidate,
        owner=owner,
        body=body,
    )
    assert status == 200
    assert recovered["recovery_status"] == "recovered"
    assert (project / "writer_assistant/apply_contracts/promotion_a/revision_1.json").read_bytes() == revision_bytes


def test_phase4_closed_inputs_and_blocked_decisions_fail_closed(tmp_path: Path) -> None:
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    unknown = {**_prepare_body(), "owner_id": "client_claimed_owner"}
    _assert_code(
        "SCHEMA_UNKNOWN_FIELD",
        lambda: apply_promotion.prepare_apply_contract(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            owner=owner,
            body=unknown,
        ),
    )
    forbidden = {**_prepare_body(), "approved_destination_type": "approved_memory_index"}
    _assert_code(
        "APPROVED_MEMORY_INDEX_ORDINARY_WRITE_FORBIDDEN",
        lambda: apply_promotion.prepare_apply_contract(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            owner=owner,
            body=forbidden,
        ),
    )

    blocked_body = _prepare_body()
    blocked_body["duplicate_resolution"] = {
        **blocked_body["duplicate_resolution"],
        "state": "unresolved",
        "evidence_ref_ids": [],
        "reviewed_candidate_ids": [],
    }
    prepared, _ = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=blocked_body,
    )
    revision = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )["revisions"][0]
    _assert_code(
        "DUPLICATE_DECISION_BLOCKS_APPLY",
        lambda: apply_promotion.approve_apply_contract(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            owner=owner,
            revision_number=1,
            body=_approval_body(revision),
        ),
    )
    assert prepared["lineage_state"] == "draft_active"


def test_phase4_update_is_explicit_and_uses_present_record_version(tmp_path: Path) -> None:
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    first, _ = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=_prepare_body(),
    )
    first_revision = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )["revisions"][0]
    approved_path = project / first_revision["destination"]["destination_path"]
    approved_path.parent.mkdir(parents=True)
    approved_path.write_bytes(canonical_json_bytes(first_revision["proposed_approved_record"]))

    update = _prepare_body(
        key="55555555-5555-4555-8555-555555555555", operation="update"
    )
    update["expected_latest_revision"] = 1
    update["expected_latest_draft_scope_hash"] = first["draft_scope_hash"]
    update["supersession"] = {
        "kind": "draft",
        "superseded_revision": 1,
        "superseded_draft_scope_hash": first["draft_scope_hash"],
        "rationale": "The owner explicitly replaces the draft with an update contract.",
    }
    second, status = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=update,
    )
    assert status == 201
    assert second["revision"] == 2
    second_revision = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )["revisions"][1]
    assert second_revision["operation"] == "update"
    assert second_revision["before_state"]["state"] == "present"
    assert second_revision["proposed_approved_record"]["record_version"] == 2


def test_phase4_route_surface_is_exact_and_has_no_owner_or_recovery_route() -> None:
    source = (
        Path(__file__).resolve().parents[1] / "backend/routes/apply_promotion.py"
    ).read_text(encoding="utf-8")
    for declaration in (
        '@lifecycle_router.post("/apply-contract/revisions")',
        '@lifecycle_router.get("/apply-contract")',
        '@lifecycle_router.post("/apply-contract/revisions/{revision}/approval")',
        '@lifecycle_router.post("/apply-contract/revisions/{revision}/revocation")',
        '@lifecycle_router.post("/apply-contract/final-challenge")',
        '@lifecycle_router.get("/apply-audit")',
    ):
        assert source.count(declaration) == 1
    assert "owner-config" not in source
    assert "recovery-route" not in source
    assert "strict_json_loads(await request.body()" in source
    assert ".shared(project_dir)" in source
    assert ".exclusive(project_dir)" in source
    assert source.count('@router.post("")') == 1
    assert "validate_promotion_request(body)" not in source
    assert "candidate_record = body.get" not in source


def _sealed_final_context(tmp_path: Path, monkeypatch):
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    monkeypatch.setattr(
        apply_promotion, "load_local_owner_identity", lambda *args, **kwargs: owner
    )
    prepared, _ = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=_prepare_body(),
    )
    revision = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )["revisions"][0]
    approval, _ = apply_promotion.approve_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        revision_number=1,
        body=_approval_body(revision),
    )
    registry, _ = _registry()
    challenge_key = "66666666-6666-4666-8666-666666666666"
    challenge, _ = apply_promotion.issue_final_challenge(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        registry=registry,
        body={
            "revision": 1,
            "sealed_contract_hash": approval["sealed_contract_hash"],
            "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
            "idempotency_key": challenge_key,
        },
    )
    apply_body = {
        "promotion_id": "promotion_a",
        "revision": 1,
        "sealed_contract_hash": approval["sealed_contract_hash"],
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "challenge_id": challenge["challenge_id"],
        "challenge_response": registry.expected_response(
            challenge["challenge_nonce"], challenge["challenge_scope"]
        ),
        "final_confirmation": {
            "confirmed": True,
            "method": "explicit_final_apply_confirmation",
        },
        "idempotency_key": "77777777-7777-4777-8777-777777777777",
    }
    return project, promotion, candidate, owner, revision, registry, apply_body


def test_phase5_final_apply_commits_once_and_completed_replay_ignores_consumed_challenge(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, _, revision, registry, body = _sealed_final_context(
        tmp_path, monkeypatch
    )
    contract_tree_before = _snapshot_tree(
        project / "writer_assistant/apply_contracts"
    )
    result = apply_promotion.final_apply_promotion(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        body=body,
        registry=registry,
    )
    assert result["lineage_state"] == "applied"
    assert result["replayed"] is False
    destination = project / result["destination_path"]
    committed = load_approved_record(destination)
    assert committed.record == revision["proposed_approved_record"]
    assert committed.approved_record_hash == result["approved_record_hash"]
    assert committed.approved_record_size == result["approved_record_size"]
    assert _snapshot_tree(project / "writer_assistant/apply_contracts") == contract_tree_before
    before_replay = _snapshot_tree(project)

    replay = apply_promotion.final_apply_promotion(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion={},
        candidate={},
        body={**body, "challenge_response": HASH_A},
        registry=registry,
    )
    assert replay == {**result, "replayed": True}
    assert _snapshot_tree(project) == before_replay
    lineage = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )
    assert lineage["state"] == "applied"
    assert len(_event_for(lineage, "apply_intent")) == 1
    assert len(_event_for(lineage, "apply_completed")) == 1


def test_phase6_completed_lineage_revalidates_committed_record_pair(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, _, _, registry, body = _sealed_final_context(
        tmp_path, monkeypatch
    )
    result = apply_promotion.final_apply_promotion(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        body=body,
        registry=registry,
    )
    destination = project / result["destination_path"]
    changed = load_approved_record(destination).record
    changed["owner_note"] = "Externally changed after completion."
    destination.write_bytes(canonical_json_bytes(changed))

    _assert_code(
        "APPLY_COMPLETION_RECORD_MISMATCH",
        lambda: apply_promotion.derive_apply_contract_lineage(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            candidate_id="candidate_a",
        ),
    )


def test_phase5_final_apply_request_is_reference_only_and_rejects_client_authority(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, _, _, registry, body = _sealed_final_context(
        tmp_path, monkeypatch
    )
    before = _snapshot_tree(project)
    _assert_code(
        "SCHEMA_UNKNOWN_FIELD",
        lambda: apply_promotion.final_apply_promotion(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            body={
                **body,
                "operation": "create",
                "destination_path": "client/claimed/path.json",
                "owner_actor": {"owner_id": "client_claimed_owner"},
            },
            registry=registry,
        ),
    )
    assert _snapshot_tree(project) == before


def _event_for(lineage: dict, event_type: str) -> list[dict]:
    return [event for event in lineage["events"] if event["event_type"] == event_type]


def test_phase5_committed_without_completion_recovers_without_rewriting_record(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, _, _, registry, body = _sealed_final_context(
        tmp_path, monkeypatch
    )
    real_completion = apply_promotion._publish_apply_completion
    calls = 0

    def crash_before_completion(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("simulated crash after approved-record commit")
        return real_completion(*args, **kwargs)

    monkeypatch.setattr(
        apply_promotion, "_publish_apply_completion", crash_before_completion
    )
    with pytest.raises(OSError):
        apply_promotion.final_apply_promotion(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            body=body,
            registry=registry,
        )
    destination = project / "writer_assistant/approved_memory/approved_character/character_a.json"
    committed_metadata = os.stat(destination, follow_symlinks=False)
    committed_bytes = destination.read_bytes()
    monkeypatch.setattr(apply_promotion, "_publish_apply_completion", real_completion)

    recovered = apply_promotion.final_apply_promotion(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion={},
        candidate={},
        body=body,
        registry=registry,
    )
    assert recovered["replayed"] is True
    assert destination.read_bytes() == committed_bytes
    after_metadata = os.stat(destination, follow_symlinks=False)
    assert (after_metadata.st_dev, after_metadata.st_ino, after_metadata.st_mtime_ns) == (
        committed_metadata.st_dev,
        committed_metadata.st_ino,
        committed_metadata.st_mtime_ns,
    )
    lineage = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )
    assert len(_event_for(lineage, "recovery_completed")) == 1
    assert _event_for(lineage, "recovery_completed")[0]["outcome"] == "committed"
    assert len(_event_for(lineage, "apply_completed")) == 1


def test_phase5_intent_before_commit_classifies_not_committed_and_never_reports_success(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, _, _, registry, body = _sealed_final_context(
        tmp_path, monkeypatch
    )

    def fail_before_commit(*args, **kwargs):
        raise OSError("simulated destination write failure")

    monkeypatch.setattr(apply_promotion, "commit_approved_record", fail_before_commit)
    _assert_code(
        "APPLY_FAILED_BEFORE_COMMIT",
        lambda: apply_promotion.final_apply_promotion(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            body=body,
            registry=registry,
        ),
    )
    assert not (
        project / "writer_assistant/approved_memory/approved_character/character_a.json"
    ).exists()
    lineage = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )
    assert lineage["state"] == "sealed_active"
    assert len(_event_for(lineage, "apply_failed_before_commit")) == 1
    assert _event_for(lineage, "recovery_completed")[0]["outcome"] == "not_committed"
    assert not _event_for(lineage, "apply_completed")


def test_phase5_final_apply_update_atomically_replaces_exact_version(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, owner = _phase4_context(tmp_path)
    monkeypatch.setattr(
        apply_promotion, "load_local_owner_identity", lambda *args, **kwargs: owner
    )
    first, _ = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=_prepare_body(),
    )
    first_revision = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )["revisions"][0]
    apply_promotion.commit_approved_record(
        project,
        operation="create",
        before_record=None,
        proposed_record=first_revision["proposed_approved_record"],
    )
    update = _prepare_body(
        key="88888888-8888-4888-8888-888888888888", operation="update"
    )
    update["expected_latest_revision"] = 1
    update["expected_latest_draft_scope_hash"] = first["draft_scope_hash"]
    update["supersession"] = {
        "kind": "draft",
        "superseded_revision": 1,
        "superseded_draft_scope_hash": first["draft_scope_hash"],
        "rationale": "The owner explicitly replaces the create draft with an update.",
    }
    update["payload"]["display_name"] = "Owner-defined character updated"
    _, _ = apply_promotion.prepare_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        body=update,
    )
    revision = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )["revisions"][1]
    approval, _ = apply_promotion.approve_apply_contract(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        revision_number=2,
        body=_approval_body(revision, key="99999999-9999-4999-8999-999999999999"),
    )
    registry, _ = _registry()
    challenge, _ = apply_promotion.issue_final_challenge(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        owner=owner,
        registry=registry,
        body={
            "revision": 2,
            "sealed_contract_hash": approval["sealed_contract_hash"],
            "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
            "idempotency_key": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        },
    )
    final_body = {
        "promotion_id": "promotion_a",
        "revision": 2,
        "sealed_contract_hash": approval["sealed_contract_hash"],
        "before_state_snapshot_token": revision["before_state"]["snapshot_token"],
        "challenge_id": challenge["challenge_id"],
        "challenge_response": registry.expected_response(
            challenge["challenge_nonce"], challenge["challenge_scope"]
        ),
        "final_confirmation": {
            "confirmed": True,
            "method": "explicit_final_apply_confirmation",
        },
        "idempotency_key": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    }
    result = apply_promotion.final_apply_promotion(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        promotion=promotion,
        candidate=candidate,
        body=final_body,
        registry=registry,
    )
    committed = load_approved_record(project / result["destination_path"])
    assert result["approved_record_version"] == 2
    assert committed.record == revision["proposed_approved_record"]
    assert committed.record["payload"]["display_name"].endswith("updated")


def test_phase5_unclassified_destination_appends_recovery_required_and_blocks_rewrite(
    tmp_path: Path, monkeypatch
) -> None:
    project, promotion, candidate, _, revision, registry, body = _sealed_final_context(
        tmp_path, monkeypatch
    )

    def write_unexpected_then_fail(*args, **kwargs):
        destination = (
            project
            / "writer_assistant/approved_memory/approved_character/character_a.json"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        unexpected = {**revision["proposed_approved_record"], "owner_note": "unexpected"}
        destination.write_bytes(canonical_json_bytes(unexpected))
        raise OSError("simulated uncertain commit outcome")

    monkeypatch.setattr(
        apply_promotion, "commit_approved_record", write_unexpected_then_fail
    )
    _assert_code(
        "RECOVERY_REQUIRED",
        lambda: apply_promotion.final_apply_promotion(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion=promotion,
            candidate=candidate,
            body=body,
            registry=registry,
        ),
    )
    destination = project / "writer_assistant/approved_memory/approved_character/character_a.json"
    unexpected_bytes = destination.read_bytes()
    _assert_code(
        "RECOVERY_REQUIRED",
        lambda: apply_promotion.final_apply_promotion(
            project_dir=project,
            project_id="project_a",
            promotion_id="promotion_a",
            promotion={},
            candidate={},
            body=body,
            registry=registry,
        ),
    )
    assert destination.read_bytes() == unexpected_bytes
    lineage = apply_promotion.derive_apply_contract_lineage(
        project_dir=project,
        project_id="project_a",
        promotion_id="promotion_a",
        candidate_id="candidate_a",
    )
    assert lineage["state"] == "recovery_required"
    assert len(_event_for(lineage, "recovery_required")) == 1
    assert not _event_for(lineage, "apply_completed")
