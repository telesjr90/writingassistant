import assert from 'node:assert/strict';
import test from 'node:test';

import {
  analysisToolReason,
  buildAnalysisSourceOptions,
  describeAnalysisRunState,
  isAnalysisToolRunnable,
} from '../src/omiAnalysisRunWorkflow.js';

test('source options preserve exact owner text and reject unsafe or empty records', () => {
  const exact = 'Owner café note.\nSecond line.';
  const options = buildAnalysisSourceOptions([
    { idea_id: 'idea_safe', raw_idea: exact, status: 'draft' },
    { idea_id: '../unsafe', raw_idea: 'Unsafe' },
    { idea_id: 'idea_empty', raw_idea: '   ' },
  ]);

  assert.equal(options.length, 1);
  assert.equal(options[0].id, 'idea_safe');
  assert.equal(options[0].rawIdea, exact);
  assert.equal(options[0].label, 'Owner café note. Second line.');
});

test('only explicitly enabled, runtime-enabled, unblocked tools are runnable', () => {
  const enabled = {
    adapter_id: 'spacy',
    selectable: true,
    preflight_status: 'enabled',
    readiness: { runtime_enabled: true, blocked: false },
  };

  assert.equal(isAnalysisToolRunnable(enabled), true);
  assert.equal(isAnalysisToolRunnable({ ...enabled, preflight_status: 'available' }), false);
  assert.equal(isAnalysisToolRunnable({ ...enabled, readiness: { runtime_enabled: false } }), false);
  assert.equal(isAnalysisToolRunnable({ ...enabled, readiness: { runtime_enabled: true, blocked: true } }), false);
});

test('tool reasons distinguish blocked, available, unavailable, configuration, and error states', () => {
  assert.equal(
    analysisToolReason({ preflight_status: 'blocked', readiness: { blocked: true, blocked_reason: 'Owner gate.' } }),
    'Owner gate.',
  );
  assert.match(analysisToolReason({ preflight_status: 'available', readiness: {} }), /flags are disabled/);
  assert.match(analysisToolReason({ preflight_status: 'unavailable', readiness: {} }), /unavailable/);
  assert.match(analysisToolReason({ preflight_status: 'not_configured', readiness: {} }), /not configured/);
  assert.match(analysisToolReason({ preflight_status: 'error', readiness: {} }), /failed closed/);
});

test('run states expose honest final, partial, failed, timeout, and not-started labels', () => {
  assert.deepEqual(describeAnalysisRunState('complete'), {
    state: 'complete', label: 'Succeeded', tone: 'is-success',
  });
  assert.equal(describeAnalysisRunState('partial').label, 'Partial results');
  assert.equal(describeAnalysisRunState('error').tone, 'is-error');
  assert.equal(describeAnalysisRunState('timeout').label, 'Timed out');
  assert.equal(describeAnalysisRunState(undefined).label, 'Not started');
});
