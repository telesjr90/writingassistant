"""Focused source contracts for T008D preparation and approval UI."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
API_JS = FRONTEND_SRC / "api.js"
SHELL = FRONTEND_SRC / "components" / "OMIShell.jsx"
ROUTE = FRONTEND_SRC / "components" / "OMIApplyPromotionRoute.jsx"
CONFIRMATION = FRONTEND_SRC / "components" / "ApplyPromotionConfirmation.jsx"
BLOCKERS = FRONTEND_SRC / "components" / "OMIApplyPromotionBlockers.jsx"

ORDINARY_DESTINATIONS = (
    "approved_character",
    "approved_location",
    "approved_timeline_event",
    "approved_relationship",
    "approved_organization",
    "approved_object",
    "approved_plot_thread",
    "approved_continuity_record",
    "approved_open_question",
)

FORBIDDEN_FRONTEND_MARKER_PARTS = (
    ("generate", "_", "prose"),
    ("rewrite", "_", "prose"),
    ("continue", "_", "scene"),
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
)


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def function_body(text: str, start: str, end: str) -> str:
    return text[text.index(start):text.index(end, text.index(start))]


def test_lifecycle_api_helpers_target_accepted_contract_routes() -> None:
    api = source(API_JS)
    read = function_body(api, "export async function getApplyPromotionContract", "export async function prepareApplyPromotionContract")
    prepare = function_body(api, "export async function prepareApplyPromotionContract", "export async function approveApplyPromotionContract")
    approve = function_body(api, "export async function approveApplyPromotionContract", "export async function submitReviewQueueAction")

    assert "apply-contract`, config" in read
    assert "apply-contract/revisions`" in prepare
    assert "apply-contract/revisions/${revision}/approval`" in approve
    for body in (read, prepare, approve):
        assert "requireSafeReviewRouteId(projectId, 'project_id')" in body
        assert "requireSafeReviewRouteId(promotionId, 'promotion_id')" in body
    assert "apply-contract/final-challenge" in api
    assert "export async function submitApplyPromotion" in api
    assert "client.post(`/projects/${projectId}/apply-promotion`, requestPayload)" in api


def test_exact_promotion_selection_has_no_first_item_fallback() -> None:
    shell = source(SHELL)
    route = source(ROUTE)

    assert "const [selectedPromotionId, setSelectedPromotionId] = useState('')" in shell
    assert "selectedPromotionId={selectedPromotionId}" in shell
    assert "onSelectPromotion={handleSelectPromotion}" in shell
    assert "findExactPromotion(storedPromotions, selectedPromotionId)" in route
    assert "findExactPromotionCandidate(asArray(candidates), promotion)" in route
    assert "Select one exact promotion record" in route
    assert "never substitutes the first promotion or candidate" in route
    assert "promotions[0]" not in route
    assert "candidates[0]" not in route


def test_ordinary_destination_allowlist_excludes_memory_index() -> None:
    api = source(API_JS)
    confirmation = source(CONFIRMATION)
    allowlist = api[
        api.index("export const APPLY_PROMOTION_DESTINATION_TYPES"):
        api.index("export function isSafeReviewRouteId")
    ]

    for destination in ORDINARY_DESTINATIONS:
        assert destination in allowlist
        assert destination in confirmation
    assert "approved_memory_index" not in allowlist
    assert "Ordinary preparation never offers approved_memory_index" in confirmation


def test_server_authoritative_owner_is_read_only_and_not_claimed_as_identity_proof() -> None:
    confirmation = source(CONFIRMATION)

    for marker in (
        "contractView?.authoritative_owner",
        "Authoritative owner",
        "project_local_owner_config",
        "Read-only server authority",
        "does not establish who is operating this local client",
        "this interface cannot edit owner configuration",
    ):
        assert marker in confirmation
    for prohibited_copy in ("authenticated", "signed in", "verified human", "identity proof", "credential"):
        assert prohibited_copy not in confirmation.casefold()


def test_explicit_operation_typed_payload_and_decisions_are_closed() -> None:
    confirmation = source(CONFIRMATION)

    for marker in (
        "Choose create or update",
        "payload_type: destinationType",
        "[destinationConfig.primaryField]",
        "endpoint_refs",
        "evidence_ref_ids: selectedEvidenceIds",
        "provenance_ref_ids: selectedProvenanceIds",
        "duplicate_resolution",
        "dependency_resolution",
        "reviewed_candidate_ids",
        "reviewed_approved_records: []",
        "dependencies: dependencies.map(normalizeDependencyInputEntry)",
        "...buildDependencyResolutionInput({",
        "Draft supersession",
        "Sealed-contract supersession",
    ):
        assert marker in confirmation
    assert "owner_actor_id" not in confirmation
    assert "destination_path:" not in function_body(
        confirmation, "function buildPreparationRequest", "async function handlePrepare"
    )


def test_dependency_entries_are_closed_bounded_accessible_and_owner_controlled() -> None:
    confirmation = source(CONFIRMATION)

    for marker in (
        "createEmptyDependencyInputEntry",
        "getDependencyResolutionBlockers",
        "normalizeDependencyInputEntry",
        "appendDependencyInputEntry",
        "removeDependencyInputEntry",
        "updateDependencyInputEntry",
        "const [dependencyEntries, setDependencyEntries] = useState([])",
        "Dependency entries (maximum 256)",
        "Add dependency entry",
        "Remove dependency",
        "Dependency ID",
        "Dependency kind",
        "Required classification",
        "Dependency status",
        "Target classification",
        "Target destination type",
        "Target destination key",
        "Target record version",
        "Target content hash",
        "Dependency evidence references",
        "Dependency provenance references",
        "Dependency rationale",
        "Optional applicability rule",
        "aria-describedby={entryBlockerId}",
        "role=\"alert\"",
    ):
        assert marker in confirmation

    request = function_body(
        confirmation, "function buildPreparationRequest", "async function handlePrepare"
    )
    assert "...buildDependencyResolutionInput({" in request
    assert "dependencies: dependencyEntries" in request
    assert "dependencies: dependencies.map(normalizeDependencyInputEntry)" in confirmation
    assert "dependencies: []" not in request
    for server_field in ("resolved_by", "resolved_at", "resolution_scope_hash"):
        assert server_field not in request


def test_dependency_owner_values_and_exact_failed_request_are_retained() -> None:
    confirmation = source(CONFIRMATION)

    assert "value={entry.dependency_id}" in confirmation
    assert "value={entry.kind}" in confirmation
    assert "value={entry.rationale}" in confirmation
    assert "value={entry.applicability_rule}" in confirmation
    assert "const request = recoveryRequest ?? buildPreparationRequest()" in confirmation
    assert "setRecoveryRequest(request)" in confirmation
    assert "setDependencyEntries([])" not in confirmation


def test_dependency_copy_does_not_claim_authentication_or_canon_promotion() -> None:
    confirmation = source(CONFIRMATION).casefold()

    for prohibited in (
        "dependency decision authenticates",
        "dependency is authentication",
        "dependency proves identity",
        "dependency becomes canon",
        "dependency promotes to canon",
    ):
        assert prohibited not in confirmation


def test_preparation_uuid_recovery_and_publication_states_are_retained() -> None:
    confirmation = source(CONFIRMATION)

    for marker in (
        "const [preparationIdempotencyKey] = useState(createIdempotencyKey)",
        "const request = recoveryRequest ?? buildPreparationRequest()",
        "setRecoveryRequest(request)",
        "Retry exact saved preparation publication",
        "Preparation publication incomplete",
        "retry the same preparation request and retained UUID",
        "Preparation publication recovered from immutable saved bytes",
        "No current candidate, before state, or owner value was used to reconstruct",
        "preparation_artifact_published",
        "preparation_revision_published",
        "preparation_events_incomplete",
    ):
        assert marker.casefold() in confirmation.casefold()


def test_approval_requires_backend_active_draft_and_displays_exact_seal() -> None:
    confirmation = source(CONFIRMATION)

    for marker in (
        "lineageState !== 'draft_active'",
        "approval_method: 'explicit_apply_contract_approval'",
        "expected_latest_draft_scope_hash: selectedRevision.draft_scope_hash",
        "before_state_snapshot_token: selectedRevision.before_state.snapshot_token",
        "Approve and seal revision",
        "Sealed contract",
        "sealed_contract_hash",
        "Memory/Canon remains unchanged",
    ):
        assert marker in confirmation
    assert "Generate final challenge" in confirmation
    assert "Observational GET never issues one" in confirmation


def test_blockers_are_visible_accessible_and_non_color_only() -> None:
    confirmation = source(CONFIRMATION)
    blockers = source(BLOCKERS)

    assert "aria-live=\"polite\"" in blockers
    assert "Action blocked" in blockers
    assert "Preparation:" in confirmation
    assert "Approval:" in confirmation
    assert "aria-describedby={blockerReasonId}" in confirmation
    assert 'role="alert"' in confirmation
    assert 'role="status"' in confirmation


def test_phase8_challenge_and_reference_only_final_apply_are_explicit() -> None:
    combined = "\n".join(source(path) for path in (API_JS, SHELL, ROUTE, CONFIRMATION))

    for marker in (
        "issueApplyPromotionFinalChallenge",
        "computeFinalChallengeResponse",
        "Generate final challenge",
        "Generate fresh challenge",
        "Explicitly replace active challenge",
        "120-second, single-use challenge",
        "It is not authentication",
        "submitApplyPromotion",
        "buildReferenceOnlyApplyPromotionRequest",
        "explicit_final_apply_confirmation",
    ):
        assert marker in combined
    final_builder = function_body(
        source(API_JS),
        "export function buildReferenceOnlyApplyPromotionRequest",
        "export async function submitApplyPromotion",
    )
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
        assert field in final_builder
    for prohibited_authority in (
        "owner_actor",
        "destination_path",
        "approved_payload",
        "evidence_refs",
        "provenance_refs",
        "source_locator_refs",
        "before_state_content",
    ):
        assert prohibited_authority not in final_builder
    for marker in ("".join(parts) for parts in FORBIDDEN_FRONTEND_MARKER_PARTS):
        assert marker not in combined


def test_challenge_expiry_restart_replacement_and_recovery_states_are_visible() -> None:
    api = source(API_JS)
    confirmation = source(CONFIRMATION)

    for marker in (
        "FINAL_CHALLENGE_EXPIRED: 'expired'",
        "FINAL_CHALLENGE_REPLACED: 'replaced'",
        "FINAL_CHALLENGE_REQUIRED_AFTER_RESTART: 'restart_invalidated'",
        "RECOVERY_REQUIRED",
        "APPLY_FAILED_BEFORE_COMMIT",
        "getFinalChallengeTemporalState",
    ):
        assert marker in api
    for marker in (
        "seconds remaining",
        "Final challenge expired after its 120-second lifetime",
        "invalidated by a backend restart",
        "Retry exact apply recovery",
        "Final apply verified not committed",
        "Completed replay or committed recovery",
        "approved_record_hash",
        "approved_record_size",
        "await refreshContract(response.revision)",
    ):
        assert marker in confirmation
