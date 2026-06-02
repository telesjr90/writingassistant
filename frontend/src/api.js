import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
});

const PROJECT_ID = 'example';

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

export async function fetchScenes() {
  return requestData(() => client.get(`/projects/${PROJECT_ID}/scenes`));
}

export async function fetchScene(sceneId) {
  return requestData(() => client.get(`/projects/${PROJECT_ID}/scenes/${sceneId}`));
}

export async function saveScene(sceneId, content) {
  return requestData(() => client.put(`/projects/${PROJECT_ID}/scenes/${sceneId}`, { content }));
}

export async function fetchBible() {
  return requestData(() => client.get(`/projects/${PROJECT_ID}/bible`));
}

export async function saveBible(data) {
  return requestData(() => client.put(`/projects/${PROJECT_ID}/bible`, data));
}

export async function fetchStoryform() {
  return requestData(() => client.get(`/projects/${PROJECT_ID}/storyform`));
}

export async function saveStoryform(data) {
  return requestData(() => client.put(`/projects/${PROJECT_ID}/storyform`, data));
}

export async function runStoryCheck(sceneId) {
  return requestData(() => client.post(`/projects/${PROJECT_ID}/story-check/${sceneId}`));
}

export async function fetchStoryformContext() {
  return requestData(() => client.get(`/projects/${PROJECT_ID}/storyform-context`));
}
