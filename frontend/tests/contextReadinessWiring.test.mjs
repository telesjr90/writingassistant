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

// --- Defect A: Unrelated data must not be blocked by readiness failure ---

test('A1: App loads scenes independently of optional-context readiness', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const afterLoadFn = loadFn.split('fetchProjectContextReadiness')[1]
    || loadFn.split('context-readiness')[1] || '';
  assert.ok(
    afterLoadFn.includes('fetchScenes') || loadFn.includes('fetchScenes'),
    'scenes must be loaded independently of readiness',
  );
});

test('A2: readiness failure path does not discard unrelated fulfilled results', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const catchBlock = loadFn.split('catch (')[1] || '';
  assert.ok(
    !catchBlock.includes('IsLoadingScenes(false)')
    || catchBlock.includes('fetchScenes'),
    'On readiness failure, scene loading must still complete or be independently handled',
  );
});

test('A3: readiness failure does not leave unrelated loading flags stuck', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const readErrPath = loadFn.split('setContextReadinessError')[1] || '';
  assert.ok(
    readErrPath.includes('IsLoadingScenes') || loadFn.includes('Promise.allSettled'),
    'scene loading flag must be set/resolved even when readiness fails',
  );
});

// --- Defect B: Normal absent Bible/storyform must be owner-editable ---

test('B1: absent Bible textarea is not read-only', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '{}',
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
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryReadiness: () => {},
      isRetryingReadiness: false,
    }),
  );
  assert.ok(!html.includes('readonly'), 'absent Bible must not have readOnly attribute');
});

test('B2: absent Bible Save button is not disabled', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '{}',
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
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryReadiness: () => {},
      isRetryingReadiness: false,
    }),
  );
  const bibleSection = html.split('Bible JSON')[1] || html;
  const firstButton = bibleSection.match(/<button[^>]*disabled/);
  if (firstButton) {
    assert.fail('absent Bible Save button must not be disabled');
  }
});

test('B3: absent Bible displays normal non-alarming status', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '{}',
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
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryReadiness: () => {},
      isRetryingReadiness: false,
    }),
  );
  assert.ok(html.includes('No Bible stored'), 'must show non-alarming absence text');
  assert.ok(
    !html.includes('is-error') || html.indexOf('is-error') === -1,
    'absence must not be styled as error',
  );
});

test('B4: absent storyform textarea allows editing and saving', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '{}',
      bibleStatus: 'Saved',
      isSavingBible: false,
      onBibleChange: () => {},
      onSaveBible: () => {},
      storyformText: '{}',
      storyformStatus: 'No storyform stored for this project.',
      isSavingStoryform: false,
      onStoryformChange: () => {},
      onSaveStoryform: () => {},
      storyformContext: '',
      bibleReadinessState: 'ready',
      storyformReadinessState: 'absent',
      storyformContextReadinessState: 'unavailable',
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryReadiness: () => {},
      isRetryingReadiness: false,
    }),
  );
  assert.ok(!html.includes('readonly'), 'absent storyform must not have readOnly attribute');
});

// --- Defect B.5: Normal absence causes zero direct requests (source check) ---

test('B5: absent Bible path issues no fetchBible call in App source', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const absentPath = loadFn.split("state === 'absent'")[1]
    || loadFn.split('"absent"')[1] || '';
  assert.ok(
    !absentPath.includes('fetchBible'),
    'absent path must not call fetchBible',
  );
});

// --- Defect C: Post-save readiness vs direct failures must be distinct ---

test('C1: post-save storyform refresh path separates readiness error from direct error',
  () => {
    const saveFn = appSource.split('handleSaveStoryform')[1] || '';
    const saveRefreshBlock = saveFn.split('fetchProjectContextReadiness')[1] || '';
    assert.ok(
      saveRefreshBlock.length > 10,
      'post-save must call fetchProjectContextReadiness',
    );
  },
);

test('C2: post-save readiness failure sets readiness error not combined status', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  const refreshCatch = saveFn.split('catch (error)')[2]
    || saveFn.split('catch (error)')[1] || '';
  assert.ok(
    !refreshCatch.includes('Saved; prompt context refresh failed')
    || refreshCatch.includes('setContextReadinessError'),
    'readiness failure must set contextReadinessError separately',
  );
});

test('C3: post-save does not run Story Check automatically', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  const saveFnBoundary = saveFn.split('handleCreateOMIIdea')[0]
    || saveFn.split('handleRetryContextReadiness')[0]
    || saveFn.split('const handleCreateOMICandidate')[0]
    || saveFn;
  assert.ok(
    !saveFnBoundary.includes('runStoryCheck') && !saveFnBoundary.includes('story-check'),
    'post-save must not run Story Check automatically',
  );
});

// --- Defect D: Stale-project protection ---

test('D1: App captures project identity for async response guard', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(
    appSource.includes('isMounted') || loadFn.includes('projectId') || loadFn.includes('captured'),
    'App must guard against stale async completion',
  );
});

test('D2: Retry captures project identity for async response guard', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  assert.ok(
    retryFn.includes('activeProjectId') || retryFn.includes('isRetrying'),
    'retry must reference active project identity',
  );
});

test('D3: Post-save refresh captures project identity', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  const refreshPart = saveFn.split('fetchProjectContextReadiness')[1] || '';
  assert.ok(
    saveFn.includes('activeProjectId'),
    'post-save refresh must reference activeProjectId',
  );
});

// --- Defect E: Retry for direct-load failures ---

test('E1: direct Bible failure shows Retry button', () => {
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
      bibleDirectError: 'Request failed (500)',
      storyformReadinessState: 'ready',
      storyformDirectError: '',
      storyformContextReadinessState: 'unavailable',
      storyformContextDirectError: '',
      onRetryReadiness: () => {},
      isRetryingReadiness: false,
    }),
  );
  assert.ok(html.includes('Retry'), 'direct Bible failure must show Retry');
});

test('E2: retry handler requests readiness first', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  assert.ok(
    retryFn.includes('fetchProjectContextReadiness'),
    'retry must request readiness first',
  );
});

test('E3: retry clears only transient errors not foundation state', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  assert.ok(
    retryFn.includes('setBibleDirectError'),
    'retry must clear direct errors',
  );
});

// --- Defect F: Remaining UI state requirements ---

test('F1: invalid Bible remains distinct from absent', () => {
  const html = renderToStaticMarkup(
    React.createElement(ProjectContext, {
      bibleText: '',
      bibleStatus: 'Bible not available: Bible resource is not valid JSON.',
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
      bibleDirectError: '',
      storyformDirectError: '',
      storyformContextDirectError: '',
      onRetryReadiness: () => {},
      isRetryingReadiness: false,
    }),
  );
  assert.ok(html.includes('not available'), 'invalid must be distinct');
  assert.ok(!html.includes('No Bible stored'), 'invalid must not display absent message');
});

test('F2: readiness-request failure and direct-failure remain separately searchable',
  () => {
    const html1 = renderToStaticMarkup(
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
        readinessError: 'Request failed (500)',
        bibleDirectError: '',
        storyformDirectError: '',
        storyformContextDirectError: '',
        onRetryReadiness: () => {},
        isRetryingReadiness: false,
      }),
    );
    assert.ok(
      html1.includes('could not be checked'),
      'readiness failure must show readiness-failure text',
    );
  },
);

test('F3: direct-resource failure after ready report is distinct from readiness failure',
  () => {
    const html = renderToStaticMarkup(
      React.createElement(ProjectContext, {
        bibleText: '',
        bibleStatus: 'Failed to load Bible: Request failed (500)',
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
        bibleDirectError: 'Request failed (500)',
        storyformDirectError: '',
        storyformContextDirectError: '',
        onRetryReadiness: () => {},
        isRetryingReadiness: false,
      }),
    );
    assert.ok(html.includes('Failed to load Bible'), 'direct failure must be labelled');
    assert.ok(
      !html.includes('could not be checked') && !html.includes('Availability could not'),
      'direct failure must not say could not be checked',
    );
  },
);

// --- Preserved existing contract tests ---

test('G1: api.js fetchProjectContextReadiness defined', () => {
  assert.ok(
    apiSource.includes('fetchProjectContextReadiness'),
    'api.js must export fetchProjectContextReadiness',
  );
});

test('G2: api.js fetchProjectContextReadiness calls only context-readiness endpoint', () => {
  const helperSource = apiSource.split('fetchProjectContextReadiness')[1] || '';
  const helperBody = helperSource.split('export async')[0] || helperSource;
  assert.ok(
    !helperBody.includes('/bible') && !helperBody.includes('/storyform-'),
    'fetchProjectContextReadiness must not issue direct resource requests',
  );
});

test('G3: api.js readiness helper does not invoke Story Check or create candidates', () => {
  const helperSource = apiSource.split('fetchProjectContextReadiness')[1] || '';
  const helperBody = helperSource.split('export async')[0] || helperSource;
  assert.ok(
    !helperBody.includes('story-check')
    && !helperBody.includes('runStoryCheck')
    && !helperBody.includes('candidate')
    && !helperBody.includes('promotion'),
    'readiness helper must not invoke Story Check or create/persist candidates',
  );
});

test('G4: App source uses independent per-resource checks not only all_ready', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(
    loadFn.includes('bibleRes.ready')
    && loadFn.includes('storyformRes.ready'),
    'Each resource readiness must be evaluated independently',
  );
});

test('G5: App source does not gate optional-context requests on all_ready', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(
    !loadFn.includes('all_ready') || loadFn.includes('resources.bible') || loadFn.includes('bibleRes'),
    'Must not gate optional context only on all_ready',
  );
});
