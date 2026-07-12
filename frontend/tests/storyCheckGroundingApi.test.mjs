import assert from 'node:assert/strict';
import test from 'node:test';

import axios from 'axios';

let responseData = null;
const requests = [];
axios.defaults.adapter = async (config) => {
  requests.push(config);
  return {
    data: responseData,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  };
};

const { runStoryCheckForSelectedSource } = await import('../src/api.js');

test.beforeEach(() => {
  requests.length = 0;
  responseData = null;
});

function selectedSource() {
  return {
    project_id: 'example',
    source_id: 'scene_001',
    source_type: 'scene',
    source_kind: 'owner-authored source',
  };
}

test('selected-source API preserves the complete grounded response', async () => {
  responseData = {
    warnings: ['[Factual] Exact warning'],
    grounding: {
      status: 'completed',
      contract_version: 'story-check-grounding-contract.v1',
      source_identity: {
        project_id: 'example',
        source_id: 'scene_001',
        source_type: 'scene',
        source_sha256: 'a'.repeat(64),
        utf8_byte_length: 13,
        hash_algorithm: 'sha256',
        hash_basis: 'utf-8-exact',
      },
      diagnostics: [{
        message: 'Exact warning',
        verification_state: 'verified',
        validator_result: { outcome: 'supported' },
      }],
      boundary: { analytical_output: true, non_canon: true, owner_approved: false },
    },
  };

  const result = await runStoryCheckForSelectedSource({
    projectId: 'example',
    selectedStoryCheckSourceId: 'scene_001',
    selectedStoryCheckSource: selectedSource(),
  });

  assert.deepEqual(result, responseData);
  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, '/projects/example/story-check/scene_001');
  assert.equal(requests[0].method, 'post');
});

test('selected-source API fails closed on a grounded source-ID mismatch', async () => {
  responseData = {
    grounding: {
      status: 'completed',
      source_identity: { source_id: 'scene_002' },
      diagnostics: [],
    },
  };

  await assert.rejects(
    runStoryCheckForSelectedSource({
      projectId: 'example',
      selectedStoryCheckSourceId: 'scene_001',
      selectedStoryCheckSource: selectedSource(),
    }),
    /does not match the selected source/,
  );
});

test('legacy response remains ungrounded and is not decorated as verified by the API', async () => {
  responseData = { warnings: ['[Factual] Legacy warning'], suggestions: [] };
  const result = await runStoryCheckForSelectedSource({
    projectId: 'example',
    selectedStoryCheckSourceId: 'scene_001',
    selectedStoryCheckSource: selectedSource(),
  });

  assert.deepEqual(result, responseData);
  assert.equal(result.grounding, undefined);
});
