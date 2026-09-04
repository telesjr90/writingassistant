from __future__ import annotations

import copy
import concurrent.futures
import hashlib
import json
import threading

import pytest

from backend.story_knowledge import raw_artifacts
from backend.story_knowledge.evidence_ledger import (
    append_evidence_ledger_event,
    build_exact_evidence_record,
    scan_evidence_ledger,
)
from backend.story_knowledge.source_map import (
    BYTE_OFFSET_BASIS,
    CHAR_OFFSET_BASIS,
    OffsetRange,
    build_exact_source_snapshot,
)


def _snapshot(text="A café 雨."):
    return build_exact_source_snapshot(
        project_id="example",
        source_document_type="omi",
        source_document_id="idea-001",
        source_document_version="1",
        source_ownership="owner_authored",
        source_content=text,
    )


def _file_ref(payload: bytes):
    return {
        "artifact_file_id": "raw-output",
        "artifact_type": "adapter_metadata",
        "relative_path": "artifacts/output.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "record_count": 1,
        "line_count": None,
        "schema_name": "fixture",
        "schema_version": "1",
        "parser_hint": "json",
        "source_locator_refs": ["snapshot-ref"],
        "evidence_refs": ["evidence-ref"],
        "provenance_refs": ["provenance-ref"],
        "boundary_flags": sorted(raw_artifacts._REQUIRED_BOUNDARY_FLAGS),
    }


def _manifest(payload: bytes):
    return raw_artifacts.build_immutable_raw_artifact_manifest(
        project_id="example",
        run_id="analysis-run-001",
        raw_artifact_bundle_id="bundle-analysis-run-001",
        artifact_files=[_file_ref(payload)],
        analysis_run_manifest_hash="a" * 64,
        created_at="2026-08-30T20:00:00Z",
        source_refs=["snapshot-ref"],
        evidence_refs=["evidence-ref"],
        provenance_refs=["provenance-ref"],
        source_locator_refs=["locator-ref"],
    )


def test_exact_evidence_preserves_character_and_utf8_byte_semantics_without_content():
    snapshot = _snapshot()
    record = build_exact_evidence_record(
        snapshot=snapshot,
        run_id="analysis-run-001",
        artifact_id="bundle-analysis-run-001",
        artifact_file_id="raw-output",
        operation_id="analyze-spacy",
        adapter_id="spacy",
        disposition="validated",
        contributor_state="succeeded",
        character_range=OffsetRange(2, 8, CHAR_OFFSET_BASIS),
        created_at="2026-08-30T20:00:00Z",
        transformation_ids=("transform-001",),
        output_id="output-001",
    )
    locator = record["source_locator"]
    assert (locator["char_start"], locator["char_end"]) == (2, 8)
    assert (locator["byte_start"], locator["byte_end"]) == (2, 11)
    assert locator["char_offset_basis"] == CHAR_OFFSET_BASIS
    assert locator["byte_offset_basis"] == BYTE_OFFSET_BASIS
    assert record["excerpt_hash"] == hashlib.sha256("café 雨".encode()).hexdigest()
    assert record["transformation_ids"] == ["transform-001"]
    assert record["output_id"] == "output-001"
    assert "excerpt" not in record and "source_text" not in record


@pytest.mark.parametrize("disposition", ["rejected", "quarantined", "unverified"])
def test_unsuccessful_evidence_dispositions_retain_reasoned_lineage(disposition):
    record = build_exact_evidence_record(
        snapshot=_snapshot("Owner source"),
        run_id="analysis-run-001",
        artifact_id="bundle-analysis-run-001",
        artifact_file_id="raw-output",
        operation_id="analyze-spacy",
        adapter_id="spacy",
        disposition=disposition,
        contributor_state="failed_closed",
        character_range=OffsetRange(0, 5, CHAR_OFFSET_BASIS),
        created_at="2026-08-30T20:00:00Z",
        reason="verification boundary did not accept output",
    )
    assert record["disposition"] == disposition
    assert record["contributor_state"] == "failed_closed"
    assert record["reason"]


def test_ledger_is_hash_chained_tamper_evident_and_idempotent(tmp_path):
    payload = {
        "artifact_id": "bundle-001",
        "artifact_manifest_hash": "a" * 64,
        "artifact_bundle_hash": "b" * 64,
        "analysis_run_manifest_hash": "c" * 64,
        "source_snapshot_ids": ["snapshot-001"],
        "availability": "available",
    }
    first = append_evidence_ledger_event(
        project_dir=tmp_path,
        project_id="example",
        run_id="analysis-run-001",
        event_type="artifact_recorded",
        idempotency_key="artifact-001",
        created_at="2026-08-30T20:00:00Z",
        payload=payload,
    )
    assert append_evidence_ledger_event(
        project_dir=tmp_path,
        project_id="example",
        run_id="analysis-run-001",
        event_type="artifact_recorded",
        idempotency_key="artifact-001",
        created_at="2026-08-30T20:00:01Z",
        payload=payload,
    )["event_hash"] == first["event_hash"]
    conflicting = dict(payload, availability="deleted")
    with pytest.raises(ValueError, match="conflict"):
        append_evidence_ledger_event(
            project_dir=tmp_path,
            project_id="example",
            run_id="analysis-run-001",
            event_type="artifact_recorded",
            idempotency_key="artifact-001",
            created_at="2026-08-30T20:00:02Z",
            payload=conflicting,
        )
    event_path = next((tmp_path / "writer_assistant/analysis_runs/analysis-run-001/evidence_ledger/events").iterdir())
    event_path.write_bytes(event_path.read_bytes().replace(b"available", b"tampered!"))
    with pytest.raises(ValueError):
        scan_evidence_ledger(
            project_dir=tmp_path, project_id="example", run_id="analysis-run-001"
        )


def test_v2_bundle_integrity_replay_tamper_and_q140_deletion(tmp_path):
    payload = b'{"state":"unavailable"}'
    manifest = _manifest(payload)
    first = raw_artifacts.write_immutable_raw_artifact_bundle(
        manifest, {"raw-output": payload}, project_dir=tmp_path
    )
    second = raw_artifacts.write_immutable_raw_artifact_bundle(
        manifest, {"raw-output": payload}, project_dir=tmp_path
    )
    assert first == second
    with pytest.raises(ValueError, match="lifecycle cannot be rewritten"):
        raw_artifacts.quarantine_raw_artifact_bundle(
            "example",
            "bundle-analysis-run-001",
            "attempted mutation",
            project_dir=tmp_path,
        )
    artifact_path = tmp_path / "projects/example/writer_assistant/raw_artifacts/bundle-analysis-run-001/artifacts/output.json"
    artifact_path.write_bytes(payload.replace(b"unavailable", b"tamperxxxxx"))
    with pytest.raises(ValueError):
        raw_artifacts.read_immutable_raw_artifact_bundle(
            "example", "bundle-analysis-run-001", project_dir=tmp_path
        )
    artifact_path.write_bytes(payload)
    with pytest.raises(ValueError, match="hash mismatch"):
        raw_artifacts.write_immutable_raw_artifact_bundle(
            manifest,
            {"raw-output": payload.replace(b"unavailable", b"tamperxxxxx")},
            project_dir=tmp_path,
        )
    sentinel = tmp_path / "projects/example/writer_assistant/candidates/sentinel.json"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("owner state", encoding="utf-8")
    deleted = raw_artifacts.delete_immutable_raw_artifact_bundle(
        "example",
        "bundle-analysis-run-001",
        project_dir=tmp_path,
        deleted_at="2026-08-30T20:01:00Z",
        deletion_id="deletion-001",
        owner_controlled=True,
    )
    assert deleted["status"] == "deleted"
    assert deleted["tombstone"]["content_retained"] is False
    assert deleted["tombstone"]["replayable"] is False
    assert sentinel.read_text(encoding="utf-8") == "owner state"
    assert not artifact_path.exists()
    compatible = raw_artifacts.read_raw_artifact_manifest_compatible(
        "example", "bundle-analysis-run-001", project_dir=tmp_path
    )
    assert compatible["status"] == "deleted"
    assert "source_text" not in json.dumps(compatible)


def test_v2_rejects_symlinked_project_storage(tmp_path):
    payload = b"{}"
    manifest = _manifest(payload)
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "projects").mkdir()
    (tmp_path / "projects/example").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="unsafe artifact storage path"):
        raw_artifacts.write_immutable_raw_artifact_bundle(
            manifest, {"raw-output": payload}, project_dir=tmp_path
        )


def test_v2_rejects_missing_payload_and_manifest_hash_tamper(tmp_path):
    payload = b"{}"
    manifest = _manifest(payload)
    with pytest.raises(ValueError, match="every declared payload"):
        raw_artifacts.write_immutable_raw_artifact_bundle(manifest, {}, project_dir=tmp_path)
    tampered = copy.deepcopy(manifest)
    tampered["analysis_run_manifest_ref"]["manifest_hash"] = "b" * 64
    with pytest.raises(ValueError, match="bundle hash mismatch"):
        raw_artifacts.validate_raw_artifact_integrity(tampered)


def test_v2_requires_lowercase_hashes_without_tightening_legacy_file_refs():
    payload = b"{}"
    manifest = _manifest(payload)
    assert raw_artifacts.validate_raw_artifact_integrity(manifest) == manifest
    legacy_file = _file_ref(payload)
    legacy_file["sha256"] = legacy_file["sha256"].upper()
    assert raw_artifacts.validate_raw_artifact_file_ref(legacy_file)["sha256"].isupper()
    for mutation in ("file", "bundle", "manifest"):
        invalid = copy.deepcopy(manifest)
        if mutation == "file":
            invalid["artifact_files"][0]["sha256"] = invalid["artifact_files"][0]["sha256"].upper()
        elif mutation == "bundle":
            invalid["bundle_hash"] = invalid["bundle_hash"].upper()
        else:
            invalid["manifest_hash"] = invalid["manifest_hash"].upper()
        with pytest.raises(ValueError, match="lowercase SHA-256"):
            raw_artifacts.validate_raw_artifact_integrity(invalid)


def test_q140_interrupted_deletion_is_visible_and_same_authorization_recovers(
    monkeypatch, tmp_path
):
    payload = b'{"state":"unavailable"}'
    manifest = _manifest(payload)
    raw_artifacts.write_immutable_raw_artifact_bundle(
        manifest, {"raw-output": payload}, project_dir=tmp_path
    )
    sentinel = tmp_path / "projects/example/writer_assistant/review_queue/sentinel.json"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("owner-controlled state", encoding="utf-8")
    original_remove = raw_artifacts._remove_immutable_payloads

    def interrupt_after_intent(project_dir, stored_manifest):
        raise RuntimeError("simulated interruption after deletion intent")

    monkeypatch.setattr(raw_artifacts, "_remove_immutable_payloads", interrupt_after_intent)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        raw_artifacts.delete_immutable_raw_artifact_bundle(
            "example",
            "bundle-analysis-run-001",
            project_dir=tmp_path,
            deleted_at="2026-08-30T20:01:00Z",
            deletion_id="deletion-recovery-001",
            owner_controlled=True,
        )
    incomplete = raw_artifacts.read_immutable_raw_artifact_bundle(
        "example", "bundle-analysis-run-001", project_dir=tmp_path
    )
    assert incomplete["status"] == "deletion_in_progress"
    assert incomplete["deletion_state"] == "in_progress"
    assert incomplete["content_available"] is True
    assert "tombstone" not in incomplete
    assert raw_artifacts.read_raw_artifact_manifest_compatible(
        "example", "bundle-analysis-run-001", project_dir=tmp_path
    )["status"] == "deletion_in_progress"

    monkeypatch.setattr(raw_artifacts, "_remove_immutable_payloads", original_remove)
    recovered = raw_artifacts.delete_immutable_raw_artifact_bundle(
        "example",
        "bundle-analysis-run-001",
        project_dir=tmp_path,
        deleted_at="2099-01-01T00:00:00Z",
        deletion_id="deletion-recovery-001",
        owner_controlled=False,
    )
    assert recovered["status"] == "deleted"
    assert recovered["idempotent"] is True
    assert recovered["tombstone"]["deleted_at"] == "2026-08-30T20:01:00Z"
    assert recovered["tombstone"]["content_retained"] is False
    assert recovered["tombstone"]["replayable"] is False
    serialized = json.dumps(recovered["tombstone"], sort_keys=True)
    assert "unavailable" not in serialized
    assert "source_text" not in serialized and "payload" not in serialized
    artifact_path = tmp_path / "projects/example/writer_assistant/raw_artifacts/bundle-analysis-run-001/artifacts/output.json"
    assert not artifact_path.exists()
    assert sentinel.read_text(encoding="utf-8") == "owner-controlled state"


def test_concurrent_ledger_publication_is_deterministic_for_replay_and_conflict(tmp_path):
    base_payload = {
        "artifact_id": "bundle-001",
        "artifact_manifest_hash": "a" * 64,
        "artifact_bundle_hash": "b" * 64,
        "analysis_run_manifest_hash": "c" * 64,
        "source_snapshot_ids": ["snapshot-001"],
        "availability": "available",
    }
    start = threading.Barrier(3)

    def publish(payload):
        start.wait(timeout=5)
        return append_evidence_ledger_event(
            project_dir=tmp_path,
            project_id="example",
            run_id="analysis-run-concurrent",
            event_type="artifact_recorded",
            idempotency_key="artifact-concurrent",
            created_at="2026-08-30T20:00:00Z",
            payload=payload,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(publish, copy.deepcopy(base_payload)) for _ in range(2)]
        start.wait(timeout=5)
        events = [future.result(timeout=5) for future in futures]
    assert events[0]["event_hash"] == events[1]["event_hash"]
    assert len(scan_evidence_ledger(
        project_dir=tmp_path, project_id="example", run_id="analysis-run-concurrent"
    )) == 1

    conflict_start = threading.Barrier(3)
    def publish_conflict(payload):
        conflict_start.wait(timeout=5)
        return append_evidence_ledger_event(
            project_dir=tmp_path,
            project_id="example",
            run_id="analysis-run-conflict",
            event_type="artifact_recorded",
            idempotency_key="artifact-conflict",
            created_at="2026-08-30T20:00:01Z",
            payload=payload,
        )
    changed = copy.deepcopy(base_payload)
    changed["availability"] = "unavailable"
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(publish_conflict, payload) for payload in (base_payload, changed)]
        conflict_start.wait(timeout=5)
        outcomes = []
        for future in futures:
            try:
                outcomes.append(future.result(timeout=5))
            except ValueError as exc:
                outcomes.append(exc)
    assert sum(isinstance(item, dict) for item in outcomes) == 1
    assert sum(isinstance(item, ValueError) and "conflict" in str(item) for item in outcomes) == 1
    assert len(scan_evidence_ledger(
        project_dir=tmp_path, project_id="example", run_id="analysis-run-conflict"
    )) == 1
