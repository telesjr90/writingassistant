import assert from 'node:assert/strict';
import test from 'node:test';

import axios from 'axios';

const requests = [];
let failureResponse = null;

axios.defaults.adapter = async (config) => {
  requests.push(config);

  if (failureResponse) {
    throw new axios.AxiosError(
      'Request failed',
      axios.AxiosError.ERR_BAD_RESPONSE,
      config,
      null,
      {
        data: failureResponse.data,
        status: failureResponse.status,
        statusText: 'Request failed',
        headers: {},
        config,
      },
    );
  }

  return {
    data: { status: 'complete' },
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  };
};

const {
  createOmiGuidedProject,
  createProject,
  OmiGuidedProjectCreationError,
} = await import('../src/api.js');

test.beforeEach(() => {
  requests.length = 0;
  failureResponse = null;
});

test('guided helper posts only the exact guided fields and preserves owner text', async () => {
  const rawIdea = '\r\n  Owner idea line one.\nLine two.  \r\n';
  const setupNotes = '  Setup note.\r\n\nSecond line.  ';

  await createOmiGuidedProject({
    title: 'Project title',
    rawIdea,
    setupNotes,
  });

  assert.equal(requests.length, 1);
  assert.equal(requests[0].baseURL, '/api');
  assert.equal(requests[0].url, '/projects/omi-guided');
  assert.equal(requests[0].method, 'post');
  assert.deepEqual(JSON.parse(requests[0].data), {
    title: 'Project title',
    raw_idea: rawIdea,
    setup_notes: setupNotes,
  });
  assert.notEqual(requests[0].url, '/projects');
});

test('guided helper preserves an empty setup-notes string', async () => {
  await createOmiGuidedProject({
    title: 'Empty notes',
    rawIdea: '  Exact idea  ',
    setupNotes: '',
  });

  assert.equal(JSON.parse(requests[0].data).setup_notes, '');
});

test('guided helper rejects missing required strings before sending a request', async () => {
  await assert.rejects(
    createOmiGuidedProject({ title: 'Missing notes', rawIdea: 'Idea' }),
    (error) => (
      error instanceof OmiGuidedProjectCreationError
      && error.code === 'invalid_guided_creation_request'
    ),
  );
  assert.equal(requests.length, 0);
});

test('guided helper retains structured backend payload and HTTP status', async () => {
  const payload = {
    status: 'recovery_required',
    project_id: 'recovery-project',
    raw_idea: '  retained idea\r\n',
    setup_notes: ' retained notes ',
  };
  failureResponse = { status: 500, data: payload };

  await assert.rejects(
    createOmiGuidedProject({
      title: 'Recovery project',
      rawIdea: payload.raw_idea,
      setupNotes: payload.setup_notes,
    }),
    (error) => (
      error instanceof OmiGuidedProjectCreationError
      && error.status === 500
      && error.payload === payload
    ),
  );
});

test('ordinary blank creation remains a distinct title-only request', async () => {
  await createProject('Blank project');

  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, '/projects');
  assert.equal(requests[0].method, 'post');
  assert.deepEqual(JSON.parse(requests[0].data), { title: 'Blank project' });
});
