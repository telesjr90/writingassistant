function getStatusClass(status) {
  if (status.startsWith('Save failed') || status.startsWith('Invalid')) {
    return 'context-status is-error';
  }

  if (status === 'Unsaved changes') {
    return 'context-status is-unsaved';
  }

  return 'context-status';
}

function ContextJsonEditor({
  label,
  value,
  status,
  isSaving,
  onChange,
  onSave,
}) {
  const displayedStatus = isSaving ? 'Saving...' : status;

  return (
    <section className="context-editor">
      <header className="context-editor-header">
        <h3>{label}</h3>
        <div className="context-actions">
          {displayedStatus && (
            <span className={getStatusClass(displayedStatus)}>{displayedStatus}</span>
          )}
          <button type="button" disabled={isSaving} onClick={onSave}>
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
}) {
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

      <div className="context-grid">
        <ContextJsonEditor
          label="Bible JSON"
          value={bibleText}
          status={bibleStatus}
          isSaving={isSavingBible}
          onChange={onBibleChange}
          onSave={onSaveBible}
        />
        <ContextJsonEditor
          label="Storyform JSON"
          value={storyformText}
          status={storyformStatus}
          isSaving={isSavingStoryform}
          onChange={onStoryformChange}
          onSave={onSaveStoryform}
        />
      </div>

      <details className="storyform-context">
        <summary>Storyform Prompt Context</summary>
        <pre>{storyformContext || 'No storyform context available.'}</pre>
      </details>
    </section>
  );
}
