function getStatusClass(status) {
  if (status.startsWith('Save failed') || status.startsWith('Invalid')) {
    return 'context-status is-error';
  }

  if (status === 'Unsaved changes') {
    return 'context-status is-unsaved';
  }

  if (status.startsWith('Failed to load') || status.startsWith('Availability could not')) {
    return 'context-status is-error';
  }

  return 'context-status';
}

function getResourceReadinessLabel(readinessState, readinessReason, directError) {
  if (directError) {
    return 'Load failed';
  }
  if (readinessState === 'loading') {
    return 'Checking availability...';
  }
  if (readinessState === 'error') {
    return 'Availability could not be checked.';
  }
  if (readinessState === 'absent') {
    return 'Not stored';
  }
  if (readinessState === 'invalid') {
    return 'Invalid';
  }
  if (readinessState === 'unavailable') {
    return 'Unavailable';
  }
  if (readinessState === 'ready') {
    return 'Available';
  }
  return '';
}

function getResourceReadinessReason(readinessState, readinessReason) {
  if (readinessState === 'invalid' && readinessReason) {
    return readinessReason;
  }
  if (readinessState === 'unavailable' && readinessReason) {
    return readinessReason;
  }
  return '';
}

function ContextJsonEditor({
  label,
  value,
  status,
  isSaving,
  onChange,
  onSave,
  readinessState,
  directError,
  readOnly,
}) {
  const displayedStatus = isSaving ? 'Saving...' : status;
  const readOnlyMode = readOnly || readinessState === 'invalid' || readinessState === 'unavailable' || readinessState === 'error' || !!directError;

  return (
    <section className="context-editor">
      <header className="context-editor-header">
        <h3>{label}</h3>
        <div className="context-actions">
          {displayedStatus && (
            <span className={getStatusClass(displayedStatus)}>{displayedStatus}</span>
          )}
          <button
            type="button"
            disabled={isSaving || readOnlyMode}
            onClick={onSave}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </header>
      <textarea
        className="context-textarea"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        spellCheck="false"
        aria-label={`${label} JSON`}
        readOnly={readOnlyMode}
      />
    </section>
  );
}

export default function ProjectContext({
  bibleText,
  bibleStatus,
  isSavingBible,
  onBibleChange,
  onSaveBible,
  storyformText,
  storyformStatus,
  isSavingStoryform,
  onStoryformChange,
  onSaveStoryform,
  storyformContext,
  bibleReadinessState = 'loading',
  bibleReadinessReason = '',
  bibleDirectError = '',
  storyformReadinessState = 'loading',
  storyformReadinessReason = '',
  storyformDirectError = '',
  storyformContextReadinessState = 'loading',
  storyformContextReadinessReason = '',
  storyformContextDirectError = '',
  readinessError = '',
  isLoadingReadiness = false,
  isRetryingReadiness = false,
  onRetryReadiness = () => {},
}) {
  const hasReadinessError = readinessError && !isRetryingReadiness;
  const hasDirectError = (
    bibleDirectError
    || storyformDirectError
    || storyformContextDirectError
  );
  const showRetry = (
    bibleReadinessState === 'error'
    || storyformReadinessState === 'error'
    || hasReadinessError
    || hasDirectError
  );

  function storyformContextDisplay() {
    if (storyformContextReadinessState === 'loading') {
      return 'Checking context availability...';
    }
    if (storyformContextReadinessState === 'error') {
      return 'Storyform context availability could not be checked.';
    }
    if (storyformContextReadinessState === 'absent') {
      return 'No storyform context available.';
    }
    if (storyformContextReadinessState === 'invalid') {
      return 'Storyform context is not available.';
    }
    if (storyformContextDirectError) {
      return `Failed to load storyform context: ${storyformContextDirectError}`;
    }
    if (storyformContextReadinessState === 'unavailable') {
      if (storyformContextReadinessReason) {
        return `Storyform context is not available (${storyformContextReadinessReason}).`;
      }
      return 'Storyform context is not available.';
    }
    return storyformContext || 'No storyform context available.';
  }

  return (
    <section className="project-context" aria-label="Editable project context">
      <header className="context-header">
        <div>
          <p className="eyebrow">Project Context</p>
          <h2>Owner-Approved Context</h2>
        </div>
        <p className="context-note">
          Analysis output does not automatically overwrite this context.
        </p>
      </header>

      {hasReadinessError && (
        <div className="context-status is-error" role="alert">
          <p>
            Context availability check failed: {readinessError}
          </p>
        </div>
      )}

      {showRetry && (
        <div className="context-actions" style={{ marginBottom: '1rem' }}>
          <button
            type="button"
            disabled={isRetryingReadiness}
            onClick={onRetryReadiness}
          >
            {isRetryingReadiness ? 'Retrying...' : 'Retry'}
          </button>
        </div>
      )}

      <div className="context-grid">
        <ContextJsonEditor
          label="Bible JSON"
          value={bibleText}
          status={bibleStatus}
          isSaving={isSavingBible}
          onChange={onBibleChange}
          onSave={onSaveBible}
          readinessState={bibleReadinessState}
          directError={bibleDirectError}
          readOnly={bibleReadinessState !== 'ready' && bibleReadinessState !== 'absent' || !!bibleDirectError}
        />
        <ContextJsonEditor
          label="Storyform JSON"
          value={storyformText}
          status={storyformStatus}
          isSaving={isSavingStoryform}
          onChange={onStoryformChange}
          onSave={onSaveStoryform}
          readinessState={storyformReadinessState}
          directError={storyformDirectError}
          readOnly={storyformReadinessState !== 'ready' && storyformReadinessState !== 'absent' || !!storyformDirectError}
        />
      </div>

      <details className="storyform-context">
        <summary>Storyform Prompt Context</summary>
        <pre>{storyformContextDisplay()}</pre>
      </details>
    </section>
  );
}
