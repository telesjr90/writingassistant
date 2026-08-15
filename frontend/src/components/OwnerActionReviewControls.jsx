import { useEffect, useMemo, useState } from 'react';
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
  'needs_info',
  'rejected',
  'deferred',
  'duplicate',
  'superseded',
  'archived',
];

function formatResponseSummary(response) {
  if (!response) {
    return '';
  }

  const status = response.status ?? 'accepted';
  const actionType = response.action_command ?? 'review action';
  const version = response.review_version ?? 'not recorded';
  const completion = response.owner_review_completed
    ? `completed at ${response.owner_reviewed_at ?? 'an unrecorded time'}`
    : 'not completed';
  const note = response.owner_note ?? 'not recorded';
  return `${status}: ${actionType}. Persisted review workflow version ${version}; review workflow ${completion}; owner note: ${note}. Not canon.`;
}

function buildLogicalCommand({
  actionType,
  queueEntryId,
  candidateId,
  currentReviewStatus,
  currentReviewVersion,
  ownerNote,
  rationale,
  reviewStatus,
  duplicateCandidateIds,
  supersededByCandidateId,
  rejectedOutputReason,
  insufficientEvidenceReason,
  quarantineNote,
}) {
  const command = {
    actionType,
    queueEntryId,
    candidateId,
    expectedCurrentReviewStatus: currentReviewStatus,
    expectedCurrentVersion: currentReviewVersion,
  };

  if (actionType === 'update_owner_note' || ownerNote !== '') {
    command.ownerNote = ownerNote;
  }
  if (rationale !== '') {
    command.rationale = rationale;
  }
  if (actionType === 'set_review_status') {
    command.targetReviewStatus = reviewStatus;
  }
  if (actionType === 'set_review_status' && reviewStatus === 'duplicate' && duplicateCandidateIds !== '') {
    command.duplicateCandidateIds = duplicateCandidateIds.split('\n');
  }
  if (actionType === 'set_review_status' && reviewStatus === 'superseded' && supersededByCandidateId !== '') {
    command.supersededByCandidateId = supersededByCandidateId;
  }
  if (
    (actionType === 'reject' || (actionType === 'set_review_status' && reviewStatus === 'rejected'))
    && rejectedOutputReason !== ''
  ) {
    command.rejectedOutputReason = rejectedOutputReason;
  }
  if (
    (actionType === 'request_more_evidence'
      || (actionType === 'set_review_status' && reviewStatus === 'needs_info'))
    && insufficientEvidenceReason !== ''
  ) {
    command.insufficientEvidenceReason = insufficientEvidenceReason;
  }
  if (actionType === 'quarantine' && quarantineNote !== '') {
    command.quarantineNote = quarantineNote;
  }

  return command;
}

function semanticCommandMatches(formState, pendingLogicalCommand) {
  if (!pendingLogicalCommand) {
    return false;
  }
  const { idempotencyKey: _idempotencyKey, ...capturedCommand } = pendingLogicalCommand;
  return JSON.stringify(formState) === JSON.stringify(capturedCommand);
}

function validateLogicalCommand(command) {
  const requiresOwnerNote = [
    'request_more_evidence',
    'defer',
    'reject',
    'quarantine',
  ].includes(command.actionType) || (
    command.actionType === 'set_review_status'
    && ['needs_info', 'rejected', 'deferred', 'duplicate', 'superseded']
      .includes(command.targetReviewStatus)
  );

  if (requiresOwnerNote && command.ownerNote === undefined) {
    return 'This review workflow command requires an owner note.';
  }
  if (
    command.actionType === 'set_review_status'
    && command.targetReviewStatus === 'duplicate'
    && command.duplicateCandidateIds === undefined
  ) {
    return 'Duplicate status requires at least one candidate ID.';
  }
  if (
    command.actionType === 'set_review_status'
    && command.targetReviewStatus === 'superseded'
    && command.supersededByCandidateId === undefined
  ) {
    return 'Superseded status requires the superseding candidate ID.';
  }
  return '';
}

export default function OwnerActionReviewControls({
  projectId,
  queueEntry,
  disabled = false,
  onSubmitAction,
  onRefreshQueue,
}) {
  const queueEntryId = queueEntry?.queue_entry_id ?? '';
  const candidateId = queueEntry?.candidate_record_id ?? queueEntry?.candidate_id ?? '';
  const [actionType, setActionType] = useState('mark_reviewed');
  const [ownerNote, setOwnerNote] = useState('');
  const [rationale, setRationale] = useState('');
  const [reviewStatus, setReviewStatus] = useState('pending');
  const [duplicateCandidateIds, setDuplicateCandidateIds] = useState('');
  const [supersededByCandidateId, setSupersededByCandidateId] = useState('');
  const [rejectedOutputReason, setRejectedOutputReason] = useState('');
  const [insufficientEvidenceReason, setInsufficientEvidenceReason] = useState('');
  const [quarantineNote, setQuarantineNote] = useState('');
  const [ownerConfirmed, setOwnerConfirmed] = useState(false);
  const [pendingLogicalCommand, setPendingLogicalCommand] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [errorStatus, setErrorStatus] = useState(null);

  function clearPendingLogicalCommand() {
    setPendingLogicalCommand(null);
  }

  useEffect(() => {
    clearPendingLogicalCommand();
    setOwnerConfirmed(false);
  }, [
    candidateId,
    queueEntryId,
    queueEntry?.review_status,
    queueEntry?.review_version,
  ]);

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

  const operationInFlight = isSubmitting || isRefreshing;
  const submitDisabled = Boolean(controlsUnavailableReason) || !ownerConfirmed || operationInFlight;
  const showsRejectedReason = actionType === 'reject'
    || (actionType === 'set_review_status' && reviewStatus === 'rejected');
  const showsInsufficientEvidenceReason = actionType === 'request_more_evidence'
    || (actionType === 'set_review_status' && reviewStatus === 'needs_info');

  function handleSemanticEdit(setter, value) {
    clearPendingLogicalCommand();
    setResult('');
    setError('');
    setErrorStatus(null);
    setOwnerConfirmed(false);
    setter(value);
  }

  function currentSemanticCommand() {
    return buildLogicalCommand({
      actionType,
      queueEntryId,
      candidateId,
      currentReviewStatus: queueEntry?.review_status,
      currentReviewVersion: queueEntry?.review_version,
      ownerNote,
      rationale,
      reviewStatus,
      duplicateCandidateIds,
      supersededByCandidateId,
      rejectedOutputReason,
      insufficientEvidenceReason,
      quarantineNote,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setResult('');
    setError('');
    setErrorStatus(null);

    if (submitDisabled || !onSubmitAction) {
      setError(controlsUnavailableReason || 'Explicit owner confirmation is required.');
      return;
    }

    const semanticCommand = currentSemanticCommand();
    const validationError = validateLogicalCommand(semanticCommand);
    if (validationError) {
      setError(validationError);
      return;
    }

    const logicalCommand = semanticCommandMatches(semanticCommand, pendingLogicalCommand)
      ? pendingLogicalCommand
      : { ...semanticCommand, idempotencyKey: crypto.randomUUID() };
    setPendingLogicalCommand(logicalCommand);
    setIsSubmitting(true);

    try {
      const response = await onSubmitAction(logicalCommand);
      clearPendingLogicalCommand();
      setResult(formatResponseSummary(response));
      setOwnerConfirmed(false);
    } catch (submitError) {
      const message = submitError instanceof Error
        ? submitError.message
        : 'Owner review action failed.';
      const status = Number.isInteger(submitError?.status) ? submitError.status : null;
      let guidance = 'Retry this same logical command; its recovery key has been retained.';
      if (status === 409) {
        guidance = 'Authoritative queue refresh is required before creating a new logical command.';
      } else if (status === 423) {
        guidance = 'The review entry is busy. Retry this same logical command; its recovery key has been retained.';
      } else if (status === 500 && submitError?.manualRecoveryRequired) {
        guidance = 'Manual recovery is required. Keep this logical command and its recovery key for the authorized recovery path.';
      }
      setError(`${message} ${guidance}`);
      setErrorStatus(status);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleCancelPendingCommand() {
    clearPendingLogicalCommand();
    setOwnerConfirmed(false);
    setError('');
    setErrorStatus(null);
    setResult('Pending logical command cancelled. The next submission will use a new recovery key.');
  }

  async function handleAuthoritativeRefresh() {
    if (!onRefreshQueue) {
      return;
    }
    setIsRefreshing(true);
    setResult('');
    try {
      await onRefreshQueue();
      clearPendingLogicalCommand();
      setOwnerConfirmed(false);
      setError('');
      setErrorStatus(null);
      setResult('Authoritative queue refreshed. Review the persisted state before confirming a new logical command.');
    } catch (refreshError) {
      setError(
        refreshError instanceof Error
          ? refreshError.message
          : 'Authoritative review queue refresh failed.',
      );
    } finally {
      setIsRefreshing(false);
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
            onChange={(event) => handleSemanticEdit(setActionType, event.target.value)}
            disabled={disabled || operationInFlight}
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
              onChange={(event) => handleSemanticEdit(setReviewStatus, event.target.value)}
              disabled={disabled || operationInFlight}
            >
              {REVIEW_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
        )}

        <label className="field-label" htmlFor="owner-review-note">
          Owner note
          <textarea
            id="owner-review-note"
            className="context-textarea owner-action-note"
            value={ownerNote}
            onChange={(event) => handleSemanticEdit(setOwnerNote, event.target.value)}
            disabled={disabled || operationInFlight}
          />
        </label>

        <label className="field-label" htmlFor="owner-review-rationale">
          Command rationale
          <input
            id="owner-review-rationale"
            className="field-input"
            value={rationale}
            onChange={(event) => handleSemanticEdit(setRationale, event.target.value)}
            disabled={disabled || operationInFlight}
          />
        </label>

        {showsInsufficientEvidenceReason && (
          <label className="field-label" htmlFor="owner-review-insufficient-evidence-reason">
            Insufficient evidence reason
            <textarea
              id="owner-review-insufficient-evidence-reason"
              className="context-textarea owner-action-note"
              value={insufficientEvidenceReason}
              onChange={(event) => handleSemanticEdit(
                setInsufficientEvidenceReason,
                event.target.value,
              )}
              disabled={disabled || operationInFlight}
            />
          </label>
        )}

        {showsRejectedReason && (
          <label className="field-label" htmlFor="owner-review-rejected-output-reason">
            Rejected output reason
            <textarea
              id="owner-review-rejected-output-reason"
              className="context-textarea owner-action-note"
              value={rejectedOutputReason}
              onChange={(event) => handleSemanticEdit(setRejectedOutputReason, event.target.value)}
              disabled={disabled || operationInFlight}
            />
          </label>
        )}

        {actionType === 'quarantine' && (
          <label className="field-label" htmlFor="owner-review-quarantine-note">
            Quarantine note
            <textarea
              id="owner-review-quarantine-note"
              className="context-textarea owner-action-note"
              value={quarantineNote}
              onChange={(event) => handleSemanticEdit(setQuarantineNote, event.target.value)}
              disabled={disabled || operationInFlight}
            />
          </label>
        )}

        {actionType === 'set_review_status' && reviewStatus === 'duplicate' && (
          <label className="field-label" htmlFor="owner-review-duplicate-candidate-ids">
            Duplicate candidate IDs (one per line)
            <textarea
              id="owner-review-duplicate-candidate-ids"
              className="context-textarea owner-action-note"
              value={duplicateCandidateIds}
              onChange={(event) => handleSemanticEdit(setDuplicateCandidateIds, event.target.value)}
              disabled={disabled || operationInFlight}
            />
          </label>
        )}

        {actionType === 'set_review_status' && reviewStatus === 'superseded' && (
          <label className="field-label" htmlFor="owner-review-superseding-candidate-id">
            Superseding candidate ID
            <input
              id="owner-review-superseding-candidate-id"
              className="field-input"
              value={supersededByCandidateId}
              onChange={(event) => handleSemanticEdit(setSupersededByCandidateId, event.target.value)}
              disabled={disabled || operationInFlight}
            />
          </label>
        )}

        <label className="omi-checkbox-row">
          <input
            type="checkbox"
            checked={ownerConfirmed}
            onChange={(event) => setOwnerConfirmed(event.target.checked)}
            disabled={Boolean(controlsUnavailableReason) || operationInFlight}
          />
          I am the owner and I explicitly confirm this bounded review workflow command.
        </label>

        <button className="primary-button" type="submit" disabled={submitDisabled}>
          {isSubmitting ? 'Sending...' : 'Send owner review command'}
        </button>

        {pendingLogicalCommand && !operationInFlight && (
          <button
            className="secondary-button"
            type="button"
            onClick={handleCancelPendingCommand}
          >
            Cancel pending command
          </button>
        )}
      </form>

      {result && <p className="context-note">{result}</p>}
      {error && (
        <div className="error-copy" role="alert">
          <p>{error}</p>
          {errorStatus === 409 && onRefreshQueue && (
            <button
              className="secondary-button"
              type="button"
              onClick={handleAuthoritativeRefresh}
              disabled={operationInFlight}
            >
              {isRefreshing ? 'Refreshing...' : 'Refresh authoritative queue'}
            </button>
          )}
        </div>
      )}
    </section>
  );
}
