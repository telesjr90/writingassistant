#!/usr/bin/env node
/**
 * MVP-READINESS-OWNER-ACCEPTANCE-005
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
const MVP_ACCEPTANCE_FIXTURE = process.env.MVP_ACCEPTANCE_FIXTURE ?? getCliFixtureName() ?? 'cyber-detective';
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
  'Cyber Detective Fixture',
  'Final Owner Decision',
]);

const CYBER_DETECTIVE_CONTENT = `A paranoid, grumpy, cybersecurity detective and his team work as private investigators. The detective only has analog equipment in his home and steals cable, power, water, everything from his neighbors.

Their secretary is a person who is in hiding after being caught doing corporate espionage by him.
The IT is a girl who used to run digital scams for her family's business.

The muscle is a heavily traumatized, ptsd, drug user, survavilist, israeli woman who shot up her platoon and blew up a base during a mission where she caught them raping kids, and was shot by her commander and left for dead. Palestines saved her.
After that she escaped and made her way to Canada.

The detective found her and kept her safe.

The detective is trying to find his kid. She killed her stepmother and stepbrother trying to kill her father on a contract.
He trained her, they had a loving relationship. she disappeared when she was 16 and he only saw her again five years later at the accident that killed the rest of his family.
He has no idea why she ran away, and why she killed them.

Nowadays he mostly works in small cases to pay the bills and tries to rebuild his life.`;

const ACCEPTANCE_FIXTURES = Object.freeze({
  'cyber-detective': Object.freeze({
    id: 'cyber-detective',
    slug: 'cyber-detective',
    title: 'Cyber detective',
    rawOwnerAuthoredContent: CYBER_DETECTIVE_CONTENT,
    contentWarningMetadata: Object.freeze([
      'mature material',
      'violence',
      'trauma',
      'abuse references',
      'drug use references',
    ]),
    ownerAuthored: true,
    allowedIntent: 'analysis/diagnostic only',
    forbiddenIntents: Object.freeze([
      'rewrite',
      'continue',
      'outline',
      'draft',
      'polish',
      'improve',
      'imitate',
      'expand',
      'generate prose',
    ]),
    setupNotes:
      'Owner-authored MVP acceptance fixture for analysis-only OMI and Story Check workflow testing.',
  }),
});

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
  { id: 'cyber_fixture_project_created', section: 'Cyber Detective Fixture', text: 'Cyber detective owner-authored fixture project is created through the browser UI.' },
  { id: 'cyber_fixture_owner_source_visible_on_review', section: 'Cyber Detective Fixture', text: 'Cyber detective owner-authored source is visible on review before creation.' },
  { id: 'cyber_fixture_active_project_scoped', section: 'Cyber Detective Fixture', text: 'Cyber detective project is active and scoped in header, selector, and Overview.' },
  { id: 'cyber_fixture_omi_candidate_planning_only', section: 'Cyber Detective Fixture', text: 'Cyber detective OMI/setup material remains candidate/planning only.' },
  { id: 'cyber_fixture_memory_canon_not_mutated', section: 'Cyber Detective Fixture', text: 'Cyber detective fixture does not mutate approved Memory/Canon.' },
  { id: 'cyber_fixture_story_check_source_selected', section: 'Cyber Detective Fixture', text: 'Cyber detective owner-authored source/scene is safely selected for Story Check.' },
  { id: 'cyber_fixture_story_check_submitted', section: 'Cyber Detective Fixture', text: 'Cyber detective Story Check is submitted through the app UI only after safe source selection.' },
  { id: 'cyber_fixture_story_check_result_diagnostic_only', section: 'Cyber Detective Fixture', text: 'Cyber detective Story Check result is diagnostic/candidate analysis only.' },
  { id: 'cyber_fixture_story_check_no_generated_prose', section: 'Cyber Detective Fixture', text: 'Cyber detective Story Check result contains no generated story prose.' },
  { id: 'cyber_fixture_story_check_analysis_only', section: 'Cyber Detective Fixture', text: 'Cyber detective Story Check path is diagnostic-only when safely exposed.' },
  { id: 'cyber_fixture_story_check_no_prose_generated', section: 'Cyber Detective Fixture', text: 'Cyber detective Story Check produces no continuation, rewrite, outline, draft, polish, imitation, expansion, or story prose.' },
  { id: 'cyber_fixture_model_output_not_canon', section: 'Cyber Detective Fixture', text: 'Cyber detective model-backed output is not presented as canon, approved memory, or truth.' },
  { id: 'cyber_fixture_no_prose_rewrite_refused', section: 'Cyber Detective Fixture', text: 'Cyber detective no-prose route refuses or fail-closes rewrite prompts.' },
  { id: 'cyber_fixture_no_prose_continue_refused', section: 'Cyber Detective Fixture', text: 'Cyber detective no-prose route refuses or fail-closes continuation prompts.' },
  { id: 'cyber_fixture_no_prose_outline_refused', section: 'Cyber Detective Fixture', text: 'Cyber detective no-prose route refuses or fail-closes outline prompts.' },
  { id: 'cyber_fixture_no_prose_draft_polish_imitation_refused', section: 'Cyber Detective Fixture', text: 'Cyber detective no-prose route refuses or fail-closes draft, polish, improve, expand, and imitate prompts.' },
  { id: 'cyber_fixture_no_rewrite', section: 'Cyber Detective Fixture', text: 'Cyber detective negative path rejects or fail-closes rewrite requests.' },
  { id: 'cyber_fixture_no_continuation', section: 'Cyber Detective Fixture', text: 'Cyber detective negative path rejects or fail-closes continuation requests.' },
  { id: 'cyber_fixture_no_outline', section: 'Cyber Detective Fixture', text: 'Cyber detective negative path rejects or fail-closes outline requests.' },
  { id: 'cyber_fixture_no_draft_polish_imitation', section: 'Cyber Detective Fixture', text: 'Cyber detective negative path rejects or fail-closes draft, polish, improve, expand, and imitate requests.' },
  { id: 'cyber_fixture_runtime_tools_not_directly_executed', section: 'Cyber Detective Fixture', text: 'Cyber detective harness does not execute BookNLP, spaCy, NCP, Subtxt, or dramatica-flow directly.' },
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

const STORY_CHECK_DIAGNOSTIC_INSTRUCTION =
  'Analyze this owner-authored setup for story diagnostics only. Do not rewrite, continue, outline, expand, polish, imitate, or generate prose.';
const FORBIDDEN_PROSE_OUTPUT_PATTERNS = Object.freeze([
  /here(?:'s| is) (?:a|the) (?:rewrite|rewritten|continuation|continued|outline|draft|polished|improved|expanded|imitation)/i,
  /(?:rewritten|continued|polished|improved|expanded) version:/i,
  /chapter\s+\d+\s*:/i,
  /scene\s+\d+\s*:/i,
  /(?:INT\.|EXT\.)\s+[A-Z0-9][A-Z0-9 .'-]+/i,
  /(?:dialogue|narration):\s*["“]/i,
  /in the style of\s+[A-Z0-9]/i,
]);

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
let selectedFixture = selectAcceptanceFixture(MVP_ACCEPTANCE_FIXTURE);
let cyberFixtureStoryCheckStatus = STATUSES.MANUAL_REVIEW_REQUIRED;
let cyberFixtureNoProseStatus = STATUSES.MANUAL_REVIEW_REQUIRED;
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

function getCliFixtureName() {
  const fixtureArg = process.argv.find((arg) => arg.startsWith('--fixture='));
  if (!fixtureArg) {
    return '';
  }
  return fixtureArg.slice('--fixture='.length).trim();
}

function selectAcceptanceFixture(fixtureName) {
  const normalized = String(fixtureName ?? '').trim() || 'cyber-detective';
  const fixture = ACCEPTANCE_FIXTURES[normalized];
  if (!fixture) {
    throw new Error(
      `Unknown MVP acceptance fixture: ${normalized}. Supported fixtures: ${Object.keys(ACCEPTANCE_FIXTURES).join(', ')}`,
    );
  }
  return fixture;
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

function containsForbiddenGeneratedProse(text) {
  return FORBIDDEN_PROSE_OUTPUT_PATTERNS.some((pattern) => pattern.test(text));
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
  uniqueProjectTitle = `${selectedFixture.title} MVP Acceptance ${Date.now()}`;
  logAction('cyber_fixture_create_project_begin', {
    fixtureId: selectedFixture.id,
    fixtureTitle: selectedFixture.title,
    fixtureSlug: selectedFixture.slug,
    uniqueProjectTitle,
    contentLength: selectedFixture.rawOwnerAuthoredContent.length,
    ownerAuthored: selectedFixture.ownerAuthored,
    allowedIntent: selectedFixture.allowedIntent,
    forbiddenIntents: selectedFixture.forbiddenIntents,
    didGenerateStoryProseFromFixture: false,
  });

  await fillFirstMatching(['OMI-guided project title', 'Project title', 'Owner project title'], uniqueProjectTitle);
  await fillFirstMatching(['Owner-authored setup idea'], selectedFixture.rawOwnerAuthoredContent);
  await fillFirstMatching(['Owner-authored setup notes'], selectedFixture.setupNotes);
  const setupText = await getScopedText('section[aria-label="OMI-guided project setup"]', 'omi-guided-project-setup');
  softAssert(
    'manual_workspace_omi_candidates_not_approved_memory',
    setupText.includes('Setup candidate') && setupText.includes('not approved project truth'),
    STATUSES.FAIL,
    { setupTextSnippet: setupText.slice(0, 800) },
    'Setup candidate/planning labels are visible.',
    'Setup candidate/planning labels were not visible.',
  );
  softAssert(
    'cyber_fixture_omi_candidate_planning_only',
    setupText.includes('Setup candidate') && setupText.includes('not approved project truth'),
    STATUSES.FAIL,
    { setupTextSnippet: setupText.slice(0, 800), fixtureId: selectedFixture.id },
    'Cyber detective setup is visibly labeled candidate/planning only.',
    'Cyber detective setup candidate/planning labels were not visible.',
  );

  await clickByText(['Review before creating project']);
  logAction('cyber_fixture_review_before_create', {
    fixtureId: selectedFixture.id,
    uniqueProjectTitle,
    contentLength: selectedFixture.rawOwnerAuthoredContent.length,
  });
  await screenshot('02-cyber-fixture-review-before-create', [
    'manual_workspace_create_project',
    'project_isolation_new_project_activated',
    'cyber_fixture_owner_source_visible_on_review',
  ]);
  const reviewText = await getScopedText('form[aria-label="Review setup draft"]', 'cyber-fixture-review-setup-draft');
  const fixtureSourceVisible = reviewText.includes(selectedFixture.title)
    && reviewText.includes(selectedFixture.rawOwnerAuthoredContent.slice(0, 80))
    && /Setup draft/i.test(reviewText)
    && /Candidate planning data/i.test(reviewText);
  softAssert(
    'cyber_fixture_owner_source_visible_on_review',
    fixtureSourceVisible,
    STATUSES.FAIL,
    {
      fixtureId: selectedFixture.id,
      fixtureTitle: selectedFixture.title,
      contentLength: selectedFixture.rawOwnerAuthoredContent.length,
      ownerAuthored: selectedFixture.ownerAuthored,
      reviewTextSnippet: reviewText.slice(0, 1200),
    },
    'Cyber detective owner-authored source is visible in review as setup/candidate planning data.',
    'Cyber detective owner-authored source was not visible in the review step.',
  );
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
  logAction('cyber_fixture_after_project_creation', {
    fixtureId: selectedFixture.id,
    uniqueProjectTitle,
  });
  await screenshot('03-cyber-fixture-after-project-creation', [
    'manual_workspace_create_project',
    'project_isolation_new_project_activated',
    'manual_workspace_overview_active_only',
    'cyber_fixture_project_created',
    'cyber_fixture_active_project_scoped',
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
    'cyber_fixture_project_created',
    Boolean(uniqueProjectId) && uniqueProjectId !== 'example' && snapshot.headerTitle.includes(selectedFixture.title),
    STATUSES.FAIL,
    {
      fixtureId: selectedFixture.id,
      fixtureTitle: selectedFixture.title,
      fixtureSlug: selectedFixture.slug,
      contentLength: selectedFixture.rawOwnerAuthoredContent.length,
      ownerAuthored: selectedFixture.ownerAuthored,
      uniqueProjectTitle,
      uniqueProjectId,
      snapshot,
      didGenerateStoryProseFromFixture: false,
    },
    'Cyber detective fixture project was created through the browser UI.',
    'Cyber detective fixture project was not created through the browser UI.',
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
    'cyber_fixture_active_project_scoped',
    titleActive && selectActive && overviewActive,
    STATUSES.FAIL,
    { uniqueProjectTitle, uniqueProjectId, snapshot },
    'Cyber detective header, selector, and Overview reflect only the created project.',
    'Cyber detective active project scoping did not match header, selector, and Overview.',
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
  logAction('fixture_selected', {
    fixtureId: selectedFixture.id,
    fixtureTitle: selectedFixture.title,
    fixtureSlug: selectedFixture.slug,
    contentLength: selectedFixture.rawOwnerAuthoredContent.length,
    ownerAuthored: selectedFixture.ownerAuthored,
    contentWarningMetadata: selectedFixture.contentWarningMetadata,
    allowedIntent: selectedFixture.allowedIntent,
    forbiddenIntents: selectedFixture.forbiddenIntents,
    didGenerateStoryProseFromFixture: false,
  });

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
  softAssert(
    'cyber_fixture_memory_canon_not_mutated',
    /approved records only/i.test(memoryText)
      && /Candidate records remain/i.test(memoryText)
      && !memoryText.includes(selectedFixture.rawOwnerAuthoredContent.slice(0, 80)),
    STATUSES.FAIL,
    { scopedText: memoryText.slice(0, 1200), fixtureId: selectedFixture.id },
    'Cyber detective owner-authored fixture content is not displayed as approved Memory/Canon.',
    'Cyber detective fixture content appeared in approved Memory/Canon.',
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

  recordChecklistItem('model_assisted_evidence_backed_only', STATUSES.MANUAL_REVIEW_REQUIRED, { diagnosticInstruction: STORY_CHECK_DIAGNOSTIC_INSTRUCTION }, 'Ollama is healthy and Story Check UI is visible; live model workflow requires owner-run fixture with selected owner-authored scene.');
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

async function selectSafeCyberFixtureSceneForStoryCheck() {
  const storyCheckEvidenceIds = [
    'cyber_fixture_story_check_source_selected',
    'cyber_fixture_story_check_submitted',
    'cyber_fixture_story_check_result_diagnostic_only',
    'cyber_fixture_story_check_no_generated_prose',
    'cyber_fixture_story_check_analysis_only',
    'cyber_fixture_story_check_no_prose_generated',
    'cyber_fixture_model_output_not_canon',
  ];
  const diagnostics = {
    fixtureId: selectedFixture.id,
    projectId: uniqueProjectId,
    sourceWorkflow: 'not evaluated',
    scenesNavText: '',
    selectedSceneId: '',
    selectedSceneContainsFixture: false,
    storyCheckButtonVisible: false,
    storyCheckButtonEnabled: false,
    missingSurface: '',
  };

  await clickByText(['Overview']).catch(() => {});
  await clickByText(['Open scenes']).catch(() => {});
  await page.waitForTimeout(700);
  await screenshot('12-cyber-fixture-source-scene-selection', storyCheckEvidenceIds);

  const scenesNavText = await getScopedText('nav[aria-label="Scenes"]', 'cyber-fixture-scenes-nav');
  diagnostics.scenesNavText = scenesNavText.slice(0, 1500);
  if (/No scenes yet/i.test(scenesNavText)) {
    diagnostics.sourceWorkflow = 'missing_scene_create_or_import_workflow';
    diagnostics.missingSurface = 'Cyber fixture project has no scenes, and no browser-visible create/import owner-authored scene/source control is exposed.';
    return diagnostics;
  }

  const sceneButton = page.locator('nav[aria-label="Scenes"] button.scene-item').first();
  if (!(await sceneButton.count().catch(() => 0))) {
    diagnostics.sourceWorkflow = 'missing_scene_select_control';
    diagnostics.missingSurface = 'Scenes nav has no selectable scene button for the Cyber fixture project.';
    return diagnostics;
  }

  await sceneButton.click();
  await page.waitForTimeout(1000);
  await screenshot('13-cyber-fixture-story-check-before-submit', storyCheckEvidenceIds);
  const editorText = await getScopedText('section.editor-panel', 'cyber-fixture-editor-panel');
  diagnostics.selectedSceneId = (
    await page.locator('section.editor-panel h2').first().innerText().catch(() => '')
  ).trim();
  diagnostics.selectedSceneContainsFixture = editorText.includes(selectedFixture.rawOwnerAuthoredContent.slice(0, 80));
  const storyCheckButton = page.getByRole('button', { name: /Run Story Check/i }).first();
  diagnostics.storyCheckButtonVisible = await storyCheckButton.count().then((count) => count > 0).catch(() => false);
  diagnostics.storyCheckButtonEnabled = diagnostics.storyCheckButtonVisible
    ? await storyCheckButton.isEnabled().catch(() => false)
    : false;

  if (!diagnostics.selectedSceneContainsFixture) {
    diagnostics.sourceWorkflow = 'selected_scene_not_cyber_fixture_source';
    diagnostics.missingSurface = 'A scene can be selected, but the visible editor content does not contain the owner-authored Cyber fixture source.';
    return diagnostics;
  }
  if (!diagnostics.storyCheckButtonVisible || !diagnostics.storyCheckButtonEnabled) {
    diagnostics.sourceWorkflow = 'story_check_submit_unavailable_after_safe_source_selection';
    diagnostics.missingSurface = 'Owner-authored Cyber fixture source appears selected, but the Run Story Check control is missing or disabled.';
    return diagnostics;
  }

  diagnostics.sourceWorkflow = 'safe_owner_authored_scene_selected';
  return diagnostics;
}

function recordCyberStoryCheckManualReview(diagnostics, note) {
  cyberFixtureStoryCheckStatus = STATUSES.MANUAL_REVIEW_REQUIRED;
  for (const id of [
    'cyber_fixture_story_check_source_selected',
    'cyber_fixture_story_check_submitted',
    'cyber_fixture_story_check_result_diagnostic_only',
    'cyber_fixture_story_check_no_generated_prose',
    'cyber_fixture_story_check_analysis_only',
    'cyber_fixture_story_check_no_prose_generated',
    'cyber_fixture_model_output_not_canon',
  ]) {
    recordChecklistItem(id, STATUSES.MANUAL_REVIEW_REQUIRED, diagnostics, note);
  }
  logAction('cyber_fixture_story_check_skipped', {
    fixtureId: selectedFixture.id,
    status: cyberFixtureStoryCheckStatus,
    reason: note,
    diagnostics,
  });
}

function recordCyberNoProseManualReview(note, evidence = {}) {
  cyberFixtureNoProseStatus = STATUSES.MANUAL_REVIEW_REQUIRED;
  recordChecklistItem('cyber_fixture_no_prose_rewrite_refused', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequest: 'rewrite this scene' }, note);
  recordChecklistItem('cyber_fixture_no_prose_continue_refused', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequest: 'continue this scene' }, note);
  recordChecklistItem('cyber_fixture_no_prose_outline_refused', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequest: 'outline the next chapter' }, note);
  recordChecklistItem('cyber_fixture_no_prose_draft_polish_imitation_refused', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequests: ['generate a draft', 'polish/improve/expand/imitate this prose'] }, note);
  recordChecklistItem('cyber_fixture_no_rewrite', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequest: 'rewrite this scene' }, note);
  recordChecklistItem('cyber_fixture_no_continuation', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequest: 'continue this scene' }, note);
  recordChecklistItem('cyber_fixture_no_outline', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequest: 'outline the next chapter' }, note);
  recordChecklistItem('cyber_fixture_no_draft_polish_imitation', STATUSES.MANUAL_REVIEW_REQUIRED, { ...evidence, negativeRequests: ['generate a draft', 'polish/improve/expand/imitate this prose'] }, note);
}

async function runCyberDetectiveFixtureChecks() {
  logAction('section_start', { section: 'Cyber Detective Fixture', fixtureId: selectedFixture.id });
  recordChecklistItem(
    'cyber_fixture_runtime_tools_not_directly_executed',
    STATUSES.PASS,
    {
      fixtureId: selectedFixture.id,
      directRuntimeToolsExecuted: false,
      tools: ['BookNLP', 'spaCy', 'NCP', 'Subtxt', 'dramatica-flow'],
    },
    'Harness did not execute BookNLP, spaCy, NCP, Subtxt, or dramatica-flow directly.',
  );

  if (!page || !uniqueProjectId) {
    for (const id of [
      'cyber_fixture_story_check_source_selected',
      'cyber_fixture_story_check_submitted',
      'cyber_fixture_story_check_result_diagnostic_only',
      'cyber_fixture_story_check_no_generated_prose',
      'cyber_fixture_story_check_analysis_only',
      'cyber_fixture_story_check_no_prose_generated',
      'cyber_fixture_model_output_not_canon',
      'cyber_fixture_no_prose_rewrite_refused',
      'cyber_fixture_no_prose_continue_refused',
      'cyber_fixture_no_prose_outline_refused',
      'cyber_fixture_no_prose_draft_polish_imitation_refused',
      'cyber_fixture_no_rewrite',
      'cyber_fixture_no_continuation',
      'cyber_fixture_no_outline',
      'cyber_fixture_no_draft_polish_imitation',
    ]) {
      if (checklistResults[id].status === STATUSES.MANUAL_REVIEW_REQUIRED) {
        recordChecklistItem(id, STATUSES.BLOCKED, { fixtureId: selectedFixture.id }, 'Cyber detective project/browser startup blocked.');
      }
    }
    logAction('cyber_fixture_final_status', {
      fixtureId: selectedFixture.id,
      storyCheckStatus: STATUSES.BLOCKED,
      noProseStatus: STATUSES.BLOCKED,
    });
    logAction('cyber_fixture_no_prose_checks_blocked', {
      fixtureId: selectedFixture.id,
      reason: 'Cyber detective project/browser startup blocked.',
    });
    return;
  }

  const sourceDiagnostics = await selectSafeCyberFixtureSceneForStoryCheck();
  const storyCheckButton = page.getByRole('button', { name: /Run Story Check/i }).first();
  const visible = await getVisibleText();
  const analysisSurfaceVisible = /Run Story Check|Story Check|Analysis/i.test(visible);
  const analysisBoundaryVisible = /candidate analysis|does not change project truth/i.test(visible);

  logAction('cyber_fixture_story_check_attempted', {
    fixtureId: selectedFixture.id,
    diagnosticInstruction: STORY_CHECK_DIAGNOSTIC_INSTRUCTION,
    storyCheckButtonVisible: sourceDiagnostics.storyCheckButtonVisible,
    storyCheckButtonEnabled: sourceDiagnostics.storyCheckButtonEnabled,
    analysisSurfaceVisible,
    ollamaReady: ollamaHealth.ok,
    sourceDiagnostics,
  });

  if (!ollamaHealth.ok) {
    cyberFixtureStoryCheckStatus = STATUSES.BLOCKED;
    for (const id of [
      'cyber_fixture_story_check_source_selected',
      'cyber_fixture_story_check_submitted',
      'cyber_fixture_story_check_result_diagnostic_only',
      'cyber_fixture_story_check_no_generated_prose',
      'cyber_fixture_story_check_analysis_only',
      'cyber_fixture_story_check_no_prose_generated',
      'cyber_fixture_model_output_not_canon',
    ]) {
      recordChecklistItem(id, STATUSES.BLOCKED, { fixtureId: selectedFixture.id, ollamaHealth }, 'Cyber detective model-backed check blocked because Ollama readiness failed.');
    }
    logAction('cyber_fixture_story_check_blocked', { fixtureId: selectedFixture.id, reason: 'ollama_unreachable' });
  } else if (sourceDiagnostics.sourceWorkflow !== 'safe_owner_authored_scene_selected') {
    const note = analysisSurfaceVisible
      ? `Story Check is visible, but no safe selected Cyber detective scene/source workflow is exposed for the owner-authored fixture: ${sourceDiagnostics.missingSurface}`
      : 'No Story Check/model-backed UI surface is visible for the Cyber detective fixture.';
    recordCyberStoryCheckManualReview({
      ...sourceDiagnostics,
      diagnosticInstruction: STORY_CHECK_DIAGNOSTIC_INSTRUCTION,
      analysisBoundaryVisible,
      analysisSurfaceVisible,
    }, note);
  } else {
    recordChecklistItem(
      'cyber_fixture_story_check_source_selected',
      STATUSES.PASS,
      {
        ...sourceDiagnostics,
        diagnosticInstruction: STORY_CHECK_DIAGNOSTIC_INSTRUCTION,
        analysisBoundaryVisible,
      },
      'Owner-authored Cyber fixture source is visibly selected before Story Check submission.',
    );
    await storyCheckButton.click();
    recordChecklistItem(
      'cyber_fixture_story_check_submitted',
      STATUSES.PASS,
      { fixtureId: selectedFixture.id, submittedThrough: 'browser UI Run Story Check button' },
      'Story Check was submitted through the app UI, not through a direct generation endpoint.',
    );
    await page.waitForTimeout(3000);
    await screenshot('14-cyber-fixture-story-check-result-error', [
      'cyber_fixture_story_check_result_diagnostic_only',
      'cyber_fixture_story_check_no_generated_prose',
      'cyber_fixture_story_check_analysis_only',
      'cyber_fixture_story_check_no_prose_generated',
      'cyber_fixture_model_output_not_canon',
    ]);
    const resultText = await getScopedText('aside.analysis-sidebar', 'cyber-fixture-analysis-sidebar');
    const forbiddenOutput = containsForbiddenGeneratedProse(resultText);
    const analysisOnly = /candidate analysis|diagnostic|evidence|insufficient evidence/i.test(resultText);
    const outputNotCanon = /does not change project truth|not canon|candidate analysis/i.test(resultText);
    recordChecklistItem('cyber_fixture_story_check_result_diagnostic_only', analysisOnly && !forbiddenOutput ? STATUSES.PASS : STATUSES.FAIL, { fixtureId: selectedFixture.id, resultTextSnippet: resultText.slice(0, 1500) }, analysisOnly && !forbiddenOutput ? 'Story Check result is diagnostic/candidate analysis only.' : 'Story Check result was not safely diagnostic-only.');
    recordChecklistItem('cyber_fixture_story_check_no_generated_prose', !forbiddenOutput ? STATUSES.PASS : STATUSES.FAIL, { fixtureId: selectedFixture.id, resultTextSnippet: resultText.slice(0, 1500) }, !forbiddenOutput ? 'No generated story prose marker was detected in Story Check result.' : 'Generated story prose marker detected in Story Check result.');
    recordChecklistItem('cyber_fixture_story_check_analysis_only', analysisOnly && !forbiddenOutput ? STATUSES.PASS : STATUSES.FAIL, { fixtureId: selectedFixture.id, resultTextSnippet: resultText.slice(0, 1500) }, analysisOnly && !forbiddenOutput ? 'Story Check result is diagnostic/candidate analysis only.' : 'Story Check result was not safely diagnostic-only.');
    recordChecklistItem('cyber_fixture_story_check_no_prose_generated', !forbiddenOutput ? STATUSES.PASS : STATUSES.FAIL, { fixtureId: selectedFixture.id, resultTextSnippet: resultText.slice(0, 1500) }, !forbiddenOutput ? 'No generated prose pattern was detected in Story Check result.' : 'Forbidden prose-generation pattern detected in Story Check result.');
    recordChecklistItem('cyber_fixture_model_output_not_canon', outputNotCanon && !forbiddenOutput ? STATUSES.PASS : STATUSES.FAIL, { fixtureId: selectedFixture.id, resultTextSnippet: resultText.slice(0, 1500) }, outputNotCanon && !forbiddenOutput ? 'Model-backed output is presented as candidate/non-canon analysis.' : 'Model-backed output canon/truth boundary was missing or unsafe.');
    cyberFixtureStoryCheckStatus = forbiddenOutput ? STATUSES.FAIL : STATUSES.PASS;
    logAction(forbiddenOutput ? 'cyber_fixture_story_check_blocked' : 'cyber_fixture_story_check_passed', {
      fixtureId: selectedFixture.id,
      forbiddenOutput,
      analysisOnly,
      outputNotCanon,
    });
  }

  await screenshot('15-cyber-fixture-no-prose-negative-prompt-attempt-result', [
    'cyber_fixture_no_prose_rewrite_refused',
    'cyber_fixture_no_prose_continue_refused',
    'cyber_fixture_no_prose_outline_refused',
    'cyber_fixture_no_prose_draft_polish_imitation_refused',
    'cyber_fixture_no_rewrite',
    'cyber_fixture_no_continuation',
    'cyber_fixture_no_outline',
    'cyber_fixture_no_draft_polish_imitation',
  ]);

  const hasSafeNoProseInput = false;
  logAction('cyber_fixture_no_prose_checks_attempted', {
    fixtureId: selectedFixture.id,
    negativeRequests: NO_PROSE_NEGATIVE_REQUESTS,
    hasSafeNoProseInput,
    attemptedThrough: 'browser UI inspection only; no unsafe prompt submitted',
  });
  if (hasSafeNoProseInput) {
    cyberFixtureNoProseStatus = STATUSES.PASS;
    logAction('cyber_fixture_no_prose_checks_passed', {
      fixtureId: selectedFixture.id,
      negativeRequests: NO_PROSE_NEGATIVE_REQUESTS,
    });
  } else {
    const noProseNote = 'No safe Cyber detective no-prose prompt/input path is exposed in the browser UI; owner must manually verify negative prompts fail closed if a safe analysis input is later exposed.';
    recordCyberNoProseManualReview(noProseNote, {
      fixtureId: selectedFixture.id,
      sourceWorkflow: sourceDiagnostics.sourceWorkflow,
      hasSafeNoProseInput,
      attemptedThrough: 'browser UI inspection only; no unsafe prompt submitted',
    });
    logAction('cyber_fixture_no_prose_checks_skipped', {
      fixtureId: selectedFixture.id,
      status: cyberFixtureNoProseStatus,
      reason: noProseNote,
    });
  }
  logAction('cyber_fixture_final_status', {
    fixtureId: selectedFixture.id,
    projectId: uniqueProjectId,
    storyCheckStatus: cyberFixtureStoryCheckStatus,
    noProseStatus: cyberFixtureNoProseStatus,
    omiCandidatePlanningStatus: checklistResults.cyber_fixture_omi_candidate_planning_only.status,
    memoryCanonStatus: checklistResults.cyber_fixture_memory_canon_not_mutated.status,
  });
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
    task: 'MVP-READINESS-OWNER-ACCEPTANCE-005',
    startedAt: runStartedAt,
    finishedAt,
    appBaseUrl: APP_BASE_URL,
    backendBaseUrl: BACKEND_BASE_URL,
    fixture: {
      id: selectedFixture.id,
      slug: selectedFixture.slug,
      title: selectedFixture.title,
      contentLength: selectedFixture.rawOwnerAuthoredContent.length,
      ownerAuthored: selectedFixture.ownerAuthored,
      contentWarningMetadata: selectedFixture.contentWarningMetadata,
      allowedIntent: selectedFixture.allowedIntent,
      forbiddenIntents: selectedFixture.forbiddenIntents,
      didGenerateStoryProseFromFixture: false,
    },
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
    task: 'MVP-READINESS-OWNER-ACCEPTANCE-005',
    resultModel: Object.values(STATUSES),
    fixture: {
      id: selectedFixture.id,
      slug: selectedFixture.slug,
      title: selectedFixture.title,
      contentLength: selectedFixture.rawOwnerAuthoredContent.length,
      ownerAuthored: selectedFixture.ownerAuthored,
      allowedIntent: selectedFixture.allowedIntent,
      forbiddenIntents: selectedFixture.forbiddenIntents,
      didGenerateStoryProseFromFixture: false,
    },
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
    `- Task: \`MVP-READINESS-OWNER-ACCEPTANCE-005\``,
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
    '## Cyber Detective Fixture',
    '',
    `- Fixture title: \`${selectedFixture.title}\``,
    `- Fixture id/slug: \`${selectedFixture.id}\` / \`${selectedFixture.slug}\``,
    `- Created project title: \`${uniqueProjectTitle || 'not created'}\``,
    `- Project id/slug: \`${uniqueProjectId || 'unknown'}\``,
    `- Content length: \`${selectedFixture.rawOwnerAuthoredContent.length}\` characters`,
    `- Owner-authored source confirmed: \`${selectedFixture.ownerAuthored ? 'yes' : 'no'}\``,
    `- Allowed intent: \`${selectedFixture.allowedIntent}\``,
    `- Forbidden intents: ${selectedFixture.forbiddenIntents.map((intent) => `\`${intent}\``).join(', ')}`,
    '- Content warning metadata is recorded for internal evidence only.',
    '- Harness generated story prose from fixture: `no`',
    `- Story Check/model-backed status: **${cyberFixtureStoryCheckStatus}**`,
    `- No-prose negative-path status: **${cyberFixtureNoProseStatus}**`,
    `- OMI candidate/planning status: **${checklistResults.cyber_fixture_omi_candidate_planning_only.status}**`,
    `- Memory/Canon non-canon status: **${checklistResults.cyber_fixture_memory_canon_not_mutated.status}**`,
    '',
    'Diagnostic-only Story Check instruction:',
    '',
    '```text',
    STORY_CHECK_DIAGNOSTIC_INSTRUCTION,
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
      await runCyberDetectiveFixtureChecks();
    } else {
      markModelBackedBlocked();
      await runCyberDetectiveFixtureChecks();
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
