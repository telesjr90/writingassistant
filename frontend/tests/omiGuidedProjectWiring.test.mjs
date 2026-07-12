import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import { createServer } from 'vite';

const frontendRoot = fileURLToPath(new URL('../', import.meta.url));
const appSource = await readFile(new URL('../src/App.jsx', import.meta.url), 'utf8');
const componentSource = await readFile(
  new URL('../src/components/OmiGuidedProjectCreation.jsx', import.meta.url),
  'utf8',
);
const vite = await createServer({
  root: frontendRoot,
  appType: 'custom',
  logLevel: 'silent',
  server: { middlewareMode: true },
});
const {
  requireCompleteOmiGuidedProjectResponse,
  upsertGuidedProjectMetadata,
} = await vite.ssrLoadModule('/src/App.jsx');
const { getGuidedCreationFailureMessage } = await vite.ssrLoadModule(
  '/src/components/OmiGuidedProjectCreation.jsx',
);

test.after(async () => {
  await vite.close();
});

function completeResponse() {
  return {
    status: 'complete',
    project_id: 'returned-project',
    title: 'Returned Project',
    creation_method: 'omi_guided',
    omi_idea_id: 'idea-returned',
    setup_note_id: 'omi_guided_setup_notes',
    project_metadata: {
      project_id: 'returned-project',
      title: 'Returned Project',
      creation_method: 'omi_guided',
      created_at: '2026-07-12T00:00:00Z',
      updated_at: '2026-07-12T00:00:01Z',
      omi_guided_creation: {
        status: 'complete',
        omi_idea_id: 'idea-returned',
        setup_note_id: 'omi_guided_setup_notes',
      },
    },
  };
}

test('App completion validation requires the complete guided contract and linked identifiers', () => {
  const response = completeResponse();
  assert.equal(
    requireCompleteOmiGuidedProjectResponse(response),
    response.project_metadata,
  );

  for (const field of ['omi_idea_id', 'setup_note_id']) {
    const malformed = completeResponse();
    delete malformed[field];
    assert.throws(
      () => requireCompleteOmiGuidedProjectResponse(malformed),
      (error) => error.code === 'malformed_guided_creation_response',
    );
  }

  for (const mutation of [
    (value) => { value.status = 'failed_rolled_back'; },
    (value) => { value.status = 'recovery_required'; },
    (value) => { value.creation_method = 'blank'; },
    (value) => { value.project_metadata.omi_guided_creation.status = 'pending'; },
    (value) => { value.project_metadata.omi_guided_creation.omi_idea_id = 'other'; },
    (value) => { delete value.project_id; },
  ]) {
    const malformed = completeResponse();
    mutation(malformed);
    assert.throws(
      () => requireCompleteOmiGuidedProjectResponse(malformed),
      (error) => error.code === 'malformed_guided_creation_response',
    );
  }
});

test('returned project metadata is added once and replaces a matching existing entry', () => {
  const metadata = completeResponse().project_metadata;
  const added = upsertGuidedProjectMetadata(
    [{ project_id: 'existing', title: 'Existing' }],
    metadata,
  );
  assert.deepEqual(added, [
    { project_id: 'existing', title: 'Existing' },
    metadata,
  ]);

  const replaced = upsertGuidedProjectMetadata(
    [
      { project_id: 'existing', title: 'Existing' },
      { project_id: 'returned-project', title: 'Stale' },
      metadata,
    ],
    metadata,
  );
  assert.equal(replaced.length, 2);
  assert.equal(replaced[1], metadata);
});

test('failure messages distinguish rollback, recovery, validation, network, and malformed results', () => {
  const rolledBack = getGuidedCreationFailureMessage({
    payload: { status: 'failed_rolled_back' },
  });
  assert.match(rolledBack, /incomplete project was removed/i);

  const recovery = getGuidedCreationFailureMessage({
    payload: { status: 'recovery_required', project_id: 'recovery-project' },
  });
  assert.match(recovery, /Recovery required/);
  assert.match(recovery, /recovery-project/);

  const unsafeRecovery = getGuidedCreationFailureMessage({
    payload: { status: 'recovery_required', project_id: '/private/project' },
  });
  assert.doesNotMatch(unsafeRecovery, /private/);

  assert.match(getGuidedCreationFailureMessage({ status: 400 }), /rejected/i);
  assert.match(
    getGuidedCreationFailureMessage({
      name: 'OmiGuidedProjectCreationError',
      status: null,
    }),
    /local service/i,
  );
  assert.match(
    getGuidedCreationFailureMessage({ code: 'malformed_guided_creation_response' }),
    /incomplete response/i,
  );
});

test('component submits exact idea and notes, guards duplicates, and resets only after verified success', () => {
  assert.match(componentSource, /onCreateGuidedProject\(\{[\s\S]*rawIdea: draft\.rawIdea,[\s\S]*setupNotes: draft\.setupNotes,/);
  assert.doesNotMatch(componentSource, /rawIdea:\s*draft\.rawIdea\.trim\(\)/);
  assert.doesNotMatch(componentSource, /setupNotes:\s*draft\.setupNotes\.trim\(\)/);
  assert.match(componentSource, /submissionPendingRef\.current/);
  assert.match(componentSource, /disabled=\{!canCreate\}/);
  assert.match(componentSource, /role="status">Creating guided project/);
  assert.match(componentSource, /if \(result\?\.success !== true\)/);
  assert.match(componentSource, /catch \(error\) \{\s*setFailureMessage/);
  assert.match(componentSource, /resetDraft\(\);\s*onComplete\?\.\(result\)/);
});

test('App guided handler uses only the dedicated API and returned selection metadata path', () => {
  const start = appSource.indexOf('const handleCreateOmiGuidedProject');
  const end = appSource.indexOf('\n\n  useEffect(() => {', start);
  const handlerSource = appSource.slice(start, end);

  assert.ok(start >= 0 && end > start);
  assert.match(handlerSource, /createOmiGuidedProject\(\{ title, rawIdea, setupNotes \}\)/);
  assert.doesNotMatch(handlerSource, /\bcreateProject\(/);
  assert.match(handlerSource, /requireCompleteOmiGuidedProjectResponse\(response\)/);
  assert.match(handlerSource, /upsertGuidedProjectMetadata\(currentProjects, metadata\)/);
  assert.match(handlerSource, /handleSelectProject\(newProjectId, \{ skipUnsavedConfirmation: true \}\)/);
  assert.match(appSource, /onCreateGuidedProject=\{handleCreateOmiGuidedProject\}/);
  assert.match(appSource, /onCreateProject=\{handleCreateProject\}/);
});
