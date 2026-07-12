import { useEffect, useMemo, useRef, useState } from 'react';
import {
  buildGroupedReviewModel,
  selectLinkedReviewCandidates,
} from '../omiGroupedReview.js';

const DECISION_STATUS = Object.freeze({
  pending: 'owner_review',
  approve: 'approved',
  reject: 'rejected',
  needs_revision: 'candidate',
});

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function hasText(value) {
  return typeof value === 'string' && value.trim() !== '';
}

function firstPresent(...values) {
  return values.find((value) => value !== null && value !== undefined && value !== '');
}

function formatValue(value, fallback = 'Not available') {
  if (value === null || value === undefined || value === '') return fallback;
  if (Array.isArray(value)) {
    return value.length > 0 ? value.map((item) => formatValue(item, fallback)).join(', ') : fallback;
  }
  if (typeof value === 'object') {
    const entries = Object.entries(value).filter(([, item]) => (
      item !== null && item !== undefined && item !== ''
    ));
    return entries.length > 0
      ? entries.map(([key, item]) => `${key.replaceAll('_', ' ')}: ${formatValue(item, fallback)}`).join('; ')
      : fallback;
  }
  return String(value);
}

function ownerDecisionValue(candidate) {
  const decision = candidate?.ownerDecision;
  if (typeof decision === 'string') return decision;
  return typeof decision?.decision === 'string' ? decision.decision : 'pending';
}

function lifecycleStatus(candidate) {
  return String(candidate?.originalRecord?.status ?? 'candidate').toLowerCase();
}

function isPendingCandidate(candidate) {
  return ownerDecisionValue(candidate) === 'pending'
    || String(candidate?.reviewStatus ?? '').toLowerCase().includes('pending');
}

function candidateMatchesReviewFilter(candidate, filter) {
  if (filter === 'all') return true;
  if (filter === 'pending') return isPendingCandidate(candidate);
  if (filter === 'reviewed') return !isPendingCandidate(candidate);
  if (filter === 'owner_review') return lifecycleStatus(candidate) === 'owner_review';
  return ownerDecisionValue(candidate) === filter || lifecycleStatus(candidate) === filter;
}

function buildEvidenceScope(candidate) {
  const evidence = asArray(candidate?.evidence);
  const excerpts = evidence
    .map((item) => firstPresent(item?.source_excerpt, item?.excerpt, item?.text, item?.note))
    .filter((item) => item !== null && item !== undefined && item !== '');
  const provenance = candidate?.provenance;

  return {
    scopeType: 'candidate',
    candidateId: candidate?.candidateId,
    sourceType: firstPresent(candidate?.toolSource, candidate?.sourceAdapter),
    sourceLocation: candidate?.sourceLocator,
    quoteExactness: firstPresent(provenance?.quote_exactness, provenance?.quoteExactness),
    confidenceSupportLabel: [candidate?.supportLabel, candidate?.confidence]
      .filter(hasText)
      .join(' / ') || null,
    originalWordingExcerpt: excerpts,
    evidenceSummary: evidence,
    supportsClaimNote: candidate?.claim,
    limitationsAmbiguity: [
      candidate?.uncertaintyLabel,
      candidate?.conflictGroupId ? `Conflict group: ${candidate.conflictGroupId}` : null,
    ].filter(hasText),
    provenanceChain: provenance,
    relatedIds: candidate?.relatedFindingIds,
    timestamps: firstPresent(
      candidate?.originalRecord?.updated_at,
      candidate?.originalRecord?.created_at,
    ),
    sourceHash: firstPresent(provenance?.source_hash, provenance?.sourceHash),
    snapshotHash: firstPresent(provenance?.snapshot_hash, provenance?.snapshotHash),
    sourceOpenState: 'unavailable',
  };
}

function groupCounts(candidates) {
  const conflictIds = new Set(candidates.map((item) => item.conflictGroupId).filter(hasText));
  const candidateTypes = new Map();
  candidates.forEach((candidate) => {
    const type = candidate.originalFindingCandidateType ?? 'Not available';
    candidateTypes.set(type, (candidateTypes.get(type) ?? 0) + 1);
  });
  return {
    total: candidates.length,
    pending: candidates.filter(isPendingCandidate).length,
    uncertain: candidates.filter((item) => hasText(item.uncertaintyLabel)).length,
    conflicts: conflictIds.size,
    candidateTypes: [...candidateTypes.entries()].sort(([left], [right]) => left.localeCompare(right)),
  };
}

function MetadataRow({ label, value, fallback = 'Not available' }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{formatValue(value, fallback)}</dd>
    </div>
  );
}

export default function OMIGroupedReview({
  omiData,
  isLoading = false,
  isUpdating = false,
  status = '',
  error = '',
  onUpdateCandidateDecision = async () => null,
  onOpenEvidence = () => {},
  onBackToDashboard = () => {},
}) {
  const [selectedSourceIdeaId, setSelectedSourceIdeaId] = useState('');
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const [searchText, setSearchText] = useState('');
  const [adapterFilter, setAdapterFilter] = useState('all');
  const [reviewFilter, setReviewFilter] = useState('all');
  const [uncertaintyOnly, setUncertaintyOnly] = useState(false);
  const [conflictOnly, setConflictOnly] = useState(false);
  const [notes, setNotes] = useState('');
  const [approvalConfirmed, setApprovalConfirmed] = useState(false);
  const [localPending, setLocalPending] = useState(false);
  const [localError, setLocalError] = useState('');
  const [announcement, setAnnouncement] = useState('');
  const actionStatusRef = useRef(null);

  const eligibleSources = useMemo(() => (
    asArray(omiData?.ideas)
      .filter((idea) => hasText(idea?.idea_id))
      .map((idea) => ({
        ideaId: idea.idea_id,
        linkedCount: selectLinkedReviewCandidates(omiData, idea.idea_id).length,
      }))
      .filter((source) => source.linkedCount > 0)
      .sort((left, right) => left.ideaId.localeCompare(right.ideaId))
  ), [omiData]);

  useEffect(() => {
    setSelectedSourceIdeaId((current) => (
      eligibleSources.some((source) => source.ideaId === current)
        ? current
        : eligibleSources[0]?.ideaId ?? ''
    ));
  }, [eligibleSources]);

  const model = useMemo(() => buildGroupedReviewModel(omiData, {
    sourceIdeaId: selectedSourceIdeaId,
  }), [omiData, selectedSourceIdeaId]);

  const candidates = useMemo(() => model.groups.flatMap((group) => group.candidates), [model]);

  useEffect(() => {
    setSelectedCandidateId((current) => (
      candidates.some((candidate) => candidate.candidateId === current)
        ? current
        : candidates[0]?.candidateId ?? ''
    ));
  }, [candidates]);

  useEffect(() => {
    setNotes('');
    setApprovalConfirmed(false);
    setLocalError('');
    setAnnouncement('');
  }, [selectedCandidateId]);

  const adapterOptions = useMemo(() => (
    model.groups.map((group) => group.sourceAdapter ?? 'Not available')
  ), [model]);

  useEffect(() => {
    if (adapterFilter !== 'all' && !adapterOptions.includes(adapterFilter)) {
      setAdapterFilter('all');
    }
  }, [adapterFilter, adapterOptions]);

  const normalizedSearch = searchText.trim().toLowerCase();
  const filteredGroups = useMemo(() => model.groups
    .map((group) => ({
      ...group,
      candidates: group.candidates.filter((candidate) => {
        const searchable = [
          candidate.label,
          candidate.name,
          candidate.claim,
          candidate.candidateId,
          candidate.originalFindingCandidateType,
          candidate.sourceAdapter,
        ].filter((item) => item !== null && item !== undefined).join(' ').toLowerCase();
        return (adapterFilter === 'all' || candidate.sourceAdapter === adapterFilter)
          && candidateMatchesReviewFilter(candidate, reviewFilter)
          && (!uncertaintyOnly || hasText(candidate.uncertaintyLabel))
          && (!conflictOnly || hasText(candidate.conflictGroupId))
          && (!normalizedSearch || searchable.includes(normalizedSearch));
      }),
    }))
    .filter((group) => group.candidates.length > 0), [
    adapterFilter,
    conflictOnly,
    model,
    normalizedSearch,
    reviewFilter,
    uncertaintyOnly,
  ]);

  const resultCount = filteredGroups.reduce((total, group) => total + group.candidates.length, 0);
  const selectedCandidate = candidates.find((candidate) => (
    candidate.candidateId === selectedCandidateId
  )) ?? null;
  const requestPending = localPending || isUpdating;
  const selectedStatus = selectedCandidate ? lifecycleStatus(selectedCandidate) : '';
  const isArchived = selectedStatus === 'archived';
  const isOwnerReview = selectedStatus === 'owner_review';
  const canReturnToReview = ['candidate', 'approved', 'rejected'].includes(selectedStatus);
  const pendingDisabled = requestPending || isArchived || (!canReturnToReview && !isOwnerReview);
  const approveDisabled = requestPending || isArchived || !isOwnerReview || !approvalConfirmed;
  const rejectDisabled = requestPending || isArchived || !isOwnerReview;
  const revisionDisabled = requestPending || isArchived || !['candidate', 'owner_review'].includes(selectedStatus);

  function clearFilters() {
    setSearchText('');
    setAdapterFilter('all');
    setReviewFilter('all');
    setUncertaintyOnly(false);
    setConflictOnly(false);
    setAnnouncement('Filters cleared.');
  }

  async function handleDecision(decision) {
    if (!selectedCandidate || requestPending || isArchived) return;
    setLocalPending(true);
    setLocalError('');
    setAnnouncement(`Updating ${selectedCandidate.candidateId}. Waiting for server confirmation.`);
    try {
      const serverRecord = await onUpdateCandidateDecision(selectedCandidate.candidateId, {
        owner_decision: {
          decision,
          approval_confirmed: decision === 'approve' && approvalConfirmed,
          decided_by: 'owner',
          notes,
        },
        status: DECISION_STATUS[decision],
      });
      if (!serverRecord) {
        throw new Error('The owner-decision request did not return a server record.');
      }
      setAnnouncement(`Server confirmed ${decision.replaceAll('_', ' ')} for ${selectedCandidate.candidateId}. OMI refreshed.`);
    } catch (updateError) {
      setLocalError(updateError instanceof Error ? updateError.message : 'Owner-decision update failed.');
      setAnnouncement('');
    } finally {
      setLocalPending(false);
      window.requestAnimationFrame(() => actionStatusRef.current?.focus());
    }
  }

  if (isLoading) {
    return (
      <section className="omi-grouped-review" data-testid="omi-grouped-review">
        <p className="omi-loading-state" role="status">Loading grouped owner review.</p>
      </section>
    );
  }

  return (
    <section
      className="omi-grouped-review"
      data-testid="omi-grouped-review"
      aria-labelledby="omi-grouped-review-heading"
    >
      <header className="omi-grouped-review-header">
        <div>
          <p className="eyebrow">Candidate-only owner review</p>
          <h2 id="omi-grouped-review-heading">Grouped Owner Review</h2>
          <p className="muted-copy">Review one explicit source idea at a time. Separate source ideas are never merged.</p>
        </div>
        <button className="secondary-button" type="button" onClick={onBackToDashboard}>
          Back to OMI Dashboard
        </button>
      </header>

      <section className="omi-grouped-boundaries" aria-label="Grouped review safety boundaries">
        <h3>Review boundaries</h3>
        <ul>
          <li>Queue presence is not approval.</li>
          <li>Support and confidence are not truth.</li>
          <li>Candidate persistence is not canon.</li>
          <li>Tool output is not canon.</li>
          <li>Approval does not apply promotion.</li>
          <li>Memory/Canon remains unchanged.</li>
        </ul>
      </section>

      {error && <p className="omi-error-state" role="alert">{error}</p>}
      {localError && <p className="omi-error-state" role="alert">{localError}</p>}
      <p className="omi-grouped-live-region" role="status" aria-live="polite">
        {localPending ? 'Owner-decision request pending. Prior candidate state remains displayed.' : announcement || status}
      </p>

      {eligibleSources.length === 0 ? (
        <section className="omi-empty-state" aria-label="No eligible grouped-review source">
          <h3>No eligible source idea</h3>
          <p>No source idea links tool-assisted candidates. Grouped review fails closed and Memory/Canon remains unchanged.</p>
        </section>
      ) : (
        <>
          <section className="omi-grouped-source-scope" aria-label="Explicit source idea scope">
            <label htmlFor="omi-grouped-source-idea">Source idea</label>
            <select
              id="omi-grouped-source-idea"
              value={selectedSourceIdeaId}
              onChange={(event) => setSelectedSourceIdeaId(event.target.value)}
            >
              {eligibleSources.map((source) => (
                <option value={source.ideaId} key={source.ideaId}>
                  {source.ideaId} — {source.linkedCount} linked candidates
                </option>
              ))}
            </select>
            <p>
              Selected source ID: <strong>{selectedSourceIdeaId}</strong>
              {' · '}{model.totalCount} linked tool-assisted candidates
            </p>
          </section>

          <section className="omi-grouped-metrics" aria-label="Grouped review metadata counts">
            <div><span>Total candidates</span><strong>{model.totalCount}</strong></div>
            <div><span>Source-adapter groups</span><strong>{model.sourceAdapterCount}</strong></div>
            <div><span>Pending</span><strong>{model.pendingCount}</strong></div>
            <div><span>Reviewed metadata</span><strong>{model.reviewedCount}</strong></div>
            <div><span>Uncertain</span><strong>{model.uncertainCount}</strong></div>
            <div><span>Conflict groups</span><strong>{model.conflictGroupCount}</strong></div>
          </section>

          <section className="omi-grouped-filters" aria-labelledby="omi-grouped-filter-heading">
            <h3 id="omi-grouped-filter-heading">Search and filter this source idea</h3>
            <div className="omi-grouped-filter-grid">
              <label>
                Search candidates
                <input
                  type="search"
                  value={searchText}
                  onChange={(event) => setSearchText(event.target.value)}
                  placeholder="Label, claim, ID, finding type, or adapter"
                />
              </label>
              <label>
                Source adapter
                <select value={adapterFilter} onChange={(event) => setAdapterFilter(event.target.value)}>
                  <option value="all">All adapters</option>
                  {adapterOptions.map((adapter) => <option value={adapter} key={adapter}>{adapter}</option>)}
                </select>
              </label>
              <label>
                Owner decision / review
                <select value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value)}>
                  <option value="all">All review states</option>
                  <option value="pending">Pending / unapproved</option>
                  <option value="reviewed">Reviewed metadata</option>
                  <option value="owner_review">Owner review lifecycle</option>
                  <option value="approve">Approved decision</option>
                  <option value="reject">Rejected decision</option>
                  <option value="needs_revision">Needs revision decision</option>
                </select>
              </label>
              <label className="omi-grouped-check-filter">
                <input
                  type="checkbox"
                  checked={uncertaintyOnly}
                  onChange={(event) => setUncertaintyOnly(event.target.checked)}
                />
                Uncertainty only
              </label>
              <label className="omi-grouped-check-filter">
                <input
                  type="checkbox"
                  checked={conflictOnly}
                  onChange={(event) => setConflictOnly(event.target.checked)}
                />
                Conflict only
              </label>
              <button className="secondary-button" type="button" onClick={clearFilters}>Clear filters</button>
            </div>
            <p role="status">Showing {resultCount} of {model.totalCount} candidates for the selected source idea.</p>
          </section>

          <div className="omi-grouped-review-layout">
            <section className="omi-grouped-list" aria-label="Adapter groups and candidate list">
              <h3>Adapter groups</h3>
              {resultCount === 0 ? (
                <div className="omi-empty-state">
                  <h4>No candidates match these filters</h4>
                  <p>Clear or adjust filters. Candidate decisions have not changed.</p>
                </div>
              ) : filteredGroups.map((group) => {
                const counts = groupCounts(group.candidates);
                return (
                  <details className="omi-grouped-disclosure" key={group.groupKey}>
                    <summary>
                      <span>{formatValue(group.sourceAdapter)}</span>
                      <span>
                        {counts.total} total · {counts.pending} pending · {counts.uncertain} uncertain · {counts.conflicts} conflict groups
                      </span>
                      <span>
                        Finding types: {counts.candidateTypes.map(([type, count]) => `${type} (${count})`).join(', ')}
                      </span>
                    </summary>
                    <ul className="omi-grouped-candidate-list">
                      {group.candidates.map((candidate) => (
                        <li key={candidate.candidateId}>
                          <button
                            type="button"
                            className="omi-grouped-candidate-row"
                            aria-current={candidate.candidateId === selectedCandidateId ? 'true' : undefined}
                            onClick={() => setSelectedCandidateId(candidate.candidateId)}
                          >
                            <span>{formatValue(candidate.label ?? candidate.name, 'Unlabeled candidate')}</span>
                            <span>{formatValue(candidate.originalFindingCandidateType)} · {candidate.candidateId}</span>
                            <span>
                              Decision: {ownerDecisionValue(candidate)}
                              {hasText(candidate.uncertaintyLabel) ? ' · Uncertain' : ''}
                              {hasText(candidate.conflictGroupId) ? ` · Conflict ${candidate.conflictGroupId}` : ''}
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </details>
                );
              })}
            </section>

            <aside className="omi-grouped-detail" aria-label="Selected candidate detail">
              <h3>Selected candidate detail</h3>
              {!selectedCandidate ? (
                <p className="muted-copy">Select a candidate from an adapter group.</p>
              ) : (
                <>
                  <div className="omi-grouped-detail-heading">
                    <div>
                      <p className="eyebrow">{formatValue(selectedCandidate.sourceAdapter)} / {formatValue(selectedCandidate.originalFindingCandidateType)}</p>
                      <h4>{formatValue(selectedCandidate.label ?? selectedCandidate.name, 'Unlabeled candidate')}</h4>
                    </div>
                    <span className="omi-status-badge">Candidate only · {selectedStatus}</span>
                  </div>
                  <dl className="omi-grouped-detail-metadata">
                    <MetadataRow label="Candidate ID" value={selectedCandidate.candidateId} />
                    <MetadataRow label="Source adapter / tool source" value={[selectedCandidate.sourceAdapter, selectedCandidate.toolSource].filter(hasText)} />
                    <MetadataRow label="Original finding type" value={selectedCandidate.originalFindingCandidateType} />
                    <MetadataRow label="Storage candidate type" value={selectedCandidate.storageCandidateType} />
                    <MetadataRow label="Label / name" value={selectedCandidate.label ?? selectedCandidate.name} />
                    <MetadataRow label="Extracted or diagnostic claim" value={selectedCandidate.claim} />
                    <MetadataRow label="Support label" value={selectedCandidate.supportLabel} />
                    <MetadataRow label="Support strength (not truth)" value={selectedCandidate.confidence} />
                    <MetadataRow label="Uncertainty" value={selectedCandidate.uncertaintyLabel} />
                    <MetadataRow label="Conflict-group ID" value={selectedCandidate.conflictGroupId} />
                    <MetadataRow label="Duplicate / related finding metadata" value={selectedCandidate.duplicateMetadata} />
                    <MetadataRow label="Related finding IDs" value={selectedCandidate.relatedFindingIds} />
                    <MetadataRow label="Raw finding ID" value={selectedCandidate.rawFindingId} />
                    <MetadataRow label="Normalized finding ID" value={selectedCandidate.normalizedFindingId} />
                    <MetadataRow label="Candidate fingerprint" value={selectedCandidate.candidateFingerprint} />
                    <MetadataRow label="Evidence fingerprint" value={selectedCandidate.evidenceFingerprint} />
                    <MetadataRow label="Owner decision" value={selectedCandidate.ownerDecision} />
                    <MetadataRow label="Lifecycle status" value={selectedStatus} />
                    <MetadataRow label="Stored review status" value={selectedCandidate.reviewStatus} />
                    <MetadataRow label="Promotion status" value="Ineligible and read-only; no grouped-review action is available" />
                    <MetadataRow label="Evidence count" value={asArray(selectedCandidate.evidence).length} />
                    <MetadataRow label="Source locator" value={selectedCandidate.sourceLocator} />
                    <MetadataRow label="Provenance" value={selectedCandidate.provenance} />
                  </dl>

                  <button
                    className="secondary-button"
                    type="button"
                    aria-haspopup="dialog"
                    onClick={(event) => onOpenEvidence(buildEvidenceScope(selectedCandidate), event.currentTarget)}
                  >
                    Open evidence and provenance
                  </button>

                  <section
                    className="omi-grouped-owner-actions"
                    aria-labelledby="omi-grouped-owner-actions-heading"
                    ref={actionStatusRef}
                    tabIndex="-1"
                  >
                    <h4 id="omi-grouped-owner-actions-heading">Owner-decision lifecycle controls</h4>
                    <p>Actions apply to this candidate only. No batch action is available.</p>
                    <label htmlFor="omi-grouped-owner-notes">Owner review notes</label>
                    <textarea
                      id="omi-grouped-owner-notes"
                      value={notes}
                      onChange={(event) => setNotes(event.target.value)}
                      disabled={requestPending || isArchived}
                      rows="3"
                    />
                    <label className="omi-grouped-approval-confirmation">
                      <input
                        type="checkbox"
                        checked={approvalConfirmed}
                        onChange={(event) => setApprovalConfirmed(event.target.checked)}
                        disabled={requestPending || isArchived || !isOwnerReview}
                      />
                      <span>
                        I confirm this owner decision approves this candidate for review lifecycle only.
                        It does not make the candidate canon and does not apply promotion.
                      </span>
                    </label>
                    <div className="omi-grouped-decision-buttons">
                      <button
                        className="secondary-button"
                        type="button"
                        disabled={pendingDisabled}
                        aria-describedby={pendingDisabled ? 'omi-grouped-pending-reason' : undefined}
                        onClick={() => handleDecision('pending')}
                      >
                        Move to owner review
                      </button>
                      <button
                        className="primary-button"
                        type="button"
                        disabled={approveDisabled}
                        aria-describedby={approveDisabled ? 'omi-grouped-approve-reason' : undefined}
                        onClick={() => handleDecision('approve')}
                      >
                        Approve review lifecycle
                      </button>
                      <button
                        className="secondary-button"
                        type="button"
                        disabled={rejectDisabled}
                        aria-describedby={rejectDisabled ? 'omi-grouped-reject-reason' : undefined}
                        onClick={() => handleDecision('reject')}
                      >
                        Reject candidate
                      </button>
                      <button
                        className="secondary-button"
                        type="button"
                        disabled={revisionDisabled}
                        aria-describedby={revisionDisabled ? 'omi-grouped-revision-reason' : undefined}
                        onClick={() => handleDecision('needs_revision')}
                      >
                        Needs revision
                      </button>
                    </div>
                    <div className="omi-grouped-disabled-reasons">
                      {pendingDisabled && <p id="omi-grouped-pending-reason">Unavailable while pending, archived, or outside an allowed transition.</p>}
                      {approveDisabled && <p id="omi-grouped-approve-reason">Approval requires owner-review lifecycle status and the explicit confirmation checkbox.</p>}
                      {rejectDisabled && <p id="omi-grouped-reject-reason">Reject is available only from owner-review lifecycle status.</p>}
                      {revisionDisabled && <p id="omi-grouped-revision-reason">Needs revision is available from candidate or owner-review lifecycle status.</p>}
                    </div>
                    {isArchived && <p>Archived records receive no grouped-review action.</p>}
                    <p>Each action waits for one server response and the authoritative OMI refresh. The displayed lifecycle is never updated optimistically.</p>
                  </section>
                </>
              )}
            </aside>
          </div>
        </>
      )}
    </section>
  );
}
