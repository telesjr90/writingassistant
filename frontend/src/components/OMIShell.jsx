import { useRef, useMemo, useState } from 'react';
import OMIBoundaryBanner from './OMIBoundaryBanner.jsx';
import OMICandidateCanonStatusStrip from './OMICandidateCanonStatusStrip.jsx';
import OMICandidateDetail from './OMICandidateDetail.jsx';
import OMIApplyPromotionRoute from './OMIApplyPromotionRoute.jsx';
import OMIDashboard, { getOMIDashboardSummary } from './OMIDashboard.jsx';
import OMIEvidenceDrawer from './OMIEvidenceDrawer.jsx';
import OMIGroupedReview from './OMIGroupedReview.jsx';

function getCandidateId(candidate) {
  return candidate?.candidate_id ?? candidate?.candidateId ?? candidate?.id ?? '';
}

function getShellTitle(omiView) {
  if (omiView === 'candidate-detail') {
    return 'OMI Candidate Detail';
  }
  if (omiView === 'apply-promotion') {
    return 'Apply-Promotion Confirmation';
  }
  if (omiView === 'grouped-review') {
    return 'Grouped Owner Review';
  }
  return 'OMI Dashboard';
}

export default function OMIShell({
  activeProjectId,
  projectTitle,
  omiData,
  isLoading = false,
  isUpdating = false,
  status = '',
  error = '',
  onUpdateCandidateDecision = async () => null,
}) {
  const summary = getOMIDashboardSummary(omiData, { isLoading, error });
  const [omiView, setOmiView] = useState('dashboard');
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const evidenceOpenerRef = useRef(null);
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

    if (destination === 'promotion-handoff') {
      const firstCandidateId = selectedCandidateId || getCandidateId(candidates[0]);
      setSelectedCandidateId(firstCandidateId);
      setOmiView('apply-promotion');
      return;
    }

    if (destination === 'grouped-review') {
      setOmiView('grouped-review');
      return;
    }

    setOmiView('dashboard');
  }

  function handleBackToDashboard() {
    setOmiView('dashboard');
  }

  function handleOpenEvidence(evidence, openerElement) {
    evidenceOpenerRef.current = openerElement ?? null;
    setSelectedEvidence(evidence);
  }

  function handleCloseEvidence() {
    setSelectedEvidence(null);
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
          <h1>{getShellTitle(omiView)}</h1>
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
      {omiView === 'apply-promotion' ? (
        <OMIApplyPromotionRoute
          activeProjectId={activeProjectId}
          candidates={candidates}
          selectedCandidateId={selectedCandidateId}
          approvedMemoryCanonSnapshot={summary.approvedSnapshot}
          onCancel={handleBackToDashboard}
        />
      ) : omiView === 'candidate-detail' ? (
        <OMICandidateDetail
          activeProjectId={activeProjectId}
          projectTitle={projectTitle}
          candidates={candidates}
          selectedCandidateId={selectedCandidateId}
          isLoading={isLoading}
          error={error}
          onBackToDashboard={handleBackToDashboard}
          onOpenApplyPromotion={() => handleNavigate('promotion-handoff')}
          onOpenEvidence={handleOpenEvidence}
        />
      ) : omiView === 'grouped-review' ? (
        <OMIGroupedReview
          omiData={omiData}
          isLoading={isLoading}
          isUpdating={isUpdating}
          status={status}
          error={error}
          onUpdateCandidateDecision={onUpdateCandidateDecision}
          onOpenEvidence={handleOpenEvidence}
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
      <OMIEvidenceDrawer
        evidence={selectedEvidence}
        isOpen={Boolean(selectedEvidence)}
        openerRef={evidenceOpenerRef}
        onClose={handleCloseEvidence}
      />
    </section>
  );
}
