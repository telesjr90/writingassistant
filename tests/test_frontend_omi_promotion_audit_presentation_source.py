"""Semantic source contracts for PHASE8-IMPL-024-T008C correction."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = REPO_ROOT / "frontend" / "src" / "components"
SHELL = COMPONENTS / "OMIShell.jsx"
DASHBOARD = COMPONENTS / "OMIDashboard.jsx"
CANDIDATE_DETAIL = COMPONENTS / "OMICandidateDetail.jsx"
CHECKLIST = COMPONENTS / "OMIPromotionReadinessChecklist.jsx"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def function_body(text: str, start: str, end: str) -> str:
    return text[text.index(start):text.index(end, text.index(start))]


def dashboard_row(dashboard: str, area: str) -> str:
    start = dashboard.index(f"area: '{area}'")
    end = dashboard.find("\n    {\n      area:", start)
    if end == -1:
        end = dashboard.index("\n  ];", start)
    return dashboard[start:end]


def test_dashboard_consumes_canonical_evidence_and_provenance_independently() -> None:
    dashboard = source(DASHBOARD)

    evidence_count = function_body(
        dashboard,
        "const evidenceLinked =",
        "const provenanceLinked =",
    )
    provenance_count = function_body(
        dashboard,
        "const provenanceLinked =",
        "const approvedTotal =",
    )
    assert "'evidence'" in evidence_count
    assert "'provenance'" not in evidence_count
    assert "'provenance'" in provenance_count
    assert "'evidence'" not in provenance_count
    assert "Evidence Linked ${evidenceLinked}" in dashboard
    assert "Provenance Linked ${provenanceLinked}" in dashboard


def test_dashboard_empty_arrays_and_objects_fail_closed() -> None:
    dashboard = source(DASHBOARD)
    has_value = function_body(dashboard, "function hasStoredValue", "function countPresentRefs")

    assert "Array.isArray(value)" in has_value
    assert "value.length > 0" in has_value
    assert "Object.keys(value).length > 0" in has_value
    assert "keys.some((key) => hasStoredValue(item?.[key]))" in dashboard


def test_shell_passes_authoritative_promotions_to_candidate_detail() -> None:
    shell = source(SHELL)

    assert "Array.isArray(omiData?.promotions)" in shell
    assert "omiData.promotions" in shell
    assert "promotion_audit_records" not in function_body(
        shell,
        "const promotions =",
        "const handleBackToDashboard",
    )
    assert "promotions={promotions}" in shell


def test_candidate_detail_associates_promotions_by_exact_candidate_id() -> None:
    detail = source(CANDIDATE_DETAIL)
    matcher = function_body(
        detail,
        "export function getPromotionsForCandidate",
        "function getPromotionTarget",
    )

    assert "asArray(promotions).filter" in matcher
    assert "promotion?.candidate_id === candidateId" in matcher
    assert "source_snapshot" not in matcher
    assert "promotion_record" not in matcher
    assert "getPromotionsForCandidate(promotions, selectedCandidateId)" in detail


def test_candidate_detail_consumes_canonical_values_and_formats_objects() -> None:
    detail = source(CANDIDATE_DETAIL)
    evidence = function_body(detail, "function EvidenceProvenance", "function DuplicateDependencyPanel")

    assert "candidate?.evidence, candidate?.evidence_summary" in evidence
    assert "candidate?.provenance," in evidence
    assert "JSON.stringify(sortStoredValue(value))" in detail
    assert ".join(" not in function_body(detail, "function formatStoredValue", "function isBlankText")
    assert "Object.keys(value).length > 0" in detail


def test_detail_passes_matching_audits_to_readiness_checklist() -> None:
    detail = source(CANDIDATE_DETAIL)

    assert "promotionAuditRecords={promotionAuditRecords}" in detail
    assert "<OMIPromotionReadinessChecklist" in detail
    assert "getPromotionReadinessItems(candidate, promotionAuditRecords)" in detail


def test_checklist_uses_canonical_values_and_explicit_audit_data() -> None:
    checklist = source(CHECKLIST)

    assert "candidate?.evidence, candidate?.evidence_summary" in checklist
    assert "candidate?.provenance," in checklist
    assert "promotionAuditRecords = []" in checklist
    assert "const promotionAudits = asArray(promotionAuditRecords)" in checklist
    assert "promotionAudits.length > 0" in checklist
    assert "candidate?.promotion_audit_record" not in checklist
    assert "candidate?.promotion_record" not in checklist
    assert "Object.keys(value).length > 0" in checklist


def test_multiple_and_unrelated_promotions_remain_exactly_scoped() -> None:
    detail = source(CANDIDATE_DETAIL)

    assert "promotionAuditRecords.map((promotion, index)" in detail
    assert "promotion?.candidate_id === candidateId" in detail
    assert "find(" not in function_body(
        detail,
        "export function getPromotionsForCandidate",
        "function getPromotionTarget",
    )


def test_promotion_audit_presentation_is_identifiable_and_audit_only() -> None:
    detail = source(CANDIDATE_DETAIL)

    for label in ("Promotion ID", "Status", "Target", "Created / confirmed"):
        assert label in detail
    assert "Promotion Audit Record. Not Applied to Memory/Canon." in detail
    assert "promotion?.promotion_id" in detail
    assert "promotion?.status" in detail
    assert "promotion?.target_file" in detail
    assert "promotion?.created_at" in detail


def test_dashboard_handoff_semantics_and_navigation_are_unchanged() -> None:
    dashboard = source(DASHBOARD)
    row = dashboard_row(dashboard, "Promotion Handoff Readiness")

    assert "omiData?.handoff_ready_count, omiData?.promotion_ready_count" in dashboard
    assert "countByStatus(candidates, ['handoff ready', 'ready'])" in dashboard
    assert "count: formatCount(handoffReadyCount, degraded)" in row
    assert "handoffReadyCount === 0 ? 'Not Ready' : 'Ready for Handoff'" in row
    assert "onNavigate('promotion-handoff')" in row


def test_correction_adds_no_runtime_or_persistence_calls() -> None:
    corrected_sources = "\n".join(
        source(path) for path in (SHELL, DASHBOARD, CANDIDATE_DETAIL, CHECKLIST)
    )

    for forbidden in (
        "fetch(",
        "axios",
        "from '../api.js'",
        "createOMICandidate",
        "createOMIPromotion",
        "submitApplyPromotion",
        "saveMemory",
        "saveCanon",
        "updateMemory",
        "updateCanon",
        "callModel",
        "ollama",
        "runStoryCheck",
        "extractOMICandidates",
    ):
        assert forbidden not in corrected_sources
