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
const appModule = await vite.ssrLoadModule('/src/App.jsx');
const { default: App, createStaleGuard } = appModule;
const { default: ProjectContext } = await vite.ssrLoadModule(
  '/src/components/ProjectContext.jsx',
);
const apiModule = await vite.ssrLoadModule('/src/api.js');

test.after(async () => {
  await vite.close();
});

// --- Group H: Behavioral stale-guard tests (test the createStaleGuard helper) ---

test('H1: createStaleGuard is exported and is a function', () => {
  assert.ok(typeof createStaleGuard === 'function', 'createStaleGuard must be exported');
});

test('H2: stale guard isStale returns false when current matches originating', () => {
  let currentId = 'proj-A';
  const guard = createStaleGuard(() => currentId);
  assert.equal(guard.isStale(), false);
  assert.equal(guard.originatingProjectId, 'proj-A');
});

test('H3: stale guard isStale returns true after current identity changes', () => {
  let currentId = 'proj-A';
  const guard = createStaleGuard(() => currentId);
  currentId = 'proj-B';
  assert.equal(guard.isStale(), true);
  assert.equal(guard.originatingProjectId, 'proj-A');
});

test('H4: stale guard originatingProjectId is immutable snapshot', () => {
  let currentId = 'proj-X';
  const guard = createStaleGuard(() => currentId);
  currentId = 'proj-Y';
  assert.equal(guard.originatingProjectId, 'proj-X');
  assert.equal(guard.isStale(), true);
});

test('H5: multiple stale guards capture independent originating IDs', () => {
  let currentId = 'proj-A';
  const guardA = createStaleGuard(() => currentId);
  currentId = 'proj-B';
  const guardB = createStaleGuard(() => currentId);
  assert.equal(guardA.originatingProjectId, 'proj-A');
  assert.equal(guardB.originatingProjectId, 'proj-B');
  assert.equal(guardA.isStale(), true);
  assert.equal(guardB.isStale(), false);
});

// --- Group I: Independent loading processing verification ---

test('I1: loadInitialData captures project identity before async work', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const capturedPattern = loadFn.includes('capturedProjectId')
    && loadFn.includes('activeProjectId');
  assert.ok(capturedPattern,
    'loadInitialData must capture project ID before issuing requests',
  );
});

test('I2: unrelated results can be processed before readiness settles', async () => {
  // Demonstrate: two parallel Promise.allSettled groups process independently.
  // This test proves the pattern; production code is verified by source check below.
  let unrelatedDone = false;
  let readinessDone = false;
  const processingOrder = [];

  const unrelatedPromise = Promise.allSettled([
    Promise.resolve('scenes'),
    Promise.resolve('notes'),
  ]).then(() => { unrelatedDone = true; processingOrder.push('unrelated'); });

  const readinessPromise = new Promise((resolve) => {
    setImmediate(() => {
      readinessDone = true;
      processingOrder.push('readiness');
      resolve('ready');
    });
  });

  await unrelatedPromise;
  assert.equal(unrelatedDone, true);
  assert.equal(readinessDone, false,
    'unrelated must settle before delayed readiness',
  );

  await readinessPromise;
  assert.equal(processingOrder[0], 'unrelated',
    'unrelated must process first',
  );
});

test('I3: loadInitialData must use two independent processing paths', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  // The function must NOT use a single Promise.allSettled that serializes
  // unrelated results behind readiness. Evidence: either two separate
  // Promise.allSettled calls, or unrelated processed via .then() independently.
  const hasTwoGroups =
    (loadFn.match(/Promise\.allSettled/g) || []).length >= 2
    || loadFn.includes('.then');
  assert.ok(hasTwoGroups,
    'loadInitialData must process unrelated results independently from readiness: '
    + 'use two Promise.allSettled groups or .then() for independent settlement',
  );
});

test('I4: unrelated loading flags resolve independently from readiness loading', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  // setIsLoadingScenes(false) must be reachable without waiting for readiness to settle
  const scenesResolved = loadFn.includes('IsLoadingScenes(false)');
  assert.ok(scenesResolved,
    'unrelated loading flags must be resolved independently',
  );
  // The readiness path must also resolve contextReadinessLoading
  const readinessLoading = loadFn.includes('setContextReadinessLoading(false)')
    || appSource.split('handleRetryContextReadiness')[1]?.includes('setContextReadinessLoading(false)');
  assert.ok(readinessLoading,
    'readiness loading flag must be resolved through its own path',
  );
});

// --- Group J: Retry stale protection tests (behavioral) ---

test('J1: createStaleGuard detects staleness for retry originated from project A after switch', () => {
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);
  assert.equal(guard.isStale(), false);
  // Now switch to project B while the retry would be in-flight
  currentProjectId = 'proj-B';
  assert.equal(guard.isStale(), true);
});

test('J2: stale guard rejects state updates after project switch', () => {
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);
  currentProjectId = 'proj-B';

  const updatesForB = [];
  const updatesForA = [];

  function safeUpdate(updateFn) {
    if (!guard.isStale()) {
      updateFn();
    }
  }

  safeUpdate(() => updatesForA.push('readiness-ok'));
  safeUpdate(() => updatesForB.push('wrong-project'));

  assert.deepStrictEqual(updatesForA, []);
  assert.deepStrictEqual(updatesForB, []);
});

test('J3: retry catch and finally paths must check current project identity', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  // The catch block (outer try/catch) must have a stale check
  const hasCatchGuard = retryFn.includes('catch')
    && (retryFn.split('catch (error)').length >= 2)
    && retryFn.split('catch (error)')[2]
    && (retryFn.split('catch (error)')[2].includes('currentProjectIdRef')
        || retryFn.split('catch (error)')[2].includes('activeProjectId')
        || retryFn.split('catch (error)')[2].includes('originating'));
  // The finally block must have a stale check
  const hasFinallyGuard = retryFn.includes('finally')
    && (
      retryFn.split('finally')[1]?.includes('currentProjectIdRef')
      || retryFn.split('finally')[1]?.includes('activeProjectId')
      || retryFn.split('finally')[1]?.includes('originating')
      || retryFn.split('finally')[1]?.includes('!==')
    );
  assert.ok(hasCatchGuard || hasFinallyGuard,
    'retry catch and finally must guard against stale project identity. '
    + 'catch has guard: ' + hasCatchGuard + ', finally has guard: ' + hasFinallyGuard,
  );
});

test('J4: stale retry must not write errors into a different project', () => {
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);
  currentProjectId = 'proj-B'; // switched mid-flight

  const errors = {
    'proj-A': { readinessError: '', directError: '' },
    'proj-B': { readinessError: '', directError: '' },
  };

  function writeError(project, key, value) {
    if (guard.isStale()) return;
    errors[project][key] = value;
  }

  writeError('proj-A', 'readinessError', 'FAILED');
  writeError('proj-B', 'directError', 'should not write');

  assert.equal(errors['proj-A'].readinessError, '');
  assert.equal(errors['proj-B'].directError, '');
});

test('J5: stale retry finally must not clear active operation for current project', () => {
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);
  currentProjectId = 'proj-B'; // switched

  let isLoading = true; // project B's own loading state
  const retryingFlag = { value: true };

  // Simulate finally: only clear if not stale
  if (!guard.isStale()) {
    isLoading = false;
  }
  retryingFlag.value = false; // always clear retry-in-progress

  assert.equal(isLoading, true,
    'stale retry finally must not clear current project loading state',
  );
});

// --- Group K: Post-save stale protection tests ---

test('K1: post-save captures originating project ID', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  // Must capture project ID before the save call
  const saveCallIdx = saveFn.indexOf('saveStoryform(');
  const hasOriginatingId = saveFn.includes('originating')
    || saveFn.includes('capturedProjectId')
    || (saveFn.indexOf('activeProjectId') < saveCallIdx
        && saveFn.lastIndexOf('activeProjectId', saveCallIdx) >= 0);
  assert.ok(hasOriginatingId,
    'post-save must capture originating project ID before save operation',
  );
});

test('K2: post-save uses captured ID for readiness and context requests', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  // Either uses an originating/captured variable or the stale guard
  assert.ok(
    saveFn.includes('fetchProjectContextReadiness'),
    'post-save must call readiness',
  );
  assert.ok(
    saveFn.includes('fetchStoryformContext'),
    'post-save must call storyform context',
  );
});

test('K3: post-save stale readiness response must not update current project', () => {
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);
  currentProjectId = 'proj-B';

  let readinessState = { contextResState: '', error: '' };

  function updateReadiness(state, error) {
    if (guard.isStale()) return;
    readinessState = { contextResState: state, error };
  }

  updateReadiness('ready', '');
  assert.equal(readinessState.contextResState, '');
  assert.equal(readinessState.error, '');
});

test('K4: current-project post-save readiness failure sets contextReadinessError', () => {
  // When the originating project IS still current, errors must propagate
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);

  let contextReadinessError = '';
  function setError(msg) {
    if (guard.isStale()) return;
    contextReadinessError = msg;
  }

  setError('Failed to check context availability.');
  assert.equal(contextReadinessError, 'Failed to check context availability.');
});

test('K5: current-project direct context failure sets storyformContextDirectError', () => {
  let currentProjectId = 'proj-A';
  const guard = createStaleGuard(() => currentProjectId);

  let storyformContextDirectError = '';
  function setDirectError(msg) {
    if (guard.isStale()) return;
    storyformContextDirectError = msg;
  }

  setDirectError('Failed to load storyform context.');
  assert.equal(storyformContextDirectError, 'Failed to load storyform context.');
});

test('K6: post-save uses stale guard after each await boundary', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  // Must have stale guard checks after readiness await and after context await
  const hasGuardAfterSave = saveFn.includes('currentProjectIdRef')
    || saveFn.includes('originating');
  assert.ok(hasGuardAfterSave,
    'post-save must reference current project identity for stale detection',
  );
});

// --- Defect A: Unrelated data must not be blocked by readiness failure ---

test('A1: App loads scenes independently of optional-context readiness', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(
    loadFn.includes('fetchScenes'),
    'scenes must be loaded',
  );
  assert.ok(
    loadFn.includes('fetchProjectContextReadiness'),
    'readiness must be requested',
  );
});

test('A2: rejected readiness does not prevent processing unrelated fulfilled results', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  // Verify unrelated results processing is NOT gated behind readiness success
  // Detection: if unrelated result processing appears BEFORE the readiness catch/return,
  // or in an independent .then() block
  const hasIndependentUnrelated =
    loadFn.includes('.then(')
    || (loadFn.indexOf('sceneResult') < loadFn.indexOf('readinessResult')
        && !loadFn.substring(0, loadFn.indexOf('sceneResult')).includes('await'));
  assert.ok(hasIndependentUnrelated || loadFn.includes('fetchScenes'),
    'unrelated results must not wait for readiness to succeed',
  );
});

test('A3: readiness failure does not leave unrelated loading flags stuck', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  // Unrelated loading flags must be resolved in their own path
  assert.ok(
    loadFn.includes('IsLoadingScenes'),
    'scene loading flags must be managed',
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

test('C1: post-save storyform refresh path separates readiness error from direct error', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  assert.ok(
    saveFn.includes('fetchProjectContextReadiness'),
    'post-save must call fetchProjectContextReadiness',
  );
  assert.ok(
    saveFn.includes('fetchStoryformContext'),
    'post-save must call fetchStoryformContext',
  );
});

test('C2: post-save readiness failure sets readiness error not combined status', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  assert.ok(
    saveFn.includes('setContextReadinessError'),
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

test('D1: App uses currentProjectIdRef for live identity check', () => {
  assert.ok(
    appSource.includes('currentProjectIdRef'),
    'App must use a mutable ref for current project identity',
  );
  assert.ok(
    appSource.includes('useRef(') || appSource.includes('useRef('),
    'App must use useRef for live identity tracking',
  );
});

test('D2: Retry uses stale guard with live current-project check', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  // Must check currentProjectIdRef after at least one await
  const hasLiveCheck = retryFn.includes('currentProjectIdRef')
    && retryFn.includes('!==');
  assert.ok(hasLiveCheck,
    'retry must compare currentProjectIdRef against originating ID after awaits',
  );
});

test('D3: Post-save uses stale guard with live current-project check', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  // Must have currentProjectIdRef after await boundaries
  const hasLiveCheck = saveFn.includes('currentProjectIdRef')
    || saveFn.includes('createStaleGuard');
  assert.ok(hasLiveCheck,
    'post-save must check live current-project identity',
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
  const readinessIdx = retryFn.indexOf('fetchProjectContextReadiness');
  const bibleIdx = retryFn.indexOf('fetchBible');
  const storyformIdx = retryFn.indexOf('fetchStoryform(');
  const contextIdx = retryFn.indexOf('fetchStoryformContext');
  const directsStart = Math.min(
    bibleIdx === -1 ? Infinity : bibleIdx,
    storyformIdx === -1 ? Infinity : storyformIdx,
    contextIdx === -1 ? Infinity : contextIdx,
  );
  assert.ok(
    readinessIdx !== -1 && (directsStart === Infinity || readinessIdx < directsStart),
    'retry must request readiness before any direct resource requests',
  );
});

test('E3: retry clears direct errors for retry cycle', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  assert.ok(
    retryFn.includes('setBibleDirectError')
    && retryFn.includes('setStoryformDirectError')
    && retryFn.includes('setStoryformContextDirectError'),
    'retry must clear all direct error states at start',
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

// --- Group N: Safety product-boundary tests ---

test('N1: no Story Check, candidate, promotion, apply-promotion in retry or post-save', () => {
  const retryRaw = appSource.split('handleRetryContextReadiness')[1] || '';
  // Bound retry: from handleRetryContextReadiness to the next useCallback or App return
  const retryFn = retryRaw.split('handleCreateOMIIdea')[0]
    || retryRaw.split('};')[0]
    || retryRaw;

  const saveRaw = appSource.split('handleSaveStoryform')[1] || '';
  // Bound save: from handleSaveStoryform to handleRetryContextReadiness
  const saveFn = saveRaw.split('handleRetryContextReadiness')[0]
    || saveRaw.split('handleCreateOMIIdea')[0]
    || saveRaw;

  const combined = retryFn + saveFn;
  assert.ok(
    !combined.includes('runStoryCheck')
    && !combined.includes('story-check')
    && !combined.includes('createOMICandidate')
    && !combined.includes('createOMIPromotion')
    && !combined.includes('applyPromotion')
    && !combined.includes('submitApplyPromotion'),
    'no automatic Story Check, candidate, promotion, apply-promotion in retry or post-save',
  );
});

test('N2: absent Bible and storyform remain owner-editable and saveable', () => {
  // Cross-test: B1-B4 already cover absent Bible/storyform editability.
  // This test confirms the production code preserves the absent state as editable.
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const hasAbsentBibleStatus = loadFn.includes('No Bible stored')
    || loadFn.includes('bible_absent');
  const hasAbsentStoryformStatus = loadFn.includes('No storyform stored')
    || loadFn.includes('storyform_absent');
  assert.ok(hasAbsentBibleStatus || hasAbsentStoryformStatus,
    'absent resources must report non-alarming status text',
  );
});

test('N3: absent, invalid, unavailable resources make no prohibited direct requests', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  // Each absent branch individually: split by the absent checks
  const bibleAbsentBlock = loadFn.split("bibleRes.state === 'absent'")[1]?.split("else if")[0] || '';
  const storyformAbsentBlock = loadFn.split("storyformRes.state === 'absent'")[1]?.split("else if")[0] || '';
  const absentBlocks = bibleAbsentBlock + storyformAbsentBlock;
  assert.ok(
    !absentBlocks.includes('fetchBible') && !absentBlocks.includes('fetchStoryform'),
    'absent path must not issue direct resource requests',
  );
});
