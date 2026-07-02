#!/usr/bin/env node
/**
 * MVP-READINESS-BROWSER-EVIDENCE-001
 * Playwright browser evidence script for project isolation smoke testing.
 *
 * Captures screenshots, workflow log, and markdown report only.
 * Does not fix product behavior. Does not call models or extractors.
 *
 * Prerequisites:
 * - Backend already running (owner-started)
 * - Frontend dev server at APP_BASE_URL (default http://localhost:5173)
 * - Playwright installed under frontend/ (`npm install -D @playwright/test`)
 * - Chromium browser installed (`npx playwright install chromium`)
 *
 * Manual run (from repo root):
 *   node scripts/mvp-project-isolation-browser-smoke.mjs
 *
 * Alternative if module resolution fails:
 *   NODE_PATH=frontend/node_modules node scripts/mvp-project-isolation-browser-smoke.mjs
 *
 * Optional env:
 *   APP_BASE_URL=http://localhost:5173
 *   MVP_EVIDENCE_DIR=artifacts/mvp-readiness/project-isolation
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..');
const FRONTEND_NODE_MODULES = path.join(REPO_ROOT, 'frontend', 'node_modules');

const APP_BASE_URL = process.env.APP_BASE_URL ?? 'http://localhost:5173';
const MVP_EVIDENCE_DIR = path.resolve(
  process.env.MVP_EVIDENCE_DIR ?? 'artifacts/mvp-readiness/project-isolation',
);

const SETUP_IDEA_TEXT =
  'Owner-authored setup idea for project isolation evidence. This is not canon, not memory, and not generated prose.';
const SETUP_NOTES_TEXT = 'Owner-authored setup notes for browser smoke evidence.';

const EXAMPLE_LEAKAGE_MARKERS = Object.freeze([
  'The Princess and the Pea',
  'scene_001',
]);

/** @type {Array<{ ts: string, action: string, [key: string]: unknown }>} */
const workflowLog = [];

/** @type {Array<{ name: string, blockerLabel: string, details: Record<string, unknown>, ts: string }>} */
const blockers = [];

let evidenceDir = MVP_EVIDENCE_DIR;
let screenshotDir = path.join(evidenceDir, 'screenshots');
/** @type {import('playwright').Page | null} */
let page = null;
let toolingBlocked = false;
let toolingError = null;
let uniqueProjectTitle = '';
let runStartedAt = new Date().toISOString();

function logAction(action, details = {}) {
  const entry = {
    ts: new Date().toISOString(),
    action,
    ...details,
  };
  workflowLog.push(entry);
  const suffix = Object.keys(details).length > 0 ? ` ${JSON.stringify(details)}` : '';
  console.log(`[ACTION] ${action}${suffix}`);
}

function softAssert(name, condition, blockerLabel, details = {}) {
  logAction('soft_assert', {
    name,
    passed: Boolean(condition),
    blockerLabel,
    ...details,
  });
  if (!condition) {
    const blocker = {
      name,
      blockerLabel,
      details,
      ts: new Date().toISOString(),
    };
    blockers.push(blocker);
    console.log(`[BLOCKER] ${blockerLabel}: ${name}`);
  }
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
      const moduleUrl = pathToFileURL(candidate).href;
      const mod = await import(moduleUrl);
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
    `Playwright not found under frontend/node_modules. Install with: cd frontend && npm install -D @playwright/test && npx playwright install chromium. Last error: ${lastError instanceof Error ? lastError.message : String(lastError)}`,
  );
}

async function screenshot(stepName) {
  if (!page) {
    throw new Error('screenshot called before page initialized');
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
  return filePath;
}

async function getVisibleText() {
  if (!page) {
    return '';
  }

  const text = await page.locator('body').innerText();
  logAction('get_visible_text', { length: text.length });
  return text;
}

async function getActiveProjectText() {
  if (!page) {
    return { headerTitle: '', selectValue: '', selectLabel: '', overviewProjectId: '' };
  }

  const headerTitle = (
    await page.locator('.project-nav .panel-header h1').first().innerText().catch(() => '')
  ).trim();
  const select = page.locator('select.project-select, select[aria-label="Select project"]').first();
  const selectValue = (await select.inputValue().catch(() => '')).trim();
  const selectedOptionText = (
    await select.locator(`option[value="${selectValue}"]`).innerText().catch(async () => {
      const selected = select.locator('option:checked');
      return selected.count().then((count) => (count ? selected.innerText() : ''));
    })
  ).trim();
  const overviewProjectId = (
    await page
      .locator('.project-overview dt:has-text("Project ID") + dd')
      .first()
      .innerText()
      .catch(() => '')
  ).trim();

  const snapshot = {
    headerTitle,
    selectValue,
    selectLabel: selectedOptionText,
    overviewProjectId,
  };
  logAction('get_active_project_text', snapshot);
  return snapshot;
}

async function getScenesNavText() {
  if (!page) {
    return '';
  }

  const text = await page.locator('nav[aria-label="Scenes"]').innerText().catch(() => '');
  logAction('get_scenes_nav_text', { length: text.length });
  return text;
}

async function getActiveOmiMemoryText() {
  if (!page) {
    return '';
  }

  const candidates = [
    { name: 'memory-canon-shell', locator: page.locator('section.memory-canon-shell') },
    { name: 'memory-canon-region', locator: page.getByRole('region', { name: /memory\s*\/\s*canon/i }) },
    { name: 'omi-panel', locator: page.locator('section.omi-panel, [aria-label="OMI"]') },
    { name: 'project-workspace', locator: page.locator('main.editor-column[aria-label="Project workspace"]') },
  ];

  for (const candidate of candidates) {
    const count = await candidate.locator.count().catch(() => 0);
    if (count === 0) {
      continue;
    }

    const text = await candidate.locator.first().innerText().catch(() => '');
    if (text.trim()) {
      logAction('get_active_omi_memory_text', {
        scope: candidate.name,
        length: text.length,
      });
      return text;
    }
  }

  const fallbackText = await getVisibleText();
  logAction('get_active_omi_memory_text_fallback', {
    scope: 'body',
    length: fallbackText.length,
  });
  return fallbackText;
}

/**
 * @param {string[]} candidates
 */
async function clickByText(candidates) {
  if (!page) {
    throw new Error('clickByText called before page initialized');
  }

  for (const candidate of candidates) {
    const exact = page.getByRole('button', { name: candidate, exact: true });
    if (await exact.count()) {
      await exact.first().click();
      logAction('click_by_text', { candidate, strategy: 'button-exact' });
      return candidate;
    }

    const looseButton = page.getByRole('button', { name: new RegExp(candidate, 'i') });
    if (await looseButton.count()) {
      await looseButton.first().click();
      logAction('click_by_text', { candidate, strategy: 'button-regex' });
      return candidate;
    }

    const link = page.getByRole('link', { name: new RegExp(candidate, 'i') });
    if (await link.count()) {
      await link.first().click();
      logAction('click_by_text', { candidate, strategy: 'link-regex' });
      return candidate;
    }

    const textMatch = page.getByText(new RegExp(`^${escapeRegExp(candidate)}$`, 'i'));
    if (await textMatch.count()) {
      await textMatch.first().click();
      logAction('click_by_text', { candidate, strategy: 'text-exact' });
      return candidate;
    }
  }

  const error = new Error(`Unable to click any candidate: ${candidates.join(', ')}`);
  logAction('click_by_text_failed', { candidates, message: error.message });
  throw error;
}

/**
 * @param {string[]} candidates
 * @param {string} value
 */
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

    const byPlaceholder = page.getByPlaceholder(new RegExp(candidate, 'i'));
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

  const error = new Error(`Unable to fill any candidate: ${candidates.join(', ')}`);
  logAction('fill_first_matching_failed', { candidates, message: error.message });
  throw error;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function containsExampleLeakage(text) {
  return EXAMPLE_LEAKAGE_MARKERS.some((marker) => text.includes(marker));
}

function containsApprovedCanonMislabel(text) {
  const lower = text.toLowerCase();
  const hasSetupCandidateContext =
    lower.includes('setup candidate') ||
    lower.includes('candidate planning data') ||
    lower.includes('owner-authored setup');

  if (!hasSetupCandidateContext) {
    return false;
  }

  const mislabelPatterns = [
    /approved memory/i,
    /approved canon/i,
    /approved project truth/i,
    /canon record/i,
  ];

  return mislabelPatterns.some((pattern) => pattern.test(text));
}

async function ensureEvidenceDirs() {
  await fs.mkdir(screenshotDir, { recursive: true });
  logAction('ensure_evidence_dir', { evidenceDir, screenshotDir });
}

async function writeEvidenceArtifacts(resultLabel, exitCode) {
  const workflowPath = path.join(evidenceDir, 'workflow-log.json');
  const reportPath = path.join(evidenceDir, 'evidence-report.md');

  const payload = {
    task: 'MVP-READINESS-BROWSER-EVIDENCE-001',
    startedAt: runStartedAt,
    finishedAt: new Date().toISOString(),
    appBaseUrl: APP_BASE_URL,
    evidenceDir,
    uniqueProjectTitle,
    result: resultLabel,
    exitCode,
    toolingBlocked,
    toolingError,
    blockers,
    actions: workflowLog,
  };

  await fs.writeFile(workflowPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');

  const reportLines = [
    '# MVP Project Isolation Browser Evidence Report',
    '',
    `- Task: \`MVP-READINESS-BROWSER-EVIDENCE-001\``,
    `- Result: **${resultLabel}**`,
    `- Exit code: \`${exitCode}\``,
    `- App base URL: \`${APP_BASE_URL}\``,
    `- Evidence directory: \`${evidenceDir}\``,
    `- Unique project title: \`${uniqueProjectTitle}\``,
    `- Started: \`${runStartedAt}\``,
    `- Finished: \`${payload.finishedAt}\``,
    '',
    '## Browser Tool',
    '',
    '- Playwright Chromium (imported from `frontend/node_modules`)',
    '',
    '## Manual Command',
    '',
    '```bash',
    '# From repo root, with backend + frontend already running:',
    'node scripts/mvp-project-isolation-browser-smoke.mjs',
    '',
    '# Alternative module resolution:',
    'NODE_PATH=frontend/node_modules node scripts/mvp-project-isolation-browser-smoke.mjs',
    '',
    '# Optional overrides:',
    'APP_BASE_URL=http://localhost:5173 MVP_EVIDENCE_DIR=artifacts/mvp-readiness/project-isolation node scripts/mvp-project-isolation-browser-smoke.mjs',
    '```',
    '',
    '## Blockers',
    '',
  ];

  if (blockers.length === 0) {
    reportLines.push('- None');
  } else {
    for (const blocker of blockers) {
      reportLines.push(
        `- \`${blocker.blockerLabel}\` — ${blocker.name} (${JSON.stringify(blocker.details)})`,
      );
    }
  }

  reportLines.push('', '## Screenshots', '');
  try {
    const files = (await fs.readdir(screenshotDir)).filter((name) => name.endsWith('.png')).sort();
    if (files.length === 0) {
      reportLines.push('- None captured');
    } else {
      for (const file of files) {
        reportLines.push(`- \`${path.join('screenshots', file)}\``);
      }
    }
  } catch {
    reportLines.push('- Screenshot directory unavailable');
  }

  reportLines.push('', '## Workflow Log', '', `- JSON artifact: \`workflow-log.json\``);
  reportLines.push('', '## Safety Notes', '');
  reportLines.push('- Evidence-only script; no product fix attempted.');
  reportLines.push('- No Ollama/model calls.');
  reportLines.push('- No BookNLP/spaCy execution.');
  reportLines.push('- No NCP/Subtxt/dramatica-flow execution.');
  reportLines.push('- Writes limited to MVP_EVIDENCE_DIR.');

  await fs.writeFile(reportPath, `${reportLines.join('\n')}\n`, 'utf8');
  logAction('write_evidence_artifacts', { workflowPath, reportPath, resultLabel, exitCode });
}

async function waitForAppReady() {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    logAction('networkidle_timeout_ignored');
  });
  await page.locator('.app-shell, .project-nav').first().waitFor({ state: 'visible', timeout: 20000 });
}

async function runWorkflow() {
  uniqueProjectTitle = `MVP Isolation Test ${Date.now()}`;
  logAction('workflow_start', { uniqueProjectTitle, appBaseUrl: APP_BASE_URL });

  logAction('navigate', { url: APP_BASE_URL });
  await page.goto(APP_BASE_URL, { waitUntil: 'domcontentloaded' });
  await waitForAppReady();
  await screenshot('01-initial-load');

  const initialText = await getVisibleText();
  const initialProject = await getActiveProjectText();
  logAction('record_initial_state', {
    initialProject,
    visibleTextLength: initialText.length,
  });

  logAction('omi_guided_setup_begin');
  await fillFirstMatching(
    ['OMI-guided project title', 'Project title', 'Owner project title'],
    uniqueProjectTitle,
  );
  await fillFirstMatching(['Owner-authored setup idea'], SETUP_IDEA_TEXT);
  await fillFirstMatching(['Owner-authored setup notes'], SETUP_NOTES_TEXT);

  const setupText = await getVisibleText();
  softAssert(
    'setup_candidate_labels_visible_on_setup_step',
    setupText.includes('Setup candidate') &&
      setupText.includes('Candidate planning data, not approved project truth'),
    'candidate_setup_not_visible',
    { snippet: setupText.slice(0, 500) },
  );

  await clickByText(['Review before creating project']);
  await screenshot('02-review-before-create');

  const reviewText = await getVisibleText();
  softAssert(
    'owner_setup_idea_visible_on_review',
    reviewText.includes(SETUP_IDEA_TEXT),
    'owner_setup_candidate_not_project_scoped',
    { field: 'rawIdea' },
  );
  softAssert(
    'owner_setup_notes_visible_on_review',
    reviewText.includes(SETUP_NOTES_TEXT),
    'owner_setup_candidate_not_project_scoped',
    { field: 'setupNotes' },
  );
  softAssert(
    'review_shows_unique_project_title',
    reviewText.includes(uniqueProjectTitle),
    'project_activation_mismatch',
    { expectedTitle: uniqueProjectTitle },
  );

  const confirmCheckbox = page.getByRole('checkbox', {
    name: /confirm this owner-authored setup can create a project/i,
  });
  if (await confirmCheckbox.count()) {
    await confirmCheckbox.first().check();
    logAction('check_final_confirmation');
  } else {
    softAssert(
      'final_confirmation_checkbox_present',
      false,
      'mvp_manual_readiness_blocked',
      { reason: 'Final confirmation checkbox not found on review step' },
    );
  }

  await clickByText(['Create project']);
  await page.waitForTimeout(1000);
  await waitForAppReady();
  await screenshot('03-after-project-creation');

  const activeProject = await getActiveProjectText();

  const activeProjectCombined = `${activeProject.headerTitle} ${activeProject.selectValue} ${activeProject.selectLabel} ${activeProject.overviewProjectId}`;

  softAssert(
    'active_project_title_matches_unique_title',
    activeProjectCombined.includes(uniqueProjectTitle),
    'project_activation_mismatch',
    { activeProject, expectedTitle: uniqueProjectTitle },
  );

  softAssert(
    'active_project_id_is_not_example',
    activeProject.selectValue !== 'example' && activeProject.selectValue.length > 0,
    'example_project_leakage',
    { activeProject },
  );

  if (activeProject.overviewProjectId) {
    softAssert(
      'overview_project_id_is_not_example',
      activeProject.overviewProjectId !== 'example',
      'example_project_leakage',
      { overviewProjectId: activeProject.overviewProjectId },
    );
  }

  softAssert(
    'post_create_header_not_still_example_only',
    activeProject.headerTitle.includes(uniqueProjectTitle) ||
      !activeProject.headerTitle.includes('The Princess and the Pea'),
    'project_activation_mismatch',
    { headerTitle: activeProject.headerTitle },
  );

  logAction('open_scenes_workspace');
  try {
    await clickByText(['Open scenes']);
    await page.waitForTimeout(500);
  } catch (error) {
    logAction('open_scenes_fallback', { message: error instanceof Error ? error.message : String(error) });
  }

  await screenshot('04-scenes-workspace');

  const scenesNavText = await getScenesNavText();
  const scenesWorkspaceText = await page
    .locator('main.editor-column, .project-overview')
    .innerText()
    .catch(async () => getVisibleText());

  softAssert(
    'scenes_nav_no_princess_and_pea',
    !scenesNavText.includes('The Princess and the Pea'),
    'example_project_leakage',
    { view: 'scenes-nav' },
  );
  softAssert(
    'scenes_nav_no_scene_001_leak',
    !scenesNavText.includes('scene_001'),
    'hardcoded_scene_route',
    { view: 'scenes-nav' },
  );
  softAssert(
    'scenes_workspace_no_example_scene_content',
    !scenesWorkspaceText.includes('scene_001') &&
      !scenesWorkspaceText.includes('The Princess and the Pea'),
    'example_project_leakage',
    { view: 'scenes-workspace' },
  );

  const hasEmptyScenesState =
    scenesNavText.includes('No scenes yet.') ||
    scenesWorkspaceText.includes('No scenes yet.') ||
    scenesWorkspaceText.includes('0 scenes');
  const hasUnexpectedSceneButtons = await page
    .locator('nav[aria-label="Scenes"] .scene-item')
    .count();

  if (hasUnexpectedSceneButtons === 0) {
    softAssert(
      'new_project_shows_empty_scenes_state',
      hasEmptyScenesState,
      'new_project_empty_scenes_missing_state',
      { hasEmptyScenesState, sceneButtonCount: hasUnexpectedSceneButtons },
    );
  } else {
    softAssert(
      'new_project_scene_list_has_no_example_scene_items',
      !containsExampleLeakage(`${scenesNavText}\n${scenesWorkspaceText}`),
      'hardcoded_scene_route',
      { sceneButtonCount: hasUnexpectedSceneButtons },
    );
  }

  logAction('open_memory_or_omi');
  let openedMemoryOrOmi = false;

  try {
    await clickByText(['Memory / Canon', 'Memory/Canon']);
    openedMemoryOrOmi = true;
  } catch {
    try {
      await clickByText(['Open OMI', 'OMI']);
      openedMemoryOrOmi = true;
    } catch (error) {
      softAssert(
        'memory_or_omi_navigation_available',
        false,
        'mvp_manual_readiness_blocked',
        {
          reason: error instanceof Error ? error.message : String(error),
        },
      );
    }
  }

  await page.waitForTimeout(500);
  await screenshot('05-omi-or-memory-canon');

  const omiMemoryText = await getActiveOmiMemoryText();
  softAssert(
    'omi_memory_view_no_princess_and_pea',
    !omiMemoryText.includes('The Princess and the Pea'),
    'omi_cross_project_data_leakage',
    { view: 'omi-or-memory' },
  );
  softAssert(
    'omi_memory_view_no_scene_001',
    !omiMemoryText.includes('scene_001'),
    'omi_cross_project_data_leakage',
    { view: 'omi-or-memory' },
  );
  softAssert(
    'omi_memory_view_no_unrelated_example_project_data',
    !(
      containsExampleLeakage(omiMemoryText) &&
      !omiMemoryText.includes(uniqueProjectTitle)
    ),
    'omi_cross_project_data_leakage',
    { openedMemoryOrOmi },
  );

  softAssert(
    'setup_candidate_not_labeled_approved_memory_or_canon',
    !containsApprovedCanonMislabel(omiMemoryText),
    'candidate_setup_not_visible',
    { view: 'omi-or-memory' },
  );

  if (openedMemoryOrOmi && omiMemoryText.toLowerCase().includes('memory / canon')) {
    softAssert(
      'memory_canon_shell_shows_approved_only_boundary',
      omiMemoryText.includes('Approved-only') ||
        omiMemoryText.includes('No approved') ||
        omiMemoryText.includes('not canon here'),
      'candidate_setup_not_visible',
      { note: 'Memory/Canon boundary copy expected for approved-only shell' },
    );
  }

  logAction('workflow_complete', {
    blockerCount: blockers.length,
    openedMemoryOrOmi,
  });
}

async function main() {
  runStartedAt = new Date().toISOString();
  evidenceDir = MVP_EVIDENCE_DIR;
  screenshotDir = path.join(evidenceDir, 'screenshots');

  let browser = null;
  let exitCode = 0;
  let resultLabel = 'PASS';

  try {
    await ensureEvidenceDirs();
    const chromium = await loadPlaywrightChromium();

    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1024 },
    });
    page = await context.newPage();

    page.on('dialog', async (dialog) => {
      logAction('dialog', { type: dialog.type(), message: dialog.message() });
      await dialog.accept();
    });

    await runWorkflow();

    if (blockers.length > 0) {
      exitCode = 1;
      resultLabel = 'BLOCKED';
    } else {
      exitCode = 0;
      resultLabel = 'PASS';
    }
  } catch (error) {
    toolingBlocked = true;
    toolingError = error instanceof Error ? error.message : String(error);
    exitCode = 2;
    resultLabel = 'BLOCKED';
    logAction('tooling_or_app_blocked', { error: toolingError });

    if (page) {
      await screenshot('99-tooling-or-app-blocked').catch(() => {});
    }
  } finally {
    if (browser) {
      await browser.close().catch(() => {});
    }

    try {
      await writeEvidenceArtifacts(resultLabel, exitCode);
    } catch (writeError) {
      console.error(
        `[ERROR] Failed to write evidence artifacts: ${
          writeError instanceof Error ? writeError.message : String(writeError)
        }`,
      );
      if (exitCode === 0) {
        exitCode = 2;
      }
    }

    console.log(`[RESULT] ${resultLabel} (exit ${exitCode})`);
    console.log(`[EVIDENCE] ${evidenceDir}`);
    process.exitCode = exitCode;
  }
}

main();
