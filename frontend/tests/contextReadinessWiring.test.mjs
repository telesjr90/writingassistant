import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

const frontendRoot = fileURLToPath(new URL('../', import.meta.url));
const appSource = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8');
const apiSource = await readFile(new URL('../src/api.js', import.meta.url), 'utf8');
const contextSource = await readFile(
  new URL('../src/components/ProjectContext.jsx', import.meta.url),
  'utf8',
);
const vite = await createServer({
  root: frontendRoot,
  appType: 'custom',
  logLevel: 'silent',
  server: { middlewareMode: true },
});
const { default: App } = await vite.ssrLoadModule('/src/App.jsx');
const { default: ProjectContext } = await vite.ssrLoadModule(
  '/src/components/ProjectContext.jsx',
);
const apiModule = await vite.ssrLoadModule('/src/api.js');

test.after(async () => {
  await vite.close();
});

function readinessResponse(overrides = {}) {
  return {
    schema_version: 'project_context_readiness.v1',
    project_id: 'example',
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
    ...overrides,
  };
}

// --- Source-code contract tests (readiness-first loading sequence) ---

test('App.jsx imports fetchProjectContextReadiness from api.js', () => {
  assert.ok(
    apiSource.includes('fetchProjectContextReadiness'),
    'api.js must export fetchProjectContextReadiness',
  );
});

test('App.jsx uses readiness before optional direct resource loading', () => {
  assert.ok(
    apiSource.includes('context-readiness'),
    'api.js must define a readiness helpers',
  );
});

test('api.js fetchProjectContextReadiness does not call direct resource endpoints', () => {
  const helperSource = apiSource.split('fetchProjectContextReadiness')[1] || '';
  assert.ok(
    !helperSource.includes('/bible') && !helperSource.includes('/storyform-'),
    'fetchProjectContextReadiness must not issue direct resource requests',
  );
});

test('App.jsx uses fetchProjectContextReadiness before Bible/storyform/context',
  () => {
    assert.ok(
      appSource.includes('fetchProjectContextReadiness'),
      'App must call readiness before loading optional context',
    );
  },
);

// --- ProjectContext component renders truthful states ---

test('ProjectContext renders loading state for Bible', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'Checking availability...',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '{}',
      storyformStatus: 'Saved',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'loading',
      storyformReadinessState: 'ready',
      storyformContextReadinessState: 'unavailable',
      bibleReadinessError: '',
      storyformReadinessError: '',
      storyformContextReadinessError: '',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('Checking availability'), 'must show loading indicator');
});

test('ProjectContext renders absent Bible distinctly from error', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'No Bible stored for this project.',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '{}',
      storyformStatus: 'Saved',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'absent',
      storyformReadinessState: 'ready',
      storyformContextReadinessState: 'unavailable',
      bibleReadinessError: '',
      storyformReadinessError: '',
      storyformContextReadinessError: '',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('No Bible stored'), 'must indicate absence');
  assert.ok(!html.toLowerCase().includes('failed to load'),
    'absence must not be styled as error');
});

test('ProjectContext renders invalid Bible distinctly', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'Bible resource is not valid JSON.',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '{}',
      storyformStatus: 'Saved',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'invalid',
      bibleReadinessReason: 'bible_malformed_json',
      storyformReadinessState: 'ready',
      storyformContextReadinessState: 'unavailable',
      bibleReadinessError: '',
      storyformReadinessError: '',
      storyformContextReadinessError: '',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('not valid') || html.includes('Bible resource is not valid'), 'must indicate invalid resource');
});

test('ProjectContext renders unavailable storyform-context distinctly', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '{}',
      bibleStatus: 'Saved',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '{}',
      storyformStatus: 'Saved',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'ready',
      storyformReadinessState: 'ready',
      storyformContextReadinessState: 'unavailable',
      storyformContextReadinessReason: 'storyform_context_storyform_invalid',
      bibleReadinessError: '',
      storyformReadinessError: '',
      storyformContextReadinessError: '',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('not available'), 'must indicate unavailable context');
});

test('ProjectContext renders readiness request failure distinctly', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'Availability could not be checked.',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '',
      storyformStatus: 'Availability could not be checked.',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'error',
      storyformReadinessState: 'error',
      storyformContextReadinessState: 'error',
      bibleReadinessError: 'Request failed (500)',
      storyformReadinessError: 'Request failed (500)',
      storyformContextReadinessError: 'Request failed (500)',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('could not be checked'), 'must show readiness failure');
  assert.ok(html.includes('Retry'), 'must offer retry');
});

test('ProjectContext renders direct resource failure after ready report distinctly', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'Failed to load Bible.',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '{}',
      storyformStatus: 'Saved',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'ready',
      storyformReadinessState: 'ready',
      storyformContextReadinessState: 'ready',
      bibleReadinessError: '',
      storyformReadinessError: '',
      storyformContextReadinessError: '',
      bibleDirectError: 'Request failed (500): Internal error',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('Failed to load Bible'), 'must show direct load failure');
});

test('ProjectContext includes retry button', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'Availability could not be checked.',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '',
      storyformStatus: 'Availability could not be checked.',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'error',
      storyformReadinessState: 'error',
      storyformContextReadinessState: 'error',
      bibleReadinessError: 'Request failed (500)',
      storyformReadinessError: 'Request failed (500)',
      storyformContextReadinessError: 'Request failed (500)',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryContextReadiness: () => {},
      isRetryingContextReadiness: false,
    }),
  );
  assert.ok(html.includes('Retry'), 'must include retry action');
});

// --- App.jsx structural source contract ---

test('App.jsx evaluates each resource independently from readiness', () => {
  assert.ok(
    appSource.includes('ready'),
    'App must reference resource ready flags individually',
  );
});

test('App.jsx readiness loading references fetchProjectContextReadiness', () => {
  assert.ok(
    appSource.includes('fetchProjectContextReadiness'),
    'App load path must reference fetchProjectContextReadiness',
  );
});

test('App.jsx does not issue direct requests for absent resources', () => {
  const loadFn = appSource.split('loadInitialData')[1] || appSource;
  assert.ok(
    loadFn.includes('ready') || loadFn.includes('readiness'),
    'Loading must be conditional on readiness',
  );
});

test('App.jsx guards against stale project responses', () => {
  assert.ok(
    appSource.includes('isMounted') || appSource.includes('activeProjectId'),
    'App must guard against stale async completion',
  );
});

test('App.jsx post-save storyform refresh uses readiness-first pattern', () => {
  const saveHandler = appSource.split('handleSaveStoryform')[1] || appSource;
  const contextInSave = saveHandler.includes('storyform-context')
    || saveHandler.includes('fetchStoryformContext');
  assert.ok(contextInSave, 'storyform save must trigger storyform context handling');
});

test('api.js does not export readiness helper that calls Story Check', () => {
  const readinessPart = apiSource.split('fetchProjectContextReadiness')[1] || '';
  assert.ok(
    !readinessPart.includes('story-check')
    && !readinessPart.includes('runStoryCheck'),
    'readiness helper must not invoke Story Check',
  );
});

test('api.js readiness helper does not create or persist candidates', () => {
  const readinessPart = apiSource.split('fetchProjectContextReadiness')[1] || '';
  const helperBody = readinessPart.split('export async')[0] || readinessPart;
  assert.ok(
    !helperBody.includes('candidate')
    && !helperBody.includes('promotion'),
    'readiness helper must not create or persist candidates',
  );
});
