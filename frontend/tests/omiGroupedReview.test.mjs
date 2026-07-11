import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildGroupedReviewModel,
  OMI_TOOL_ASSISTED_SOURCE,
  selectLinkedReviewCandidates,
} from '../src/omiGroupedReview.js';

const SOURCE_ID = 'idea_source';

function candidate({
  id,
  sourceIdeaId = SOURCE_ID,
  source = OMI_TOOL_ASSISTED_SOURCE,
  adapter = 'ncp',
  findingType = 'story_fact',
  storageType = 'project_bible_candidate',
  normalizedFindingId = `finding-${id}`,
  decision = 'pending',
  reviewStatus = 'candidate_review_pending',
  uncertaintyLabel = null,
  conflictGroupId = null,
  extractedClaim = `Claim ${id}`,
} = {}) {
  return {
    candidate_id: id,
    candidate_type: storageType,
    owner_decision: { decision, approved: decision === 'approve' },
    review_status: reviewStatus,
    promotion_status: { eligible: false, promotion_id: null },
    candidate_content: {
      source,
      source_idea_id: sourceIdeaId,
      source_adapter: adapter,
      tool_source: adapter,
      candidate_type: findingType,
      label: `Label ${id}`,
      name: `Name ${id}`,
      extracted_claim: extractedClaim,
      evidence: [{ source_excerpt: `Evidence ${id}`, source_locator: `source:${id}` }],
      source_locator: `source:${id}`,
      provenance: { adapter, tool_source: adapter, support: 'Support only' },
      support_label: 'Support only',
      confidence: 'medium support',
      uncertainty_label: uncertaintyLabel,
      conflict_group_id: conflictGroupId,
      duplicate_metadata: { duplicate_of: ['finding-other'], related_finding_ids: ['finding-other'] },
      raw_finding_id: `raw-${id}`,
      normalized_finding_id: normalizedFindingId,
      candidate_fingerprint: `candidate-fingerprint-${id}`,
      evidence_fingerprint: `evidence-fingerprint-${id}`,
    },
  };
}

function data(...candidates) {
  return {
    ideas: [{ idea_id: SOURCE_ID, linked_candidate_ids: candidates.map((item) => item.candidate_id) }],
    candidates,
  };
}

test('missing or malformed input fails closed', () => {
  assert.deepEqual(selectLinkedReviewCandidates(null, SOURCE_ID), []);
  assert.deepEqual(selectLinkedReviewCandidates({}, SOURCE_ID), []);
  assert.deepEqual(selectLinkedReviewCandidates(data(), '../unsafe'), []);

  const model = buildGroupedReviewModel({ ideas: 'not-an-array', candidates: [] }, { sourceIdeaId: SOURCE_ID });
  assert.equal(model.totalCount, 0);
  assert.equal(model.sourceIdeaId, SOURCE_ID);
});

test('selection excludes unlinked and non-tool-assisted candidates', () => {
  const linked = candidate({ id: 'candidate-linked' });
  const outside = candidate({ id: 'candidate-outside' });
  const otherSource = candidate({ id: 'candidate-other-source', source: 'manual_owner_entry' });
  const omiData = data(linked, otherSource, outside);
  omiData.ideas[0].linked_candidate_ids = ['candidate-other-source', 'candidate-linked'];

  assert.deepEqual(
    selectLinkedReviewCandidates(omiData, SOURCE_ID).map((item) => item.candidate_id),
    ['candidate-linked'],
  );
});

test('selection and model do not mutate inputs', () => {
  const omiData = data(candidate({ id: 'candidate-one' }));
  const before = structuredClone(omiData);

  selectLinkedReviewCandidates(omiData, SOURCE_ID);
  buildGroupedReviewModel(omiData, { sourceIdeaId: SOURCE_ID });

  assert.deepEqual(omiData, before);
});

test('primary grouping uses source adapter and secondary counts use original finding type', () => {
  const model = buildGroupedReviewModel(data(
    candidate({ id: 'candidate-a', adapter: 'spacy', findingType: 'character', storageType: 'project_bible_candidate' }),
    candidate({ id: 'candidate-b', adapter: 'spacy', findingType: 'location', storageType: 'project_bible_candidate' }),
    candidate({ id: 'candidate-c', adapter: 'ncp', findingType: 'character', storageType: 'project_bible_candidate' }),
  ), { sourceIdeaId: SOURCE_ID });

  assert.deepEqual(model.groups.map((group) => group.sourceAdapter), ['ncp', 'spacy']);
  assert.deepEqual(model.groups[1].candidateTypes, [
    { candidateType: 'character', count: 1 },
    { candidateType: 'location', count: 1 },
  ]);
});

test('groups and candidates sort deterministically', () => {
  const model = buildGroupedReviewModel(data(
    candidate({ id: 'candidate-c', adapter: 'spacy', findingType: 'location', normalizedFindingId: 'finding-z' }),
    candidate({ id: 'candidate-b', adapter: 'spacy', findingType: 'character', normalizedFindingId: 'finding-z' }),
    candidate({ id: 'candidate-a', adapter: 'spacy', findingType: 'character', normalizedFindingId: 'finding-a' }),
    candidate({ id: 'candidate-d', adapter: 'ncp', findingType: 'story_fact' }),
  ), { sourceIdeaId: SOURCE_ID });

  assert.deepEqual(model.groups.map((group) => group.sourceAdapter), ['ncp', 'spacy']);
  assert.deepEqual(
    model.groups[1].candidates.map((item) => item.candidateId),
    ['candidate-a', 'candidate-b', 'candidate-c'],
  );
});

test('pending and reviewed counts derive from owner decision and review metadata only', () => {
  const model = buildGroupedReviewModel(data(
    candidate({ id: 'candidate-pending', decision: 'pending', reviewStatus: 'candidate_review_pending' }),
    candidate({ id: 'candidate-reviewed', decision: 'approve', reviewStatus: 'owner_review' }),
    candidate({ id: 'candidate-status-pending', decision: 'reject', reviewStatus: 'review_pending' }),
  ), { sourceIdeaId: SOURCE_ID });

  assert.equal(model.pendingCount, 2);
  assert.equal(model.reviewedCount, 1);
});

test('uncertainty and conflict counts are deterministic', () => {
  const model = buildGroupedReviewModel(data(
    candidate({ id: 'candidate-a', uncertaintyLabel: 'insufficient_evidence', conflictGroupId: 'conflict-1' }),
    candidate({ id: 'candidate-b', uncertaintyLabel: 'ambiguous_support', conflictGroupId: 'conflict-1' }),
    candidate({ id: 'candidate-c', conflictGroupId: 'conflict-2' }),
  ), { sourceIdeaId: SOURCE_ID });

  assert.equal(model.uncertainCount, 2);
  assert.equal(model.conflictGroupCount, 2);
  assert.equal(model.groups[0].conflictGroupCount, 2);
});

test('normalization preserves review evidence, provenance, identifiers, fingerprints, duplicates, and original record', () => {
  const record = candidate({ id: 'candidate-a', extractedClaim: undefined });
  record.candidate_content.diagnostic_claim = 'Diagnostic claim';
  delete record.candidate_content.extracted_claim;
  const model = buildGroupedReviewModel(data(record), { sourceIdeaId: SOURCE_ID });
  const normalized = model.groups[0].candidates[0];

  assert.equal(normalized.claim, 'Diagnostic claim');
  assert.equal(normalized.sourceLocator, 'source:candidate-a');
  assert.deepEqual(normalized.evidence, record.candidate_content.evidence);
  assert.deepEqual(normalized.provenance, record.candidate_content.provenance);
  assert.equal(normalized.rawFindingId, 'raw-candidate-a');
  assert.equal(normalized.normalizedFindingId, 'finding-candidate-a');
  assert.equal(normalized.candidateFingerprint, 'candidate-fingerprint-candidate-a');
  assert.equal(normalized.evidenceFingerprint, 'evidence-fingerprint-candidate-a');
  assert.deepEqual(normalized.duplicateMetadata, record.candidate_content.duplicate_metadata);
  assert.deepEqual(normalized.relatedFindingIds, ['finding-other']);
  assert.equal(normalized.originalRecord, record);
});

test('safety boundaries remain true and no truth, canon, or promotion recommendation is introduced', () => {
  const model = buildGroupedReviewModel(data(candidate({ id: 'candidate-a' })), { sourceIdeaId: SOURCE_ID });

  assert.deepEqual(model.safetyBoundaries, {
    queuePresenceIsNotApproval: true,
    supportIsNotTruth: true,
    candidatePersistenceIsNotCanon: true,
    toolOutputIsNotCanon: true,
    approvalDoesNotApplyPromotion: true,
  });
  assert.equal('truthScore' in model, false);
  assert.equal('canonScore' in model, false);
  assert.equal('promotionRecommendation' in model, false);
});
