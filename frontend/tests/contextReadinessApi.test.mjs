import assert from 'node:assert/strict';
import test from 'node:test';

import axios from 'axios';

const requests = [];
let responseData = null;
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
    data: responseData,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  };
};

const { fetchProjectContextReadiness } = await import('../src/api.js');

test.beforeEach(() => {
  requests.length = 0;
  responseData = null;
  failureResponse = null;
});

function readinessResponse() {
  return {
    schema_version: 'project_context_readiness.v1',
    project_id: 'example',
    status_vocabulary: ['absent', 'invalid', 'not_applicable', 'ready', 'unavailable'],
    resource_order: ['bible', 'storyform', 'storyform_context'],
    resources: {
      bible: {
        resource_id: 'bible',
        resource_type: 'project_json',
        exists: false,
        structurally_valid: false,
        ready: false,
        state: 'absent',
        reason_code: 'bible_absent',
        diagnostics: ['Optional Bible resource is not present.'],
        source_locator: 'bible.json',
      },
      storyform: {
        resource_id: 'storyform',
        resource_type: 'project_json',
        exists: false,
        structurally_valid: false,
        ready: false,
        state: 'absent',
        reason_code: 'storyform_absent',
        diagnostics: ['Optional storyform resource is not present.'],
        source_locator: 'storyform.json',
      },
      storyform_context: {
        resource_id: 'storyform_context',
        resource_type: 'derived_context',
        exists: false,
        structurally_valid: false,
        ready: false,
        state: 'unavailable',
        reason_code: 'storyform_context_storyform_absent',
        diagnostics: ['Storyform context requires a present storyform.'],
        source_locator: 'storyform.json',
      },
    },
    summary: {
      resource_count: 3,
      ready_count: 0,
      all_ready: false,
    },
    safety: {
      read_only: true,
      analysis_runtime_invoked: false,
      model_or_external_tool_invoked: false,
      resource_mutation: false,
      candidate_persistence: false,
      promotion_or_apply_promotion: false,
      memory_canon_mutation: false,
      story_prose_generated: false,
    },
  };
}

test('fetchProjectContextReadiness issues GET /projects/{projectId}/context-readiness', async () => {
  responseData = readinessResponse();

  await fetchProjectContextReadiness('example');

  assert.equal(requests.length, 1);
  assert.equal(requests[0].baseURL, '/api');
  assert.equal(requests[0].method, 'get');
  assert.equal(requests[0].url, '/projects/example/context-readiness');
});

test('fetchProjectContextReadiness preserves complete readiness payload', async () => {
  responseData = readinessResponse();

  const result = await fetchProjectContextReadiness('example');

  assert.equal(result.schema_version, 'project_context_readiness.v1');
  assert.equal(result.project_id, 'example');
  assert.deepStrictEqual(result.resource_order, ['bible', 'storyform', 'storyform_context']);
  assert.equal(result.resources.bible.state, 'absent');
  assert.equal(result.resources.storyform.state, 'absent');
  assert.equal(result.resources.storyform_context.state, 'unavailable');
  assert.equal(result.summary.all_ready, false);
  assert.equal(result.safety.read_only, true);
});

test('fetchProjectContextReadiness preserves absent state as-is', async () => {
  responseData = readinessResponse();
  responseData.resources.bible.state = 'absent';
  responseData.resources.bible.ready = false;

  const result = await fetchProjectContextReadiness('example');

  assert.equal(result.resources.bible.state, 'absent');
  assert.equal(result.resources.bible.ready, false);
  assert.equal(result.resources.bible.exists, false);
});

test('fetchProjectContextReadiness preserves invalid state as-is', async () => {
  responseData = readinessResponse();
  responseData.resources.bible.state = 'invalid';
  responseData.resources.bible.ready = false;
  responseData.resources.bible.exists = true;
  responseData.resources.bible.reason_code = 'bible_malformed_json';

  const result = await fetchProjectContextReadiness('example');

  assert.equal(result.resources.bible.state, 'invalid');
  assert.equal(result.resources.bible.ready, false);
  assert.equal(result.resources.bible.reason_code, 'bible_malformed_json');
});

test('fetchProjectContextReadiness preserves unavailable state as-is', async () => {
  responseData = readinessResponse();
  responseData.resources.storyform_context.state = 'unavailable';
  responseData.resources.storyform_context.ready = false;

  const result = await fetchProjectContextReadiness('example');

  assert.equal(result.resources.storyform_context.state, 'unavailable');
  assert.equal(result.resources.storyform_context.ready, false);
});

test('fetchProjectContextReadiness preserves ready state as-is', async () => {
  responseData = readinessResponse();
  responseData.resources.bible.state = 'ready';
  responseData.resources.bible.ready = true;
  responseData.resources.bible.exists = true;
  responseData.resources.bible.structurally_valid = true;

  const result = await fetchProjectContextReadiness('example');

  assert.equal(result.resources.bible.state, 'ready');
  assert.equal(result.resources.bible.ready, true);
});

test('transport failure is rejected as error and not converted to absence', async () => {
  failureResponse = { status: 500, data: { detail: 'Server error' } };

  await assert.rejects(
    () => fetchProjectContextReadiness('example'),
    (err) => err instanceof Error && err.message.includes('Request failed'),
  );
});

test('transport failure does not set state to absent', async () => {
  failureResponse = { status: 404, data: { detail: 'Not found' } };

  await assert.rejects(
    () => fetchProjectContextReadiness('example'),
    (err) => {
      assert.ok(err instanceof Error);
      assert.ok(err.message.includes('Request failed'));
      assert.ok(!err.message.includes('absent'));
      return true;
    },
  );
});

test('fetchProjectContextReadiness does not call Bible endpoint', async () => {
  responseData = readinessResponse();

  await fetchProjectContextReadiness('example');

  const bibleRequests = requests.filter((r) => r.url && r.url.includes('/bible'));
  assert.equal(bibleRequests.length, 0);
});

test('fetchProjectContextReadiness does not call storyform endpoint', async () => {
  responseData = readinessResponse();

  await fetchProjectContextReadiness('example');

  const storyformRequests = requests.filter(
    (r) => r.url && r.url.includes('/storyform') && !r.url.includes('context-readiness'),
  );
  assert.equal(storyformRequests.length, 0);
});

test('fetchProjectContextReadiness does not call storyform-context endpoint', async () => {
  responseData = readinessResponse();

  await fetchProjectContextReadiness('example');

  const contextRequests = requests.filter(
    (r) => r.url && r.url.includes('/storyform-context'),
  );
  assert.equal(contextRequests.length, 0);
});
