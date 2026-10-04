import { useEffect, useRef, useState } from 'react';
import OMIWorkflowStatusRow from './OMIWorkflowStatusRow.jsx';
import OMILoadingState from './OMILoadingState.jsx';
import {
  describeNcpInterfaceState,
  validateNcpDestinationIdentifier,
} from '../omiAnalysisRunWorkflow.js';

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

function hasStoredValue(value) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  if (value && typeof value === 'object') {
    return Object.keys(value).length > 0;
  }
  return value !== null && value !== undefined && value !== '';
}

function countPresentRefs(items, keys) {
  return items.filter((item) => (
    keys.some((key) => hasStoredValue(item?.[key]))
  )).length;
}

function formatCount(count, degraded) {
  if (degraded) {
    return 'Unavailable';
  }
  return Number.isFinite(count) ? String(count) : '0';
}

function evidenceSummary({
  evidenceLinked,
  provenanceLinked,
  total,
  degraded,
  fallback = 'No stored evidence/provenance metadata',
}) {
  if (degraded) {
    return 'Unavailable: OMI status did not load';
  }
  if (!Number.isFinite(total) || total === 0) {
    return fallback;
  }
  return `Evidence Linked ${evidenceLinked} / ${total}; Provenance Linked ${provenanceLinked} / ${total}`;
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
    'evidence',
    'evidence_refs',
    'evidence_summary',
  ]);
  const provenanceLinked = degraded ? 0 : countPresentRefs(candidates, [
    'provenance',
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
    provenanceLinked,
  };
}

const NCP_DIAGNOSTIC_FIXTURE = Object.freeze({
  contractVersion: 'writer-assistant-ncp-operator-controls.v1',
  schemaInterfaceId: 'ncp-schema-interface-deterministic-fixture',
  schemaPath: '.external_sources/narrative-context-protocol/schema/ncp-schema.json',
  schemaSha256: '34197d575b261905a43c4e79c48435df833deeeecd85cce918b00850f2bf8ca4',
  standardValidationId: 'ncp-standard-validation-deterministic-fixture',
  matrixId: 'ncp-roundtrip-matrix-deterministic-fixture',
  importValidationId: 'ncp-import-validation-deterministic-fixture',
  ownerReviewStatus: 'candidate_only_owner_review_required',
});

const NCP_INTERFACE_SCENARIOS = Object.freeze([
  ['success', 'Diagnostics available'],
  ['loading', 'Loading'],
  ['empty', 'Empty'],
  ['invalid', 'Invalid'],
  ['unavailable', 'Unavailable'],
  ['request_failure', 'Request failure'],
]);

function NcpTraceabilityList() {
  return (
    <dl className="omi-ncp-metadata">
      <div>
        <dt>Operator contract</dt>
        <dd><code>{NCP_DIAGNOSTIC_FIXTURE.contractVersion}</code></dd>
      </div>
      <div>
        <dt>Schema interface ID</dt>
        <dd><code>{NCP_DIAGNOSTIC_FIXTURE.schemaInterfaceId}</code></dd>
      </div>
      <div>
        <dt>Schema source</dt>
        <dd><code>{NCP_DIAGNOSTIC_FIXTURE.schemaPath}</code></dd>
      </div>
      <div>
        <dt>Schema SHA-256</dt>
        <dd><code>{NCP_DIAGNOSTIC_FIXTURE.schemaSha256}</code></dd>
      </div>
      <div>
        <dt>Standard validation</dt>
        <dd><code>{NCP_DIAGNOSTIC_FIXTURE.standardValidationId}</code></dd>
      </div>
      <div>
        <dt>Round-trip matrix</dt>
        <dd><code>{NCP_DIAGNOSTIC_FIXTURE.matrixId}</code></dd>
      </div>
    </dl>
  );
}

export function NcpDiagnosticsOwnerSurface({ onBackToDashboard = () => {} }) {
  const [interfaceScenario, setInterfaceScenario] = useState('success');
  const [destinationId, setDestinationId] = useState('');
  const [intentConfirmed, setIntentConfirmed] = useState(false);
  const [finalConfirmed, setFinalConfirmed] = useState(false);
  const [handoffReady, setHandoffReady] = useState(false);
  const retryTimerRef = useRef(null);
  const interfaceState = describeNcpInterfaceState(interfaceScenario);
  const destinationValidation = validateNcpDestinationIdentifier(destinationId);
  const showDestinationFeedback = destinationId !== '';
  const canPrepareHandoff = Boolean(
    interfaceState.operable
    && destinationValidation.valid
    && intentConfirmed
    && finalConfirmed,
  );

  useEffect(() => () => {
    if (retryTimerRef.current) {
      window.clearTimeout(retryTimerRef.current);
    }
  }, []);

  function resetHandoff() {
    setFinalConfirmed(false);
    setHandoffReady(false);
  }

  function handleScenarioChange(event) {
    if (retryTimerRef.current) {
      window.clearTimeout(retryTimerRef.current);
      retryTimerRef.current = null;
    }
    setInterfaceScenario(event.target.value);
    setIntentConfirmed(false);
    resetHandoff();
  }

  function handleRetry() {
    setInterfaceScenario('loading');
    setIntentConfirmed(false);
    resetHandoff();
    retryTimerRef.current = window.setTimeout(() => {
      setInterfaceScenario('success');
      retryTimerRef.current = null;
    }, 250);
  }

  function handlePrepareHandoff() {
    if (canPrepareHandoff) {
      setHandoffReady(true);
    }
  }

  const stateContent = {
    loading: (
      <p className="omi-loading-state" role="status" aria-live="polite">
        Loading the deterministic local interface record. No external request or NCP runtime call is made.
      </p>
    ),
    empty: (
      <div className="omi-analysis-notice is-warning" role="status">
        <strong>No NCP operator-controls record is available.</strong>
        <span>Addition of a record requires a separately authorized backend integration; no fallback analysis runs here.</span>
      </div>
    ),
    invalid: (
      <div className="omi-analysis-notice is-error" role="alert">
        <strong>Schema or round-trip validation is invalid.</strong>
        <span>Standard export handoff is blocked. The invalid record cannot approve data or change project truth.</span>
      </div>
    ),
    unavailable: (
      <div className="omi-analysis-notice is-warning" role="status">
        <strong>NCP interface unavailable.</strong>
        <span>Gateway diagnostics cannot be inspected, and this UI does not substitute raw-text analysis.</span>
      </div>
    ),
    request_failure: (
      <div className="omi-analysis-notice is-error" role="alert">
        <strong>Interface check failed.</strong>
        <span>The deterministic record could not be loaded. No import, export, or project mutation started.</span>
        <button className="secondary-button" type="button" onClick={handleRetry}>
          Retry interface check
        </button>
      </div>
    ),
  };

  return (
    <section className="omi-ncp-owner" aria-labelledby="omi-ncp-owner-heading">
      <div className="omi-ncp-header">
        <div>
          <p className="eyebrow">Owner-controlled gateway</p>
          <h2 id="omi-ncp-owner-heading">NCP import, export, and diagnostics</h2>
          <p className="muted-copy">
            NCP is a schema gateway and diagnostic support interface—not a raw-text analyzer or truth selector.
          </p>
        </div>
        <button className="secondary-button" type="button" onClick={onBackToDashboard}>
          Back to OMI Dashboard
        </button>
      </div>

      <section className="omi-ncp-boundary" aria-labelledby="omi-ncp-boundary-heading">
        <h3 id="omi-ncp-boundary-heading">No execution or truth mutation</h3>
        <p>
          This UI can validate a future handoff state only. It cannot write an export, persist an import,
          approve a candidate, record a review decision, promote or apply promotion, or change Memory/Canon.
        </p>
      </section>

      <section className="omi-ncp-section" aria-labelledby="omi-ncp-interface-heading">
        <div className="omi-ncp-section-heading">
          <div>
            <h3 id="omi-ncp-interface-heading">Interface readiness</h3>
            <p className="muted-copy">Deterministic local fixture states exercise the UI without a backend route or external runtime.</p>
          </div>
          <span className={`omi-status-badge ${interfaceState.tone}`} role="status" aria-live="polite">
            {interfaceState.label}
          </span>
        </div>
        <label className="omi-analysis-field" htmlFor="omi-ncp-interface-scenario">
          Interface state preview (no request sent)
          <select
            id="omi-ncp-interface-scenario"
            value={interfaceScenario}
            onChange={handleScenarioChange}
          >
            {NCP_INTERFACE_SCENARIOS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        {interfaceScenario !== 'success' ? stateContent[interfaceScenario] : null}
      </section>

      {interfaceState.operable ? (
        <>
          <section className="omi-ncp-package-grid" aria-label="NCP package readiness">
            <article className="omi-ncp-package is-standard">
              <div className="omi-ncp-section-heading">
                <h3>Standard approved-context export</h3>
                <span className="omi-status-badge is-success">Validation passed</span>
              </div>
              <p>Approved-context-only package. Readiness is for a future handoff; this UI cannot export or write it.</p>
              <ul>
                <li>Schema interface validated</li>
                <li>Trusted round-trip matrix gate passed</li>
                <li>Approved context remains separate from candidate material</li>
              </ul>
            </article>
            <article className="omi-ncp-package is-blocked">
              <div className="omi-ncp-section-heading">
                <h3>Candidate review bundle</h3>
                <span className="omi-status-badge is-warning">Owner decision pending</span>
              </div>
              <p>Separately labeled review-only behavior. It is not approved context and cannot execute.</p>
              <button className="secondary-button" type="button" disabled aria-describedby="omi-ncp-bundle-reason">
                Prepare candidate bundle
              </button>
              <p id="omi-ncp-bundle-reason" className="omi-disabled-reason">
                Disabled: candidate-bundle contents and status semantics remain unresolved.
              </p>
            </article>
          </section>

          <section className="omi-ncp-section" aria-labelledby="omi-ncp-destination-heading">
            <div className="omi-ncp-section-heading">
              <div>
                <h3 id="omi-ncp-destination-heading">Safe destination and confirmation</h3>
                <p className="muted-copy">Only a new opaque target ID is accepted. Filesystem paths and overwrite semantics are blocked.</p>
              </div>
              <span className={`omi-status-badge ${destinationValidation.valid ? 'is-success' : 'is-warning'}`}>
                {destinationValidation.valid ? 'Destination valid' : 'Destination required'}
              </span>
            </div>
            <label className="omi-ncp-field" htmlFor="omi-ncp-destination-id">
              New opaque target identifier
              <input
                id="omi-ncp-destination-id"
                type="text"
                value={destinationId}
                maxLength={128}
                autoComplete="off"
                spellCheck="false"
                aria-invalid={showDestinationFeedback && !destinationValidation.valid}
                aria-describedby="omi-ncp-destination-help omi-ncp-destination-feedback"
                placeholder="owner-export-2026-01"
                onChange={(event) => {
                  setDestinationId(event.target.value);
                  setIntentConfirmed(false);
                  resetHandoff();
                }}
              />
            </label>
            <p id="omi-ncp-destination-help" className="muted-copy">
              1–128 characters: letters, numbers, dots, underscores, and hyphens. This identifier is not a path.
            </p>
            <p
              id="omi-ncp-destination-feedback"
              className={`omi-ncp-validation ${destinationValidation.valid ? 'is-valid' : showDestinationFeedback ? 'is-invalid' : ''}`}
              role={showDestinationFeedback && !destinationValidation.valid ? 'alert' : 'status'}
              aria-live="polite"
            >
              {destinationValidation.message}
            </p>
            <label className="omi-analysis-confirmation">
              <input
                type="checkbox"
                checked={intentConfirmed}
                disabled={!destinationValidation.valid}
                onChange={(event) => {
                  setIntentConfirmed(event.target.checked);
                  resetHandoff();
                }}
              />
              <span>I explicitly select this new opaque target for approved-context handoff planning.</span>
            </label>
            <label className="omi-analysis-confirmation">
              <input
                type="checkbox"
                checked={finalConfirmed}
                disabled={!intentConfirmed || !destinationValidation.valid}
                onChange={(event) => {
                  setFinalConfirmed(event.target.checked);
                  setHandoffReady(false);
                }}
              />
              <span>
                Final confirmation: validation is ready, but this action will not export, write, overwrite,
                approve, promote, or mutate project truth.
              </span>
            </label>
            <div className="omi-ncp-actions">
              <button className="primary-button" type="button" disabled={!canPrepareHandoff} onClick={handlePrepareHandoff}>
                Prepare future handoff
              </button>
              <span className="muted-copy">No destination write occurs in this UI.</span>
            </div>
            {handoffReady ? (
              <div className="omi-analysis-notice is-success" role="status" aria-live="polite">
                <strong>Ready for future execution handoff.</strong>
                <span>Confirmation recorded in local UI state only. No export, write, import, or canon mutation occurred.</span>
              </div>
            ) : null}
          </section>

          <section className="omi-ncp-section" aria-labelledby="omi-ncp-import-heading">
            <div className="omi-ncp-section-heading">
              <div>
                <h3 id="omi-ncp-import-heading">External import review</h3>
                <p className="muted-copy">Candidate-only owner review is required for every external import.</p>
              </div>
              <span className="omi-status-badge is-warning">Review required</span>
            </div>
            <p>
              External <code>complete</code> status remains source metadata only. Unknown fields preserve provenance,
              and omitted fields never express deletion intent.
            </p>
            <dl className="omi-ncp-metadata">
              <div><dt>Import validation</dt><dd><code>{NCP_DIAGNOSTIC_FIXTURE.importValidationId}</code></dd></div>
              <div><dt>Owner review status</dt><dd><code>{NCP_DIAGNOSTIC_FIXTURE.ownerReviewStatus}</code></dd></div>
              <div><dt>Local approval</dt><dd>No</dd></div>
              <div><dt>Deletion intent from omissions</dt><dd>No</dd></div>
            </dl>
            <button className="secondary-button" type="button" disabled aria-describedby="omi-ncp-import-reason">
              Import external package
            </button>
            <p id="omi-ncp-import-reason" className="omi-disabled-reason">
              Disabled: this surface does not persist imports or create candidate/review records.
            </p>
          </section>

          <section className="omi-ncp-section" aria-labelledby="omi-ncp-diagnostics-heading">
            <div className="omi-ncp-section-heading">
              <div>
                <h3 id="omi-ncp-diagnostics-heading">Scoped diagnostics and traceability</h3>
                <p className="muted-copy">Support-only diagnostics establish interface integrity, not local approval or truth.</p>
              </div>
              <span className="omi-status-badge is-success">Guardrails active</span>
            </div>
            <div className="omi-ncp-diagnostic-summary" aria-label="NCP diagnostic gates">
              <div><strong>Schema</strong><span>Supported local interface</span></div>
              <div><strong>Standard validation</strong><span>Passed</span></div>
              <div><strong>Trusted round trip</strong><span>Diagnostic gate passed</span></div>
              <div><strong>Matrix quarantine</strong><span>Fail-closed rows retained</span></div>
            </div>
            <details className="omi-ncp-traceability">
              <summary>Inspect provenance and trace references</summary>
              <NcpTraceabilityList />
            </details>
          </section>

          <section className="omi-ncp-section" aria-labelledby="omi-ncp-pending-heading">
            <h3 id="omi-ncp-pending-heading">Pending owner decisions</h3>
            <p>Retention, deletion, overwrite, purge, replacement, rollback, and candidate-bundle execution are not authorized.</p>
            <div className="omi-ncp-actions">
              <button className="secondary-button" type="button" disabled aria-describedby="omi-ncp-destructive-reason">Overwrite target</button>
              <button className="secondary-button" type="button" disabled aria-describedby="omi-ncp-destructive-reason">Delete artifact</button>
              <button className="secondary-button" type="button" disabled aria-describedby="omi-ncp-destructive-reason">Purge retained data</button>
            </div>
            <p id="omi-ncp-destructive-reason" className="omi-disabled-reason">
              Disabled pending explicit owner decisions, audit policy, and rollback semantics.
            </p>
          </section>
        </>
      ) : null}
    </section>
  );
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
    provenanceLinked,
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
        evidenceLinked: ownerInputCount ?? 0,
        provenanceLinked: ownerInputCount ?? 0,
        total: ownerInputCount ?? 0,
        degraded,
        fallback: ZERO_STATE_OWNER_INPUT,
      }),
      action: 'Open live analysis',
      unavailable: degraded
        ? 'Unavailable while OMI status is unavailable'
        : 'Add owner input before analysis',
      disabledReason: 'Owner confirmation and backend-enabled tools are required before submission',
      onAction: !degraded && ownerInputCount > 0
        ? () => onNavigate('live-analysis')
        : null,
    },
    {
      area: 'Candidates',
      count: formatCount(candidateCount, degraded),
      status: degraded ? 'Unavailable' : candidateCount === 0 ? 'Zero State' : 'Candidate: Pending Review',
      statusTone: candidateCount === 0 ? 'is-warning' : '',
      blockers: degraded ? 'Unavailable' : `${formatCount(blockedCount, false)} blocked`,
      evidence: evidenceSummary({
        evidenceLinked,
        provenanceLinked,
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
      area: 'NCP Gateway / Diagnostics',
      count: '1',
      status: 'Contract Ready',
      blockers: 'Execution unavailable',
      evidence: 'Schema, validation, round-trip, and matrix diagnostics only',
      action: 'Open NCP gateway',
      disabledReason: 'No import/export write or project-truth mutation is authorized',
      onAction: () => onNavigate('ncp-diagnostics'),
    },
    {
      area: 'Duplicate Decisions',
      count: formatCount(duplicateCount, degraded),
      status: degraded ? 'Unavailable' : duplicateCount === 0 ? 'No Pending Duplicates' : 'Pending',
      blockers: degraded ? 'Unavailable' : duplicateCount === 0 ? 'None recorded' : `${formatCount(duplicateCount, false)} decisions`,
      evidence: degraded ? 'Unavailable' : 'Provenance required before handoff',
      unavailable: 'Unavailable in this version',
      disabledReason: 'Duplicate decisions are review metadata only',
    },
    {
      area: 'Promotion Handoff Readiness',
      count: formatCount(handoffReadyCount, degraded),
      status: degraded ? 'Unavailable' : handoffReadyCount === 0 ? 'Not Ready' : 'Ready for Handoff',
      blockers: degraded ? 'Unavailable' : handoffReadyCount === 0 ? 'Requirements incomplete' : 'No stored blockers',
      evidence: degraded ? 'Unavailable' : 'Ready means packet complete; Memory/Canon has not changed',
      action: 'Review promotion readiness',
      disabledReason: OMI_DISABLED_APPLY_REASON,
      onAction: () => onNavigate('promotion-handoff'),
    },
    {
      area: 'Promotion Audit Records',
      count: formatCount(promotionAuditCount, degraded),
      status: degraded ? 'Unavailable' : promotionAuditCount === 0 ? 'No Audit Records' : 'Promotion Audit Record',
      blockers: degraded ? 'Unavailable' : 'Audit-only',
      evidence: degraded ? 'Unavailable' : 'Not Applied to Memory/Canon',
      unavailable: 'Unavailable in this version',
      disabledReason: 'Audit records are not canon changes',
    },
    {
      area: 'Deferred Categories',
      count: formatCount(deferred.length, degraded),
      status: degraded ? 'Unavailable' : deferred.length === 0 ? 'None Deferred' : 'Deferred',
      blockers: degraded ? 'Unavailable' : 'Owner review required later',
      evidence: degraded ? 'Unavailable' : 'Source retained when available',
      unavailable: 'Unavailable in this version',
      disabledReason: 'Deferred categories do not mutate Memory/Canon',
    },
    {
      area: 'Warnings / Health',
      count: formatCount(warnings.length + (error ? 1 : 0), false),
      status: degraded ? 'Degraded Error State' : warnings.length === 0 ? 'No Warnings' : 'Warnings Present',
      statusTone: degraded || warnings.length > 0 ? 'is-error' : '',
      blockers: degraded ? 'No inferred counts' : warnings.length === 0 ? 'None recorded' : 'Review warnings',
      evidence: degraded ? error : 'Dashboard counts show review status only',
      unavailable: 'Unavailable in this version',
      disabledReason: 'Health review cannot apply promotion',
    },
  ];

  return (
    <section className="omi-dashboard" data-testid="omi-dashboard" aria-label="OMI Dashboard">
      {isLoading && (
        <OMILoadingState>
          Loading OMI status.
        </OMILoadingState>
      )}

      {error && (
        <section className="omi-error-state" role="alert" aria-label="Degraded OMI status">
          <h2>OMI status unavailable</h2>
          <p>{error}</p>
          <p>No inferred counts are shown while OMI status is degraded.</p>
        </section>
      )}

      <div className="omi-workflow-table-wrap">
        <p
          className="omi-table-scroll-guidance"
          data-testid="omi-dashboard-scroll-guidance"
        >
          Scroll horizontally within this table to review all columns.
        </p>
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
            <h2>Approved Memory/Canon Snapshot</h2>
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
        <h2>Warnings / Health</h2>
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
