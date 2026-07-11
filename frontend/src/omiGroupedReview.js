export const OMI_TOOL_ASSISTED_SOURCE = 'omi_tool_assisted_fused_analysis';

const SAFE_SOURCE_ID = /^idea_[A-Za-z0-9][A-Za-z0-9_-]*$/;

const SAFETY_BOUNDARIES = Object.freeze({
  queuePresenceIsNotApproval: true,
  supportIsNotTruth: true,
  candidatePersistenceIsNotCanon: true,
  toolOutputIsNotCanon: true,
  approvalDoesNotApplyPromotion: true,
});

function isRecord(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function isSafeSourceIdeaId(value) {
  return typeof value === 'string' && SAFE_SOURCE_ID.test(value);
}

function compareText(left, right) {
  const normalizedLeft = typeof left === 'string' ? left : '';
  const normalizedRight = typeof right === 'string' ? right : '';

  if (normalizedLeft < normalizedRight) return -1;
  if (normalizedLeft > normalizedRight) return 1;
  return 0;
}

function firstDefined(...values) {
  return values.find((value) => value !== undefined && value !== null);
}

function ownerDecisionFor(candidate, content) {
  return firstDefined(candidate.owner_decision, content.owner_decision, null);
}

function decisionValue(ownerDecision) {
  if (typeof ownerDecision === 'string') return ownerDecision;
  if (isRecord(ownerDecision) && typeof ownerDecision.decision === 'string') {
    return ownerDecision.decision;
  }
  return null;
}

function reviewStatusFor(candidate, content) {
  return firstDefined(candidate.review_status, content.review_status, null);
}

function isPendingReview(ownerDecision, reviewStatus) {
  const decision = decisionValue(ownerDecision);
  if (!decision || decision === 'pending') return true;
  return typeof reviewStatus === 'string' && reviewStatus.includes('pending');
}

function normalizeCandidate(candidate, sourceIdeaId) {
  const content = candidate.candidate_content;
  const provenance = firstDefined(content.provenance, candidate.provenance, null);
  const evidence = firstDefined(content.evidence, candidate.evidence, []);
  const duplicateMetadata = firstDefined(content.duplicate_metadata, candidate.duplicate_metadata, null);
  const ownerDecision = ownerDecisionFor(candidate, content);
  const reviewStatus = reviewStatusFor(candidate, content);
  const sourceAdapter = typeof content.source_adapter === 'string' ? content.source_adapter : null;
  const originalFindingCandidateType = typeof content.candidate_type === 'string'
    ? content.candidate_type
    : null;

  return {
    candidateId: candidate.candidate_id,
    sourceIdeaId,
    sourceAdapter,
    toolSource: firstDefined(content.tool_source, provenance?.tool_source, provenance?.tool, null),
    originalFindingCandidateType,
    storageCandidateType: typeof candidate.candidate_type === 'string' ? candidate.candidate_type : null,
    label: firstDefined(content.label, content.name, null),
    name: firstDefined(content.name, content.label, null),
    claim: firstDefined(content.extracted_claim, content.diagnostic_claim, null),
    extractedClaim: firstDefined(content.extracted_claim, content.diagnostic_claim, null),
    diagnosticClaim: firstDefined(content.diagnostic_claim, content.extracted_claim, null),
    evidence,
    sourceLocator: firstDefined(
      content.source_locator,
      Array.isArray(evidence) ? evidence[0]?.source_locator : undefined,
      provenance?.source_locator,
      null,
    ),
    provenance,
    supportLabel: firstDefined(content.support_label, provenance?.support, null),
    confidence: firstDefined(content.confidence, provenance?.confidence, null),
    uncertaintyLabel: firstDefined(content.uncertainty_label, null),
    conflictGroupId: firstDefined(content.conflict_group_id, null),
    duplicateMetadata,
    relatedFindingIds: firstDefined(duplicateMetadata?.related_finding_ids, content.related_finding_ids, []),
    rawFindingId: firstDefined(content.raw_finding_id, provenance?.raw_finding_id, null),
    normalizedFindingId: firstDefined(
      content.normalized_finding_id,
      provenance?.normalized_finding_id,
      null,
    ),
    candidateFingerprint: firstDefined(
      content.candidate_fingerprint,
      provenance?.candidate_fingerprint,
      null,
    ),
    evidenceFingerprint: firstDefined(
      content.evidence_fingerprint,
      provenance?.evidence_fingerprint,
      null,
    ),
    ownerDecision,
    reviewStatus,
    promotionStatus: firstDefined(candidate.promotion_status, content.promotion_status, null),
    originalRecord: candidate,
  };
}

function compareCandidates(left, right) {
  return compareText(left.sourceAdapter, right.sourceAdapter)
    || compareText(left.originalFindingCandidateType, right.originalFindingCandidateType)
    || compareText(left.normalizedFindingId, right.normalizedFindingId)
    || compareText(left.candidateId, right.candidateId);
}

function hasLabel(value) {
  return typeof value === 'string' && value.trim() !== '';
}

function countGroup(candidates) {
  const pendingCount = candidates.filter((candidate) => (
    isPendingReview(candidate.ownerDecision, candidate.reviewStatus)
  )).length;
  const conflictGroupIds = new Set(
    candidates.map((candidate) => candidate.conflictGroupId).filter(hasLabel),
  );
  const candidateTypes = new Map();

  candidates.forEach((candidate) => {
    const candidateType = candidate.originalFindingCandidateType;
    candidateTypes.set(candidateType, (candidateTypes.get(candidateType) ?? 0) + 1);
  });

  return {
    totalCount: candidates.length,
    pendingCount,
    uncertainCount: candidates.filter((candidate) => hasLabel(candidate.uncertaintyLabel)).length,
    conflictGroupCount: conflictGroupIds.size,
    candidateTypes: [...candidateTypes.entries()]
      .map(([candidateType, count]) => ({ candidateType, count }))
      .sort((left, right) => compareText(left.candidateType, right.candidateType)),
  };
}

export function selectLinkedReviewCandidates(omiData, sourceIdeaId) {
  if (!isRecord(omiData) || !isSafeSourceIdeaId(sourceIdeaId)) return [];
  if (!Array.isArray(omiData.ideas) || !Array.isArray(omiData.candidates)) return [];

  const sourceIdea = omiData.ideas.find((idea) => (
    isRecord(idea) && idea.idea_id === sourceIdeaId
  ));
  if (!sourceIdea || !Array.isArray(sourceIdea.linked_candidate_ids)) return [];

  const linkedIds = new Set(sourceIdea.linked_candidate_ids.filter((id) => typeof id === 'string'));
  if (linkedIds.size === 0) return [];

  return omiData.candidates
    .filter((candidate) => (
      isRecord(candidate)
      && typeof candidate.candidate_id === 'string'
      && linkedIds.has(candidate.candidate_id)
      && isRecord(candidate.candidate_content)
      && candidate.candidate_content.source === OMI_TOOL_ASSISTED_SOURCE
    ))
    .slice()
    .sort((left, right) => compareText(left.candidate_id, right.candidate_id));
}

export function buildGroupedReviewModel(omiData, { sourceIdeaId } = {}) {
  const selected = selectLinkedReviewCandidates(omiData, sourceIdeaId);
  const candidates = selected
    .map((candidate) => normalizeCandidate(candidate, sourceIdeaId))
    .sort(compareCandidates);
  const grouped = new Map();

  candidates.forEach((candidate) => {
    const groupKey = `source-adapter:${candidate.sourceAdapter ?? 'missing'}`;
    const existing = grouped.get(groupKey) ?? {
      groupKey,
      sourceAdapter: candidate.sourceAdapter,
      candidates: [],
    };
    existing.candidates.push(candidate);
    grouped.set(groupKey, existing);
  });

  const groups = [...grouped.values()]
    .map((group) => ({
      ...group,
      ...countGroup(group.candidates),
      candidates: group.candidates.slice().sort(compareCandidates),
    }))
    .sort((left, right) => compareText(left.sourceAdapter, right.sourceAdapter));
  const counts = countGroup(candidates);

  return {
    sourceIdeaId: isSafeSourceIdeaId(sourceIdeaId) ? sourceIdeaId : null,
    totalCount: counts.totalCount,
    pendingCount: counts.pendingCount,
    reviewedCount: counts.totalCount - counts.pendingCount,
    uncertainCount: counts.uncertainCount,
    conflictGroupCount: counts.conflictGroupCount,
    sourceAdapterCount: groups.length,
    groups,
    safetyBoundaries: { ...SAFETY_BOUNDARIES },
  };
}
