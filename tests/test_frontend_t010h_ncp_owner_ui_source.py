"""Focused source contracts for the T010H NCP and diagnostics owner UI."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "frontend" / "src"
SHELL = SRC / "components" / "OMIShell.jsx"
DASHBOARD = SRC / "components" / "OMIDashboard.jsx"
HELPERS = SRC / "omiAnalysisRunWorkflow.js"
CSS = SRC / "styles.css"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_shell_and_dashboard_expose_the_ncp_owner_route() -> None:
    shell = source(SHELL)
    dashboard = source(DASHBOARD)

    assert "NcpDiagnosticsOwnerSurface" in shell
    assert "destination === 'ncp-diagnostics'" in shell
    assert "setOmiView('ncp-diagnostics')" in shell
    assert "omiView === 'ncp-diagnostics'" in shell
    assert "onNavigate('ncp-diagnostics')" in dashboard
    assert "NCP Gateway and Diagnostics" in shell


def test_ncp_surface_separates_standard_candidate_import_and_diagnostics_roles() -> None:
    dashboard = source(DASHBOARD)

    for text in (
        "Standard approved-context export",
        "Candidate review bundle",
        "External import review",
        "Scoped diagnostics and traceability",
        "Candidate-only owner review",
        "not a raw-text analyzer or truth selector",
        "source metadata only",
        "omitted fields never express deletion intent",
    ):
        assert text in dashboard


def test_destination_validation_and_confirmation_are_fail_closed() -> None:
    dashboard = source(DASHBOARD)
    helpers = source(HELPERS)

    assert "SAFE_NCP_DESTINATION_PATTERN" in helpers
    assert "destructive_destination_semantics" in helpers
    assert "Filesystem paths are not accepted" in helpers
    assert 'id="omi-ncp-destination-id"' in dashboard
    assert "maxLength={128}" in dashboard
    assert "aria-invalid=" in dashboard
    assert "disabled={!canPrepareHandoff}" in dashboard
    assert "Ready for future execution handoff" in dashboard
    assert "No destination write occurs in this UI" in dashboard


def test_all_required_interface_states_and_retry_are_visible() -> None:
    dashboard = source(DASHBOARD)
    helpers = source(HELPERS)

    for state in (
        "loading",
        "empty",
        "invalid",
        "unavailable",
        "request_failure",
        "success",
    ):
        assert state in helpers
        assert state in dashboard
    assert "Retry interface check" in dashboard
    assert "handleRetry" in dashboard
    assert "Loading the deterministic local interface record" in dashboard


def test_accessibility_and_narrow_containment_contracts_are_present() -> None:
    dashboard = source(DASHBOARD)
    css = source(CSS)

    assert 'aria-labelledby="omi-ncp-owner-heading"' in dashboard
    assert 'aria-live="polite"' in dashboard
    assert 'role="alert"' in dashboard
    assert 'aria-describedby="omi-ncp-destination-help omi-ncp-destination-feedback"' in dashboard
    assert ".omi-ncp-package-grid" in css
    assert ".omi-ncp-metadata" in css
    assert ".omi-ncp-diagnostic-summary" in css
    assert "grid-template-columns: 1fr" in css
    assert "overflow-wrap: anywhere" in css


def test_destructive_and_mutating_behaviors_remain_disabled_or_absent() -> None:
    dashboard = source(DASHBOARD)

    for disabled_action in (
        "Overwrite target",
        "Delete artifact",
        "Purge retained data",
        "Import external package",
        "Prepare candidate bundle",
    ):
        assert disabled_action in dashboard
    for forbidden_call in (
        "createOMICandidate",
        "createOMIPromotion",
        "submitApplyPromotion",
        "saveBible",
        "saveStoryform",
        "runStoryCheck",
    ):
        assert forbidden_call not in dashboard
    assert "cannot write an export, persist an import" in dashboard
    assert "No export, write, import, or canon mutation occurred" in dashboard
