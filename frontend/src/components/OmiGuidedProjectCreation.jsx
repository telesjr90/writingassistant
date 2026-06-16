import { useMemo, useState } from 'react';

const STEPS = {
  SETUP: 'setup',
  REVIEW: 'review',
};

const INITIAL_DRAFT = {
  projectTitle: '',
  rawIdea: '',
  setupNotes: '',
};

function getTrimmedDraft(draft) {
  return {
    projectTitle: draft.projectTitle.trim(),
    rawIdea: draft.rawIdea.trim(),
    setupNotes: draft.setupNotes.trim(),
  };
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
  onCreateProject,
  onCancel,
  onComplete,
  disabled = false,
}) {
  const [draft, setDraft] = useState(INITIAL_DRAFT);
  const [step, setStep] = useState(STEPS.SETUP);
  const [finalConfirmation, setFinalConfirmation] = useState(false);
  const trimmedDraft = useMemo(() => getTrimmedDraft(draft), [draft]);
  const projectIdPreview = previewProjectId(trimmedDraft.projectTitle);
  const canReview = Boolean(trimmedDraft.projectTitle);
  const canCreate = canReview && finalConfirmation && !disabled;

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

    if (!canCreate || typeof onCreateProject !== 'function') {
      return;
    }

    const created = await onCreateProject(trimmedDraft.projectTitle);

    if (created) {
      resetDraft();
      onComplete?.();
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
              <dd>{trimmedDraft.projectTitle}</dd>
            </div>
            <div>
              <dt>Project ID preview</dt>
              <dd>{projectIdPreview}</dd>
            </div>
            <div>
              <dt>Setup draft</dt>
              <dd>{trimmedDraft.rawIdea || 'No owner-authored setup idea entered.'}</dd>
            </div>
            <div>
              <dt>Candidate planning data</dt>
              <dd>{trimmedDraft.setupNotes || 'No owner-authored setup notes entered.'}</dd>
            </div>
          </dl>

          <label className="project-select-label">
            <input
              type="checkbox"
              checked={finalConfirmation}
              onChange={(event) => setFinalConfirmation(event.target.checked)}
              disabled={disabled}
            />
            <span>
              I confirm this owner-authored setup can create a project through the
              existing project creation path.
            </span>
          </label>

          <div className="button-row">
            <button type="submit" disabled={!canCreate}>
              Create project
            </button>
            <button
              type="button"
              onClick={() => {
                setStep(STEPS.SETUP);
                setFinalConfirmation(false);
              }}
              disabled={disabled}
            >
              Back to setup draft
            </button>
            <button type="button" onClick={handleCancel} disabled={disabled}>
              Cancel setup draft
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
