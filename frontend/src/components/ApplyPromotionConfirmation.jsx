import { useEffect, useMemo, useState } from 'react';
import {
  APPLY_PROMOTION_DESTINATION_TYPES,
  ApplyPromotionContractError,
  approveApplyPromotionContract,
  classifyApplyPromotionFailure,
  computeFinalChallengeResponse,
  getApplyPromotionContract,
  getFinalChallengeTemporalState,
  isSafeReviewRouteId,
  issueApplyPromotionFinalChallenge,
  prepareApplyPromotionContract,
  submitApplyPromotion,
} from '../api.js';
import OMIApplyPromotionBlockers from './OMIApplyPromotionBlockers.jsx';

const DESTINATION_CONFIG = Object.freeze({
  approved_character: { label: 'Approved character', primaryField: 'display_name', primaryLabel: 'Display name' },
  approved_location: { label: 'Approved location', primaryField: 'display_name', primaryLabel: 'Display name' },
  approved_timeline_event: { label: 'Approved timeline event', primaryField: 'event_label', primaryLabel: 'Event label' },
  approved_relationship: { label: 'Approved relationship', primaryField: 'relationship_label', primaryLabel: 'Relationship label' },
  approved_organization: { label: 'Approved organization', primaryField: 'display_name', primaryLabel: 'Display name' },
  approved_object: { label: 'Approved object', primaryField: 'display_name', primaryLabel: 'Display name' },
  approved_plot_thread: { label: 'Approved plot thread', primaryField: 'thread_label', primaryLabel: 'Thread label' },
  approved_continuity_record: { label: 'Approved continuity record', primaryField: 'continuity_label', primaryLabel: 'Continuity label' },
  approved_open_question: { label: 'Approved open question', primaryField: 'question_text', primaryLabel: 'Question text' },
});

const REFERENCE_DESTINATION_TYPES = Object.freeze([
  ...APPLY_PROMOTION_DESTINATION_TYPES,
  'approved_memory_index',
]);

const INCOMPLETE_PUBLICATION_STATES = new Set([
  'preparation_artifact_published',
  'preparation_revision_published',
  'preparation_events_incomplete',
]);

const INCOMPLETE_PUBLICATION_CODES = new Set([
  'APPLY_CONTRACT_PREPARATION_INCOMPLETE',
  'APPLY_CONTRACT_PREPARATION_PUBLICATION_INCOMPLETE',
]);

const CHALLENGE_STATE_COPY = Object.freeze({
  idle: 'No final challenge has been issued.',
  active: 'Final challenge active and available for one final confirmation.',
  expired: 'Final challenge expired after its 120-second lifetime.',
  replaced: 'Final challenge was replaced by a newer explicit challenge.',
  restart_invalidated: 'Final challenge was invalidated by a backend restart.',
  consumed: 'Final challenge has been consumed and cannot be reused.',
  unknown: 'Final challenge is no longer recognized by the backend.',
  invalid: 'Final challenge response is malformed and cannot be used.',
});

function compactString(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function formatValue(value, missingLabel = 'Safely unavailable') {
  if (value === null || value === undefined || value === '') {
    return missingLabel;
  }
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

function createIdempotencyKey() {
  return globalThis.crypto?.randomUUID?.() ?? '';
}

function toggleSelection(values, value, selected) {
  if (selected) {
    return values.includes(value) ? values : [...values, value];
  }
  return values.filter((item) => item !== value);
}

function emptyRecordReference() {
  return {
    destination_type: '',
    destination_key: '',
    record_version: '',
    content_hash: '',
  };
}

function recordReferenceComplete(reference) {
  return (
    REFERENCE_DESTINATION_TYPES.includes(reference.destination_type)
    && isSafeReviewRouteId(reference.destination_key)
    && Number.isInteger(Number(reference.record_version))
    && Number(reference.record_version) >= 1
    && Number(reference.record_version) <= 2147483647
    && /^[a-f0-9]{64}$/.test(reference.content_hash)
  );
}

const DEPENDENCY_STATUSES = Object.freeze(['unresolved', 'satisfied', 'not_applicable', 'blocked']);
const MAX_DEPENDENCY_ENTRIES = 256;
const SAFE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const FIELD_ID_PATTERN = /^[A-Za-z][A-Za-z0-9_-]{0,63}$/;

export function createEmptyDependencyInputEntry() {
  return {
    dependency_id: '',
    kind: '',
    required: null,
    status: '',
    target_mode: '',
    target: emptyRecordReference(),
    rationale: '',
    evidence_ref_ids: [],
    provenance_ref_ids: [],
    applicability_rule: '',
  };
}

export function appendDependencyInputEntry(entries) {
  return entries.length >= MAX_DEPENDENCY_ENTRIES
    ? entries
    : [...entries, createEmptyDependencyInputEntry()];
}

export function updateDependencyInputEntry(entries, index, values) {
  return entries.map((entry, entryIndex) => (
    entryIndex === index ? { ...entry, ...values } : entry
  ));
}

export function removeDependencyInputEntry(entries, index) {
  return entries.filter((_, entryIndex) => entryIndex !== index);
}

function uniqueSafeReferences(values) {
  return (
    Array.isArray(values)
    && values.length <= 128
    && new Set(values).size === values.length
    && values.every((value) => SAFE_ID_PATTERN.test(value))
  );
}

function getDependencyInputEntryBlockers(entry, index) {
  const prefix = `Dependency ${index + 1}:`;
  const blockers = [];
  if (!SAFE_ID_PATTERN.test(compactString(entry?.dependency_id))) {
    blockers.push(`${prefix} Enter a stable dependency ID.`);
  }
  if (!FIELD_ID_PATTERN.test(compactString(entry?.kind))) {
    blockers.push(`${prefix} Enter an accepted dependency kind.`);
  }
  if (typeof entry?.required !== 'boolean') {
    blockers.push(`${prefix} Choose required or not required.`);
  }
  if (!DEPENDENCY_STATUSES.includes(entry?.status)) {
    blockers.push(`${prefix} Choose a dependency status.`);
  }
  if (!['none', 'record'].includes(entry?.target_mode)) {
    blockers.push(`${prefix} Choose whether this dependency has a target record.`);
  } else if (entry.target_mode === 'record' && !recordReferenceComplete(entry.target)) {
    blockers.push(`${prefix} Complete the target destination type, key, record version, and 64-character content hash.`);
  }
  const rationale = compactString(entry?.rationale);
  if (!rationale || rationale.length > 4096) {
    blockers.push(`${prefix} Enter a dependency rationale.`);
  }
  if (!uniqueSafeReferences(entry?.evidence_ref_ids) || entry.evidence_ref_ids.length === 0) {
    blockers.push(`${prefix} Select at least one evidence reference.`);
  }
  if (!uniqueSafeReferences(entry?.provenance_ref_ids) || entry.provenance_ref_ids.length === 0) {
    blockers.push(`${prefix} Select at least one provenance reference.`);
  }
  if (compactString(entry?.applicability_rule).length > 2048) {
    blockers.push(`${prefix} Keep the applicability rule at or below 2,048 characters.`);
  }
  return blockers;
}

export function getDependencyResolutionBlockers({
  state,
  dependencies = [],
  rationale,
  evidenceRefIds = [],
}) {
  const blockers = [];
  if (!['unresolved', 'none_declared', 'satisfied', 'blocked'].includes(state)) {
    blockers.push('Choose an explicit dependency decision.');
  }
  const normalizedRationale = compactString(rationale);
  if (!normalizedRationale || normalizedRationale.length > 4096 || !uniqueSafeReferences(evidenceRefIds) || evidenceRefIds.length === 0) {
    blockers.push('Record a dependency rationale with selected evidence.');
  }
  if (!Array.isArray(dependencies) || dependencies.length > MAX_DEPENDENCY_ENTRIES) {
    blockers.push('Dependency entries must remain within the accepted maximum of 256.');
    return blockers;
  }
  if (state === 'none_declared' && dependencies.length > 0) {
    blockers.push('Dependency decision "none_declared" requires zero dependency entries.');
  }
  if (['satisfied', 'blocked'].includes(state) && dependencies.length === 0) {
    blockers.push(`Dependency decision "${state}" requires at least one dependency entry.`);
  }
  dependencies.forEach((entry, index) => {
    blockers.push(...getDependencyInputEntryBlockers(entry, index));
  });
  return blockers;
}

export function normalizeDependencyInputEntry(entry) {
  const normalized = {
    dependency_id: compactString(entry.dependency_id),
    kind: compactString(entry.kind),
    required: entry.required,
    status: entry.status,
    target: entry.target_mode === 'record' ? {
      destination_type: entry.target.destination_type,
      destination_key: compactString(entry.target.destination_key),
      record_version: Number(entry.target.record_version),
      content_hash: compactString(entry.target.content_hash),
    } : null,
    rationale: compactString(entry.rationale),
    evidence_ref_ids: [...entry.evidence_ref_ids],
    provenance_ref_ids: [...entry.provenance_ref_ids],
  };
  const applicabilityRule = compactString(entry.applicability_rule);
  if (applicabilityRule) {
    normalized.applicability_rule = applicabilityRule;
  }
  return normalized;
}

export function buildDependencyResolutionInput({ state, dependencies, rationale, evidenceRefIds }) {
  return {
    state,
    dependencies: dependencies.map(normalizeDependencyInputEntry),
    rationale: compactString(rationale),
    evidence_ref_ids: [...evidenceRefIds],
  };
}

function MetadataRow({ label, value, missingLabel = 'Safely unavailable' }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{formatValue(value, missingLabel)}</dd>
    </div>
  );
}

function ReferenceCheckboxes({ legend, items, idField, selectedIds, onChange }) {
  return (
    <fieldset className="omi-apply-reference-options">
      <legend>{legend}</legend>
      {items.length === 0 ? (
        <p className="muted-copy">No server-derived references are available.</p>
      ) : items.map((item) => {
        const identifier = item?.[idField] ?? '';
        return (
          <label key={identifier} className="omi-checkbox-row">
            <input
              type="checkbox"
              checked={selectedIds.includes(identifier)}
              onChange={(event) => onChange(identifier, event.target.checked)}
            />
            <span>
              <strong>{identifier}</strong>
              {' — '}
              {formatValue(item?.note ?? item?.source_kind ?? item?.locator_id)}
            </span>
          </label>
        );
      })}
    </fieldset>
  );
}

export function getApplyPromotionPreparationBlockers({
  projectId,
  promotionId,
  candidateId,
  authoritativeOwner,
  operation,
  destinationType,
  destinationKey,
  primaryValue,
  factField,
  factValue,
  selectedEvidenceIds,
  selectedProvenanceIds,
  duplicateState,
  duplicateRationale,
  dependencyState,
  dependencyRationale,
  dependencyEntries,
  relationshipEndpoints,
  lineageState,
  supersessionRationale,
  sealedSupersessionConfirmed,
  idempotencyKey,
}) {
  const blockers = [];
  if (!isSafeReviewRouteId(projectId) || !isSafeReviewRouteId(promotionId) || !isSafeReviewRouteId(candidateId)) {
    blockers.push('Exact project, promotion, and candidate association is required.');
  }
  if (!authoritativeOwner?.owner_id || authoritativeOwner?.identity_source !== 'project_local_owner_config') {
    blockers.push('Server-authoritative local owner configuration is unavailable.');
  }
  if (!idempotencyKey) {
    blockers.push('A secure preparation UUID could not be created in this browser.');
  }
  if (!['create', 'update'].includes(operation)) {
    blockers.push('Choose create or update explicitly.');
  }
  if (!APPLY_PROMOTION_DESTINATION_TYPES.includes(destinationType)) {
    blockers.push('Choose an allowed ordinary approved-record destination.');
  }
  if (!isSafeReviewRouteId(destinationKey)) {
    blockers.push('Enter a safe destination key.');
  }
  if (!compactString(primaryValue)) {
    blockers.push('Complete the destination-specific primary field.');
  }
  const factIsOptionalAndEmpty = destinationType === 'approved_open_question'
    && !compactString(factField)
    && !compactString(factValue);
  if (!factIsOptionalAndEmpty && (!isSafeReviewRouteId(factField) || !compactString(factValue))) {
    blockers.push('Complete the typed fact field and value.');
  }
  if (!factIsOptionalAndEmpty && selectedEvidenceIds.length === 0) {
    blockers.push('Select evidence for the proposed fact.');
  }
  if (!factIsOptionalAndEmpty && selectedProvenanceIds.length === 0) {
    blockers.push('Select provenance for the proposed fact.');
  }
  const allowedDuplicateStates = operation === 'create'
    ? ['unresolved', 'distinct_record', 'do_not_apply']
    : ['unresolved', 'update_existing', 'merge_into_existing', 'do_not_apply'];
  if (!allowedDuplicateStates.includes(duplicateState)) {
    blockers.push('Choose a duplicate decision that matches the operation.');
  }
  if (!compactString(duplicateRationale) || selectedEvidenceIds.length === 0) {
    blockers.push('Record a duplicate rationale with selected evidence.');
  }
  blockers.push(...getDependencyResolutionBlockers({
    state: dependencyState,
    dependencies: dependencyEntries,
    rationale: dependencyRationale,
    evidenceRefIds: selectedEvidenceIds,
  }));
  if (destinationType === 'approved_relationship' && !relationshipEndpoints.every(recordReferenceComplete)) {
    blockers.push('Provide two complete relationship endpoint record references.');
  }
  if (['draft_active', 'sealed_active'].includes(lineageState) && !compactString(supersessionRationale)) {
    blockers.push(`Explain the ${lineageState === 'draft_active' ? 'draft' : 'sealed'} supersession.`);
  }
  if (lineageState === 'sealed_active' && !sealedSupersessionConfirmed) {
    blockers.push('Confirm the sealed-contract supersession explicitly.');
  }
  return blockers;
}

export default function ApplyPromotionConfirmation({
  projectId,
  promotion = null,
  candidate = null,
  onCancel = () => {},
}) {
  const promotionId = compactString(promotion?.promotion_id);
  const candidateId = compactString(candidate?.candidate_id ?? candidate?.candidateId ?? candidate?.id);
  const [contractView, setContractView] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isIssuingChallenge, setIsIssuingChallenge] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [requestError, setRequestError] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [preparationResult, setPreparationResult] = useState(null);
  const [approvalResult, setApprovalResult] = useState(null);
  const [recoveryRequest, setRecoveryRequest] = useState(null);
  const [preparationIdempotencyKey] = useState(createIdempotencyKey);
  const [approvalIdempotencyKey] = useState(createIdempotencyKey);
  const [challengeIdempotencyKey, setChallengeIdempotencyKey] = useState(createIdempotencyKey);
  const [finalApplyIdempotencyKey, setFinalApplyIdempotencyKey] = useState(createIdempotencyKey);
  const [challenge, setChallenge] = useState(null);
  const [challengeState, setChallengeState] = useState('idle');
  const [challengeSecondsRemaining, setChallengeSecondsRemaining] = useState(0);
  const [challengeNotice, setChallengeNotice] = useState('');
  const [finalConfirmationChecked, setFinalConfirmationChecked] = useState(false);
  const [retainedFinalApplyRequest, setRetainedFinalApplyRequest] = useState(null);
  const [applyResult, setApplyResult] = useState(null);
  const [applyState, setApplyState] = useState('not_started');

  const [operation, setOperation] = useState('');
  const [destinationType, setDestinationType] = useState('');
  const [destinationKey, setDestinationKey] = useState('');
  const [primaryValue, setPrimaryValue] = useState('');
  const [factField, setFactField] = useState('');
  const [factValue, setFactValue] = useState('');
  const [selectedEvidenceIds, setSelectedEvidenceIds] = useState([]);
  const [selectedProvenanceIds, setSelectedProvenanceIds] = useState([]);
  const [duplicateState, setDuplicateState] = useState('');
  const [duplicateRationale, setDuplicateRationale] = useState('');
  const [reviewedCandidate, setReviewedCandidate] = useState(false);
  const [dependencyState, setDependencyState] = useState('');
  const [dependencyRationale, setDependencyRationale] = useState('');
  const [dependencyEntries, setDependencyEntries] = useState([]);
  const [ownerNote, setOwnerNote] = useState('');
  const [supersessionRationale, setSupersessionRationale] = useState('');
  const [sealedSupersessionConfirmed, setSealedSupersessionConfirmed] = useState(false);
  const [relationshipEndpoints, setRelationshipEndpoints] = useState([
    emptyRecordReference(),
    emptyRecordReference(),
  ]);
  const [approvalConfirmed, setApprovalConfirmed] = useState(false);

  async function refreshContract(revision = null) {
    const view = await getApplyPromotionContract(projectId, promotionId, { revision });
    setContractView(view);
    return view;
  }

  useEffect(() => {
    if (!isSafeReviewRouteId(projectId) || !isSafeReviewRouteId(promotionId)) {
      setContractView(null);
      return undefined;
    }
    let cancelled = false;
    setIsLoading(true);
    setRequestError(null);
    getApplyPromotionContract(projectId, promotionId)
      .then((view) => {
        if (!cancelled) {
          setContractView(view);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setRequestError(error);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, promotionId]);

  useEffect(() => {
    if (!challenge || challengeState !== 'active') {
      return undefined;
    }
    function updateChallengeClock() {
      const temporal = getFinalChallengeTemporalState(challenge);
      setChallengeSecondsRemaining(temporal.secondsRemaining);
      if (temporal.state === 'expired') {
        setChallengeState('expired');
        setFinalConfirmationChecked(false);
      }
    }
    updateChallengeClock();
    const timer = globalThis.setInterval(updateChallengeClock, 1000);
    return () => globalThis.clearInterval(timer);
  }, [challenge, challengeState]);

  const lineage = contractView?.lineage ?? {};
  const lineageState = lineage.state ?? 'unavailable';
  const selectedRevision = contractView?.selected_revision ?? null;
  const sealedRevision = contractView?.sealed_revision ?? null;
  const authoritativeOwner = contractView?.authoritative_owner ?? null;
  const authorityEvidence = useMemo(
    () => (Array.isArray(lineage?.authority?.evidence_refs) ? lineage.authority.evidence_refs : []),
    [lineage],
  );
  const authorityProvenance = useMemo(
    () => (Array.isArray(lineage?.authority?.provenance_refs) ? lineage.authority.provenance_refs : []),
    [lineage],
  );
  const serverBlockers = Array.isArray(contractView?.blockers) ? contractView.blockers : [];
  const incompletePublication = INCOMPLETE_PUBLICATION_STATES.has(lineageState)
    || INCOMPLETE_PUBLICATION_CODES.has(requestError?.code);
  const canRetryIncompletePublication = Boolean(recoveryRequest);
  const destinationConfig = DESTINATION_CONFIG[destinationType] ?? null;

  const preparationBlockers = getApplyPromotionPreparationBlockers({
    projectId,
    promotionId,
    candidateId,
    authoritativeOwner,
    operation,
    destinationType,
    destinationKey,
    primaryValue,
    factField,
    factValue,
    selectedEvidenceIds,
    selectedProvenanceIds,
    duplicateState,
    duplicateRationale,
    dependencyState,
    dependencyRationale,
    dependencyEntries,
    relationshipEndpoints,
    lineageState,
    supersessionRationale,
    sealedSupersessionConfirmed,
    idempotencyKey: preparationIdempotencyKey,
  });
  if (incompletePublication && !canRetryIncompletePublication) {
    preparationBlockers.push('Incomplete publication requires the original retained preparation UUID, which is unavailable in this browser state.');
  }

  const approvalBlockers = [];
  if (lineageState !== 'draft_active') {
    approvalBlockers.push('Backend lineage is not draft_active.');
  }
  if (!selectedRevision?.revision) {
    approvalBlockers.push('No exact published revision is selected.');
  }
  if (!approvalIdempotencyKey) {
    approvalBlockers.push('A secure approval UUID could not be created in this browser.');
  }
  if (incompletePublication) {
    approvalBlockers.push('Preparation publication is incomplete.');
  }
  serverBlockers
    .filter((blocker) => blocker?.code !== 'APPLY_CONTRACT_NOT_PREPARED')
    .forEach((blocker) => approvalBlockers.push(`Backend blocker: ${blocker?.code ?? 'UNKNOWN_BLOCKER'}.`));
  if (!approvalConfirmed) {
    approvalBlockers.push('Explicit contract approval confirmation is incomplete.');
  }

  const sealedContractRevision = sealedRevision?.revision?.revision ?? null;
  const sealedContractHash = sealedRevision?.sealed_contract_hash ?? null;
  const sealedBeforeStateToken = sealedRevision?.revision?.before_state?.snapshot_token ?? null;
  const challengeIssuanceBlockers = [];
  if (lineageState !== 'sealed_active') {
    challengeIssuanceBlockers.push('Backend lineage is not sealed_active.');
  }
  if (contractView?.revalidation?.eligible_for_final_challenge !== true) {
    challengeIssuanceBlockers.push('Backend revalidation does not permit final challenge issuance.');
  }
  if (!sealedContractRevision || !sealedContractHash || !sealedBeforeStateToken) {
    challengeIssuanceBlockers.push('The exact sealed revision, C2, and before-state token are unavailable.');
  }
  if (!challengeIdempotencyKey) {
    challengeIssuanceBlockers.push('A secure final-challenge UUID could not be created in this browser.');
  }
  serverBlockers.forEach((blocker) => (
    challengeIssuanceBlockers.push(`Backend blocker: ${blocker?.code ?? 'UNKNOWN_BLOCKER'}.`)
  ));

  const exactApplyRetry = Boolean(
    retainedFinalApplyRequest
    && ['recovery_required', 'failed'].includes(applyState),
  );
  const finalApplyBlockers = [];
  if (!exactApplyRetry) {
    if (lineageState !== 'sealed_active') {
      finalApplyBlockers.push('Backend lineage is not sealed_active.');
    }
    if (challengeState !== 'active') {
      finalApplyBlockers.push('An active final challenge is required.');
    }
    if (!challenge?.challenge_response) {
      finalApplyBlockers.push('The anti-replay challenge response is unavailable.');
    }
    if (!finalConfirmationChecked) {
      finalApplyBlockers.push('Explicit final apply confirmation is incomplete.');
    }
  }
  if (!finalApplyIdempotencyKey) {
    finalApplyBlockers.push('A secure final-apply UUID could not be created in this browser.');
  }
  if (contractView?.revalidation?.eligible_for_final_challenge !== true && !exactApplyRetry) {
    finalApplyBlockers.push('Backend revalidation no longer permits the sealed final operation.');
  }
  serverBlockers.forEach((blocker) => (
    finalApplyBlockers.push(`Backend blocker: ${blocker?.code ?? 'UNKNOWN_BLOCKER'}.`)
  ));
  if (applyState === 'completed' || applyState === 'replayed') {
    finalApplyBlockers.push('This promotion already has an authoritative completed apply result.');
  }

  const visibleBlockers = [...new Set([
    ...preparationBlockers.map((blocker) => `Preparation: ${blocker}`),
    ...approvalBlockers.map((blocker) => `Approval: ${blocker}`),
    ...challengeIssuanceBlockers.map((blocker) => `Challenge: ${blocker}`),
    ...finalApplyBlockers.map((blocker) => `Final apply: ${blocker}`),
  ])];

  function buildPayload() {
    const facts = destinationType === 'approved_open_question'
      && !compactString(factField)
      && !compactString(factValue)
      ? []
      : [{
        field: compactString(factField),
        value: compactString(factValue),
        evidence_ref_ids: selectedEvidenceIds,
        provenance_ref_ids: selectedProvenanceIds,
      }];
    const payload = {
      payload_type: destinationType,
      [destinationConfig.primaryField]: compactString(primaryValue),
      facts,
    };
    if (destinationType === 'approved_relationship') {
      payload.endpoint_refs = relationshipEndpoints.map((reference) => ({
        destination_type: reference.destination_type,
        destination_key: compactString(reference.destination_key),
        record_version: Number(reference.record_version),
        content_hash: compactString(reference.content_hash),
      }));
    }
    return payload;
  }

  function buildSupersession() {
    if (lineageState === 'draft_active') {
      return {
        kind: 'draft',
        superseded_revision: lineage.latest_revision,
        superseded_draft_scope_hash: lineage.latest_draft_scope_hash,
        rationale: compactString(supersessionRationale),
      };
    }
    if (lineageState === 'sealed_active') {
      return {
        kind: 'sealed',
        superseded_revision: lineage.active_sealed_revision,
        sealed_contract_hash: lineage.active_sealed_contract_hash,
        rationale: compactString(supersessionRationale),
        confirmed: sealedSupersessionConfirmed,
      };
    }
    return null;
  }

  function buildPreparationRequest() {
    return {
      idempotency_key: preparationIdempotencyKey,
      expected_latest_revision: lineage.latest_revision ?? null,
      expected_latest_draft_scope_hash: lineage.latest_draft_scope_hash ?? null,
      operation,
      approved_destination_type: destinationType,
      destination_key: compactString(destinationKey),
      payload: buildPayload(),
      duplicate_resolution: {
        state: duplicateState,
        rationale: compactString(duplicateRationale),
        evidence_ref_ids: selectedEvidenceIds,
        reviewed_candidate_ids: reviewedCandidate ? [candidateId] : [],
        reviewed_approved_records: [],
      },
      dependency_resolution: {
        ...buildDependencyResolutionInput({
          state: dependencyState,
          dependencies: dependencyEntries,
          rationale: dependencyRationale,
          evidenceRefIds: selectedEvidenceIds,
        }),
      },
      supersession: buildSupersession(),
      ...(compactString(ownerNote) ? { owner_note: compactString(ownerNote) } : {}),
    };
  }

  async function handlePrepare(event) {
    event.preventDefault();
    setStatusMessage('');
    setRequestError(null);
    if (preparationBlockers.length > 0) {
      setRequestError(new ApplyPromotionContractError('Preparation is blocked by the visible requirements.'));
      return;
    }
    const request = recoveryRequest ?? buildPreparationRequest();
    setIsPreparing(true);
    try {
      const response = await prepareApplyPromotionContract(projectId, promotionId, request);
      setPreparationResult(response);
      setRecoveryRequest(null);
      await refreshContract(response.revision);
      setStatusMessage(
        response.recovery_status === 'recovered'
          ? 'Preparation publication recovered from immutable saved bytes.'
          : 'Immutable preparation and draft revision published.',
      );
    } catch (error) {
      const contractError = error instanceof ApplyPromotionContractError
        ? error
        : new ApplyPromotionContractError('Preparation failed closed.');
      if (INCOMPLETE_PUBLICATION_CODES.has(contractError.code)) {
        setRecoveryRequest(request);
      }
      setRequestError(contractError);
    } finally {
      setIsPreparing(false);
    }
  }

  async function handleApprove(event) {
    event.preventDefault();
    setStatusMessage('');
    setRequestError(null);
    if (approvalBlockers.length > 0) {
      setRequestError(new ApplyPromotionContractError('Approval is blocked by the visible requirements.'));
      return;
    }
    setIsApproving(true);
    try {
      const response = await approveApplyPromotionContract(
        projectId,
        promotionId,
        selectedRevision.revision,
        {
          idempotency_key: approvalIdempotencyKey,
          expected_latest_revision: selectedRevision.revision,
          expected_latest_draft_scope_hash: selectedRevision.draft_scope_hash,
          before_state_snapshot_token: selectedRevision.before_state.snapshot_token,
          confirmed: true,
          approval_method: 'explicit_apply_contract_approval',
        },
      );
      setApprovalResult(response);
      setApprovalConfirmed(false);
      await refreshContract(selectedRevision.revision);
      setStatusMessage('Contract approval recorded and the exact revision seal is active. Memory/Canon remains unchanged.');
    } catch (error) {
      setRequestError(error instanceof ApplyPromotionContractError
        ? error
        : new ApplyPromotionContractError('Approval failed closed.'));
    } finally {
      setIsApproving(false);
    }
  }

  async function handleIssueChallenge({ fresh = false } = {}) {
    setStatusMessage('');
    setRequestError(null);
    if (challengeIssuanceBlockers.length > 0) {
      setRequestError(new ApplyPromotionContractError('Final challenge issuance is blocked by authoritative contract state.'));
      return;
    }
    const key = fresh ? createIdempotencyKey() : challengeIdempotencyKey;
    if (!key) {
      setRequestError(new ApplyPromotionContractError('A secure final-challenge UUID could not be created.'));
      return;
    }
    if (fresh) {
      setChallengeIdempotencyKey(key);
      setChallengeNotice(
        challengeState === 'active'
          ? 'The prior challenge was explicitly replaced. Only the new challenge may be used.'
          : 'A fresh challenge was explicitly requested for the active seal.',
      );
      setFinalConfirmationChecked(false);
      setRetainedFinalApplyRequest(null);
      if (applyState === 'not_committed') {
        setFinalApplyIdempotencyKey(createIdempotencyKey());
        setApplyState('not_started');
        setApplyResult(null);
      }
    }
    setIsIssuingChallenge(true);
    try {
      const response = await issueApplyPromotionFinalChallenge(projectId, promotionId, {
        revision: sealedContractRevision,
        sealedContractHash,
        beforeStateSnapshotToken: sealedBeforeStateToken,
        idempotencyKey: key,
      });
      const scope = response?.challenge_scope;
      if (
        scope?.project_id !== projectId
        || scope?.promotion_id !== promotionId
        || scope?.revision !== sealedContractRevision
        || scope?.sealed_contract_hash !== sealedContractHash
        || scope?.before_state_snapshot_token !== sealedBeforeStateToken
      ) {
        throw new ApplyPromotionContractError('Returned final challenge does not match the active sealed contract.');
      }
      const challengeResponse = await computeFinalChallengeResponse(response);
      const acceptedChallenge = { ...response, challenge_response: challengeResponse };
      const temporal = getFinalChallengeTemporalState(acceptedChallenge);
      if (temporal.state !== 'active') {
        throw new ApplyPromotionContractError('Returned final challenge is already expired or has invalid timing.');
      }
      setChallenge(acceptedChallenge);
      setChallengeState('active');
      setChallengeSecondsRemaining(temporal.secondsRemaining);
      setChallengeNotice(
        response.replayed
          ? 'The same unexpired challenge was replayed for the retained request UUID.'
          : fresh
            ? 'A fresh challenge replaced any prior outstanding challenge for this seal.'
            : 'Final challenge issued by explicit POST.',
      );
      setStatusMessage('Final challenge ready for one explicit final confirmation.');
    } catch (error) {
      const contractError = error instanceof ApplyPromotionContractError
        ? error
        : new ApplyPromotionContractError('Final challenge issuance failed closed.');
      const classified = classifyApplyPromotionFailure(contractError.code);
      setChallengeState(classified.challengeState ?? 'invalid');
      setFinalConfirmationChecked(false);
      setRequestError(contractError);
    } finally {
      setIsIssuingChallenge(false);
    }
  }

  async function handleFinalApply(event) {
    event.preventDefault();
    setStatusMessage('');
    setRequestError(null);
    if (finalApplyBlockers.length > 0) {
      setRequestError(new ApplyPromotionContractError('Final apply is blocked by the visible requirements.'));
      return;
    }
    const request = retainedFinalApplyRequest ?? {
      promotionId,
      revision: sealedContractRevision,
      sealedContractHash,
      beforeStateSnapshotToken: sealedBeforeStateToken,
      challengeId: challenge.challenge_id,
      challengeResponse: challenge.challenge_response,
      idempotencyKey: finalApplyIdempotencyKey,
    };
    setRetainedFinalApplyRequest(request);
    setIsApplying(true);
    setApplyState(exactApplyRetry ? 'recovering' : 'pending');
    try {
      const response = await submitApplyPromotion(projectId, request);
      const sealedRecord = sealedRevision?.revision;
      if (
        response?.lineage_state !== 'applied'
        || response?.promotion_id !== promotionId
        || response?.revision !== request.revision
        || response?.sealed_contract_hash !== request.sealedContractHash
        || response?.approved_record_hash !== sealedRecord?.approved_record_hash
        || response?.approved_record_size !== sealedRecord?.approved_record_size
      ) {
        throw new ApplyPromotionContractError('Completed apply response does not match the exact sealed approved-record pair.');
      }
      setApplyResult(response);
      setApplyState(response.replayed ? 'replayed' : 'completed');
      setChallengeState('consumed');
      setFinalConfirmationChecked(false);
      await refreshContract(response.revision);
      setStatusMessage(
        response.replayed
          ? 'Authoritative completed replay or committed recovery verified and refreshed.'
          : 'Apply completed once and authoritative contract state refreshed.',
      );
    } catch (error) {
      const contractError = error instanceof ApplyPromotionContractError
        ? error
        : new ApplyPromotionContractError('Final apply failed closed.');
      const classified = classifyApplyPromotionFailure(contractError.code);
      if (classified.challengeState) {
        setChallengeState(classified.challengeState);
        setFinalConfirmationChecked(false);
      }
      setApplyState(classified.applyState);
      if (classified.challengeState && classified.applyState === 'not_started') {
        setRetainedFinalApplyRequest(null);
      }
      if (classified.applyState === 'blocked') {
        setRetainedFinalApplyRequest(null);
        setFinalConfirmationChecked(false);
      }
      setRequestError(contractError);
      try {
        await refreshContract(request.revision);
      } catch {
        // Preserve the original final-apply failure as the owner-visible error.
      }
    } finally {
      setIsApplying(false);
    }
  }

  function updateEndpoint(index, field, value) {
    setRelationshipEndpoints((current) => current.map((reference, itemIndex) => (
      itemIndex === index ? { ...reference, [field]: value } : reference
    )));
  }

  function updateDependencyEntry(index, values) {
    setDependencyEntries((current) => updateDependencyInputEntry(current, index, values));
  }

  function updateDependencyTarget(index, field, value) {
    setDependencyEntries((current) => updateDependencyInputEntry(current, index, {
      target: {
        ...current[index].target,
        [field]: value,
      },
    }));
  }

  function toggleDependencyReference(index, field, value, selected) {
    setDependencyEntries((current) => updateDependencyInputEntry(current, index, {
      [field]: toggleSelection(current[index][field], value, selected),
    }));
  }

  const formLockedToRecovery = Boolean(recoveryRequest);
  const preparationDisabled = preparationBlockers.length > 0 || isPreparing || isLoading;
  const approvalDisabled = approvalBlockers.length > 0 || isApproving || isLoading;
  const challengeDisabled = challengeIssuanceBlockers.length > 0 || isIssuingChallenge || isLoading;
  const finalApplyDisabled = finalApplyBlockers.length > 0 || isApplying || isLoading;
  const blockerReasonId = 'omi-apply-promotion-visible-blocker-reasons';

  return (
    <section
      className="omi-apply-confirmation"
      data-testid="omi-apply-promotion-confirmation"
      aria-label="Apply-Promotion contract preparation, approval, and final confirmation"
    >
      <header className="omi-apply-guard-header">
        <div>
          <p className="eyebrow">Owner-controlled apply contract</p>
          <h2>Prepare and approve an immutable revision</h2>
        </div>
        <span className={`omi-status-badge ${applyResult ? '' : 'is-warning'}`}>
          {applyResult ? 'Applied by explicit owner-controlled flow' : 'Not Applied to Memory/Canon'}
        </span>
      </header>

      <section className="omi-apply-boundary" aria-label="Apply-Promotion boundary copy">
        <p>Preparation and approval alone do not apply this promotion.</p>
        <p>Queue presence is not approval. Confidence is not truth. Candidate persistence is not canon.</p>
        <p>The server-configured local owner is authoritative; this interface cannot edit owner configuration.</p>
        <p>Only an explicit final challenge and confirmed final POST can invoke the approved-record mutation path.</p>
      </section>

      <OMIApplyPromotionBlockers blockers={visibleBlockers} describedById={blockerReasonId} />

      {isLoading && <p className="omi-apply-loading" role="status">Loading authoritative contract lineage…</p>}
      {statusMessage && (
        <p className="omi-apply-status" role="status" aria-live="polite" tabIndex="-1">
          {statusMessage}
        </p>
      )}
      {requestError && (
        <p className="error-copy" role="alert">
          {requestError.code ? `${requestError.code}: ` : ''}{requestError.message}
        </p>
      )}

      {incompletePublication && (
        <section className="omi-apply-recovery-state" role="status" aria-label="Incomplete preparation publication">
          <h3>Preparation publication incomplete</h3>
          <p>Retry the same preparation request and retained UUID to resume exact saved publication.</p>
          <p>
            {canRetryIncompletePublication
              ? 'The original request and UUID remain retained in this browser; fields are locked during recovery.'
              : 'The original UUID is not available in this browser state, so approval remains blocked.'}
          </p>
        </section>
      )}

      {preparationResult?.recovery_status === 'recovered' && (
        <section className="omi-apply-recovered-state" role="status" aria-label="Recovered preparation publication">
          <h3>Preparation publication recovered from immutable saved bytes</h3>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Preparation ID" value={preparationResult.preparation_id} />
            <MetadataRow label="Revision" value={preparationResult.revision} />
            <MetadataRow label="Revision path" value={preparationResult.revision_path} />
          </dl>
          <p>No current candidate, before state, or owner value was used to reconstruct the saved revision.</p>
        </section>
      )}

      <div className="omi-apply-section-grid">
        <section className="omi-apply-section" aria-label="Exact promotion association">
          <h3>Exact promotion association</h3>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Project ID" value={projectId} />
            <MetadataRow label="Promotion ID" value={promotionId} missingLabel="Missing exact promotion" />
            <MetadataRow label="Candidate ID" value={candidateId} missingLabel="Missing associated candidate" />
            <MetadataRow label="Promotion status" value={promotion?.status} />
          </dl>
        </section>

        <section className="omi-apply-section" aria-label="Authoritative owner identity">
          <h3>Authoritative owner</h3>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Display name" value={authoritativeOwner?.display_name} />
            <MetadataRow label="Owner ID" value={authoritativeOwner?.owner_id} />
            <MetadataRow label="Identity source" value={authoritativeOwner?.identity_source} />
            <MetadataRow label="Configuration version" value={authoritativeOwner?.config_version} />
          </dl>
          <p className="muted-copy">Read-only server authority; it does not establish who is operating this local client.</p>
        </section>
      </div>

      <form className="omi-apply-preparation-form" onSubmit={handlePrepare}>
        <div className="section-heading">
          <div>
            <h3>Prepare immutable revision</h3>
            <p className="muted-copy">The retained preparation UUID is reused for every retry of this publication.</p>
          </div>
          <span className="omi-status-badge">Lineage: {lineageState}</span>
        </div>

        <fieldset disabled={formLockedToRecovery || isPreparing}>
          <legend>Operation and destination</legend>
          <div className="omi-apply-form-grid">
            <label className="field-label">
              Operation
              <select value={operation} onChange={(event) => {
                setOperation(event.target.value);
                setDuplicateState('');
              }}>
                <option value="">Choose create or update</option>
                <option value="create">Create a new approved record</option>
                <option value="update">Update an existing approved record</option>
              </select>
            </label>
            <label className="field-label">
              Approved destination type
              <select value={destinationType} onChange={(event) => {
                setDestinationType(event.target.value);
                setPrimaryValue('');
              }}>
                <option value="">Choose an ordinary destination</option>
                {APPLY_PROMOTION_DESTINATION_TYPES.map((value) => (
                  <option key={value} value={value}>{DESTINATION_CONFIG[value].label}</option>
                ))}
              </select>
            </label>
            <label className="field-label">
              Destination key
              <input value={destinationKey} onChange={(event) => setDestinationKey(event.target.value)} />
            </label>
            {destinationConfig && (
              <label className="field-label">
                {destinationConfig.primaryLabel}
                <input value={primaryValue} onChange={(event) => setPrimaryValue(event.target.value)} />
              </label>
            )}
          </div>
          <p className="muted-copy">Ordinary preparation never offers approved_memory_index.</p>
        </fieldset>

        {destinationType === 'approved_relationship' && (
          <fieldset disabled={formLockedToRecovery || isPreparing}>
            <legend>Relationship endpoint record references</legend>
            <div className="omi-apply-endpoint-grid">
              {relationshipEndpoints.map((reference, index) => (
                <div className="omi-apply-endpoint" key={`endpoint-${index + 1}`}>
                  <h4>Endpoint {index + 1}</h4>
                  <label className="field-label">
                    Destination type
                    <select value={reference.destination_type} onChange={(event) => updateEndpoint(index, 'destination_type', event.target.value)}>
                      <option value="">Choose referenced type</option>
                      {REFERENCE_DESTINATION_TYPES.map((value) => <option key={value} value={value}>{value}</option>)}
                    </select>
                  </label>
                  <label className="field-label">Destination key<input value={reference.destination_key} onChange={(event) => updateEndpoint(index, 'destination_key', event.target.value)} /></label>
                  <label className="field-label">Record version<input type="number" min="1" value={reference.record_version} onChange={(event) => updateEndpoint(index, 'record_version', event.target.value)} /></label>
                  <label className="field-label">Content hash<input className="omi-monospace-input" value={reference.content_hash} onChange={(event) => updateEndpoint(index, 'content_hash', event.target.value)} /></label>
                </div>
              ))}
            </div>
          </fieldset>
        )}

        <fieldset disabled={formLockedToRecovery || isPreparing}>
          <legend>Typed fact and authority references</legend>
          <div className="omi-apply-form-grid">
            <label className="field-label">
              Fact field ID
              <input value={factField} onChange={(event) => setFactField(event.target.value)} />
            </label>
            <label className="field-label">
              Owner-entered fact value
              <input value={factValue} onChange={(event) => setFactValue(event.target.value)} />
            </label>
          </div>
          {destinationType === 'approved_open_question' && (
            <p className="muted-copy">A fact is optional for an approved open question; leave both fact inputs empty to omit it.</p>
          )}
          <div className="omi-apply-reference-grid">
            <ReferenceCheckboxes
              legend="Evidence references"
              items={authorityEvidence}
              idField="ref_id"
              selectedIds={selectedEvidenceIds}
              onChange={(value, selected) => setSelectedEvidenceIds((current) => toggleSelection(current, value, selected))}
            />
            <ReferenceCheckboxes
              legend="Provenance references"
              items={authorityProvenance}
              idField="provenance_id"
              selectedIds={selectedProvenanceIds}
              onChange={(value, selected) => setSelectedProvenanceIds((current) => toggleSelection(current, value, selected))}
            />
          </div>
        </fieldset>

        <fieldset disabled={formLockedToRecovery || isPreparing}>
          <legend>Explicit duplicate and dependency decisions</legend>
          <div className="omi-apply-decision-grid">
            <div>
              <label className="field-label">
                Duplicate decision
                <select value={duplicateState} onChange={(event) => setDuplicateState(event.target.value)}>
                  <option value="">Choose a duplicate decision</option>
                  <option value="unresolved">Unresolved — blocks approval</option>
                  {operation === 'create' && <option value="distinct_record">Distinct record</option>}
                  {operation === 'update' && <option value="update_existing">Update existing</option>}
                  {operation === 'update' && <option value="merge_into_existing">Merge into existing</option>}
                  <option value="do_not_apply">Do not apply — blocks approval</option>
                </select>
              </label>
              <label className="field-label">Duplicate rationale<textarea value={duplicateRationale} onChange={(event) => setDuplicateRationale(event.target.value)} /></label>
              <label className="omi-checkbox-row">
                <input type="checkbox" checked={reviewedCandidate} onChange={(event) => setReviewedCandidate(event.target.checked)} />
                I reviewed the selected candidate ID for this duplicate decision.
              </label>
            </div>
            <div>
              <label className="field-label">
                Dependency decision
                <select value={dependencyState} onChange={(event) => setDependencyState(event.target.value)}>
                  <option value="">Choose a dependency decision</option>
                  <option value="unresolved">Unresolved — blocks approval</option>
                  <option value="none_declared">No dependencies declared</option>
                  <option value="satisfied">Declared dependencies satisfied</option>
                  <option value="blocked">Blocked dependency — blocks approval</option>
                </select>
              </label>
              <label className="field-label">Dependency rationale<textarea value={dependencyRationale} onChange={(event) => setDependencyRationale(event.target.value)} /></label>
              <p className="muted-copy">
                No dependency value is inferred. No dependencies declared requires zero entries; satisfied and blocked require at least one complete owner-entered entry.
              </p>
            </div>
          </div>

          <section className="omi-apply-dependency-editor" aria-labelledby="omi-apply-dependency-entries-heading">
            <div className="omi-apply-dependency-editor-heading">
              <div>
                <h4 id="omi-apply-dependency-entries-heading">Dependency entries (maximum 256)</h4>
                <p className="muted-copy">Each entry is closed to the accepted preparation schema. Server validation remains authoritative.</p>
              </div>
              <button
                className="secondary-button"
                type="button"
                disabled={dependencyState === 'none_declared' || !dependencyState || dependencyEntries.length >= MAX_DEPENDENCY_ENTRIES}
                onClick={() => setDependencyEntries((current) => appendDependencyInputEntry(current))}
              >
                Add dependency entry
              </button>
            </div>

            {dependencyState === 'none_declared' && dependencyEntries.length === 0 && (
              <p className="omi-apply-dependency-empty" role="status">No dependency entries are permitted for this decision.</p>
            )}
            {dependencyEntries.length === 0 && dependencyState !== 'none_declared' && (
              <p className="omi-apply-dependency-empty" role="status">No dependency entries have been added.</p>
            )}

            {dependencyEntries.map((entry, index) => {
              const entryBlockers = getDependencyInputEntryBlockers(entry, index);
              const entryBlockerId = `omi-apply-dependency-${index + 1}-blockers`;
              return (
                <fieldset
                  className="omi-apply-dependency-entry"
                  key={`dependency-${index + 1}`}
                  aria-describedby={entryBlockerId}
                >
                  <legend>Dependency {index + 1}</legend>
                  <div className="omi-apply-dependency-entry-heading">
                    <p>Enter only owner-reviewed dependency facts and references.</p>
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() => setDependencyEntries((current) => removeDependencyInputEntry(current, index))}
                    >
                      Remove dependency
                    </button>
                  </div>

                  <div className="omi-apply-dependency-grid">
                    <label className="field-label">
                      Dependency ID
                      <input value={entry.dependency_id} onChange={(event) => updateDependencyEntry(index, { dependency_id: event.target.value })} />
                    </label>
                    <label className="field-label">
                      Dependency kind
                      <input value={entry.kind} onChange={(event) => updateDependencyEntry(index, { kind: event.target.value })} />
                    </label>
                    <label className="field-label">
                      Required classification
                      <select
                        value={entry.required === null ? '' : String(entry.required)}
                        onChange={(event) => updateDependencyEntry(index, {
                          required: event.target.value === '' ? null : event.target.value === 'true',
                        })}
                      >
                        <option value="">Choose required classification</option>
                        <option value="true">Required</option>
                        <option value="false">Not required</option>
                      </select>
                    </label>
                    <label className="field-label">
                      Dependency status
                      <select value={entry.status} onChange={(event) => updateDependencyEntry(index, { status: event.target.value })}>
                        <option value="">Choose dependency status</option>
                        {DEPENDENCY_STATUSES.map((status) => <option key={status} value={status}>{status}</option>)}
                      </select>
                    </label>
                    <label className="field-label">
                      Target classification
                      <select value={entry.target_mode} onChange={(event) => updateDependencyEntry(index, { target_mode: event.target.value })}>
                        <option value="">Choose target classification</option>
                        <option value="none">No target record</option>
                        <option value="record">Specific approved-record target</option>
                      </select>
                    </label>
                    <label className="field-label">
                      Optional applicability rule
                      <input value={entry.applicability_rule} onChange={(event) => updateDependencyEntry(index, { applicability_rule: event.target.value })} />
                    </label>
                  </div>

                  {entry.target_mode === 'record' && (
                    <div className="omi-apply-dependency-target" aria-label={`Dependency ${index + 1} target record reference`}>
                      <label className="field-label">
                        Target destination type
                        <select value={entry.target.destination_type} onChange={(event) => updateDependencyTarget(index, 'destination_type', event.target.value)}>
                          <option value="">Choose referenced type</option>
                          {REFERENCE_DESTINATION_TYPES.map((value) => <option key={value} value={value}>{value}</option>)}
                        </select>
                      </label>
                      <label className="field-label">
                        Target destination key
                        <input value={entry.target.destination_key} onChange={(event) => updateDependencyTarget(index, 'destination_key', event.target.value)} />
                      </label>
                      <label className="field-label">
                        Target record version
                        <input type="number" min="1" max="2147483647" value={entry.target.record_version} onChange={(event) => updateDependencyTarget(index, 'record_version', event.target.value)} />
                      </label>
                      <label className="field-label">
                        Target content hash
                        <input className="omi-monospace-input" value={entry.target.content_hash} onChange={(event) => updateDependencyTarget(index, 'content_hash', event.target.value)} />
                      </label>
                    </div>
                  )}

                  <div className="omi-apply-reference-grid">
                    <ReferenceCheckboxes
                      legend="Dependency evidence references"
                      items={authorityEvidence}
                      idField="ref_id"
                      selectedIds={entry.evidence_ref_ids}
                      onChange={(value, selected) => toggleDependencyReference(index, 'evidence_ref_ids', value, selected)}
                    />
                    <ReferenceCheckboxes
                      legend="Dependency provenance references"
                      items={authorityProvenance}
                      idField="provenance_id"
                      selectedIds={entry.provenance_ref_ids}
                      onChange={(value, selected) => toggleDependencyReference(index, 'provenance_ref_ids', value, selected)}
                    />
                  </div>

                  <label className="field-label">
                    Dependency rationale
                    <textarea value={entry.rationale} onChange={(event) => updateDependencyEntry(index, { rationale: event.target.value })} />
                  </label>

                  <div
                    id={entryBlockerId}
                    className={`omi-apply-dependency-entry-status ${entryBlockers.length > 0 ? 'is-blocked' : ''}`}
                    role="status"
                    aria-live="polite"
                  >
                    <strong>{entryBlockers.length > 0 ? 'Entry incomplete' : 'Entry fields complete'}</strong>
                    {entryBlockers.length > 0 && (
                      <ul>{entryBlockers.map((blocker) => <li key={blocker}>{blocker}</li>)}</ul>
                    )}
                  </div>
                </fieldset>
              );
            })}
          </section>
        </fieldset>

        {['draft_active', 'sealed_active'].includes(lineageState) && (
          <fieldset className="omi-apply-supersession" disabled={formLockedToRecovery || isPreparing}>
            <legend>{lineageState === 'draft_active' ? 'Draft supersession' : 'Sealed-contract supersession'}</legend>
            <p>
              {lineageState === 'draft_active'
                ? `A new revision must explicitly supersede draft revision ${lineage.latest_revision}.`
                : `A new revision must explicitly supersede sealed revision ${lineage.active_sealed_revision}.`}
            </p>
            <label className="field-label">Supersession rationale<textarea value={supersessionRationale} onChange={(event) => setSupersessionRationale(event.target.value)} /></label>
            {lineageState === 'sealed_active' && (
              <label className="omi-checkbox-row">
                <input type="checkbox" checked={sealedSupersessionConfirmed} onChange={(event) => setSealedSupersessionConfirmed(event.target.checked)} />
                I explicitly confirm supersession of the active sealed contract. This does not apply the promotion.
              </label>
            )}
          </fieldset>
        )}

        <label className="field-label">
          Optional owner note
          <textarea disabled={formLockedToRecovery || isPreparing} value={ownerNote} onChange={(event) => setOwnerNote(event.target.value)} />
        </label>

        <dl className="omi-apply-metadata">
          <MetadataRow label="Retained preparation UUID" value={preparationIdempotencyKey} />
          <MetadataRow label="Expected latest revision" value={lineage.latest_revision} missingLabel="No prior revision" />
          <MetadataRow label="Expected draft hash" value={lineage.latest_draft_scope_hash} missingLabel="No prior draft" />
        </dl>

        <button
          className="primary-button"
          type="submit"
          disabled={preparationDisabled}
          aria-describedby={blockerReasonId}
        >
          {isPreparing
            ? 'Publishing immutable preparation…'
            : recoveryRequest
              ? 'Retry exact saved preparation publication'
              : 'Prepare immutable revision'}
        </button>
      </form>

      {selectedRevision && (
        <section className="omi-apply-section" aria-label="Selected apply-contract revision">
          <div className="section-heading">
            <div>
              <h3>Selected revision {selectedRevision.revision}</h3>
              <p className="muted-copy">Backend-published immutable revision; frontend state is advisory.</p>
            </div>
            <span className="omi-status-badge">{lineageState}</span>
          </div>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Operation" value={selectedRevision.operation} />
            <MetadataRow label="Destination" value={selectedRevision.destination?.approved_destination_type} />
            <MetadataRow label="Destination key" value={selectedRevision.destination?.destination_key} />
            <MetadataRow label="Destination path" value={selectedRevision.destination?.destination_path} />
            <MetadataRow label="Approved-record hash" value={selectedRevision.approved_record_hash} />
            <MetadataRow label="Approved-record size" value={selectedRevision.approved_record_size} />
            <MetadataRow label="Before-state token" value={selectedRevision.before_state?.snapshot_token} />
            <MetadataRow label="Duplicate decision" value={selectedRevision.duplicate_resolution?.state} />
            <MetadataRow label="Dependency decision" value={selectedRevision.dependency_resolution?.state} />
          </dl>
          <details className="omi-apply-record-preview">
            <summary>Complete approved-record preview</summary>
            <pre>{formatValue(selectedRevision.proposed_approved_record)}</pre>
          </details>
        </section>
      )}

      {selectedRevision && lineageState === 'draft_active' && (
        <form className="omi-apply-approval-form" onSubmit={handleApprove}>
          <h3>Explicit revision approval</h3>
          <p>Approval seals this exact revision. It does not mutate approved Memory or Canon.</p>
          <label className="omi-checkbox-row">
            <input
              type="checkbox"
              checked={approvalConfirmed}
              onChange={(event) => setApprovalConfirmed(event.target.checked)}
              disabled={isApproving}
            />
            I explicitly approve revision {selectedRevision.revision}, its complete approved-record hash and size, and its recorded before state.
          </label>
          <button
            className="primary-button"
            type="submit"
            disabled={approvalDisabled}
            aria-describedby={blockerReasonId}
          >
            {isApproving ? 'Recording approval…' : `Approve and seal revision ${selectedRevision.revision}`}
          </button>
        </form>
      )}

      {(sealedRevision || approvalResult) && (
        <section className="omi-apply-sealed-state" role="status" aria-label="Active sealed contract">
          <h3>Sealed contract reference</h3>
          <p>Challenge issuance is permitted only while the backend reports lineage state sealed_active.</p>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Revision" value={sealedRevision?.revision?.revision ?? approvalResult?.revision} />
            <MetadataRow label="Sealed-contract hash" value={sealedRevision?.sealed_contract_hash ?? approvalResult?.sealed_contract_hash} />
            <MetadataRow label="Approval event" value={sealedRevision?.approval_event_id ?? approvalResult?.approval_event_id} />
            <MetadataRow label="Lineage state" value={lineageState} />
          </dl>
        </section>
      )}

      {sealedRevision && !applyResult && (
        <section className="omi-apply-challenge" aria-label="Final anti-replay challenge">
          <div className="section-heading">
            <div>
              <h3>Final anti-replay challenge</h3>
              <p className="muted-copy">Generate final challenge explicitly. Observational GET never issues one.</p>
            </div>
            <span className={`omi-status-badge ${challengeState === 'active' ? '' : 'is-warning'}`}>
              Challenge: {challengeState.replaceAll('_', ' ')}
            </span>
          </div>
          <p>
            This 120-second, single-use challenge is anti-replay and explicit-confirmation evidence
            for a trusted local MVP deployment. It is not authentication and does not establish who
            is operating the local client.
          </p>
          <p className="omi-apply-challenge-status" role="status" aria-live="polite">
            {CHALLENGE_STATE_COPY[challengeState] ?? CHALLENGE_STATE_COPY.invalid}
            {challengeState === 'active' ? ` ${challengeSecondsRemaining} seconds remaining.` : ''}
          </p>
          {challengeNotice && <p className="muted-copy">{challengeNotice}</p>}
          {challenge && (
            <dl className="omi-apply-metadata">
              <MetadataRow label="Challenge ID" value={challenge.challenge_id} />
              <MetadataRow label="Issued at" value={challenge.challenge_scope?.issued_at} />
              <MetadataRow label="Expires at" value={challenge.challenge_scope?.expires_at} />
              <MetadataRow label="Bound revision" value={challenge.challenge_scope?.revision} />
              <MetadataRow label="Bound operation" value={challenge.challenge_scope?.operation} />
              <MetadataRow label="Bound destination path" value={challenge.challenge_scope?.destination_path} />
            </dl>
          )}
          <div className="omi-apply-challenge-actions">
            {challengeState === 'idle' && (
              <button
                className="primary-button"
                type="button"
                disabled={challengeDisabled}
                aria-describedby={blockerReasonId}
                onClick={() => handleIssueChallenge()}
              >
                {isIssuingChallenge ? 'Generating final challenge…' : 'Generate final challenge'}
              </button>
            )}
            {challengeState === 'active' && (
              <button
                className="secondary-button"
                type="button"
                disabled={challengeDisabled}
                onClick={() => handleIssueChallenge({ fresh: true })}
              >
                Explicitly replace active challenge
              </button>
            )}
            {(['expired', 'replaced', 'restart_invalidated', 'unknown', 'invalid'].includes(challengeState)
              || applyState === 'not_committed') && (
              <button
                className="primary-button"
                type="button"
                disabled={challengeDisabled}
                aria-describedby={blockerReasonId}
                onClick={() => handleIssueChallenge({ fresh: true })}
              >
                {isIssuingChallenge ? 'Generating fresh challenge…' : 'Generate fresh challenge'}
              </button>
            )}
          </div>
        </section>
      )}

      {applyState === 'recovery_required' && (
        <section className="omi-apply-recovery-state" role="alert" aria-label="Final apply recovery required">
          <h3>Final apply recovery required</h3>
          <p>The destination state is unresolved. Do not create a new request or challenge.</p>
          <p>Retry the exact retained final request and UUID so the backend can replay the intent and classify recovery.</p>
        </section>
      )}

      {applyState === 'not_committed' && (
        <section className="omi-apply-recovery-state" role="status" aria-label="Final apply not committed">
          <h3>Final apply verified not committed</h3>
          <p>The backend verified the destination still matches the recorded before state.</p>
          <p>Use the explicit fresh-challenge control to begin a new final attempt with a new apply UUID.</p>
        </section>
      )}

      {sealedRevision && !applyResult && (challenge || retainedFinalApplyRequest) && (
        <form className="omi-apply-final-confirmation" onSubmit={handleFinalApply}>
          <h3>Final confirmation</h3>
          <p>
            Confirm the exact sealed revision, operation, destination, before-state token, and complete
            approved-record hash/size. The request sends references and challenge values only.
          </p>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Promotion ID" value={promotionId} />
            <MetadataRow label="Revision" value={sealedContractRevision} />
            <MetadataRow label="Operation" value={sealedRevision.revision?.operation} />
            <MetadataRow label="Destination path" value={sealedRevision.revision?.destination?.destination_path} />
            <MetadataRow label="Sealed-contract hash" value={sealedContractHash} />
            <MetadataRow label="Before-state token" value={sealedBeforeStateToken} />
            <MetadataRow label="Approved-record hash" value={sealedRevision.revision?.approved_record_hash} />
            <MetadataRow label="Approved-record size" value={sealedRevision.revision?.approved_record_size} />
            <MetadataRow label="Retained final-apply UUID" value={finalApplyIdempotencyKey} />
          </dl>
          {exactApplyRetry ? (
            <p className="omi-apply-challenge-status" role="status">
              The original explicit confirmation, challenge binding, and final request remain retained for exact replay/recovery.
            </p>
          ) : (
            <label className="omi-checkbox-row omi-apply-final-check">
              <input
                type="checkbox"
                checked={finalConfirmationChecked}
                onChange={(event) => setFinalConfirmationChecked(event.target.checked)}
                disabled={isApplying || challengeState !== 'active'}
              />
              I explicitly confirm this one final apply for the displayed sealed revision and complete approved-record hash/size.
            </label>
          )}
          <button
            className="omi-final-apply-button"
            type="submit"
            disabled={finalApplyDisabled}
            aria-describedby={blockerReasonId}
          >
            {isApplying
              ? exactApplyRetry ? 'Replaying exact recovery request…' : 'Final apply pending…'
              : exactApplyRetry ? 'Retry exact apply recovery' : 'Final Apply-Promotion'}
          </button>
        </form>
      )}

      {applyResult && (
        <section className="omi-apply-success" role="status" aria-live="polite" tabIndex="-1">
          <h3>{applyResult.replayed ? 'Completed replay or committed recovery' : 'Apply-Promotion completed'}</h3>
          <p>The backend returned an authoritative completed result and the contract lineage was refreshed.</p>
          <dl className="omi-apply-metadata">
            <MetadataRow label="Apply ID" value={applyResult.apply_id} />
            <MetadataRow label="Lineage state" value={applyResult.lineage_state} />
            <MetadataRow label="Replayed" value={applyResult.replayed} />
            <MetadataRow label="Destination path" value={applyResult.destination_path} />
            <MetadataRow label="Approved-record version" value={applyResult.approved_record_version} />
            <MetadataRow label="Approved-record hash" value={applyResult.approved_record_hash} />
            <MetadataRow label="Approved-record size" value={applyResult.approved_record_size} />
          </dl>
        </section>
      )}

      <div className="omi-apply-final-actions">
        <button className="secondary-button" type="button" onClick={onCancel}>
          Cancel / Return
        </button>
      </div>
    </section>
  );
}
