import ApplyPromotionConfirmation from './ApplyPromotionConfirmation.jsx';

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function getCandidateId(candidate) {
  return candidate?.candidate_id ?? candidate?.candidateId ?? candidate?.id ?? '';
}

function getPromotionId(promotion) {
  return promotion?.promotion_id ?? '';
}

export function findExactPromotion(promotions, selectedPromotionId) {
  if (!selectedPromotionId) {
    return null;
  }
  return promotions.find((promotion) => getPromotionId(promotion) === selectedPromotionId) ?? null;
}

export function findExactPromotionCandidate(candidates, promotion) {
  if (!promotion?.candidate_id) {
    return null;
  }
  return candidates.find((candidate) => getCandidateId(candidate) === promotion.candidate_id) ?? null;
}

export default function OMIApplyPromotionRoute({
  activeProjectId,
  candidates = [],
  promotions = [],
  selectedCandidateId = '',
  selectedPromotionId = '',
  onSelectPromotion = () => {},
  approvedMemoryCanonSnapshot = null,
  onCancel = () => {},
}) {
  const storedPromotions = asArray(promotions);
  const promotion = findExactPromotion(storedPromotions, selectedPromotionId);
  const candidate = findExactPromotionCandidate(asArray(candidates), promotion);
  const associationValid = Boolean(
    promotion
    && candidate
    && getCandidateId(candidate) === selectedCandidateId
    && promotion.candidate_id === selectedCandidateId,
  );

  return (
    <section className="omi-apply-route" aria-label="Route-backed Apply-Promotion Confirmation">
      <div className="omi-apply-selection">
        <label className="field-label" htmlFor="omi-apply-promotion-selection">
          Exact promotion record
        </label>
        <select
          id="omi-apply-promotion-selection"
          value={selectedPromotionId}
          onChange={(event) => onSelectPromotion(event.target.value)}
        >
          <option value="">Select a promotion record</option>
          {storedPromotions.map((item) => (
            <option key={getPromotionId(item)} value={getPromotionId(item)}>
              {getPromotionId(item)} — candidate {item?.candidate_id ?? 'missing'}
            </option>
          ))}
        </select>
        <p className="muted-copy">
          Selection is explicit. The interface never substitutes the first promotion or candidate.
        </p>
      </div>

      {!selectedPromotionId && (
        <p className="omi-apply-selection-state" role="status">
          Select one exact promotion record to inspect its authoritative apply-contract lineage.
        </p>
      )}
      {selectedPromotionId && !associationValid && (
        <p className="error-copy" role="alert">
          The selected promotion and candidate association is missing or inconsistent. Preparation is blocked.
        </p>
      )}
      {associationValid && (
        <ApplyPromotionConfirmation
          key={selectedPromotionId}
          projectId={activeProjectId}
          promotion={promotion}
          candidate={candidate}
          approvedMemoryCanonSnapshot={approvedMemoryCanonSnapshot}
          onCancel={onCancel}
        />
      )}
    </section>
  );
}
