import ApplyPromotionConfirmation from './ApplyPromotionConfirmation.jsx';

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function getCandidateId(candidate) {
  return candidate?.candidate_id ?? candidate?.candidateId ?? candidate?.id ?? '';
}

function findCandidate(candidates, selectedCandidateId) {
  if (!selectedCandidateId) {
    return candidates[0] ?? null;
  }
  return candidates.find((candidate) => getCandidateId(candidate) === selectedCandidateId) ?? candidates[0] ?? null;
}

export default function OMIApplyPromotionRoute({
  activeProjectId,
  candidates = [],
  selectedCandidateId = '',
  approvedMemoryCanonSnapshot = null,
  onCancel = () => {},
}) {
  const candidate = findCandidate(asArray(candidates), selectedCandidateId);

  return (
    <section className="omi-apply-route" aria-label="Route-backed Apply-Promotion Confirmation">
      <ApplyPromotionConfirmation
        projectId={activeProjectId}
        candidate={candidate}
        approvedMemoryCanonSnapshot={approvedMemoryCanonSnapshot}
        applyPromotionAvailable={false}
        onCancel={onCancel}
      />
    </section>
  );
}
