import { chromium } from '../frontend/node_modules/@playwright/test/index.mjs';
import { createHash } from 'node:crypto';
import {
  chmod,
  mkdir,
  readdir,
  readFile,
  stat,
  writeFile,
} from 'node:fs/promises';
import path from 'node:path';

const repositoryRoot = path.resolve(import.meta.dirname, '..');
const evidenceRoot = process.env.T008D_EVIDENCE_DIR;
const apiOrigin = process.env.T008D_API_ORIGIN ?? 'http://127.0.0.1:8000';
const uiOrigin = process.env.T008D_UI_ORIGIN ?? 'http://127.0.0.1:5173';
const projectTitle = process.env.T008D_PROJECT_TITLE ?? 'T008D Phase9 Browser Validation 20260801';

if (!evidenceRoot || !path.isAbsolute(evidenceRoot)) {
  throw new Error('T008D_EVIDENCE_DIR must be an absolute path');
}

const browserDir = path.join(evidenceRoot, 'browser');
const networkDir = path.join(evidenceRoot, 'network');
const filesystemDir = path.join(evidenceRoot, 'filesystem');
const mutationDir = path.join(evidenceRoot, 'mutation');
const eventDir = path.join(evidenceRoot, 'event-chain');
await Promise.all([
  mkdir(browserDir, { recursive: true }),
  mkdir(networkDir, { recursive: true }),
  mkdir(filesystemDir, { recursive: true }),
  mkdir(mutationDir, { recursive: true }),
  mkdir(eventDir, { recursive: true }),
]);

const setupLedger = [];
const networkLedger = [];
const consoleLedger = [];
const pageErrors = [];
const pendingResponses = [];
const requestEntries = new WeakMap();
let networkSequence = 0;
let browser;
let page;
let projectId = null;
let projectDir = null;
let runResult = { status: 'started' };

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function assert(condition, message, details = null) {
  if (!condition) {
    throw new Error(`${message}${details === null ? '' : `: ${JSON.stringify(details)}`}`);
  }
}

async function writeJson(target, value) {
  await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

async function apiRequest(relativePath, { method = 'GET', body = undefined } = {}) {
  const url = `${apiOrigin}${relativePath}`;
  const startedAt = new Date().toISOString();
  const response = await fetch(url, {
    method,
    headers: body === undefined ? undefined : { 'content-type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  let parsed = null;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch {
    parsed = text;
  }
  setupLedger.push({
    started_at: startedAt,
    completed_at: new Date().toISOString(),
    method,
    url,
    request_body: body ?? null,
    status: response.status,
    response_body: parsed,
  });
  if (!response.ok) {
    throw new Error(`API_SETUP_FAILED ${method} ${relativePath} ${response.status}: ${text}`);
  }
  return parsed;
}

async function snapshotTree(root) {
  const rows = [];
  async function visit(directory, relative = '') {
    const entries = await readdir(directory, { withFileTypes: true });
    entries.sort((left, right) => Buffer.from(left.name).compare(Buffer.from(right.name)));
    for (const entry of entries) {
      const absolute = path.join(directory, entry.name);
      const itemPath = relative ? `${relative}/${entry.name}` : entry.name;
      const metadata = await stat(absolute);
      if (entry.isDirectory()) {
        rows.push({ path: itemPath, kind: 'directory', mode: metadata.mode & 0o777 });
        await visit(absolute, itemPath);
      } else if (entry.isFile()) {
        const bytes = await readFile(absolute);
        rows.push({
          path: itemPath,
          kind: 'file',
          mode: metadata.mode & 0o777,
          size: bytes.length,
          sha256: sha256(bytes),
        });
      } else {
        rows.push({ path: itemPath, kind: 'unsupported' });
      }
    }
  }
  await visit(root);
  return rows;
}

function fileMap(snapshot) {
  return new Map(snapshot.filter((row) => row.kind === 'file').map((row) => [row.path, row]));
}

function diffSnapshots(before, after) {
  const prior = fileMap(before);
  const current = fileMap(after);
  const paths = [...new Set([...prior.keys(), ...current.keys()])].sort();
  return paths.flatMap((itemPath) => {
    const left = prior.get(itemPath);
    const right = current.get(itemPath);
    if (!left) return [{ path: itemPath, change: 'added', after: right }];
    if (!right) return [{ path: itemPath, change: 'deleted', before: left }];
    if (left.sha256 !== right.sha256 || left.mode !== right.mode) {
      return [{ path: itemPath, change: 'changed', before: left, after: right }];
    }
    return [];
  });
}

function protectedAuthority(snapshot) {
  return snapshot.filter((row) => row.kind === 'file' && (
    row.path === 'omi/index.json'
    || row.path.startsWith('omi/candidates/')
    || row.path.startsWith('omi/promotions/')
    || row.path === 'writer_assistant/config/local_owner.json'
    || row.path.startsWith('writer_assistant/apply_contracts/')
    || row.path.startsWith('writer_assistant/promotion_audit/')
  ));
}

async function recordSnapshot(label) {
  const snapshot = await snapshotTree(projectDir);
  await writeJson(path.join(filesystemDir, `${label}.json`), snapshot);
  return snapshot;
}

async function createPromotionFixture(name) {
  const idea = await apiRequest(`/api/projects/${projectId}/omi/ideas`, {
    method: 'POST',
    body: {
      raw_idea: `Owner-authored structural planning input for ${name} validation.`,
      provenance: { source_type: 'owner_input', source_id: `phase9_${name}_idea` },
    },
  });
  const candidate = await apiRequest(`/api/projects/${projectId}/omi/candidates`, {
    method: 'POST',
    body: {
      idea_id: idea.idea_id,
      candidate_type: 'project_bible_candidate',
      candidate_content: { summary: `Owner-authored structural candidate for ${name} validation.` },
      destination: 'project_bible_candidate',
      provenance: { source_type: 'owner_input', source_id: `phase9_${name}_candidate` },
      evidence: [{ evidence_type: 'owner_statement', locator: `phase9/${name}` }],
    },
  });
  await apiRequest(`/api/projects/${projectId}/omi/candidates/${candidate.candidate_id}/decision`, {
    method: 'PATCH',
    body: { owner_decision: { decision: 'pending' }, status: 'owner_review', destination: null },
  });
  await apiRequest(`/api/projects/${projectId}/omi/candidates/${candidate.candidate_id}/decision`, {
    method: 'PATCH',
    body: {
      owner_decision: { decision: 'approve', approval_confirmed: true },
      status: 'approved',
      destination: null,
    },
  });
  const promotion = await apiRequest(`/api/projects/${projectId}/omi/promotions`, {
    method: 'POST',
    body: {
      candidate_id: candidate.candidate_id,
      final_confirmation: true,
      target_file: 'bible.json',
      target_path: 'bible.json',
      provenance: { source_type: 'owner_input', source_id: `phase9_${name}_promotion` },
      evidence: [{ evidence_type: 'owner_statement', locator: `phase9/${name}` }],
    },
  });
  return { idea, candidate, promotion };
}

function isApiUrl(url) {
  try {
    return new URL(url).pathname.startsWith('/api/');
  } catch {
    return false;
  }
}

async function waitForPost(pathname, action) {
  const responsePromise = page.waitForResponse((response) => (
    response.request().method() === 'POST' && new URL(response.url()).pathname === pathname
  ));
  await action();
  const response = await responsePromise;
  await response.finished();
  const body = await response.json();
  assert(response.ok(), `Browser POST failed for ${pathname}`, { status: response.status(), body });
  return { status: response.status(), body };
}

async function openPromotion(promotionId) {
  const dashboard = page.getByTestId('omi-dashboard');
  if (await dashboard.isVisible().catch(() => false)) {
    await page.getByRole('button', {
      name: 'Review promotion readiness for Promotion Handoff Readiness',
      exact: true,
    }).click();
  }
  const selection = page.getByLabel('Exact promotion record', { exact: true });
  await selection.waitFor({ state: 'visible' });
  await selection.selectOption(promotionId);
  const confirmation = page.getByTestId('omi-apply-promotion-confirmation');
  await confirmation.waitFor({ state: 'visible' });
  await page.getByText(promotionId, { exact: true }).waitFor({ state: 'visible' });
  return confirmation;
}

async function fillPreparation({
  operation,
  duplicateState,
  dependencyState,
  dependencyEntry = null,
  displayName,
  factValue,
  destinationKey = 'phase9-record',
}) {
  const operationGroup = page.getByRole('group', { name: 'Operation and destination', exact: true });
  await operationGroup.getByRole('combobox').nth(0).selectOption(operation);
  await operationGroup.getByRole('combobox').nth(1).selectOption('approved_character');
  await page.getByLabel('Destination key', { exact: true }).fill(destinationKey);
  await page.getByLabel('Display name', { exact: true }).fill(displayName);
  await page.getByLabel('Fact field ID', { exact: true }).fill('role');
  await page.getByLabel('Owner-entered fact value', { exact: true }).fill(factValue);
  await page.getByRole('group', { name: 'Evidence references', exact: true }).getByRole('checkbox').first().check();
  await page.getByRole('group', { name: 'Provenance references', exact: true }).getByRole('checkbox').first().check();
  const decisionGroup = page.getByRole('group', {
    name: 'Explicit duplicate and dependency decisions',
    exact: true,
  });
  await decisionGroup.getByRole('combobox').nth(0).selectOption(duplicateState);
  await page.getByLabel('Duplicate rationale', { exact: true }).fill('The owner reviewed the candidate against the current approved-record scope.');
  await page.getByLabel('I reviewed the selected candidate ID for this duplicate decision.', { exact: true }).check();
  await decisionGroup.getByRole('combobox').nth(1).selectOption(dependencyState);
  await page.getByLabel('Dependency rationale', { exact: true }).fill('The owner explicitly reviewed dependency state for this bounded validation.');
  if (dependencyEntry) {
    await page.getByRole('button', { name: 'Add dependency entry', exact: true }).click();
    const dependencyGroup = page.getByRole('group', { name: 'Dependency 1', exact: true });
    await dependencyGroup.getByLabel('Dependency ID', { exact: true }).fill(dependencyEntry.dependencyId);
    await dependencyGroup.getByLabel('Dependency kind', { exact: true }).fill(dependencyEntry.kind);
    await dependencyGroup.getByRole('combobox').nth(0).selectOption(String(dependencyEntry.required));
    await dependencyGroup.getByRole('combobox').nth(1).selectOption(dependencyEntry.status);
    await dependencyGroup.getByRole('combobox').nth(2).selectOption('none');
    await dependencyGroup.getByRole('group', { name: 'Dependency evidence references', exact: true })
      .getByRole('checkbox').first().check();
    await dependencyGroup.getByRole('group', { name: 'Dependency provenance references', exact: true })
      .getByRole('checkbox').first().check();
    await dependencyGroup.getByLabel('Dependency rationale', { exact: true }).fill(dependencyEntry.rationale);
  }
  await page.getByLabel('Optional owner note', { exact: true }).fill('Phase 9 owner-controlled browser validation.');
}

async function prepareAndSeal(promotionId, form) {
  await openPromotion(promotionId);
  await fillPreparation(form);
  const revisionsPath = `/api/projects/${projectId}/omi/promotions/${promotionId}/apply-contract/revisions`;
  const prepared = await waitForPost(revisionsPath, () => (
    page.getByRole('button', { name: 'Prepare immutable revision', exact: true }).click()
  ));
  assert(prepared.body.revision === 1, 'Expected first immutable revision');
  await page.getByText('Immutable preparation and draft revision published.', { exact: true }).waitFor();
  const approvalLabel = `I explicitly approve revision ${prepared.body.revision}, its complete approved-record hash and size, and its recorded before state.`;
  await page.getByLabel(approvalLabel, { exact: true }).check();
  const approvalPath = `${revisionsPath}/${prepared.body.revision}/approval`;
  const approved = await waitForPost(approvalPath, () => (
    page.getByRole('button', { name: `Approve and seal revision ${prepared.body.revision}`, exact: true }).click()
  ));
  await page.getByRole('heading', { name: 'Sealed contract reference', exact: true }).waitFor();
  return { prepared: prepared.body, approved: approved.body };
}

async function issueChallenge(promotionId, { replace = false } = {}) {
  const challengePath = `/api/projects/${projectId}/omi/promotions/${promotionId}/apply-contract/final-challenge`;
  const first = await waitForPost(challengePath, () => (
    page.getByRole('button', { name: 'Generate final challenge', exact: true }).click()
  ));
  await page.getByText(/Final challenge active and available/).waitFor();
  if (!replace) return first.body;
  const replacement = await waitForPost(challengePath, () => (
    page.getByRole('button', { name: 'Explicitly replace active challenge', exact: true }).click()
  ));
  assert(replacement.body.challenge_id !== first.body.challenge_id, 'Challenge replacement did not replace the prior challenge');
  await page.getByText('A fresh challenge replaced any prior outstanding challenge for this seal.', { exact: true }).waitFor();
  return replacement.body;
}

async function finalApply(promotionId) {
  await page.getByLabel(
    'I explicitly confirm this one final apply for the displayed sealed revision and complete approved-record hash/size.',
    { exact: true },
  ).check();
  const result = await waitForPost(`/api/projects/${projectId}/apply-promotion`, () => (
    page.getByRole('button', { name: 'Final Apply-Promotion', exact: true }).click()
  ));
  await page.getByRole('heading', { name: 'Apply-Promotion completed', exact: true }).waitFor();
  return result.body;
}

async function returnToDashboard() {
  await page.getByRole('button', { name: 'Cancel / Return', exact: true }).click();
  await page.getByTestId('omi-dashboard').waitFor({ state: 'visible' });
}

function assertFinalMutationIsolation(before, after, promotionId, expectedRecordChange) {
  const protectedDiff = diffSnapshots(protectedAuthority(before), protectedAuthority(after));
  assert(protectedDiff.length === 0, 'Final apply mutated protected authority or immutable contracts', protectedDiff);
  const changes = diffSnapshots(before, after);
  const allowedEventPrefix = `writer_assistant/promotion_audits/${promotionId}/events/`;
  const recordPath = 'writer_assistant/approved_memory/approved_character/phase9-record.json';
  const unexpected = changes.filter((change) => (
    change.path !== recordPath && !change.path.startsWith(allowedEventPrefix)
  ));
  assert(unexpected.length === 0, 'Final apply changed an unexpected project file', unexpected);
  const recordChange = changes.find((change) => change.path === recordPath);
  assert(recordChange?.change === expectedRecordChange, 'Approved-record mutation did not match operation', recordChange);
  const eventChanges = changes.filter((change) => change.path.startsWith(allowedEventPrefix));
  assert(eventChanges.length === 2 && eventChanges.every((change) => change.change === 'added'), 'Final apply must append exactly intent and completion events', eventChanges);
  return changes;
}

async function eventChainSummary(promotionId) {
  const directory = path.join(projectDir, 'writer_assistant', 'promotion_audits', promotionId, 'events');
  const names = (await readdir(directory)).sort();
  let previousBytes = null;
  const rows = [];
  for (let index = 0; index < names.length; index += 1) {
    const name = names[index];
    const match = /^(\d{12})_([a-f0-9]{64})\.json$/.exec(name);
    assert(match, 'Invalid event filename', name);
    const bytes = await readFile(path.join(directory, name));
    const event = JSON.parse(bytes.toString('utf8'));
    assert(Number(match[1]) === index + 1 && event.sequence === index + 1, 'Noncontiguous event sequence', name);
    assert(event.event_id === match[2] && event.event_filename === name, 'Event filename/id mismatch', name);
    const expectedPrevious = previousBytes === null ? null : sha256(previousBytes);
    assert(event.previous_event_hash === expectedPrevious, 'Previous-document hash mismatch', name);
    rows.push({
      filename: name,
      sequence: event.sequence,
      event_type: event.event_type,
      event_id: event.event_id,
      event_content_hash: event.event_content_hash,
      previous_event_hash: event.previous_event_hash,
      document_sha256: sha256(bytes),
    });
    previousBytes = bytes;
  }
  return rows;
}

try {
  const created = await apiRequest('/api/projects', { method: 'POST', body: { title: projectTitle } });
  projectId = created.project_id;
  projectDir = path.join(repositoryRoot, 'projects', projectId);
  await writeJson(path.join(evidenceRoot, 'disposable-project.json'), { project_id: projectId, project_dir: projectDir });

  const ownerPath = path.join(projectDir, 'writer_assistant', 'config', 'local_owner.json');
  await mkdir(path.dirname(ownerPath), { recursive: true, mode: 0o700 });
  await writeJson(ownerPath, {
    schema_version: 'local_owner_identity.v1',
    project_id: projectId,
    owner_id: 'phase9_owner',
    display_name: 'Phase 9 Local Owner',
    config_version: 1,
    updated_at: new Date().toISOString(),
  });
  await chmod(ownerPath, 0o600);

  const createFixture = await createPromotionFixture('create');
  const updateFixture = await createPromotionFixture('update');
  const blockedFixture = await createPromotionFixture('blocked');
  const setupOmi = await apiRequest(`/api/projects/${projectId}/omi`);
  assert(setupOmi.promotions.length === 3, 'Expected three API-created promotion handoffs');
  await writeJson(path.join(networkDir, 'setup-api-ledger.json'), setupLedger);
  const afterSetup = await recordSnapshot('01-after-api-setup');

  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, colorScheme: 'light' });
  page = await context.newPage();
  page.on('console', (message) => consoleLedger.push({ type: message.type(), text: message.text() }));
  page.on('pageerror', (error) => pageErrors.push({ message: error.message, stack: error.stack ?? null }));
  page.on('request', (request) => {
    if (!isApiUrl(request.url())) return;
    const entry = {
      sequence: ++networkSequence,
      method: request.method(),
      url: request.url(),
      request_body: request.postData(),
      response_status: null,
      response_body: null,
      failure: null,
    };
    requestEntries.set(request, entry);
    networkLedger.push(entry);
  });
  page.on('requestfailed', (request) => {
    const entry = requestEntries.get(request);
    if (entry) entry.failure = request.failure()?.errorText ?? 'request failed';
  });
  page.on('response', (response) => {
    if (!isApiUrl(response.url())) return;
    pendingResponses.push((async () => {
      const entry = requestEntries.get(response.request());
      if (!entry) return;
      entry.response_status = response.status();
      try {
        entry.response_body = await response.text();
      } catch (error) {
        entry.failure = `response body unavailable: ${error.message}`;
      }
    })());
  });

  await page.goto(uiOrigin, { waitUntil: 'domcontentloaded' });
  const projectSelect = page.getByLabel('Select project', { exact: true });
  await projectSelect.waitFor({ state: 'visible' });
  await projectSelect.selectOption(projectId);
  await page.getByTestId('omi-workspace-entry').click();
  await page.getByTestId('omi-dashboard').waitFor({ state: 'visible' });
  await page.getByText(`Active project: ${projectTitle} / project-local OMI`, { exact: true }).waitFor();
  await page.screenshot({ path: path.join(browserDir, '01-disposable-project-dashboard.png'), fullPage: true });

  const createSeal = await prepareAndSeal(createFixture.promotion.promotion_id, {
    operation: 'create',
    duplicateState: 'distinct_record',
    dependencyState: 'none_declared',
    displayName: 'Phase 9 Approved Character',
    factValue: 'Owner-controlled create validation',
  });
  await issueChallenge(createFixture.promotion.promotion_id, { replace: true });
  await page.screenshot({ path: path.join(browserDir, '02-create-final-confirmation.png'), fullPage: true });
  const createBefore = await recordSnapshot('02-create-before-final-apply');
  const createResult = await finalApply(createFixture.promotion.promotion_id);
  const createAfter = await recordSnapshot('03-create-after-final-apply');
  const createMutation = assertFinalMutationIsolation(createBefore, createAfter, createFixture.promotion.promotion_id, 'added');
  assert(createResult.approved_record_version === 1, 'Create apply did not produce record version 1', createResult);
  await writeJson(path.join(mutationDir, 'create-final-mutation.json'), createMutation);
  await page.screenshot({ path: path.join(browserDir, '03-create-completed.png'), fullPage: true });
  await returnToDashboard();

  const updateSeal = await prepareAndSeal(updateFixture.promotion.promotion_id, {
    operation: 'update',
    duplicateState: 'update_existing',
    dependencyState: 'none_declared',
    displayName: 'Phase 9 Approved Character Updated',
    factValue: 'Owner-controlled update validation',
  });
  await issueChallenge(updateFixture.promotion.promotion_id);
  const updateBefore = await recordSnapshot('04-update-before-final-apply');
  const updateResult = await finalApply(updateFixture.promotion.promotion_id);
  const updateAfter = await recordSnapshot('05-update-after-final-apply');
  const updateMutation = assertFinalMutationIsolation(updateBefore, updateAfter, updateFixture.promotion.promotion_id, 'changed');
  assert(updateResult.approved_record_version === 2, 'Update apply did not produce record version 2', updateResult);
  await writeJson(path.join(mutationDir, 'update-final-mutation.json'), updateMutation);
  await page.screenshot({ path: path.join(browserDir, '04-update-completed.png'), fullPage: true });
  await returnToDashboard();

  await openPromotion(blockedFixture.promotion.promotion_id);
  await fillPreparation({
    operation: 'create',
    duplicateState: 'unresolved',
    dependencyState: 'blocked',
    displayName: 'Blocked Phase 9 Character',
    factValue: 'Blocked validation state',
    destinationKey: 'phase9-blocked-record',
    dependencyEntry: {
      dependencyId: 'phase9_blocked_dependency',
      kind: 'promotion_prerequisite',
      required: true,
      status: 'blocked',
      rationale: 'The owner confirmed this required prerequisite remains blocked.',
    },
  });
  const blockedPrepared = await waitForPost(
    `/api/projects/${projectId}/omi/promotions/${blockedFixture.promotion.promotion_id}/apply-contract/revisions`,
    () => page.getByRole('button', { name: 'Prepare immutable revision', exact: true }).click(),
  );
  assert(blockedPrepared.body.revision === 1, 'Blocked scenario did not retain its draft revision');
  const blockedPreparationEntry = networkLedger.filter((entry) => (
    entry.method === 'POST'
    && new URL(entry.url).pathname === `/api/projects/${projectId}/omi/promotions/${blockedFixture.promotion.promotion_id}/apply-contract/revisions`
  )).at(-1);
  const blockedPreparationBody = JSON.parse(blockedPreparationEntry.request_body);
  const blockedDependencies = blockedPreparationBody.dependency_resolution.dependencies;
  assert(blockedPreparationBody.dependency_resolution.state === 'blocked' && blockedDependencies.length === 1, 'Blocked dependency decision did not submit exactly one structured entry', blockedPreparationBody.dependency_resolution);
  assert(Object.keys(blockedDependencies[0]).sort().join(',') === [
    'dependency_id',
    'evidence_ref_ids',
    'kind',
    'provenance_ref_ids',
    'rationale',
    'required',
    'status',
    'target',
  ].sort().join(','), 'Blocked dependency entry did not match the closed accepted input schema', blockedDependencies[0]);
  assert(
    blockedDependencies[0].dependency_id === 'phase9_blocked_dependency'
    && blockedDependencies[0].kind === 'promotion_prerequisite'
    && blockedDependencies[0].required === true
    && blockedDependencies[0].status === 'blocked'
    && blockedDependencies[0].target === null
    && blockedDependencies[0].rationale === 'The owner confirmed this required prerequisite remains blocked.'
    && blockedDependencies[0].evidence_ref_ids.length === 1
    && blockedDependencies[0].provenance_ref_ids.length === 1,
    'Blocked dependency entry did not retain the explicit owner-entered values and selected references',
    blockedDependencies[0],
  );
  const blockedApproval = page.getByRole('button', { name: 'Approve and seal revision 1', exact: true });
  assert(await blockedApproval.isDisabled(), 'Blocked duplicate/dependency decisions did not disable approval');
  const blockersText = await page.getByTestId('omi-apply-promotion-blockers').innerText();
  assert(blockersText.includes('DUPLICATE_DECISION_BLOCKS_APPLY'), 'Duplicate blocker is not visible');
  assert(blockersText.includes('DEPENDENCY_DECISION_BLOCKS_APPLY'), 'Dependency blocker is not visible');

  await page.getByRole('group', { name: 'Operation and destination', exact: true })
    .getByRole('combobox').nth(0).focus();
  await page.keyboard.press('Tab');
  const keyboardProof = await page.evaluate(() => ({
    tag: document.activeElement?.tagName,
    label: document.activeElement?.labels?.[0]?.innerText?.trim() ?? null,
  }));
  assert(keyboardProof.tag === 'SELECT', 'Keyboard tab order did not reach the next native select', keyboardProof);
  await page.setViewportSize({ width: 390, height: 844 });
  const responsiveProof = await page.getByTestId('omi-apply-promotion-confirmation').evaluate((element) => ({
    viewport_width: document.documentElement.clientWidth,
    document_scroll_width: document.documentElement.scrollWidth,
    confirmation_left: element.getBoundingClientRect().left,
    confirmation_right: element.getBoundingClientRect().right,
    controls_outside_confirmation: Array.from(element.querySelectorAll('input, select, textarea, button')).filter((control) => {
      const controlRect = control.getBoundingClientRect();
      const surfaceRect = element.getBoundingClientRect();
      return controlRect.left < surfaceRect.left - 1 || controlRect.right > surfaceRect.right + 1;
    }).length,
  }));
  assert(responsiveProof.document_scroll_width <= responsiveProof.viewport_width, 'Document overflowed mobile viewport', responsiveProof);
  assert(responsiveProof.controls_outside_confirmation === 0, 'Apply controls escaped responsive containment', responsiveProof);
  await page.screenshot({ path: path.join(browserDir, '05-blocked-mobile.png'), fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });

  const beforeGet = await recordSnapshot('06-before-zero-write-gets');
  const getProof = await page.evaluate(async ({ projectId: browserProjectId, promotionId }) => {
    const contract = await fetch(`/api/projects/${browserProjectId}/omi/promotions/${promotionId}/apply-contract?revision=1`);
    const audit = await fetch(`/api/projects/${browserProjectId}/omi/promotions/${promotionId}/apply-audit`);
    return { contract_status: contract.status, audit_status: audit.status };
  }, { projectId, promotionId: updateFixture.promotion.promotion_id });
  assert(getProof.contract_status === 200 && getProof.audit_status === 200, 'Observational GET routes failed', getProof);
  const afterGet = await recordSnapshot('07-after-zero-write-gets');
  assert(diffSnapshots(beforeGet, afterGet).length === 0, 'Observational GET routes wrote project state', diffSnapshots(beforeGet, afterGet));

  const finalApplyEntries = networkLedger.filter((entry) => (
    entry.method === 'POST' && new URL(entry.url).pathname === `/api/projects/${projectId}/apply-promotion`
  ));
  assert(finalApplyEntries.length === 2, 'Expected two UI final apply requests before replay', finalApplyEntries);
  const replayApplyBody = JSON.parse(finalApplyEntries.at(-1).request_body);
  assert(Object.keys(replayApplyBody).sort().join(',') === [
    'before_state_snapshot_token',
    'challenge_id',
    'challenge_response',
    'final_confirmation',
    'idempotency_key',
    'promotion_id',
    'revision',
    'sealed_contract_hash',
  ].sort().join(','), 'Final request was not reference-only', replayApplyBody);
  const replayBefore = await recordSnapshot('08-before-completed-replay');
  const replay = await page.evaluate(async ({ browserProjectId, requestBody }) => {
    const response = await fetch(`/api/projects/${browserProjectId}/apply-promotion`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(requestBody),
    });
    return { status: response.status, body: await response.json() };
  }, { browserProjectId: projectId, requestBody: replayApplyBody });
  assert(replay.status === 200 && replay.body.replayed === true && replay.body.lineage_state === 'applied', 'Completed apply replay failed', replay);
  const replayAfter = await recordSnapshot('09-after-completed-replay');
  assert(diffSnapshots(replayBefore, replayAfter).length === 0, 'Completed replay wrote project state', diffSnapshots(replayBefore, replayAfter));

  const createEvents = await eventChainSummary(createFixture.promotion.promotion_id);
  const updateEvents = await eventChainSummary(updateFixture.promotion.promotion_id);
  const blockedEvents = await eventChainSummary(blockedFixture.promotion.promotion_id);
  assert(createEvents.at(-2)?.event_type === 'apply_intent' && createEvents.at(-1)?.event_type === 'apply_completed', 'Create event suffix is not intent/completion');
  assert(updateEvents.at(-2)?.event_type === 'apply_intent' && updateEvents.at(-1)?.event_type === 'apply_completed', 'Update event suffix is not intent/completion');
  assert(!blockedEvents.some((event) => event.event_type.startsWith('apply_')), 'Blocked scenario published final apply events');
  await writeJson(path.join(eventDir, 'create-chain.json'), createEvents);
  await writeJson(path.join(eventDir, 'update-chain.json'), updateEvents);
  await writeJson(path.join(eventDir, 'blocked-chain.json'), blockedEvents);

  await Promise.allSettled(pendingResponses);
  const failedApiRequests = networkLedger.filter((entry) => entry.failure || (entry.response_status ?? 500) >= 400);
  assert(failedApiRequests.length === 0, 'Browser API ledger contains failed requests', failedApiRequests);
  assert(pageErrors.length === 0, 'Browser page errors occurred', pageErrors);
  const errorConsole = consoleLedger.filter((entry) => entry.type === 'error');
  assert(errorConsole.length === 0, 'Browser console errors occurred', errorConsole);

  const finalSnapshot = await recordSnapshot('10-final-project-state');
  runResult = {
    status: 'passed',
    project_id: projectId,
    project_dir: projectDir,
    scenarios: {
      create: { promotion_id: createFixture.promotion.promotion_id, seal: createSeal, result: createResult },
      update: { promotion_id: updateFixture.promotion.promotion_id, seal: updateSeal, result: updateResult },
      blocked: { promotion_id: blockedFixture.promotion.promotion_id, blockers: blockersText },
      replay,
    },
    blocked_dependency_request: blockedDependencies[0],
    reference_only_final_request_keys: Object.keys(replayApplyBody).sort(),
    explicit_challenge_post_count: networkLedger.filter((entry) => new URL(entry.url).pathname.endsWith('/final-challenge') && entry.method === 'POST').length,
    final_apply_post_count: networkLedger.filter((entry) => new URL(entry.url).pathname.endsWith('/apply-promotion') && entry.method === 'POST').length,
    zero_write_gets: getProof,
    keyboard: keyboardProof,
    responsive: responsiveProof,
    event_counts: { create: createEvents.length, update: updateEvents.length, blocked: blockedEvents.length },
    setup_snapshot_file_count: fileMap(afterSetup).size,
    final_snapshot_file_count: fileMap(finalSnapshot).size,
    console_errors: errorConsole.length,
    page_errors: pageErrors.length,
  };
} catch (error) {
  runResult = {
    ...runResult,
    status: 'failed',
    project_id: projectId,
    project_dir: projectDir,
    error: error.message,
    stack: error.stack,
  };
  process.exitCode = 1;
  if (page) {
    try {
      await page.screenshot({ path: path.join(browserDir, '99-failure.png'), fullPage: true });
    } catch {
      // Preserve the original validation failure.
    }
  }
} finally {
  await Promise.allSettled(pendingResponses);
  await writeJson(path.join(networkDir, 'setup-api-ledger.json'), setupLedger);
  await writeJson(path.join(networkDir, 'browser-api-ledger.json'), networkLedger);
  await writeJson(path.join(browserDir, 'browser-console.json'), consoleLedger);
  await writeJson(path.join(browserDir, 'browser-page-errors.json'), pageErrors);
  await writeJson(path.join(browserDir, 'browser-result.json'), runResult);
  if (browser) await browser.close();
}

console.log(JSON.stringify(runResult, null, 2));
