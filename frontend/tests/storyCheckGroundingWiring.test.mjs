import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

const frontendRoot = fileURLToPath(new URL('../', import.meta.url));
const vite = await createServer({
  root: frontendRoot,
  appType: 'custom',
  logLevel: 'silent',
  server: { middlewareMode: true },
});
const sidebarModule = await vite.ssrLoadModule('/src/components/AnalysisSidebar.jsx');
const {
  default: AnalysisSidebar,
  getGroundedStoryCheckDiagnostics,
  getGroundingPresentationState,
} = sidebarModule;

test.after(async () => {
  await vite.close();
});

const sourceIdentity = {
  project_id: 'example',
  source_id: 'scene_001',
  source_type: 'scene',
  source_kind: 'owner-authored source',
  source_sha256: 'a'.repeat(64),
  utf8_byte_length: 20,
  hash_algorithm: 'sha256',
  hash_basis: 'utf-8-exact',
};

function evidence(excerpt = 'Exact factual claim') {
  return {
    source_id: sourceIdentity.source_id,
    source_sha256: sourceIdentity.source_sha256,
    start_byte: 0,
    end_byte: 19,
    excerpt,
    offset_basis: 'utf-8-bytes-zero-based-half-open',
  };
}

function diagnostic({
  id,
  classification,
  message,
  state,
  outcome,
  evidenceItems = [],
  directEvidenceMatched = false,
}) {
  return {
    diagnostic_id: id,
    classification,
    message,
    source_identity: sourceIdentity,
    verification_state: state,
    validator_result: {
      outcome,
      reason_codes: outcome === 'supported'
        ? ['exact_evidence_matched']
        : ['validation_not_applicable'],
      direct_evidence_matched: directEvidenceMatched,
    },
    evidence: evidenceItems,
  };
}

function groundedReport(diagnostics) {
  return {
    coherence_score: 6,
    warnings: ['Exact factual claim'],
    suggestions: ['What remains uncertain?'],
    grounding: {
      status: 'completed',
      contract_version: 'story-check-grounding-contract.v1',
      source_identity: sourceIdentity,
      diagnostics,
      boundary: { analytical_output: true, non_canon: true, owner_approved: false },
    },
  };
}

function render(report, overrides = {}) {
  return renderToStaticMarkup(React.createElement(AnalysisSidebar, {
    report,
    selectedSceneId: 'scene_001',
    selectedStoryCheckSourceId: 'scene_001',
    selectedStoryCheckSource: {
      source_id: 'scene_001',
      source_kind: 'owner-authored source',
    },
    rawArtifactEvidenceStatus: {},
    isAnalyzing: false,
    onRunStoryCheck: () => {},
    ...overrides,
  }));
}

test('verified, unverified, and quarantined diagnostics render in distinct labeled groups', () => {
  const report = groundedReport([
    diagnostic({
      id: 'verified-1',
      classification: 'factual_warning',
      message: 'Exact factual claim',
      state: 'verified',
      outcome: 'supported',
      evidenceItems: [evidence()],
      directEvidenceMatched: true,
    }),
    diagnostic({
      id: 'unverified-1',
      classification: 'question',
      message: 'What remains uncertain?',
      state: 'unverified',
      outcome: 'not_applicable',
    }),
    diagnostic({
      id: 'quarantined-1',
      classification: 'factual_warning',
      message: 'Unsupported factual warning',
      state: 'quarantined',
      outcome: 'unsupported',
    }),
  ]);
  const html = render(report);

  for (const text of [
    'Verified Findings',
    'Unverified Diagnostics',
    'Quarantined Factual Warnings',
    'Status: verified',
    'Status: unverified',
    'Status: quarantined',
    'Exact factual claim',
    'What remains uncertain?',
    'Unsupported factual warning',
  ]) {
    assert.match(html, new RegExp(text));
  }
  assert.match(html, /Quarantined output is unsupported or mismatched model output/);
});

test('source identity and exact evidence details are accessible and bounded', () => {
  const report = groundedReport([diagnostic({
    id: 'verified-1',
    classification: 'factual_warning',
    message: 'Exact factual claim',
    state: 'verified',
    outcome: 'supported',
    evidenceItems: [evidence()],
    directEvidenceMatched: true,
  })]);
  const html = render(report);

  assert.match(html, /Source and evidence details/);
  assert.match(html, /scene_001/);
  assert.match(html, new RegExp('a'.repeat(64)));
  assert.match(html, /Exact UTF-8 evidence 1/);
  assert.match(html, /Bytes 0–19/);
  assert.match(html, /utf-8-bytes-zero-based-half-open/);
});

test('malformed verified or legacy responses cannot default to verified', () => {
  const malformed = diagnostic({
    id: 'malformed-1',
    classification: 'factual_warning',
    message: 'Malformed verified warning',
    state: 'verified',
    outcome: 'supported',
    evidenceItems: [],
    directEvidenceMatched: true,
  });
  assert.equal(getGroundingPresentationState(malformed, sourceIdentity), 'quarantined');
  assert.equal(getGroundedStoryCheckDiagnostics({ warnings: ['legacy'] }).length, 0);

  const malformedHtml = render(groundedReport([malformed]));
  assert.match(malformedHtml, /Status: quarantined/);
  assert.match(malformedHtml, /Malformed verified warning/);

  const legacyHtml = render({ warnings: ['[Factual] Legacy warning'], suggestions: [] });
  assert.match(legacyHtml, /Legacy Ungrounded Output/);
  assert.match(legacyHtml, /Status: unverified/);
  assert.doesNotMatch(legacyHtml, /Status: verified/);
});

test('missing verification fields and unknown states cannot render as verified', () => {
  const missingFields = {
    diagnostic_id: 'missing-fields',
    classification: 'observation',
    message: 'Missing verification fields',
    evidence: [],
  };
  const unknownState = {
    ...diagnostic({
      id: 'unknown-state',
      classification: 'factual_warning',
      message: 'Unknown verification state',
      state: 'future_state',
      outcome: 'supported',
      evidenceItems: [evidence()],
      directEvidenceMatched: true,
    }),
  };

  assert.equal(getGroundingPresentationState(missingFields, sourceIdentity), 'unverified');
  assert.equal(getGroundingPresentationState(unknownState, sourceIdentity), 'unverified');
  const html = render(groundedReport([missingFields, unknownState]));
  assert.match(html, /Missing verification fields/);
  assert.match(html, /Unknown verification state/);
  assert.match(html, /Status: unverified/);
  assert.doesNotMatch(html, /Status: verified/);
});

test('current loading and error states remain visible', () => {
  assert.match(render(null, { isAnalyzing: true }), /Analyzing\.\.\./);
  const errorHtml = render({ error: 'Story check failed.' });
  assert.match(errorHtml, /Story Check Error/);
  assert.match(errorHtml, /Story check failed\./);
});
