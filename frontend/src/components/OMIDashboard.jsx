import OMIWorkflowStatusRow from './OMIWorkflowStatusRow.jsx';

export const OMI_DISABLED_APPLY_REASON =
  'Disabled: apply-promotion requires owner approval, destination, evidence/provenance review, duplicate resolution, dependency review, and final confirmation.';

const ZERO_STATE_OWNER_INPUT =
  'No owner input is stored for this project. Open the project workspace to add owner-authored source material.';
const ZERO_STATE_CANDIDATES =
  'No candidates are stored for this project. Raw ideas may remain unstructured and are not Memory/Canon.';

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function explicitCount(...values) {
  for (const value of values) {
    const count = Number(value);
    if (Number.isFinite(count) && count >= 0) {
      return count;
    }
  }
  return null;
}

function countByStatus(items, matches) {
  return items.filter((item) => {
    const status = String(
      item?.status
      ?? item?.review_status
      ?? item?.lifecycle_state
      ?? item?.decision
      ?? '',
    ).toLowerCase();
    return matches.some((match) => status.includes(match));
  }).length;
}

function countPresentRefs(items, keys) {
  return items.filter((item) => (
    keys.some((key) => {
      const value = item?.[key];
      if (Array.isArray(value)) {
        return value.length > 0;
      }
      return value !== null && value !== undefined && value !== '';
    })
  )).length;
}

function formatCount(count, degraded) {
  if (degraded) {
    return 'Unavailable';
  }
  return Number.isFinite(count) ? String(count) : '0';
}

function evidenceSummary({ linked, total, degraded, fallback = 'No stored evidence/provenance metadata' }) {
  if (degraded) {
    return 'Unavailable: OMI status did not load';
  }
  if (!Number.isFinite(total) || total === 0) {
    return fallback;
  }
  return `Evidence Linked ${linked} / ${total}; Provenance Linked ${linked} / ${total}`;
}

function approvedMemoryTotal(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) {
    return 0;
  }

  const explicit = explicitCount(
    snapshot.total,
    snapshot.total_count,
    snapshot.approved_count,
    snapshot.record_count,
  );
  if (explicit !== null) {
    return explicit;
  }

  return Object.values(snapshot).reduce((total, value) => {
    if (Array.isArray(value)) {
      return total + value.length;
    }
    if (Number.isFinite(Number(value)) && Number(value) >= 0) {
      return total + Number(value);
    }
    return total;
  }, 0);
}

function approvedMemoryRows(snapshot) {
  const categories = [
    ['Characters', 'characters'],
    ['Locations', 'locations'],
    ['Timeline', 'timeline'],
    ['Plot Threads', 'plot_threads'],
  ];

  return categories.map(([label, key]) => {
    const value = snapshot?.[key];
    const count = Array.isArray(value) ? value.length : explicitCount(value) ?? 0;
    return [label, count];
  });
}

export function getOMIDashboardSummary(omiData, { isLoading = false, error = '' } = {}) {
  const ideas = asArray(omiData?.ideas);
  const candidates = asArray(omiData?.candidates);
  const groups = asArray(omiData?.groups ?? omiData?.candidate_groups);
  const promotions = asArray(omiData?.promotions ?? omiData?.promotion_audit_records);
  const deferred = asArray(omiData?.deferred ?? omiData?.deferred_categories);
  const warnings = asArray(omiData?.warnings ?? omiData?.health_warnings);
  const approvedSnapshot =
    omiData?.approved_memory_canon_snapshot
    ?? omiData?.approved_memory_snapshot
    ?? omiData?.memory_canon_snapshot
    ?? null;
  const degraded = Boolean(error);
  const ownerInputCount = degraded ? null : explicitCount(omiData?.owner_input_count, omiData?.raw_idea_count) ?? ideas.length;
  const candidateCount = degraded ? null : explicitCount(omiData?.candidate_count) ?? candidates.length;
  const promotionAuditCount = degraded ? null : explicitCount(omiData?.promotion_audit_count) ?? promotions.length;
  const handoffReadyCount = degraded
    ? null
    : explicitCount(omiData?.handoff_ready_count, omiData?.promotion_ready_count)
      ?? countByStatus(candidates, ['handoff ready', 'ready']);
  const blockedCount = degraded
    ? null
    : explicitCount(omiData?.blocked_count)
      ?? countByStatus(candidates, ['blocked', 'missing', 'needs evidence']);
  const duplicateCount = degraded
    ? null
    : explicitCount(omiData?.duplicate_decision_count)
      ?? countByStatus(candidates, ['duplicate', 'merge']);
  const evidenceLinked = degraded ? 0 : countPresentRefs(candidates, [
    'evidence_refs',
    'evidence_summary',
    'provenance_refs',
    'provenance_summary',
    'source_locator',
    'source_locator_refs',
  ]);
  const approvedTotal = degraded ? null : approvedMemoryTotal(approvedSnapshot);

  return {
    isLoading,
    degraded,
    ideas,
    candidates,
    groups,
    promotions,
    deferred,
    warnings,
    approvedSnapshot,
    ownerInputCount,
    candidateCount,
    blockedCount,
    duplicateCount,
    handoffReadyCount,
    promotionAuditCount,
    approvedTotal,
    evidenceLinked,
  };
}

export default function OMIDashboard({
  omiData,
  isLoading = false,
  error = '',
  onNavigate = () => {},
}) {
  const summary = getOMIDashboardSummary(omiData, { isLoading, error });
  const {
    degraded,
    ownerInputCount,
    candidateCount,
    blockedCount,
    duplicateCount,
    handoffReadyCount,
    promotionAuditCount,
    approvedSnapshot,
    approvedTotal,
    evidenceLinked,
    groups,
    deferred,
    warnings,
  } = summary;
  const disabledApplyReasonId = 'omi-dashboard-disabled-apply-reason';
  const rows = [
    {
      area: 'Owner Input',
      count: formatCount(ownerInputCount, degraded),
      status: degraded ? 'Unavailable' : ownerInputCount === 0 ? 'Zero State' : 'Reviewable',
      statusTone: ownerInputCount === 0 ? 'is-warning' : '',
      blockers: degraded ? 'Unavailable' : ownerInputCount === 0 ? 'No owner input' : 'Stored review source',
      evidence: evidenceSummary({
        linked: ownerInputCount ?? 0,
        total: ownerInputCount ?? 0,
        degraded,
        fallback: ZERO_STATE_OWNER_INPUT,
      }),
      action: 'Open owner input',
      disabledReason: 'No risky action in row',
      onAction: () => onNavigate('owner-input'),
    },
    {
      area: 'Candidates',
      count: formatCount(candidateCount, degraded),
      status: degraded ? 'Unavailable' : candidateCount === 0 ? 'Zero State' : 'Candidate: Pending Review',
      statusTone: candidateCount === 0 ? 'is-warning' : '',
      blockers: degraded ? 'Unavailable' : `${formatCount(blockedCount, false)} blocked`,
      evidence: evidenceSummary({
        linked: evidenceLinked,
        total: candidateCount ?? 0,
        degraded,
        fallback: ZERO_STATE_CANDIDATES,
      }),
      action: 'Review candidates',
      disabledReason: 'Candidates are not approved Memory/Canon',
      onAction: () => onNavigate('candidates'),
    },
    {
      area: 'Grouped Review',
      count: formatCount(groups.length, degraded),
      status: degraded ? 'Unavailable' : groups.length === 0 ? 'No Groups' : 'Needs Review',
      blockers: degraded ? 'Unavailable' : groups.length === 0 ? 'No grouped packets' : `${formatCount(blockedCount, false)} possible blockers`,
      evidence: degraded ? 'Unavailable' : groups.length === 0 ? 'No stored group provenance' : 'Stored group metadata only',
      action: 'Open grouped review',
      disabledReason: 'Grouped review does not approve canon',
      onAction: () => onNavigate('grouped-review'),
    },
    {
      area: 'Duplicate Decisions',
      count: formatCount(duplicateCount, degraded),
      status: degraded ? 'Unavailable' : duplicateCount === 0 ? 'No Pending Duplicates' : 'Pending',
      blockers: degraded ? 'Unavailable' : duplicateCount === 0 ? 'None recorded' : `${formatCount(duplicateCount, false)} decisions`,
      evidence: degraded ? 'Unavailable' : 'Provenance required before handoff',
      action: 'Resolve duplicates',
      disabledReason: 'Duplicate decisions are review metadata only',
      onAction: () => onNavigate('duplicate-decisions'),
    },
    {
      area: 'Promotion Handoff Readiness',
      count: formatCount(handoffReadyCount, degraded),
      status: degraded ? 'Unavailable' : handoffReadyCount === 0 ? 'Not Ready' : 'Ready for Handoff',
      blockers: degraded ? 'Unavailable' : handoffReadyCount === 0 ? 'Requirements incomplete' : 'No stored blockers',
      evidence: degraded ? 'Unavailable' : 'Ready means packet complete; Memory/Canon has not changed',
      action: 'Open handoff queue',
      disabledReason: OMI_DISABLED_APPLY_REASON,
      onAction: () => onNavigate('promotion-handoff'),
    },
    {
      area: 'Promotion Audit Records',
      count: formatCount(promotionAuditCount, degraded),
      status: degraded ? 'Unavailable' : promotionAuditCount === 0 ? 'No Audit Records' : 'Promotion Audit Record',
      blockers: degraded ? 'Unavailable' : 'Audit-only',
      evidence: degraded ? 'Unavailable' : 'Not Applied to Memory/Canon',
      action: 'View audit records',
      disabledReason: 'Audit records are not canon changes',
      onAction: () => onNavigate('promotion-audits'),
    },
    {
      area: 'Deferred Categories',
      count: formatCount(deferred.length, degraded),
      status: degraded ? 'Unavailable' : deferred.length === 0 ? 'None Deferred' : 'Deferred',
      blockers: degraded ? 'Unavailable' : 'Owner review required later',
      evidence: degraded ? 'Unavailable' : 'Source retained when available',
      action: 'Open deferred categories',
      disabledReason: 'Deferred categories do not mutate Memory/Canon',
      onAction: () => onNavigate('deferred-categories'),
    },
    {
      area: 'Warnings / Health',
      count: formatCount(warnings.length + (error ? 1 : 0), false),
      status: degraded ? 'Degraded Error State' : warnings.length === 0 ? 'No Warnings' : 'Warnings Present',
      statusTone: degraded || warnings.length > 0 ? 'is-error' : '',
      blockers: degraded ? 'No inferred counts' : warnings.length === 0 ? 'None recorded' : 'Review warnings',
      evidence: degraded ? error : 'Dashboard counts show review status only',
      action: 'Open health review',
      disabledReason: 'Health review cannot apply promotion',
      onAction: () => onNavigate('health'),
    },
  ];

  return (
    <section className="omi-dashboard" data-testid="omi-dashboard" aria-label="OMI Dashboard">
      {isLoading && (
        <p className="omi-loading-state" role="status">
          Loading OMI status.
        </p>
      )}

      {error && (
        <section className="omi-error-state" role="alert" aria-label="Degraded OMI status">
          <h3>OMI status unavailable</h3>
          <p>{error}</p>
          <p>No inferred counts are shown while OMI status is degraded.</p>
        </section>
      )}

      <div className="omi-workflow-table-wrap">
        <table className="omi-workflow-table">
          <caption>Project-local OMI operational workflow rows</caption>
          <thead>
            <tr>
              <th scope="col">Workflow area</th>
              <th scope="col">Count</th>
              <th scope="col">Status</th>
              <th scope="col">Blockers</th>
              <th scope="col">Evidence / Provenance</th>
              <th scope="col">Action</th>
              <th scope="col">Disabled risky action / reason</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <OMIWorkflowStatusRow key={row.area} row={row} />
            ))}
          </tbody>
        </table>
      </div>

      <section
        className="omi-approved-snapshot"
        data-testid="omi-dashboard-approved-memory-snapshot"
        aria-label="Approved Memory/Canon Snapshot"
      >
        <div className="section-heading">
          <div>
            <h3>Approved Memory/Canon Snapshot</h3>
            <p className="muted-copy">
              Approved Memory/Canon is shown separately from candidates and promotion audit records.
            </p>
          </div>
          <span className="omi-status-badge">Canon unchanged</span>
        </div>
        <dl>
          {approvedMemoryRows(approvedSnapshot).map(([label, count]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{degraded ? 'Unavailable' : count}</dd>
            </div>
          ))}
          <div>
            <dt>Total Approved Memory/Canon</dt>
            <dd>{degraded ? 'Unavailable' : approvedTotal}</dd>
          </div>
        </dl>
        <button
          className="secondary-button"
          type="button"
          aria-label="Open Approved Memory/Canon"
          onClick={() => onNavigate('approved-memory-canon')}
        >
          Open Approved Memory/Canon
        </button>
      </section>

      <section className="omi-health-panel" aria-label="Warnings / Health">
        <h3>Warnings / Health</h3>
        <ul>
          <li>Dashboard counts show review status only. Candidates, groups, and promotion records are not canon.</li>
          <li>Ready means the handoff packet is complete. Memory/Canon has not changed.</li>
          <li>Owner input can be used for review, but it is not Memory/Canon by itself.</li>
        </ul>
        <button
          className="primary-button"
          type="button"
          disabled
          aria-describedby={disabledApplyReasonId}
        >
          Apply to Memory/Canon
        </button>
        <p
          id={disabledApplyReasonId}
          className="omi-disabled-reason"
          data-testid="omi-dashboard-disabled-apply-reason"
        >
          {OMI_DISABLED_APPLY_REASON}
        </p>
      </section>
    </section>
  );
}
