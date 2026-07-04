function formatCount(value) {
  return Number.isFinite(value) ? String(value) : 'Unavailable';
}

export default function OMICandidateCanonStatusStrip({
  ownerInputCount,
  candidateCount,
  blockedCount,
  handoffReadyCount,
  promotionAuditCount,
  approvedMemoryCount,
  isDegraded = false,
}) {
  return (
    <section
      className="omi-status-strip"
      data-testid="omi-candidate-canon-status"
      aria-label="Candidate and canon status"
    >
      <div>
        <span>Owner Input</span>
        <strong data-testid="omi-dashboard-raw-idea-count">
          {formatCount(ownerInputCount)}
        </strong>
      </div>
      <div>
        <span>Candidates</span>
        <strong data-testid="omi-dashboard-candidate-count">
          {formatCount(candidateCount)}
        </strong>
      </div>
      <div>
        <span>Blocked Review</span>
        <strong>{formatCount(blockedCount)}</strong>
      </div>
      <div>
        <span>Handoff Ready</span>
        <strong data-testid="omi-dashboard-promotion-ready-count">
          {formatCount(handoffReadyCount)}
        </strong>
      </div>
      <div>
        <span>Promotion Audit Record</span>
        <strong>{formatCount(promotionAuditCount)}</strong>
      </div>
      <div className="is-approved-memory">
        <span>Approved Memory/Canon</span>
        <strong>{formatCount(approvedMemoryCount)}</strong>
      </div>
      <div>
        <span>Status</span>
        <strong>{isDegraded ? 'Degraded: no inferred counts' : 'Canon unchanged'}</strong>
      </div>
    </section>
  );
}
