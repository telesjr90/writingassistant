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
      const detailText = typeof detail === 'string' ? detail : JSON.stringify(detail);
      return status ? `Request failed (${status}): ${detailText}` : `Request failed: ${detailText}`;
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

export class OmiGuidedProjectCreationError extends Error {
  constructor(message, { status = null, payload = null, code = null } = {}) {
    super(message);
    this.name = 'OmiGuidedProjectCreationError';
    this.status = status;
    this.payload = payload;
    this.code = code;
  }
}

export async function createOmiGuidedProject({ title, rawIdea, setupNotes }) {
  if (
    typeof title !== 'string'
    || typeof rawIdea !== 'string'
    || typeof setupNotes !== 'string'
  ) {
    throw new OmiGuidedProjectCreationError(
      'Guided creation requires string values for title, raw idea, and setup notes.',
      { code: 'invalid_guided_creation_request' },
    );
  }

  const payload = {
    title,
    raw_idea: rawIdea,
    setup_notes: setupNotes,
  };

  try {
    const response = await client.post('/projects/omi-guided', payload);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status ?? null;
      const responsePayload = error.response?.data ?? null;
      throw new OmiGuidedProjectCreationError(
        getErrorMessage(error),
        { status, payload: responsePayload },
      );
    }

    throw new OmiGuidedProjectCreationError(getErrorMessage(error));
  }
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

  const response = await runStoryCheck(selectedStoryCheckSourceId, projectId);
  const groundedSourceId = response?.grounding?.source_identity?.source_id;
  if (groundedSourceId && groundedSourceId !== selectedStoryCheckSourceId) {
    throw new Error('Story Check response source does not match the selected source.');
  }

  return response;
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

export async function fetchProjectContextReadiness(projectId = PROJECT_ID) {
  return requestData(() => client.get(`/projects/${projectId}/context-readiness`));
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
const UUID_V4_PATTERN = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/;
const SHA256_PATTERN = /^[a-f0-9]{64}$/;
const FINAL_CHALLENGE_ID_PATTERN = /^challenge_[a-f0-9]{16}_[a-f0-9]{64}$/;
const FINAL_CHALLENGE_RESPONSE_ALGORITHM = 'sha256-canonical-final-confirmation-v1';

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

function compactStringField(value) {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : undefined;
}

export class ApplyPromotionContractError extends Error {
  constructor(message, { status = null, code = null, payload = null } = {}) {
    super(message);
    this.name = 'ApplyPromotionContractError';
    this.status = status;
    this.code = code;
    this.payload = payload;
  }
}

async function requestApplyPromotionContract(request) {
  try {
    const response = await request();
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status ?? null;
      const payload = error.response?.data ?? null;
      const detail = payload?.detail;
      const code = typeof detail === 'object' ? detail?.code ?? null : null;
      const message = typeof detail === 'object' && detail?.message
        ? detail.message
        : getErrorMessage(error);
      throw new ApplyPromotionContractError(message, { status, code, payload });
    }
    throw new ApplyPromotionContractError(getErrorMessage(error));
  }
}

export async function fetchReviewQueueEntries(projectId = PROJECT_ID) {
  requireSafeReviewRouteId(projectId, 'project_id');
  return requestData(() => client.get(`/projects/${projectId}/review-queue`));
}

export async function getApplyPromotionContract(
  projectId = PROJECT_ID,
  promotionId,
  { revision = null } = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(promotionId, 'promotion_id');
  const config = revision === null ? undefined : { params: { revision } };
  return requestApplyPromotionContract(() => (
    client.get(`/projects/${projectId}/omi/promotions/${promotionId}/apply-contract`, config)
  ));
}

export async function prepareApplyPromotionContract(
  projectId = PROJECT_ID,
  promotionId,
  payload = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(promotionId, 'promotion_id');
  requireApplyPromotionDestinationType(payload.approved_destination_type);
  return requestApplyPromotionContract(() => (
    client.post(
      `/projects/${projectId}/omi/promotions/${promotionId}/apply-contract/revisions`,
      payload,
    )
  ));
}

export async function approveApplyPromotionContract(
  projectId = PROJECT_ID,
  promotionId,
  revision,
  payload = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(promotionId, 'promotion_id');
  if (!Number.isInteger(revision) || revision < 1) {
    throw new ApplyPromotionContractError('A positive contract revision is required for approval.');
  }
  return requestApplyPromotionContract(() => (
    client.post(
      `/projects/${projectId}/omi/promotions/${promotionId}/apply-contract/revisions/${revision}/approval`,
      payload,
    )
  ));
}

function requireUuidV4(value, label) {
  if (typeof value !== 'string' || !UUID_V4_PATTERN.test(value)) {
    throw new ApplyPromotionContractError(`${label} must be a UUIDv4.`);
  }
}

function requireSha256(value, label) {
  if (typeof value !== 'string' || !SHA256_PATTERN.test(value)) {
    throw new ApplyPromotionContractError(`${label} must be a lowercase SHA-256 value.`);
  }
}

function requirePositiveRevision(value) {
  if (!Number.isInteger(value) || value < 1 || value > 256) {
    throw new ApplyPromotionContractError('A contract revision from 1 through 256 is required.');
  }
}

export function buildFinalChallengeRequest({
  revision,
  sealedContractHash,
  beforeStateSnapshotToken,
  idempotencyKey,
}) {
  requirePositiveRevision(revision);
  requireSha256(sealedContractHash, 'sealed_contract_hash');
  requireSha256(beforeStateSnapshotToken, 'before_state_snapshot_token');
  requireUuidV4(idempotencyKey, 'idempotency_key');
  return {
    revision,
    sealed_contract_hash: sealedContractHash,
    before_state_snapshot_token: beforeStateSnapshotToken,
    idempotency_key: idempotencyKey,
  };
}

export async function issueApplyPromotionFinalChallenge(
  projectId = PROJECT_ID,
  promotionId,
  input = {},
) {
  requireSafeReviewRouteId(projectId, 'project_id');
  requireSafeReviewRouteId(promotionId, 'promotion_id');
  const requestPayload = buildFinalChallengeRequest(input);
  return requestApplyPromotionContract(() => (
    client.post(
      `/projects/${projectId}/omi/promotions/${promotionId}/apply-contract/final-challenge`,
      requestPayload,
    )
  ));
}

export function canonicalizeFinalChallengeValue(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') {
    return JSON.stringify(value);
  }
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) {
      throw new ApplyPromotionContractError('Challenge scope contains an unsupported number.');
    }
    return Object.is(value, -0) ? '0' : String(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalizeFinalChallengeValue(item)).join(',')}]`;
  }
  if (value && typeof value === 'object' && Object.getPrototypeOf(value) === Object.prototype) {
    return `{${Object.keys(value).sort().map((key) => (
      `${JSON.stringify(key)}:${canonicalizeFinalChallengeValue(value[key])}`
    )).join(',')}}`;
  }
  throw new ApplyPromotionContractError('Challenge scope contains an unsupported value.');
}

function decodeBase64Url(value) {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]+$/.test(value)) {
    throw new ApplyPromotionContractError('Final challenge nonce is malformed.');
  }
  const normalized = value.replaceAll('-', '+').replaceAll('_', '/');
  const decoded = globalThis.atob(`${normalized}${'='.repeat((4 - (normalized.length % 4)) % 4)}`);
  return Uint8Array.from(decoded, (character) => character.charCodeAt(0));
}

export async function computeFinalChallengeResponse(challenge) {
  if (
    challenge?.response_algorithm !== FINAL_CHALLENGE_RESPONSE_ALGORITHM
    || !FINAL_CHALLENGE_ID_PATTERN.test(challenge?.challenge_id ?? '')
    || challenge?.challenge_scope?.challenge_id !== challenge.challenge_id
  ) {
    throw new ApplyPromotionContractError('Final challenge response does not match the accepted protocol.');
  }
  if (!globalThis.crypto?.subtle) {
    throw new ApplyPromotionContractError('Web Crypto is required to confirm the final challenge.');
  }
  const nonce = decodeBase64Url(challenge.challenge_nonce);
  const encoder = new TextEncoder();
  const prefix = encoder.encode('apply-promotion-final-confirmation-v1\u0000');
  const confirmation = encoder.encode(canonicalizeFinalChallengeValue({
    challenge_scope: challenge.challenge_scope,
    final_confirmation: {
      confirmed: true,
      method: 'explicit_final_apply_confirmation',
    },
  }));
  const preimage = new Uint8Array(prefix.length + nonce.length + 1 + confirmation.length);
  preimage.set(prefix, 0);
  preimage.set(nonce, prefix.length);
  preimage[prefix.length + nonce.length] = 0;
  preimage.set(confirmation, prefix.length + nonce.length + 1);
  const digest = await globalThis.crypto.subtle.digest('SHA-256', preimage);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

export function buildReferenceOnlyApplyPromotionRequest({
  promotionId,
  revision,
  sealedContractHash,
  beforeStateSnapshotToken,
  challengeId,
  challengeResponse,
  idempotencyKey,
}) {
  requireSafeReviewRouteId(promotionId, 'promotion_id');
  requirePositiveRevision(revision);
  requireSha256(sealedContractHash, 'sealed_contract_hash');
  requireSha256(beforeStateSnapshotToken, 'before_state_snapshot_token');
  if (typeof challengeId !== 'string' || !FINAL_CHALLENGE_ID_PATTERN.test(challengeId)) {
    throw new ApplyPromotionContractError('challenge_id does not match the accepted final-challenge protocol.');
  }
  requireSha256(challengeResponse, 'challenge_response');
  requireUuidV4(idempotencyKey, 'idempotency_key');
  return {
    promotion_id: promotionId,
    revision,
    sealed_contract_hash: sealedContractHash,
    before_state_snapshot_token: beforeStateSnapshotToken,
    challenge_id: challengeId,
    challenge_response: challengeResponse,
    final_confirmation: {
      confirmed: true,
      method: 'explicit_final_apply_confirmation',
    },
    idempotency_key: idempotencyKey,
  };
}

export async function submitApplyPromotion(projectId = PROJECT_ID, input = {}) {
  requireSafeReviewRouteId(projectId, 'project_id');
  const requestPayload = buildReferenceOnlyApplyPromotionRequest(input);
  return requestApplyPromotionContract(() => (
    client.post(`/projects/${projectId}/apply-promotion`, requestPayload)
  ));
}

export function classifyApplyPromotionFailure(code) {
  const challengeStates = {
    FINAL_CHALLENGE_EXPIRED: 'expired',
    FINAL_CHALLENGE_REPLACED: 'replaced',
    FINAL_CHALLENGE_REQUIRED_AFTER_RESTART: 'restart_invalidated',
    FINAL_CHALLENGE_CONSUMED: 'consumed',
    FINAL_CHALLENGE_UNKNOWN: 'unknown',
  };
  if (challengeStates[code]) {
    return { challengeState: challengeStates[code], applyState: 'not_started' };
  }
  if (code === 'RECOVERY_REQUIRED') {
    return { challengeState: 'consumed', applyState: 'recovery_required' };
  }
  if (code === 'APPLY_FAILED_BEFORE_COMMIT') {
    return { challengeState: 'consumed', applyState: 'not_committed' };
  }
  return { challengeState: null, applyState: code ? 'blocked' : 'failed' };
}

export function getFinalChallengeTemporalState(challenge, nowMs = Date.now()) {
  const expiresAt = Date.parse(challenge?.challenge_scope?.expires_at ?? '');
  if (!Number.isFinite(expiresAt)) {
    return { state: 'invalid', secondsRemaining: 0 };
  }
  const millisecondsRemaining = expiresAt - nowMs;
  if (millisecondsRemaining <= 0) {
    return { state: 'expired', secondsRemaining: 0 };
  }
  return {
    state: 'active',
    secondsRemaining: Math.ceil(millisecondsRemaining / 1000),
  };
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
