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
  isLoading,
  onChange,
  onSave,
  saveDisabled,
  saveStatus,
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
            {isLoading ? 'Loading...' : 'Save'}
          </button>
          {saveStatus && <span className="save-status">{saveStatus}</span>}
        </div>
      </header>

      {!selectedSceneId && <p className="editor-empty">Select a scene to begin editing.</p>}
      <EditorContent editor={editor} />
    </section>
  );
}
