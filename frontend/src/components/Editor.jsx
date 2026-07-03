import { useEffect } from 'react';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import {
  DEFAULT_DOCUMENT_TYPE,
  DOCUMENT_TYPES,
  resolveActiveDocumentType,
} from '../sharedDocumentController.js';

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

const DOCUMENT_TYPE_LABELS = {
  [DOCUMENT_TYPES.SCENE]: {
    eyebrow: 'Editor',
    empty: 'Select a scene to begin editing.',
    emptyContent: 'This scene is empty. Saving an empty scene is allowed.',
    surfaceAria: 'Scene draft editor',
  },
  [DOCUMENT_TYPES.NOTE]: {
    eyebrow: 'Note',
    empty: 'Select a note to begin editing.',
    emptyContent: 'This note is empty. Saving an empty note is allowed.',
    surfaceAria: 'Note draft editor',
  },
  [DOCUMENT_TYPES.MATERIAL]: {
    eyebrow: 'Material',
    empty: 'Select a material to begin editing.',
    emptyContent: 'This material is empty. Saving an empty material is allowed.',
    surfaceAria: 'Material draft editor',
  },
};

export default function Editor({
  content,
  disabled,
  isDirty,
  isLoading,
  isSaving,
  onChange,
  onSave,
  saveDisabled,
  saveStatus,
  documentError,
  selectedDocumentId,
  documentType = DEFAULT_DOCUMENT_TYPE,
}) {
  const resolvedDocumentType = resolveActiveDocumentType(documentType);
  const labels = DOCUMENT_TYPE_LABELS[resolvedDocumentType];
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
        'aria-label': labels.surfaceAria,
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

  const title = selectedDocumentId
    ? selectedDocumentId.replace(/[-_]+/g, ' ')
    : `No ${resolvedDocumentType} selected`;
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

    if (isDirty) {
      return 'Unsaved changes';
    }

    if (saveStatus) {
      return saveStatus;
    }

    return selectedDocumentId ? 'Saved' : '';
  })();
  const saveStatusClass = displayedSaveStatus.startsWith('Save failed')
    ? 'save-status is-error'
    : `save-status${isDirty ? ' is-unsaved' : ''}`;

  return (
    <section className="editor-panel">
      <header className="editor-header">
        <div>
          <p className="eyebrow">{labels.eyebrow}</p>
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

      {!selectedDocumentId && <p className="editor-empty">{labels.empty}</p>}
      {selectedDocumentId && documentError && <p className="error-copy">{documentError}</p>}
      {selectedDocumentId && !isLoading && content.length === 0 && (
        <p className="muted-copy">{labels.emptyContent}</p>
      )}
      {resolvedDocumentType === DOCUMENT_TYPES.NOTE && selectedDocumentId && (
        <p
          className="muted-copy"
          data-testid="ux2-note-save-reload-proof"
        >
          owner-authored note save/reload proof; not canon by default; notes/materials do not mutate memory or canon.
        </p>
      )}
      {resolvedDocumentType === DOCUMENT_TYPES.MATERIAL && selectedDocumentId && (
        <p
          className="muted-copy"
          data-testid="ux2-material-save-reload-proof"
        >
          owner-provided material save/reload proof; not canon by default; notes/materials do not mutate memory or canon.
        </p>
      )}
      <EditorContent editor={editor} />
    </section>
  );
}
