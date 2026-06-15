export const DOCUMENT_TYPES = Object.freeze({
  SCENE: 'scene',
  NOTE: 'note',
  MATERIAL: 'material',
});

export const DOCUMENT_TYPE_VALUES = Object.freeze(Object.values(DOCUMENT_TYPES));
export const DEFAULT_DOCUMENT_TYPE = DOCUMENT_TYPES.SCENE;

export function isSupportedDocumentType(documentType) {
  return DOCUMENT_TYPE_VALUES.includes(documentType);
}

export function resolveActiveDocumentType(documentType) {
  return isSupportedDocumentType(documentType) ? documentType : DEFAULT_DOCUMENT_TYPE;
}

export function getDocumentResponseContent(response) {
  return response?.content ?? '';
}

export function hasUnsavedDocumentEdits({ scene = false, note = false, material = false } = {}) {
  return Boolean(scene || note || material);
}

export function getDocumentSwitchMessage(documentType, messages) {
  const resolvedType = resolveActiveDocumentType(documentType);
  return messages[resolvedType] ?? messages[DEFAULT_DOCUMENT_TYPE];
}

export function createDocumentDescriptor({
  type,
  id,
  content,
  isDirty,
  isLoading,
  isSaving,
  error,
  saveStatus,
  onChange,
  onSave,
}) {
  return {
    type: resolveActiveDocumentType(type),
    id: id ?? '',
    content: content ?? '',
    isDirty: Boolean(isDirty),
    isLoading: Boolean(isLoading),
    isSaving: Boolean(isSaving),
    error: error ?? '',
    saveStatus: saveStatus ?? '',
    onChange,
    onSave,
  };
}

export function getActiveDocumentDescriptor(documentType, descriptors) {
  const resolvedType = resolveActiveDocumentType(documentType);
  return descriptors[resolvedType] ?? descriptors[DEFAULT_DOCUMENT_TYPE];
}

export function canSaveDocument(document) {
  return Boolean(document?.id) && !document.isLoading && !document.isSaving;
}
