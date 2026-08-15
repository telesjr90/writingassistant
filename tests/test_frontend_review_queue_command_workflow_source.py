from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "frontend" / "src" / "api.js"
CONTROLS_PATH = ROOT / "frontend" / "src" / "components" / "OwnerActionReviewControls.jsx"
PANEL_PATH = ROOT / "frontend" / "src" / "components" / "ReviewQueuePanel.jsx"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _submit_api_source() -> str:
    return _source(API_PATH).split("export async function submitReviewQueueAction", 1)[1]


def test_controls_are_the_only_uuid_generation_owner() -> None:
    sources = {
        "api": _source(API_PATH),
        "controls": _source(CONTROLS_PATH),
        "panel": _source(PANEL_PATH),
    }

    assert sources["controls"].count("crypto.randomUUID()") == 1
    assert "crypto.randomUUID()" not in sources["api"]
    assert "crypto.randomUUID()" not in sources["panel"]


def test_one_logical_command_reuses_key_for_network_and_manual_retry() -> None:
    source = _source(CONTROLS_PATH)

    assert "pendingLogicalCommand" in source
    assert "semanticCommandMatches(semanticCommand, pendingLogicalCommand)" in source
    assert "? pendingLogicalCommand" in source
    assert "setPendingLogicalCommand(logicalCommand)" in source
    assert "Retry this same logical command" in source


def test_semantic_edit_cancel_and_new_command_rotate_key() -> None:
    source = _source(CONTROLS_PATH)

    semantic_edit = source.split("function handleSemanticEdit", 1)[1].split(
        "function currentSemanticCommand", 1
    )[0]
    cancellation = source.split("function handleCancelPendingCommand", 1)[1].split(
        "async function handleAuthoritativeRefresh", 1
    )[0]
    assert "clearPendingLogicalCommand()" in semantic_edit
    assert "setOwnerConfirmed(false)" in semantic_edit
    assert "clearPendingLogicalCommand()" in cancellation
    assert "next submission will use a new recovery key" in cancellation
    assert "{ ...semanticCommand, idempotencyKey: crypto.randomUUID() }" in source


def test_api_requires_and_forwards_supplied_key_unchanged() -> None:
    source = _submit_api_source()

    assert "idempotencyKey" in source
    assert "idempotencyKey === undefined || idempotencyKey === null" in source
    assert "idempotency_key: idempotencyKey" in source


def test_api_never_generates_normalizes_or_rotates_idempotency_key() -> None:
    source = _submit_api_source()

    assert "randomUUID" not in source
    assert "UUID_V4_PATTERN" not in source
    assert ".trim(" not in source
    assert ".toLowerCase(" not in source
    assert ".toUpperCase(" not in source


def test_payload_uses_review_version_and_closed_command_fields() -> None:
    controls = _source(CONTROLS_PATH)
    api = _submit_api_source()

    assert "queueEntry?.review_version" in controls
    assert "queueEntry?.version" not in controls
    for field in (
        "action_type",
        "queue_entry_id",
        "candidate_id",
        "actor: 'owner-reviewed'",
        "owner_confirmed",
        "preserve_candidate_linkage",
        "preserve_evidence_provenance",
        "idempotency_key",
        "expected_current_review_status",
        "expected_current_version",
        "target_review_status",
        "duplicate_candidate_ids",
        "superseded_by_candidate_id",
        "rejected_output_reason",
        "insufficient_evidence_reason",
        "quarantine_note",
    ):
        assert field in api
    assert "metadata:" not in api


def test_owner_authored_text_is_forwarded_without_transformation() -> None:
    source = _submit_api_source()

    assert "['owner_note', ownerNote]" in source
    assert "['rationale', rationale]" in source
    assert "['quarantine_note', quarantineNote]" in source
    assert "if (value !== undefined)" in source
    assert "compactStringField" not in source
    assert ".trim(" not in source


def test_409_requires_authoritative_refresh_before_new_command() -> None:
    source = _source(CONTROLS_PATH)

    assert "status === 409" in source
    assert "Authoritative queue refresh is required before creating a new logical command." in source
    assert "await onRefreshQueue()" in source
    assert "Refresh authoritative queue" in source
    assert "clearPendingLogicalCommand()" in source.split(
        "async function handleAuthoritativeRefresh", 1
    )[1]


def test_423_and_500_keep_same_command_available_for_retry() -> None:
    source = _source(CONTROLS_PATH)
    catch_block = source.split("} catch (submitError) {", 1)[1].split("} finally {", 1)[0]

    assert "status === 423" in catch_block
    assert "status === 500" in catch_block
    assert "manualRecoveryRequired" in catch_block
    assert "recovery key has been retained" in catch_block
    assert "clearPendingLogicalCommand()" not in catch_block


def test_success_triggers_authoritative_queue_refresh() -> None:
    source = _source(PANEL_PATH)
    submit = source.split("async function handleSubmitAction", 1)[1].split("return (", 1)[0]

    post_position = submit.index("await submitReviewQueueAction")
    refresh_position = submit.index("await refreshReviewQueue()")
    success_position = submit.index("setStatus('Owner review command accepted")
    assert post_position < refresh_position < success_position
    assert "onRefreshQueue={refreshReviewQueue}" in source


def test_panel_displays_persisted_version_note_and_completion_fields() -> None:
    source = _source(PANEL_PATH)

    for field in (
        "selectedEntry.review_version",
        "selectedEntry.owner_note",
        "selectedEntry.owner_review_completed",
        "selectedEntry.owner_reviewed_at",
    ):
        assert field in source
    assert "Review workflow completion" in source
    assert "Review workflow completed at" in source


def test_frontend_exposes_no_promotion_canon_prose_model_or_training_mutation() -> None:
    api = _submit_api_source()
    controls = _source(CONTROLS_PATH)

    for forbidden_field in (
        "apply_promotion",
        "memory_canon_mutation",
        "project_truth_mutation",
        "generated_prose",
        "model_call",
        "training_artifact",
    ):
        assert forbidden_field not in api
    assert "REVIEW_ACTION_TYPES.map" in controls
    assert "They do not change canon" in controls
    assert "owner-authored prose" in controls
