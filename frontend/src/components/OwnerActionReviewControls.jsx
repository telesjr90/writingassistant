import { useMemo, useState } from 'react';
import {
  REVIEW_ACTION_TYPES,
  isSafeReviewRouteId,
} from '../api.js';

const ACTION_LABELS = {
  mark_reviewed: 'Mark reviewed',
  request_more_evidence: 'Request more evidence',
  defer: 'Defer',
  reject: 'Reject',
  quarantine: 'Quarantine',
  update_owner_note: 'Update owner note',
  set_review_status: 'Set review status',
};

const REVIEW_STATUSES = [
  'pending',
  'reviewed',
  'needs_more_evidence',
  'deferred',
  'rejected',
  'quarantined',
];

function formatResponseSummary(response) {
  if (!response) {
    return '';
  }

  const status = response.status ?? 'accepted';
  const actionType = response.action_type ?? 'review action';
  return `${status}: ${actionType}. Review workflow response only; not canon.`;
}

export default function OwnerActionReviewControls({
  projectId,
  queueEntry,
  disabled = false,
  onSubmitAction,
}) {
  const queueEntryId = queueEntry?.queue_entry_id ?? '';
  const candidateId = queueEntry?.candidate_record_id ?? queueEntry?.candidate_id ?? '';
  const [actionType, setActionType] = useState('mark_reviewed');
  const [ownerNote, setOwnerNote] = useState('');
  const [rationale, setRationale] = useState('');
  const [reviewStatus, setReviewStatus] = useState('reviewed');
  const [ownerConfirmed, setOwnerConfirmed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  const controlsUnavailableReason = useMemo(() => {
    if (!isSafeReviewRouteId(projectId)) {
      return 'Owner action controls unavailable: project_id is missing or unsafe.';
    }
    if (!isSafeReviewRouteId(queueEntryId)) {
      return 'Owner action controls unavailable: queue_entry_id is missing or unsafe.';
    }
    if (!isSafeReviewRouteId(candidateId)) {
      return 'Owner action controls unavailable: candidate_id is missing or unsafe.';
    }
    if (!REVIEW_ACTION_TYPES.includes(actionType)) {
      return 'Owner action controls unavailable: unsupported command.';
    }
    if (disabled) {
      return 'Owner action controls unavailable while review queue data is loading.';
    }
    return '';
  }, [actionType, candidateId, disabled, projectId, queueEntryId]);

  const noteRelevant = [
    'request_more_evidence',
    'defer',
    'reject',
    'quarantine',
    'update_owner_note',
    'set_review_status',
  ].includes(actionType);
  const submitDisabled = Boolean(controlsUnavailableReason) || !ownerConfirmed || isSubmitting;

  async function handleSubmit(event) {
    event.preventDefault();
    setResult('');
    setError('');

    if (submitDisabled || !onSubmitAction) {
      setError(controlsUnavailableReason || 'Explicit owner confirmation is required.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await onSubmitAction({
        actionType,
        ownerNote,
        rationale,
        reviewStatus,
        queueEntryId,
        candidateId,
        expectedCurrentReviewStatus: queueEntry?.review_status,
        expectedCurrentVersion: queueEntry?.version,
      });
      setResult(formatResponseSummary(response));
      setOwnerConfirmed(false);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Owner review action failed.',
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="owner-action-controls" aria-label="Owner review action controls">
      <div className="review-boundary-note">
        Explicit owner commands update review workflow state only. They do not change canon,
        memory, project truth, or owner-authored prose.
      </div>

      {controlsUnavailableReason && (
        <p className="error-copy" role="alert">
          {controlsUnavailableReason}
        </p>
      )}

      <form className="owner-action-form" onSubmit={handleSubmit}>
        <label className="field-label" htmlFor="owner-review-action-type">
          Owner action
          <select
            id="owner-review-action-type"
            className="field-input"
            value={actionType}
            onChange={(event) => {
              setActionType(event.target.value);
              setOwnerConfirmed(false);
            }}
            disabled={disabled || isSubmitting}
          >
            {REVIEW_ACTION_TYPES.map((type) => (
              <option key={type} value={type}>
                {ACTION_LABELS[type]}
              </option>
            ))}
          </select>
        </label>

        {actionType === 'set_review_status' && (
          <label className="field-label" htmlFor="owner-review-status">
            Review status
            <select
              id="owner-review-status"
              className="field-input"
              value={reviewStatus}
              onChange={(event) => setReviewStatus(event.target.value)}
              disabled={disabled || isSubmitting}
            >
              {REVIEW_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
        )}

        {noteRelevant && (
          <label className="field-label" htmlFor="owner-review-note">
            Owner note / rationale
            <textarea
              id="owner-review-note"
              className="context-textarea owner-action-note"
              value={ownerNote}
              onChange={(event) => setOwnerNote(event.target.value)}
              disabled={disabled || isSubmitting}
            />
          </label>
        )}

        <label className="field-label" htmlFor="owner-review-rationale">
          Command rationale
          <input
            id="owner-review-rationale"
            className="field-input"
            value={rationale}
            onChange={(event) => setRationale(event.target.value)}
            disabled={disabled || isSubmitting}
          />
        </label>

        <label className="omi-checkbox-row">
          <input
            type="checkbox"
            checked={ownerConfirmed}
            onChange={(event) => setOwnerConfirmed(event.target.checked)}
            disabled={Boolean(controlsUnavailableReason) || isSubmitting}
          />
          I am the owner and I explicitly confirm this bounded review workflow command.
        </label>

        <button className="primary-button" type="submit" disabled={submitDisabled}>
          {isSubmitting ? 'Sending...' : 'Send owner review command'}
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
