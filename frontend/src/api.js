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
