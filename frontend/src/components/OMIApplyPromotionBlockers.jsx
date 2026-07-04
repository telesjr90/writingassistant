export const REQUIRED_APPLY_PROMOTION_BLOCKERS = Object.freeze([
  'Candidate not ready',
  'Missing owner approval',
  'Missing destination',
  'Unsupported destination',
  'Missing evidence/provenance',
  'Missing source locator',
  'Duplicate unresolved',
  'Dependency unresolved',
  'Promotion audit record missing',
  'Target file/path missing',
  'Approved Memory/Canon before-state unavailable',
  'Final confirmation incomplete',
  'Apply-promotion unavailable in this version',
  'Apply-promotion failed or would fail closed',
]);

export default function OMIApplyPromotionBlockers({
  blockers = [],
  describedById,
}) {
  const visibleBlockers = blockers.length > 0
    ? blockers
    : ['No visible blockers. Owner final confirmation is still required.'];

  return (
    <section
      className="omi-apply-blockers"
      data-testid="omi-apply-promotion-blockers"
      aria-label="Apply-Promotion blockers"
    >
      <div className="section-heading">
        <div>
          <h2>Visible Blockers</h2>
          <p className="muted-copy">
            Blocked reasons appear before Owner Final Confirmation and Final Apply-Promotion.
          </p>
        </div>
        <span className={blockers.length > 0 ? 'omi-status-badge is-error' : 'omi-status-badge'}>
          {blockers.length > 0 ? 'Promotion Blocked' : 'No blocker recorded'}
        </span>
      </div>
      <ul id={describedById} className="omi-apply-blocker-list">
        {visibleBlockers.map((blocker) => (
          <li key={blocker}>
            <strong>{blockers.length > 0 ? 'Blocked' : 'Ready check'}</strong>
            <span>{blocker}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
