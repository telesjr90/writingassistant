import { useCallback, useEffect, useRef, useMemo, useState } from 'react';
import OMIBoundaryBanner from './OMIBoundaryBanner.jsx';
import OMICandidateCanonStatusStrip from './OMICandidateCanonStatusStrip.jsx';
import OMICandidateDetail from './OMICandidateDetail.jsx';
import OMIApplyPromotionRoute from './OMIApplyPromotionRoute.jsx';
import OMIAnalysisRunWorkflow from './OMIAnalysisRunWorkflow.jsx';
import OMIDashboard, { getOMIDashboardSummary } from './OMIDashboard.jsx';
import OMIEvidenceDrawer from './OMIEvidenceDrawer.jsx';
import OMIGroupedReview from './OMIGroupedReview.jsx';

function getCandidateId(candidate) {
  return candidate?.candidate_id ?? candidate?.candidateId ?? candidate?.id ?? '';
}

function getPromotionId(promotion) {
  return promotion?.promotion_id ?? '';
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
  if (omiView === 'live-analysis') {
    return 'Owner-Facing Live Analysis';
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
  dashboardResetRequest = 0,
  onUpdateCandidateDecision = async () => null,
  onOpenMemoryCanon = () => {},
}) {
  const summary = getOMIDashboardSummary(omiData, { isLoading, error });
  const [omiView, setOmiView] = useState('dashboard');
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const [selectedPromotionId, setSelectedPromotionId] = useState('');
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const evidenceOpenerRef = useRef(null);
  const candidates = useMemo(() => (
    Array.isArray(omiData?.candidates) ? omiData.candidates : []
  ), [omiData]);
  const promotions = useMemo(() => (
    Array.isArray(omiData?.promotions) ? omiData.promotions : []
  ), [omiData]);

  const handleBackToDashboard = useCallback(() => {
    setOmiView('dashboard');
    setSelectedCandidateId('');
    setSelectedPromotionId('');
    setSelectedEvidence(null);
    evidenceOpenerRef.current = null;
  }, []);

  useEffect(() => {
    handleBackToDashboard();
  }, [dashboardResetRequest, handleBackToDashboard]);

  function handleNavigate(destination) {
    if (destination === 'candidates') {
      const firstCandidateId = getCandidateId(candidates[0]);
      setSelectedCandidateId(firstCandidateId);
      setSelectedEvidence(null);
      evidenceOpenerRef.current = null;
      setOmiView('candidate-detail');
      return;
    }

    if (destination === 'promotion-handoff') {
      const selectedPromotion = promotions.find(
        (promotion) => getPromotionId(promotion) === selectedPromotionId,
      );
      const selectedPromotionIsExact = Boolean(
        selectedPromotion
        && selectedPromotion.candidate_id === selectedCandidateId,
      );
      if (!selectedPromotionIsExact) {
        setSelectedPromotionId('');
      }
      setSelectedEvidence(null);
      evidenceOpenerRef.current = null;
      setOmiView('apply-promotion');
      return;
    }

    if (destination === 'grouped-review') {
      setSelectedCandidateId('');
      setSelectedEvidence(null);
      evidenceOpenerRef.current = null;
      setOmiView('grouped-review');
      return;
    }

    if (destination === 'live-analysis') {
      setSelectedCandidateId('');
      setSelectedEvidence(null);
      evidenceOpenerRef.current = null;
      setOmiView('live-analysis');
      return;
    }

    if (destination === 'approved-memory-canon') {
      handleBackToDashboard();
      onOpenMemoryCanon();
      return;
    }

    handleBackToDashboard();
  }

  function handleSelectPromotion(promotionId) {
    const promotion = promotions.find(
      (item) => getPromotionId(item) === promotionId,
    );
    setSelectedPromotionId(promotion ? promotionId : '');
    setSelectedCandidateId(promotion?.candidate_id ?? '');
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
          promotions={promotions}
          selectedCandidateId={selectedCandidateId}
          selectedPromotionId={selectedPromotionId}
          onSelectPromotion={handleSelectPromotion}
          approvedMemoryCanonSnapshot={summary.approvedSnapshot}
          onCancel={handleBackToDashboard}
        />
      ) : omiView === 'candidate-detail' ? (
        <OMICandidateDetail
          activeProjectId={activeProjectId}
          projectTitle={projectTitle}
          candidates={candidates}
          promotions={promotions}
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
      ) : omiView === 'live-analysis' ? (
        <OMIAnalysisRunWorkflow
          activeProjectId={activeProjectId}
          ideas={summary.ideas}
          candidates={candidates}
          onBackToDashboard={handleBackToDashboard}
          onOpenCandidateReview={() => handleNavigate('candidates')}
          onOpenGroupedReview={() => handleNavigate('grouped-review')}
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
