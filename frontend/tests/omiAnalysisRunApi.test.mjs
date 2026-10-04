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
  return { data: responseData, status: 200, statusText: 'OK', headers: {}, config };
};

const {
  OmiAnalysisRunError,
  fetchOmiAnalysisRunResult,
  fetchOmiAnalysisRunStatus,
  fetchOmiAnalysisTools,
  submitOmiAnalysisRun,
} = await import('../src/api.js');

test.beforeEach(() => {
  requests.length = 0;
  responseData = { ok: true };
  failureResponse = null;
});

test('analysis helpers use only the accepted control-plane endpoints', async () => {
  await fetchOmiAnalysisTools('example');
  await submitOmiAnalysisRun('example', {
    raw_idea: 'Exact owner text.',
    source_idea_id: 'idea_001',
    requested_adapters: ['spacy'],
    allow_deterministic_fallback: false,
    idempotency_key: 'owner-run-example-idea_001-abc123',
  });
  await fetchOmiAnalysisRunStatus('example', 'analysis-run-abc123');
  await fetchOmiAnalysisRunResult('example', 'analysis-run-abc123');

  assert.deepEqual(requests.map(({ method, url }) => [method, url]), [
    ['get', '/projects/example/omi/analysis/tools'],
    ['post', '/projects/example/omi/analysis/runs'],
    ['get', '/projects/example/omi/analysis/runs/analysis-run-abc123'],
    ['get', '/projects/example/omi/analysis/runs/analysis-run-abc123/result'],
  ]);
  assert.deepEqual(JSON.parse(requests[1].data), {
    raw_idea: 'Exact owner text.',
    source_idea_id: 'idea_001',
    requested_adapters: ['spacy'],
    allow_deterministic_fallback: false,
    idempotency_key: 'owner-run-example-idea_001-abc123',
  });
});

test('submission fails closed for missing source, tools, fallback ambiguity, and unsafe ids', async () => {
  const base = {
    raw_idea: 'Owner text',
    source_idea_id: 'idea_001',
    requested_adapters: ['spacy'],
    allow_deterministic_fallback: false,
    idempotency_key: 'owner-run-safe',
  };

  await assert.rejects(() => submitOmiAnalysisRun('example', { ...base, raw_idea: ' ' }), OmiAnalysisRunError);
  await assert.rejects(() => submitOmiAnalysisRun('example', { ...base, source_idea_id: '../bad' }));
  await assert.rejects(() => submitOmiAnalysisRun('example', { ...base, requested_adapters: [] }), OmiAnalysisRunError);
  await assert.rejects(() => submitOmiAnalysisRun('example', { ...base, requested_adapters: ['spacy', 'spacy'] }), OmiAnalysisRunError);
  await assert.rejects(() => submitOmiAnalysisRun('example', { ...base, allow_deterministic_fallback: true }), OmiAnalysisRunError);
  assert.equal(requests.length, 0);
});

test('transport failures preserve status and backend payload for actionable errors', async () => {
  failureResponse = { status: 409, data: { detail: 'idempotency conflict' } };

  await assert.rejects(
    () => fetchOmiAnalysisTools('example'),
    (error) => {
      assert.equal(error.name, 'OmiAnalysisRunError');
      assert.equal(error.status, 409);
      assert.deepEqual(error.payload, { detail: 'idempotency conflict' });
      return true;
    },
  );
});
