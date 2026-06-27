"""Source-level checks for PHASE8-IMPL-016-T005 frontend owner review workflow."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

API_JS = FRONTEND_SRC / "api.js"
APP_JSX = FRONTEND_SRC / "App.jsx"
REVIEW_QUEUE_PANEL_JSX = FRONTEND_SRC / "components" / "ReviewQueuePanel.jsx"
OWNER_ACTION_CONTROLS_JSX = FRONTEND_SRC / "components" / "OwnerActionReviewControls.jsx"

ALLOWED_COMMANDS = (
    "mark_reviewed",
    "request_more_evidence",
    "defer",
    "reject",
    "quarantine",
    "update_owner_note",
    "set_review_status",
)

FORBIDDEN_MARKER_PARTS = (
    ("apply", "-", "promotion"),
    ("Apply", "Promotion"),
    ("promote", "_", "candidate"),
    ("write", "_", "memory"),
    ("write", "_", "canon"),
    ("canon", "_", "path"),
    ("memory", "_", "path"),
    ("raw", "_", "artifact", "_", "path"),
    ("model", "_", "prompt"),
    ("generated", "_", "text"),
    ("prose", "_", "text"),
    ("scene", "_", "prose"),
    ("jsonl", "_", "output", "_", "path"),
    ("dataset", "_", "manifest", "_", "path"),
    ("model", "_", "artifact", "_", "path"),
    ("generate", "_", "prose"),
    ("rewrite", "_", "prose"),
    ("continue", "_", "scene"),
    ("outline", "_", "chapter"),
    ("create", "_", "training", "_", "jsonl"),
    ("call", "_", "model"),
    ("ol", "lama"),
    ("Book", "NLP"),
    ("spacy", ".", "load"),
)


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_frontend_source() -> str:
    return "\n".join(
        read_source(path)
        for path in [
            API_JS,
            APP_JSX,
            REVIEW_QUEUE_PANEL_JSX,
            OWNER_ACTION_CONTROLS_JSX,
        ]
    )


def api_helper_body() -> str:
    source = read_source(API_JS)
    start = source.index("export async function submitReviewQueueAction")
    return source[start:]


def test_api_helper_posts_to_t004_review_action_route() -> None:
    source = read_source(API_JS)

    assert "export async function submitReviewQueueAction" in source
    assert "/api/projects/" not in source
    assert "/review-queue/" in source
    assert "/actions" in source
    assert "client.post(`/projects/${projectId}/review-queue/${queueEntryId}/actions`, payload)" in source
    assert "requireSafeReviewRouteId(projectId, 'project_id')" in source
    assert "requireSafeReviewRouteId(queueEntryId, 'queue_entry_id')" in source
    assert "requireReviewActionType(actionType)" in source


def test_allowed_review_command_controls_exist() -> None:
    source = combined_frontend_source()

    for command in ALLOWED_COMMANDS:
        assert command in source
    assert "OwnerActionReviewControls" in source
    assert "Send owner review command" in source
    assert "explicitly confirm this bounded review workflow command" in source


def test_candidate_only_no_canon_warnings_exist() -> None:
    source = combined_frontend_source()

    assert "candidate-only" in source
    assert "no-canon" in source
    assert "queue presence, confidence" in source
    assert "review status are not canon" in source
    assert "not project truth" in source
    assert "not canon" in source


def test_evidence_provenance_source_locator_are_displayed_and_preserved() -> None:
    source = combined_frontend_source()

    assert "evidence/provenance/source" in source
    assert "source locator" in source
    assert "source_locator" in source
    assert "provenance_summary" in source
    assert "evidence_summary" in source
    assert "preserve_evidence_provenance" in source
    assert "preserve_candidate_linkage" in source


def test_command_payload_excludes_forbidden_fields() -> None:
    source = combined_frontend_source()
    body = api_helper_body()

    for marker in ("".join(parts) for parts in FORBIDDEN_MARKER_PARTS):
        assert marker not in source
        assert marker not in body
    assert "payload = {" in body
    assert "action_type: actionType" in body
    assert "queue_entry_id: queueEntryId" in body
    assert "owner_confirmed: true" in body


def test_read_only_queue_display_is_separate_from_post_controls() -> None:
    panel_source = read_source(REVIEW_QUEUE_PANEL_JSX)
    controls_source = read_source(OWNER_ACTION_CONTROLS_JSX)

    assert "fetchReviewQueueEntries(projectId)" in panel_source
    assert 'aria-label="Read-only candidate details"' in panel_source
    assert "submitReviewQueueAction" in panel_source
    assert "OwnerActionReviewControls" in panel_source
    assert "submitReviewQueueAction" not in controls_source
    assert "onSubmitAction" in controls_source
    assert "controlsUnavailableReason" in controls_source
