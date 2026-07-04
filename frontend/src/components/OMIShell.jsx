import { useMemo, useState } from 'react';
import OMIBoundaryBanner from './OMIBoundaryBanner.jsx';
import OMICandidateCanonStatusStrip from './OMICandidateCanonStatusStrip.jsx';
import OMICandidateDetail from './OMICandidateDetail.jsx';
import OMIDashboard, { getOMIDashboardSummary } from './OMIDashboard.jsx';

function getCandidateId(candidate) {
  return candidate?.candidate_id ?? candidate?.candidateId ?? candidate?.id ?? '';
}

export default function OMIShell({
  activeProjectId,
  projectTitle,
  omiData,
  isLoading = false,
  error = '',
}) {
  const summary = getOMIDashboardSummary(omiData, { isLoading, error });
  const [omiView, setOmiView] = useState('dashboard');
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const candidates = useMemo(() => (
    Array.isArray(omiData?.candidates) ? omiData.candidates : []
  ), [omiData]);

  function handleNavigate(destination) {
    if (destination === 'candidates') {
      const firstCandidateId = getCandidateId(candidates[0]);
      setSelectedCandidateId(firstCandidateId);
      setOmiView('candidate-detail');
      return;
    }

    setOmiView('dashboard');
  }

  function handleBackToDashboard() {
    setOmiView('dashboard');
  }

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
          <h1>{omiView === 'candidate-detail' ? 'OMI Candidate Detail' : 'OMI Dashboard'}</h1>
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
      {omiView === 'candidate-detail' ? (
        <OMICandidateDetail
          activeProjectId={activeProjectId}
          projectTitle={projectTitle}
          candidates={candidates}
          selectedCandidateId={selectedCandidateId}
          isLoading={isLoading}
          error={error}
          onBackToDashboard={handleBackToDashboard}
        />
      ) : (
        <OMIDashboard
          omiData={omiData}
          isLoading={isLoading}
          error={error}
          onNavigate={handleNavigate}
        />
      )}
    </section>
  );
}
