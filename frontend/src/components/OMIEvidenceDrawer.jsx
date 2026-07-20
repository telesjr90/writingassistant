import * as Dialog from '@radix-ui/react-dialog';
import { useEffect, useMemo, useRef } from 'react';

export const SOURCE_OPEN_STATES = {
  loading: 'Source record loading',
  missing: 'Source record missing',
  unsafe: 'Source location unsafe',
  out_of_range: 'Source location out of range',
  corrupt: 'Source record corrupt',
  cross_project: 'Source record belongs to another project',
  unavailable: 'Source open action unavailable',
  failed_closed: 'Source open action failed closed',
  available: 'Source record available',
};

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function firstPresent(...values) {
  for (const value of values) {
    if (value !== null && value !== undefined && value !== '') {
      return value;
    }
  }
  return null;
}

function formatStoredValue(value, missingLabel = 'Unavailable') {
  if (value === null || value === undefined || value === '') {
    return missingLabel;
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : missingLabel;
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function normalizeSourceOpenState(value) {
  const key = String(value ?? '').toLowerCase().replaceAll('-', '_').replaceAll(' ', '_');
  return SOURCE_OPEN_STATES[key] ? key : 'unavailable';
}

function getScopeLabel(evidence) {
  const scopeType = formatStoredValue(evidence?.scopeType, 'candidate');
  const candidateId = formatStoredValue(evidence?.candidateId, 'Missing');
  const field = evidence?.fieldKey ? ` / Field: ${formatStoredValue(evidence.fieldKey, 'Missing')}` : '';
  const group = evidence?.groupId ? ` / Group: ${formatStoredValue(evidence.groupId, 'Missing')}` : '';
  const promotion = evidence?.promotionId
    ? ` / Promotion Audit Record: ${formatStoredValue(evidence.promotionId, 'Missing')}`
    : '';
  const approved = evidence?.approvedMemoryCanonId
    ? ` / Approved Memory/Canon item: ${formatStoredValue(evidence.approvedMemoryCanonId, 'Missing')}`
    : '';

  return `${scopeType}: Candidate ${candidateId}${field}${group}${promotion}${approved}`;
}

function getSourceOpenReason(evidence) {
  const sourceLocation = firstPresent(evidence?.sourceLocation, evidence?.source_locator);
  if (!sourceLocation) {
    return 'Source location missing';
  }

  const state = normalizeSourceOpenState(evidence?.sourceOpenState);
  return SOURCE_OPEN_STATES[state];
}

function getSourceOpenDisabled(evidence) {
  const state = normalizeSourceOpenState(evidence?.sourceOpenState);
  const sourceLocation = firstPresent(evidence?.sourceLocation, evidence?.source_locator);
  return !sourceLocation || state !== 'available';
}

function MetadataRow({ label, value, missingLabel = 'Unavailable', isProminent = false }) {
  return (
    <div className={isProminent ? 'is-prominent' : ''}>
      <dt>{label}</dt>
      <dd>{formatStoredValue(value, missingLabel)}</dd>
    </div>
  );
}

export function buildCandidateEvidenceScope(candidate) {
  const candidateId = firstPresent(candidate?.candidate_id, candidate?.candidateId, candidate?.id);
  return {
    scopeType: 'candidate',
    candidateId,
    fieldKey: null,
    sourceType: firstPresent(candidate?.source_type, candidate?.sourceType, candidate?.source),
    sourceLocation: firstPresent(
      candidate?.source_location,
      candidate?.source_locator,
      candidate?.source_id,
      candidate?.raw_idea_id,
      candidate?.idea_id,
    ),
    quoteExactness: firstPresent(candidate?.quote_exactness, candidate?.quoteExactness),
    confidenceSupportLabel: firstPresent(
      candidate?.confidence_support_label,
      candidate?.support_label,
      candidate?.confidence,
    ),
    originalWordingExcerpt: firstPresent(
      candidate?.original_wording_excerpt,
      candidate?.original_excerpt,
      candidate?.excerpt,
    ),
    evidenceSummary: firstPresent(candidate?.evidence_summary, candidate?.evidence_refs),
    supportsClaimNote: firstPresent(candidate?.supports_claim_note, candidate?.support_note),
    limitationsAmbiguity: firstPresent(candidate?.limitations_ambiguity, candidate?.limitations),
    provenanceChain: firstPresent(candidate?.provenance_chain, candidate?.provenance_summary, candidate?.provenance_refs),
    relatedIds: firstPresent(candidate?.related_ids, candidate?.relatedIds, candidate?.evidence_refs),
    timestamps: firstPresent(candidate?.timestamps, candidate?.created_at, candidate?.updated_at),
    sourceHash: firstPresent(candidate?.source_hash, candidate?.sourceHash),
    snapshotHash: firstPresent(candidate?.snapshot_hash, candidate?.snapshotHash),
    sourceOpenState: firstPresent(candidate?.source_open_state, candidate?.sourceOpenState),
  };
}

export function buildFieldEvidenceScope(candidate, field) {
  const candidateScope = buildCandidateEvidenceScope(candidate);
  const fieldKey = firstPresent(field?.field, field?.field_name, field?.name, field?.key, field?.id);

  return {
    ...candidateScope,
    scopeType: 'field',
    fieldKey,
    sourceType: firstPresent(field?.source_type, field?.source, candidateScope.sourceType),
    sourceLocation: firstPresent(field?.source_location, field?.source_locator, candidateScope.sourceLocation),
    quoteExactness: firstPresent(field?.quote_exactness, candidateScope.quoteExactness),
    confidenceSupportLabel: firstPresent(
      field?.confidence_support_label,
      field?.support_label,
      field?.confidence,
      candidateScope.confidenceSupportLabel,
    ),
    originalWordingExcerpt: firstPresent(
      field?.original_wording_excerpt,
      field?.original_excerpt,
      field?.excerpt,
      candidateScope.originalWordingExcerpt,
    ),
    evidenceSummary: firstPresent(field?.evidence_summary, field?.evidence, field?.evidence_refs),
    supportsClaimNote: firstPresent(field?.supports_claim_note, field?.support_note, candidateScope.supportsClaimNote),
    limitationsAmbiguity: firstPresent(field?.limitations_ambiguity, field?.limitations, candidateScope.limitationsAmbiguity),
    provenanceChain: firstPresent(field?.provenance_chain, field?.provenance_summary, field?.provenance, field?.provenance_refs),
    relatedIds: firstPresent(field?.related_ids, field?.relatedIds, field?.evidence_refs, candidateScope.relatedIds),
    timestamps: firstPresent(field?.timestamps, field?.created_at, field?.updated_at, candidateScope.timestamps),
    sourceHash: firstPresent(field?.source_hash, candidateScope.sourceHash),
    snapshotHash: firstPresent(field?.snapshot_hash, candidateScope.snapshotHash),
    sourceOpenState: firstPresent(field?.source_open_state, candidateScope.sourceOpenState),
  };
}

export default function OMIEvidenceDrawer({
  evidence,
  isOpen = false,
  openerRef = null,
  onClose = () => {},
}) {
  const closeTopRef = useRef(null);
  const previousActiveElementRef = useRef(null);
  const sourceReasonId = 'omi-source-open-disabled-reason';
  const copyReasonId = 'omi-source-copy-disabled-reason';
  const reviewReasonId = 'omi-evidence-review-action-disabled-reason';
  const ownerNoteReasonId = 'omi-evidence-owner-note-disabled-reason';
  const scopeLabel = useMemo(() => getScopeLabel(evidence), [evidence]);
  const sourceOpenReason = useMemo(() => getSourceOpenReason(evidence), [evidence]);
  const sourceOpenDisabled = useMemo(() => getSourceOpenDisabled(evidence), [evidence]);
  const sourceLocation = firstPresent(evidence?.sourceLocation, evidence?.source_locator);
  const copyDisabled = !sourceLocation;

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    return () => {
      const focusTarget = openerRef?.current ?? previousActiveElementRef.current;
      if (focusTarget?.isConnected && typeof focusTarget.focus === 'function') {
        focusTarget.focus();
      }
    };
  }, [isOpen, openerRef]);

  function handleOpenChange(nextOpen) {
    if (!nextOpen && isOpen) {
      onClose();
    }
  }

  function handleOpenAutoFocus(event) {
    previousActiveElementRef.current = openerRef?.current ?? document.activeElement;
    event.preventDefault();
    closeTopRef.current?.focus();
  }

  function handleCloseAutoFocus(event) {
    event.preventDefault();
    const focusTarget = openerRef?.current ?? previousActiveElementRef.current;
    if (focusTarget?.isConnected && typeof focusTarget.focus === 'function') {
      focusTarget.focus();
    }
  }

  async function handleCopySourceLocation() {
    if (copyDisabled || !navigator.clipboard) {
      return;
    }
    await navigator.clipboard.writeText(String(sourceLocation));
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={handleOpenChange}>
      {evidence ? (
        <Dialog.Portal>
          <Dialog.Overlay className="omi-evidence-overlay" />
          <Dialog.Content
            asChild
            aria-describedby={undefined}
            onOpenAutoFocus={handleOpenAutoFocus}
            onCloseAutoFocus={handleCloseAutoFocus}
            onPointerDownOutside={(event) => event.preventDefault()}
            onInteractOutside={(event) => event.preventDefault()}
          >
            <aside
              className="omi-evidence-drawer"
              data-testid="omi-evidence-drawer"
            >
        <header className="omi-evidence-header">
          <div>
            <p className="eyebrow">Evidence Scope</p>
            <Dialog.Title asChild>
              <h2>Evidence scope: {scopeLabel}</h2>
            </Dialog.Title>
          </div>
          <Dialog.Close asChild>
            <button
              ref={closeTopRef}
              className="secondary-button"
              type="button"
              data-testid="omi-evidence-drawer-close-top"
              aria-label="Close evidence drawer"
            >
              Close
            </button>
          </Dialog.Close>
        </header>

        <section className="omi-evidence-boundary" aria-label="Evidence and canon boundary">
          <p>Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.</p>
          <p>Viewing evidence does not copy source text into Memory/Canon.</p>
          <p>Confidence indicates support strength, not truth.</p>
        </section>

        <section className="omi-evidence-section omi-evidence-source-section" aria-label="Stored source metadata only">
          <h3>Stored source metadata only</h3>
          <dl className="omi-evidence-metadata">
            <MetadataRow label="Source type" value={evidence.sourceType} missingLabel="Missing" />
            <MetadataRow label="Source location" value={evidence.sourceLocation} missingLabel="Not linked" isProminent />
            <MetadataRow label="Quote exactness" value={evidence.quoteExactness} missingLabel="Unavailable" />
            <MetadataRow
              label="Confidence/support"
              value={evidence.confidenceSupportLabel}
              missingLabel="Unavailable"
            />
          </dl>
          <span className="omi-status-badge">Confidence/support is support strength, not truth.</span>
        </section>

        <section className="omi-evidence-section" aria-label="Stored evidence body">
          <h3>Evidence body</h3>
          <dl className="omi-evidence-metadata">
            <MetadataRow
              label="Original wording/excerpt"
              value={evidence.originalWordingExcerpt}
              missingLabel="Unavailable"
              isProminent
            />
            <MetadataRow label="Evidence summary" value={evidence.evidenceSummary} missingLabel="Missing" />
            <MetadataRow label="Supports claim" value={evidence.supportsClaimNote} missingLabel="Unavailable" />
            <MetadataRow
              label="Limitations / ambiguity"
              value={evidence.limitationsAmbiguity}
              missingLabel="Unavailable"
            />
          </dl>
        </section>

        <section className="omi-evidence-section" aria-label="Stored provenance metadata">
          <h3>Provenance chain and IDs</h3>
          <dl className="omi-evidence-metadata">
            <MetadataRow
              label="Provenance chain"
              value={evidence.provenanceChain}
              missingLabel="Not linked"
              isProminent
            />
            <MetadataRow label="Related IDs" value={evidence.relatedIds} missingLabel="Not linked" />
            <MetadataRow label="Timestamps" value={evidence.timestamps} missingLabel="Unavailable" />
            <MetadataRow label="Source hash" value={evidence.sourceHash} missingLabel="Unavailable" />
            <MetadataRow label="Snapshot hash" value={evidence.snapshotHash} missingLabel="Unavailable" />
          </dl>
        </section>

        <section className="omi-evidence-section" aria-label="Source opening fail-closed states">
          <h3>Source opening state</h3>
          <p className="omi-disabled-reason" id={sourceReasonId} data-testid="omi-source-open-disabled-reason">
            {sourceOpenReason}
          </p>
          <ul className="omi-evidence-state-list" aria-label="Required source-opening states">
            {Object.entries(SOURCE_OPEN_STATES)
              .filter(([key]) => key !== 'available')
              .map(([key, label]) => (
                <li key={key}>{label}</li>
              ))}
          </ul>
          <p className="review-boundary-note">
            Source-opening failures must not create fallback summaries or inferred evidence.
          </p>
        </section>

        <footer className="omi-evidence-footer" aria-label="Evidence Drawer review-only footer actions">
          <fieldset className="omi-evidence-action-group">
            <legend>Navigation / copy</legend>
            <button
              className="secondary-button"
              type="button"
              onClick={handleCopySourceLocation}
              disabled={copyDisabled}
              aria-describedby={copyDisabled ? copyReasonId : undefined}
            >
              Copy source location
            </button>
            <p id={copyReasonId} className="omi-disabled-reason">
              {copyDisabled ? 'Source location missing' : 'Review-only copy action; Memory/Canon is unchanged.'}
            </p>
            <button
              className="secondary-button"
              type="button"
              disabled={sourceOpenDisabled}
              aria-describedby={sourceReasonId}
            >
              Open source record
            </button>
          </fieldset>

          <fieldset className="omi-evidence-action-group">
            <legend>Review marking</legend>
            <button className="secondary-button" type="button" disabled aria-describedby={reviewReasonId}>
              Mark evidence accepted for review
            </button>
            <button className="secondary-button" type="button" disabled aria-describedby={reviewReasonId}>
              Mark insufficient evidence
            </button>
            <p id={reviewReasonId} className="omi-disabled-reason">
              Disabled: evidence review marking is review metadata only and is not wired in this slice.
            </p>
          </fieldset>

          <fieldset className="omi-evidence-action-group">
            <legend>Owner note</legend>
            <button className="secondary-button" type="button" disabled aria-describedby={ownerNoteReasonId}>
              Add owner note
            </button>
            <p id={ownerNoteReasonId} className="omi-disabled-reason">
              Disabled: owner note storage is future review metadata wiring only.
            </p>
          </fieldset>

          <fieldset className="omi-evidence-action-group">
            <legend>Close</legend>
            <Dialog.Close asChild>
              <button
                className="primary-button"
                type="button"
                data-testid="omi-evidence-drawer-close-bottom"
              >
                Close drawer
              </button>
            </Dialog.Close>
          </fieldset>
        </footer>
            </aside>
          </Dialog.Content>
        </Dialog.Portal>
      ) : null}
    </Dialog.Root>
  );
}
