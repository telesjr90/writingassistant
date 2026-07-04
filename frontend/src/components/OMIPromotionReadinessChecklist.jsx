function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function hasValue(value) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  return value !== null && value !== undefined && value !== '';
}

function getStatusText(isMet, blockedText) {
  return isMet ? 'Complete' : blockedText;
}

export function getPromotionReadinessItems(candidate) {
  const blockers = asArray(candidate?.blockers ?? candidate?.promotion_blockers);
  const status = String(candidate?.status ?? candidate?.review_status ?? '').toLowerCase();
  const destination = candidate?.destination ?? candidate?.target_destination;
  const evidence = candidate?.evidence_summary ?? candidate?.evidence_refs;
  const provenance = candidate?.provenance_summary ?? candidate?.provenance_refs ?? candidate?.source_locator;
  const duplicateState = candidate?.duplicate_state ?? candidate?.duplicate_decision;
  const dependencyState = candidate?.dependency_state ?? candidate?.dependency_review;
  const schemaStatus = candidate?.schema_status ?? candidate?.candidate_schema_status;
  const promotionAudit = candidate?.promotion_audit_record ?? candidate?.promotion_record;

  return [
    {
      label: 'Owner approved candidate',
      isMet: status.includes('owner approved') || status.includes('approved'),
      detail: getStatusText(
        status.includes('owner approved') || status.includes('approved'),
        'Candidate: Pending Review',
      ),
    },
    {
      label: 'Destination selected and allowed',
      isMet: hasValue(destination),
      detail: getStatusText(hasValue(destination), 'Missing destination'),
    },
    {
      label: 'Evidence reviewed or insufficiency accepted',
      isMet: hasValue(evidence),
      detail: getStatusText(hasValue(evidence), 'Missing evidence'),
    },
    {
      label: 'Provenance reviewed',
      isMet: hasValue(provenance),
      detail: getStatusText(hasValue(provenance), 'Missing provenance'),
    },
    {
      label: 'Duplicate decision complete',
      isMet: hasValue(duplicateState) && !String(duplicateState).toLowerCase().includes('unresolved'),
      detail: getStatusText(
        hasValue(duplicateState) && !String(duplicateState).toLowerCase().includes('unresolved'),
        'Duplicate unresolved',
      ),
    },
    {
      label: 'Dependencies reviewed',
      isMet: hasValue(dependencyState) && !String(dependencyState).toLowerCase().includes('unresolved'),
      detail: getStatusText(
        hasValue(dependencyState) && !String(dependencyState).toLowerCase().includes('unresolved'),
        'Dependency unresolved',
      ),
    },
    {
      label: 'Candidate schema supported',
      isMet: !String(schemaStatus || '').toLowerCase().includes('unsupported') && blockers.length === 0,
      detail: blockers.length > 0
        ? blockers.join('; ')
        : getStatusText(
          !String(schemaStatus || '').toLowerCase().includes('unsupported'),
          'Unsupported candidate schema',
        ),
    },
    {
      label: 'Promotion audit record preview available',
      isMet: hasValue(promotionAudit),
      detail: hasValue(promotionAudit)
        ? 'Promotion audit record exists but is not applied.'
        : 'Promotion Audit Record: Not Applied to Memory/Canon',
    },
  ];
}

export default function OMIPromotionReadinessChecklist({ candidate }) {
  const items = getPromotionReadinessItems(candidate);

  return (
    <section
      className="omi-candidate-panel"
      data-testid="omi-promotion-readiness-checklist"
      aria-label="Promotion readiness checklist"
    >
      <h2>Promotion readiness checklist</h2>
      <ul className="omi-checklist">
        {items.map((item) => (
          <li
            key={item.label}
            className={item.isMet ? 'is-met' : 'is-blocked'}
          >
            <strong>{item.isMet ? '[x]' : '[ ]'} {item.label}</strong>
            <span>{item.detail}</span>
          </li>
        ))}
      </ul>
      <p className="review-boundary-note">
        Ready means the handoff packet is complete. Memory/Canon has not changed.
      </p>
    </section>
  );
}
