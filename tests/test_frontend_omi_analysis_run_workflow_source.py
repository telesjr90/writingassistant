"""Focused source contracts for PHASE8-IMPL-025-T011H owner-facing live runs."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "frontend" / "src"
WORKFLOW = SRC / "components" / "OMIAnalysisRunWorkflow.jsx"
SHELL = SRC / "components" / "OMIShell.jsx"
DASHBOARD = SRC / "components" / "OMIDashboard.jsx"
API = SRC / "api.js"
CSS = SRC / "styles.css"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_shell_and_dashboard_expose_a_local_live_analysis_route() -> None:
    shell = source(SHELL)
    dashboard = source(DASHBOARD)

    assert "import OMIAnalysisRunWorkflow" in shell
    assert "destination === 'live-analysis'" in shell
    assert "setOmiView('live-analysis')" in shell
    assert "omiView === 'live-analysis'" in shell
    assert "<OMIAnalysisRunWorkflow" in shell
    assert "onNavigate('live-analysis')" in dashboard
    assert "ownerInputCount > 0" in dashboard


def test_api_uses_only_existing_analysis_control_plane_routes() -> None:
    api = source(API)

    for route in (
        "/omi/analysis/tools",
        "/omi/analysis/runs`",
        "/omi/analysis/runs/${runId}`",
        "/omi/analysis/runs/${runId}/result`",
    ):
        assert route in api
    assert "allow_deterministic_fallback: false" in api
    assert "source_idea_id" in api
    assert "idempotency_key" in api
    assert "/cancel" not in api[api.index("export class OmiAnalysisRunError"):api.index("export async function createOMIIdea")]


def test_workflow_requires_explicit_source_tools_and_owner_confirmation() -> None:
    workflow = source(WORKFLOW)

    assert 'id="omi-analysis-source"' in workflow
    assert "selectedTools.length > 0" in workflow
    assert "ownerConfirmed" in workflow
    assert "type=\"submit\" disabled={!canSubmit}" in workflow
    assert "No run starts until this button is activated" in workflow
    assert "isAnalysisToolRunnable(tool)" in workflow
    assert "Only backend-enabled tools can be selected" in workflow


def test_progress_recovery_and_failure_states_are_truthful() -> None:
    workflow = source(WORKFLOW)

    assert "Submission in progress" in workflow
    assert "No progress percentage is fabricated" in workflow
    assert "Retry same request safely" in workflow
    assert "Reinspect durable run" in workflow
    assert "Cancellation and timeout actions are unavailable" in workflow
    assert "Readiness check failed" in workflow
    assert "Inspection failed" in workflow
    assert "Submission failed" in workflow


def test_result_manifest_ledger_provenance_and_handoff_are_visible() -> None:
    workflow = source(WORKFLOW)

    for visible_section in (
        "Normalized findings",
        "Manifest reference",
        "Raw artifact reference",
        "Evidence ledger",
        "Provenance, manifest, and evidence audit",
        "Candidate-review handoff",
    ):
        assert visible_section in workflow
    assert "raw bytes and hidden filesystem paths are not exposed" in workflow
    assert "Open existing candidate review" in workflow
    assert "Open grouped owner review" in workflow


def test_apply_and_product_safety_boundaries_remain_disabled() -> None:
    workflow = source(WORKFLOW)

    assert "Apply-promotion remains separate" in workflow
    assert "Apply to Memory/Canon" in workflow
    assert "Disabled here" in workflow
    assert "does not persist candidates" in workflow
    assert "never approves candidates, creates promotions, applies promotion" in workflow
    for forbidden in (
        "createOMIPromotion",
        "submitApplyPromotion",
        "saveBible",
        "saveStoryform",
        "createOMICandidate",
        "runStoryCheck",
    ):
        assert forbidden not in workflow


def test_workflow_has_accessible_labels_statuses_and_responsive_containment() -> None:
    workflow = source(WORKFLOW)
    css = source(CSS)

    assert "aria-labelledby" in workflow
    assert "aria-describedby" in workflow
    assert "aria-live=\"polite\"" in workflow
    assert "role=\"alert\"" in workflow
    assert "<fieldset" in workflow and "<legend>" in workflow
    assert ".omi-analysis-tool-list" in css
    assert ".omi-analysis-inspection-grid" in css
    assert "grid-template-columns: 1fr" in css
    assert ".omi-analysis-confirmation" in css
