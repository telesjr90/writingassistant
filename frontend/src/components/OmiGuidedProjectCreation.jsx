import { useMemo, useRef, useState } from 'react';

const STEPS = {
  SETUP: 'setup',
  REVIEW: 'review',
};

const INITIAL_DRAFT = {
  projectTitle: '',
  rawIdea: '',
  setupNotes: '',
};

function getReviewDraft(draft) {
  return {
    projectTitle: draft.projectTitle.trim(),
    rawIdea: draft.rawIdea,
    setupNotes: draft.setupNotes,
  };
}

function safeRecoveryProjectId(value) {
  return typeof value === 'string' && /^[a-z0-9][a-z0-9_-]{0,63}$/.test(value)
    ? value
    : '';
}

export function getGuidedCreationFailureMessage(error) {
  const payload = error?.payload;

  if (payload?.status === 'failed_rolled_back') {
    return 'Guided creation failed, and the incomplete project was removed. Your setup is still available to edit and retry.';
  }

  if (payload?.status === 'recovery_required') {
    const projectId = safeRecoveryProjectId(payload.project_id);
    const projectReference = projectId ? ` Project identifier: ${projectId}.` : '';
    return `Recovery required: guided creation did not complete cleanly.${projectReference} Do not use this project until an owner has inspected and recovered it.`;
  }

  if (error?.code === 'malformed_guided_creation_response') {
    return 'Guided creation returned an incomplete response. No project was opened. Review your setup and retry.';
  }

  if (error?.code === 'guided_creation_cancelled') {
    return 'Guided project creation was cancelled. Your setup was preserved.';
  }

  if (error?.status === 400) {
    return 'Guided creation was rejected. Check the project title and enter a non-blank setup idea.';
  }

  if (error?.status === 409) {
    return 'A conflicting project already exists. Review the title and retry.';
  }

  if (error?.status == null && error?.name === 'OmiGuidedProjectCreationError') {
    return 'Could not reach guided project creation. Check the local service and retry.';
  }

  return 'Guided project creation failed. Your setup was preserved; review it and retry.';
}

function previewProjectId(title) {
  const normalized = title
    .trim()
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64)
    .replace(/^-+|-+$/g, '');

  return normalized || 'Preview after confirmation';
}

export default function OmiGuidedProjectCreation({
  onCreateGuidedProject,
  onCancel,
  onComplete,
  disabled = false,
}) {
  const [draft, setDraft] = useState(INITIAL_DRAFT);
  const [step, setStep] = useState(STEPS.SETUP);
  const [finalConfirmation, setFinalConfirmation] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [failureMessage, setFailureMessage] = useState('');
  const submissionPendingRef = useRef(false);
  const reviewDraft = useMemo(() => getReviewDraft(draft), [draft]);
  const projectIdPreview = previewProjectId(reviewDraft.projectTitle);
  const canReview = Boolean(reviewDraft.projectTitle && draft.rawIdea.trim());
  const canCreate = canReview && finalConfirmation && !disabled && !isSubmitting;

  function updateDraft(fieldName, value) {
    setDraft((currentDraft) => ({
      ...currentDraft,
      [fieldName]: value,
    }));
    setFinalConfirmation(false);
  }

  function resetDraft() {
    setDraft(INITIAL_DRAFT);
    setStep(STEPS.SETUP);
    setFinalConfirmation(false);
    setFailureMessage('');
  }

  function handleCancel() {
    resetDraft();
    onCancel?.();
  }

  function handleReview(event) {
    event.preventDefault();

    if (!canReview) {
      return;
    }

    setStep(STEPS.REVIEW);
  }

  async function handleFinalCreate(event) {
    event.preventDefault();

    if (
      !canCreate
      || submissionPendingRef.current
      || typeof onCreateGuidedProject !== 'function'
    ) {
      return;
    }

    submissionPendingRef.current = true;
    setIsSubmitting(true);
    setFailureMessage('');

    try {
      const result = await onCreateGuidedProject({
        title: reviewDraft.projectTitle,
        rawIdea: draft.rawIdea,
        setupNotes: draft.setupNotes,
      });

      if (result?.success !== true) {
        const error = new Error('Guided creation did not return verified completion.');
        error.code = 'malformed_guided_creation_response';
        throw error;
      }

      resetDraft();
      onComplete?.(result);
    } catch (error) {
      setFailureMessage(getGuidedCreationFailureMessage(error));
    } finally {
      submissionPendingRef.current = false;
      setIsSubmitting(false);
    }
  }

  return (
    <section className="omi-guided-project-creation" aria-label="OMI-guided project setup">
      <div className="panel-header">
        <p className="eyebrow">Setup draft</p>
        <h2>OMI-guided project setup</h2>
      </div>
      <p className="muted-copy">
        Owner-authored setup only. Candidate planning data stays not approved project
        truth, not canon, and not memory.
      </p>

      {failureMessage ? <p className="error-text" role="alert">{failureMessage}</p> : null}
      {isSubmitting ? <p className="muted-copy" role="status">Creating guided project...</p> : null}

      {step === STEPS.SETUP ? (
        <form onSubmit={handleReview} aria-label="Owner-authored setup input">
          <label className="project-select-label">
            <span className="muted-copy">Project title</span>
            <input
              className="project-title-input"
              type="text"
              value={draft.projectTitle}
              onChange={(event) => updateDraft('projectTitle', event.target.value)}
              placeholder="Owner project title"
              disabled={disabled}
              aria-label="OMI-guided project title"
            />
          </label>

          <label className="project-select-label">
            <span className="muted-copy">Owner-authored setup idea</span>
            <textarea
              value={draft.rawIdea}
              onChange={(event) => updateDraft('rawIdea', event.target.value)}
              placeholder="Owner-authored setup idea"
              disabled={disabled}
              aria-label="Owner-authored setup idea"
            />
          </label>

          <label className="project-select-label">
            <span className="muted-copy">Owner-authored setup notes</span>
            <textarea
              value={draft.setupNotes}
              onChange={(event) => updateDraft('setupNotes', event.target.value)}
              placeholder="Optional owner-authored setup notes"
              disabled={disabled}
              aria-label="Owner-authored setup notes"
            />
          </label>

          <div className="scene-item" aria-label="Setup candidate labels">
            <span>Setup candidate</span>
            <small>Candidate planning data, not approved project truth</small>
          </div>

          <div className="button-row">
            <button type="submit" disabled={!canReview || disabled}>
              Review before creating project
            </button>
            <button type="button" onClick={handleCancel} disabled={disabled}>
              Cancel setup draft
            </button>
          </div>
        </form>
      ) : (
        <form onSubmit={handleFinalCreate} aria-label="Review setup draft">
          <dl className="project-overview-list">
            <div>
              <dt>Project title</dt>
              <dd>{reviewDraft.projectTitle}</dd>
            </div>
            <div>
              <dt>Project ID preview</dt>
              <dd>{projectIdPreview}</dd>
            </div>
            <div>
              <dt>Setup draft</dt>
              <dd>{reviewDraft.rawIdea || 'No owner-authored setup idea entered.'}</dd>
            </div>
            <div>
              <dt>Candidate planning data</dt>
              <dd>{reviewDraft.setupNotes || 'No owner-authored setup notes entered.'}</dd>
            </div>
          </dl>

          <label className="project-select-label">
            <input
              type="checkbox"
              checked={finalConfirmation}
              onChange={(event) => setFinalConfirmation(event.target.checked)}
              disabled={disabled || isSubmitting}
            />
            <span>
              I confirm this owner-authored setup can create a project through the
              dedicated guided project creation path.
            </span>
          </label>

          <div className="button-row">
            <button type="submit" disabled={!canCreate}>
              {isSubmitting ? 'Creating guided project...' : 'Create guided project'}
            </button>
            <button
              type="button"
              onClick={() => {
                setStep(STEPS.SETUP);
                setFinalConfirmation(false);
              }}
              disabled={disabled || isSubmitting}
            >
              Back to setup draft
            </button>
            <button type="button" onClick={handleCancel} disabled={disabled || isSubmitting}>
              Cancel setup draft
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
