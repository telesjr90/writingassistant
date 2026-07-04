import OMIBoundaryBanner from './OMIBoundaryBanner.jsx';
import OMICandidateCanonStatusStrip from './OMICandidateCanonStatusStrip.jsx';
import OMIDashboard, { getOMIDashboardSummary } from './OMIDashboard.jsx';

export default function OMIShell({
  activeProjectId,
  projectTitle,
  omiData,
  isLoading = false,
  error = '',
}) {
  const summary = getOMIDashboardSummary(omiData, { isLoading, error });

  return (
    <section className="omi-shell" aria-label="Project-local OMI workspace">
      <header className="omi-shell-header">
        <div>
          <p
            className="eyebrow"
            data-testid="omi-active-project-label"
          >
            Active project: {projectTitle || activeProjectId || 'Project'} / project-local OMI
          </p>
          <h1>OMI Dashboard</h1>
          <p
            className="muted-copy"
            data-testid="omi-source-scope-label"
          >
            Project-local review metadata only; candidates are not canon.
          </p>
        </div>
      </header>

      <OMIBoundaryBanner />
      <OMICandidateCanonStatusStrip
        ownerInputCount={summary.ownerInputCount}
        candidateCount={summary.candidateCount}
        blockedCount={summary.blockedCount}
        handoffReadyCount={summary.handoffReadyCount}
        promotionAuditCount={summary.promotionAuditCount}
        approvedMemoryCount={summary.approvedTotal}
        isDegraded={summary.degraded}
      />
      <OMIDashboard
        omiData={omiData}
        isLoading={isLoading}
        error={error}
      />
    </section>
  );
}
