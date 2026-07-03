import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
});

export const PROJECT_ID = 'example';

function getErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail ?? error.response?.data?.error;
    const status = error.response?.status;

    if (detail) {
      return status ? `Request failed (${status}): ${detail}` : `Request failed: ${detail}`;
    }

    return status ? `Request failed (${status})` : error.message;
  }

  return error instanceof Error ? error.message : 'Unknown API error';
}

async function requestData(request) {
  try {
    const { data } = await request();
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function listProjects() {
  return requestData(() => client.get('/projects'));
}

export async function createProject(title) {
  return requestData(() => client.post('/projects', { title }));
}

export async function fetchScenes(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/scenes`));
}

export async function fetchScene(sceneId, projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/scenes/${sceneId}`));
}

export async function saveScene(sceneId, content, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/scenes/${sceneId}`, { content }));
}

export async function createOrImportOwnerAuthoredSource(
  projectId = PROJECT_ID,
  { sourceId, content } = {},
) {
  requireSafeOwnerAuthoredSourceId(projectId, 'project_id');
  requireSafeOwnerAuthoredSourceId(sourceId, 'source_id');

  const ownerAuthoredContent = typeof content === 'string' ? content : '';
  await saveScene(sourceId, ownerAuthoredContent, projectId);

  return {
    project_id: projectId,
    source_id: sourceId,
    source_type: 'scene',
    source_kind: 'owner-authored source',
    source_scope: 'project-scoped selected source',
    status: 'saved',
    is_canon: false,
    is_memory: false,
    is_training_data: false,
    is_approved_truth: false,
  };
}

export function selectStoryCheckSource(projectId = PROJECT_ID, sourceId) {
  requireSafeOwnerAuthoredSourceId(projectId, 'project_id');
  requireSafeOwnerAuthoredSourceId(sourceId, 'source_id');

  return {
    project_id: projectId,
    source_id: sourceId,
    source_type: 'scene',
    source_kind: 'owner-authored source',
    source_scope: 'project-scoped selected source',
    selected_for: 'Story Check',
    is_canon: false,
    is_memory: false,
    is_training_data: false,
    is_approved_truth: false,
  };
}

export async function fetchBible(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/bible`));
}

export async function saveBible(data, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/bible`, data));
}

export async function fetchStoryform(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/storyform`));
}

export async function saveStoryform(data, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/storyform`, data));
}

export async function runStoryCheck(sceneId, projectId = PROJECT_ID) {
  return requestData(() => client.post(`/projects/${projectId}/story-check/${sceneId}`));
}

export async function runStoryCheckForSelectedSource({
  projectId = PROJECT_ID,
  selectedStoryCheckSourceId,
  selectedStoryCheckSource,
} = {}) {
  requireSafeOwnerAuthoredSourceId(projectId, 'project_id');
  requireSafeOwnerAuthoredSourceId(selectedStoryCheckSourceId, 'selected_story_check_source_id');

  if (!selectedStoryCheckSource || selectedStoryCheckSource.source_id !== selectedStoryCheckSourceId) {
    throw new Error('Story Check requires a selected owner-authored source.');
  }

  return runStoryCheck(selectedStoryCheckSourceId, projectId);
}

export function fetchRawArtifactEvidenceStatus(projectId = PROJECT_ID) {
  requireSafeOwnerAuthoredSourceId(projectId, 'project_id');

  return {
    project_id: projectId,
    runtime_extraction_status: 'runtime extraction unavailable',
    evidence_status: 'read-only raw artifact evidence',
    support_data_boundary: 'raw artifacts are support data only',
    canon_boundary: 'raw artifacts are not canon',
    mutation_boundary: 'raw artifact inspection does not mutate memory or canon',
    runtime_execution_available: false,
    mutates_memory_or_canon: false,
  };
}

export function refuseForbiddenProseIntent(intent) {
  const normalizedIntent = typeof intent === 'string' ? intent.trim().toLowerCase() : '';
  const forbiddenIntents = new Set([
    'rewrite',
    'continue',
    'outline',
    'draft',
    'polish',
    'improve',
    'expand',
    'imitate',
    'generate prose',
  ]);

  if (!forbiddenIntents.has(normalizedIntent)) {
    return {
      refused: false,
      boundary: 'analysis-only no-prose boundary',
      message: 'This interface exposes diagnostics only.',
    };
  }

  return {
    refused: true,
    intent: normalizedIntent,
    boundary: 'analysis-only no-prose boundary',
    message: `forbidden intent: ${normalizedIntent}; no generated story prose.`,
  };
}

export async function fetchStoryformContext(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/storyform-context`));
}

export async function getOMI(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/omi`));
}

export async function createOMIIdea(projectId = PROJECT_ID, payload) {
  return requestData(() => client.post(`/projects/${projectId}/omi/ideas`, payload));
}

export async function getOMIIdea(projectId = PROJECT_ID, ideaId) {
  return requestData(() => client.get(`/projects/${projectId}/omi/ideas/${ideaId}`));
}

export async function createOMICandidate(projectId = PROJECT_ID, payload) {
  return requestData(() => client.post(`/projects/${projectId}/omi/candidates`, payload));
}

export async function getOMICandidate(projectId = PROJECT_ID, candidateId) {
  return requestData(() => client.get(`/projects/${projectId}/omi/candidates/${candidateId}`));
}

export async function updateOMIIdeaDecision(projectId = PROJECT_ID, ideaId, payload) {
  return requestData(() => client.patch(`/projects/${projectId}/omi/ideas/${ideaId}/decision`, payload));
}

export async function updateOMICandidateDecision(projectId = PROJECT_ID, candidateId, payload) {
  return requestData(() => (
    client.patch(`/projects/${projectId}/omi/candidates/${candidateId}/decision`, payload)
  ));
}

export async function getOMIPromotions(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/omi/promotions`));
}

export async function getOMIPromotion(projectId = PROJECT_ID, promotionId) {
  return requestData(() => client.get(`/projects/${projectId}/omi/promotions/${promotionId}`));
}

export async function createOMIPromotion(projectId = PROJECT_ID, payload) {
  return requestData(() => client.post(`/projects/${projectId}/omi/promotions`, payload));
}

// Note API helpers (PHASE7-IMPL-005-T005)
export async function fetchNotes(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/notes`));
}

export async function fetchNote(noteId, projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/notes/${noteId}`));
}

export async function saveNote(noteId, content, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/notes/${noteId}`, { content }));
}

export async function createOwnerAuthoredNote(
  projectId = PROJECT_ID,
  { noteId, content } = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(noteId, 'note_id');

  const ownerAuthoredContent = typeof content === 'string' ? content : '';
  await saveNote(noteId, ownerAuthoredContent, projectId);

  return {
    project_id: projectId,
    note_id: noteId,
    source_kind: 'owner-authored note',
    source_scope: 'project-scoped notes/materials',
    canon_boundary: 'not canon by default',
    memory_boundary: 'notes/materials do not mutate memory or canon',
    is_canon: false,
    mutates_memory_or_canon: false,
    status: 'saved',
  };
}

export async function fetchNoteMetadata(noteId, projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/notes/${noteId}/metadata`));
}

export async function saveNoteMetadata(noteId, metadata, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/notes/${noteId}/metadata`, { metadata }));
}

// Material API helpers (PHASE7-IMPL-005-T005)
export async function fetchMaterials(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/materials`));
}

export async function fetchMaterial(materialId, projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/materials/${materialId}`));
}

export async function saveMaterial(materialId, content, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/materials/${materialId}`, { content }));
}

export async function createOwnerProvidedMaterial(
  projectId = PROJECT_ID,
  { materialId, content } = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(materialId, 'material_id');

  const ownerProvidedContent = typeof content === 'string' ? content : '';
  await saveMaterial(materialId, ownerProvidedContent, projectId);

  return {
    project_id: projectId,
    material_id: materialId,
    source_kind: 'owner-provided material',
    source_scope: 'project-scoped notes/materials',
    canon_boundary: 'not canon by default',
    memory_boundary: 'notes/materials do not mutate memory or canon',
    is_canon: false,
    mutates_memory_or_canon: false,
    status: 'saved',
  };
}

export async function reloadProjectScopedNotesMaterials(
  projectId = PROJECT_ID,
  { noteId, materialId } = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');

  const [notesPayload, materialsPayload, notePayload, materialPayload] = await Promise.all([
    fetchNotes(projectId),
    fetchMaterials(projectId),
    noteId ? fetchNote(noteId, projectId) : Promise.resolve(null),
    materialId ? fetchMaterial(materialId, projectId) : Promise.resolve(null),
  ]);

  return {
    project_id: projectId,
    notes: notesPayload?.notes ?? [],
    materials: materialsPayload?.materials ?? [],
    note: notePayload,
    material: materialPayload,
    note_id: noteId ?? null,
    material_id: materialId ?? null,
    proof: 'owner-authored note / owner-provided material save-reload proof',
    canon_boundary: 'not canon by default',
    memory_boundary: 'notes/materials do not mutate memory or canon',
  };
}

export async function fetchMaterialMetadata(materialId, projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/materials/${materialId}/metadata`));
}

export async function saveMaterialMetadata(materialId, metadata, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/materials/${materialId}/metadata`, { metadata }));
}

const SAFE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;
const SAFE_DESTINATION_PATH_PATTERN = /^memory\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+\.json$/;

function requireSafeOwnerAuthoredSourceId(value, label) {
  if (!isSafeReviewRouteId(value)) {
    throw new Error(`${label} is required before selecting an owner-authored source.`);
  }
}

export const REVIEW_ACTION_TYPES = Object.freeze([
  'mark_reviewed',
  'request_more_evidence',
  'defer',
  'reject',
  'quarantine',
  'update_owner_note',
  'set_review_status',
]);

export const APPLY_PROMOTION_DESTINATION_TYPES = Object.freeze([
  'approved_character',
  'approved_location',
  'approved_timeline_event',
  'approved_relationship',
  'approved_organization',
  'approved_object',
  'approved_plot_thread',
  'approved_continuity_record',
  'approved_open_question',
  'approved_memory_index',
]);

export function isSafeReviewRouteId(value) {
  return typeof value === 'string' && SAFE_ID_PATTERN.test(value);
}

function requireSafeReviewRouteId(value, label) {
  if (!isSafeReviewRouteId(value)) {
    throw new Error(`${label} is required before sending an owner review action.`);
  }
}

function requireReviewActionType(actionType) {
  if (!REVIEW_ACTION_TYPES.includes(actionType)) {
    throw new Error('Unsupported owner review action.');
  }
}

function requireApplyPromotionDestinationType(destinationType) {
  if (!APPLY_PROMOTION_DESTINATION_TYPES.includes(destinationType)) {
    throw new Error('Unsupported apply-promotion destination.');
  }
}

function requireNonEmptyRefList(value, label) {
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error(`${label} is required before apply-promotion.`);
  }
}

function requireSafeDestinationPath(value) {
  if (typeof value !== 'string' || !SAFE_DESTINATION_PATH_PATTERN.test(value)) {
    throw new Error('destination_path is required before apply-promotion.');
  }
}

function compactStringField(value) {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : undefined;
}

export async function fetchReviewQueueEntries(projectId = PROJECT_ID) {
  requireSafeReviewRouteId(projectId, 'project_id');
  return requestData(() => client.get(`/projects/${projectId}/review-queue`));
}

export async function submitApplyPromotion(projectId = PROJECT_ID, payload = {}) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(payload.candidate_id, 'candidate_id');
  requireSafeReviewRouteId(payload.owner_actor_id, 'owner_actor_id');
  requireApplyPromotionDestinationType(payload.destination_type);
  requireSafeDestinationPath(payload.destination_path);
  requireNonEmptyRefList(payload.evidence_refs, 'evidence_refs');
  requireNonEmptyRefList(payload.provenance_refs, 'provenance_refs');
  requireNonEmptyRefList(payload.source_locator_refs, 'source_locator_refs');

  if (typeof payload.candidate_type !== 'string' || payload.candidate_type.trim() === '') {
    throw new Error('candidate_type is required before apply-promotion.');
  }
  if (payload.destination_key && !isSafeReviewRouteId(payload.destination_key)) {
    throw new Error('destination_key is required before apply-promotion.');
  }
  if (payload.queue_entry_id && !isSafeReviewRouteId(payload.queue_entry_id)) {
    throw new Error('queue_entry_id must be safe before apply-promotion.');
  }
  if (payload.owner_confirmation !== true) {
    throw new Error('owner_confirmation is required before apply-promotion.');
  }

  const requestPayload = {
    project_id: projectId,
    candidate_id: payload.candidate_id,
    queue_entry_id: compactStringField(payload.queue_entry_id),
    candidate_type: payload.candidate_type,
    owner_actor_id: payload.owner_actor_id,
    owner_actor_label: compactStringField(payload.owner_actor_label),
    owner_confirmation: true,
    owner_note: compactStringField(payload.owner_note) ?? '',
    destination_type: payload.destination_type,
    destination_path: payload.destination_path,
    destination_key: compactStringField(payload.destination_key),
    approved_payload: {
      record_type: payload.destination_type,
      candidate_id: payload.candidate_id,
      destination_key: compactStringField(payload.destination_key),
      evidence_refs: payload.evidence_refs,
      provenance_refs: payload.provenance_refs,
      source_locator_refs: payload.source_locator_refs,
    },
    evidence_refs: payload.evidence_refs,
    provenance_refs: payload.provenance_refs,
    source_locator_refs: payload.source_locator_refs,
    source_candidate_snapshot_hash: compactStringField(payload.source_candidate_snapshot_hash),
    requested_at: compactStringField(payload.requested_at),
    boundary_flags: [
      'candidate persistence is not canon',
      'queue presence is not approval',
      'confidence is not truth',
      'raw artifacts are support data',
      'no_auto_promotion',
      'no_confidence_as_truth',
      'no_queue_presence_as_approval',
      'no_generated_prose',
      'no_model_calls',
      'no_training_artifacts',
    ],
  };

  return requestData(() => (
    client.post(`/projects/${projectId}/apply-promotion`, requestPayload)
  ));
}

export async function submitReviewQueueAction({
  projectId = PROJECT_ID,
  queueEntryId,
  candidateId,
  actionType,
  ownerNote,
  rationale,
  expectedCurrentReviewStatus,
  expectedCurrentVersion,
  reviewStatus,
}) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(queueEntryId, 'queue_entry_id');
  requireSafeReviewRouteId(candidateId, 'candidate_id');
  requireReviewActionType(actionType);

  const payload = {
    action_type: actionType,
    queue_entry_id: queueEntryId,
    actor: {
      actor_type: 'owner',
      owner_confirmed: true,
      owner_confirmation_marker: 'owner-reviewed',
    },
    owner_confirmed: true,
    preserve_candidate_linkage: true,
    preserve_evidence_provenance: true,
    metadata: {
      client_surface: 'owner-action-review-controls',
      no_silent_promotion: true,
      no_model_calls: true,
      no_generated_prose: true,
    },
  };

  payload.candidate_id = candidateId;

  const note = compactStringField(ownerNote);
  const actionRationale = compactStringField(rationale);
  const currentStatus = compactStringField(expectedCurrentReviewStatus);
  const nextReviewStatus = compactStringField(reviewStatus);

  if (note) {
    payload.owner_note = note;
  }
  if (actionRationale) {
    payload.rationale = actionRationale;
  }
  if (currentStatus) {
    payload.expected_current_review_status = currentStatus;
  }
  if (Number.isInteger(expectedCurrentVersion)) {
    payload.expected_current_version = expectedCurrentVersion;
  }
  if (actionType === 'set_review_status' && nextReviewStatus) {
    payload.target_review_status = nextReviewStatus;
  }

  return requestData(() => (
    client.post(`/projects/${projectId}/review-queue/${queueEntryId}/actions`, payload)
  ));
}
