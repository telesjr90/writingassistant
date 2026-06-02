import { useEffect } from 'react';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function textToHtml(content) {
  if (!content.trim()) {
    return '<p></p>';
  }

  return content
    .split(/\n{2,}/)
    .map((paragraph) => `<p>${escapeHtml(paragraph).replace(/\n/g, '<br>')}</p>`)
    .join('');
}

export default function Editor({
  content,
  disabled,
  hasUnsavedChanges,
  isLoading,
  isSaving,
  onChange,
  onSave,
  saveDisabled,
  saveStatus,
  sceneError,
  selectedSceneId,
}) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: textToHtml(content),
    editable: !disabled,
    onUpdate: ({ editor: currentEditor }) => {
      onChange(currentEditor.getText({ blockSeparator: '\n\n' }));
    },
    editorProps: {
      attributes: {
        class: 'tiptap-surface',
        'aria-label': 'Scene draft editor',
      },
    },
  });

  useEffect(() => {
    if (!editor) {
      return;
    }

    const currentText = editor.getText({ blockSeparator: '\n\n' });

    if (currentText !== content) {
      editor.commands.setContent(textToHtml(content), { emitUpdate: false });
    }
  }, [content, editor]);

  useEffect(() => {
    editor?.setEditable(!disabled);
  }, [disabled, editor]);

  const title = selectedSceneId ? selectedSceneId.replace(/[-_]+/g, ' ') : 'No scene selected';
  const displayedSaveStatus = (() => {
    if (isLoading) {
      return 'Loading...';
    }

    if (isSaving) {
      return 'Saving...';
    }

    if (saveStatus.startsWith('Save failed')) {
      return saveStatus;
    }

    if (hasUnsavedChanges) {
      return 'Unsaved changes';
    }

    if (saveStatus) {
      return saveStatus;
    }

    return selectedSceneId ? 'Saved' : '';
  })();
  const saveStatusClass = displayedSaveStatus.startsWith('Save failed')
    ? 'save-status is-error'
    : `save-status${hasUnsavedChanges ? ' is-unsaved' : ''}`;

  return (
    <section className="editor-panel">
      <header className="editor-header">
        <div>
          <p className="eyebrow">Editor</p>
          <h2>{title}</h2>
        </div>
        <div className="editor-actions" aria-label="Editor actions">
          <button type="button" disabled={!editor} onClick={() => editor?.chain().focus().toggleBold().run()}>
            Bold
          </button>
          <button type="button" disabled={!editor} onClick={() => editor?.chain().focus().toggleItalic().run()}>
            Italic
          </button>
          <button type="button" disabled={saveDisabled} onClick={onSave}>
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          {displayedSaveStatus && <span className={saveStatusClass}>{displayedSaveStatus}</span>}
        </div>
      </header>

      {!selectedSceneId && <p className="editor-empty">Select a scene to begin editing.</p>}
      {selectedSceneId && sceneError && <p className="error-copy">{sceneError}</p>}
      {selectedSceneId && !isLoading && content.length === 0 && (
        <p className="muted-copy">This scene is empty. Saving an empty scene is allowed.</p>
      )}
      <EditorContent editor={editor} />
    </section>
  );
}
