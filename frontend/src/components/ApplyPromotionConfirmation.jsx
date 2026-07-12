import { useMemo, useState } from 'react';
import {
  APPLY_PROMOTION_DESTINATION_TYPES,
  isSafeReviewRouteId,
  submitApplyPromotion,
} from '../api.js';
import OMIApplyPromotionBlockers from './OMIApplyPromotionBlockers.jsx';

const DESTINATION_LABELS = {
  approved_character: 'Approved character',
  approved_location: 'Approved location',
  approved_timeline_event: 'Approved timeline event',
  approved_relationship: 'Approved relationship',
  approved_organization: 'Approved organization',
  approved_object: 'Approved object',
  approved_plot_thread: 'Approved plot thread',
  approved_continuity_record: 'Approved continuity record',
  approved_open_question: 'Approved open question',
  approved_memory_index: 'Approved memory index',
};

const DESTINATION_FOLDER = {
  approved_character: 'approved_character',
  approved_location: 'approved_location',
  approved_timeline_event: 'approved_timeline_event',
  approved_relationship: 'approved_relationship',
  approved_organization: 'approved_organization',
  approved_object: 'approved_object',
  approved_plot_thread: 'approved_plot_thread',
  approved_continuity_record: 'approved_continuity_record',
  approved_open_question: 'approved_open_question',
  approved_memory_index: 'approved_memory_index',
};

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

function compactString(value) {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : '';
}

function formatValue(value, missingLabel = 'Safely unavailable') {
  if (value === null || value === undefined || value === '') {
    return missingLabel;
  }
  if (Array.isArray(value)) {
    return value.length === 0 ? missingLabel : value.join(', ');
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function hasValue(value) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  return value !== null && value !== undefined && value !== '';
}

function asRefList(...values) {
  const refs = [];

  values.forEach((value) => {
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== null && item !== undefined && String(item).trim() !== '') {
          refs.push(item);
        }
      });
      return;
    }

    if (value !== null && value !== undefined && value !== '') {
      refs.push(value);
    }
  });

  return refs;
}

function normalizeDestinationType(value) {
  const raw = compactString(value);
  if (APPLY_PROMOTION_DESTINATION_TYPES.includes(raw)) {
    return raw;
  }

  const normalized = raw.toLowerCase().replaceAll(' ', '_').replaceAll('-', '_');
  if (APPLY_PROMOTION_DESTINATION_TYPES.includes(normalized)) {
    return normalized;
  }

  const prefixed = `approved_${normalized}`;
  return APPLY_PROMOTION_DESTINATION_TYPES.includes(prefixed) ? prefixed : '';
}

function getCandidateId(candidate, queueEntry) {
  return compactString(firstPresent(
    candidate?.candidate_id,
    candidate?.candidateId,
    candidate?.id,
    queueEntry?.candidate_record_id,
    queueEntry?.candidate_id,
  ));
}

function getCandidateType(candidate, queueEntry) {
  return compactString(firstPresent(
    candidate?.candidate_type,
    candidate?.type,
    candidate?.category,
    queueEntry?.candidate_type,
  ));
}

function getStatus(candidate, queueEntry) {
  return compactString(firstPresent(
    candidate?.status,
    candidate?.review_status,
    candidate?.decision,
    queueEntry?.review_status,
    queueEntry?.lifecycle_state,
  ));
}

function getDestinationType(candidate, queueEntry) {
  return normalizeDestinationType(firstPresent(
    candidate?.destination_type,
    candidate?.target_destination_type,
    candidate?.memory_canon_destination_type,
    queueEntry?.destination_type,
    queueEntry?.target_destination_type,
  ));
}

function getDestinationLabel(destinationType, candidate, queueEntry) {
  return formatValue(
    firstPresent(
      DESTINATION_LABELS[destinationType],
      candidate?.destination,
      candidate?.target_destination,
      candidate?.memory_canon_destination,
      queueEntry?.destination,
      queueEntry?.target_category,
    ),
  );
}

function getDestinationKey(candidate, queueEntry, candidateId) {
  return compactString(firstPresent(
    candidate?.destination_key,
    candidate?.target_key,
    queueEntry?.destination_key,
    queueEntry?.target_key,
    candidateId,
  ));
}

function getTargetPath(destinationType, destinationKey, candidate, queueEntry) {
  const explicitPath = compactString(firstPresent(
    candidate?.destination_path,
    candidate?.target_path,
    queueEntry?.destination_path,
    queueEntry?.target_path,
  ));
  if (explicitPath) {
    return explicitPath;
  }
  if (destinationType && destinationKey) {
    return `memory/${DESTINATION_FOLDER[destinationType]}/${destinationKey}.json`;
  }
  return '';
}

function getOwnerApproved(candidate, queueEntry) {
  const status = getStatus(candidate, queueEntry).toLowerCase();
  return Boolean(
    candidate?.owner_approved === true
    || queueEntry?.owner_approved === true
    || status.includes('owner approved')
    || status === 'approved'
    || status.includes('approved'),
  );
}

function getEvidenceRefs(candidate, queueEntry) {
  return asRefList(candidate?.evidence_refs, queueEntry?.evidence_refs, candidate?.evidence_summary, queueEntry?.evidence_summary);
}

function getProvenanceRefs(candidate, queueEntry) {
  return asRefList(
    candidate?.provenance_refs,
    queueEntry?.provenance_refs,
    candidate?.provenance_summary,
    queueEntry?.provenance_summary,
  );
}

function getSourceLocatorRefs(candidate, queueEntry) {
  return asRefList(
    candidate?.source_locator_refs,
    queueEntry?.source_locator_refs,
    candidate?.source_locator,
    candidate?.source_location,
    candidate?.source_id,
    candidate?.raw_idea_id,
    queueEntry?.source_locator,
    queueEntry?.source_document,
  );
}

function isResolved(value, unresolvedLabel) {
  if (!hasValue(value)) {
    return false;
  }
  return !String(value).toLowerCase().includes(unresolvedLabel);
}

function getBeforeState(candidate, queueEntry, approvedMemoryCanonSnapshot) {
  return firstPresent(
    approvedMemoryCanonSnapshot,
    candidate?.approved_memory_canon_before_state,
    candidate?.before_state_snapshot,
    candidate?.approved_memory_canon_snapshot,
    queueEntry?.approved_memory_canon_before_state,
    queueEntry?.before_state_snapshot,
  );
}

function getPromotionAudit(candidate, queueEntry) {
  return firstPresent(
    candidate?.promotion_audit_record,
    candidate?.promotion_record,
    candidate?.promotion_audit_preview,
    queueEntry?.promotion_audit_record,
    queueEntry?.promotion_record,
    queueEntry?.promotion_audit_preview,
  );
}

export function getApplyPromotionBlockers({
  projectId,
  candidate,
  queueEntry,
  approvedMemoryCanonSnapshot,
  ownerFinalConfirmation,
  applyPromotionAvailable,
  failureMessage,
}) {
  const candidateId = getCandidateId(candidate, queueEntry);
  const candidateType = getCandidateType(candidate, queueEntry);
  const status = getStatus(candidate, queueEntry);
  const destinationType = getDestinationType(candidate, queueEntry);
  const destinationKey = getDestinationKey(candidate, queueEntry, candidateId);
  const targetPath = getTargetPath(destinationType, destinationKey, candidate, queueEntry);
  const evidenceRefs = getEvidenceRefs(candidate, queueEntry);
  const provenanceRefs = getProvenanceRefs(candidate, queueEntry);
  const sourceLocatorRefs = getSourceLocatorRefs(candidate, queueEntry);
  const ownerApproved = getOwnerApproved(candidate, queueEntry);
  const duplicateState = firstPresent(candidate?.duplicate_state, candidate?.duplicate_decision, queueEntry?.duplicate_state);
  const dependencyState = firstPresent(candidate?.dependency_state, candidate?.dependency_review, queueEntry?.dependency_state);
  const promotionAudit = getPromotionAudit(candidate, queueEntry);
  const beforeState = getBeforeState(candidate, queueEntry, approvedMemoryCanonSnapshot);
  const explicitBlockers = asArray(candidate?.blockers ?? candidate?.promotion_blockers ?? queueEntry?.blockers);
  const blockers = [];

  if (!candidateId || !candidateType || !status.toLowerCase().includes('ready')) {
    blockers.push('Candidate not ready');
  }
  if (!ownerApproved) {
    blockers.push('Missing owner approval');
  }
  if (!destinationType && !hasValue(firstPresent(candidate?.destination, queueEntry?.target_category))) {
    blockers.push('Missing destination');
  }
  if (!destinationType) {
    blockers.push('Unsupported destination');
  }
  if (evidenceRefs.length === 0 || provenanceRefs.length === 0) {
    blockers.push('Missing evidence/provenance');
  }
  if (sourceLocatorRefs.length === 0) {
    blockers.push('Missing source locator');
  }
  if (!isResolved(duplicateState, 'unresolved')) {
    blockers.push('Duplicate unresolved');
  }
  if (!isResolved(dependencyState, 'unresolved')) {
    blockers.push('Dependency unresolved');
  }
  if (!hasValue(promotionAudit)) {
    blockers.push('Promotion audit record missing');
  }
  if (!targetPath) {
    blockers.push('Target file/path missing');
  }
  if (!hasValue(beforeState)) {
    blockers.push('Approved Memory/Canon before-state unavailable');
  }
  if (!ownerFinalConfirmation) {
    blockers.push('Final confirmation incomplete');
  }
  if (!applyPromotionAvailable) {
    blockers.push('Apply-promotion unavailable in this version');
  }
  if (failureMessage || !isSafeReviewRouteId(projectId) || explicitBlockers.length > 0) {
    blockers.push('Apply-promotion failed or would fail closed');
  }

  return [...new Set(blockers)];
}

function MetadataRow({ label, value, missingLabel = 'Safely unavailable' }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{formatValue(value, missingLabel)}</dd>
    </div>
  );
}

export default function ApplyPromotionConfirmation({
  projectId,
  candidate = null,
  queueEntry = null,
  approvedMemoryCanonSnapshot = null,
  disabled = false,
  applyPromotionAvailable = false,
  onCancel = () => {},
}) {
  const [ownerFinalConfirmation, setOwnerFinalConfirmation] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const candidateId = getCandidateId(candidate, queueEntry);
  const candidateType = getCandidateType(candidate, queueEntry);
  const queueEntryId = compactString(queueEntry?.queue_entry_id);
  const status = getStatus(candidate, queueEntry) || 'Candidate: Pending Review';
  const destinationType = getDestinationType(candidate, queueEntry);
  const destinationKey = getDestinationKey(candidate, queueEntry, candidateId);
  const targetPath = getTargetPath(destinationType, destinationKey, candidate, queueEntry);
  const destinationLabel = getDestinationLabel(destinationType, candidate, queueEntry);
  const evidenceRefs = useMemo(() => getEvidenceRefs(candidate, queueEntry), [candidate, queueEntry]);
  const provenanceRefs = useMemo(() => getProvenanceRefs(candidate, queueEntry), [candidate, queueEntry]);
  const sourceLocatorRefs = useMemo(() => getSourceLocatorRefs(candidate, queueEntry), [candidate, queueEntry]);
  const beforeState = getBeforeState(candidate, queueEntry, approvedMemoryCanonSnapshot);
  const promotionAudit = getPromotionAudit(candidate, queueEntry);
  const duplicateState = firstPresent(candidate?.duplicate_state, candidate?.duplicate_decision, queueEntry?.duplicate_state);
  const dependencyState = firstPresent(candidate?.dependency_state, candidate?.dependency_review, queueEntry?.dependency_state);
  const finalReasonId = 'omi-apply-promotion-final-action-disabled-reason';
  const blockerReasonId = 'omi-apply-promotion-visible-blocker-reasons';
  const blockers = getApplyPromotionBlockers({
    projectId,
    candidate,
    queueEntry,
    approvedMemoryCanonSnapshot,
    ownerFinalConfirmation,
    applyPromotionAvailable: applyPromotionAvailable && !disabled,
    failureMessage: error,
  });
  const finalDisabled = blockers.length > 0 || isSubmitting;
  const finalDisabledReason = finalDisabled
    ? `Disabled: Final Apply-Promotion cannot run while visible blockers remain: ${blockers.join('; ')}.`
    : 'All visible blockers are absent and owner final confirmation is complete.';
  const finalActionName = `Final Apply-Promotion for candidate ${candidateId || 'missing candidate'} to ${destinationLabel}`;

  async function handleSubmit(event) {
    event.preventDefault();
    setResult('');
    setError('');

    if (finalDisabled) {
      setError('Apply-promotion failed or would fail closed.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await submitApplyPromotion(projectId, {
        candidate_id: candidateId,
        queue_entry_id: queueEntryId,
        candidate_type: candidateType,
        owner_actor_id: 'owner-001',
        owner_actor_label: 'Owner',
        owner_confirmation: true,
        owner_note: '',
        destination_type: destinationType,
        destination_path: targetPath,
        destination_key: destinationKey,
        evidence_refs: evidenceRefs,
        provenance_refs: provenanceRefs,
        source_locator_refs: sourceLocatorRefs,
        source_candidate_snapshot_hash: compactString(candidate?.source_candidate_snapshot_hash),
        requested_at: new Date().toISOString(),
      });
      setResult(formatValue(response, 'Apply-promotion completed with no returned audit details.'));
      setOwnerFinalConfirmation(false);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Apply-promotion failed or would fail closed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section
      className="omi-apply-confirmation"
      data-testid="omi-apply-promotion-confirmation"
      aria-label="Apply-Promotion Confirmation"
    >
      <header className="omi-apply-guard-header">
        <div>
          <p className="eyebrow">Guarded Handoff</p>
          <h1>Apply-Promotion Confirmation</h1>
        </div>
        <span className="omi-status-badge is-warning">Not Applied to Memory/Canon</span>
      </header>

      <section className="omi-apply-boundary" aria-label="Apply-Promotion boundary copy">
        <p>This is a candidate-only, no-canon handoff.</p>
        <p>Queue presence is not approval. Confidence is not truth.</p>
        <p>Candidate persistence is not canon. Raw artifacts are support data, not canon.</p>
        <p>Apply-Promotion is the only approved Memory/Canon mutation path.</p>
        <p>Final owner confirmation is required before Apply-Promotion.</p>
        <p>Memory/Canon Unchanged.</p>
      </section>

      <OMIApplyPromotionBlockers blockers={blockers} describedById={blockerReasonId} />

      <div className="omi-apply-section-grid">
        <section className="omi-apply-section" aria-label="Candidate Snapshot">
          <h2>Candidate Snapshot</h2>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Candidate" value={candidateId} missingLabel="Missing candidate" />
            <MetadataRow label="Candidate type" value={candidateType} missingLabel="Missing candidate type" />
            <MetadataRow label="Candidate status" value={status} />
            <MetadataRow
              label="Structured field summary"
              value={firstPresent(candidate?.structured_field_summary, candidate?.field_review_rows, candidate?.fields)}
              missingLabel="No stored structured field summary"
            />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Destination and target path">
          <h2>Destination</h2>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Destination" value={destinationLabel} />
            <MetadataRow label="Destination type" value={destinationType} missingLabel="Unsupported destination" />
            <MetadataRow label="Destination key" value={destinationKey} missingLabel="Missing destination" />
            <MetadataRow label="Target Path" value={targetPath} missingLabel="Target file/path missing" />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Evidence / Provenance Summary">
          <h2>Evidence / Provenance Summary</h2>
          <dl className="omi-apply-metadata" data-testid="ux2-promotion-audit-evidence">
            <MetadataRow label="Evidence refs" value={evidenceRefs} missingLabel="Missing evidence/provenance" />
            <MetadataRow label="Provenance refs" value={provenanceRefs} missingLabel="Missing evidence/provenance" />
            <MetadataRow
              label="Support limitations"
              value={firstPresent(candidate?.limitations_ambiguity, candidate?.supports_claim_note)}
            />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Source Location Summary">
          <h2>Source Location Summary</h2>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Source locator refs" value={sourceLocatorRefs} missingLabel="Missing source locator" />
            <MetadataRow label="Source hash" value={candidate?.source_hash} />
            <MetadataRow label="Snapshot hash" value={candidate?.snapshot_hash ?? candidate?.source_candidate_snapshot_hash} />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Duplicate / Link / Dependency Summary">
          <h2>Duplicate / Link / Dependency Summary</h2>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Duplicate decision" value={duplicateState} missingLabel="Duplicate unresolved" />
            <MetadataRow label="Dependencies" value={dependencyState} missingLabel="Dependency unresolved" />
            <MetadataRow
              label="Related candidate links"
              value={firstPresent(candidate?.related_ids, candidate?.linked_candidate_ids, queueEntry?.related_ids)}
              missingLabel="No linked candidates recorded"
            />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Approved Memory/Canon Before-State">
          <h2>Approved Memory/Canon Before-State</h2>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Before-state snapshot" value={beforeState} missingLabel="Approved Memory/Canon before-state unavailable" />
            <MetadataRow label="Before-state status" value="Memory/Canon Unchanged" />
            <MetadataRow label="Mutation status" value="Not Applied to Memory/Canon" />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Promotion Audit Record">
          <h2>Promotion Audit Record</h2>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Promotion Audit Record" value={promotionAudit} missingLabel="Promotion audit record missing" />
            <MetadataRow label="Audit Preview" value="Audit Preview: candidate ID, owner approval, destination, evidence, provenance, target path, timestamp, and confirmation." />
            <MetadataRow label="Audit boundary" value="Promotion audit records are audit-only until apply-promotion succeeds." />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Failure safety">
          <h2>Failure Safety</h2>
          <p>
            Failure safety copy: if apply-promotion fails, Memory/Canon must remain unchanged
            and the audit trail must show the failure state.
          </p>
        </section>
      </div>

      <form className="omi-apply-final-form" onSubmit={handleSubmit}>
        <section className="omi-apply-section" aria-label="Owner Final Confirmation">
          <h2>Owner Final Confirmation</h2>
          <label
            className="omi-checkbox-row"
            data-testid="ux2-apply-promotion-owner-confirmation"
          >
            <input
              type="checkbox"
              checked={ownerFinalConfirmation}
              onChange={(event) => {
                setOwnerFinalConfirmation(event.target.checked);
                setError('');
              }}
              disabled={isSubmitting}
            />
            I am the owner and this is owner final confirmation for apply-promotion.
          </label>
        </section>

        <p id={finalReasonId} className="omi-disabled-reason">
          {finalDisabledReason}
        </p>

        <div className="omi-apply-final-actions">
          <button className="secondary-button" type="button" onClick={onCancel}>
            Cancel / Return
          </button>
          <button
            className="omi-final-apply-button"
            type="submit"
            data-testid="omi-apply-promotion-final-action"
            disabled={finalDisabled}
            aria-label={finalActionName}
            aria-describedby={`${blockerReasonId} ${finalReasonId}`}
          >
            {isSubmitting ? 'Final Apply-Promotion pending' : 'Final Apply-Promotion'}
          </button>
        </div>
      </form>

      {result && <p className="context-note">{result}</p>}
      {error && (
        <p className="error-copy" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
