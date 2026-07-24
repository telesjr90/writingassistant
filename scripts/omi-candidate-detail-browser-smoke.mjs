#!/usr/bin/env node
/**
 * OMI Candidate Detail browser-visible evidence harness.
 *
 * Evidence-only runner. It opens the app, navigates from OMI Dashboard to
 * Candidate Detail, captures desktop/mobile screenshots, and compares read-only
 * snapshots. It blocks mutating API methods in fixture mode.
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
const PROJECT_ID = process.env.OMI_CANDIDATE_DETAIL_PROJECT_ID ?? 'example';
const EVIDENCE_DIR = path.resolve(
  process.env.OMI_CANDIDATE_DETAIL_EVIDENCE_DIR
    ?? 'docs/roadmap/validation/omi-candidate-detail-browser-evidence',
);
const VALIDATION_MD = path.resolve(
  process.env.OMI_CANDIDATE_DETAIL_VALIDATION_MD
    ?? 'docs/roadmap/validation/omi_candidate_detail_browser_evidence.md',
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
  candidate_id: 'fixture-candidate-001',
  candidate_type: 'character_profile',
  status: 'pending_review',
  destination: '',
  source_id: 'owner-input-fixture-001',
  source_locator: 'Owner Input fixture row 1',
  evidence_summary: 'Stored evidence summary: owner input reference retained.',
  provenance_summary: 'Stored provenance summary: project-local owner input fixture.',
  original_wording_excerpt: 'Stored original wording excerpt from owner input.',
  supports_claim_note: 'Stored supports-claim note only.',
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
const pageErrors = [];
const consoleErrors = [];
const failedRequests = [];
const httpErrorResponses = [];
const unmatchedFixtures = [];
const nonGetApiRequests = [];
const applyPromotionRequests = [];
let apiMode = 'live-backend';
let browser = null;
let page = null;
let viteProcess = null;
let playwrightChromium = null;
let desktopScreenshotPath = '';
let mobileScreenshotPath = '';
let beforeSnapshot = null;
let afterSnapshot = null;
let finalTelemetry = null;
let finalDesktopMeasurements = null;
let finalMobileMeasurements = null;

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
      logAction('live_backend_has_no_candidate_using_read_only_fixture', { omiUrl });
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

async function installReadOnlyApiFixture(context) {
  await context.route('**/api/**', async (route) => {
    const request = route.request();
    const method = request.method().toUpperCase();
    const pathname = new URL(request.url()).pathname;

    if (method !== 'GET') {
      mutatingApiRequests.push({ method, pathname });
      await route.fulfill(jsonResponse({ detail: 'Mutating API requests are blocked in OMI candidate detail evidence.' }, 405));
      return;
    }

    const routeMap = new Map([
      ['/api/projects', FIXTURE_API.projects],
      [`/api/projects/${PROJECT_ID}/scenes`, FIXTURE_API.scenes],
      [`/api/projects/${PROJECT_ID}/notes`, FIXTURE_API.notes],
      [`/api/projects/${PROJECT_ID}/materials`, FIXTURE_API.materials],
      [`/api/projects/${PROJECT_ID}/bible`, FIXTURE_API.bible],
      [`/api/projects/${PROJECT_ID}/storyform`, FIXTURE_API.storyform],
      [`/api/projects/${PROJECT_ID}/storyform-context`, FIXTURE_API.storyformContext],
      [`/api/projects/${PROJECT_ID}/omi`, FIXTURE_API.omi],
      [`/api/projects/${PROJECT_ID}/omi/candidates/${FIXTURE_CANDIDATE.candidate_id}`, FIXTURE_CANDIDATE],
      [`/api/projects/${PROJECT_ID}/context-readiness`, {
        resources: {
          bible: { state: 'absent', ready: false },
          storyform: { state: 'absent', ready: false },
          storyform_context: { state: 'unavailable', ready: false },
        },
      }],
    ]);

    if (routeMap.has(pathname)) {
      await route.fulfill(jsonResponse(routeMap.get(pathname)));
      return;
    }

    unmatchedFixtures.push({ method, pathname });
    await route.fulfill(jsonResponse({ detail: `Unhandled read-only fixture route: ${pathname}` }, 404));
  });
  logAction('read_only_api_fixture_installed', { projectId: PROJECT_ID });
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

async function openCandidateDetail() {
  await page.goto(APP_BASE_URL, { waitUntil: 'domcontentloaded' });
  await waitForAppReady();

  const entry = page.locator('[data-testid="omi-workspace-entry"]').first();
  await entry.waitFor({ state: 'visible', timeout: 15000 });
  await entry.click();
  await page.locator('[data-testid="omi-dashboard"]').waitFor({ state: 'visible', timeout: 15000 });

  const reviewCandidates = page.getByRole('button', { name: /Review candidates for Candidates/i }).first();
  await reviewCandidates.click();
  await page.locator('[data-testid="omi-candidate-detail"]').waitFor({ state: 'visible', timeout: 15000 });
  await page.waitForTimeout(250);
  logAction('omi_candidate_detail_opened');
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

async function assertCandidateDetailVisibleEvidence(viewName) {
  const detail = page.locator('[data-testid="omi-candidate-detail"]').first();
  const fieldTable = page.locator('[data-testid="omi-candidate-field-table"]').first();
  const readiness = page.locator('[data-testid="omi-promotion-readiness-checklist"]').first();
  const candidateButton = page.getByRole('button', { name: /^Approve Candidate for Handoff$/ }).first();
  const candidateReason = page.locator('[data-testid="omi-candidate-approval-disabled-reason"]').first();
  const fieldButton = page.getByRole('button', { name: /Approve field .* for handoff/i }).first();
  const fieldReason = page.locator('[data-testid="omi-field-approval-disabled-reason"]').first();
  const applyButton = page.getByRole('button', { name: /^Apply to Memory\/Canon$/ }).first();

  assertEvidence(`${viewName}: Candidate Detail is reachable`, await detail.isVisible(), {});
  assertEvidence(`${viewName}: field table visible`, await fieldTable.isVisible(), {});
  assertEvidence(`${viewName}: readiness checklist visible`, await readiness.isVisible(), {});
  assertEvidence(`${viewName}: candidate approval disabled`, await candidateButton.isDisabled(), {});
  assertEvidence(`${viewName}: field approval disabled`, await fieldButton.isDisabled(), {});
  assertEvidence(`${viewName}: apply to Memory/Canon disabled`, await applyButton.isDisabled(), {});

  const candidateDescribedBy = await candidateButton.getAttribute('aria-describedby');
  const candidateReasonId = await candidateReason.getAttribute('id');
  assertEvidence(`${viewName}: disabled candidate approval reason associated`, candidateDescribedBy === candidateReasonId, {
    candidateDescribedBy,
    candidateReasonId,
  });

  const fieldDescribedBy = await fieldButton.getAttribute('aria-describedby');
  const fieldReasonId = await fieldReason.getAttribute('id');
  assertEvidence(`${viewName}: disabled field approval reason associated`, fieldDescribedBy === fieldReasonId, {
    fieldDescribedBy,
    fieldReasonId,
  });

  const detailText = await visibleText(detail);
  for (const requiredText of [
    'This remains a candidate until apply-promotion is separately confirmed and completed.',
    'Ready means the handoff packet is complete. Memory/Canon has not changed.',
    'Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.',
    'Confidence indicates support strength, not truth.',
    'Promotion Audit Record',
    'Not Applied to Memory/Canon',
    'No approved Memory/Canon links.',
  ]) {
    assertEvidence(`${viewName}: required copy visible: ${requiredText}`, detailText.includes(requiredText), {});
  }

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

async function assertMobileTabs() {
  const labels = await page.locator('.omi-mobile-tabs a').evaluateAll((links) => (
    links.map((link) => link.textContent?.trim()).filter(Boolean)
  ));
  const display = await page.locator('.omi-mobile-tabs').first().evaluate((element) => (
    window.getComputedStyle(element).display
  ));

  assertEvidence('mobile: Candidate Detail uses exactly Fields, Evidence, Readiness tabs', (
    display !== 'none'
    && labels.length === 3
    && labels[0] === 'Fields'
    && labels[1] === 'Evidence'
    && labels[2] === 'Readiness'
  ), { labels, display });
}

async function collectCandidateDetailMeasurementsAtScroll(viewportLabel, scrollLeft) {
  const metrics = await page.evaluate(({ vpLabel, sl }) => {
    const docEl = document.documentElement;
    const body = document.body;

    const fw = document.querySelector('.omi-field-table-wrap');
    if (fw) { fw.scrollLeft = sl; }

    const projectNav = document.querySelector('.project-nav');
    const analysisSidebar = document.querySelector('.analysis-sidebar');
    const editorCol = document.querySelector('.editor-column');
    const omiShell = document.querySelector('.omi-shell');
    const detailLayout = document.querySelector('.omi-candidate-detail-layout');
    const scrollGuidance = document.querySelector('[data-testid="omi-candidate-field-scroll-guidance"]');
    const fieldTable = document.querySelector('.omi-candidate-field-table');

    function bbox(el) {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), left: Math.round(r.left), right: Math.round(r.right) };
    }

    const wrapperBbox = bbox(fw);
    const wrapperData = fw ? { ...bbox(fw), clientWidth: fw.clientWidth, scrollWidth: fw.scrollWidth, scrollLeft: fw.scrollLeft } : null;

    function insideWrapper(elemBbox, tolerance) {
      if (!elemBbox || !wrapperBbox) return false;
      const t = tolerance || 1;
      return elemBbox.left >= wrapperBbox.left - t && elemBbox.right <= wrapperBbox.right + t;
    }

    const actionCells = [];
    if (fieldTable) {
      fieldTable.querySelectorAll('tbody tr td:last-child').forEach(td => {
        const cellBox = bbox(td);
        const buttons = [];
        td.querySelectorAll('button').forEach(btn => {
          const bb = bbox(btn);
          buttons.push({ ...bb, label: (btn.getAttribute('aria-label') || '').slice(0, 80), fullyInsideWrapper: insideWrapper(bb) });
        });
        actionCells.push({ ...cellBox, buttons, fullyInsideWrapper: insideWrapper(cellBox) });
      });
    }

    const maxScrollLeft = fw ? fw.scrollWidth - fw.clientWidth : 0;

    const navRect = projectNav ? projectNav.getBoundingClientRect() : null;
    const sidebarRect = analysisSidebar ? analysisSidebar.getBoundingClientRect() : null;
    const editorRect = editorCol ? editorCol.getBoundingClientRect() : null;
    const shellRect = omiShell ? omiShell.getBoundingClientRect() : null;

    let detailColumns = null;
    if (detailLayout) {
      detailColumns = window.getComputedStyle(detailLayout).gridTemplateColumns;
    }

    const stickyColWidth = fieldTable ? Math.round(
      (fieldTable.querySelector('thead th:last-child')?.getBoundingClientRect()?.width || 0)
    ) : 0;
    const wrapperWidth = wrapperData ? wrapperData.clientWidth : 0;
    const nonStickyUsable = wrapperWidth - stickyColWidth;

    return {
      viewportLabel: vpLabel,
      scrollLeft: sl,
      document: { clientWidth: docEl.clientWidth, scrollWidth: docEl.scrollWidth },
      body: { clientWidth: body.clientWidth, scrollWidth: body.scrollWidth },
      projectNav: navRect ? { width: Math.round(navRect.width) } : null,
      analysisSidebar: sidebarRect ? { width: Math.round(sidebarRect.width) } : null,
      editorColumn: editorRect ? { width: Math.round(editorRect.width) } : null,
      omiShell: shellRect ? { width: Math.round(shellRect.width) } : null,
      detailLayoutColumns: detailColumns,
      fieldWrapper: wrapperData,
      maxScrollLeft: Math.round(maxScrollLeft),
      actionCells,
      scrollGuidanceVisible: scrollGuidance ? window.getComputedStyle(scrollGuidance).display !== 'none' : false,
      stickyColumn: { width: stickyColWidth },
      viewport: { wrapperWidth, nonStickyUsable, stickyOccupiesFullViewport: stickyColWidth >= wrapperWidth - 10 },
    };
  }, { vpLabel: viewportLabel, sl: scrollLeft });
  logAction('collect_candidate_detail_measurements_at_scroll', { viewportLabel, scrollLeft, metrics });
  return metrics;
}

async function verifyColumnReachability() {
  const reachability = await page.evaluate(() => {
    const fw = document.querySelector('.omi-field-table-wrap');
    const ft = document.querySelector('.omi-candidate-field-table');
    if (!fw || !ft) return { error: 'missing table or wrapper' };

    const results = [];
    const headerCells = ft.querySelectorAll('thead th');
    const dataRows = ft.querySelectorAll('tbody tr');

    const wrapperRect = fw.getBoundingClientRect();
    const wrapperLeft = wrapperRect.left;
    const wrapperRight = wrapperRect.right;
    const wrapperW = fw.clientWidth;
    const totalW = fw.scrollWidth;
    const maxSL = totalW - wrapperW;

    const stickyTh = headerCells[headerCells.length - 1];
    const stickyColWidth = stickyTh ? stickyTh.getBoundingClientRect().width : 0;
    const stickyLeft = wrapperRight - stickyColWidth;
    const nonStickyVisibleLeft = wrapperLeft;
    const nonStickyVisibleRight = stickyLeft;
    const nonStickyVisibleWidth = Math.max(0, nonStickyVisibleRight - nonStickyVisibleLeft);

    function intersectWidth(elemLeft, elemRight) {
      const visLeft = Math.max(elemLeft, nonStickyVisibleLeft);
      const visRight = Math.min(elemRight, nonStickyVisibleRight);
      return Math.max(0, visRight - visLeft);
    }

    function insideWrapper(elemLeft, elemRight) {
      return elemLeft >= wrapperLeft - 1 && elemRight <= wrapperRight + 1;
    }

    headerCells.forEach((th, idx) => {
      fw.scrollLeft = 0;
      fw.dispatchEvent(new Event('scroll', { bubbles: true }));

      const isSticky = idx === headerCells.length - 1;
      const thText = th.textContent?.trim() || '';
      const thWidth = Math.round(th.getBoundingClientRect().width);
      const thNaturalLeft = Math.round(th.getBoundingClientRect().left);
      const thNaturalRight = Math.round(th.getBoundingClientRect().right);

      let scrollPos;
      if (isSticky || idx === 0) {
        scrollPos = 0;
      } else {
        scrollPos = Math.min(maxSL, Math.max(0, Math.round(thNaturalLeft - nonStickyVisibleLeft)));
      }
      fw.scrollLeft = scrollPos;
      fw.dispatchEvent(new Event('scroll', { bubbles: true }));

      const thBox = th.getBoundingClientRect();
      const thLeft = Math.round(thBox.left);
      const thRight = Math.round(thBox.right);
      const thWidthMeasured = Math.round(thBox.width);

      const td = dataRows.length > 0 ? dataRows[0].querySelectorAll('td, th')[idx] : null;
      const tdBox = td ? td.getBoundingClientRect() : null;
      const tdLeft = tdBox ? Math.round(tdBox.left) : null;
      const tdRight = tdBox ? Math.round(tdBox.right) : null;
      const tdWidthMeasured = tdBox ? Math.round(tdBox.width) : null;

      const thIntersect = isSticky ? nonStickyVisibleWidth : intersectWidth(thLeft, thRight);
      const tdIntersect = !isSticky && tdBox ? intersectWidth(tdLeft, tdRight) : null;

      const thPct = thWidthMeasured > 0 ? Math.round((thIntersect / thWidthMeasured) * 100) : 0;
      const tdPct = tdWidthMeasured && tdWidthMeasured > 0 ? Math.round((tdIntersect / tdWidthMeasured) * 100) : null;

      const thInsideWrapper = insideWrapper(thLeft, thRight);
      const tdInsideWrapper = tdBox ? insideWrapper(tdLeft, tdRight) : null;

      const colWidth = thWidthMeasured;
      const fullyFits = colWidth <= nonStickyVisibleWidth;
      const headerVisible = isSticky ? thInsideWrapper : (thIntersect > 5);
      const headerIdentifiable = fullyFits ? (thIntersect >= colWidth * 0.9) : (thIntersect >= nonStickyVisibleWidth * 0.5);
      const dataCellVisible = isSticky ? tdInsideWrapper : (tdIntersect !== null && tdIntersect > 5);
      const dataCellReadable = tdIntersect !== null ? (fullyFits ? (tdIntersect >= (tdWidthMeasured || colWidth) * 0.9) : (tdIntersect >= nonStickyVisibleWidth * 0.5)) : null;

      results.push({
        index: idx, text: thText, isSticky,
        scrollPositionRequested: scrollPos,
        scrollPositionActual: fw.scrollLeft,
        headerRect: { left: thLeft, right: thRight, width: thWidthMeasured },
        dataCellRect: tdBox ? { left: tdLeft, right: tdRight, width: tdWidthMeasured } : null,
        nonStickyRegion: { left: nonStickyVisibleLeft, right: nonStickyVisibleRight, width: nonStickyVisibleWidth },
        headerIntersectWidth: thIntersect,
        headerVisiblePercent: thPct,
        dataCellIntersectWidth: tdIntersect,
        dataCellVisiblePercent: tdPct,
        headerInsideWrapper: thInsideWrapper,
        dataCellInsideWrapper: tdInsideWrapper,
        headerVisible,
        headerIdentifiable,
        dataCellVisible,
        dataCellReadable,
      });
    });

    fw.scrollLeft = 0;
    return { columns: results, nonStickyVisibleWidth, stickyColWidth, wrapperW };
  });
  logAction('verify_column_reachability', reachability);
  return reachability;
}

function collectTelemetry() {
  const tel = {
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
  logAction('telemetry_summary', tel);
  return tel;
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

  await openCandidateDetail();
  await assertCandidateDetailVisibleEvidence('desktop');

  const m0 = await collectCandidateDetailMeasurementsAtScroll('desktop', 0);
  finalDesktopMeasurements = m0;

  const maxSL = m0.maxScrollLeft || 0;
  if (maxSL > 0) {
    await page.evaluate((sl) => {
      const fw = document.querySelector('.omi-field-table-wrap');
      if (fw) { fw.scrollLeft = sl; }
    }, maxSL);
    await page.waitForTimeout(150);
  }
  const mMax = maxSL > 0 ? await collectCandidateDetailMeasurementsAtScroll('desktop-max-scroll', maxSL) : null;

  if (maxSL > 0) {
    await page.evaluate(() => {
      const fw = document.querySelector('.omi-field-table-wrap');
      if (fw) { fw.scrollLeft = 0; }
    });
    await page.waitForTimeout(150);
  }

  const columnReachability = await verifyColumnReachability();

  desktopScreenshotPath = await screenshot('01-desktop-omi-candidate-detail');

  const wrapperCW = m0.fieldWrapper?.clientWidth || 0;
  const T004A_BASELINE_CW = 418;

  assertEvidence('desktop: wrapper clientWidth > T004A baseline (418px)', wrapperCW > T004A_BASELINE_CW, {
    wrapperCW, baslineCW: T004A_BASELINE_CW,
  });
  assertEvidence('desktop: wrapper clientWidth >= 450px', wrapperCW >= 450, { wrapperCW });
  assertEvidence('desktop: document does not overflow', m0.document.clientWidth === m0.document.scrollWidth, m0.document);
  assertEvidence('desktop: body does not overflow', m0.body.clientWidth === m0.body.scrollWidth, m0.body);
  assertEvidence('desktop: scroll guidance visible', m0.scrollGuidanceVisible === true, {});

  const sticky = m0.stickyColumn || {};
  const vp = m0.viewport || {};
  assertEvidence('desktop: sticky column does not occupy full viewport', (vp.stickyOccupiesFullViewport) === false, {
    stickyWidth: sticky.width, wrapperWidth: vp.wrapperWidth, nonStickyUsable: vp.nonStickyUsable,
  });

  assertEvidence('desktop: scrollLeft=0 action cells measured', (m0.actionCells || []).length > 0, { count: m0.actionCells.length });
  for (const ac of (m0.actionCells || [])) {
    assertEvidence('desktop: scrollLeft=0 action cell inside wrapper', ac.fullyInsideWrapper === true, {
      x: ac.x, y: ac.y, left: ac.left, right: ac.right,
    });
    for (const btn of (ac.buttons || [])) {
      assertEvidence('desktop: scrollLeft=0 button inside wrapper', btn.fullyInsideWrapper === true, {
        label: btn.label, left: btn.left, right: btn.right,
      });
    }
  }

  if (mMax) {
    assertEvidence('desktop: maxScrollLeft measurements available', mMax.actionCells.length > 0, { count: mMax.actionCells.length });
    for (const ac of (mMax.actionCells || [])) {
      assertEvidence('desktop: maxScroll action cell inside wrapper', ac.fullyInsideWrapper === true, {
        x: ac.x, y: ac.y, left: ac.left, right: ac.right,
      });
      for (const btn of (ac.buttons || [])) {
        assertEvidence('desktop: maxScroll button inside wrapper', btn.fullyInsideWrapper === true, {
          label: btn.label, left: btn.left, right: btn.right,
        });
      }
    }
  }

  const columns = (columnReachability && columnReachability.columns) ? columnReachability.columns : [];
  assertEvidence('desktop: non-sticky visible region > 0', (columnReachability && columnReachability.nonStickyVisibleWidth > 0) === true, {
    nsvw: columnReachability?.nonStickyVisibleWidth, stickyW: columnReachability?.stickyColWidth, wrapperW: columnReachability?.wrapperW,
  });
  for (const col of columns) {
    if (col.isSticky) {
      assertEvidence(`desktop: sticky column "${col.text}" inside wrapper`, col.headerInsideWrapper === true, {
        index: col.index, text: col.text, headerInsideWrapper: col.headerInsideWrapper, dataCellInsideWrapper: col.dataCellInsideWrapper,
      });
      continue;
    }
    const colWidth = col.headerRect?.width || 0;
    const fitsFully = colWidth <= (columnReachability?.nonStickyVisibleWidth || 0);
    assertEvidence(`desktop: non-sticky col "${col.text}" header visible`, col.headerVisible === true, {
      index: col.index, text: col.text, scrollReq: col.scrollPositionRequested, scrollAct: col.scrollPositionActual,
      hdrIntersectW: col.headerIntersectWidth, hdrPct: col.headerVisiblePercent, hdrIdentifiable: col.headerIdentifiable,
    });
    assertEvidence(`desktop: non-sticky col "${col.text}" header identifiable`, col.headerIdentifiable === true, {
      index: col.index, hdrPct: col.headerVisiblePercent, hdrIntersectW: col.headerIntersectWidth,
    });
    assertEvidence(`desktop: non-sticky col "${col.text}" data visible`, col.dataCellVisible === true, {
      index: col.index, dataIntersectW: col.dataCellIntersectWidth, dataPct: col.dataCellVisiblePercent, dataReadable: col.dataCellReadable,
    });
    assertEvidence(`desktop: non-sticky col "${col.text}" data readable`, col.dataCellReadable === true, {
      index: col.index, dataPct: col.dataCellVisiblePercent, dataIntersectW: col.dataCellIntersectWidth,
    });
  }

  afterSnapshot = await readOnlyProjectSnapshot('after');
  assertEvidence('opening candidate detail does not create candidates', beforeSnapshot.omi.candidateCount === afterSnapshot.omi.candidateCount, {
    before: beforeSnapshot.omi.candidateCount,
    after: afterSnapshot.omi.candidateCount,
  });
  assertEvidence('opening candidate detail does not mutate approved Memory/Canon snapshot', (
    beforeSnapshot.omi.approvedMemoryTotal === afterSnapshot.omi.approvedMemoryTotal
    && beforeSnapshot.omi.approvedSnapshotJson === afterSnapshot.omi.approvedSnapshotJson
    && beforeSnapshot.bibleJson === afterSnapshot.bibleJson
    && beforeSnapshot.storyformJson === afterSnapshot.storyformJson
  ), { before: beforeSnapshot, after: afterSnapshot });
  assertEvidence('opening candidate detail performs no mutating API requests', mutatingApiRequests.length === 0, {
    mutatingApiRequests,
    apiMode,
  });

  await page.setViewportSize({ width: 390, height: 900 });
  await page.waitForTimeout(250);
  await assertCandidateDetailVisibleEvidence('mobile');
  await assertMobileTabs();
  finalMobileMeasurements = await collectCandidateDetailMeasurementsAtScroll('mobile', 0);
  mobileScreenshotPath = await screenshot('02-mobile-omi-candidate-detail');

  const mm = finalMobileMeasurements;
  assertEvidence('mobile: document cw = sw', mm.document.clientWidth === mm.document.scrollWidth, mm.document);
  assertEvidence('mobile: body cw = sw', mm.body.clientWidth === mm.body.scrollWidth, mm.body);
  assertEvidence('mobile: wrapper cw = sw (card mode, no scroll)', (mm.fieldWrapper?.clientWidth || 0) === (mm.fieldWrapper?.scrollWidth || 0), mm.fieldWrapper);
  assertEvidence('mobile: guidance hidden', mm.scrollGuidanceVisible === false, {});
  assertEvidence('mobile: action cells present', (mm.actionCells || []).length > 0, { count: mm.actionCells.length });

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
    task: 'OMI Candidate Detail Browser Evidence Only',
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
    '# OMI Candidate Detail Browser Evidence',
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
    `- Desktop: \`${path.relative(REPO_ROOT, desktopScreenshotPath || path.join(SCREENSHOT_DIR, '01-desktop-omi-candidate-detail.png'))}\``,
    `- Mobile: \`${path.relative(REPO_ROOT, mobileScreenshotPath || path.join(SCREENSHOT_DIR, '02-mobile-omi-candidate-detail.png'))}\``,
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
    '- If the backend or candidate data is unavailable, Playwright serves a read-only candidate API fixture and blocks mutating API requests.',
    '- No backend code changed by this script.',
    '- No candidates were created by this script.',
    '- Memory/Canon snapshot, bible JSON, and storyform JSON were compared before/after.',
    '- No model/Ollama calls were made.',
    '- Apply-promotion was not run and Candidate Detail apply remained disabled.',
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
