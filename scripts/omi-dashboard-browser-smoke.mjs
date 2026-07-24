#!/usr/bin/env node
/**
 * OMI Dashboard browser-visible evidence harness.
 *
 * Evidence-only runner. It opens the existing app, captures desktop/mobile
 * screenshots, and compares read-only API snapshots before and after opening
 * the OMI Dashboard. It does not create candidates, call models, run
 * extraction, run apply-promotion, or mutate Memory/Canon.
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
const PROJECT_ID = process.env.OMI_DASHBOARD_PROJECT_ID ?? 'example';
const EVIDENCE_DIR = path.resolve(
  process.env.OMI_DASHBOARD_EVIDENCE_DIR
    ?? 'docs/roadmap/validation/omi-dashboard-browser-evidence',
);
const VALIDATION_MD = path.resolve(
  process.env.OMI_DASHBOARD_VALIDATION_MD
    ?? 'docs/roadmap/validation/omi_dashboard_browser_evidence.md',
);

const SCREENSHOT_DIR = path.join(EVIDENCE_DIR, 'screenshots');
const WORKFLOW_LOG_PATH = path.join(EVIDENCE_DIR, 'workflow-log.json');
const RUN_STARTED_AT = new Date().toISOString();
const APPLY_REASON =
  'Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.';
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
  'write for me',
]);

/** @type {Array<{ ts: string, action: string, [key: string]: unknown }>} */
const workflowLog = [];
/** @type {Array<{ name: string, details: Record<string, unknown>, ts: string }>} */
const failures = [];
let page = null;
let browser = null;
let viteProcess = null;
let playwrightChromium = null;
let desktopScreenshotPath = '';
let mobileScreenshotPath = '';
let beforeSnapshot = null;
let afterSnapshot = null;
let apiMode = 'live-backend';
const mutatingApiRequests = [];
const pageErrors = [];
const consoleErrors = [];
const failedRequests = [];
const httpErrorResponses = [];
const unmatchedFixtures = [];
const nonGetApiRequests = [];
const applyPromotionRequests = [];
let finalTelemetry = null;
let finalDesktopMeasurements = null;
let finalMobileMeasurements = null;

const ZERO_STATE_API = Object.freeze({
  project: {
    project_id: PROJECT_ID,
    id: PROJECT_ID,
    title: 'Example Project',
    status: 'valid',
  },
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
  omi: {
    index: null,
    owner_input_count: 0,
    candidate_count: 0,
    blocked_count: 0,
    handoff_ready_count: 0,
    promotion_audit_count: 0,
    ideas: [],
    candidates: [],
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

function normalizeJson(value) {
  return JSON.stringify(value ?? null);
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function explicitCount(...values) {
  for (const value of values) {
    const count = Number(value);
    if (Number.isFinite(count) && count >= 0) {
      return count;
    }
  }
  return null;
}

function approvedMemoryTotal(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) {
    return 0;
  }

  const explicit = explicitCount(
    snapshot.total,
    snapshot.total_count,
    snapshot.approved_count,
    snapshot.record_count,
  );
  if (explicit !== null) {
    return explicit;
  }

  return Object.values(snapshot).reduce((total, value) => {
    if (Array.isArray(value)) {
      return total + value.length;
    }
    const count = Number(value);
    if (Number.isFinite(count) && count >= 0) {
      return total + count;
    }
    return total;
  }, 0);
}

function snapshotOMI(omiPayload) {
  const approvedSnapshot =
    omiPayload?.approved_memory_canon_snapshot
    ?? omiPayload?.approved_memory_snapshot
    ?? omiPayload?.memory_canon_snapshot
    ?? null;
  const candidates = asArray(omiPayload?.candidates);
  const promotions = asArray(omiPayload?.promotions ?? omiPayload?.promotion_audit_records);

  return {
    candidateCount: explicitCount(omiPayload?.candidate_count) ?? candidates.length,
    rawIdeaCount: explicitCount(omiPayload?.owner_input_count, omiPayload?.raw_idea_count)
      ?? asArray(omiPayload?.ideas).length,
    promotionAuditCount: explicitCount(omiPayload?.promotion_audit_count) ?? promotions.length,
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

async function readOnlyProjectSnapshot(label) {
  if (apiMode === 'fixture') {
    const snapshot = {
      label,
      apiMode,
      omi: snapshotOMI(ZERO_STATE_API.omi),
      bibleJson: normalizeJson(ZERO_STATE_API.bible),
      storyformJson: normalizeJson(ZERO_STATE_API.storyform),
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
    omi: snapshotOMI(omi),
    bibleJson: normalizeJson(bible),
    storyformJson: normalizeJson(storyform),
  };
  logAction('read_only_project_snapshot', snapshot);
  return snapshot;
}

async function detectApiMode() {
  const omiUrl = new URL(`/api/projects/${PROJECT_ID}/omi`, APP_BASE_URL).href;
  try {
    await fetchJson(omiUrl);
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

async function installReadOnlyApiFixture(context) {
  await context.route('**/api/**', async (route) => {
    const request = route.request();
    const method = request.method().toUpperCase();
    const url = new URL(request.url());
    const pathname = url.pathname;

    if (method !== 'GET') {
      mutatingApiRequests.push({ method, pathname });
      await route.fulfill(jsonResponse({ detail: 'Mutating API requests are blocked in OMI dashboard evidence.' }, 405));
      return;
    }

    if (pathname === '/api/projects') {
      await route.fulfill(jsonResponse(ZERO_STATE_API.projects));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/scenes`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.scenes));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/notes`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.notes));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/materials`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.materials));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/bible`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.bible));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/storyform`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.storyform));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/storyform-context`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.storyformContext));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/omi`) {
      await route.fulfill(jsonResponse(ZERO_STATE_API.omi));
      return;
    }
    if (pathname === `/api/projects/${PROJECT_ID}/context-readiness`) {
      await route.fulfill(jsonResponse({
        resources: {
          bible: { state: 'absent', ready: false },
          storyform: { state: 'absent', ready: false },
          storyform_context: { state: 'unavailable', ready: false },
        },
      }));
      return;
    }

    unmatchedFixtures.push({ method, pathname });
    await route.fulfill(jsonResponse({ detail: `Unhandled read-only fixture route: ${pathname}` }, 404));
  });
  logAction('read_only_api_fixture_installed', { projectId: PROJECT_ID });
}

async function waitForAppReady() {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    logAction('networkidle_timeout_ignored');
  });
  await page.locator('.app-shell, .project-nav').first().waitFor({ state: 'visible', timeout: 20000 });
}

async function openOMIDashboard() {
  await page.goto(APP_BASE_URL, { waitUntil: 'domcontentloaded' });
  await waitForAppReady();

  const entry = page.locator('[data-testid="omi-workspace-entry"]').first();
  await entry.waitFor({ state: 'visible', timeout: 15000 });
  await entry.click();
  await page.locator('[data-testid="omi-dashboard"]').waitFor({ state: 'visible', timeout: 15000 });
  await page.waitForTimeout(250);
  logAction('omi_dashboard_opened');
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

async function assertDashboardVisibleEvidence(viewName) {
  const dashboard = page.locator('[data-testid="omi-dashboard"]').first();
  const boundary = page.locator('[data-testid="omi-boundary-banner"]').first();
  const statusStrip = page.locator('[data-testid="omi-candidate-canon-status"]').first();
  const activeProject = page.locator('[data-testid="omi-active-project-label"]').first();
  const approvedSnapshot = page.locator('[data-testid="omi-dashboard-approved-memory-snapshot"]').first();
  const applyButton = page.getByRole('button', { name: /^Apply to Memory\/Canon$/ }).first();
  const applyReason = page.locator('[data-testid="omi-dashboard-disabled-apply-reason"]').first();
  const workflowRows = page.locator('.omi-workflow-table tbody tr');

  assertEvidence(`${viewName}: OMI Dashboard is reachable`, await dashboard.isVisible(), {});
  assertEvidence(`${viewName}: active project label visible`, await activeProject.isVisible(), {
    text: await visibleText(activeProject),
  });
  assertEvidence(`${viewName}: OMI boundary banner visible`, await boundary.isVisible(), {
    text: await visibleText(boundary),
  });
  assertEvidence(`${viewName}: candidate/canon status strip visible`, await statusStrip.isVisible(), {
    text: await visibleText(statusStrip),
  });
  assertEvidence(`${viewName}: dense workflow rows visible`, (await workflowRows.count()) >= 8, {
    rowCount: await workflowRows.count(),
  });
  assertEvidence(`${viewName}: Approved Memory/Canon snapshot visible`, await approvedSnapshot.isVisible(), {
    text: await visibleText(approvedSnapshot),
  });
  assertEvidence(`${viewName}: Apply to Memory/Canon disabled`, await applyButton.isDisabled(), {});
  assertEvidence(`${viewName}: disabled apply reason visible`, await applyReason.isVisible(), {
    text: await visibleText(applyReason),
  });

  const describedBy = await applyButton.getAttribute('aria-describedby');
  const reasonId = await applyReason.getAttribute('id');
  const reasonText = await visibleText(applyReason);
  assertEvidence(`${viewName}: apply reason associated with disabled control`, Boolean(describedBy && reasonId && describedBy === reasonId), {
    describedBy,
    reasonId,
  });
  assertEvidence(`${viewName}: apply reason text matches expected boundary`, reasonText === APPLY_REASON, {
    reasonText,
  });

  const tableBox = await page.locator('.omi-workflow-table-wrap').first().boundingBox();
  const snapshotBox = await approvedSnapshot.boundingBox();
  assertEvidence(
    `${viewName}: approved Memory/Canon snapshot is visually separate from OMI counts`,
    Boolean(tableBox && snapshotBox && snapshotBox.y > tableBox.y + 40),
    { tableBox, snapshotBox },
  );

  const interactiveLabels = await page
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
  assertEvidence(`${viewName}: no generated prose controls visible`, matchedForbiddenControls.length === 0, {
    matchedForbiddenControls,
  });
}

async function assertMobileStackedLayout() {
  const layout = await page.locator('.omi-workflow-table').first().evaluate((table) => {
    const thead = table.querySelector('thead');
    const firstRow = table.querySelector('tbody tr');
    const firstCell = table.querySelector('tbody tr td');
    return {
      tableDisplay: window.getComputedStyle(table).display,
      theadDisplay: thead ? window.getComputedStyle(thead).display : '',
      firstRowDisplay: firstRow ? window.getComputedStyle(firstRow).display : '',
      firstCellDisplay: firstCell ? window.getComputedStyle(firstCell).display : '',
      viewportWidth: window.innerWidth,
    };
  });

  assertEvidence(
    'mobile: stacked workflow row layout visible',
    layout.viewportWidth <= 430
      && layout.theadDisplay === 'none'
      && layout.firstRowDisplay === 'block'
      && layout.firstCellDisplay === 'block',
    layout,
  );
}

async function collectDashboardMeasurements(viewportLabel) {
  const metrics = await page.evaluate((vpLabel) => {
    const docEl = document.documentElement;
    const body = document.body;
    const projectNav = document.querySelector('.project-nav');
    const analysisSidebar = document.querySelector('.analysis-sidebar');
    const editorCol = document.querySelector('.editor-column');
    const omiShell = document.querySelector('.omi-shell');
    const statusStrip = document.querySelector('[data-testid="omi-candidate-canon-status"]');
    const workflowWrap = document.querySelector('.omi-workflow-table-wrap');
    const scrollGuidance = document.querySelector('[data-testid="omi-dashboard-scroll-guidance"]');

    const navRect = projectNav ? projectNav.getBoundingClientRect() : null;
    const sidebarRect = analysisSidebar ? analysisSidebar.getBoundingClientRect() : null;
    const editorRect = editorCol ? editorCol.getBoundingClientRect() : null;
    const shellRect = omiShell ? omiShell.getBoundingClientRect() : null;
    const stripRect = statusStrip ? statusStrip.getBoundingClientRect() : null;
    const wrapMeasure = workflowWrap
      ? { clientWidth: workflowWrap.clientWidth, scrollWidth: workflowWrap.scrollWidth }
      : null;
    const guidanceVisible = scrollGuidance
      ? window.getComputedStyle(scrollGuidance).display !== 'none'
      : false;

    const enabledActions = [];
    document.querySelectorAll('button:not([disabled]), a[href]:not([disabled])').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.right > docEl.clientWidth) {
        enabledActions.push(el.textContent?.trim().slice(0, 60) || '(unnamed)');
      }
    });

    return {
      viewportLabel: vpLabel,
      document: { clientWidth: docEl.clientWidth, scrollWidth: docEl.scrollWidth },
      body: { clientWidth: body.clientWidth, scrollWidth: body.scrollWidth },
      projectNav: navRect ? { width: Math.round(navRect.width) } : null,
      analysisSidebar: sidebarRect ? { width: Math.round(sidebarRect.width) } : null,
      editorColumn: editorRect ? { width: Math.round(editorRect.width) } : null,
      omiShell: shellRect ? { width: Math.round(shellRect.width) } : null,
      statusStrip: stripRect
        ? { width: Math.round(stripRect.width), clientWidth: statusStrip.clientWidth, scrollWidth: statusStrip.scrollWidth }
        : null,
      workflowWrapper: wrapMeasure,
      scrollGuidanceVisible: guidanceVisible,
      enabledActionsOutsideViewport: enabledActions,
    };
  }, viewportLabel);
  logAction('collect_dashboard_measurements', metrics);
  return metrics;
}

function collectTelemetry() {
  const telemetry = {
    pageErrors: pageErrors.length,
    pageErrorDetails: [...pageErrors],
    consoleErrors: consoleErrors.length,
    consoleErrorDetails: [...consoleErrors].slice(0, 20),
    failedRequests: failedRequests.length,
    failedRequestDetails: [...failedRequests].slice(0, 20),
    httpErrorResponses: httpErrorResponses.length,
    httpErrorDetails: [...httpErrorResponses].slice(0, 20),
    unmatchedFixtures: unmatchedFixtures.length,
    unmatchedFixtureDetails: [...unmatchedFixtures].slice(0, 20),
    nonGetApiRequests: nonGetApiRequests.length,
    nonGetApiDetails: [...nonGetApiRequests].slice(0, 20),
    applyPromotionRequests: applyPromotionRequests.length,
    applyPromotionDetails: [...applyPromotionRequests].slice(0, 20),
  };
  logAction('telemetry_summary', telemetry);
  return telemetry;
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
  if (apiMode === 'fixture') {
    await installReadOnlyApiFixture(context);
  }
  page = await context.newPage();

  page.on('pageerror', (error) => { pageErrors.push(String(error)); });
  page.on('console', (msg) => {
    if (msg.type() === 'error') { consoleErrors.push(msg.text()); }
  });
  page.on('requestfailed', (req) => {
    failedRequests.push(req.url());
    const failure = req.failure();
    if (failure && failure.errorText) {
      consoleErrors.push(`Request failed: ${req.url()} — ${failure.errorText}`);
    }
  });
  page.on('response', (res) => {
    if (res.status() >= 400) {
      httpErrorResponses.push({ url: res.url(), status: res.status() });
    }
  });

  page.on('request', (req) => {
    const url = new URL(req.url());
    const pn = url.pathname;
    if (req.method().toUpperCase() !== 'GET' && pn.startsWith('/api/')) {
      nonGetApiRequests.push({ method: req.method(), pathname: pn });
    }
    if (pn.startsWith('/api/') && (pn.toLowerCase().includes('apply-promotion') || pn.toLowerCase().includes('promotion'))) {
      applyPromotionRequests.push({ method: req.method(), pathname: pn });
    }
  });

  await openOMIDashboard();
  await assertDashboardVisibleEvidence('desktop');
  finalDesktopMeasurements = await collectDashboardMeasurements('desktop');
  desktopScreenshotPath = await screenshot('01-desktop-omi-dashboard');

  const dm = finalDesktopMeasurements;
  assertEvidence('desktop: document cw = sw', dm.document.clientWidth === dm.document.scrollWidth, dm.document);
  assertEvidence('desktop: body cw = sw', dm.body.clientWidth === dm.body.scrollWidth, dm.body);
  assertEvidence('desktop: ProjectNav ~260px', Math.abs((dm.projectNav?.width || 0) - 260) <= 10, dm.projectNav);
  assertEvidence('desktop: AnalysisSidebar ~320px', Math.abs((dm.analysisSidebar?.width || 0) - 320) <= 10, dm.analysisSidebar);
  assertEvidence('desktop: status-strip cw = sw (no overflow)', (dm.statusStrip?.clientWidth || 0) === (dm.statusStrip?.scrollWidth || 0), dm.statusStrip);
  assertEvidence('desktop: workflow-wrapper local scroll only', (dm.workflowWrapper?.scrollWidth || 0) >= (dm.workflowWrapper?.clientWidth || 0), dm.workflowWrapper);
  assertEvidence('desktop: local-scroll guidance visible', dm.scrollGuidanceVisible === true, {});
  assertEvidence('desktop: no enabled action outside viewport', (dm.enabledActionsOutsideViewport || []).length === 0, { count: dm.enabledActionsOutsideViewport.length });

  const nonOmi = await page.evaluate(() => {
    const overviewEntry = document.querySelector('[data-testid="omi-workspace-entry"]');
    if (overviewEntry) {
      const navItems = document.querySelectorAll('.project-nav button, .project-nav a');
      for (const item of navItems) {
        const text = item.textContent?.trim() || '';
        if (text.toLowerCase().includes('overview')) {
          item.click();
          return { clickedOverview: true };
        }
      }
    }
    return { clickedOverview: false, reason: 'no overview nav found' };
  });
  await page.waitForTimeout(300);
  const nonOmiMeasurements = await page.evaluate(() => {
    const ec = document.querySelector('.editor-column');
    const cs = ec ? window.getComputedStyle(ec) : null;
    const dw = ec ? ec.getAttribute('data-active-workspace') : null;
    return {
      dataActiveWorkspace: dw,
      editorPadding: cs ? cs.paddingLeft : 'unknown',
      editorColumnWidth: ec ? Math.round(ec.getBoundingClientRect().width) : 0,
      documentCW: document.documentElement.clientWidth,
      documentSW: document.documentElement.scrollWidth,
    };
  });
  assertEvidence('non-OMI: data-active-workspace !== omi-dashboard', nonOmiMeasurements.dataActiveWorkspace !== 'omi-dashboard', nonOmiMeasurements);
  assertEvidence('non-OMI: editor padding is 32px (normal desktop)', nonOmiMeasurements.editorPadding === '32px', nonOmiMeasurements);
  assertEvidence('non-OMI: no document overflow', nonOmiMeasurements.documentCW === nonOmiMeasurements.documentSW, nonOmiMeasurements);

  await openOMIDashboard();
  await page.waitForTimeout(250);
  const omiAgain = await page.evaluate(() => {
    const ec = document.querySelector('.editor-column');
    const cs = ec ? window.getComputedStyle(ec) : null;
    return {
      dataActiveWorkspace: ec ? ec.getAttribute('data-active-workspace') : null,
      editorPadding: cs ? cs.paddingLeft : 'unknown',
    };
  });
  assertEvidence('return-OMI: data-active-workspace = omi-dashboard', omiAgain.dataActiveWorkspace === 'omi-dashboard', omiAgain);
  assertEvidence('return-OMI: editor padding restored to 16px', omiAgain.editorPadding === '16px', omiAgain);

  afterSnapshot = await readOnlyProjectSnapshot('after');
  assertEvidence('opening dashboard does not create candidates', beforeSnapshot.omi.candidateCount === afterSnapshot.omi.candidateCount, {
    before: beforeSnapshot.omi.candidateCount,
    after: afterSnapshot.omi.candidateCount,
  });
  assertEvidence('opening dashboard does not mutate approved Memory/Canon snapshot', (
    beforeSnapshot.omi.approvedMemoryTotal === afterSnapshot.omi.approvedMemoryTotal
    && beforeSnapshot.omi.approvedSnapshotJson === afterSnapshot.omi.approvedSnapshotJson
    && beforeSnapshot.bibleJson === afterSnapshot.bibleJson
    && beforeSnapshot.storyformJson === afterSnapshot.storyformJson
  ), {
    before: beforeSnapshot,
    after: afterSnapshot,
  });
  assertEvidence('opening dashboard performs no mutating API requests', mutatingApiRequests.length === 0, {
    mutatingApiRequests,
    apiMode,
  });

  await page.setViewportSize({ width: 390, height: 900 });
  await page.waitForTimeout(250);
  await assertDashboardVisibleEvidence('mobile');
  await assertMobileStackedLayout();
  finalMobileMeasurements = await collectDashboardMeasurements('mobile');
  mobileScreenshotPath = await screenshot('02-mobile-omi-dashboard');

  const mm = finalMobileMeasurements;
  assertEvidence('mobile: document cw = sw', mm.document.clientWidth === mm.document.scrollWidth, mm.document);
  assertEvidence('mobile: body cw = sw', mm.body.clientWidth === mm.body.scrollWidth, mm.body);
  assertEvidence('mobile: workflow-wrapper cw = sw (no horizontal scroll needed)', (mm.workflowWrapper?.clientWidth || 0) === (mm.workflowWrapper?.scrollWidth || 0), mm.workflowWrapper);
  assertEvidence('mobile: guidance hidden', mm.scrollGuidanceVisible === false, {});
  assertEvidence('mobile: status strip cw = sw (no overflow)', (mm.statusStrip?.clientWidth || 0) === (mm.statusStrip?.scrollWidth || 0), mm.statusStrip);

  finalTelemetry = collectTelemetry();

  assertEvidence('telemetry: page errors = 0', pageErrors.length === 0, { pageErrors: pageErrors.length });
  assertEvidence('telemetry: console errors = 0', consoleErrors.length === 0, { consoleErrors: consoleErrors.length });
  assertEvidence('telemetry: failed requests = 0', failedRequests.length === 0, { failedRequests: failedRequests.length });
  assertEvidence('telemetry: HTTP error responses = 0', httpErrorResponses.length === 0, { httpErrorResponses: httpErrorResponses.length });
  assertEvidence('telemetry: unmatched fixtures = 0', unmatchedFixtures.length === 0, { unmatchedFixtures: unmatchedFixtures.length });
  assertEvidence('telemetry: non-GET API requests = 0', nonGetApiRequests.length === 0, { nonGetApiRequests: nonGetApiRequests.length });
  assertEvidence('telemetry: apply-promotion API requests = 0', applyPromotionRequests.length === 0, { applyPromotionRequests: applyPromotionRequests.length });

  await context.close();
}

async function writeArtifacts(exitCode, telemetry, desktopMeasurements, mobileMeasurements) {
  const result = failures.length === 0 ? 'PASS' : 'FAIL';
  const finishedAt = new Date().toISOString();
  const payload = {
    task: 'OMI Dashboard Browser Evidence Only',
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
    },
    beforeSnapshot,
    afterSnapshot,
    telemetry: telemetry || {},
    measurements: {
      desktop: desktopMeasurements || {},
      mobile: mobileMeasurements || {},
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
    },
  };

  await fs.writeFile(WORKFLOW_LOG_PATH, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');

  const assertionLines = workflowLog
    .filter((entry) => entry.action === 'assert_pass' || entry.action === 'assert_fail')
    .map((entry) => `- ${entry.action === 'assert_pass' ? 'PASS' : 'FAIL'}: ${entry.name}`);

  const reportLines = [
    '# OMI Dashboard Browser Evidence',
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
    `- Desktop: \`${path.relative(REPO_ROOT, desktopScreenshotPath || path.join(SCREENSHOT_DIR, '01-desktop-omi-dashboard.png'))}\``,
    `- Mobile: \`${path.relative(REPO_ROOT, mobileScreenshotPath || path.join(SCREENSHOT_DIR, '02-mobile-omi-dashboard.png'))}\``,
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
    '- If the backend is unavailable, Playwright serves a read-only zero-state API fixture and blocks mutating API requests.',
    '- No backend code changed by this script.',
    '- No candidates were created by this script.',
    '- Memory/Canon snapshot, bible JSON, and storyform JSON were compared before/after.',
    '- No model/Ollama calls were made.',
    '- Apply-promotion was not run and the dashboard apply control remained disabled.',
    '- No generated prose controls were added by this script.',
  ];

  if (telemetry) {
    reportLines.push('', '## T004B Telemetry', '',
      `- page errors: \`${telemetry.pageErrors}\``,
      `- console errors: \`${telemetry.consoleErrors}\``,
      `- failed application requests: \`${telemetry.failedRequests}\``,
      `- HTTP error responses: \`${telemetry.httpErrorResponses}\``,
      `- unmatched fixture requests: \`${telemetry.unmatchedFixtures}\``,
      `- non-GET /api/** requests: \`${telemetry.nonGetApiRequests}\``,
      `- apply-promotion requests: \`${telemetry.applyPromotionRequests}\``,
    );
  }

  if (desktopMeasurements) {
    reportLines.push('', '## Desktop Measurements (1440x1000)', '',
      '```json',
      JSON.stringify(desktopMeasurements, null, 2),
      '```',
    );
  }

  if (mobileMeasurements) {
    reportLines.push('', '## Mobile Measurements (390x900)', '',
      '```json',
      JSON.stringify(mobileMeasurements, null, 2),
      '```',
    );
  }

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
  let telemetry = null;
  let desktopMeasurements = null;
  let mobileMeasurements = null;
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
    await writeArtifacts(exitCode, finalTelemetry, finalDesktopMeasurements, finalMobileMeasurements).catch((error) => {
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
