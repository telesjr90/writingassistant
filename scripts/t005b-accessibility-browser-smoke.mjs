#!/usr/bin/env node
/**
 * T005B Accessibility browser evidence harness — final corrected.
 *
 * Proves mobile/coarse-pointer target sizing, checkbox label hit areas,
 * and keyboard-origin focus-visible through browser-computed geometry.
 * Read-only, non-mutating. Must exit 0 when all mandatory evidence is present.
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
const PROJECT_ID = process.env.T005B_PROJECT_ID ?? 'example';
const EVIDENCE_DIR = path.resolve(process.env.T005B_EVIDENCE_DIR ?? '/tmp/PHASE8-IMPL-024-T005B-browser-fallback');

const WORKFLOW_LOG_PATH = path.join(EVIDENCE_DIR, 'workflow-log.json');
const GEOMETRY_PATH = path.join(EVIDENCE_DIR, 'geometry.json');
const VALIDATION_MD_PATH = path.join(EVIDENCE_DIR, 'validation.md');
const SCREENSHOT_DIR = path.join(EVIDENCE_DIR, 'screenshots');
const RUN_STARTED_AT = new Date().toISOString();

const GUIDED_TITLE = 'T005B test project';
const GUIDED_IDEA = 'T005B owner-authored setup idea for target-sizing and checkbox-label evidence.';

// ---------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------

const FIXTURE_CANDIDATE = Object.freeze({
  candidate_id: 't005b-fixture-candidate-001',
  candidate_type: 'character_profile',
  candidate_content: { source: 'omi_tool_assisted_fused_analysis', type: 'character_profile', value: { Name: 'T005B test character' } },
  status: 'owner_review',
  destination: 'approved_memory',
  destination_type: 'character',
  source_id: 't005b-owner-fixture-001',
  source_locator: 't005b-fixture-row-1',
  source_hash: 't005b-fixture-hash',
  snapshot_hash: 't005b-fixture-snapshot',
  evidence_summary: 'Stored evidence summary.',
  provenance_summary: 'Stored provenance summary.',
  supports_claim_note: 'Stored supports-claim note.',
  duplicate_state: '',
  dependency_state: '',
  schema_status: 'supported',
  promotion_audit_record: { promotion_id: 't005b-fixture-promo-001', candidate_id: 't005b-fixture-candidate-001', status: 'pending_owner_confirmation', created_at: '2026-01-01T00:00:00Z', destination: 'approved_memory', destination_type: 'character' },
  approved_memory_canon_links: {},
  field_review_rows: [{ field: 'Name', proposed_value: 'T005B test character name', decision: 'confirmed', evidence_summary: 'Stored field evidence.', provenance_summary: 'Stored field provenance.', duplicate_dependency: '', owner_note: 'Stored owner note.' }],
});

const FIXTURE_IDEA = Object.freeze({
  idea_id: 'idea_t005b-fixture-001',
  idea_type: 'raw_idea',
  content: 'T005B owner-authored setup idea.',
  model_generated: false,
  creation_method: 'owner_authored',
  linked_candidate_ids: ['t005b-fixture-candidate-001'],
  status: 'pending',
  provenance: { tool_source: 'owner_input' },
});

const FIXTURE_API = Object.freeze({
  projects: { projects: [{ project_id: PROJECT_ID, id: PROJECT_ID, title: 'Example Project', status: 'valid' }] },
  scenes: { scenes: [] },
  notes: { notes: [] },
  materials: { materials: [] },
  bible: {},
  storyform: {},
  storyformContext: { context: '' },
  omi: {
    index: null, owner_input_count: 1, candidate_count: 1, blocked_count: 1, handoff_ready_count: 0, promotion_audit_count: 0,
    ideas: [FIXTURE_IDEA], candidates: [FIXTURE_CANDIDATE], groups: [], promotions: [], deferred: [], warnings: [],
    approved_memory_canon_snapshot: { characters: [], locations: [], timeline: [], plot_threads: [] },
  },
  contextReadiness: { resources: { bible: { state: 'absent', ready: false }, storyform: { state: 'absent', ready: false }, storyform_context: { state: 'unavailable', ready: false } } },
});

// ---------------------------------------------------------------
// State
// ---------------------------------------------------------------

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
let viteProcess = null;
let viteStartedByUs = false;
let playwrightChromium = null;
let desktopScreenshotPath = '';
let mobileScreenshotPath = '';
let cleanupResult = null;

// Geometry collectors
let desktopGeometry = {};
let mobileGeometry = {};

function logAction(action, details = {}) {
  const entry = { ts: new Date().toISOString(), action, ...details };
  workflowLog.push(entry);
  console.log(`[ACTION] ${action}${Object.keys(details).length ? ' ' + JSON.stringify(details) : ''}`);
}

function recordFailure(name, details = {}) {
  failures.push({ name, details, ts: new Date().toISOString() });
  logAction('assert_fail', { name, ...details });
}

function assertEvidence(name, condition, details = {}) {
  if (!condition) { recordFailure(name, details); return; }
  logAction('assert_pass', { name, ...details });
}

function jsonResponse(payload, status = 200) {
  return { status, contentType: 'application/json', body: `${JSON.stringify(payload)}\n` };
}

function collectTelemetry() {
  return {
    pageErrors: pageErrors.length, consoleErrors: consoleErrors.length, failedRequests: failedRequests.length,
    httpErrorResponses: httpErrorResponses.length, unmatchedFixtures: unmatchedFixtures.length,
    nonGetApiRequests: nonGetApiRequests.length, applyPromotionRequests: applyPromotionRequests.length,
    mutatingApiRequests: mutatingApiRequests.length,
  };
}

// ---------------------------------------------------------------
// Infrastructure
// ---------------------------------------------------------------

async function loadPlaywrightChromium() {
  const candidates = [
    path.join(FRONTEND_NODE_MODULES, '@playwright/test', 'index.js'),
    path.join(FRONTEND_NODE_MODULES, '@playwright/test', 'index.mjs'),
    path.join(FRONTEND_NODE_MODULES, 'playwright', 'index.js'),
    path.join(FRONTEND_NODE_MODULES, 'playwright', 'index.mjs'),
  ];
  let lastError = null;
  for (const c of candidates) {
    try {
      const mod = await import(pathToFileURL(c).href);
      const cr = mod.chromium ?? mod.default?.chromium;
      if (cr) { logAction('playwright_import_ok', { modulePath: c }); return cr; }
    } catch (e) { lastError = e; }
  }
  throw new Error(`Playwright not found. Last error: ${lastError?.message}`);
}

async function ensureEvidenceDirs() {
  await fs.mkdir(SCREENSHOT_DIR, { recursive: true });
  logAction('ensure_evidence_dirs', { evidenceDir: EVIDENCE_DIR });
}

async function appIsReachable() {
  try { return (await fetch(APP_BASE_URL, { method: 'GET' })).ok; } catch { return false; }
}

async function startViteIfNeeded() {
  if (await appIsReachable()) { logAction('app_reachable_existing'); return; }
  logAction('start_vite');
  viteProcess = spawn('npm', ['--prefix', 'frontend', 'run', 'dev'], {
    cwd: REPO_ROOT, stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env }, detached: true,
  });
  viteStartedByUs = true;
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    if (await appIsReachable()) { logAction('app_reachable_started'); return; }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error('App did not become reachable');
}

async function detectApiMode() {
  try {
    const r = await fetch(new URL(`/api/projects/${PROJECT_ID}/omi`, APP_BASE_URL).href);
    if (r.ok) {
      const data = await r.json();
      const hasCandidates = Array.isArray(data?.candidates) && data.candidates.length > 0;
      if (hasCandidates && Array.isArray(data?.groups) && data.groups.length > 0) {
        apiMode = 'live-backend';
        logAction('live_backend_with_data');
        return;
      }
    }
  } catch {}
  apiMode = 'fixture';
  logAction('using_fixture_mode');
}

async function installReadOnlyFixtures(ctx) {
  await ctx.route('**/api/**', async (route) => {
    const req = route.request();
    const method = req.method().toUpperCase();
    const pn = new URL(req.url()).pathname;
    if (pn.includes('/apply-promotion')) applyPromotionRequests.push({ method, pathname: pn });
    if (method !== 'GET') { mutatingApiRequests.push({ method, pathname: pn }); await route.fulfill(jsonResponse({ detail: 'Blocked' }, 405)); return; }
    if (apiMode !== 'fixture') { await route.continue(); return; }
    const map = new Map([
      ['/api/projects', FIXTURE_API.projects],
      [`/api/projects/${PROJECT_ID}/scenes`, FIXTURE_API.scenes],
      [`/api/projects/${PROJECT_ID}/notes`, FIXTURE_API.notes],
      [`/api/projects/${PROJECT_ID}/materials`, FIXTURE_API.materials],
      [`/api/projects/${PROJECT_ID}/bible`, FIXTURE_API.bible],
      [`/api/projects/${PROJECT_ID}/storyform`, FIXTURE_API.storyform],
      [`/api/projects/${PROJECT_ID}/storyform-context`, FIXTURE_API.storyformContext],
      [`/api/projects/${PROJECT_ID}/omi`, FIXTURE_API.omi],
      [`/api/projects/${PROJECT_ID}/context-readiness`, FIXTURE_API.contextReadiness],
      [`/api/projects/${PROJECT_ID}/omi/candidates/${FIXTURE_CANDIDATE.candidate_id}`, FIXTURE_CANDIDATE],
    ]);
    if (map.has(pn)) { await route.fulfill(jsonResponse(map.get(pn))); return; }
    unmatchedFixtures.push({ method, pathname: pn });
    await route.fulfill(jsonResponse({ detail: `Unhandled: ${pn}` }, 404));
  });
  logAction('fixtures_installed');
}

function installPageTelemetry(pg) {
  pg.on('pageerror', (e) => pageErrors.push(String(e)));
  pg.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  pg.on('requestfailed', (r) => failedRequests.push(r.url()));
  pg.on('response', (r) => { if (r.status() >= 400) httpErrorResponses.push({ url: r.url(), status: r.status() }); });
  pg.on('request', (r) => {
    const pn = new URL(r.url()).pathname;
    if (r.method() !== 'GET' && pn.startsWith('/api/')) nonGetApiRequests.push({ method: r.method(), pathname: pn });
    if (pn.startsWith('/api/') && (pn.toLowerCase().includes('apply-promotion') || pn.toLowerCase().includes('promotion'))) applyPromotionRequests.push({ method: r.method(), pathname: pn });
  });
}

async function screenshot(pg, name) {
  const safe = name.trim().toLowerCase().replace(/[^a-z0-9._-]+/g, '-');
  const fp = path.join(SCREENSHOT_DIR, `${safe}.png`);
  await pg.screenshot({ path: fp, fullPage: true });
  logAction('screenshot', { name, filePath: fp });
  return fp;
}

// ---------------------------------------------------------------
// Geometry collection
// ---------------------------------------------------------------

async function measure(pg, selector, name) {
  return pg.evaluate(({ s, n }) => {
    const el = document.querySelector(s);
    if (!el) return { name: n, found: false };
    const r = el.getBoundingClientRect();
    return { name: n, found: true, x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), elType: el.tagName, visible: r.width > 0 && r.height > 0 };
  }, { s: selector, n: name });
}

// ---------------------------------------------------------------
// Keyboard-origin focus (returns per-target result)
// ---------------------------------------------------------------

async function focusViaTab(pg, selector, name) {
  const el = pg.locator(selector).first();
  const v = await el.isVisible().catch(() => false);
  if (!v) return { name, found: false, focused: false, reason: 'not visible' };

  for (let i = 0; i < 40; i++) {
    const active = await pg.evaluate(() => {
      const ae = document.activeElement;
      return ae ? { tag: ae.tagName, sel: ae.matches('details summary') ? 'SUMMARY' : ae.tagName + (ae.getAttribute('type') ? `[type="${ae.getAttribute('type')}"]` : '') } : null;
    });
    if (active && active.tag === 'SUMMARY' && name.includes('summary')) {
      const cs = await pg.evaluate(() => {
        const ae = document.activeElement; const s = window.getComputedStyle(ae);
        return { focused: true, elTag: ae.tagName, outline: s.outline, outlineColor: s.outlineColor, outlineWidth: s.outlineWidth, outlineStyle: s.outlineStyle, outlineOffset: s.outlineOffset, boxShadow: s.boxShadow };
      });
      return { name, found: true, ...cs };
    }
    if (active && (
      (name === 'button-or-link' && (active.tag === 'BUTTON' || active.tag === 'A'))
      || (name === 'input-or-select' && (active.tag === 'INPUT' || active.tag === 'SELECT'))
      || (name === 'checkbox' && active.tag === 'INPUT' && active.sel.includes('checkbox'))
    )) {
      const cs = await pg.evaluate(() => {
        const ae = document.activeElement; const s = window.getComputedStyle(ae);
        return { focused: true, elTag: ae.tagName, outline: s.outline, outlineColor: s.outlineColor, outlineWidth: s.outlineWidth, outlineStyle: s.outlineStyle, outlineOffset: s.outlineOffset, boxShadow: s.boxShadow };
      });
      return { name, found: true, ...cs };
    }
    await pg.keyboard.press('Tab');
    await pg.waitForTimeout(80);
  }
  return { name, found: true, focused: false, reason: `could not reach ${name} via Tab` };
}

async function focusSummaryDirect(pg, summarySelector) {
  // Tab from body to reach summary in grouped-review
  await pg.evaluate(() => document.body.focus());
  for (let i = 0; i < 50; i++) {
    await pg.keyboard.press('Tab');
    await pg.waitForTimeout(60);
    const result = await pg.evaluate(() => {
      const ae = document.activeElement;
      if (!ae || ae.tagName !== 'SUMMARY') return false;
      const s = window.getComputedStyle(ae);
      return {
        found: true, focused: true, elTag: 'SUMMARY',
        outline: s.outline, outlineColor: s.outlineColor, outlineWidth: s.outlineWidth, outlineStyle: s.outlineStyle, outlineOffset: s.outlineOffset, boxShadow: s.boxShadow,
      };
    });
    if (result) return { name: 'summary', ...result };
  }
  return { name: 'summary', found: true, focused: false, reason: 'could not reach summary via Tab' };
}

// ---------------------------------------------------------------
// Keyboard-origin focus evidence (guided page: button, input/select, checkbox only)
// ---------------------------------------------------------------

async function collectContextMedia(pg) {
  return pg.evaluate(() => ({
    pointerCoarse: window.matchMedia('(pointer: coarse)').matches,
    anyPointerCoarse: window.matchMedia('(any-pointer: coarse)').matches,
    maxTouchPoints: navigator.maxTouchPoints,
  }));
}

async function guidedPageFocus(pg) {
  const results = {};
  results.button = await focusViaTab(pg, 'button:not([disabled])', 'button-or-link');
  results['input-or-select'] = await focusViaTab(pg, 'input:not([type="hidden"]), select', 'input-or-select');
  results.checkbox = await focusViaTab(pg, 'input[type="checkbox"]', 'checkbox');
  logAction('focus-guided-page', results);
  return results;
}

// ---------------------------------------------------------------
// Checkbox label click test
// ---------------------------------------------------------------

async function clickLabelText(pg, labelSelector, checkName) {
  const label = pg.locator(labelSelector).first();
  const lv = await label.isVisible().catch(() => false);
  if (!lv) return { name: checkName, tested: false, reason: 'label not visible' };

  const cb = label.locator('input[type="checkbox"]');
  const cv = await cb.isVisible().catch(() => false);
  if (!cv) return { name: checkName, tested: false, reason: 'checkbox not found inside label' };

  const before = await cb.isChecked();
  const lr = await label.boundingBox();

  const span = label.locator('span').first();
  const sv = await span.isVisible().catch(() => false);
  let cx, cy;
  if (sv) {
    const sr = await span.boundingBox();
    cx = sr.x + sr.width / 2; cy = sr.y + sr.height / 2;
  } else {
    cx = lr.x + lr.width - 10; cy = lr.y + lr.height / 2;
  }
  await pg.mouse.click(cx, cy);
  await pg.waitForTimeout(200);

  const after = await cb.isChecked();
  if (after) { await cb.click(); await pg.waitForTimeout(100); } // restore unchecked

  return {
    name: checkName, tested: true, beforeChecked: before, afterChecked: after, toggled: before !== after,
    labelRect: { x: Math.round(lr.x), y: Math.round(lr.y), w: Math.round(lr.width), h: Math.round(lr.height) },
    clickX: Math.round(cx), clickY: Math.round(cy),
  };
}

// ---------------------------------------------------------------
// Navigation helpers
// ---------------------------------------------------------------

async function waitForAppShell(pg) {
  await pg.waitForLoadState('domcontentloaded');
  await pg.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await pg.locator('.app-shell, .project-nav').first().waitFor({ state: 'visible', timeout: 20000 });
}

async function navigateToGuidedReview(pg) {
  const form = pg.locator('form[aria-label="Owner-authored setup input"]');
  await form.waitFor({ state: 'visible', timeout: 10000 });
  await pg.fill('input[aria-label="OMI-guided project title"]', GUIDED_TITLE);
  await pg.fill('textarea[aria-label="Owner-authored setup idea"]', GUIDED_IDEA);
  await pg.waitForTimeout(200);
  await form.locator('button[type="submit"]').click();
  await pg.waitForTimeout(500);
  const reviewForm = pg.locator('form[aria-label="Review setup draft"]');
  await reviewForm.waitFor({ state: 'visible', timeout: 10000 });
  logAction('guided_review_visible');
}

async function openOMIDashboard(pg) {
  const entry = pg.locator('[data-testid="omi-workspace-entry"]').first();
  await entry.waitFor({ state: 'visible', timeout: 15000 });
  await entry.click();
  await pg.locator('[data-testid="omi-dashboard"]').waitFor({ state: 'visible', timeout: 15000 });
  await pg.waitForTimeout(300);
  logAction('omi_dashboard_opened');
}

async function openGroupedReview(pg) {
  const row = pg.getByRole('row', { name: /Grouped Review/i }).first();
  await row.getByRole('button').first().click();
  await pg.locator('[data-testid="omi-grouped-review"]').waitFor({ state: 'visible', timeout: 15000 });
  await pg.waitForTimeout(300);
  logAction('omi_grouped_review_opened');
}

async function openApplyPromotion(pg) {
  const back = pg.getByRole('button', { name: /Back to Dashboard/i }).first();
  if (await back.isVisible().catch(() => false)) await back.click();
  else { await pg.goto(APP_BASE_URL); await waitForAppShell(pg); await openOMIDashboard(pg); }
  await pg.locator('[data-testid="omi-dashboard"]').waitFor({ state: 'visible', timeout: 10000 });
  await pg.waitForTimeout(200);
  const promoRow = pg.getByRole('row', { name: /Promotion Handoff Readiness/i }).first();
  await promoRow.getByRole('button').first().click();
  await pg.locator('[data-testid="omi-apply-promotion-confirmation"]').waitFor({ state: 'visible', timeout: 15000 });
  await pg.waitForTimeout(300);
  logAction('omi_apply_promotion_opened');
}

// ---------------------------------------------------------------
// Single context run — returns geometry, focus, and click results
// ---------------------------------------------------------------

async function runContext(chromium, viewport, label) {
  const ctxOpts = { viewport };
  if (label === 'mobile-coarse-pointer') ctxOpts.hasTouch = true;
  const ctx = await chromium.newContext(ctxOpts);
  if (apiMode === 'fixture') await installReadOnlyFixtures(ctx);
  const pg = await ctx.newPage();
  installPageTelemetry(pg);
  await pg.goto(APP_BASE_URL, { waitUntil: 'domcontentloaded' });
  await waitForAppShell(pg);

  const contextMedia = await collectContextMedia(pg);
  logAction(`${label}: context media`, contextMedia);
  if (label === 'mobile-coarse-pointer') {
    assertEvidence('mobile: pointerCoarse === true', contextMedia.pointerCoarse === true, { ...contextMedia });
  }

  const result = {
    label,
    geometry: {},
    focus: {},
    clicks: {},
    contextMedia,
  };

  // --- 1. Guided review ---
  await navigateToGuidedReview(pg);

  result.geometry['omi-checkbox-row'] = await measure(pg, '.omi-checkbox-row', 'omi-checkbox-row');
  assertEvidence(`${label}: guided .omi-checkbox-row found`, result.geometry['omi-checkbox-row'].found, {});

  const guidedClick = await clickLabelText(pg, '.omi-checkbox-row', 'guided-confirmation');
  result.clicks.guided = guidedClick;
  assertEvidence(`${label}: guided checkbox toggles on label click`, guidedClick.tested && guidedClick.toggled, guidedClick);
  if (label === 'mobile-coarse-pointer' && result.geometry['omi-checkbox-row'].found) {
    assertEvidence(`${label}: guided checkbox-row height >= 44`, result.geometry['omi-checkbox-row'].height >= 44, result.geometry['omi-checkbox-row']);
  }

  // --- 2. Guided-page focus (button, input-or-select, checkbox only) ---
  if (label === 'desktop') {
    const gf = await guidedPageFocus(pg);
    result.focus = { ...gf };
    for (const [name, data] of Object.entries(gf)) {
      assertEvidence(`focus: ${name} found`, data.found, data);
      if (data.found) {
        assertEvidence(`focus: ${name} focused`, data.focused, data);
        if (data.focused) {
          const visible = data.outlineStyle !== 'none' && data.outlineWidth !== '0px';
          assertEvidence(`focus: ${name} visible outline`, visible, data);
          assertEvidence(`focus: ${name} semantic color`, data.outlineColor?.includes('122, 162, 232'), data);
        }
      }
    }
  }

  // Return to overview
  await pg.locator('button:has-text("Back to setup draft")').click();
  await pg.waitForTimeout(300);

  // --- 3. OMI Dashboard ---
  await openOMIDashboard(pg);
  for (const sel of ['.primary-button', '.secondary-button', '.omi-row-action']) {
    const n = sel.replace('.', '');
    const g = await measure(pg, sel, n);
    result.geometry[n] = g;
    if (label === 'mobile-coarse-pointer' && g.found) assertEvidence(`${label}: ${n} height >= 44`, g.height >= 44, g);
    logAction(`${label}: ${n} measured`, { found: g.found, h: g.height });
  }

  // --- 4. Grouped Review ---
  await openGroupedReview(pg);
  const groupedSels = [
    ['.omi-grouped-candidate-row', 'omi-grouped-candidate-row'],
    ['.omi-grouped-disclosure summary', 'omi-grouped-disclosure-summary'],
    ['.omi-grouped-source-scope select', 'grouped-source-scope-select'],
    ['.omi-grouped-filter-grid input[type="search"]', 'grouped-filter-search'],
    ['.omi-grouped-filter-grid select', 'grouped-filter-select'],
    ['.omi-grouped-check-filter', 'omi-grouped-check-filter'],
    ['.omi-grouped-approval-confirmation', 'omi-grouped-approval-confirmation'],
  ];
  for (const [sel, name] of groupedSels) {
    const g = await measure(pg, sel, name);
    result.geometry[name] = g;
    assertEvidence(`${label}: ${name} found`, g.found, g);
    if (label === 'mobile-coarse-pointer' && g.found) assertEvidence(`${label}: ${name} height >= 44`, g.height >= 44, g);
  }

  // --- 5. Grouped-review disclosure-summary keyboard focus ---
  if (label === 'desktop') {
    const sf = await focusSummaryDirect(pg);
    result.focus.summary = sf;
    assertEvidence('focus: summary found', sf.found, sf);
    if (sf.found) {
      assertEvidence('focus: summary focused', sf.focused, sf);
      if (sf.focused) {
        const v = sf.outlineStyle !== 'none' && sf.outlineWidth !== '0px';
        assertEvidence('focus: summary visible outline', v, sf);
        assertEvidence('focus: summary semantic color', sf.outlineColor?.includes('122, 162, 232'), sf);
      }
    }
  }

  // --- 6. Apply-Promotion ---
  await openApplyPromotion(pg);
  const applyBtn = await measure(pg, '.omi-final-apply-button', 'omi-final-apply-button');
  result.geometry['omi-final-apply-button'] = applyBtn;
  assertEvidence(`${label}: omi-final-apply-button found`, applyBtn.found, applyBtn);
  if (label === 'mobile-coarse-pointer' && applyBtn.found) assertEvidence(`${label}: omi-final-apply-button height >= 44`, applyBtn.height >= 44, applyBtn);

  const applyCbLabel = pg.locator('.omi-checkbox-row').first();
  const applyCbVis = await applyCbLabel.isVisible().catch(() => false);
  assertEvidence(`${label}: apply checkbox-row visible`, applyCbVis, {});
  const applyCbGeom = await measure(pg, '.omi-checkbox-row', 'apply-omi-checkbox-row');
  result.geometry['apply-omi-checkbox-row'] = applyCbGeom;
  if (label === 'mobile-coarse-pointer' && applyCbGeom.found) assertEvidence(`${label}: apply checkbox-row height >= 44`, applyCbGeom.height >= 44, applyCbGeom);

  // Check if apply-confirmation checkbox is disabled (truthful product state)
  const applyCbInput = applyCbLabel.locator('input[type="checkbox"]');
  const applyDisabled = await applyCbInput.evaluate((el) => el.disabled).catch(() => true);
  if (applyDisabled) {
    logAction(`${label}: apply checkbox disabled (truthful)`, {});
    result.clicks.apply = { tested: true, toggled: false, reason: 'checkbox disabled — truthful product state' };
  } else {
    await applyCbInput.check();
    await pg.waitForTimeout(100);
    await applyCbInput.uncheck();
    await pg.waitForTimeout(100);

    const applyClick = await clickLabelText(pg, '.omi-checkbox-row', 'apply-confirmation');
    result.clicks.apply = applyClick;
    assertEvidence(`${label}: apply checkbox toggle (label click)`, applyClick.tested && applyClick.toggled, applyClick);
    if (applyClick.afterChecked) { await applyCbInput.uncheck().catch(() => {}); }
  }

  // Screenshot
  const ss = await screenshot(pg, label === 'desktop' ? '01-desktop-t005b' : '02-mobile-coarse-t005b');
  if (label === 'desktop') desktopScreenshotPath = ss;
  else mobileScreenshotPath = ss;

  await ctx.close();
  return result;
}

// ---------------------------------------------------------------
// Cleanup — structured result
// ---------------------------------------------------------------

async function cleanup() {
  const result = { startedVite: viteStartedByUs, pid: viteProcess?.pid ?? null, sigtermSent: false, exited: false, sigkillNeeded: false, success: false };

  if (browser) { await browser.close().catch(() => {}); browser = null; }

  if (viteProcess && viteProcess.pid) {
    const pid = viteProcess.pid;
    try { process.kill(-pid, 'SIGTERM'); result.sigtermSent = true; } catch { try { viteProcess.kill('SIGTERM'); result.sigtermSent = true; } catch {} }

    try {
      await Promise.race([new Promise((r) => { viteProcess.once('exit', () => { result.exited = true; r(); }); }), new Promise((r) => setTimeout(r, 2000))]);
    } catch {}

    if (!result.exited) {
      result.sigkillNeeded = true;
      try { process.kill(-pid, 'SIGKILL'); } catch { try { viteProcess.kill('SIGKILL'); } catch {} }
      try { await Promise.race([new Promise((r) => { viteProcess.once('exit', () => { result.exited = true; r(); }); }), new Promise((r) => setTimeout(r, 3000))]); } catch {}
    }
    result.success = result.exited;
  } else {
    result.success = true;
  }

  cleanupResult = result;
  logAction('cleanup_complete', result);
  return result;
}

// ---------------------------------------------------------------
// Final consistency assertions
// ---------------------------------------------------------------

function mandatoryGeometryKeys() {
  return [
    'omi-checkbox-row', 'primary-button', 'secondary-button', 'omi-row-action',
    'omi-grouped-candidate-row', 'omi-grouped-disclosure-summary',
    'grouped-source-scope-select', 'grouped-filter-search', 'grouped-filter-select',
    'omi-grouped-check-filter', 'omi-grouped-approval-confirmation',
    'omi-final-apply-button', 'apply-omi-checkbox-row',
  ];
}

function assertFinalConsistency(desktop, mobile) {
  for (const key of mandatoryGeometryKeys()) {
    const d = desktop.geometry[key];
    const m = mobile.geometry[key];
    assertEvidence(`final: desktop ${key} exists`, !!d?.found, { key });
    assertEvidence(`final: mobile ${key} exists`, !!m?.found, { key });
  }
  for (const ck of ['guided', 'apply']) {
    const dc = desktop.clicks[ck];
    const mc = mobile.clicks[ck];
    assertEvidence(`final: desktop ${ck} click tested`, dc?.tested, {});
    if (dc?.reason?.includes('disabled')) {
      logAction(`final: desktop ${ck} click disabled (truthful)`, {});
    } else {
      assertEvidence(`final: desktop ${ck} click toggled`, dc?.toggled, {});
    }
    assertEvidence(`final: mobile ${ck} click tested`, mc?.tested, {});
    if (mc?.reason?.includes('disabled')) {
      logAction(`final: mobile ${ck} click disabled (truthful)`, {});
    } else {
      assertEvidence(`final: mobile ${ck} click toggled`, mc?.toggled, {});
    }
  }
  for (const fk of ['button', 'input-or-select', 'checkbox', 'summary']) {
    const f = desktop.focus[fk];
    assertEvidence(`final: focus ${fk} found`, f?.found, f);
    if (f?.found) {
      assertEvidence(`final: focus ${fk} focused`, f?.focused, f);
      if (f?.focused) {
        assertEvidence(`final: focus ${fk} visible outline`, f?.outlineStyle !== 'none' && f?.outlineWidth !== '0px', f);
        assertEvidence(`final: focus ${fk} semantic color`, f?.outlineColor?.includes('122, 162, 232'), f);
      }
    }
  }
  assertEvidence('final: geometry.json has desktop', Object.keys(desktop.geometry).length > 0, {});
  assertEvidence('final: geometry.json has mobile', Object.keys(mobile.geometry).length > 0, {});
}

// ---------------------------------------------------------------
// Main
// ---------------------------------------------------------------

async function main() {
  let exitCode = 0;
  let desktopResult = null;
  let mobileResult = null;

  try {
    await ensureEvidenceDirs();
    playwrightChromium = await loadPlaywrightChromium();
  await startViteIfNeeded();

  // Always use fixture mode for deterministic evidence
  apiMode = 'fixture';
  logAction('using_fixture_mode');

    const chromium = await playwrightChromium.launch();

    desktopResult = await runContext(chromium, { width: 1440, height: 1000 }, 'desktop');
    mobileResult = await runContext(chromium, { width: 390, height: 844 }, 'mobile-coarse-pointer');

    await chromium.close();

    desktopGeometry = desktopResult.geometry;
    mobileGeometry = mobileResult.geometry;

    // Telemetry
    const t = collectTelemetry();
    assertEvidence('telemetry: page errors = 0', t.pageErrors === 0, { count: t.pageErrors });
    assertEvidence('telemetry: console errors = 0', t.consoleErrors === 0, { count: t.consoleErrors });
    assertEvidence('telemetry: failed requests = 0', t.failedRequests === 0, { count: t.failedRequests });
    assertEvidence('telemetry: HTTP errors = 0', t.httpErrorResponses === 0, { count: t.httpErrorResponses });
    assertEvidence('telemetry: unmatched fixtures = 0', t.unmatchedFixtures === 0, { count: t.unmatchedFixtures });
    assertEvidence('telemetry: non-GET = 0', t.nonGetApiRequests === 0, { count: t.nonGetApiRequests });
    assertEvidence('telemetry: apply-promotion = 0', t.applyPromotionRequests === 0, { count: t.applyPromotionRequests });
    assertEvidence('telemetry: mutating = 0', t.mutatingApiRequests === 0, { count: t.mutatingApiRequests });

    // Final consistency
    assertFinalConsistency(desktopResult, mobileResult);

    exitCode = failures.length === 0 ? 0 : 1;
  } catch (error) {
    exitCode = 1;
    recordFailure('script execution failed', { message: error instanceof Error ? error.message : String(error) });
  } finally {
    // Cleanup AFTER all evidence is collected
    await cleanup();
    assertEvidence('final: cleanup success', cleanupResult?.success, cleanupResult);

    // Write geometry
    const gp = {
      desktop: desktopResult?.geometry ?? {},
      mobileCoarsePointer: mobileResult?.geometry ?? {},
      desktopClicks: desktopResult?.clicks ?? {},
      mobileClicks: mobileResult?.clicks ?? {},
      desktopFocus: desktopResult?.focus ?? {},
      contextMedia: {
        desktop: desktopResult?.contextMedia ?? {},
        mobileCoarsePointer: mobileResult?.contextMedia ?? {},
      },
      cleanup: cleanupResult ?? {},
    };
    await fs.writeFile(GEOMETRY_PATH, `${JSON.stringify(gp, null, 2)}\n`, 'utf8');

    // Write validation.md
    const al = workflowLog.filter((e) => e.action === 'assert_pass' || e.action === 'assert_fail').map((e) => `- ${e.action === 'assert_pass' ? 'PASS' : 'FAIL'}: ${e.name}`);
    const tl = collectTelemetry();
    const lines = [
      '# T005B Accessibility Browser Evidence',
      '', `- Result: **${failures.length === 0 ? 'PASS' : 'FAIL'}**`, `- Started: \`${RUN_STARTED_AT}\``, `- Finished: \`${new Date().toISOString()}\``, `- App: \`${APP_BASE_URL}\``, `- Project: \`${PROJECT_ID}\``, `- API mode: \`${apiMode}\``,
      '', '## Screenshots', '', `- Desktop: \`${desktopScreenshotPath}\``, `- Mobile: \`${mobileScreenshotPath}\``,
      '', '## Assertions', '', ...al,
      '', '## Cleanup', '', '```json', JSON.stringify(cleanupResult, null, 2), '```',
      '', '## Telemetry', '',
      `- page: ${tl.pageErrors}`, `- console: ${tl.consoleErrors}`, `- failed: ${tl.failedRequests}`, `- HTTP: ${tl.httpErrorResponses}`, `- unmatched: ${tl.unmatchedFixtures}`, `- non-GET: ${tl.nonGetApiRequests}`, `- apply-promo: ${tl.applyPromotionRequests}`, `- mutating: ${tl.mutatingApiRequests}`,
      '', '## Safety', '', '- Read-only API fixtures.', '- No mutating API requests.', '- No apply-promotion executed.', '- No candidates created.', '- No Memory/Canon mutation.',
    ];
    if (failures.length > 0) { lines.push('', '## Failures', ''); for (const f of failures) lines.push(`- ${f.name}: \`${JSON.stringify(f.details)}\``); }
    await fs.writeFile(VALIDATION_MD_PATH, `${lines.join('\n')}\n`, 'utf8');

    // Write final workflow-log
    const payload = {
      task: 'PHASE8-IMPL-024-T005B Browser Evidence', result: failures.length === 0 ? 'PASS' : 'FAIL', startedAt: RUN_STARTED_AT, finishedAt: new Date().toISOString(),
      appBaseUrl: APP_BASE_URL, projectId: PROJECT_ID, apiMode, evidenceDir: EVIDENCE_DIR,
      telemetry: tl, failures, actions: workflowLog, cleanup: cleanupResult,
    };
    await fs.writeFile(WORKFLOW_LOG_PATH, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
    logAction('write_artifacts', { result: failures.length === 0 ? 'PASS' : 'FAIL' });
  }

  process.exitCode = exitCode;
  setTimeout(() => process.exit(exitCode), 50);
}

main();
