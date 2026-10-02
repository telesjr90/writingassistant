"""PHASE8-IMPL-017-T006 approved memory/canon mutation safety regression."""

from __future__ import annotations

import copy
import json
import uuid
from pathlib import Path
from typing import Any

import anyio
import httpx
import pytest

from backend import main, project_manager
from backend.routes import apply_promotion as apply_promotion_route
from backend.story_knowledge import (
    apply_promotion,
    candidate_persistence,
    candidate_record,
    candidate_review_gate,
    review_queue_storage,
)
from backend.story_knowledge.apply_contract import ApplyContractError


PROJECT_ID = "example"
CANDIDATE_ID = "core_candidate_scene_001_character_001"
QUEUE_ENTRY_ID = "review_queue_entry_scene_001_character_001"
TARGET_CANDIDATE_ID = "core_candidate_scene_002_character_001"
TARGET_QUEUE_ENTRY_ID = "review_queue_entry_scene_002_character_001"
REVIEW_FIXTURE_TIME = "2026-08-09T20:00:00Z"

ALLOWED_REVIEW_COMMANDS = (
    "approve",
    "mark_reviewed",
    "request_more_evidence",
    "defer",
    "reject",
    "mark_duplicate",
    "mark_split_required",
    "quarantine",
    "update_owner_note",
    "set_review_status",
)


class RouteClient:
    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        async def send_request() -> httpx.Response:
            transport = httpx.ASGITransport(app=main.app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as async_client:
                return await async_client.request(method, path, **kwargs)

        return anyio.run(send_request)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)


@pytest.fixture
def route_client() -> RouteClient:
    return RouteClient()


def valid_promotion_request(**overrides: Any) -> dict[str, Any]:
    request = {
        "project_id": PROJECT_ID,
        "candidate_id": CANDIDATE_ID,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_type": "character_candidate",
        "owner_actor_id": "owner-001",
        "owner_actor_label": "Owner",
        "owner_confirmation": True,
        "owner_note": "Owner-authored audit note.",
        "destination_type": "approved_character",
        "destination_path": "memory/characters/character_001.json",
        "destination_key": "character_001",
        "approved_payload": {
            "record_type": "approved_character",
            "name": "Owner-authored character label",
            "facts": [
                {
                    "field": "role",
                    "value": "owner-approved analytical note",
                    "evidence_refs": ["evidence-001"],
                    "provenance_refs": ["provenance-001"],
                }
            ],
        },
        "evidence_refs": ["evidence-001"],
        "provenance_refs": ["provenance-001"],
        "source_locator_refs": ["source-locator-001"],
        "source_candidate_snapshot_hash": "candidate-snapshot-001",
        "requested_at": "2026-06-28T00:00:00Z",
        "boundary_flags": [
            "candidate persistence is not canon",
            "queue presence is not approval",
            "confidence is not truth",
            "raw artifacts are support data",
        ],
    }
    request.update(overrides)
    return request


def valid_candidate_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "candidate_id": CANDIDATE_ID,
        "project_id": PROJECT_ID,
        "candidate_type": "character_candidate",
        "status": "candidate",
        "target_category": "characters",
        "source_locator": {"source_locator_id": "source-locator-001"},
        "evidence": [{"evidence_id": "evidence-001"}],
        "provenance": [{"provenance_id": "provenance-001"}],
        "owner_decision": "undecided",
        "destination": "character_memory_candidate",
        "confidence": 0.88,
        "candidate_payload": {"name": "Owner-authored character label"},
        "snapshot_hash": "candidate-snapshot-001",
    }
    record.update(overrides)
    return record


def valid_queue_entry(**overrides: Any) -> dict[str, Any]:
    entry = {
        "queue_entry_id": QUEUE_ENTRY_ID,
        "project_id": PROJECT_ID,
        "candidate_record_id": CANDIDATE_ID,
        "candidate_type": "character_candidate",
        "review_status": "pending",
        "lifecycle_state": "owner_review_pending",
        "evidence_refs": ["evidence-001"],
        "provenance_refs": ["provenance-001"],
        "source_locator": {"source_locator_id": "source-locator-001"},
        "confidence": 0.88,
        "human_review_required": True,
    }
    entry.update(overrides)
    return entry


def valid_review_candidate_record(
    candidate_id: str = CANDIDATE_ID,
    source_document_id: str = "scene_001",
) -> dict[str, Any]:
    return candidate_record.validate_candidate_record(
        {
            "candidate_id": candidate_id,
            "project_id": PROJECT_ID,
            "candidate_type": "character_candidate",
            "status": "candidate",
            "target_category": "characters",
            "source_locator": {
                "project_id": PROJECT_ID,
                "source_document_type": "scene",
                "source_document_id": source_document_id,
                "section_id": None,
                "chapter_id": None,
                "scene_id": "scene_001",
                "line_start": None,
                "line_end": None,
                "char_start": None,
                "char_end": None,
                "source_hash": None,
            },
            "evidence": [],
            "provenance": {
                "origin": "extractor",
                "extraction_method": "fixture_orchestrator",
                "timestamp": REVIEW_FIXTURE_TIME,
                "human_review_required": True,
            },
            "owner_decision": "undecided",
            "destination": "omi_candidate_only",
            "confidence": 0.4,
            "created_at": REVIEW_FIXTURE_TIME,
            "updated_at": REVIEW_FIXTURE_TIME,
        }
    )


def valid_review_queue_entry(
    candidate: dict[str, Any], queue_entry_id: str = QUEUE_ENTRY_ID
) -> dict[str, Any]:
    entry = candidate_review_gate.build_review_queue_entry(candidate, project_id=PROJECT_ID)
    entry.update(
        queue_entry_id=queue_entry_id,
        review_status="pending",
        lifecycle_state="owner_review_pending",
        evidence_summary="Evidence summary",
        evidence_refs=["evidence_001"],
        provenance_summary="Fixture provenance",
        provenance_refs=["fixture_orchestrator"],
        review_version=0,
        owner_note=None,
        rationale=None,
        duplicate_candidate_ids=None,
        superseded_by_candidate_id=None,
        rejected_output_reason=None,
        insufficient_evidence_reason=None,
        quarantine_note=None,
        owner_review_completed=False,
        owner_reviewed_at=None,
    )
    return review_queue_storage.validate_review_queue_entry(entry)


def build_valid_plan() -> dict[str, Any]:
    return apply_promotion.build_promotion_plan(
        valid_promotion_request(),
        candidate_record=valid_candidate_record(),
        queue_entry=valid_queue_entry(),
    )


def review_command_payload(action_type: str, **overrides: Any) -> dict[str, Any]:
    payload = {
        "action_type": action_type,
        "queue_entry_id": QUEUE_ENTRY_ID,
        "candidate_id": CANDIDATE_ID,
        "actor": "owner-reviewed",
        "owner_confirmed": True,
        "preserve_candidate_linkage": True,
        "preserve_evidence_provenance": True,
        "idempotency_key": str(uuid.uuid4()),
        "expected_current_review_status": "pending",
        "expected_current_version": 0,
    }
    payload.update(
        {
            "approve": {
                "owner_note": "Owner approves review metadata only.",
                "rationale": "Evidence supports review approval.",
            },
            "request_more_evidence": {"owner_note": "Need more supporting evidence."},
            "defer": {"owner_note": "Defer for later owner review."},
            "reject": {"owner_note": "Reject after owner review."},
            "mark_duplicate": {
                "owner_note": "Owner marks this as a duplicate candidate.",
                "duplicate_candidate_ids": [TARGET_CANDIDATE_ID],
                "duplicate_target_queue_entry_id": TARGET_QUEUE_ENTRY_ID,
                "duplicate_target_expected_review_status": "pending",
                "duplicate_target_expected_version": 0,
            },
            "mark_split_required": {
                "owner_note": "This incorrect cluster requires a later split.",
                "rationale": "The evidence supports separately reviewable units.",
            },
            "quarantine": {"owner_note": "The supporting evidence is invalid."},
            "update_owner_note": {"owner_note": "Owner-authored review note."},
            "set_review_status": {
                "target_review_status": "deferred",
                "owner_note": "Defer through the review-status command.",
            },
        }.get(action_type, {})
    )
    payload.update(overrides)
    return payload


def approved_memory_files(project_dir: Path) -> list[Path]:
    return sorted((project_dir / "writer_assistant" / "approved_memory").rglob("*.json"))


def promotion_audit_files(project_dir: Path) -> list[Path]:
    return sorted((project_dir / "writer_assistant" / "promotion_audit").rglob("*.json"))


def file_snapshots(paths: list[Path]) -> list[tuple[Path, bytes]]:
    return [(path, path.read_bytes()) for path in paths]


def assert_no_memory_or_applied_audit(project_dir: Path) -> None:
    assert approved_memory_files(project_dir) == []
    applied = []
    for path in promotion_audit_files(project_dir):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("promotion_status") == "applied":
            applied.append(record)
    assert applied == []


def test_plan_building_validation_does_not_mutate_approved_memory_or_audit(tmp_path: Path) -> None:
    validated = apply_promotion.validate_promotion_request(valid_promotion_request())
    plan = build_valid_plan()

    assert validated["validation_status"] == "valid"
    assert plan["validation_status"] == "valid"
    assert plan["mutation_performed"] is False
    assert plan["mutation_preview"]["will_mutate_only_after_apply"] is True
    assert_no_memory_or_applied_audit(tmp_path)


@pytest.mark.parametrize("owner_confirmation", [None, False])
def test_apply_requires_explicit_owner_confirmation_without_mutation(
    tmp_path: Path,
    owner_confirmation: bool | None,
) -> None:
    request = valid_promotion_request(owner_confirmation=owner_confirmation)
    result = apply_promotion.validate_promotion_request(request)

    assert result["validation_status"] == "rejected"
    assert "owner_confirmation" in " ".join(result["errors"])
    assert result["mutation_performed"] is False
    assert_no_memory_or_applied_audit(tmp_path)


@pytest.mark.parametrize(
    "overrides",
    [
        {"destination_path": "../memory/characters/escape.json"},
        {"evidence_refs": []},
        {"provenance_refs": []},
        {"source_locator_refs": []},
        {"candidate_type": "unsupported_candidate"},
        {"generated_prose": "blocked"},
        {"model_output": "blocked"},
        {"raw_artifact_body": "blocked"},
        {"training_" + "jsonl": "records.jsonl"},
    ],
)
def test_failed_validation_does_not_partially_mutate(
    tmp_path: Path,
    overrides: dict[str, Any],
) -> None:
    result = apply_promotion.validate_promotion_request(valid_promotion_request(**overrides))

    assert result["validation_status"] == "rejected"
    assert result["mutation_performed"] is False
    assert_no_memory_or_applied_audit(tmp_path)


def test_apply_writes_approved_memory_and_audit_together(tmp_path: Path) -> None:
    plan = build_valid_plan()

    result = apply_promotion.apply_promotion_plan(plan, project_dir=tmp_path)

    assert result["promotion_status"] == "applied"
    assert result["mutation_performed"] is True
    memory_files = approved_memory_files(tmp_path)
    audit_files = promotion_audit_files(tmp_path)
    assert len(memory_files) == 1
    assert len(audit_files) == 1

    approved_payload = json.loads(memory_files[0].read_text(encoding="utf-8"))
    audit_record = json.loads(audit_files[0].read_text(encoding="utf-8"))
    assert isinstance(approved_payload, dict)
    assert approved_payload["promotion_record_id"] == audit_record["promotion_record_id"]
    assert approved_payload["approved_payload"]["name"] == "Owner-authored character label"
    assert approved_payload["evidence_refs"] == ["evidence-001"]
    assert approved_payload["provenance_refs"] == ["provenance-001"]
    assert approved_payload["source_locator_refs"] == ["source-locator-001"]
    assert audit_record["promotion_status"] == "applied"
    assert audit_record["evidence_refs"] == ["evidence-001"]
    assert audit_record["provenance_refs"] == ["provenance-001"]
    assert audit_record["source_locator_refs"] == ["source-locator-001"]
    assert audit_record["no_generated_prose_confirmation"] is True
    assert audit_record["no_model_call_confirmation"] is True
    assert audit_record["no_training_artifact_confirmation"] is True


def test_duplicate_apply_is_deterministic_without_conflicting_audit(tmp_path: Path) -> None:
    plan = build_valid_plan()
    first = apply_promotion.apply_promotion_plan(plan, project_dir=tmp_path)
    memory_before = [
        (path.relative_to(tmp_path), path.read_text(encoding="utf-8"))
        for path in approved_memory_files(tmp_path)
    ]

    second = apply_promotion.apply_promotion_plan(copy.deepcopy(plan), project_dir=tmp_path)

    assert second["promotion_status"] in {"applied", "rejected", "blocked"}
    if second["promotion_status"] == "applied":
        assert second["promotion_record_id"] == first["promotion_record_id"]
    memory_after = [
        (path.relative_to(tmp_path), path.read_text(encoding="utf-8"))
        for path in approved_memory_files(tmp_path)
    ]
    assert memory_after == memory_before
    applied_records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in promotion_audit_files(tmp_path)
        if json.loads(path.read_text(encoding="utf-8")).get("promotion_status") == "applied"
    ]
    assert len(applied_records) == 1


@pytest.mark.parametrize("action_type", ALLOWED_REVIEW_COMMANDS)
def test_review_queue_actions_do_not_mutate_approved_memory_or_canon(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    route_client: RouteClient,
    action_type: str,
) -> None:
    monkeypatch.setattr(project_manager, "PROJECTS_DIR", tmp_path)
    project_manager.create_project("Example", projects_dir=tmp_path)
    project_dir = (tmp_path / PROJECT_ID).resolve()
    candidate = valid_review_candidate_record()
    target_candidate = valid_review_candidate_record(
        TARGET_CANDIDATE_ID, "scene_002"
    )
    candidate_persistence.write_candidate_record(project_dir, candidate)
    candidate_persistence.write_candidate_record(project_dir, target_candidate)
    review_queue_storage.write_review_queue_entry(
        valid_review_queue_entry(candidate), project_dir=project_dir
    )
    review_queue_storage.write_review_queue_entry(
        valid_review_queue_entry(target_candidate, TARGET_QUEUE_ENTRY_ID),
        project_dir=project_dir,
    )
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir(mode=0o700)
    monkeypatch.setattr(main.app.state, "validated_runtime_dir", runtime_dir, raising=False)
    approved_memory_before = file_snapshots(approved_memory_files(project_dir))
    promotion_audit_before = file_snapshots(promotion_audit_files(project_dir))

    response = route_client.post(
        f"/api/projects/{PROJECT_ID}/review-queue/{QUEUE_ENTRY_ID}/actions",
        json=review_command_payload(action_type),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_workflow_state"]["is_canon"] is False
    assert payload["review_workflow_state"]["candidate_record_mutation_performed"] is False
    assert payload["review_workflow_state"]["promotion_created"] is False
    assert payload["review_workflow_state"]["apply_promotion_performed"] is False
    assert payload["review_workflow_state"]["memory_canon_mutation_performed"] is False
    assert any("not canon" in warning.lower() for warning in payload["warnings"])
    assert file_snapshots(approved_memory_files(project_dir)) == approved_memory_before
    assert file_snapshots(promotion_audit_files(project_dir)) == promotion_audit_before
    assert_no_memory_or_applied_audit(project_dir)


@pytest.mark.parametrize(
    "body_overrides",
    [
        {"owner_confirmation": False},
        {"destination_type": "storyform_truth_direct_write"},
        {"generated_prose": "blocked"},
        {"model_prompt": "blocked"},
        {"raw_artifact_body": "blocked"},
        {"dataset_" + "manifest": "blocked"},
    ],
)
def test_apply_promotion_route_failures_do_not_create_approved_memory(
    tmp_path: Path,
    body_overrides: dict[str, Any],
) -> None:
    project_dir = tmp_path / PROJECT_ID
    body = {
        "promotion_id": "promotion_001",
        "revision": 1,
        "sealed_contract_hash": "a" * 64,
        "before_state_snapshot_token": "b" * 64,
        "challenge_id": f"challenge_{'c' * 16}_{'d' * 64}",
        "challenge_response": "e" * 64,
        "final_confirmation": {
            "confirmed": True,
            "method": "explicit_final_apply_confirmation",
        },
        "idempotency_key": "11111111-1111-4111-8111-111111111111",
        **body_overrides,
    }

    with pytest.raises(ApplyContractError) as exc_info:
        apply_promotion.final_apply_promotion(
            project_dir=project_dir,
            project_id=PROJECT_ID,
            promotion_id="promotion_001",
            promotion={},
            candidate={},
            body=body,
            registry=None,
        )

    assert exc_info.value.code == "SCHEMA_UNKNOWN_FIELD"
    assert not project_dir.exists()


def test_apply_promotion_route_is_explicit_reference_only_final_apply() -> None:
    route_source = Path(apply_promotion_route.__file__).read_text(encoding="utf-8")
    service_source = Path(apply_promotion.__file__).read_text(encoding="utf-8")

    assert '@router.post("")' in route_source
    assert "async def post_apply_promotion(" in route_source
    assert "apply_promotion.final_apply_promotion(" in route_source
    assert "validate_promotion_request(body)" not in route_source
    assert 'label="final apply request"' in service_source
    for field in (
        "promotion_id",
        "revision",
        "sealed_contract_hash",
        "before_state_snapshot_token",
        "challenge_id",
        "challenge_response",
        "final_confirmation",
        "idempotency_key",
    ):
        assert f'"{field}"' in service_source


def test_frontend_source_keeps_review_actions_separate_from_apply_promotion() -> None:
    root = Path(__file__).resolve().parents[1] / "frontend" / "src"
    api_source = (root / "api.js").read_text(encoding="utf-8")
    review_panel = (root / "components" / "ReviewQueuePanel.jsx").read_text(encoding="utf-8")
    owner_controls = (root / "components" / "OwnerActionReviewControls.jsx").read_text(
        encoding="utf-8"
    )
    confirmation = (root / "components" / "ApplyPromotionConfirmation.jsx").read_text(
        encoding="utf-8"
    )

    assert "submitApplyPromotion" in api_source
    assert "submitReviewQueueAction" in api_source
    assert "client.post(`/projects/${projectId}/apply-promotion`, requestPayload)" in api_source
    assert "client.post(`/projects/${projectId}/review-queue/${queueEntryId}/actions`, payload)" in api_source
    assert "submitApplyPromotion" not in owner_controls
    assert "submitReviewQueueAction" not in confirmation
    assert "OwnerActionReviewControls" in review_panel
    assert "ApplyPromotionConfirmation" in review_panel


def test_frontend_apply_promotion_requires_explicit_final_confirmation() -> None:
    root = Path(__file__).resolve().parents[1] / "frontend" / "src"
    api_source = (root / "api.js").read_text(encoding="utf-8")
    confirmation = (root / "components" / "ApplyPromotionConfirmation.jsx").read_text(
        encoding="utf-8"
    )

    final_request_builder = api_source.split(
        "export function buildReferenceOnlyApplyPromotionRequest", 1
    )[1].split("export async function submitApplyPromotion", 1)[0]
    for field_fragment in (
        "promotion_id:",
        "revision,",
        "sealed_contract_hash:",
        "before_state_snapshot_token:",
        "challenge_id:",
        "challenge_response:",
        "final_confirmation:",
        "idempotency_key:",
    ):
        assert field_fragment in final_request_builder
    assert "confirmed: true" in final_request_builder
    assert "method: 'explicit_final_apply_confirmation'" in final_request_builder
    assert "owner_confirmation" not in final_request_builder

    assert "if (!finalConfirmationChecked)" in confirmation
    assert "Explicit final apply confirmation is incomplete." in confirmation
    assert "checked={finalConfirmationChecked}" in confirmation
    assert "disabled={finalApplyDisabled}" in confirmation
    assert (
        "const finalApplyDisabled = finalApplyBlockers.length > 0 || isApplying || isLoading"
        in confirmation
    )


def test_frontend_source_retains_candidate_only_boundary_copy_and_no_forbidden_controls() -> None:
    root = Path(__file__).resolve().parents[1] / "frontend" / "src"
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            root / "api.js",
            root / "components" / "ReviewQueuePanel.jsx",
            root / "components" / "OwnerActionReviewControls.jsx",
            root / "components" / "ApplyPromotionConfirmation.jsx",
        ]
    )
    normalized_sources = sources.lower()

    for marker in (
        "candidate-only",
        "no-canon",
        "queue presence is not approval",
        "confidence is not truth",
        "candidate persistence is not canon",
        "raw artifacts are support data",
    ):
        assert marker in normalized_sources
    forbidden_markers = [
        "".join(parts)
        for parts in (
            ("generate", "_", "prose"),
            ("rewrite", "_", "prose"),
            ("continue", "_", "scene"),
            ("outline", "_", "chapter"),
            ("call", "_", "model"),
            ("call", "_", "ollama"),
            ("run", "_", "extraction"),
            ("run", "_", "book", "nlp"),
            ("run", "_", "spacy"),
            ("run", "_", "ncp"),
            ("run", "_", "subtxt"),
            ("run", "_", "dramatica", "_", "flow"),
            ("training", "_", "jsonl"),
            ("dataset", "_", "manifest"),
            ("model", "_", "artifact"),
            ("raw", "_", "artifact", "_", "body"),
        )
    ]
    for marker in forbidden_markers:
        assert marker not in sources


def test_backend_source_excludes_runtime_model_training_and_prose_controls() -> None:
    root = Path(__file__).resolve().parents[1]
    sources = "\n".join(
        (root / path).read_text(encoding="utf-8")
        for path in [
            "backend/story_knowledge/apply_promotion.py",
            "backend/routes/apply_promotion.py",
        ]
    )

    assert "owner_confirmation" in sources
    assert "approved_memory" in sources
    assert "promotion_audit" in sources
    assert "apply_promotion_plan" in sources
    assert "build_promotion_plan" in sources
    forbidden_markers = [
        "".join(parts)
        for parts in (
            ("import ", "ollama"),
            ("ollama", "."),
            ("run_", "booknlp"),
            ("run_", "spacy"),
            ("spacy", ".", "load"),
            ("Book", "NLP"),
            ("run_", "ncp"),
            ("run_", "subtxt"),
            ("run_", "dramatica", "_", "flow"),
            ("training", "_", "jsonl"),
            ("dataset", "_", "manifest"),
            ("model", "_", "artifact", "_", "path"),
            ("generate", "_", "prose"),
            ("rewrite", "_", "prose"),
            ("continue", "_", "scene"),
            ("outline", "_", "chapter"),
        )
    ]
    for marker in forbidden_markers:
        assert marker not in sources
