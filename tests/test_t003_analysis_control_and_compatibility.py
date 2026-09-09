from __future__ import annotations

import copy
import concurrent.futures
import json
import threading
from contextlib import contextmanager

import pytest

from backend import main, omi_analysis_orchestrator, project_manager
from backend.routes import omi_analysis_runs
from backend.story_knowledge import analysis_run_control, persisted_compatibility
from backend.story_knowledge.apply_promotion import build_promotion_audit_record
from backend.story_knowledge.evidence_ledger import (
    append_evidence_ledger_event,
    resolve_evidence_ledger,
    scan_evidence_ledger,
)
from backend.story_knowledge.promotion_apply_events import append_event


def _project(monkeypatch, tmp_path):
    projects = tmp_path / "projects"
    project = projects / "example"
    project.mkdir(parents=True)
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", projects)
    monkeypatch.setattr(project_manager, "REPO_ROOT", tmp_path)
    return project


def _fake_result(*args, **kwargs):
    adapters = kwargs["requested_adapters"]
    return {
        "analysis_status": "fail_closed",
        "explanation": "selected fixtures unavailable",
        "source_idea_id": kwargs.get("source_idea_id"),
        "adapter_results": [
            {
                "adapter": adapter,
                "state": "unavailable",
                "explanation": "fixture not supplied",
                "candidates": [],
            }
            for adapter in adapters
        ],
        "findings": [],
        "persisted_candidate_ids": [],
        "safety": {
            "no_prose": True,
            "no_memory_canon_mutation": True,
            "no_apply_promotion": True,
        },
    }


def _finding_result(*args, provenance_extra=None, **kwargs):
    adapter = kwargs["requested_adapters"][0]
    provenance = {
        "tool_source": adapter,
        "adapter": adapter,
        "support": "direct source support only",
        **(provenance_extra or {}),
    }
    finding = {
        "candidate_type": "evidence_note",
        "label": "Focused evidence",
        "extracted_claim": "The selected subspan supplies bounded support.",
        "evidence": [{"source_excerpt": "café 雨", "source_locator": "raw_idea:exact"}],
        "source_locator": "raw_idea:exact",
        "provenance": provenance,
        "source_adapter": adapter,
        "support_label": "bounded support",
        "owner_decision": {"decision": "pending", "approved": False},
        "review_status": "candidate_review_pending",
        "raw_finding_id": "finding-001",
    }
    return {
        "analysis_status": "succeeded",
        "explanation": "fixture completed",
        "source_idea_id": kwargs.get("source_idea_id"),
        "adapter_results": [{
            "adapter": adapter,
            "state": "succeeded",
            "explanation": "fixture completed",
            "candidates": [finding],
        }],
        "findings": [finding],
        "persisted_candidate_ids": [],
        "safety": {
            "no_prose": True,
            "no_memory_canon_mutation": True,
            "no_apply_promotion": True,
        },
    }


def test_routes_and_truthful_control_capabilities_are_registered():
    paths = {route.path for route in omi_analysis_runs.router.routes}
    assert "/api/projects/{project_id}/omi/analysis/tools" in paths
    assert "/api/projects/{project_id}/omi/analysis/runs" in paths
    assert "/api/projects/{project_id}/omi/analysis/runs/{run_id}" in paths
    assert "/api/projects/{project_id}/omi/analysis/runs/{run_id}/result" in paths
    assert main.submit_omi_analysis_run is omi_analysis_runs.submit_analysis_run
    assert main.get_omi_analysis_run_status is omi_analysis_runs.get_analysis_run_status
    assert not any(path.endswith("/cancel") for path in paths)
    with pytest.raises(Exception):
        omi_analysis_runs.AnalysisRunSubmit(
            raw_idea="Owner input",
            requested_adapters=["spacy"],
            timeout_seconds=5,
        )
    report = analysis_run_control.supported_analysis_tools("example", env={})
    assert report["execution_mode"] == "synchronous"
    assert report["timeout"]["supported"] is False
    assert report["cancellation"]["supported"] is False
    assert {tool["adapter_id"] for tool in report["tools"]} == analysis_run_control.SUPPORTED_ADAPTERS


def test_stable_run_replay_status_result_and_deleted_nonreplayability(monkeypatch, tmp_path):
    _project(monkeypatch, tmp_path)
    first = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="Owner café note.",
        source_idea_id="idea-001",
        requested_adapters=["spacy"],
        idempotency_key="request-001",
        runner=_fake_result,
        created_at="2026-08-30T20:00:00Z",
    )
    assert first["state"] == "degraded"
    assert first["timeout_supported"] is False
    assert first["candidate_persistence_performed"] is False
    initial_chain = scan_evidence_ledger(
        project_dir=tmp_path / "projects/example",
        project_id="example",
        run_id=first["run_id"],
    )
    contributor = next(event for event in initial_chain if event["event_type"] == "contributor_recorded")
    unsuccessful_evidence = next(event for event in initial_chain if event["event_type"] == "evidence_recorded")
    assert contributor["payload"]["result_state"] == "unavailable"
    assert unsuccessful_evidence["payload"]["disposition"] == "unverified"
    assert unsuccessful_evidence["payload"]["reason"] == "fixture not supplied"
    manifest_path = (
        tmp_path / "projects/example/writer_assistant/analysis_runs"
        / first["run_id"] / "manifest.json"
    )
    persisted_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    compatible_manifest = persisted_compatibility.read_compatible_record(
        persisted_manifest, record_kind="analysis_manifest"
    )
    assert compatible_manifest["version_state"] == "new"
    assert compatible_manifest["physical_migration_performed"] is False
    replay = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="Owner café note.",
        source_idea_id="idea-001",
        requested_adapters=["spacy"],
        idempotency_key="request-001",
        runner=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not rerun")),
    )
    assert replay["run_id"] == first["run_id"]
    assert replay["idempotent_replay"] is True
    with pytest.raises(ValueError, match="idempotency conflict"):
        analysis_run_control.submit_analysis_run(
            "example",
            raw_idea="Different owner input",
            source_idea_id="idea-001",
            requested_adapters=["spacy"],
            idempotency_key="request-001",
            runner=_fake_result,
        )
    result = analysis_run_control.get_analysis_run_result("example", first["run_id"])
    assert result["result_available"] is True
    assert result["result"]["analysis_status"] == "fail_closed"
    deleted = analysis_run_control.delete_analysis_run_artifacts(
        "example",
        first["run_id"],
        deletion_id="owner-delete-001",
        deleted_at="2026-08-30T20:05:00Z",
        owner_controlled=True,
    )
    assert deleted["candidate_review_promotion_approved_stores_mutated"] is False
    after = analysis_run_control.get_analysis_run_result("example", first["run_id"])
    assert after["artifact_status"] == "deleted"
    assert after["result_available"] is False
    assert after["replayable"] is False
    compatible_deleted = persisted_compatibility.read_compatible_record(
        after["tombstone"], record_kind="raw_artifact"
    )
    assert compatible_deleted["version_state"] == "deleted"
    assert compatible_deleted["stored_input_mutated"] is False
    resolved = resolve_evidence_ledger(
        project_dir=tmp_path / "projects/example",
        project_id="example",
        run_id=first["run_id"],
    )
    evidence_events = [event for event in resolved if event["event_type"] == "evidence_recorded"]
    assert evidence_events[0]["payload"]["content_available"] is False
    assert evidence_events[0]["resolution"]["replayable"] is False


def test_partial_and_controlled_error_states_are_truthful(monkeypatch, tmp_path):
    _project(monkeypatch, tmp_path)

    def partial(*args, **kwargs):
        return {
            **_fake_result(*args, **kwargs),
            "analysis_status": "succeeded",
            "adapter_results": [
                {"adapter": "spacy", "state": "empty", "explanation": "ran safely", "candidates": []},
                {"adapter": "booknlp", "state": "unavailable", "explanation": "not installed", "candidates": []},
            ],
        }

    partial_run = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="Owner note",
        source_idea_id=None,
        requested_adapters=["spacy", "booknlp"],
        runner=partial,
        created_at="2026-08-30T20:00:00Z",
    )
    assert partial_run["state"] == "partial"
    error_run = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="Different owner note",
        source_idea_id=None,
        requested_adapters=["spacy"],
        runner=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("fixture error")),
        created_at="2026-08-30T20:00:01Z",
    )
    assert error_run["state"] == "error"
    unsafe = _fake_result(
        "example", "Unsafe distinct input", requested_adapters=["spacy"]
    )
    unsafe["generated_prose"] = "forbidden"
    with pytest.raises(ValueError, match="product safety boundary"):
        analysis_run_control.submit_analysis_run(
            "example",
            raw_idea="Unsafe distinct input",
            source_idea_id=None,
            requested_adapters=["spacy"],
            runner=lambda *args, **kwargs: unsafe,
            created_at="2026-08-30T20:00:02Z",
        )


def test_t003g_detects_old_new_mixed_malformed_deleted_without_migration():
    old = {"schema_version": "1.0"}
    new = {"schema_version": "raw-artifact-bundle.v2"}
    assert persisted_compatibility.detect_persisted_version(
        old, record_kind="raw_artifact"
    )["state"] == "legacy"
    assert persisted_compatibility.detect_persisted_version(
        new, record_kind="raw_artifact"
    )["state"] == "new"
    assert persisted_compatibility.detect_persisted_version(
        [old, new], record_kind="raw_artifact"
    )["state"] == "mixed"
    assert persisted_compatibility.detect_persisted_version(
        "bad", record_kind="raw_artifact"
    )["state"] == "malformed"
    deleted = {"schema_version": "analysis-artifact-deletion-tombstone.v1", "deletion_state": "deleted"}
    assert persisted_compatibility.detect_persisted_version(
        deleted, record_kind="raw_artifact"
    )["state"] == "deleted"
    assert old == {"schema_version": "1.0"}


def test_finding_span_roles_dependency_graph_and_actual_provenance(monkeypatch, tmp_path):
    _project(monkeypatch, tmp_path)
    first = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="AA café 雨 ZZ",
        source_idea_id="idea-exact",
        requested_adapters=["spacy"],
        runner=lambda *args, **kwargs: _finding_result(
            *args,
            provenance_extra={
                "implementation_kind": "fixture_mock",
                "tool": {"availability": "available", "name": "spaCy fixture", "version": "3.7"},
                "runtime": {"availability": "available", "name": "python", "version": "3.12"},
                "provider": {"availability": "unknown"},
                "model": {"availability": "available", "name": "fixture-model", "version": "1"},
            },
            **kwargs,
        ),
        created_at="2026-08-30T20:00:00Z",
    )
    run_dir = tmp_path / "projects/example/writer_assistant/analysis_runs" / first["run_id"]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    operation = manifest["operations"][0]
    assert operation["consumes"] == ["owner_selected_source"]
    assert operation["produces"] == ["raw_extraction_evidence", "normalized_evidence"]
    provenance = manifest["contributors"][0]["provenance"]
    assert provenance["adapter_id"] == "spacy"
    assert provenance["implementation_kind"] == "fixture_mock"
    assert provenance["tool"] == {"availability": "available", "name": "spaCy fixture", "version": "3.7"}
    assert provenance["model"] == {"availability": "available", "name": "fixture-model", "version": "1"}
    chain = scan_evidence_ledger(
        project_dir=tmp_path / "projects/example", project_id="example", run_id=first["run_id"]
    )
    exact = next(
        event["payload"] for event in chain
        if event["event_type"] == "evidence_recorded" and event["payload"]["output_id"] is not None
    )
    locator = exact["source_locator"]
    assert (locator["char_start"], locator["char_end"]) == (3, 9)
    assert (locator["byte_start"], locator["byte_end"]) == (3, 12)
    assert exact["excerpt_hash"] == __import__("hashlib").sha256("café 雨".encode("utf-8")).hexdigest()

    graph_run = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea="Different source",
        source_idea_id="idea-graph",
        requested_adapters=["spacy", "subtxt", "ncp"],
        runner=_fake_result,
        created_at="2026-08-30T20:00:01Z",
    )
    graph_path = tmp_path / "projects/example/writer_assistant/analysis_runs" / graph_run["run_id"] / "manifest.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    operations = {item["adapter_id"]: item for item in graph["operations"]}
    assert operations["subtxt"]["consumes"] == ["normalized_evidence"]
    assert operations["ncp"]["consumes"] == ["imported_artifact"]
    assert operations["ncp"]["produces"] == ["gateway_input_output"]
    assert graph["dependency_graph"] == [{
        "producer_operation_id": "analyze-spacy",
        "consumer_operation_id": "analyze-subtxt",
        "dependency_class": "normalized_evidence",
    }]
    contributors = {item["adapter_id"]: item for item in graph["contributors"]}
    assert contributors["subtxt"]["result_state"] == "unavailable"
    assert contributors["ncp"]["result_state"] == "unavailable"
    assert contributors["spacy"]["provenance"]["tool"]["availability"] == "unavailable"


def test_ollama_exact_source_operation_manifest_and_lineage_are_distinct(
    monkeypatch, tmp_path
):
    _project(monkeypatch, tmp_path)
    source = "AA café 雨 ZZ"
    run = analysis_run_control.submit_analysis_run(
        "example",
        raw_idea=source,
        source_idea_id="idea-ollama-exact-source",
        requested_adapters=["ollama_model"],
        runner=_finding_result,
        created_at="2026-09-08T20:00:00Z",
    )
    run_dir = (
        tmp_path
        / "projects/example/writer_assistant/analysis_runs"
        / run["run_id"]
    )
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

    assert omi_analysis_orchestrator.OMI_OLLAMA_ADAPTER_NAME == "ollama_model"
    operation = manifest["operations"][0]
    operation_id = omi_analysis_orchestrator.OMI_OLLAMA_EXACT_SOURCE_OPERATION_ID
    assert operation == {
        "operation_id": operation_id,
        "adapter_id": "ollama_model",
        "consumes": ["owner_selected_source"],
        "produces": ["diagnostic_candidate_finding"],
        "configuration": {
            "execution_mode": "synchronous",
            "adapter_role": "exact_source_structured_extractor",
            "operation_semantics": "exact_source_structured_extraction",
        },
        "feature_flags": {"candidate_persistence": False},
    }
    assert "normalized_evidence" not in operation["consumes"]

    contributor = manifest["contributors"][0]
    assert contributor["operation_id"] == operation_id
    assert contributor["adapter_id"] == "ollama_model"
    assert contributor["provenance"]["operation_id"] == operation_id
    assert contributor["provenance"]["adapter_id"] == "ollama_model"
    assert {item["operation_id"] for item in manifest["outputs"]} == {operation_id}
    assert {item["operation_id"] for item in manifest["transformations"]} == {
        operation_id
    }

    source_identity = manifest["sources"][0]
    source_hash = __import__("hashlib").sha256(source.encode("utf-8")).hexdigest()
    assert source_identity["content_hash"] == source_hash
    source_artifact = next(
        item
        for item in manifest["artifact_references"]
        if item["artifact_id"] == "source-artifact"
    )
    assert source_artifact["content_hash"] == source_hash
    assert source_artifact["source_snapshot_ids"] == [source_identity["snapshot_id"]]

    exact_contract = analysis_run_control._OPERATION_CONTRACTS[operation_id]
    assert exact_contract["adapter_id"] == "ollama_model"
    assert exact_contract["operation_semantics"] == (
        "exact_source_structured_extraction"
    )
    assert analysis_run_control._DEFAULT_OPERATION_BY_ADAPTER["ollama_model"] == (
        operation_id
    )


def test_t003g_validates_standalone_ledger_and_promotion_audit_variants(tmp_path):
    payload = {
        "artifact_id": "bundle-001",
        "artifact_manifest_hash": "a" * 64,
        "artifact_bundle_hash": "b" * 64,
        "analysis_run_manifest_hash": "c" * 64,
        "source_snapshot_ids": ["snapshot-001"],
        "availability": "available",
    }
    event = append_evidence_ledger_event(
        project_dir=tmp_path,
        project_id="example",
        run_id="analysis-run-compat",
        event_type="artifact_recorded",
        idempotency_key="artifact-001",
        created_at="2026-08-30T20:00:00Z",
        payload=payload,
    )
    assert persisted_compatibility.read_compatible_record(
        event, record_kind="ledger_event"
    )["record"] == event
    for field in ("event_hash", "event_scope_hash"):
        tampered = copy.deepcopy(event)
        tampered[field] = "f" * 64
        with pytest.raises(ValueError):
            persisted_compatibility.read_compatible_record(tampered, record_kind="ledger_event")
    wrong_sequence = copy.deepcopy(event)
    wrong_sequence["sequence"] = 2
    wrong_sequence["event_hash"] = analysis_run_control.canonical_sha256(
        {key: value for key, value in wrong_sequence.items() if key != "event_hash"}
    )
    with pytest.raises(ValueError, match="sequence"):
        persisted_compatibility.read_compatible_record(wrong_sequence, record_kind="ledger_event")
    wrong_predecessor = copy.deepcopy(event)
    wrong_predecessor["previous_event_hash"] = "a" * 64
    wrong_predecessor["event_hash"] = analysis_run_control.canonical_sha256(
        {key: value for key, value in wrong_predecessor.items() if key != "event_hash"}
    )
    with pytest.raises(ValueError, match="previous"):
        persisted_compatibility.read_compatible_record(wrong_predecessor, record_kind="ledger_event")

    legacy = build_promotion_audit_record({
        "project_id": "example",
        "candidate_id": "candidate-001",
        "destination_type": "story_bible",
        "destination_path": "story_bible/entry.json",
        "destination_key": "entry",
        "owner_actor_id": "owner-001",
        "owner_confirmation": True,
        "evidence_refs": ["evidence-001"],
        "provenance_refs": ["provenance-001"],
        "source_locator_refs": ["locator-001"],
        "promotion_status": "dry_run",
    })
    assert persisted_compatibility.read_compatible_record(
        legacy, record_kind="promotion_audit"
    )["record"] == legacy
    malformed_legacy = copy.deepcopy(legacy)
    malformed_legacy["owner_confirmation"] = False
    with pytest.raises(ValueError):
        persisted_compatibility.read_compatible_record(
            malformed_legacy, record_kind="promotion_audit"
        )

    promotion_dir = tmp_path / "promotion-project"
    promotion_dir.mkdir()
    promotion_event = append_event(
        promotion_dir,
        event_type="draft_superseded",
        project_id="example",
        promotion_id="promotion-001",
        candidate_id="candidate-001",
        revision=2,
        idempotency_key="11111111-1111-4111-8111-111111111111",
        operation_identity="prep_" + "c" * 64,
        created_at="2030-01-01T00:00:00Z",
        content={
            "preparation_id": "prep_" + "c" * 64,
            "preparation_scope_hash": "a" * 64,
            "superseded_revision": 1,
            "superseding_revision": 2,
            "superseded_draft_scope_hash": "a" * 64,
            "superseding_draft_scope_hash": "b" * 64,
            "authoritative_owner_actor": {
                "actor_type": "owner", "owner_id": "owner_a", "display_name": "Owner",
                "identity_source": "project_local_owner_config", "config_version": 1,
                "config_hash": "a" * 64,
            },
            "rationale": "Supersede the reviewed draft.",
        },
    ).event
    assert persisted_compatibility.read_compatible_record(
        promotion_event, record_kind="promotion_audit"
    )["record"] == promotion_event
    corrupted = copy.deepcopy(promotion_event)
    corrupted["event_content_hash"] = "f" * 64
    with pytest.raises(ValueError):
        persisted_compatibility.read_compatible_record(corrupted, record_kind="promotion_audit")
    unsupported = copy.deepcopy(promotion_event)
    unsupported["event_version"] = "promotion_apply_event.v999"
    with pytest.raises(ValueError):
        persisted_compatibility.read_compatible_record(unsupported, record_kind="promotion_audit")
    mixed = persisted_compatibility.read_compatible_record(
        [legacy, promotion_event], record_kind="promotion_audit"
    )
    assert mixed["version_state"] == "mixed"
    assert mixed["records"] == [legacy, promotion_event]


def test_concurrent_run_submission_is_one_execution_one_replay_and_conflicts(monkeypatch, tmp_path):
    _project(monkeypatch, tmp_path)
    start = threading.Barrier(3)
    entered = threading.Event()
    release = threading.Event()
    calls = 0
    calls_guard = threading.Lock()

    def runner(*args, **kwargs):
        nonlocal calls
        with calls_guard:
            calls += 1
        entered.set()
        assert release.wait(timeout=5)
        return _fake_result(*args, **kwargs)

    def submit(raw_idea):
        start.wait(timeout=5)
        return analysis_run_control.submit_analysis_run(
            "example",
            raw_idea=raw_idea,
            source_idea_id="idea-concurrent",
            requested_adapters=["spacy"],
            idempotency_key="request-concurrent",
            runner=runner,
            created_at="2026-08-30T20:00:00Z",
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(submit, "Owner input") for _ in range(2)]
        start.wait(timeout=5)
        assert entered.wait(timeout=5)
        release.set()
        results = [future.result(timeout=5) for future in futures]
    assert calls == 1
    assert {item["run_id"] for item in results} == {results[0]["run_id"]}
    assert sorted(item["idempotent_replay"] for item in results) == [False, True]

    conflict_start = threading.Barrier(3)
    def conflicting(raw_idea):
        conflict_start.wait(timeout=5)
        return analysis_run_control.submit_analysis_run(
            "example",
            raw_idea=raw_idea,
            source_idea_id="idea-conflict",
            requested_adapters=["spacy"],
            idempotency_key="request-conflict",
            runner=_fake_result,
            created_at="2026-08-30T20:00:01Z",
        )
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(conflicting, text) for text in ("First input", "Second input")]
        conflict_start.wait(timeout=5)
        outcomes = []
        for future in futures:
            try:
                outcomes.append(future.result(timeout=5))
            except ValueError as exc:
                outcomes.append(exc)
    assert sum(isinstance(item, dict) for item in outcomes) == 1
    assert sum(isinstance(item, ValueError) and "idempotency conflict" in str(item) for item in outcomes) == 1


def _concurrent_semantic_replay(
    monkeypatch,
    *,
    requests,
    source_idea_id,
):
    original_lock = analysis_run_control._acquire_submission_lock
    lock_arrivals = threading.Barrier(2)
    seen_request_scopes = []
    scopes_guard = threading.Lock()

    @contextmanager
    def synchronized_lock(*, project_dir, project_id, scope):
        if scope.startswith("request:"):
            with scopes_guard:
                seen_request_scopes.append(scope)
            lock_arrivals.wait(timeout=5)
        with original_lock(project_dir=project_dir, project_id=project_id, scope=scope):
            yield

    monkeypatch.setattr(analysis_run_control, "_acquire_submission_lock", synchronized_lock)
    runner_entered = threading.Event()
    second_runner_entered = threading.Event()
    release_runner = threading.Event()
    calls = 0
    calls_guard = threading.Lock()

    def runner(*args, **kwargs):
        nonlocal calls
        with calls_guard:
            calls += 1
            call_number = calls
        runner_entered.set()
        if call_number == 2:
            second_runner_entered.set()
        assert release_runner.wait(timeout=5)
        return _fake_result(*args, **kwargs)

    def submit(request):
        return analysis_run_control.submit_analysis_run(
            "example",
            raw_idea="Canonical owner input",
            source_idea_id=source_idea_id,
            requested_adapters=request["requested_adapters"],
            allow_deterministic_fallback=request.get("allow_deterministic_fallback", False),
            runner=runner,
            created_at="2026-08-30T20:10:00Z",
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(submit, request) for request in requests]
        assert runner_entered.wait(timeout=5)
        second_runner_entered.wait(timeout=0.5)
        release_runner.set()
        results = [future.result(timeout=5) for future in futures]
    return calls, seen_request_scopes, results


def test_concurrent_adapter_order_permutations_share_canonical_request_lock(monkeypatch, tmp_path):
    project = _project(monkeypatch, tmp_path)
    calls, scopes, results = _concurrent_semantic_replay(
        monkeypatch,
        source_idea_id="idea-adapter-order",
        requests=[
            {"requested_adapters": ["spacy", "booknlp"]},
            {"requested_adapters": ["booknlp", "spacy"]},
        ],
    )

    assert calls == 1
    assert len(scopes) == 2
    assert len(set(scopes)) == 1
    assert len({item["run_id"] for item in results}) == 1
    assert sorted(item["idempotent_replay"] for item in results) == [False, True]
    runs_root = project / "writer_assistant" / "analysis_runs"
    run_directories = [path for path in runs_root.iterdir() if path.is_dir()]
    assert len(run_directories) == 1
    chain = scan_evidence_ledger(
        project_dir=project,
        project_id="example",
        run_id=results[0]["run_id"],
    )
    assert chain
    assert len({event["event_hash"] for event in chain}) == len(chain)
    assert len({(event["event_type"], event["idempotency_key"]) for event in chain}) == len(chain)
    record = json.loads((run_directories[0] / "run.json").read_text(encoding="utf-8"))
    assert record["evidence_ledger_ref"]["event_count_at_finalization"] == len(chain)


def test_concurrent_deterministic_fallback_normalization_shares_request_lock(monkeypatch, tmp_path):
    _project(monkeypatch, tmp_path)
    calls, scopes, results = _concurrent_semantic_replay(
        monkeypatch,
        source_idea_id="idea-fallback-normalization",
        requests=[
            {
                "requested_adapters": ["spacy"],
                "allow_deterministic_fallback": True,
            },
            {
                "requested_adapters": ["deterministic_fallback", "spacy"],
                "allow_deterministic_fallback": True,
            },
        ],
    )

    assert calls == 1
    assert len(scopes) == 2
    assert len(set(scopes)) == 1
    assert len({item["run_id"] for item in results}) == 1
    assert sorted(item["idempotent_replay"] for item in results) == [False, True]
