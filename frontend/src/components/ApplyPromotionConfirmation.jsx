import { useMemo, useState } from 'react';
import {
  APPLY_PROMOTION_DESTINATION_TYPES,
  isSafeReviewRouteId,
  submitApplyPromotion,
} from '../api.js';

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

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'Not recorded';
  }
  if (Array.isArray(value)) {
    return value.length === 0 ? 'None' : value.join(', ');
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function compactString(value) {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : '';
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

function sourceLocatorRefs(entry) {
  return asRefList(
    entry?.source_locator_refs,
    entry?.source_locator,
    entry?.source_document,
  );
}

function formatPromotionResult(response) {
  const result = response?.promotion_result;
  const audit = result?.audit_record;
  const plan = response?.promotion_plan;

  if (!result && !plan) {
    return 'Apply-promotion completed, but no audit details were returned.';
  }

  return [
    `status: ${formatValue(result?.promotion_status ?? plan?.validation_status)}`,
    `promotion_record_id: ${formatValue(result?.promotion_record_id ?? audit?.promotion_record_id)}`,
    `destination_path: ${formatValue(audit?.destination_path ?? plan?.destination_path)}`,
    `mutation_performed: ${formatValue(result?.mutation_performed)}`,
  ].join(' | ');
}

export default function ApplyPromotionConfirmation({
  projectId,
  queueEntry,
  disabled = false,
}) {
  const candidateId = queueEntry?.candidate_record_id ?? queueEntry?.candidate_id ?? '';
  const candidateType = queueEntry?.candidate_type ?? '';
  const queueEntryId = queueEntry?.queue_entry_id ?? '';
  const evidenceRefs = useMemo(
    () => asRefList(queueEntry?.evidence_refs, queueEntry?.evidence_summary),
    [queueEntry],
  );
  const provenanceRefs = useMemo(
    () => asRefList(queueEntry?.provenance_refs, queueEntry?.provenance_summary),
    [queueEntry],
  );
  const locatorRefs = useMemo(() => sourceLocatorRefs(queueEntry), [queueEntry]);
  const [destinationType, setDestinationType] = useState('approved_character');
  const [destinationKey, setDestinationKey] = useState('');
  const [ownerActorId, setOwnerActorId] = useState('owner-001');
  const [ownerActorLabel, setOwnerActorLabel] = useState('Owner');
  const [ownerNote, setOwnerNote] = useState('');
  const [ownerConfirmation, setOwnerConfirmation] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  const trimmedDestinationKey = compactString(destinationKey);
  const destinationPath = trimmedDestinationKey
    ? `memory/${DESTINATION_FOLDER[destinationType]}/${trimmedDestinationKey}.json`
    : '';

  const unavailableReason = useMemo(() => {
    if (!isSafeReviewRouteId(projectId)) {
      return 'Apply-promotion unavailable: project_id is missing or unsafe.';
    }
    if (!isSafeReviewRouteId(candidateId)) {
      return 'Apply-promotion unavailable: candidate_id is missing.';
    }
    if (!candidateType) {
      return 'Apply-promotion unavailable: candidate_type is missing.';
    }
    if (!APPLY_PROMOTION_DESTINATION_TYPES.includes(destinationType)) {
      return 'Apply-promotion unavailable: unsupported destination_type.';
    }
    if (!isSafeReviewRouteId(trimmedDestinationKey)) {
      return 'Apply-promotion unavailable: destination_key is required.';
    }
    if (evidenceRefs.length === 0) {
      return 'Apply-promotion unavailable: evidence_refs are required.';
    }
    if (provenanceRefs.length === 0) {
      return 'Apply-promotion unavailable: provenance_refs are required.';
    }
    if (locatorRefs.length === 0) {
      return 'Apply-promotion unavailable: source_locator_refs are required.';
    }
    if (!isSafeReviewRouteId(compactString(ownerActorId))) {
      return 'Apply-promotion unavailable: owner actor is required.';
    }
    if (disabled) {
      return 'Apply-promotion unavailable while review queue data is loading.';
    }
    return '';
  }, [
    candidateId,
    candidateType,
    destinationType,
    disabled,
    evidenceRefs.length,
    locatorRefs.length,
    ownerActorId,
    projectId,
    provenanceRefs.length,
    trimmedDestinationKey,
  ]);
  const submitDisabled = Boolean(unavailableReason) || !ownerConfirmation || isSubmitting;

  async function handleSubmit(event) {
    event.preventDefault();
    setResult('');
    setError('');

    if (submitDisabled) {
      setError(unavailableReason || 'Final owner confirmation is required before apply-promotion.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await submitApplyPromotion(projectId, {
        candidate_id: candidateId,
        queue_entry_id: queueEntryId,
        candidate_type: candidateType,
        owner_actor_id: compactString(ownerActorId),
        owner_actor_label: compactString(ownerActorLabel),
        owner_confirmation: true,
        owner_note: compactString(ownerNote),
        destination_type: destinationType,
        destination_path: destinationPath,
        destination_key: trimmedDestinationKey,
        evidence_refs: evidenceRefs,
        provenance_refs: provenanceRefs,
        source_locator_refs: locatorRefs,
        source_candidate_snapshot_hash: compactString(queueEntry?.source_candidate_snapshot_hash),
        requested_at: new Date().toISOString(),
      });
      setResult(formatPromotionResult(response));
      setOwnerConfirmation(false);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Apply-promotion failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="apply-promotion-confirmation" aria-label="Apply-promotion confirmation">
      <div className="review-boundary-note">
        Apply-promotion is the only approved memory/canon mutation path. This is a
        candidate-only, no-canon confirmation surface: queue presence is not approval,
        confidence is not truth, candidate persistence is not canon, and raw artifacts are support data, not canon.
        apply-promotion is explicit/audited/owner-confirmed and requires explicit owner confirmation.
      </div>

      <dl className="omi-provenance-grid" data-testid="ux2-promotion-audit-evidence">
        <div>
          <dt>evidence_refs</dt>
          <dd>{formatValue(evidenceRefs)}</dd>
        </div>
        <div>
          <dt>provenance_refs</dt>
          <dd>{formatValue(provenanceRefs)}</dd>
        </div>
        <div>
          <dt>source_locator_refs</dt>
          <dd>{formatValue(locatorRefs)}</dd>
        </div>
      </dl>

      {unavailableReason && (
        <p className="error-copy" role="alert">
          {unavailableReason}
        </p>
      )}

      <form className="apply-promotion-form" onSubmit={handleSubmit}>
        <label className="field-label" htmlFor="apply-promotion-destination-type">
          Destination
          <select
            id="apply-promotion-destination-type"
            className="field-input"
            value={destinationType}
            onChange={(event) => {
              setDestinationType(event.target.value);
              setOwnerConfirmation(false);
            }}
            disabled={disabled || isSubmitting}
          >
            {APPLY_PROMOTION_DESTINATION_TYPES.map((type) => (
              <option key={type} value={type}>
                {DESTINATION_LABELS[type]}
              </option>
            ))}
          </select>
        </label>

        <label className="field-label" htmlFor="apply-promotion-destination-key">
          Destination key
          <input
            id="apply-promotion-destination-key"
            className="field-input"
            value={destinationKey}
            onChange={(event) => {
              setDestinationKey(event.target.value);
              setOwnerConfirmation(false);
            }}
            disabled={disabled || isSubmitting}
          />
        </label>

        <label className="field-label" htmlFor="apply-promotion-owner-actor">
          Owner actor id
          <input
            id="apply-promotion-owner-actor"
            className="field-input"
            value={ownerActorId}
            onChange={(event) => {
              setOwnerActorId(event.target.value);
              setOwnerConfirmation(false);
            }}
            disabled={disabled || isSubmitting}
          />
        </label>

        <label className="field-label" htmlFor="apply-promotion-owner-label">
          Owner label
          <input
            id="apply-promotion-owner-label"
            className="field-input"
            value={ownerActorLabel}
            onChange={(event) => setOwnerActorLabel(event.target.value)}
            disabled={disabled || isSubmitting}
          />
        </label>

        <label className="field-label" htmlFor="apply-promotion-owner-note">
          Owner note
          <textarea
            id="apply-promotion-owner-note"
            className="context-textarea owner-action-note"
            value={ownerNote}
            onChange={(event) => setOwnerNote(event.target.value)}
            disabled={disabled || isSubmitting}
          />
        </label>

        <p className="context-note">
          destination_path preview: {destinationPath || 'Select a destination key'}
        </p>

        <label
          className="omi-checkbox-row"
          data-testid="ux2-apply-promotion-owner-confirmation"
        >
          <input
            type="checkbox"
            checked={ownerConfirmation}
            onChange={(event) => setOwnerConfirmation(event.target.checked)}
            disabled={Boolean(unavailableReason) || isSubmitting}
          />
          I am the owner and I give final owner confirmation to call apply-promotion.
        </label>

        <button className="primary-button" type="submit" disabled={submitDisabled}>
          {isSubmitting ? 'Applying...' : 'Apply promotion'}
        </button>
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
