#!/usr/bin/env node
/**
 * OMI Evidence Drawer browser-visible evidence harness.
 *
 * Evidence-only runner. It opens Candidate Detail, opens the contextual
 * Evidence Drawer, captures desktop/mobile screenshots, and compares read-only
 * snapshots. It blocks mutating API methods and does not create candidates,
 * call models, run extraction, run apply-promotion, or mutate Memory/Canon.
 */

import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const FRONTEND_NODE_MODULES = path.join(REPO_ROOT, 'frontend', 'node_modules');

const APP_BASE_URL = process.env.APP_BASE_URL ?? 'http://localhost:5173';
const PROJECT_ID = process.env.OMI_EVIDENCE_DRAWER_PROJECT_ID ?? 'example';
const CONTEXT_READINESS_PATH = `/api/projects/${PROJECT_ID}/context-readiness`;
const EVIDENCE_DIR = path.resolve(
  process.env.OMI_EVIDENCE_DRAWER_EVIDENCE_DIR
    ?? 'docs/roadmap/validation/omi-evidence-drawer-browser-evidence',
);
const VALIDATION_MD = path.resolve(
  process.env.OMI_EVIDENCE_DRAWER_VALIDATION_MD
    ?? 'docs/roadmap/validation/omi_evidence_drawer_browser_evidence.md',
);

const SCREENSHOT_DIR = path.join(EVIDENCE_DIR, 'screenshots');
const WORKFLOW_LOG_PATH = path.join(EVIDENCE_DIR, 'workflow-log.json');
const RUN_STARTED_AT = new Date().toISOString();
const FORBIDDEN_CONTROL_LABELS = Object.freeze([
  'rewrite',
  'continue',
  'outline',
  'draft',
  'polish',
  'improve',
  'expand',
  'imitate',
  'revise',
  'generate prose',
  'story prose',
  'compose',
]);

const FIXTURE_CANDIDATE = Object.freeze({
  candidate_id: 'fixture-candidate-evidence-001',
  candidate_type: 'character_profile',
  status: 'pending_review',
  destination: 'characters',
  source_type: 'Owner Input',
  source_location: 'owner-input-fixture-001#L1-L3',
  source_locator: 'owner-input-fixture-001#L1-L3',
  source_open_state: 'unsafe',
  quote_exactness: 'exact excerpt stored',
  confidence_support_label: 'Support: moderate',
  original_wording_excerpt: 'Stored original wording excerpt from owner input.',
  evidence_summary: 'Stored evidence summary: owner input reference retained.',
  supports_claim_note: 'Stored supports-claim note only.',
  limitations_ambiguity: 'Stored limitation: source record opening is unsafe in fixture mode.',
  provenance_chain: ['owner-input-fixture-001', 'candidate-fixture-evidence-001'],
  related_ids: ['owner-input-fixture-001', 'fixture-candidate-evidence-001'],
  timestamps: 'created_at=2026-07-03T00:00:00Z; updated_at=2026-07-03T00:00:00Z',
  source_hash: 'fixture-source-hash',
  snapshot_hash: 'fixture-snapshot-hash',
  duplicate_state: 'Duplicate unresolved',
  dependency_state: 'Dependency unresolved',
  schema_status: 'supported',
  promotion_audit_record: null,
  approved_memory_canon_links: [],
  field_review_rows: [
    {
      field: 'Name',
      proposed_value: 'Stored candidate name',
      decision: 'Required field decisions unresolved',
      evidence_summary: 'Stored field evidence summary.',
      provenance_summary: 'Stored field provenance summary.',
      source_type: 'Owner Input',
      source_location: 'owner-input-fixture-001#L2',
      source_open_state: 'unsafe',
      quote_exactness: 'exact excerpt stored',
      confidence_support_label: 'Support: moderate',
      original_wording_excerpt: 'Stored field original wording excerpt.',
      supports_claim_note: 'Stored field supports-claim note only.',
      limitations_ambiguity: 'Stored field limitation.',
      provenance_chain: ['owner-input-fixture-001', 'field-name'],
      related_ids: ['field-name'],
      source_hash: 'fixture-field-source-hash',
      snapshot_hash: 'fixture-field-snapshot-hash',
      duplicate_dependency: 'Duplicate unresolved',
      owner_note: 'Stored owner note.',
    },
  ],
});

const FIXTURE_API = Object.freeze({
  projects: {
    projects: [
      {
        project_id: PROJECT_ID,
        id: PROJECT_ID,
        title: 'Example Project',
        status: 'valid',
      },
    ],
  },
  scenes: { scenes: [] },
  notes: { notes: [] },
  materials: { materials: [] },
  bible: {},
  storyform: {},
  storyformContext: { context: '' },
  contextReadiness: {
    schema_version: 'project_context_readiness.v1',
    project_id: PROJECT_ID,
    status_vocabulary: [
      'absent',
      'invalid',
      'not_applicable',
      'ready',
      'unavailable',
    ],
    resource_order: [
      'bible',
      'storyform',
      'storyform_context',
    ],
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
  },
  omi: {
    index: null,
    owner_input_count: 1,
    candidate_count: 1,
    blocked_count: 1,
    handoff_ready_count: 0,
    promotion_audit_count: 0,
    ideas: [],
    candidates: [FIXTURE_CANDIDATE],
    groups: [],
    promotions: [],
    deferred: [],
    warnings: [],
    approved_memory_canon_snapshot: {
      characters: [],
      locations: [],
      timeline: [],
      plot_threads: [],
    },
  },
});

const workflowLog = [];
const failures = [];
const mutatingApiRequests = [];
let apiMode = 'live-backend';
let browser = null;
let page = null;
let viteProcess = null;
let playwrightChromium = null;
let desktopScreenshotPath = '';
let mobileScreenshotPath = '';
let compactMobileScreenshotPath = '';
let beforeSnapshot = null;
let afterSnapshot = null;
const pageErrors = [];
const consoleErrors = [];
const failedApplicationRequests = [];
const failedApplicationResponses = [];
let readinessRequestCount = 0;
const readinessResponses = [];

function logAction(action, details = {}) {
  const entry = { ts: new Date().toISOString(), action, ...details };
  workflowLog.push(entry);
  const suffix = Object.keys(details).length ? ` ${JSON.stringify(details)}` : '';
  console.log(`[ACTION] ${action}${suffix}`);
}

function recordFailure(name, details = {}) {
  failures.push({ name, details, ts: new Date().toISOString() });
  logAction('assert_fail', { name, ...details });
}

function assertEvidence(name, condition, details = {}) {
  if (!condition) {
    recordFailure(name, details);
    return;
  }
  logAction('assert_pass', { name, ...details });
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeJson(value) {
  return JSON.stringify(value ?? null);
}

function approvedMemoryTotal(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) {
    return 0;
  }
  return Object.values(snapshot).reduce((total, value) => {
    if (Array.isArray(value)) {
      return total + value.length;
    }
    const count = Number(value);
    return Number.isFinite(count) && count >= 0 ? total + count : total;
  }, 0);
}

function snapshotOMI(omiPayload) {
  const approvedSnapshot =
    omiPayload?.approved_memory_canon_snapshot
    ?? omiPayload?.approved_memory_snapshot
    ?? omiPayload?.memory_canon_snapshot
    ?? null;
  const candidates = asArray(omiPayload?.candidates);
  return {
    candidateCount: Number(omiPayload?.candidate_count) || candidates.length,
    approvedMemoryTotal: approvedMemoryTotal(approvedSnapshot),
    approvedSnapshotJson: normalizeJson(approvedSnapshot),
  };
}

async function loadPlaywrightChromium() {
  const candidates = [
    path.join(FRONTEND_NODE_MODULES, '@playwright/test', 'index.js'),
    path.join(FRONTEND_NODE_MODULES, '@playwright/test', 'index.mjs'),
    path.join(FRONTEND_NODE_MODULES, 'playwright', 'index.js'),
    path.join(FRONTEND_NODE_MODULES, 'playwright', 'index.mjs'),
  ];

  let lastError = null;
  for (const candidate of candidates) {
    try {
      const mod = await import(pathToFileURL(candidate).href);
      const chromium = mod.chromium ?? mod.default?.chromium;
      if (chromium) {
        logAction('playwright_import_ok', { modulePath: candidate });
        return chromium;
      }
    } catch (error) {
      lastError = error;
    }
  }

  throw new Error(
    `Playwright not found under frontend/node_modules. Last error: ${
      lastError instanceof Error ? lastError.message : String(lastError)
    }`,
  );
}

async function ensureEvidenceDirs() {
  await fs.mkdir(SCREENSHOT_DIR, { recursive: true });
  logAction('ensure_evidence_dirs', { evidenceDir: EVIDENCE_DIR, screenshotDir: SCREENSHOT_DIR });
}

async function fetchJson(url) {
  const response = await fetch(url, { method: 'GET' });
  if (!response.ok) {
    throw new Error(`GET ${url} failed with ${response.status}`);
  }
  return response.json();
}

async function appIsReachable() {
  try {
    const response = await fetch(APP_BASE_URL, { method: 'GET' });
    return response.ok;
  } catch {
    return false;
  }
}

async function startViteIfNeeded() {
  if (await appIsReachable()) {
    logAction('app_reachable_existing_server', { appBaseUrl: APP_BASE_URL });
    return;
  }

  logAction('start_vite_dev_server', { appBaseUrl: APP_BASE_URL });
  viteProcess = spawn('npm', ['--prefix', 'frontend', 'run', 'dev'], {
    cwd: REPO_ROOT,
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env },
    detached: true,
  });

  viteProcess.stdout.on('data', (chunk) => {
    logAction('vite_stdout', { text: String(chunk).trim().slice(0, 500) });
  });
  viteProcess.stderr.on('data', (chunk) => {
    logAction('vite_stderr', { text: String(chunk).trim().slice(0, 500) });
  });

  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    if (await appIsReachable()) {
      logAction('app_reachable_started_server', { appBaseUrl: APP_BASE_URL });
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  throw new Error(`App did not become reachable at ${APP_BASE_URL}`);
}

async function detectApiMode() {
  const omiUrl = new URL(`/api/projects/${PROJECT_ID}/omi`, APP_BASE_URL).href;
  try {
    const omi = await fetchJson(omiUrl);
    if (asArray(omi?.candidates).length === 0 && !Number(omi?.candidate_count)) {
      apiMode = 'fixture';
      logAction('live_backend_has_no_evidence_candidate_using_read_only_fixture', { omiUrl });
      return;
    }
    apiMode = 'live-backend';
  } catch (error) {
    apiMode = 'fixture';
    logAction('backend_unavailable_using_read_only_fixture', {
      omiUrl,
      message: error instanceof Error ? error.message : String(error),
    });
  }
}

function jsonResponse(payload, status = 200) {
  return {
    status,
    contentType: 'application/json',
    body: `${JSON.stringify(payload)}\n`,
  };
}

async function installApiGuard(context) {
  await context.route('**/api/**', async (route) => {
    const request = route.request();
    const method = request.method().toUpperCase();
    const pathname = new URL(request.url()).pathname;

    if (method !== 'GET') {
      mutatingApiRequests.push({ method, pathname });
      await route.fulfill(jsonResponse({ detail: 'Mutating API requests are blocked in OMI evidence drawer evidence.' }, 405));
      return;
    }

    if (apiMode !== 'fixture') {
      await route.continue();
      return;
    }

    const routeMap = new Map([
      ['/api/projects', FIXTURE_API.projects],
      [`/api/projects/${PROJECT_ID}/scenes`, FIXTURE_API.scenes],
      [`/api/projects/${PROJECT_ID}/notes`, FIXTURE_API.notes],
      [`/api/projects/${PROJECT_ID}/materials`, FIXTURE_API.materials],
      [CONTEXT_READINESS_PATH, FIXTURE_API.contextReadiness],
      [`/api/projects/${PROJECT_ID}/bible`, FIXTURE_API.bible],
      [`/api/projects/${PROJECT_ID}/storyform`, FIXTURE_API.storyform],
      [`/api/projects/${PROJECT_ID}/storyform-context`, FIXTURE_API.storyformContext],
      [`/api/projects/${PROJECT_ID}/omi`, FIXTURE_API.omi],
      [`/api/projects/${PROJECT_ID}/omi/candidates/${FIXTURE_CANDIDATE.candidate_id}`, FIXTURE_CANDIDATE],
    ]);

    if (routeMap.has(pathname)) {
      await route.fulfill(jsonResponse(routeMap.get(pathname)));
      return;
    }

    await route.fulfill(jsonResponse({ detail: `Unhandled read-only fixture route: ${pathname}` }, 404));
  });
  logAction('api_guard_installed', { projectId: PROJECT_ID, apiMode });
}

async function readOnlyProjectSnapshot(label) {
  if (apiMode === 'fixture') {
    const snapshot = {
      label,
      apiMode,
      omi: snapshotOMI(FIXTURE_API.omi),
      bibleJson: normalizeJson(FIXTURE_API.bible),
      storyformJson: normalizeJson(FIXTURE_API.storyform),
    };
    logAction('read_only_project_snapshot_fixture', snapshot);
    return snapshot;
  }

  const omiUrl = new URL(`/api/projects/${PROJECT_ID}/omi`, APP_BASE_URL).href;
  const bibleUrl = new URL(`/api/projects/${PROJECT_ID}/bible`, APP_BASE_URL).href;
  const storyformUrl = new URL(`/api/projects/${PROJECT_ID}/storyform`, APP_BASE_URL).href;
  const [omi, bible, storyform] = await Promise.all([
    fetchJson(omiUrl),
    fetchJson(bibleUrl).catch((error) => ({ unavailable: true, message: error.message })),
    fetchJson(storyformUrl).catch((error) => ({ unavailable: true, message: error.message })),
  ]);

  const snapshot = {
    label,
    apiMode,
    omi: snapshotOMI(omi),
    bibleJson: normalizeJson(bible),
    storyformJson: normalizeJson(storyform),
  };
  logAction('read_only_project_snapshot', snapshot);
  return snapshot;
}

async function waitForAppReady() {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    logAction('networkidle_timeout_ignored');
  });
  await page.locator('.app-shell, .project-nav').first().waitFor({ state: 'visible', timeout: 20000 });
}

async function openEvidenceDrawer() {
  await page.goto(APP_BASE_URL, { waitUntil: 'domcontentloaded' });
  await waitForAppReady();

  const entry = page.locator('[data-testid="omi-workspace-entry"]').first();
  await entry.waitFor({ state: 'visible', timeout: 15000 });
  await entry.click();
  await page.locator('[data-testid="omi-dashboard"]').waitFor({ state: 'visible', timeout: 15000 });

  const reviewCandidates = page.getByRole('button', { name: /Review candidates for Candidates/i }).first();
  await reviewCandidates.click();
  await page.locator('[data-testid="omi-candidate-detail"]').waitFor({ state: 'visible', timeout: 15000 });

  const trigger = page.locator('[data-testid="omi-evidence-drawer-trigger"]').first();
  await trigger.waitFor({ state: 'visible', timeout: 15000 });
  const closedDocumentMetrics = await documentWidthMetrics();
  await trigger.click();
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'visible', timeout: 15000 });
  await page.waitForTimeout(250);
  logAction('omi_evidence_drawer_opened');
  return { trigger, closedDocumentMetrics };
}

async function screenshot(name) {
  const safeName = name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
  const filePath = path.join(SCREENSHOT_DIR, `${safeName}.png`);
  await page.screenshot({ path: filePath, fullPage: true });
  logAction('screenshot', { name, filePath });
  return filePath;
}

async function visibleText(locator) {
  return (await locator.innerText().catch(() => '')).trim();
}

async function documentWidthMetrics() {
  return page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
}

async function assertDrawerContainment(viewName, closedDocumentMetrics) {
  const drawer = page.locator('[data-testid="omi-evidence-drawer"]').first();
  const box = await drawer.boundingBox();
  const viewport = page.viewportSize();
  const openDocumentMetrics = await documentWidthMetrics();
  const tolerance = 1;
  const contained = Boolean(
    box
    && viewport
    && box.x >= -tolerance
    && box.y >= -tolerance
    && box.x + box.width <= viewport.width + tolerance
    && box.y + box.height <= viewport.height + tolerance
  );

  assertEvidence(`${viewName}: drawer is fully contained within the viewport`, contained, {
    box,
    viewport,
  });
  assertEvidence(`${viewName}: drawer causes no document-level horizontal overflow`, (
    openDocumentMetrics.scrollWidth <= Math.max(
      closedDocumentMetrics.scrollWidth,
      openDocumentMetrics.clientWidth,
    )
  ), {
    closedDocumentMetrics,
    openDocumentMetrics,
  });
}

async function assertDrawerVisibleEvidence(viewName) {
  const drawer = page.locator('[data-testid="omi-evidence-drawer"]').first();
  const namedDialog = page.getByRole('dialog', { name: /^Evidence scope:/ }).first();
  const drawerText = await visibleText(drawer);
  const sourceOpenButton = page.getByRole('button', { name: /^Open source record$/ }).first();
  const sourceReason = page.locator('[data-testid="omi-source-open-disabled-reason"]').first();

  assertEvidence(`${viewName}: Evidence Drawer is visible`, await drawer.isVisible(), {});
  assertEvidence(`${viewName}: dialog has accessible role and visible scope name`, await namedDialog.isVisible(), {
    accessibleName: await namedDialog.getAttribute('aria-labelledby'),
  });
  assertEvidence(`${viewName}: drawer title includes evidence scope`, drawerText.includes('Evidence scope:'), {});

  for (const requiredText of [
    'Source type',
    'Source location',
    'Quote exactness',
    'Confidence/support',
    'Original wording/excerpt',
    'Evidence summary',
    'Supports claim',
    'Limitations / ambiguity',
    'Provenance chain',
    'Related IDs',
    'Timestamps',
    'Source hash',
    'Snapshot hash',
    'Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.',
    'Viewing evidence does not copy source text into Memory/Canon.',
    'Confidence indicates support strength, not truth.',
    'Navigation / copy',
    'Review marking',
    'Owner note',
    'Close',
  ]) {
    assertEvidence(`${viewName}: required drawer copy visible: ${requiredText}`, drawerText.includes(requiredText), {});
  }

  assertEvidence(`${viewName}: Open source record disabled fail-closed`, await sourceOpenButton.isDisabled(), {});
  const describedBy = await sourceOpenButton.getAttribute('aria-describedby');
  const reasonId = await sourceReason.getAttribute('id');
  assertEvidence(`${viewName}: source open disabled reason associated`, describedBy === reasonId, {
    describedBy,
    reasonId,
    reasonText: await visibleText(sourceReason),
  });

  const applyButtons = await page.getByRole('button', { name: /Apply to Memory\/Canon/i }).count();
  const drawerApplyButtons = await drawer.getByRole('button', { name: /Apply to Memory\/Canon/i }).count();
  assertEvidence(`${viewName}: Evidence Drawer has no apply to Memory/Canon action`, drawerApplyButtons === 0, {
    pageApplyButtons: applyButtons,
    drawerApplyButtons,
  });

  const interactiveLabels = await drawer
    .locator('button, a, input, textarea, select')
    .evaluateAll((elements) => elements.map((element) => {
      const aria = element.getAttribute('aria-label') ?? '';
      const placeholder = element.getAttribute('placeholder') ?? '';
      const value = element.getAttribute('value') ?? '';
      return `${aria} ${placeholder} ${value} ${element.textContent ?? ''}`.trim();
    }));
  const matchedForbiddenControls = interactiveLabels.filter((label) => {
    const normalized = label.toLowerCase();
    return FORBIDDEN_CONTROL_LABELS.some((forbidden) => {
      const escaped = forbidden.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      return new RegExp(`(^|\\b)${escaped}(\\b|$)`, 'i').test(normalized);
    });
  });
  assertEvidence(`${viewName}: no generated prose controls visible in drawer`, matchedForbiddenControls.length === 0, {
    matchedForbiddenControls,
  });
}

async function assertFocusTrapAndReturnFocus() {
  const topClose = page.locator('[data-testid="omi-evidence-drawer-close-top"]').first();
  const bottomClose = page.locator('[data-testid="omi-evidence-drawer-close-bottom"]').first();
  const trigger = page.locator('[data-testid="omi-evidence-drawer-trigger"]').first();
  const initiallyFocused = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
  assertEvidence('desktop: drawer moves focus to labelled top close button', initiallyFocused === 'omi-evidence-drawer-close-top', {
    initiallyFocused,
  });

  await page.keyboard.press('Shift+Tab');
  const afterShiftTab = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
  assertEvidence('desktop: focus trap wraps backward inside drawer', afterShiftTab === 'omi-evidence-drawer-close-bottom', {
    afterShiftTab,
  });

  await page.keyboard.press('Tab');
  const afterForwardTab = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
  assertEvidence('desktop: focus trap wraps forward inside drawer', afterForwardTab === 'omi-evidence-drawer-close-top', {
    afterForwardTab,
  });

  await page.mouse.click(10, 10);
  assertEvidence('desktop: pointer interaction on overlay does not dismiss drawer', await topClose.isVisible(), {});

  await page.keyboard.press('Escape');
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'detached', timeout: 15000 });
  const returnedToTrigger = await trigger.evaluate((element) => document.activeElement === element);
  assertEvidence('desktop: Escape dismisses and returns focus to exact opener', returnedToTrigger, {});

  await trigger.click();
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'visible', timeout: 15000 });
  const reopenedFocus = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
  assertEvidence('desktop: drawer successfully reopens after Escape with accepted initial focus', (
    reopenedFocus === 'omi-evidence-drawer-close-top'
  ), { reopenedFocus });

  await bottomClose.scrollIntoViewIfNeeded();
  await bottomClose.click();
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'detached', timeout: 15000 });
  const buttonCloseReturnedToTrigger = await trigger.evaluate((element) => document.activeElement === element);
  assertEvidence('desktop: close button dismisses and returns focus to exact opener', buttonCloseReturnedToTrigger, {});

  await trigger.click();
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'visible', timeout: 15000 });
}

async function reopenAtViewport(width, height) {
  const topClose = page.locator('[data-testid="omi-evidence-drawer-close-top"]').first();
  const trigger = page.locator('[data-testid="omi-evidence-drawer-trigger"]').first();
  await topClose.click();
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'detached', timeout: 15000 });
  await page.setViewportSize({ width, height });
  await page.waitForTimeout(250);
  const closedDocumentMetrics = await documentWidthMetrics();
  await trigger.click();
  await page.locator('[data-testid="omi-evidence-drawer"]').waitFor({ state: 'visible', timeout: 15000 });
  await page.waitForTimeout(250);
  return closedDocumentMetrics;
}

async function assertMobileSheet(viewName, minimumWidth) {
  const drawer = page.locator('[data-testid="omi-evidence-drawer"]').first();
  const topClose = page.locator('[data-testid="omi-evidence-drawer-close-top"]').first();
  const bottomClose = page.locator('[data-testid="omi-evidence-drawer-close-bottom"]').first();
  const box = await drawer.boundingBox();

  assertEvidence(`${viewName}: Evidence Drawer is full-screen sheet width`, Boolean(box && box.width >= minimumWidth), { box });
  assertEvidence(`${viewName}: top close visible`, await topClose.isVisible(), {});
  assertEvidence(`${viewName}: bottom close visible`, await bottomClose.isVisible(), {});
}

async function runWorkflow() {
  logAction('workflow_start', {
    appBaseUrl: APP_BASE_URL,
    projectId: PROJECT_ID,
    evidenceDir: EVIDENCE_DIR,
  });

  await detectApiMode();
  beforeSnapshot = await readOnlyProjectSnapshot('before');

  browser = await playwrightChromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  await installApiGuard(context);
  page = await context.newPage();
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });
  page.on('console', (message) => {
    if (message.type() === 'error') {
      consoleErrors.push(message.text());
    }
  });
  page.on('requestfailed', (request) => {
    failedApplicationRequests.push({
      method: request.method(),
      url: request.url(),
      failure: request.failure()?.errorText ?? 'unknown',
    });
  });
  page.on('request', (request) => {
    const pathname = new URL(request.url()).pathname;
    if (request.method().toUpperCase() === 'GET' && pathname === CONTEXT_READINESS_PATH) {
      readinessRequestCount += 1;
    }
  });
  page.on('response', (response) => {
    const pathname = new URL(response.url()).pathname;
    if (pathname === CONTEXT_READINESS_PATH) {
      readinessResponses.push({ status: response.status(), url: response.url() });
    }
    if (response.status() >= 400) {
      failedApplicationResponses.push({ status: response.status(), url: response.url() });
    }
  });

  const desktopOpen = await openEvidenceDrawer();
  await assertDrawerVisibleEvidence('desktop');
  await assertDrawerContainment('desktop', desktopOpen.closedDocumentMetrics);
  await assertFocusTrapAndReturnFocus();
  desktopScreenshotPath = await screenshot('01-desktop-omi-evidence-drawer');

  const mobileClosedDocumentMetrics = await reopenAtViewport(390, 900);
  await assertDrawerVisibleEvidence('mobile');
  await assertDrawerContainment('mobile', mobileClosedDocumentMetrics);
  await assertMobileSheet('mobile', 389);
  mobileScreenshotPath = await screenshot('02-mobile-omi-evidence-drawer');

  const compactClosedDocumentMetrics = await reopenAtViewport(320, 568);
  await assertDrawerVisibleEvidence('compact mobile');
  await assertDrawerContainment('compact mobile', compactClosedDocumentMetrics);
  await assertMobileSheet('compact mobile', 319);
  compactMobileScreenshotPath = await screenshot('03-compact-mobile-omi-evidence-drawer');

  afterSnapshot = await readOnlyProjectSnapshot('after');
  assertEvidence('opening evidence drawer does not create candidates', beforeSnapshot.omi.candidateCount === afterSnapshot.omi.candidateCount, {
    before: beforeSnapshot.omi.candidateCount,
    after: afterSnapshot.omi.candidateCount,
  });
  assertEvidence('opening evidence drawer does not mutate approved Memory/Canon snapshot', (
    beforeSnapshot.omi.approvedMemoryTotal === afterSnapshot.omi.approvedMemoryTotal
    && beforeSnapshot.omi.approvedSnapshotJson === afterSnapshot.omi.approvedSnapshotJson
    && beforeSnapshot.bibleJson === afterSnapshot.bibleJson
    && beforeSnapshot.storyformJson === afterSnapshot.storyformJson
  ), { before: beforeSnapshot, after: afterSnapshot });
  assertEvidence('opening evidence drawer performs no mutating API requests', mutatingApiRequests.length === 0, {
    mutatingApiRequests,
    apiMode,
  });
  assertEvidence('browser reports no unexpected page errors', pageErrors.length === 0, { pageErrors });
  assertEvidence('browser reports no unexpected console errors', consoleErrors.length === 0, { consoleErrors });
  assertEvidence('browser reports no failed application requests', failedApplicationRequests.length === 0, {
    failedApplicationRequests,
  });
  assertEvidence('browser reports no failed application responses', failedApplicationResponses.length === 0, {
    failedApplicationResponses,
  });
  assertEvidence('browser observes at least one successful context-readiness GET request', (
    readinessRequestCount > 0 && readinessResponses.length > 0
  ), { readinessRequestCount, readinessResponses });
  assertEvidence('browser context-readiness responses are HTTP 200', (
    readinessResponses.length > 0
    && readinessResponses.every((response) => response.status === 200)
  ), { readinessResponses });
  assertEvidence('browser reports zero failed context-readiness responses', (
    failedApplicationResponses.every(
      (response) => new URL(response.url).pathname !== CONTEXT_READINESS_PATH,
    )
  ), { failedApplicationResponses });

  await context.close();
}

async function writeArtifacts(exitCode) {
  const result = failures.length === 0 ? 'PASS' : 'FAIL';
  const finishedAt = new Date().toISOString();
  const payload = {
    task: 'OMI Evidence Drawer Browser Evidence Only',
    result,
    exitCode,
    startedAt: RUN_STARTED_AT,
    finishedAt,
    appBaseUrl: APP_BASE_URL,
    projectId: PROJECT_ID,
    apiMode,
    evidenceDir: EVIDENCE_DIR,
    validationMarkdown: VALIDATION_MD,
    screenshots: {
      desktop: desktopScreenshotPath,
      mobile: mobileScreenshotPath,
      compactMobile: compactMobileScreenshotPath,
    },
    beforeSnapshot,
    afterSnapshot,
    readiness: {
      requestCount: readinessRequestCount,
      responses: readinessResponses,
    },
    failures,
    actions: workflowLog,
    safety: {
      noBackendCodeChangedByScript: true,
      noCandidatesCreatedByScript: beforeSnapshot?.omi?.candidateCount === afterSnapshot?.omi?.candidateCount,
      noMemoryCanonMutatedByScript: beforeSnapshot?.omi?.approvedSnapshotJson === afterSnapshot?.omi?.approvedSnapshotJson,
      noModelOrOllamaCalls: true,
      applyPromotionNotRunOrEnabled: true,
      noGeneratedProseControlsAdded: true,
      mutatingApiRequests,
      pageErrors,
      consoleErrors,
      failedApplicationRequests,
      failedApplicationResponses,
    },
  };

  await fs.writeFile(WORKFLOW_LOG_PATH, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');

  const assertionLines = workflowLog
    .filter((entry) => entry.action === 'assert_pass' || entry.action === 'assert_fail')
    .map((entry) => `- ${entry.action === 'assert_pass' ? 'PASS' : 'FAIL'}: ${entry.name}`);

  const reportLines = [
    '# OMI Evidence Drawer Browser Evidence',
    '',
    `- Result: **${result}**`,
    `- Exit code: \`${exitCode}\``,
    `- Started: \`${RUN_STARTED_AT}\``,
    `- Finished: \`${finishedAt}\``,
    `- App base URL: \`${APP_BASE_URL}\``,
    `- Project ID: \`${PROJECT_ID}\``,
    `- API mode: \`${apiMode}\``,
    `- Evidence directory: \`${path.relative(REPO_ROOT, EVIDENCE_DIR)}\``,
    `- Workflow log: \`${path.relative(REPO_ROOT, WORKFLOW_LOG_PATH)}\``,
    '',
    '## Screenshots',
    '',
    `- Desktop: \`${path.relative(REPO_ROOT, desktopScreenshotPath || path.join(SCREENSHOT_DIR, '01-desktop-omi-evidence-drawer.png'))}\``,
    `- Mobile: \`${path.relative(REPO_ROOT, mobileScreenshotPath || path.join(SCREENSHOT_DIR, '02-mobile-omi-evidence-drawer.png'))}\``,
    `- Compact mobile (320 x 568): \`${path.relative(REPO_ROOT, compactMobileScreenshotPath || path.join(SCREENSHOT_DIR, '03-compact-mobile-omi-evidence-drawer.png'))}\``,
    '',
    '## Assertions',
    '',
    ...assertionLines,
    '',
    '## Read-Only Snapshot Check',
    '',
    `- Candidate count before: \`${beforeSnapshot?.omi?.candidateCount ?? 'unavailable'}\``,
    `- Candidate count after: \`${afterSnapshot?.omi?.candidateCount ?? 'unavailable'}\``,
    `- Approved Memory/Canon total before: \`${beforeSnapshot?.omi?.approvedMemoryTotal ?? 'unavailable'}\``,
    `- Approved Memory/Canon total after: \`${afterSnapshot?.omi?.approvedMemoryTotal ?? 'unavailable'}\``,
    '',
    '## Safety Confirmations',
    '',
    '- Evidence-only browser navigation and GET snapshots only.',
    '- If the backend or candidate evidence data is unavailable, Playwright serves a read-only candidate evidence API fixture and blocks mutating API requests.',
    '- No backend code changed by this script.',
    '- No candidates were created by this script.',
    '- Memory/Canon snapshot, bible JSON, and storyform JSON were compared before/after.',
    '- No model/Ollama calls were made.',
    '- Apply-promotion was not run or enabled from the Evidence Drawer.',
    '- No generated prose controls were added by this script.',
    `- Mutating API request count: \`${mutatingApiRequests.length}\`.`,
    `- Page error count: \`${pageErrors.length}\`.`,
    `- Console error count: \`${consoleErrors.length}\`.`,
    `- Failed application request count: \`${failedApplicationRequests.length}\`.`,
    `- Failed application response count: \`${failedApplicationResponses.length}\`.`,
    `- Context-readiness GET request count: \`${readinessRequestCount}\`.`,
    `- Context-readiness response statuses: \`${readinessResponses.map((response) => response.status).join(', ') || 'none'}\`.`,
  ];

  if (failures.length > 0) {
    reportLines.push('', '## Failures', '');
    for (const failure of failures) {
      reportLines.push(`- ${failure.name}: \`${JSON.stringify(failure.details)}\``);
    }
  }

  await fs.writeFile(VALIDATION_MD, `${reportLines.join('\n')}\n`, 'utf8');
  logAction('write_artifacts', {
    result,
    workflowLogPath: WORKFLOW_LOG_PATH,
    validationMarkdown: VALIDATION_MD,
  });
}

async function cleanup() {
  if (browser) {
    await browser.close().catch(() => {});
  }
  if (viteProcess) {
    const pid = viteProcess.pid;
    if (pid) {
      try {
        process.kill(-pid, 'SIGTERM');
      } catch {
        viteProcess.kill('SIGTERM');
      }
    }
    await Promise.race([
      new Promise((resolve) => viteProcess.once('exit', resolve)),
      new Promise((resolve) => setTimeout(resolve, 1500)),
    ]);
    if (!viteProcess.killed && pid) {
      try {
        process.kill(-pid, 'SIGKILL');
      } catch {
        viteProcess.kill('SIGKILL');
      }
    }
  }
}

async function main() {
  let exitCode = 0;
  try {
    await ensureEvidenceDirs();
    playwrightChromium = await loadPlaywrightChromium();
    await startViteIfNeeded();
    await runWorkflow();
    exitCode = failures.length === 0 ? 0 : 1;
  } catch (error) {
    exitCode = 1;
    recordFailure('script execution failed', {
      message: error instanceof Error ? error.message : String(error),
    });
  } finally {
    await writeArtifacts(exitCode).catch((error) => {
      console.error(error instanceof Error ? error.stack : error);
      exitCode = 1;
    });
    await cleanup();
  }

  if (exitCode !== 0) {
    process.exitCode = exitCode;
  }
}

main();
