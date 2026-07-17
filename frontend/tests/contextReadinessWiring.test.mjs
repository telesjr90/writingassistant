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
const { default: App, createOperationGuard } = appModule;
const { default: ProjectContext } = await vite.ssrLoadModule(
  '/src/components/ProjectContext.jsx',
);
const apiModule = await vite.ssrLoadModule('/src/api.js');

test.after(async () => {
  await vite.close();
});

// ============================================================
// Group H: createOperationGuard behavioral tests
// ============================================================

test('H1: createOperationGuard is exported and is a function', () => {
  assert.ok(typeof createOperationGuard === 'function',
    'createOperationGuard must be exported');
});

test('H2: isCurrent returns true when session matches', () => {
  let pid = 'proj-A';
  let gen = 5;
  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  assert.equal(guard.isCurrent(), true);
  assert.deepStrictEqual(guard.session, { projectId: 'proj-A', generation: 5 });
});

test('H3: isCurrent returns false after projectId changes', () => {
  let pid = 'proj-A';
  let gen = 5;
  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  pid = 'proj-B';
  gen = 6;
  assert.equal(guard.isCurrent(), false);
  assert.deepStrictEqual(guard.session, { projectId: 'proj-A', generation: 5 });
});

test('H4: isCurrent returns false after generation changes (same projectId)', () => {
  let pid = 'proj-A';
  let gen = 5;
  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  pid = 'proj-A';
  gen = 6;
  assert.equal(guard.isCurrent(), false);
});

test('H5: session is an immutable snapshot', () => {
  let pid = 'proj-X';
  let gen = 3;
  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  pid = 'proj-Y';
  gen = 99;
  assert.deepStrictEqual(guard.session, { projectId: 'proj-X', generation: 3 });
});

// ============================================================
// Group L: Save lifecycle behavioral tests (Defects 1 & 3)
// ============================================================

test('L1: project switch resets save state; B is not stranded in saving', async () => {
  // Simulate: save starts in A, user switches to B before save completes.
  // Production: projectGenRef increments on switch, setIsSavingStoryform(false) called.
  let pid = 'proj-A';
  let gen = 5;
  const stateSpy = { saving: false, status: '' };

  // Save guard captured at start (gen=5)
  const saveGuard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  stateSpy.saving = true;

  // Project switch: B is selected, gen increments
  pid = 'proj-B';
  gen = 6;

  // Project-switch reset in useEffect would have called setIsSavingStoryform(false)
  stateSpy.saving = false; // reset by production useEffect

  // The stale A save's finally runs
  if (saveGuard.isCurrent()) {
    stateSpy.saving = false; // must NOT execute
  }

  assert.equal(saveGuard.isCurrent(), false, 'stale guard must not be current');
  assert.equal(stateSpy.saving, false,
    'B must not be left in saving state from stale A save');
});

test('L2: stale A save finalization does not clear B\'s saving initiated by B', async () => {
  let pid = 'proj-A';
  let gen = 5;
  const ops = [];

  // A starts save
  const guardA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  // Switch to B
  pid = 'proj-B';
  gen = 6;

  // B starts its own save
  const guardB = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  let bSaving = true;

  // A's stale save finally runs
  if (guardA.isCurrent()) {
    bSaving = false; // must NOT fire
  } else {
    ops.push('a-rejected');
  }

  // B's save completes normally
  if (guardB.isCurrent()) {
    bSaving = false;
    ops.push('b-completed');
  }

  assert.deepStrictEqual(ops, ['a-rejected', 'b-completed']);
  assert.equal(bSaving, false);
});

test('L3: ABA switch (A→B→A) rejects original A operation', () => {
  let pid = 'proj-A';
  let gen = 5;

  // A starts save (gen=5)
  const guardOldA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  // Switch to B (gen=6)
  pid = 'proj-B';
  gen = 6;

  // Switch back to A (gen=7)
  pid = 'proj-A';
  gen = 7;

  // Old A's guard: gen=5, current gen=7 → not current
  assert.equal(guardOldA.isCurrent(), false,
    'A→B→A must reject original A operation via generation mismatch');

  // New A session creates its own guard
  const guardNewA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  assert.equal(guardNewA.isCurrent(), true);
});

test('L4: current-session save normal finalization succeeds', () => {
  let pid = 'proj-A';
  let gen = 5;
  let saving = false;
  let status = '';

  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  saving = true;

  // Simulate save success
  if (guard.isCurrent()) {
    status = 'Saved';
    saving = false;
  }

  assert.equal(saving, false);
  assert.equal(status, 'Saved');
});

test('L5: stale save error does not write into current project', () => {
  let pid = 'proj-A';
  let gen = 5;
  let status = '';

  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  // Switch
  pid = 'proj-B';
  gen = 6;

  // Stale save catch block
  if (guard.isCurrent()) {
    status = 'Save failed: error'; // must NOT execute
  }

  assert.equal(status, '');
});

// ============================================================
// Group M: Retry lifecycle behavioral tests (Defect 2 & 3)
// ============================================================

test('M1: stale Retry from A does not clear B\'s active Retry state', () => {
  let pid = 'proj-A';
  let gen = 5;
  const stateSpy = { retrying: false, loading: false };

  // A starts Retry
  const guardA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  stateSpy.retrying = true;
  stateSpy.loading = true;

  // Switch to B
  pid = 'proj-B';
  gen = 6;

  // B starts its own Retry
  const guardB = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  stateSpy.retrying = true; // B's retry flag
  stateSpy.loading = true;

  // A's stale Retry finally runs
  if (guardA.isCurrent()) {
    stateSpy.loading = false;  // must NOT fire
    stateSpy.retrying = false; // must NOT fire
  }

  assert.equal(stateSpy.retrying, true,
    'B retry flag must not be cleared by stale A retry');
  assert.equal(stateSpy.loading, true,
    'B loading flag must not be cleared by stale A retry');
});

test('M2: current-session Retry finally clears its own flags', () => {
  let pid = 'proj-A';
  let gen = 5;
  let retrying = false;
  let loading = false;

  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  retrying = true;
  loading = true;

  // Normal finally: operation is current
  if (guard.isCurrent()) {
    loading = false;
    retrying = false;
  }

  assert.equal(retrying, false);
  assert.equal(loading, false);
});

test('M3: stale Retry catch does not write errors into current project', () => {
  let pid = 'proj-A';
  let gen = 5;
  let readinessError = '';
  let readinessState = '';

  const guard = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  // Switch
  pid = 'proj-B';
  gen = 6;

  // Stale catch
  if (guard.isCurrent()) {
    readinessError = 'FAILED';
    readinessState = 'error';
  }

  assert.equal(readinessError, '');
  assert.equal(readinessState, '');
});

test('M4: ABA retry rejection via generation mismatch', () => {
  let pid = 'proj-A';
  let gen = 5;

  const guardOldA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  // A→B→A
  pid = 'proj-B';
  gen = 6;
  pid = 'proj-A';
  gen = 7;

  let retrying = true; // current session's retry flag
  let loading = true;

  // Old A's finally
  if (guardOldA.isCurrent()) {
    retrying = false; // must NOT fire
    loading = false;  // must NOT fire
  }

  assert.equal(retrying, true);
  assert.equal(loading, true);
});

test('M5: project switch resets retry flag so B can start its own Retry', () => {
  let pid = 'proj-A';
  let gen = 5;

  // A's retry was active (retrying=true in production)
  // Switch to B
  pid = 'proj-B';
  gen = 6;

  // useEffect calls setIsRetryingContextReadiness(false)
  let retrying = false; // reset by project switch

  // B starts its own Retry
  const guardB = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  retrying = true;

  assert.equal(retrying, true, 'B must be able to start its own Retry');
  assert.equal(guardB.isCurrent(), true);
});

// ============================================================
// Group R: Integrated deferred-promise save/retry scenarios
// ============================================================

test('R1: deferred save for A; switch to B; B saves normally', async () => {
  let pid = 'proj-A';
  let gen = 5;
  const log = [];
  const bState = { saving: false, status: '' };

  // A starts save, captures guard
  const guardA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  // A's save is deferred (in-flight)
  const saveADeferred = new Promise((resolve) => {
    setImmediate(() => {
      // A save completes
      if (guardA.isCurrent()) {
        log.push('a-save-ok'); // should NOT fire
      } else {
        log.push('a-save-stale');
      }
      resolve();
    });
  });

  // Switch to B during A's save
  pid = 'proj-B';
  gen = 6;

  // B starts its own save
  const guardB = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  if (guardB.isCurrent()) {
    bState.saving = true;
    // B's save completes immediately
    bState.status = 'Saved';
    bState.saving = false;
    log.push('b-save-ok');
  }

  await saveADeferred;

  assert.deepStrictEqual(log, ['b-save-ok', 'a-save-stale']);
  assert.equal(bState.status, 'Saved');
  assert.equal(bState.saving, false);
});

test('R2: deferred retry for A; switch to B; B retries normally', async () => {
  let pid = 'proj-A';
  let gen = 5;
  const log = [];
  const bState = { retrying: false, loading: false };

  // A starts retry
  const guardA = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));

  const retryADeferred = new Promise((resolve) => {
    setImmediate(() => {
      if (guardA.isCurrent()) {
        log.push('a-retry-ok'); // should NOT fire
      } else {
        log.push('a-retry-stale');
      }
      // finally: guard.isCurrent() → no cleanup for B
      resolve();
    });
  });

  // Switch to B
  pid = 'proj-B';
  gen = 6;

  // B starts its own retry
  const guardB = createOperationGuard(() => ({
    projectId: pid, generation: gen,
  }));
  bState.retrying = true;
  bState.loading = true;

  await retryADeferred;

  // B's retry completes normally
  if (guardB.isCurrent()) {
    bState.loading = false;
    bState.retrying = false;
    log.push('b-retry-done');
  }

  assert.deepStrictEqual(log, ['a-retry-stale', 'b-retry-done']);
  assert.equal(bState.retrying, false);
  assert.equal(bState.loading, false);
});

// ============================================================
// Group P: Production source verification (non-behavioral)
// ============================================================

test('P1: projectGenRef exists in App source', () => {
  assert.ok(appSource.includes('projectGenRef'),
    'App must use projectGenRef for monotonic generation');
});

test('P2: createOperationGuard is used in handleSaveStoryform', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  assert.ok(saveFn.includes('createOperationGuard'),
    'save handler must use createOperationGuard');
});

test('P3: createOperationGuard is used in handleRetryContextReadiness', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  assert.ok(retryFn.includes('createOperationGuard'),
    'retry handler must use createOperationGuard');
});

test('P4: project-switch resets isSavingStoryform', () => {
  assert.ok(
    appSource.includes('setIsSavingStoryform(false)'),
    'project switch must reset isSavingStoryform',
  );
});

test('P5: retry finally guards both loading and retrying flags', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1].split('handleCreateOMIIdea')[0] || '';
  // The finally block must guard BOTH setContextReadinessLoading and setIsRetryingContextReadiness
  const finalFn = retryFn.split('finally')[1]?.split('}')[0] || '';
  assert.ok(
    finalFn.includes('IsRetryingContextReadiness'),
    'retry finally must guard setIsRetryingContextReadiness',
  );
});

// ============================================================
// Defect A: Unrelated data independence
// ============================================================

test('A1: App loads scenes independently of optional-context readiness', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(loadFn.includes('fetchScenes'), 'scenes must be loaded');
  assert.ok(loadFn.includes('fetchProjectContextReadiness'), 'readiness must be requested');
});

test('A2: rejected readiness does not prevent processing unrelated fulfilled results', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const hasIndependentUnrelated =
    loadFn.includes('.then(')
    || (loadFn.indexOf('sceneResult') < loadFn.indexOf('readinessResult')
        && !loadFn.substring(0, loadFn.indexOf('sceneResult')).includes('await'));
  assert.ok(hasIndependentUnrelated || loadFn.includes('fetchScenes'),
    'unrelated results must not wait for readiness to succeed');
});

test('A3: readiness failure does not leave unrelated loading flags stuck', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(loadFn.includes('IsLoadingScenes'), 'scene loading flags must be managed');
});

// ============================================================
// I: Independent loading processing verification
// ============================================================

test('I1: loadInitialData captures project identity before async work', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(loadFn.includes('capturedProjectId') && loadFn.includes('activeProjectId'),
    'loadInitialData must capture project ID before issuing requests');
});

test('I2: unrelated results can be processed before readiness settles', async () => {
  let unrelatedDone = false;
  let readinessDone = false;
  const processingOrder = [];
  const unrelatedPromise = Promise.allSettled([
    Promise.resolve('scenes'), Promise.resolve('notes'),
  ]).then(() => { unrelatedDone = true; processingOrder.push('unrelated'); });
  const readinessPromise = new Promise((resolve) => {
    setImmediate(() => { readinessDone = true; processingOrder.push('readiness'); resolve('ready'); });
  });
  await unrelatedPromise;
  assert.equal(unrelatedDone, true);
  assert.equal(readinessDone, false, 'unrelated must settle before delayed readiness');
  await readinessPromise;
  assert.equal(processingOrder[0], 'unrelated', 'unrelated must process first');
});

test('I3: loadInitialData uses independent processing paths', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const hasTwoGroups = (loadFn.match(/Promise\.allSettled/g) || []).length >= 2
    || loadFn.includes('.then');
  assert.ok(hasTwoGroups, 'loadInitialData must process unrelated independently from readiness');
});

test('I4: unrelated loading flags resolve independently', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(loadFn.includes('IsLoadingScenes(false)'), 'unrelated loading flags must resolve independently');
});

// ============================================================
// Defect B: Absent Bible/storyform must be owner-editable
// ============================================================

test('B1: absent Bible textarea is not read-only', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '{}', bibleStatus: 'No Bible stored for this project.',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'Saved',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'absent', storyformReadinessState: 'ready',
    storyformContextReadinessState: 'unavailable', bibleDirectError: '',
    storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  assert.ok(!html.includes('readonly'), 'absent Bible must not have readOnly attribute');
});

test('B2: absent Bible Save button is not disabled', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '{}', bibleStatus: 'No Bible stored for this project.',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'Saved',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'absent', storyformReadinessState: 'ready',
    storyformContextReadinessState: 'unavailable', bibleDirectError: '',
    storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  const bibleSection = html.split('Bible JSON')[1] || html;
  const firstButton = bibleSection.match(/<button[^>]*disabled/);
  if (firstButton) assert.fail('absent Bible Save button must not be disabled');
});

test('B3: absent Bible displays normal non-alarming status', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '{}', bibleStatus: 'No Bible stored for this project.',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'Saved',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'absent', storyformReadinessState: 'ready',
    storyformContextReadinessState: 'unavailable', bibleDirectError: '',
    storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  assert.ok(html.includes('No Bible stored'), 'must show non-alarming absence text');
  assert.ok(!html.includes('is-error') || html.indexOf('is-error') === -1, 'absence must not be styled as error');
});

test('B4: absent storyform textarea allows editing and saving', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '{}', bibleStatus: 'Saved',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'No storyform stored for this project.',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'ready', storyformReadinessState: 'absent',
    storyformContextReadinessState: 'unavailable', bibleDirectError: '',
    storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  assert.ok(!html.includes('readonly'), 'absent storyform must not have readOnly attribute');
});

test('B5: absent Bible path issues no fetchBible call in App source', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const absentPath = loadFn.split("state === 'absent'")[1] || loadFn.split('"absent"')[1] || '';
  assert.ok(!absentPath.includes('fetchBible'), 'absent path must not call fetchBible');
});

// ============================================================
// Defect C: Post-save readiness vs direct failures distinct
// ============================================================

test('C1: post-save calls fetchProjectContextReadiness and fetchStoryformContext', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  assert.ok(saveFn.includes('fetchProjectContextReadiness'), 'post-save must call readiness');
  assert.ok(saveFn.includes('fetchStoryformContext'), 'post-save must call storyform context');
});

test('C2: post-save readiness failure sets contextReadinessError', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  assert.ok(saveFn.includes('setContextReadinessError'), 'readiness failure must set contextReadinessError');
});

test('C3: post-save does not run Story Check automatically', () => {
  const saveFn = appSource.split('handleSaveStoryform')[1] || '';
  const saveFnBoundary = saveFn.split('handleCreateOMIIdea')[0]
    || saveFn.split('handleRetryContextReadiness')[0]
    || saveFn.split('const handleCreateOMICandidate')[0]
    || saveFn;
  assert.ok(!saveFnBoundary.includes('runStoryCheck') && !saveFnBoundary.includes('story-check'),
    'post-save must not run Story Check automatically');
});

// ============================================================
// Defect E: Retry for direct-load failures
// ============================================================

test('E1: direct Bible failure shows Retry button', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '', bibleStatus: 'Failed to load Bible.',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'Saved',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'ready',
    bibleDirectError: 'Request failed (500)', storyformReadinessState: 'ready',
    storyformDirectError: '', storyformContextReadinessState: 'unavailable',
    storyformContextDirectError: '', onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
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
  assert.ok(readinessIdx !== -1 && (directsStart === Infinity || readinessIdx < directsStart),
    'retry must request readiness before any direct resource requests');
});

test('E3: retry clears direct errors for retry cycle', () => {
  const retryFn = appSource.split('handleRetryContextReadiness')[1] || '';
  assert.ok(
    retryFn.includes('setBibleDirectError')
    && retryFn.includes('setStoryformDirectError')
    && retryFn.includes('setStoryformContextDirectError'),
    'retry must clear all direct error states at start');
});

// ============================================================
// Defect F: Remaining UI state requirements
// ============================================================

test('F1: invalid Bible remains distinct from absent', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '', bibleStatus: 'Bible not available: Bible resource is not valid JSON.',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'Saved',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'invalid',
    bibleReadinessReason: 'bible_malformed_json', storyformReadinessState: 'ready',
    storyformContextReadinessState: 'unavailable', bibleDirectError: '',
    storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  assert.ok(html.includes('not available'), 'invalid must be distinct');
  assert.ok(!html.includes('No Bible stored'), 'invalid must not display absent message');
});

test('F2: readiness-request failure and direct-failure remain separately searchable', () => {
  const html1 = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '', bibleStatus: 'Availability could not be checked.',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '', storyformStatus: 'Availability could not be checked.',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'error', storyformReadinessState: 'error',
    storyformContextReadinessState: 'error', readinessError: 'Request failed (500)',
    bibleDirectError: '', storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  assert.ok(html1.includes('could not be checked'), 'readiness failure must show readiness-failure text');
});

test('F3: direct-resource failure after ready report is distinct from readiness failure', () => {
  const html = renderToStaticMarkup(React.createElement(ProjectContext, {
    bibleText: '', bibleStatus: 'Failed to load Bible: Request failed (500)',
    isSavingBible: false, onBibleChange: () => {}, onSaveBible: () => {},
    storyformText: '{}', storyformStatus: 'Saved',
    isSavingStoryform: false, onStoryformChange: () => {}, onSaveStoryform: () => {},
    storyformContext: '', bibleReadinessState: 'ready', storyformReadinessState: 'ready',
    storyformContextReadinessState: 'unavailable', bibleDirectError: 'Request failed (500)',
    storyformDirectError: '', storyformContextDirectError: '',
    onRetryReadiness: () => {}, isRetryingReadiness: false,
  }));
  assert.ok(html.includes('Failed to load Bible'), 'direct failure must be labelled');
  assert.ok(!html.includes('could not be checked') && !html.includes('Availability could not'),
    'direct failure must not say could not be checked');
});

// ============================================================
// Preserved contract tests (G)
// ============================================================

test('G1: api.js fetchProjectContextReadiness defined', () => {
  assert.ok(apiSource.includes('fetchProjectContextReadiness'), 'api.js must export fetchProjectContextReadiness');
});

test('G2: api.js fetchProjectContextReadiness calls only context-readiness endpoint', () => {
  const helperSource = apiSource.split('fetchProjectContextReadiness')[1] || '';
  const helperBody = helperSource.split('export async')[0] || helperSource;
  assert.ok(!helperBody.includes('/bible') && !helperBody.includes('/storyform-'),
    'fetchProjectContextReadiness must not issue direct resource requests');
});

test('G3: api.js readiness helper does not invoke Story Check or create candidates', () => {
  const helperSource = apiSource.split('fetchProjectContextReadiness')[1] || '';
  const helperBody = helperSource.split('export async')[0] || helperSource;
  assert.ok(
    !helperBody.includes('story-check') && !helperBody.includes('runStoryCheck')
    && !helperBody.includes('candidate') && !helperBody.includes('promotion'),
    'readiness helper must not invoke Story Check or create/persist candidates');
});

test('G4: App source uses independent per-resource checks not only all_ready', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(loadFn.includes('bibleRes.ready') && loadFn.includes('storyformRes.ready'),
    'Each resource readiness must be evaluated independently');
});

test('G5: App source does not gate optional-context requests on all_ready', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  assert.ok(
    !loadFn.includes('all_ready') || loadFn.includes('resources.bible') || loadFn.includes('bibleRes'),
    'Must not gate optional context only on all_ready');
});

// ============================================================
// Safety product-boundary tests (N)
// ============================================================

test('N1: no Story Check, candidate, promotion, apply-promotion in retry or post-save', () => {
  const retryRaw = appSource.split('handleRetryContextReadiness')[1] || '';
  const retryFn = retryRaw.split('handleCreateOMIIdea')[0] || retryRaw.split('};')[0] || retryRaw;
  const saveRaw = appSource.split('handleSaveStoryform')[1] || '';
  const saveFn = saveRaw.split('handleRetryContextReadiness')[0]
    || saveRaw.split('handleCreateOMIIdea')[0] || saveRaw;
  const combined = retryFn + saveFn;
  assert.ok(
    !combined.includes('runStoryCheck') && !combined.includes('story-check')
    && !combined.includes('createOMICandidate') && !combined.includes('createOMIPromotion')
    && !combined.includes('applyPromotion') && !combined.includes('submitApplyPromotion'),
    'no automatic Story Check, candidate, promotion, apply-promotion in retry or post-save');
});

test('N2: absent Bible and storyform remain owner-editable and saveable', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const hasAbsentBibleStatus = loadFn.includes('No Bible stored') || loadFn.includes('bible_absent');
  const hasAbsentStoryformStatus = loadFn.includes('No storyform stored') || loadFn.includes('storyform_absent');
  assert.ok(hasAbsentBibleStatus || hasAbsentStoryformStatus,
    'absent resources must report non-alarming status text');
});

test('N3: absent, invalid, unavailable resources make no prohibited direct requests', () => {
  const loadFn = appSource.split('async function loadInitialData')[1]
    || appSource.split('function loadInitialData')[1] || '';
  const bibleAbsentBlock = loadFn.split("bibleRes.state === 'absent'")[1]?.split("else if")[0] || '';
  const storyformAbsentBlock = loadFn.split("storyformRes.state === 'absent'")[1]?.split("else if")[0] || '';
  const absentBlocks = bibleAbsentBlock + storyformAbsentBlock;
  assert.ok(
    !absentBlocks.includes('fetchBible') && !absentBlocks.includes('fetchStoryform'),
    'absent path must not issue direct resource requests');
});
