"""Source-level checks for PHASE8-IMPL-017-T005 frontend apply-promotion workflow."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

API_JS = FRONTEND_SRC / "api.js"
REVIEW_QUEUE_PANEL_JSX = FRONTEND_SRC / "components" / "ReviewQueuePanel.jsx"
OWNER_ACTION_CONTROLS_JSX = FRONTEND_SRC / "components" / "OwnerActionReviewControls.jsx"
APPLY_PROMOTION_CONFIRMATION_JSX = (
    FRONTEND_SRC / "components" / "ApplyPromotionConfirmation.jsx"
)

ALLOWED_DESTINATION_TYPES = (
    "approved_character",
    "approved_location",
    "approved_timeline_event",
    "approved_relationship",
    "approved_organization",
    "approved_object",
    "approved_plot_thread",
    "approved_continuity_record",
    "approved_open_question",
    "approved_memory_index",
)

FORBIDDEN_FRONTEND_MARKER_PARTS = (
    ("generate", "_", "prose"),
    ("rewrite", "_", "prose"),
    ("continue", "_", "scene"),
    ("outline", "_", "chapter"),
    ("call", "_", "model"),
    ("call", "_", "ollama"),
    ("run", "_", "extraction"),
    ("run", "_", "booknlp"),
    ("run", "_", "spacy"),
    ("run", "_", "ncp"),
    ("run", "_", "subtxt"),
    ("run", "_", "dramatica", "_", "flow"),
    ("training", "_", "jsonl"),
    ("dataset", "_", "manifest"),
    ("model", "_", "artifact"),
    ("raw", "_", "artifact", "_", "body"),
)


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def combined_frontend_source() -> str:
    return "\n".join(
        read_source(path)
        for path in [
            API_JS,
            REVIEW_QUEUE_PANEL_JSX,
            OWNER_ACTION_CONTROLS_JSX,
            APPLY_PROMOTION_CONFIRMATION_JSX,
        ]
    )


def apply_helper_body() -> str:
    source = read_source(API_JS)
    start = source.index("export async function submitApplyPromotion")
    end = source.index("export async function submitReviewQueueAction")
    return source[start:end]


def test_apply_promotion_api_helper_targets_t004_route() -> None:
    source = read_source(API_JS)
    body = apply_helper_body()

    assert "export async function submitApplyPromotion" in source
    assert "client.post(`/projects/${projectId}/apply-promotion`, requestPayload)" in body
    assert "requireSafeReviewRouteId(projectId, 'project_id')" in body
    assert "requireSafeReviewRouteId(payload.candidate_id, 'candidate_id')" in body
    assert "requireApplyPromotionDestinationType(payload.destination_type)" in body
    assert "owner_confirmation" in body


def test_apply_promotion_confirmation_gate_and_boundary_copy_exist() -> None:
    source = read_source(APPLY_PROMOTION_CONFIRMATION_JSX)

    for marker in (
        "owner_confirmation",
        "owner confirmation",
        "candidate-only",
        "no-canon",
        "queue presence is not approval",
        "confidence is not truth",
        "candidate persistence is not canon",
        "raw artifacts are support data",
        "final owner confirmation",
        "Apply-promotion is the only approved memory/canon mutation path",
    ):
        assert marker in source
    assert "submitDisabled = Boolean(unavailableReason) || !ownerConfirmation || isSubmitting" in source


def test_evidence_provenance_source_locator_fields_are_preserved() -> None:
    source = combined_frontend_source()
    body = apply_helper_body()

    for marker in (
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "sourceLocatorRefs",
        "source_locator",
        "source_document",
    ):
        assert marker in source
        assert marker in body or marker in read_source(APPLY_PROMOTION_CONFIRMATION_JSX)


def test_destination_allowlist_is_frontend_visible() -> None:
    source = combined_frontend_source()

    assert "APPLY_PROMOTION_DESTINATION_TYPES" in source
    for destination_type in ALLOWED_DESTINATION_TYPES:
        assert destination_type in source


def test_fail_closed_apply_promotion_inputs_exist() -> None:
    source = read_source(APPLY_PROMOTION_CONFIRMATION_JSX)
    body = apply_helper_body()

    for marker in (
        "project_id is missing or unsafe",
        "candidate_id is missing",
        "candidate_type is missing",
        "unsupported destination_type",
        "destination_key is required",
        "evidence_refs are required",
        "provenance_refs are required",
        "source_locator_refs are required",
        "owner actor is required",
        "owner_confirmation is required before apply-promotion",
    ):
        assert marker in source or marker in body


def test_review_commands_remain_separate_from_apply_promotion_controls() -> None:
    panel_source = read_source(REVIEW_QUEUE_PANEL_JSX)
    owner_controls_source = read_source(OWNER_ACTION_CONTROLS_JSX)
    apply_source = read_source(APPLY_PROMOTION_CONFIRMATION_JSX)

    assert "OwnerActionReviewControls" in panel_source
    assert "ApplyPromotionConfirmation" in panel_source
    assert "submitReviewQueueAction" in panel_source
    assert "submitApplyPromotion" not in owner_controls_source
    assert "submitReviewQueueAction" not in apply_source
    assert "review workflow command" in owner_controls_source
    assert "Apply-promotion is the only approved memory/canon mutation path" in apply_source


def test_apply_promotion_source_excludes_forbidden_controls() -> None:
    source = combined_frontend_source()
    body = apply_helper_body()

    for marker in ("".join(parts) for parts in FORBIDDEN_FRONTEND_MARKER_PARTS):
        assert marker not in source
        assert marker not in body
