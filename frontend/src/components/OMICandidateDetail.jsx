import OMICandidateFieldTable from './OMICandidateFieldTable.jsx';
import {
  buildCandidateEvidenceScope,
} from './OMIEvidenceDrawer.jsx';
import OMIPromotionReadinessChecklist, {
  getPromotionReadinessItems,
} from './OMIPromotionReadinessChecklist.jsx';

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function firstPresent(...values) {
  for (const value of values) {
    if (value !== null && value !== undefined && value !== '') {
      return value;
    }
  }
  return null;
}

function formatStoredValue(value, missingLabel = 'Unavailable') {
  if (value === null || value === undefined || value === '') {
    return missingLabel;
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : missingLabel;
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function getCandidateId(candidate) {
  return firstPresent(candidate?.candidate_id, candidate?.candidateId, candidate?.id);
}

function getCandidateStatus(candidate) {
  const status = String(
    firstPresent(candidate?.status, candidate?.review_status, candidate?.decision, 'Pending Review'),
  );
  return status.toLowerCase().includes('approved')
    ? 'Candidate: Owner Approved'
    : 'Candidate: Pending Review';
}

function getCandidateType(candidate) {
  return formatStoredValue(
    firstPresent(candidate?.candidate_type, candidate?.type, candidate?.category),
    'Unsupported candidate schema',
  );
}

function getDestination(candidate) {
  return formatStoredValue(
    firstPresent(candidate?.destination, candidate?.target_destination, candidate?.memory_canon_destination),
    'Missing destination',
  );
}

function getSource(candidate) {
  return formatStoredValue(
    firstPresent(
      candidate?.source,
      candidate?.source_id,
      candidate?.source_locator,
      candidate?.raw_idea_id,
      candidate?.idea_id,
    ),
    'Unavailable',
  );
}

function getCandidateApprovalDisabledReason(candidate) {
  const readinessItems = getPromotionReadinessItems(candidate);
  const blockers = readinessItems.filter((item) => !item.isMet).map((item) => item.detail);
  if (blockers.length === 0) {
    return 'Disabled: candidate approval is reserved for future review metadata wiring; it does not update Memory/Canon.';
  }
  return `Disabled: candidate approval requires ${blockers.join('; ')}.`;
}

function findCandidate(candidates, selectedCandidateId) {
  if (!selectedCandidateId) {
    return null;
  }
  return candidates.find((candidate) => getCandidateId(candidate) === selectedCandidateId) ?? null;
}

function ReadOnlyReferences({ candidate }) {
  const approvedLinks = asArray(
    candidate?.approved_memory_canon_links
      ?? candidate?.approved_memory_links
      ?? candidate?.canon_links,
  );
  const promotionAudit = candidate?.promotion_audit_record ?? candidate?.promotion_record;

  return (
    <section className="omi-candidate-panel" aria-label="Read-only approved Memory/Canon references">
      <h2>Approved Memory/Canon links</h2>
      {approvedLinks.length === 0 ? (
        <p className="muted-copy">No approved Memory/Canon links.</p>
      ) : (
        <ul className="omi-readonly-reference-list">
          {approvedLinks.map((link, index) => (
            <li key={formatStoredValue(link?.id ?? link?.record_id ?? index)}>
              <span className="omi-status-badge">Read-only reference</span>
              <span>{formatStoredValue(link)}</span>
            </li>
          ))}
        </ul>
      )}
      <p className="review-boundary-note">
        Promotion Audit Record: {formatStoredValue(promotionAudit, 'Not Applied to Memory/Canon')}
      </p>
    </section>
  );
}

function EvidenceProvenance({ candidate, onOpenEvidence = () => {} }) {
  return (
    <section className="omi-candidate-panel" aria-label="Evidence and provenance summary">
      <div className="section-heading">
        <h2>Evidence / Provenance</h2>
        <button
          className="secondary-button"
          type="button"
          data-testid="omi-evidence-drawer-trigger"
          aria-haspopup="dialog"
          onClick={(event) => onOpenEvidence(buildCandidateEvidenceScope(candidate), event.currentTarget)}
        >
          Open evidence drawer
        </button>
      </div>
      <dl className="omi-candidate-metadata">
        <div>
          <dt>Evidence</dt>
          <dd>
            {formatStoredValue(
              firstPresent(candidate?.evidence_summary, candidate?.evidence_refs),
              'Missing evidence',
            )}
          </dd>
        </div>
        <div>
          <dt>Provenance</dt>
          <dd>
            {formatStoredValue(
              firstPresent(candidate?.provenance_summary, candidate?.provenance_refs, candidate?.source_locator),
              'Missing provenance',
            )}
          </dd>
        </div>
        <div>
          <dt>Original wording excerpt</dt>
          <dd>{formatStoredValue(candidate?.original_wording_excerpt, 'Unavailable')}</dd>
        </div>
        <div>
          <dt>Supports-claim note</dt>
          <dd>{formatStoredValue(candidate?.supports_claim_note, 'Unavailable')}</dd>
        </div>
      </dl>
      <p className="review-boundary-note">
        Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
      </p>
      <p className="review-boundary-note">Confidence indicates support strength, not truth.</p>
    </section>
  );
}

function DuplicateDependencyPanel({ candidate }) {
  return (
    <section className="omi-candidate-panel" aria-label="Duplicate / Merge / Clarification">
      <h2>Duplicate / Merge / Clarification</h2>
      <dl className="omi-candidate-metadata">
        <div>
          <dt>Duplicate/dependency</dt>
          <dd>
            {formatStoredValue(
              firstPresent(candidate?.duplicate_state, candidate?.duplicate_decision),
              'Duplicate unresolved',
            )}
          </dd>
        </div>
        <div>
          <dt>Dependency review</dt>
          <dd>
            {formatStoredValue(
              firstPresent(candidate?.dependency_state, candidate?.dependency_review),
              'Dependency unresolved',
            )}
          </dd>
        </div>
      </dl>
      <div className="omi-disabled-action-row" aria-label="Duplicate decision metadata actions">
        {['Treat as New Candidate', 'Plan Merge with Existing', 'Ignore as Duplicate', 'Needs Owner Clarification'].map((label) => (
          <button className="secondary-button" type="button" disabled key={label}>
            {label}
          </button>
        ))}
      </div>
      <p className="omi-disabled-reason">
        Disabled: duplicate and dependency changes are future review metadata wiring only.
      </p>
    </section>
  );
}

export default function OMICandidateDetail({
  activeProjectId,
  projectTitle,
  candidates = [],
  selectedCandidateId = '',
  isLoading = false,
  error = '',
  onBackToDashboard = () => {},
  onOpenApplyPromotion = () => {},
  onOpenEvidence = () => {},
}) {
  const storedCandidates = asArray(candidates);
  const candidate = findCandidate(storedCandidates, selectedCandidateId);
  const approvalReasonId = 'omi-candidate-approval-disabled-reason';

  if (isLoading) {
    return (
      <section className="omi-candidate-detail" data-testid="omi-candidate-detail" aria-label="OMI Candidate Detail">
        <p className="omi-loading-state" role="status">Loading candidate.</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="omi-candidate-detail" data-testid="omi-candidate-detail" aria-label="OMI Candidate Detail">
        <section className="omi-error-state" role="alert">
          <h2>Candidate schema unsupported or partially corrupt.</h2>
          <p>{error}</p>
        </section>
      </section>
    );
  }

  if (storedCandidates.length === 0) {
    return (
      <section className="omi-candidate-detail" data-testid="omi-candidate-detail" aria-label="OMI Candidate Detail">
        <section className="omi-empty-state">
          <h2>No candidate selected.</h2>
          <p>No candidates are stored for this project. Candidate review is empty and Memory/Canon has not changed.</p>
          <button className="secondary-button" type="button" onClick={onBackToDashboard}>
            Back to OMI Dashboard
          </button>
        </section>
      </section>
    );
  }

  if (!selectedCandidateId) {
    return (
      <section className="omi-candidate-detail" data-testid="omi-candidate-detail" aria-label="OMI Candidate Detail">
        <section className="omi-empty-state">
          <h2>No candidate selected.</h2>
          <p>Select a stored candidate from the OMI Dashboard review row.</p>
          <button className="secondary-button" type="button" onClick={onBackToDashboard}>
            Back to OMI Dashboard
          </button>
        </section>
      </section>
    );
  }

  if (!candidate) {
    return (
      <section className="omi-candidate-detail" data-testid="omi-candidate-detail" aria-label="OMI Candidate Detail">
        <section className="omi-empty-state">
          <h2>Candidate not found.</h2>
          <p>Candidate not found. Stored review metadata is unavailable.</p>
          <button className="secondary-button" type="button" onClick={onBackToDashboard}>
            Back to OMI Dashboard
          </button>
        </section>
      </section>
    );
  }

  const candidateId = getCandidateId(candidate);
  const disabledReason = getCandidateApprovalDisabledReason(candidate);

  return (
    <section className="omi-candidate-detail" data-testid="omi-candidate-detail" aria-label="OMI Candidate Detail">
      <header className="omi-candidate-header">
        <div>
          <p className="eyebrow">Active project: {projectTitle || activeProjectId || 'Project'} / project-local OMI</p>
          <h1>Candidate: {candidateId}</h1>
        </div>
        <button className="secondary-button" type="button" onClick={onBackToDashboard}>
          Back to OMI Dashboard
        </button>
      </header>

      <section className="omi-candidate-status-grid" aria-label="Candidate status metadata">
        <div>
          <span>Candidate ID</span>
          <strong>{formatStoredValue(candidateId, 'Missing')}</strong>
        </div>
        <div>
          <span>Candidate type</span>
          <strong>{getCandidateType(candidate)}</strong>
        </div>
        <div>
          <span>Candidate status</span>
          <strong>{getCandidateStatus(candidate)}</strong>
        </div>
        <div>
          <span>Destination</span>
          <strong>{getDestination(candidate)}</strong>
        </div>
        <div>
          <span>Source</span>
          <strong>{getSource(candidate)}</strong>
        </div>
        <div>
          <span>Project-local label</span>
          <strong>project-local review metadata only</strong>
        </div>
      </section>

      <p className="review-boundary-note">
        This remains a candidate until apply-promotion is separately confirmed and completed.
      </p>

      <section className="omi-candidate-actions" aria-label="Candidate actions">
        <button
          className="primary-button"
          type="button"
          disabled
          aria-describedby={approvalReasonId}
        >
          Approve Candidate for Handoff
        </button>
        <button className="secondary-button" type="button" disabled>Reject Candidate</button>
        <button className="secondary-button" type="button" disabled>Needs Revision</button>
        <button className="secondary-button" type="button" disabled>Archive Candidate</button>
        <p
          id={approvalReasonId}
          className="omi-disabled-reason"
          data-testid="omi-candidate-approval-disabled-reason"
        >
          {disabledReason} Owner approval prepares this candidate for a future handoff. It does not update Memory/Canon.
        </p>
      </section>

      <nav className="omi-mobile-tabs" aria-label="Mobile Candidate Detail sections">
        <a href="#omi-candidate-fields">Fields</a>
        <a href="#omi-candidate-evidence">Evidence</a>
        <a href="#omi-candidate-readiness">Readiness</a>
      </nav>

      <div className="omi-candidate-detail-layout">
        <div id="omi-candidate-fields">
          <OMICandidateFieldTable candidate={candidate} onOpenEvidence={onOpenEvidence} />
        </div>
        <aside className="omi-candidate-side-rail" id="omi-candidate-evidence">
          <EvidenceProvenance candidate={candidate} onOpenEvidence={onOpenEvidence} />
          <DuplicateDependencyPanel candidate={candidate} />
          <ReadOnlyReferences candidate={candidate} />
        </aside>
      </div>

      <div id="omi-candidate-readiness">
        <OMIPromotionReadinessChecklist candidate={candidate} />
      </div>

      <section className="omi-candidate-panel" aria-label="Candidate apply-promotion boundary">
        <h2>Apply to Memory/Canon</h2>
        <button
          className="secondary-button"
          type="button"
          onClick={onOpenApplyPromotion}
        >
          Open Apply-Promotion Handoff
        </button>
        <button className="primary-button" type="button" disabled>
          Apply to Memory/Canon
        </button>
        <p className="omi-disabled-reason">
          Disabled: apply-promotion requires a completed route-backed confirmation and every handoff gate.
        </p>
        <p className="review-boundary-note">Promotion Audit Record. Not Applied to Memory/Canon.</p>
      </section>
    </section>
  );
}
