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

export async function fetchMaterialMetadata(materialId, projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/materials/${materialId}/metadata`));
}

export async function saveMaterialMetadata(materialId, metadata, projectId = PROJECT_ID) {
  return requestData(() => client.put(`/projects/${projectId}/materials/${materialId}/metadata`, { metadata }));
}

const SAFE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;

export const REVIEW_ACTION_TYPES = Object.freeze([
  'mark_reviewed',
  'request_more_evidence',
  'defer',
  'reject',
  'quarantine',
  'update_owner_note',
  'set_review_status',
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

function compactStringField(value) {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : undefined;
}

export async function fetchReviewQueueEntries(projectId = PROJECT_ID) {
  requireSafeReviewRouteId(projectId, 'project_id');
  return requestData(() => client.get(`/projects/${projectId}/review-queue`));
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
