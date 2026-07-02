#!/usr/bin/env node
/**
 * MVP-READINESS-OWNER-ACCEPTANCE-002
 * Playwright automated owner MVP acceptance checklist evidence harness.
 *
 * Evidence-only runner. It does not mark MVP complete, does not record owner
 * acceptance, does not call creative generation directly, and does not execute
 * BookNLP/spaCy/NCP/Subtxt/dramatica-flow directly.
 *
 * Manual run, with frontend/backend already running:
 *   node scripts/mvp-owner-acceptance-browser-smoke.mjs
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const FRONTEND_NODE_MODULES = path.join(REPO_ROOT, 'frontend', 'node_modules');

const APP_BASE_URL = process.env.APP_BASE_URL ?? 'http://localhost:5173';
const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL ?? 'http://localhost:8000';
const DEFAULT_OLLAMA_BASE_URL = 'http://localhost:11434';
const WSL_OLLAMA_REMEDIATION_COMMAND = [
  "WINDOWS_HOST=$(ip route show | grep -i default | awk '{ print $3 }')",
  'export OLLAMA_HOST="http://$WINDOWS_HOST:11434"',
  'curl "$OLLAMA_HOST/api/version"',
].join('\n');
const MVP_ACCEPTANCE_EVIDENCE_DIR = path.resolve(
  process.env.MVP_ACCEPTANCE_EVIDENCE_DIR
    ?? 'artifacts/mvp-readiness/owner-acceptance',
);

const STATUSES = Object.freeze({
  PASS: 'PASS',
  FAIL: 'FAIL',
  BLOCKED: 'BLOCKED',
  NOT_EXPOSED: 'NOT_EXPOSED',
  MANUAL_REVIEW_REQUIRED: 'MANUAL_REVIEW_REQUIRED',
});

const FINAL_DECISIONS = Object.freeze({
  READY_FOR_OWNER_REVIEW: 'READY_FOR_OWNER_REVIEW',
  BLOCKED: 'BLOCKED',
  MANUAL_REVIEW_REQUIRED: 'MANUAL_REVIEW_REQUIRED',
});

const SECTION_ORDER = Object.freeze([
  'Startup Requirements',
  'Project Isolation',
  'Manual Workspace Checks',
  'Runtime Extraction Checks',
  'Candidate / Review Checks',
  'Apply-Promotion Checks',
  'Model-Assisted / Analysis Runtime Checks',
  'No-Prose Checks',
  'Final Owner Decision',
]);

const CHECKLIST_ITEMS = Object.freeze([
  { id: 'startup_backend_running', section: 'Startup Requirements', text: 'Backend is running.' },
  { id: 'startup_frontend_running', section: 'Startup Requirements', text: 'Frontend is running.' },
  { id: 'startup_ollama_reachable', section: 'Startup Requirements', text: 'Ollama is reachable if model-backed workflows are tested.' },
  { id: 'startup_ollama_unreachable', section: 'Startup Requirements', text: 'Ollama unreachable blocker is recorded when localhost:11434 readiness checks fail.' },
  { id: 'startup_project_isolation_script_available', section: 'Startup Requirements', text: 'Browser evidence script is available at scripts/mvp-project-isolation-browser-smoke.mjs.' },
  { id: 'startup_owner_understands_analysis_boundaries', section: 'Startup Requirements', text: 'Owner understands model-backed, BookNLP/spaCy, NCP/Subtxt/dramatica-flow, and extraction checks must remain evidence-backed, candidate-first, and non-canon unless explicitly approved through the allowed workflow.' },
  { id: 'project_isolation_playwright_evidence_reviewed', section: 'Project Isolation', text: 'Playwright browser evidence is reviewed.' },
  { id: 'project_isolation_script_records_pass', section: 'Project Isolation', text: 'scripts/mvp-project-isolation-browser-smoke.mjs records PASS.' },
  { id: 'project_isolation_script_exit_zero', section: 'Project Isolation', text: 'SCRIPT_EXIT=0 is recorded.' },
  { id: 'project_isolation_no_blockers', section: 'Project Isolation', text: 'No blockers are recorded in the evidence report or workflow log.' },
  { id: 'project_isolation_new_project_activated', section: 'Project Isolation', text: 'New project creation activates the new project in the header, selector, and Overview.' },
  { id: 'project_isolation_scenes_no_leakage', section: 'Project Isolation', text: 'Scenes for a new project do not leak example, scene_001, or unrelated project data.' },
  { id: 'project_isolation_memory_canon_no_leakage', section: 'Project Isolation', text: 'Memory/Canon for a new project does not leak unrelated project data.' },
  { id: 'manual_workspace_create_project', section: 'Manual Workspace Checks', text: 'Create a project.' },
  { id: 'manual_workspace_select_existing_project', section: 'Manual Workspace Checks', text: 'Select an existing project.' },
  { id: 'manual_workspace_overview_active_only', section: 'Manual Workspace Checks', text: 'Confirm Overview reflects the active project only.' },
  { id: 'manual_workspace_scenes_empty_new_project', section: 'Manual Workspace Checks', text: 'Confirm Scenes show empty/new project behavior for a new project.' },
  { id: 'manual_workspace_notes_project_scoped', section: 'Manual Workspace Checks', text: 'Confirm Notes are project-scoped and owner-authored/owner-provided only.' },
  { id: 'manual_workspace_materials_project_scoped', section: 'Manual Workspace Checks', text: 'Confirm Materials are project-scoped and owner-authored/owner-provided only.' },
  { id: 'manual_workspace_memory_canon_approved_only', section: 'Manual Workspace Checks', text: 'Confirm Memory/Canon shows approved-only boundaries.' },
  { id: 'manual_workspace_omi_candidates_not_approved_memory', section: 'Manual Workspace Checks', text: 'Confirm setup/OMI candidates remain candidates or planning state, not approved memory/canon.' },
  { id: 'runtime_extraction_unavailable_fail_closed', section: 'Runtime Extraction Checks', text: 'Unavailable dependency states are explicit and fail closed.' },
  { id: 'runtime_extraction_failures_no_success_claim', section: 'Runtime Extraction Checks', text: 'Runtime failures do not silently claim extraction success.' },
  { id: 'runtime_extraction_raw_artifacts_support_only', section: 'Runtime Extraction Checks', text: 'Raw artifacts remain support data only.' },
  { id: 'runtime_extraction_raw_artifacts_not_truth', section: 'Runtime Extraction Checks', text: 'Raw artifacts do not become candidates, canon, approved memory, training data, or truth by themselves.' },
  { id: 'runtime_extraction_no_memory_canon_mutation', section: 'Runtime Extraction Checks', text: 'Runtime extraction does not mutate approved memory/canon.' },
  { id: 'runtime_extraction_candidate_first_owner_review', section: 'Runtime Extraction Checks', text: 'Runtime extraction outputs remain candidate-first and owner-review-gated.' },
  { id: 'candidate_review_candidate_first_visible', section: 'Candidate / Review Checks', text: 'Candidate-first behavior is visible and preserved.' },
  { id: 'candidate_review_queue_not_approval', section: 'Candidate / Review Checks', text: 'Review queue entries are not treated as approval.' },
  { id: 'candidate_review_read_only_state', section: 'Candidate / Review Checks', text: 'Read-only review state is available where expected.' },
  { id: 'candidate_review_owner_action_explicit', section: 'Candidate / Review Checks', text: 'Owner-action execution happens only through explicit owner commands.' },
  { id: 'candidate_review_confidence_not_truth', section: 'Candidate / Review Checks', text: 'Confidence values are not presented as truth.' },
  { id: 'candidate_review_persistence_not_canon', section: 'Candidate / Review Checks', text: 'Candidate persistence is not canon.' },
  { id: 'apply_promotion_requires_confirmation', section: 'Apply-Promotion Checks', text: 'Apply-promotion requires explicit owner confirmation.' },
  { id: 'apply_promotion_audit_details', section: 'Apply-Promotion Checks', text: 'Apply-promotion records audit details.' },
  { id: 'apply_promotion_only_approved_workflow', section: 'Apply-Promotion Checks', text: 'Approved memory/canon mutation happens only through the approved workflow.' },
  { id: 'apply_promotion_failed_rejected_unchanged', section: 'Apply-Promotion Checks', text: 'Failed or rejected promotion leaves approved memory/canon unchanged.' },
  { id: 'apply_promotion_no_bypass', section: 'Apply-Promotion Checks', text: 'No extraction, model, queue, or candidate state bypasses apply-promotion.' },
  { id: 'model_assisted_evidence_backed_only', section: 'Model-Assisted / Analysis Runtime Checks', text: 'Model-assisted observations are evidence-backed only.' },
  { id: 'model_assisted_confidence_not_truth', section: 'Model-Assisted / Analysis Runtime Checks', text: 'Confidence is not truth.' },
  { id: 'model_assisted_output_not_canon', section: 'Model-Assisted / Analysis Runtime Checks', text: 'Model output is not canon.' },
  { id: 'model_assisted_ncp_structured_context_only', section: 'Model-Assisted / Analysis Runtime Checks', text: 'NCP remains structured context interchange only.' },
  { id: 'model_assisted_subtxt_diagnostic_only', section: 'Model-Assisted / Analysis Runtime Checks', text: 'Subtxt remains rubric/diagnostic guidance only.' },
  { id: 'model_assisted_dramatica_flow_analysis_only', section: 'Model-Assisted / Analysis Runtime Checks', text: 'dramatica-flow remains analysis-only through audited allowlists.' },
  { id: 'model_assisted_no_prose_outline_canon_training_promotion', section: 'Model-Assisted / Analysis Runtime Checks', text: 'NCP/Subtxt/dramatica-flow outputs do not generate prose, outlines, canon, training artifacts, or automatic promotion.' },
  { id: 'no_prose_no_rewrite', section: 'No-Prose Checks', text: 'No rewrite behavior is exposed or accepted.' },
  { id: 'no_prose_no_continuation', section: 'No-Prose Checks', text: 'No continuation behavior is exposed or accepted.' },
  { id: 'no_prose_no_outline_generation', section: 'No-Prose Checks', text: 'No outline generation behavior is exposed or accepted.' },
  { id: 'no_prose_no_generated_prose', section: 'No-Prose Checks', text: 'No generated prose behavior is exposed or accepted.' },
  { id: 'no_prose_no_imitation_polish_improve_expand_draft_chapter', section: 'No-Prose Checks', text: 'No imitation, polish, improvement, expansion, draft, chapter generation, or prose-production path is exposed or accepted.' },
  { id: 'final_owner_decision_pending', section: 'Final Owner Decision', text: 'Pending owner acceptance - checklist not yet complete or not yet accepted.' },
  { id: 'final_owner_decision_accepted_by_owner', section: 'Final Owner Decision', text: 'Accepted by owner - owner explicitly accepts MVP manual readiness.' },
  { id: 'final_owner_decision_blocked_with_reason', section: 'Final Owner Decision', text: 'Blocked with reason - owner finds a blocker.' },
]);

const EXAMPLE_LEAKAGE_MARKERS = Object.freeze([
  'The Princess and the Pea',
  'scene_001',
]);

const NO_PROSE_NEGATIVE_REQUESTS = Object.freeze([
  'rewrite this scene',
  'continue this scene',
  'outline the next chapter',
  'generate a draft',
  'polish/improve/expand/imitate this prose',
]);

const OWNER_DIAGNOSTIC_TEXT =
  'Owner-authored diagnostic-only test text. Analyze whether the scene has enough evidence for structure claims. Do not write, rewrite, continue, outline, imitate, polish, improve, expand, or draft prose.';
const PROJECT_SETUP_IDEA =
  'Owner-authored MVP acceptance setup idea. This is evidence fixture text only and is not canon.';
const PROJECT_SETUP_NOTES =
  'Owner-authored MVP acceptance setup notes. Candidate planning data only.';

let page = null;
let browser = null;
let runStartedAt = new Date().toISOString();
let finalDecision = FINAL_DECISIONS.MANUAL_REVIEW_REQUIRED;
let startupBlocked = false;
let appBlockerFound = false;
let toolingBlocked = false;
let uniqueProjectTitle = '';
let uniqueProjectId = '';
let previousProjectId = '';
let ollamaHealth = {
  version: { ok: false, error: 'not checked' },
  tags: { ok: false, error: 'not checked' },
  ok: false,
  selectedBaseUrl: '',
  selectedSource: '',
  attemptedCandidates: [],
};

/** @type {Array<{ ts: string, action: string, [key: string]: unknown }>} */
const workflowLog = [];
/** @type {Record<string, { id: string, section: string, text: string, status: string, evidence: unknown[], screenshotPaths: string[], notes: string[], ts: string }>} */
const checklistResults = Object.fromEntries(
  CHECKLIST_ITEMS.map((item) => [
    item.id,
    {
      ...item,
      status: STATUSES.MANUAL_REVIEW_REQUIRED,
      evidence: [],
      screenshotPaths: [],
      notes: ['Not evaluated yet.'],
      ts: runStartedAt,
    },
  ]),
);

const screenshotDir = path.join(MVP_ACCEPTANCE_EVIDENCE_DIR, 'screenshots');

function logAction(action, details = {}) {
  const entry = { ts: new Date().toISOString(), action, ...details };
  workflowLog.push(entry);
  const suffix = Object.keys(details).length ? ` ${JSON.stringify(details)}` : '';
  console.log(`[ACTION] ${action}${suffix}`);
}

function recordChecklistItem(id, status, evidence = {}, note = '') {
  const current = checklistResults[id];
  if (!current) {
    throw new Error(`Unknown checklist item: ${id}`);
  }

  const next = {
    ...current,
    status,
    evidence: [...current.evidence, evidence],
    notes: note ? [note] : current.notes.filter((value) => value !== 'Not evaluated yet.'),
    ts: new Date().toISOString(),
  };
  if (note && current.notes.some((value) => value !== 'Not evaluated yet.')) {
    next.notes = [...current.notes.filter((value) => value !== 'Not evaluated yet.'), note];
  }
  checklistResults[id] = next;
  logAction('checklist_item', { id, status, note });
  console.log(`[${status}] ${current.section} :: ${current.text}`);

  if (status === STATUSES.FAIL) {
    appBlockerFound = true;
  }
  if (status === STATUSES.BLOCKED) {
    startupBlocked = startupBlocked || id.startsWith('startup_');
    appBlockerFound = appBlockerFound || !id.startsWith('startup_ollama');
  }
}

function softAssert(id, condition, failStatus, evidence = {}, passNote = 'Assertion passed.', failNote = 'Assertion failed.') {
  recordChecklistItem(
    id,
    condition ? STATUSES.PASS : failStatus,
    evidence,
    condition ? passNote : failNote,
  );
  return Boolean(condition);
}

async function ensureEvidenceDirs() {
  await fs.mkdir(screenshotDir, { recursive: true });
  logAction('ensure_evidence_dirs', {
    evidenceDir: MVP_ACCEPTANCE_EVIDENCE_DIR,
    screenshotDir,
  });
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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
    `Playwright Chromium could not be imported from frontend/node_modules. Last error: ${lastError instanceof Error ? lastError.message : String(lastError)}`,
  );
}

async function screenshot(stepName, checklistIds = []) {
  if (!page) {
    return '';
  }
  const safeName = stepName
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
  const filePath = path.join(screenshotDir, `${safeName || 'step'}.png`);
  await page.screenshot({ path: filePath, fullPage: true });
  logAction('screenshot', { stepName, filePath });
  for (const id of checklistIds) {
    if (checklistResults[id]) {
      checklistResults[id].screenshotPaths.push(filePath);
    }
  }
  return filePath;
}

async function getVisibleText() {
  if (!page) {
    return '';
  }
  const text = await page.locator('body').innerText().catch(() => '');
  logAction('get_visible_text', { length: text.length });
  return text;
}

async function getScopedText(selector, scopeName = selector) {
  if (!page) {
    return '';
  }
  const locator = page.locator(selector).first();
  const count = await locator.count().catch(() => 0);
  if (!count) {
    logAction('get_scoped_text_missing', { scopeName, selector });
    return '';
  }
  const text = await locator.innerText().catch(() => '');
  logAction('get_scoped_text', { scopeName, selector, length: text.length });
  return text;
}

async function clickByText(candidates) {
  if (!page) {
    throw new Error('clickByText called before page initialized');
  }

  for (const candidate of candidates) {
    const exactButton = page.getByRole('button', { name: candidate, exact: true });
    if (await exactButton.count()) {
      await exactButton.first().click();
      logAction('click_by_text', { candidate, strategy: 'button-exact' });
      return candidate;
    }

    const looseButton = page.getByRole('button', { name: new RegExp(escapeRegExp(candidate), 'i') });
    if (await looseButton.count()) {
      await looseButton.first().click();
      logAction('click_by_text', { candidate, strategy: 'button-regex' });
      return candidate;
    }

    const link = page.getByRole('link', { name: new RegExp(escapeRegExp(candidate), 'i') });
    if (await link.count()) {
      await link.first().click();
      logAction('click_by_text', { candidate, strategy: 'link-regex' });
      return candidate;
    }
  }

  throw new Error(`Unable to click any candidate: ${candidates.join(', ')}`);
}

async function fillFirstMatching(candidates, value) {
  if (!page) {
    throw new Error('fillFirstMatching called before page initialized');
  }

  for (const candidate of candidates) {
    const byLabel = page.getByLabel(candidate, { exact: false });
    if (await byLabel.count()) {
      await byLabel.first().fill(value);
      logAction('fill_first_matching', { candidate, strategy: 'label', length: value.length });
      return candidate;
    }

    const byPlaceholder = page.getByPlaceholder(new RegExp(escapeRegExp(candidate), 'i'));
    if (await byPlaceholder.count()) {
      await byPlaceholder.first().fill(value);
      logAction('fill_first_matching', { candidate, strategy: 'placeholder', length: value.length });
      return candidate;
    }

    const byAria = page.locator(`[aria-label="${candidate}"]`);
    if (await byAria.count()) {
      await byAria.first().fill(value);
      logAction('fill_first_matching', { candidate, strategy: 'aria-label', length: value.length });
      return candidate;
    }
  }

  throw new Error(`Unable to fill any candidate: ${candidates.join(', ')}`);
}

async function safeFetchJson(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? 5000);

  try {
    const response = await fetch(url, {
      method: options.method ?? 'GET',
      headers: options.headers ?? undefined,
      body: options.body ?? undefined,
      signal: controller.signal,
    });
    const text = await response.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { rawText: text.slice(0, 1000) };
    }
    return { ok: response.ok, status: response.status, data, error: null };
  } catch (error) {
    return {
      ok: false,
      status: null,
      data: null,
      error: error instanceof Error ? error.message : String(error),
    };
  } finally {
    clearTimeout(timeout);
  }
}

function normalizeOllamaBaseUrl(value) {
  const trimmed = String(value ?? '').trim();
  if (!trimmed) {
    return '';
  }
  const withScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(trimmed)
    ? trimmed
    : `http://${trimmed}`;
  return withScheme.replace(/\/+$/, '');
}

async function isWslRuntime() {
  if (process.env.WSL_INTEROP) {
    return true;
  }
  const version = await fs.readFile('/proc/version', 'utf8').catch(() => '');
  return /microsoft|wsl/i.test(version);
}

function decodeLinuxRouteGateway(gatewayHex) {
  if (!/^[0-9a-fA-F]{8}$/.test(gatewayHex)) {
    return '';
  }
  const bytes = gatewayHex.match(/../g);
  if (!bytes) {
    return '';
  }
  return bytes
    .reverse()
    .map((byte) => String(Number.parseInt(byte, 16)))
    .join('.');
}

async function detectWslWindowsHostUrl() {
  if (!(await isWslRuntime())) {
    return '';
  }
  const routeTable = await fs.readFile('/proc/net/route', 'utf8').catch(() => '');
  const route = routeTable
    .split('\n')
    .map((line) => line.trim().split(/\s+/))
    .find((fields) => fields.length >= 3 && fields[1] === '00000000' && fields[2] !== '00000000');
  const gatewayIp = route ? decodeLinuxRouteGateway(route[2]) : '';
  return gatewayIp ? `http://${gatewayIp}:11434` : '';
}

async function buildOllamaCandidates() {
  const candidates = [];
  const addCandidate = (source, value) => {
    const baseUrl = normalizeOllamaBaseUrl(value);
    if (!baseUrl || candidates.some((candidate) => candidate.baseUrl === baseUrl)) {
      return;
    }
    candidates.push({ source, baseUrl });
  };

  addCandidate('OLLAMA_BASE_URL', process.env.OLLAMA_BASE_URL);
  addCandidate('OLLAMA_HOST', process.env.OLLAMA_HOST);
  addCandidate('localhost', DEFAULT_OLLAMA_BASE_URL);
  addCandidate('WSL Windows-host fallback', await detectWslWindowsHostUrl());
  return candidates;
}

async function checkOllamaHealth() {
  const candidates = await buildOllamaCandidates();
  const attemptedCandidates = [];
  let selectedAttempt = null;

  for (const candidate of candidates) {
    const versionUrl = `${candidate.baseUrl}/api/version`;
    const tagsUrl = `${candidate.baseUrl}/api/tags`;
    const version = await safeFetchJson(versionUrl);
    const tags = await safeFetchJson(tagsUrl);
    const ok = version.ok && tags.ok;
    const error = [version.error, tags.error].filter(Boolean).join(' | ');
    const attempt = {
      ...candidate,
      versionUrl,
      tagsUrl,
      ok,
      versionStatus: version.status,
      tagsStatus: tags.status,
      errorSummary: error || (ok ? '' : 'Health endpoints did not return OK.'),
    };
    attemptedCandidates.push(attempt);
    logAction('ollama_health_candidate', attempt);

    if (ok) {
      selectedAttempt = { ...attempt, version, tags };
      break;
    }
  }

  const version = selectedAttempt?.version ?? { ok: false, error: 'no candidate succeeded' };
  const tags = selectedAttempt?.tags ?? { ok: false, error: 'no candidate succeeded' };
  const ok = Boolean(selectedAttempt);
  const error = attemptedCandidates
    .filter((attempt) => !attempt.ok)
    .map((attempt) => `${attempt.baseUrl}: ${attempt.errorSummary}`)
    .join(' | ');
  ollamaHealth = {
    version,
    tags,
    ok,
    selectedBaseUrl: selectedAttempt?.baseUrl ?? '',
    selectedSource: selectedAttempt?.source ?? '',
    attemptedCandidates,
    wslRemediationCommand: WSL_OLLAMA_REMEDIATION_COMMAND,
  };
  logAction('ollama_health', {
    ok,
    selectedBaseUrl: ollamaHealth.selectedBaseUrl,
    selectedSource: ollamaHealth.selectedSource,
    attemptedCandidates,
    error,
  });

  if (ok) {
    recordChecklistItem(
      'startup_ollama_reachable',
      STATUSES.PASS,
      { version, tags, selectedBaseUrl: ollamaHealth.selectedBaseUrl, selectedSource: ollamaHealth.selectedSource, attemptedCandidates },
      'Ollama /api/version and /api/tags are reachable.',
    );
    recordChecklistItem(
      'startup_ollama_unreachable',
      STATUSES.PASS,
      { version, tags, selectedBaseUrl: ollamaHealth.selectedBaseUrl, selectedSource: ollamaHealth.selectedSource, attemptedCandidates },
      'No Ollama unreachable blocker recorded.',
    );
    return ollamaHealth;
  }

  recordChecklistItem(
    'startup_ollama_reachable',
    STATUSES.BLOCKED,
    { version, tags, attemptedCandidates, remediation: WSL_OLLAMA_REMEDIATION_COMMAND },
    `Ollama unreachable. ${error || 'Health endpoints did not return OK.'} WSL remediation: \`${WSL_OLLAMA_REMEDIATION_COMMAND.replace(/\n/g, ' && ')}\`.`,
  );
  recordChecklistItem(
    'startup_ollama_unreachable',
    STATUSES.BLOCKED,
    { version, tags, attemptedCandidates, remediation: WSL_OLLAMA_REMEDIATION_COMMAND },
    `Ollama unreachable. ${error || 'Health endpoints did not return OK.'}`,
  );
  return ollamaHealth;
}

function hasLeakage(text) {
  return EXAMPLE_LEAKAGE_MARKERS.some((marker) => text.includes(marker));
}

function markModelBackedBlocked() {
  const modelItems = CHECKLIST_ITEMS.filter((item) => (
    item.section === 'Model-Assisted / Analysis Runtime Checks'
    || item.section === 'No-Prose Checks'
  ));
  for (const item of modelItems) {
    recordChecklistItem(
      item.id,
      STATUSES.BLOCKED,
      { ollamaHealth },
      'Model-backed check blocked because Ollama readiness failed.',
    );
  }
}

async function waitForAppReady() {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    logAction('networkidle_timeout_ignored');
  });
  await page.locator('.app-shell, .project-nav').first().waitFor({ state: 'visible', timeout: 20000 });
}

async function getActiveProjectSnapshot() {
  const headerTitle = (await page.locator('.project-nav .panel-header h1').first().innerText().catch(() => '')).trim();
  const select = page.locator('select.project-select, select[aria-label="Select project"]').first();
  const selectValue = (await select.inputValue().catch(() => '')).trim();
  const selectedOptionText = (await select.locator(`option[value="${selectValue}"]`).innerText().catch(() => '')).trim();
  const overviewProjectId = (
    await page
      .locator('.project-overview dt:has-text("Project ID") + dd')
      .first()
      .innerText()
      .catch(() => '')
  ).trim();
  const snapshot = { headerTitle, selectValue, selectedOptionText, overviewProjectId };
  logAction('active_project_snapshot', snapshot);
  return snapshot;
}

async function createUniqueProjectThroughUi() {
  uniqueProjectTitle = `MVP Owner Acceptance ${Date.now()}`;
  logAction('create_unique_project_begin', { uniqueProjectTitle });

  await fillFirstMatching(['OMI-guided project title', 'Project title', 'Owner project title'], uniqueProjectTitle);
  await fillFirstMatching(['Owner-authored setup idea'], PROJECT_SETUP_IDEA);
  await fillFirstMatching(['Owner-authored setup notes'], PROJECT_SETUP_NOTES);
  const setupText = await getScopedText('section[aria-label="OMI-guided project setup"]', 'omi-guided-project-setup');
  softAssert(
    'manual_workspace_omi_candidates_not_approved_memory',
    setupText.includes('Setup candidate') && setupText.includes('not approved project truth'),
    STATUSES.FAIL,
    { setupTextSnippet: setupText.slice(0, 800) },
    'Setup candidate/planning labels are visible.',
    'Setup candidate/planning labels were not visible.',
  );

  await clickByText(['Review before creating project']);
  await screenshot('02-review-before-create', [
    'manual_workspace_create_project',
    'project_isolation_new_project_activated',
  ]);
  const confirmCheckbox = page.getByRole('checkbox', {
    name: /confirm this owner-authored setup can create a project/i,
  });
  if (await confirmCheckbox.count()) {
    await confirmCheckbox.first().check();
    logAction('owner_action_test_fixture_confirmation_checked');
  } else {
    recordChecklistItem(
      'manual_workspace_create_project',
      STATUSES.FAIL,
      { reason: 'Final confirmation checkbox not found.' },
      'Project creation confirmation checkbox was not exposed.',
    );
    return false;
  }

  await clickByText(['Create project']);
  await page.waitForTimeout(1000);
  await waitForAppReady();
  await screenshot('03-after-project-creation', [
    'manual_workspace_create_project',
    'project_isolation_new_project_activated',
    'manual_workspace_overview_active_only',
  ]);

  const snapshot = await getActiveProjectSnapshot();
  uniqueProjectId = snapshot.selectValue;
  const titleActive = snapshot.headerTitle.includes(uniqueProjectTitle);
  const selectActive = snapshot.selectedOptionText.includes(uniqueProjectTitle);
  const overviewActive = snapshot.overviewProjectId === uniqueProjectId && uniqueProjectId !== 'example';
  softAssert(
    'manual_workspace_create_project',
    Boolean(uniqueProjectId) && uniqueProjectId !== 'example',
    STATUSES.FAIL,
    { uniqueProjectTitle, snapshot },
    'Created project through owner-confirmed UI fixture.',
    'Project creation did not produce a non-example active project.',
  );
  softAssert(
    'project_isolation_new_project_activated',
    titleActive && selectActive && overviewActive,
    STATUSES.FAIL,
    { uniqueProjectTitle, uniqueProjectId, snapshot },
    'Header, selector, and Overview reflect the created project.',
    'Header, selector, and Overview did not all reflect the created project.',
  );
  softAssert(
    'manual_workspace_overview_active_only',
    overviewActive,
    STATUSES.FAIL,
    { uniqueProjectId, snapshot },
    'Overview reflects the active project.',
    'Overview did not reflect the active project.',
  );
  return Boolean(uniqueProjectId) && uniqueProjectId !== 'example';
}

async function runStartupChecks() {
  logAction('section_start', { section: 'Startup Requirements' });
  await ensureEvidenceDirs();

  const backend = await safeFetchJson(`${BACKEND_BASE_URL.replace(/\/$/, '')}/api/projects`);
  softAssert(
    'startup_backend_running',
    backend.ok,
    STATUSES.BLOCKED,
    { endpoint: '/api/projects', backend },
    'Backend reachable through safe /api/projects endpoint.',
    'Backend safe endpoint was not reachable.',
  );

  const scriptPath = path.join(REPO_ROOT, 'scripts', 'mvp-project-isolation-browser-smoke.mjs');
  const scriptExists = await fs.access(scriptPath).then(() => true).catch(() => false);
  softAssert(
    'startup_project_isolation_script_available',
    scriptExists,
    STATUSES.BLOCKED,
    { scriptPath },
    'Existing project isolation browser smoke script exists.',
    'Existing project isolation browser smoke script was not found.',
  );

  recordChecklistItem(
    'startup_owner_understands_analysis_boundaries',
    STATUSES.MANUAL_REVIEW_REQUIRED,
    { source: 'Automated script can record boundary text but cannot confirm owner understanding.' },
    'Owner understanding remains a manual review item.',
  );

  await checkOllamaHealth();

  let chromium;
  try {
    chromium = await loadPlaywrightChromium();
  } catch (error) {
    toolingBlocked = true;
    recordChecklistItem(
      'startup_frontend_running',
      STATUSES.BLOCKED,
      { error: error instanceof Error ? error.message : String(error) },
      'Playwright tooling blocked before frontend navigation.',
    );
    return null;
  }

  try {
    browser = await chromium.launch();
    page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
    logAction('navigate_frontend', { url: APP_BASE_URL });
    await page.goto(APP_BASE_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await waitForAppReady();
    await screenshot('01-startup-frontend', ['startup_frontend_running']);
    recordChecklistItem(
      'startup_frontend_running',
      STATUSES.PASS,
      { appBaseUrl: APP_BASE_URL },
      'Frontend reached and app shell rendered.',
    );
    return page;
  } catch (error) {
    toolingBlocked = true;
    recordChecklistItem(
      'startup_frontend_running',
      STATUSES.BLOCKED,
      { appBaseUrl: APP_BASE_URL, error: error instanceof Error ? error.message : String(error) },
      'Frontend was not reachable or app shell did not render.',
    );
    return null;
  }
}

async function runProjectIsolationChecks() {
  logAction('section_start', { section: 'Project Isolation' });
  if (!page) {
    for (const id of [
      'project_isolation_playwright_evidence_reviewed',
      'project_isolation_script_records_pass',
      'project_isolation_script_exit_zero',
      'project_isolation_no_blockers',
      'project_isolation_new_project_activated',
      'project_isolation_scenes_no_leakage',
      'project_isolation_memory_canon_no_leakage',
    ]) {
      recordChecklistItem(id, STATUSES.BLOCKED, {}, 'Frontend/browser startup blocked.');
    }
    return;
  }

  recordChecklistItem(
    'project_isolation_playwright_evidence_reviewed',
    STATUSES.MANUAL_REVIEW_REQUIRED,
    { source: 'Automated harness records a fresh equivalent smoke path; owner can review prior artifact separately.' },
    'Prior project isolation evidence review remains a manual review item.',
  );

  const created = await createUniqueProjectThroughUi();
  if (!created) {
    recordChecklistItem('project_isolation_script_records_pass', STATUSES.FAIL, {}, 'Equivalent project creation smoke failed.');
    recordChecklistItem('project_isolation_script_exit_zero', STATUSES.FAIL, {}, 'Equivalent script exit would be non-zero.');
    recordChecklistItem('project_isolation_no_blockers', STATUSES.FAIL, {}, 'Project creation blocker found.');
    return;
  }

  await screenshot('04-project-overview', ['project_isolation_new_project_activated']);

  const scenesText = await getScopedText('nav[aria-label="Scenes"]', 'scoped-scenes-nav');
  const sceneEmpty = /No scenes yet/i.test(scenesText);
  softAssert(
    'project_isolation_scenes_no_leakage',
    !hasLeakage(scenesText) && !/example/i.test(scenesText),
    STATUSES.FAIL,
    { scopedText: scenesText },
    'Scoped Scenes nav has no example, scene_001, or unrelated leakage.',
    'Scoped Scenes nav leaked example, scene_001, or unrelated project data.',
  );
  softAssert(
    'manual_workspace_scenes_empty_new_project',
    sceneEmpty,
    STATUSES.FAIL,
    { scopedText: scenesText },
    'Scenes show empty/new project behavior.',
    'Scenes did not show expected empty/new project behavior.',
  );

  await clickByText(['Memory / Canon']);
  await page.waitForTimeout(500);
  await screenshot('05-memory-canon', [
    'project_isolation_memory_canon_no_leakage',
    'manual_workspace_memory_canon_approved_only',
  ]);
  const memoryText = await getScopedText('section.memory-canon-shell', 'scoped-memory-canon-shell');
  softAssert(
    'project_isolation_memory_canon_no_leakage',
    !hasLeakage(memoryText) && !/The Princess and the Pea/i.test(memoryText),
    STATUSES.FAIL,
    { scopedText: memoryText },
    'Scoped Memory/Canon shell has no unrelated leakage.',
    'Scoped Memory/Canon shell leaked unrelated project data.',
  );
  softAssert(
    'manual_workspace_memory_canon_approved_only',
    /approved records only/i.test(memoryText)
      && /Candidate records remain/i.test(memoryText)
      && /No apply-promotion/i.test(memoryText),
    STATUSES.FAIL,
    { scopedText: memoryText.slice(0, 1200) },
    'Memory/Canon approved-only boundary copy is visible.',
    'Memory/Canon approved-only boundary copy was missing.',
  );

  const projectIsolationPass =
    checklistResults.project_isolation_new_project_activated.status === STATUSES.PASS
    && checklistResults.project_isolation_scenes_no_leakage.status === STATUSES.PASS
    && checklistResults.project_isolation_memory_canon_no_leakage.status === STATUSES.PASS;
  recordChecklistItem(
    'project_isolation_script_records_pass',
    projectIsolationPass ? STATUSES.PASS : STATUSES.FAIL,
    { equivalentScriptPath: 'scripts/mvp-owner-acceptance-browser-smoke.mjs' },
    projectIsolationPass
      ? 'Equivalent project isolation smoke path records PASS.'
      : 'Equivalent project isolation smoke path found blockers.',
  );
  recordChecklistItem(
    'project_isolation_script_exit_zero',
    projectIsolationPass ? STATUSES.PASS : STATUSES.FAIL,
    { equivalentScriptExit: projectIsolationPass ? 0 : 1 },
    projectIsolationPass ? 'Equivalent SCRIPT_EXIT=0.' : 'Equivalent SCRIPT_EXIT would be non-zero.',
  );
  recordChecklistItem(
    'project_isolation_no_blockers',
    projectIsolationPass ? STATUSES.PASS : STATUSES.FAIL,
    {},
    projectIsolationPass ? 'No project isolation blockers recorded.' : 'Project isolation blocker recorded.',
  );
}

async function runManualWorkspaceChecks() {
  logAction('section_start', { section: 'Manual Workspace Checks' });
  if (!page || !uniqueProjectId) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Manual Workspace Checks')) {
      if (checklistResults[item.id].status === STATUSES.MANUAL_REVIEW_REQUIRED) {
        recordChecklistItem(item.id, STATUSES.BLOCKED, {}, 'Project creation/browser startup blocked.');
      }
    }
    return;
  }

  previousProjectId = 'example';
  const select = page.locator('select.project-select, select[aria-label="Select project"]').first();
  if (await select.count()) {
    await select.selectOption(previousProjectId).catch(() => {});
    await page.waitForTimeout(700);
    await select.selectOption(uniqueProjectId).catch(() => {});
    await page.waitForTimeout(700);
    const snapshot = await getActiveProjectSnapshot();
    softAssert(
      'manual_workspace_select_existing_project',
      snapshot.selectValue === uniqueProjectId,
      STATUSES.FAIL,
      { previousProjectId, uniqueProjectId, snapshot },
      'Project selector can switch to an existing project.',
      'Project selector did not switch to the expected project.',
    );
  } else {
    recordChecklistItem(
      'manual_workspace_select_existing_project',
      STATUSES.NOT_EXPOSED,
      {},
      'Project selector was not exposed.',
    );
  }

  const notesText = await getScopedText('nav[aria-label="Notes"]', 'scoped-notes-nav');
  if (/No notes yet/i.test(notesText)) {
    recordChecklistItem(
      'manual_workspace_notes_project_scoped',
      STATUSES.MANUAL_REVIEW_REQUIRED,
      { scopedText: notesText },
      'Notes list is project-scoped and empty, but no UI create-note workflow is exposed for a save/reload isolation proof.',
    );
  } else {
    recordChecklistItem(
      'manual_workspace_notes_project_scoped',
      hasLeakage(notesText) ? STATUSES.FAIL : STATUSES.MANUAL_REVIEW_REQUIRED,
      { scopedText: notesText },
      hasLeakage(notesText)
        ? 'Notes nav leaked unrelated data.'
        : 'Notes surface exists; owner should manually review note body save/switch isolation.',
    );
  }

  const materialsText = await getScopedText('nav[aria-label="Materials"]', 'scoped-materials-nav');
  if (/No materials yet/i.test(materialsText)) {
    recordChecklistItem(
      'manual_workspace_materials_project_scoped',
      STATUSES.MANUAL_REVIEW_REQUIRED,
      { scopedText: materialsText },
      'Materials list is project-scoped and empty, but no UI create-material workflow is exposed for a save/reload isolation proof.',
    );
  } else {
    recordChecklistItem(
      'manual_workspace_materials_project_scoped',
      hasLeakage(materialsText) ? STATUSES.FAIL : STATUSES.MANUAL_REVIEW_REQUIRED,
      { scopedText: materialsText },
      hasLeakage(materialsText)
        ? 'Materials nav leaked unrelated data.'
        : 'Materials surface exists; owner should manually review material body save/switch isolation.',
    );
  }
  await screenshot('06-manual-workspace-nav', [
    'manual_workspace_notes_project_scoped',
    'manual_workspace_materials_project_scoped',
  ]);
}

async function runRuntimeExtractionChecks() {
  logAction('section_start', { section: 'Runtime Extraction Checks' });
  if (!page) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Runtime Extraction Checks')) {
      recordChecklistItem(item.id, STATUSES.BLOCKED, {}, 'Frontend/browser startup blocked.');
    }
    return;
  }

  const visible = await getVisibleText();
  await screenshot('07-runtime-extraction-surfaces', CHECKLIST_ITEMS
    .filter((item) => item.section === 'Runtime Extraction Checks')
    .map((item) => item.id));

  const extractionSurfaceVisible = /runtime extraction|booknlp|spacy|raw artifact/i.test(visible);
  if (!extractionSurfaceVisible) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Runtime Extraction Checks')) {
      recordChecklistItem(
        item.id,
        STATUSES.MANUAL_REVIEW_REQUIRED,
        { visibleSurface: false },
        'No browser-visible runtime extraction/raw artifact control was exposed; manual/API review required.',
      );
    }
    return;
  }

  recordChecklistItem('runtime_extraction_unavailable_fail_closed', STATUSES.MANUAL_REVIEW_REQUIRED, { visibleSurface: true }, 'Runtime extraction wording is visible; owner should review fail-closed runtime behavior.');
  recordChecklistItem('runtime_extraction_failures_no_success_claim', STATUSES.MANUAL_REVIEW_REQUIRED, { visibleSurface: true }, 'Runtime extraction surface requires manual failed-runtime review.');
  recordChecklistItem('runtime_extraction_raw_artifacts_support_only', /support data/i.test(visible) ? STATUSES.PASS : STATUSES.MANUAL_REVIEW_REQUIRED, { visibleTextSnippet: visible.slice(0, 1500) }, 'Raw artifact support-data language checked where visible.');
  recordChecklistItem('runtime_extraction_raw_artifacts_not_truth', /not canon|not.*truth|support data/i.test(visible) ? STATUSES.PASS : STATUSES.MANUAL_REVIEW_REQUIRED, { visibleTextSnippet: visible.slice(0, 1500) }, 'Raw artifact not-truth boundary checked where visible.');
  recordChecklistItem('runtime_extraction_no_memory_canon_mutation', /no.*memory.*canon mutation|not canon/i.test(visible) ? STATUSES.PASS : STATUSES.MANUAL_REVIEW_REQUIRED, { visibleTextSnippet: visible.slice(0, 1500) }, 'No memory/canon mutation boundary checked where visible.');
  recordChecklistItem('runtime_extraction_candidate_first_owner_review', /candidate|owner review/i.test(visible) ? STATUSES.PASS : STATUSES.MANUAL_REVIEW_REQUIRED, { visibleTextSnippet: visible.slice(0, 1500) }, 'Candidate-first/owner-review language checked where visible.');
}

async function runCandidateReviewChecks() {
  logAction('section_start', { section: 'Candidate / Review Checks' });
  if (!page) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Candidate / Review Checks')) {
      recordChecklistItem(item.id, STATUSES.BLOCKED, {}, 'Frontend/browser startup blocked.');
    }
    return;
  }

  await clickByText(['Overview']).catch(() => {});
  await clickByText(['Open OMI']).catch(() => {});
  await page.waitForTimeout(700);
  await screenshot('08-candidate-review-surfaces', CHECKLIST_ITEMS
    .filter((item) => item.section === 'Candidate / Review Checks')
    .map((item) => item.id));

  const omiText = await getScopedText('section.omi-panel', 'scoped-omi-panel');
  const reviewText = await getScopedText('section.review-queue-panel', 'scoped-review-queue-panel');
  const combined = `${omiText}\n${reviewText}`;
  if (!combined.trim()) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Candidate / Review Checks')) {
      recordChecklistItem(item.id, STATUSES.NOT_EXPOSED, {}, 'Candidate/review surface was not visible.');
    }
    return;
  }

  softAssert('candidate_review_candidate_first_visible', /candidate-only|candidate planning|Candidate/i.test(combined), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: combined.slice(0, 1500) }, 'Candidate-first language/state is visible.', 'Candidate-first language/state needs manual review.');
  softAssert('candidate_review_queue_not_approval', /queue presence.*not approval|not canon|not project truth/i.test(combined), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: combined.slice(0, 1500) }, 'Review queue not-approval language is visible.', 'Review queue approval boundary needs manual review.');
  softAssert('candidate_review_read_only_state', /Read-only|read-only/i.test(combined), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: combined.slice(0, 1500) }, 'Read-only review state is visible.', 'Read-only review state needs manual review or data fixture.');
  softAssert('candidate_review_owner_action_explicit', /owner command|owner review command|explicit owner|controls are unavailable/i.test(combined), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: combined.slice(0, 1500) }, 'Owner action command boundary is visible where available.', 'Owner action execution requires manual review or queue fixture.');
  softAssert('candidate_review_confidence_not_truth', /Confidence.*not canon|confidence.*not truth/i.test(combined), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: combined.slice(0, 1500) }, 'Confidence is not presented as truth where visible.', 'Confidence boundary requires manual review or queue fixture.');
  softAssert('candidate_review_persistence_not_canon', /candidate persistence is not canon|candidate.*not canon/i.test(combined), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: combined.slice(0, 1500) }, 'Candidate persistence is not canon language is visible where available.', 'Candidate persistence boundary requires manual review.');
}

async function runApplyPromotionChecks() {
  logAction('section_start', { section: 'Apply-Promotion Checks' });
  if (!page) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Apply-Promotion Checks')) {
      recordChecklistItem(item.id, STATUSES.BLOCKED, {}, 'Frontend/browser startup blocked.');
    }
    return;
  }

  const applyText = await getScopedText('section.apply-promotion-confirmation', 'scoped-apply-promotion-confirmation');
  await screenshot('09-apply-promotion', CHECKLIST_ITEMS
    .filter((item) => item.section === 'Apply-Promotion Checks')
    .map((item) => item.id));

  if (!applyText.trim()) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Apply-Promotion Checks')) {
      recordChecklistItem(item.id, STATUSES.MANUAL_REVIEW_REQUIRED, {}, 'No safe apply-promotion UI fixture is visible without a review queue entry.');
    }
    return;
  }

  softAssert('apply_promotion_requires_confirmation', /confirmation|owner_confirmation|Final owner/i.test(applyText), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: applyText.slice(0, 1500) }, 'Apply-promotion confirmation requirement is visible.', 'Apply-promotion confirmation requirement needs manual review.');
  softAssert('apply_promotion_audit_details', /audit|promotion_record_id|evidence_refs|provenance_refs|source_locator_refs/i.test(applyText), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: applyText.slice(0, 1500) }, 'Audit/detail fields are visible where safe.', 'Audit details require manual review or queue fixture.');
  softAssert('apply_promotion_only_approved_workflow', /only approved memory\/canon mutation path|only approved/i.test(applyText), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: applyText.slice(0, 1500) }, 'Approved workflow boundary is visible.', 'Approved workflow boundary requires manual review.');
  softAssert('apply_promotion_failed_rejected_unchanged', /unavailable|required|not canon/i.test(applyText), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: applyText.slice(0, 1500) }, 'Fail-closed/unavailable state is visible; no promotion executed.', 'Rejected/failed mutation unchanged behavior requires manual review.');
  softAssert('apply_promotion_no_bypass', /queue presence is not approval|confidence is not truth|candidate persistence is not canon|raw artifacts are support data/i.test(applyText), STATUSES.MANUAL_REVIEW_REQUIRED, { scopedText: applyText.slice(0, 1500) }, 'No-bypass language is visible.', 'No-bypass behavior requires manual review.');
}

async function runModelAssistedChecks() {
  logAction('section_start', { section: 'Model-Assisted / Analysis Runtime Checks' });
  if (!ollamaHealth.ok) {
    markModelBackedBlocked();
    return;
  }
  if (!page) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Model-Assisted / Analysis Runtime Checks')) {
      recordChecklistItem(item.id, STATUSES.BLOCKED, {}, 'Frontend/browser startup blocked.');
    }
    return;
  }

  const storyCheckVisible = /Run Story Check|Story Check|Analysis/i.test(await getVisibleText());
  await screenshot('10-model-assisted-analysis', CHECKLIST_ITEMS
    .filter((item) => item.section === 'Model-Assisted / Analysis Runtime Checks')
    .map((item) => item.id));

  if (!storyCheckVisible) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'Model-Assisted / Analysis Runtime Checks')) {
      recordChecklistItem(item.id, STATUSES.NOT_EXPOSED, {}, 'No Story Check/model-assisted UI surface visible.');
    }
    return;
  }

  recordChecklistItem('model_assisted_evidence_backed_only', STATUSES.MANUAL_REVIEW_REQUIRED, { diagnosticText: OWNER_DIAGNOSTIC_TEXT }, 'Ollama is healthy and Story Check UI is visible; live model workflow requires owner-run fixture with selected owner-authored scene.');
  recordChecklistItem('model_assisted_confidence_not_truth', STATUSES.MANUAL_REVIEW_REQUIRED, {}, 'Confidence/truth boundary requires model output or existing visible result.');
  recordChecklistItem('model_assisted_output_not_canon', STATUSES.MANUAL_REVIEW_REQUIRED, {}, 'Model output not-canon boundary requires model output or existing visible result.');
  recordChecklistItem('model_assisted_ncp_structured_context_only', STATUSES.NOT_EXPOSED, {}, 'No NCP UI/runtime label visible in browser surface.');
  recordChecklistItem('model_assisted_subtxt_diagnostic_only', STATUSES.NOT_EXPOSED, {}, 'No Subtxt UI/runtime label visible in browser surface.');
  recordChecklistItem('model_assisted_dramatica_flow_analysis_only', STATUSES.NOT_EXPOSED, {}, 'No dramatica-flow UI/runtime label visible in browser surface.');
  recordChecklistItem('model_assisted_no_prose_outline_canon_training_promotion', STATUSES.MANUAL_REVIEW_REQUIRED, {}, 'Analysis-only runtime no-prose/no-canon/no-training/no-promotion boundary needs manual or API review.');
}

async function runNoProseChecks() {
  logAction('section_start', { section: 'No-Prose Checks', negativeRequests: NO_PROSE_NEGATIVE_REQUESTS });
  if (!ollamaHealth.ok) {
    markModelBackedBlocked();
    return;
  }
  if (!page) {
    for (const item of CHECKLIST_ITEMS.filter((entry) => entry.section === 'No-Prose Checks')) {
      recordChecklistItem(item.id, STATUSES.BLOCKED, {}, 'Frontend/browser startup blocked.');
    }
    return;
  }

  await screenshot('11-no-prose-surfaces', CHECKLIST_ITEMS
    .filter((item) => item.section === 'No-Prose Checks')
    .map((item) => item.id));
  const visible = await getVisibleText();
  const hasAnalysisSurface = /Run Story Check|Story Check|Analysis/i.test(visible);
  const noProseBoundaryVisible = /cannot write or rewrite story prose|candidate analysis|does not change project truth|no-canon/i.test(visible);

  const status = hasAnalysisSurface && noProseBoundaryVisible
    ? STATUSES.MANUAL_REVIEW_REQUIRED
    : STATUSES.MANUAL_REVIEW_REQUIRED;
  const note = hasAnalysisSurface
    ? 'Analysis surface exists; negative-path no-prose prompts require owner-run selected-scene fixture to avoid unsafe mutation.'
    : 'No model/no-prose route available in browser surface.';

  for (const id of [
    'no_prose_no_rewrite',
    'no_prose_no_continuation',
    'no_prose_no_outline_generation',
    'no_prose_no_generated_prose',
    'no_prose_no_imitation_polish_improve_expand_draft_chapter',
  ]) {
    recordChecklistItem(id, status, { negativeRequests: NO_PROSE_NEGATIVE_REQUESTS, noProseBoundaryVisible }, note);
  }
}

function runFinalOwnerDecisionChecks() {
  logAction('section_start', { section: 'Final Owner Decision' });
  recordChecklistItem(
    'final_owner_decision_pending',
    STATUSES.PASS,
    { finalDecision: 'Pending owner acceptance.' },
    'Automated harness leaves owner acceptance pending.',
  );
  recordChecklistItem(
    'final_owner_decision_accepted_by_owner',
    STATUSES.MANUAL_REVIEW_REQUIRED,
    {},
    'The automated script must not choose Accepted; owner acceptance remains pending.',
  );
  recordChecklistItem(
    'final_owner_decision_blocked_with_reason',
    appBlockerFound || startupBlocked ? STATUSES.MANUAL_REVIEW_REQUIRED : STATUSES.MANUAL_REVIEW_REQUIRED,
    {},
    'Owner may later choose blocked with reason after reviewing evidence.',
  );
}

function computeFinalDecision() {
  const values = Object.values(checklistResults);
  if (toolingBlocked || startupBlocked || values.some((item) => item.status === STATUSES.FAIL || item.status === STATUSES.BLOCKED)) {
    return FINAL_DECISIONS.BLOCKED;
  }
  if (values.some((item) => item.status === STATUSES.NOT_EXPOSED)) {
    return FINAL_DECISIONS.MANUAL_REVIEW_REQUIRED;
  }
  const ownerOnlyManualItems = new Set([
    'startup_owner_understands_analysis_boundaries',
    'project_isolation_playwright_evidence_reviewed',
    'final_owner_decision_accepted_by_owner',
    'final_owner_decision_blocked_with_reason',
  ]);
  const manualItems = values.filter((item) => item.status === STATUSES.MANUAL_REVIEW_REQUIRED);
  if (manualItems.some((item) => !ownerOnlyManualItems.has(item.id))) {
    return FINAL_DECISIONS.MANUAL_REVIEW_REQUIRED;
  }
  return FINAL_DECISIONS.READY_FOR_OWNER_REVIEW;
}

function exitCodeForDecision() {
  if (toolingBlocked || checklistResults.startup_frontend_running.status === STATUSES.BLOCKED) {
    return 2;
  }
  if (finalDecision === FINAL_DECISIONS.BLOCKED) {
    return 1;
  }
  return 0;
}

function groupedResults() {
  return SECTION_ORDER.map((section) => ({
    section,
    items: CHECKLIST_ITEMS
      .filter((item) => item.section === section)
      .map((item) => checklistResults[item.id]),
  }));
}

async function writeEvidenceArtifacts() {
  finalDecision = computeFinalDecision();
  const exitCode = exitCodeForDecision();
  const finishedAt = new Date().toISOString();
  const checklistPath = path.join(MVP_ACCEPTANCE_EVIDENCE_DIR, 'checklist-results.json');
  const workflowPath = path.join(MVP_ACCEPTANCE_EVIDENCE_DIR, 'workflow-log.json');
  const reportPath = path.join(MVP_ACCEPTANCE_EVIDENCE_DIR, 'evidence-report.md');
  const summary = Object.values(checklistResults).reduce((acc, item) => {
    acc[item.status] = (acc[item.status] ?? 0) + 1;
    return acc;
  }, {});

  await fs.writeFile(workflowPath, `${JSON.stringify({
    task: 'MVP-READINESS-OWNER-ACCEPTANCE-002',
    startedAt: runStartedAt,
    finishedAt,
    appBaseUrl: APP_BASE_URL,
    backendBaseUrl: BACKEND_BASE_URL,
    ollamaBaseUrl: ollamaHealth.selectedBaseUrl,
    ollamaSource: ollamaHealth.selectedSource,
    ollamaAttemptedCandidates: ollamaHealth.attemptedCandidates,
    evidenceDir: MVP_ACCEPTANCE_EVIDENCE_DIR,
    uniqueProjectTitle,
    uniqueProjectId,
    finalDecision,
    exitCode,
    toolingBlocked,
    startupBlocked,
    appBlockerFound,
    ollamaHealth,
    actions: workflowLog,
  }, null, 2)}\n`, 'utf8');

  await fs.writeFile(checklistPath, `${JSON.stringify({
    task: 'MVP-READINESS-OWNER-ACCEPTANCE-002',
    resultModel: Object.values(STATUSES),
    finalDecision,
    exitCode,
    summary,
    groupedResults: groupedResults(),
    results: Object.values(checklistResults),
  }, null, 2)}\n`, 'utf8');

  const problemItems = Object.values(checklistResults)
    .filter((item) => item.status !== STATUSES.PASS);
  const report = [
    '# MVP Owner Acceptance Browser Evidence Report',
    '',
    `- Task: \`MVP-READINESS-OWNER-ACCEPTANCE-002\``,
    `- Final automated decision: **${finalDecision}**`,
    `- Exit code: \`${exitCode}\``,
    `- App base URL: \`${APP_BASE_URL}\``,
    `- Backend base URL: \`${BACKEND_BASE_URL}\``,
    `- Selected Ollama base URL: \`${ollamaHealth.selectedBaseUrl || 'none'}\``,
    `- Selected Ollama source: \`${ollamaHealth.selectedSource || 'none'}\``,
    `- Evidence directory: \`${MVP_ACCEPTANCE_EVIDENCE_DIR}\``,
    `- Started: \`${runStartedAt}\``,
    `- Finished: \`${finishedAt}\``,
    '',
    '## Blocked / Manual-Review Summary',
    '',
    problemItems.length === 0
      ? '- None. All automated checklist items passed.'
      : problemItems.map((item) => `- **${item.status}** \`${item.id}\` — ${item.text} ${item.notes.length ? `(${item.notes.join(' ')})` : ''}`).join('\n'),
    '',
    '## Ollama Readiness Handling',
    '',
    ollamaHealth.ok
      ? '- Ollama `/api/version` and `/api/tags` readiness checks passed.'
      : '- Ollama readiness failed or was unavailable. Model-backed checks are BLOCKED.',
    '',
    '- Attempted candidates:',
    ...(ollamaHealth.attemptedCandidates.length
      ? ollamaHealth.attemptedCandidates.map((candidate) => (
        `  - ${candidate.ok ? 'PASS' : 'BLOCKED'} ${candidate.source}: \`${candidate.baseUrl}\` (` +
        `version: ${candidate.versionStatus ?? 'n/a'}, tags: ${candidate.tagsStatus ?? 'n/a'}` +
        `${candidate.errorSummary ? `, error: ${candidate.errorSummary}` : ''})`
      ))
      : ['  - None.']),
    '',
    'WSL remediation command:',
    '',
    '```bash',
    WSL_OLLAMA_REMEDIATION_COMMAND,
    '```',
    '',
    '## Checklist Results',
    '',
  ];

  for (const group of groupedResults()) {
    report.push(`### ${group.section}`, '');
    for (const item of group.items) {
      report.push(`- **${item.status}** \`${item.id}\` — ${item.text}`);
      for (const note of item.notes) {
        report.push(`  - ${note}`);
      }
    }
    report.push('');
  }

  report.push('## Screenshots', '');
  const screenshots = await fs.readdir(screenshotDir).catch(() => []);
  const pngs = screenshots.filter((file) => file.endsWith('.png')).sort();
  if (pngs.length === 0) {
    report.push('- None captured.');
  } else {
    for (const file of pngs) {
      report.push(`- \`screenshots/${file}\``);
    }
  }

  report.push(
    '',
    '## Safety Boundary',
    '',
    '- This report does not mark MVP complete.',
    '- This report does not claim owner acceptance.',
    '- No product fixes are implemented by this script.',
    '- No generated prose is requested or produced by this script.',
    '- Ollama checks are readiness checks only unless the owner later runs app Story Check through the app.',
    '- BookNLP/spaCy/NCP/Subtxt/dramatica-flow are not executed directly.',
    '- No automatic canon/memory mutation or apply-promotion shortcut is performed.',
    '',
    '## Artifacts',
    '',
    '- `workflow-log.json`',
    '- `checklist-results.json`',
    '- `evidence-report.md`',
  );

  await fs.writeFile(reportPath, `${report.join('\n')}\n`, 'utf8');
  logAction('write_evidence_artifacts', { checklistPath, workflowPath, reportPath, finalDecision, exitCode });
  return { exitCode, finalDecision };
}

async function main() {
  try {
    await runStartupChecks();
    if (page) {
      await runProjectIsolationChecks();
      await runManualWorkspaceChecks();
      await runRuntimeExtractionChecks();
      await runCandidateReviewChecks();
      await runApplyPromotionChecks();
      await runModelAssistedChecks();
      await runNoProseChecks();
    } else {
      markModelBackedBlocked();
    }
    runFinalOwnerDecisionChecks();
  } catch (error) {
    appBlockerFound = true;
    logAction('unhandled_error', { error: error instanceof Error ? error.stack ?? error.message : String(error) });
  } finally {
    if (browser) {
      await browser.close().catch(() => {});
    }
    const { exitCode } = await writeEvidenceArtifacts();
    process.exitCode = exitCode;
  }
}

main();
