import { useEffect, useMemo, useState } from 'react';

const CANDIDATE_TYPES = [
  { value: 'planning_note', label: 'Planning note' },
  { value: 'project_bible_candidate', label: 'Project bible candidate' },
  { value: 'storyform_context_candidate', label: 'Storyform context candidate' },
  { value: 'scene_prompt_context_candidate', label: 'Scene prompt context candidate' },
  { value: 'template_starter_candidate', label: 'Template starter candidate' },
];

const DESTINATIONS = [
  { value: 'planning_notes', label: 'Planning notes' },
  { value: 'project_bible_candidate', label: 'Project bible candidate' },
  { value: 'storyform_context_candidate', label: 'Storyform context candidate' },
  { value: 'scene_prompt_context_candidate', label: 'Scene prompt context candidate' },
  { value: 'template_starter_candidate', label: 'Template starter candidate' },
  { value: 'discard', label: 'Discard' },
];

const DECISIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'approve', label: 'Approve' },
  { value: 'reject', label: 'Reject' },
  { value: 'needs_revision', label: 'Needs revision' },
];

const IDEA_STATUSES = [
  { value: 'draft', label: 'Draft' },
  { value: 'owner_review', label: 'Owner review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'candidate', label: 'Candidate' },
  { value: 'archived', label: 'Archived' },
];

const CANDIDATE_STATUSES = [
  { value: 'candidate', label: 'Candidate' },
  { value: 'owner_review', label: 'Owner review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'archived', label: 'Archived' },
];

const PROMOTION_TARGETS = [
  { value: 'planning_notes', label: 'Planning notes' },
  { value: 'bible.json', label: 'bible.json' },
  { value: 'storyform.json', label: 'storyform.json' },
  { value: 'owner_memory.json', label: 'owner_memory.json' },
];

function formatDate(value) {
  if (!value) {
    return 'No timestamp';
  }

  return value;
}

function formatCount(count, singular, plural = `${singular}s`) {
  return `${count} ${count === 1 ? singular : plural}`;
}

function formatDecision(record) {
  const decision = record?.owner_decision ?? {};
  if (decision.decision === 'approve' && decision.approval_confirmed) {
    return 'Approved and confirmed';
  }
  if (decision.decision === 'approve') {
    return 'Approval pending confirmation';
  }
  if (decision.decision === 'reject') {
    return 'Rejected';
  }
  if (decision.decision === 'needs_revision') {
    return 'Needs revision';
  }
  return 'Pending review';
}

function hasObject(value) {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'Not recorded';
  }
  if (Array.isArray(value)) {
    return value.length === 0 ? 'None' : value.join(', ');
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function provenanceRows(provenance) {
  if (!hasObject(provenance)) {
    return [];
  }

  return [
    ['Source type', provenance.source_type],
    ['Source label', provenance.source_label],
    ['Source path', provenance.source_path],
    ['Created by', provenance.created_by],
    ['Tool', provenance.tool],
    ['Model', provenance.model],
    ['Prompt', provenance.prompt_id],
    ['Timestamp', provenance.timestamp],
    ['Confidence', provenance.confidence],
    ['Notes', provenance.notes],
  ].filter(([, value]) => value !== undefined);
}

function provenanceSummary(provenance) {
  if (!hasObject(provenance)) {
    return 'No provenance';
  }

  return provenance.source_label || provenance.source_type || 'Recorded provenance';
}

function evidenceSummary(evidence) {
  if (!Array.isArray(evidence) || evidence.length === 0) {
    return 'No evidence attached';
  }

  return formatCount(evidence.length, 'evidence item');
}

function parseCandidateContent(text) {
  let parsed;

  try {
    parsed = JSON.parse(text);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Invalid JSON.';
    throw new Error(`Candidate content JSON is invalid: ${message}`);
  }

  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error('Candidate content must be a JSON object.');
  }

  return parsed;
}

function statusForDecision(decision, fallbackStatus) {
  if (decision === 'approve') {
    return 'approved';
  }
  if (decision === 'reject') {
    return 'rejected';
  }
  if (decision === 'needs_revision') {
    return 'candidate';
  }
  return fallbackStatus;
}

function promotionReadiness(candidate) {
  const blockedReasons = [];
  const ownerDecision = candidate.owner_decision ?? {};

  if (candidate.status !== 'approved') {
    blockedReasons.push('Candidate status must be approved.');
  }
  if (ownerDecision.decision !== 'approve') {
    blockedReasons.push('Owner decision must be approve.');
  }
  if (!ownerDecision.approval_confirmed) {
    blockedReasons.push('Owner approval confirmation is required.');
  }
  if (!candidate.destination || candidate.destination === 'discard') {
    blockedReasons.push('A promotable destination is required.');
  }
  if (!DESTINATIONS.some((option) => option.value === candidate.destination)) {
    blockedReasons.push('Destination must be allow-listed.');
  }
  if (!candidate.provenance || typeof candidate.provenance !== 'object') {
    blockedReasons.push('Provenance is required.');
  }
  if (
    !candidate.candidate_content
    || typeof candidate.candidate_content !== 'object'
    || Array.isArray(candidate.candidate_content)
  ) {
    blockedReasons.push('Candidate content must be a JSON object.');
  }

  return {
    ready: blockedReasons.length === 0,
    blockedReasons,
  };
}

function promotionRequirementRows(candidate, readiness) {
  const ownerDecision = candidate.owner_decision ?? {};
  return [
    {
      label: 'Owner approval',
      met: ownerDecision.decision === 'approve',
      detail: ownerDecision.decision ?? 'pending',
    },
    {
      label: 'Approval confirmation',
      met: ownerDecision.approval_confirmed === true,
      detail: ownerDecision.approval_confirmed ? 'confirmed' : 'missing',
    },
    {
      label: 'Allowed destination',
      met: Boolean(candidate.destination)
        && candidate.destination !== 'discard'
        && DESTINATIONS.some((option) => option.value === candidate.destination),
      detail: candidate.destination ?? 'not selected',
    },
    {
      label: 'Provenance',
      met: hasObject(candidate.provenance),
      detail: provenanceSummary(candidate.provenance),
    },
    {
      label: 'Structured content',
      met: hasObject(candidate.candidate_content),
      detail: hasObject(candidate.candidate_content) ? 'JSON object' : 'missing',
    },
    {
      label: 'Safe target label/path',
      met: readiness.ready,
      detail: readiness.ready ? 'choose target when creating record' : 'blocked until ready',
    },
  ];
}

function OwnerDecisionForm({
  record,
  type,
  isUpdating,
  onSubmit,
  onError,
}) {
  const existingDecision = record.owner_decision ?? {};
  const statusOptions = type === 'candidate' ? CANDIDATE_STATUSES : IDEA_STATUSES;
  const [decision, setDecision] = useState(existingDecision.decision ?? 'pending');
  const [status, setStatus] = useState(record.status ?? statusOptions[0].value);
  const [approvalConfirmed, setApprovalConfirmed] = useState(
    Boolean(existingDecision.approval_confirmed || existingDecision.approved),
  );
  const [notes, setNotes] = useState(existingDecision.notes ?? '');
  const [selectedDestination, setSelectedDestination] = useState(
    record.destination ?? 'planning_notes',
  );

  useEffect(() => {
    setDecision(existingDecision.decision ?? 'pending');
    setStatus(record.status ?? statusOptions[0].value);
    setApprovalConfirmed(Boolean(existingDecision.approval_confirmed || existingDecision.approved));
    setNotes(existingDecision.notes ?? '');
    setSelectedDestination(record.destination ?? 'planning_notes');
  }, [
    existingDecision.approval_confirmed,
    existingDecision.approved,
    existingDecision.decision,
    existingDecision.notes,
    record.destination,
    record.status,
    statusOptions,
  ]);

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      await onSubmit(record, {
        owner_decision: {
          decision,
          approval_confirmed: decision === 'approve' ? approvalConfirmed : false,
          notes,
        },
        status,
        ...(type === 'candidate' ? { destination: selectedDestination } : {}),
      });
    } catch (updateError) {
      onError(updateError instanceof Error ? updateError.message : 'OMI decision update failed.');
    }
  }

  function handleDecisionChange(event) {
    const nextDecision = event.target.value;
    setDecision(nextDecision);
    setStatus(statusForDecision(nextDecision, status));
    if (nextDecision !== 'approve') {
      setApprovalConfirmed(false);
    }
  }

  return (
    <form className="omi-decision-form" onSubmit={handleSubmit}>
      <div className="omi-decision-grid">
        <label className="field-label">
          Status
          <select
            className="field-input"
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            disabled={isUpdating}
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field-label">
          Decision
          <select
            className="field-input"
            value={decision}
            onChange={handleDecisionChange}
            disabled={isUpdating}
          >
            {DECISIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        {type === 'candidate' && (
          <label className="field-label">
            Destination
            <select
              className="field-input"
              value={selectedDestination}
              onChange={(event) => setSelectedDestination(event.target.value)}
              disabled={isUpdating}
            >
              {DESTINATIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {decision === 'approve' && (
        <label className="omi-checkbox-row">
          <input
            type="checkbox"
            checked={approvalConfirmed}
            onChange={(event) => setApprovalConfirmed(event.target.checked)}
            disabled={isUpdating}
          />
          Approval confirmed
        </label>
      )}

      <label className="field-label">
        Owner notes
        <textarea
          className="context-textarea omi-note-textarea"
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          disabled={isUpdating}
        />
      </label>

      <button className="primary-button" type="submit" disabled={isUpdating}>
        {isUpdating ? 'Saving...' : 'Save decision'}
      </button>
    </form>
  );
}

function PromotionRecordForm({
  candidate,
  readiness,
  isCreatingPromotion,
  onSubmit,
  onError,
}) {
  const [target, setTarget] = useState('planning_notes');
  const [finalConfirmation, setFinalConfirmation] = useState(false);

  useEffect(() => {
    setFinalConfirmation(false);
  }, [candidate.candidate_id]);

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      await onSubmit({
        candidate_id: candidate.candidate_id,
        final_confirmation: finalConfirmation,
        target_file: target,
        target_path: target,
      });
      setFinalConfirmation(false);
    } catch (promotionError) {
      onError(
        promotionError instanceof Error
          ? promotionError.message
          : 'Promotion record create failed.',
      );
    }
  }

  return (
    <div className="omi-promotion-panel">
      <div className="omi-readiness">
        <strong>{readiness.ready ? 'Promotion-ready' : 'Not promotion-ready'}</strong>
        {readiness.blockedReasons.length > 0 && (
          <ul>
            {readiness.blockedReasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        )}
      </div>

      {readiness.ready && (
        <form className="omi-promotion-form" onSubmit={handleSubmit}>
          <label className="field-label">
            Target file/path
            <select
              className="field-input"
              value={target}
              onChange={(event) => setTarget(event.target.value)}
              disabled={isCreatingPromotion}
            >
              {PROMOTION_TARGETS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="omi-checkbox-row">
            <input
              type="checkbox"
              checked={finalConfirmation}
              onChange={(event) => setFinalConfirmation(event.target.checked)}
              disabled={isCreatingPromotion}
            />
            Final confirmation
          </label>

          <button
            className="primary-button"
            type="submit"
            disabled={isCreatingPromotion || !finalConfirmation}
          >
            {isCreatingPromotion ? 'Creating...' : 'Create promotion record'}
          </button>
        </form>
      )}
    </div>
  );
}

export default function OMIPanel({
  omiData,
  isLoading,
  status,
  error,
  isCreatingIdea,
  isCreatingCandidate,
  isCreatingPromotion,
  isUpdating,
  onCreateIdea,
  onCreateCandidate,
  onCreatePromotion,
  onUpdateIdeaDecision,
  onUpdateCandidateDecision,
}) {
  const ideas = useMemo(() => omiData?.ideas ?? [], [omiData]);
  const candidates = useMemo(() => omiData?.candidates ?? [], [omiData]);
  const promotions = useMemo(() => omiData?.promotions ?? [], [omiData]);
  const [rawIdea, setRawIdea] = useState('');
  const [selectedIdeaId, setSelectedIdeaId] = useState('');
  const [candidateType, setCandidateType] = useState('planning_note');
  const [destination, setDestination] = useState('planning_notes');
  const [candidateContent, setCandidateContent] = useState('{\n  "summary": "",\n  "fields": []\n}');
  const [formError, setFormError] = useState('');
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const selectedCandidate = useMemo(
    () => candidates.find((candidate) => candidate.candidate_id === selectedCandidateId)
      ?? candidates[0]
      ?? null,
    [candidates, selectedCandidateId],
  );
  const selectedCandidateReadiness = selectedCandidate
    ? promotionReadiness(selectedCandidate)
    : null;
  const selectedCandidatePromotions = useMemo(() => {
    if (!selectedCandidate) {
      return [];
    }

    return promotions.filter(
      (promotion) => promotion.candidate_id === selectedCandidate.candidate_id,
    );
  }, [promotions, selectedCandidate]);

  useEffect(() => {
    if (!selectedIdeaId && ideas.length > 0) {
      setSelectedIdeaId(ideas[0].idea_id);
    }
  }, [ideas, selectedIdeaId]);

  useEffect(() => {
    if (!selectedCandidateId && candidates.length > 0) {
      setSelectedCandidateId(candidates[0].candidate_id);
      return;
    }

    if (
      selectedCandidateId
      && !candidates.some((candidate) => candidate.candidate_id === selectedCandidateId)
    ) {
      setSelectedCandidateId(candidates[0]?.candidate_id ?? '');
    }
  }, [candidates, selectedCandidateId]);

  async function handleCreateIdea(event) {
    event.preventDefault();
    setFormError('');

    try {
      const idea = await onCreateIdea(rawIdea);
      setRawIdea('');
      if (idea?.idea_id) {
        setSelectedIdeaId(idea.idea_id);
      }
    } catch (createError) {
      setFormError(createError instanceof Error ? createError.message : 'Idea create failed.');
    }
  }

  async function handleCreateCandidate(event) {
    event.preventDefault();
    setFormError('');

    try {
      const parsedContent = parseCandidateContent(candidateContent);
      const candidate = await onCreateCandidate({
        idea_id: selectedIdeaId,
        candidate_type: candidateType,
        candidate_content: parsedContent,
        destination,
        evidence: [],
      });
      setCandidateContent('{\n  "summary": "",\n  "fields": []\n}');
      if (candidate?.candidate_id) {
        setSelectedCandidateId(candidate.candidate_id);
      }
    } catch (createError) {
      setFormError(
        createError instanceof Error ? createError.message : 'Candidate create failed.',
      );
    }
  }

  return (
    <section className="omi-panel" aria-label="Organize My Idea">
      <div className="section-heading">
        <div>
          <h2>Organize My Idea</h2>
          <p className="muted-copy">
            OMI stores candidate planning material only. It does not write story prose or change project truth.
            {' '}
            Approving a candidate does not promote it. Promotion requires a separate confirmation step.
            {' '}
            Creating a promotion record does not change bible, storyform, scenes, or project truth.
            {' '}
            The app cannot write or rewrite story prose.
          </p>
        </div>
        <span className="context-status">{isLoading ? 'Loading' : status}</span>
      </div>

      {(error || formError) && (
        <p className="error-copy" role="alert">
          {formError || error}
        </p>
      )}

      <div className="omi-grid">
        <form className="omi-form" onSubmit={handleCreateIdea}>
          <h3>Raw idea</h3>
          <textarea
            className="context-textarea omi-textarea"
            value={rawIdea}
            onChange={(event) => setRawIdea(event.target.value)}
            disabled={isCreatingIdea}
            aria-label="Raw OMI idea"
          />
          <button
            className="primary-button"
            type="submit"
            disabled={isCreatingIdea || rawIdea.trim() === ''}
          >
            {isCreatingIdea ? 'Creating...' : 'Create idea'}
          </button>
        </form>

        <form className="omi-form" onSubmit={handleCreateCandidate}>
          <h3>Candidate</h3>
          <label className="field-label" htmlFor="omi-idea-select">
            Linked idea
          </label>
          <select
            id="omi-idea-select"
            className="field-input"
            value={selectedIdeaId}
            onChange={(event) => setSelectedIdeaId(event.target.value)}
            disabled={ideas.length === 0 || isCreatingCandidate}
          >
            {ideas.length === 0 ? (
              <option value="">Create an idea first</option>
            ) : (
              ideas.map((idea) => (
                <option key={idea.idea_id} value={idea.idea_id}>
                  {idea.idea_id}
                </option>
              ))
            )}
          </select>

          <label className="field-label" htmlFor="omi-candidate-type">
            Candidate type
          </label>
          <select
            id="omi-candidate-type"
            className="field-input"
            value={candidateType}
            onChange={(event) => setCandidateType(event.target.value)}
            disabled={isCreatingCandidate}
          >
            {CANDIDATE_TYPES.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <label className="field-label" htmlFor="omi-destination">
            Destination
          </label>
          <select
            id="omi-destination"
            className="field-input"
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
            disabled={isCreatingCandidate}
          >
            {DESTINATIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <label className="field-label" htmlFor="omi-candidate-content">
            Candidate content JSON
          </label>
          <textarea
            id="omi-candidate-content"
            className="context-textarea omi-textarea"
            value={candidateContent}
            onChange={(event) => setCandidateContent(event.target.value)}
            disabled={isCreatingCandidate}
          />

          <button
            className="primary-button"
            type="submit"
            disabled={isCreatingCandidate || selectedIdeaId === ''}
          >
            {isCreatingCandidate ? 'Creating...' : 'Create candidate'}
          </button>
        </form>
      </div>

      <div className="omi-record-grid">
        <div className="omi-list" aria-label="OMI ideas">
          <h3>Ideas</h3>
          {ideas.length === 0 ? (
            <p className="muted-copy">No OMI ideas yet.</p>
          ) : (
            ideas.map((idea) => (
              <article className="omi-record" key={idea.idea_id}>
                <div className="omi-record-header">
                  <strong>{idea.idea_id}</strong>
                  <span>{idea.status}</span>
                </div>
                <p>{idea.raw_idea}</p>
                <dl className="omi-metadata">
                  <div>
                    <dt>Linked candidates</dt>
                    <dd>{idea.linked_candidate_ids?.length ?? 0}</dd>
                  </div>
                  <div>
                    <dt>Source</dt>
                    <dd>{provenanceSummary(idea.provenance)}</dd>
                  </div>
                  <div>
                    <dt>Decision</dt>
                    <dd>{idea.owner_decision?.decision ?? 'pending'}</dd>
                  </div>
                  <div>
                    <dt>Approved</dt>
                    <dd>{idea.owner_decision?.approved ? 'Yes' : 'No'}</dd>
                  </div>
                  <div>
                    <dt>By</dt>
                    <dd>{idea.owner_decision?.decided_by ?? 'Unreviewed'}</dd>
                  </div>
                  <div>
                    <dt>Created</dt>
                    <dd>{formatDate(idea.created_at)}</dd>
                  </div>
                  <div>
                    <dt>Updated</dt>
                    <dd>{formatDate(idea.updated_at)}</dd>
                  </div>
                </dl>
                <OwnerDecisionForm
                  record={idea}
                  type="idea"
                  isUpdating={isUpdating}
                  onSubmit={(record, payload) => onUpdateIdeaDecision(record.idea_id, payload)}
                  onError={setFormError}
                />
                <small>Updated {formatDate(idea.updated_at)}</small>
              </article>
            ))
          )}
        </div>

        <div className="omi-list" aria-label="OMI candidates">
          <h3>Candidates</h3>
          {candidates.length === 0 ? (
            <p className="muted-copy">No OMI candidates yet.</p>
          ) : (
            candidates.map((candidate) => (
              <article className="omi-record" key={candidate.candidate_id}>
                <div className="omi-record-header">
                  <strong>{candidate.candidate_id}</strong>
                  <span>{candidate.status}</span>
                </div>
                <dl className="omi-metadata">
                  <div>
                    <dt>Idea</dt>
                    <dd>{candidate.idea_id}</dd>
                  </div>
                  <div>
                    <dt>Type</dt>
                    <dd>{candidate.candidate_type}</dd>
                  </div>
                  <div>
                    <dt>Destination</dt>
                    <dd>{candidate.destination}</dd>
                  </div>
                  <div>
                    <dt>Promotion</dt>
                    <dd>{promotionReadiness(candidate).ready ? 'Ready' : 'Blocked'}</dd>
                  </div>
                  <div>
                    <dt>Decision</dt>
                    <dd>{candidate.owner_decision?.decision ?? 'pending'}</dd>
                  </div>
                  <div>
                    <dt>Approved</dt>
                    <dd>{candidate.owner_decision?.approved ? 'Yes' : 'No'}</dd>
                  </div>
                  <div>
                    <dt>Source</dt>
                    <dd>{provenanceSummary(candidate.provenance)}</dd>
                  </div>
                  <div>
                    <dt>Evidence</dt>
                    <dd>{evidenceSummary(candidate.evidence)}</dd>
                  </div>
                </dl>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => setSelectedCandidateId(candidate.candidate_id)}
                >
                  {selectedCandidate?.candidate_id === candidate.candidate_id
                    ? 'Viewing details'
                    : 'View details'}
                </button>
                <pre className="omi-json-preview">
                  {JSON.stringify(candidate.candidate_content ?? {}, null, 2)}
                </pre>
                <OwnerDecisionForm
                  record={candidate}
                  type="candidate"
                  isUpdating={isUpdating}
                  onSubmit={(record, payload) => (
                    onUpdateCandidateDecision(record.candidate_id, payload)
                  )}
                  onError={setFormError}
                />
                <PromotionRecordForm
                  candidate={candidate}
                  readiness={promotionReadiness(candidate)}
                  isCreatingPromotion={isCreatingPromotion}
                  onSubmit={onCreatePromotion}
                  onError={setFormError}
                />
              </article>
            ))
          )}
        </div>
      </div>

      <section className="omi-detail-panel" aria-label="Selected OMI candidate details">
        <div className="omi-detail-header">
          <div>
            <h3>Candidate lifecycle</h3>
            <p className="muted-copy">
              Approval and promotion records are review metadata only. They do not apply candidate
              content to project truth.
            </p>
          </div>
          {selectedCandidate && (
            <span className="context-status">
              {selectedCandidateReadiness?.ready ? 'Promotion-ready' : 'Blocked'}
            </span>
          )}
        </div>

        {!selectedCandidate ? (
          <p className="muted-copy">Select or create a candidate to inspect lifecycle details.</p>
        ) : (
          <>
            <div className="omi-detail-grid">
              <dl className="omi-metadata">
                <div>
                  <dt>Candidate</dt>
                  <dd>{selectedCandidate.candidate_id}</dd>
                </div>
                <div>
                  <dt>Idea</dt>
                  <dd>{selectedCandidate.idea_id}</dd>
                </div>
                <div>
                  <dt>Type</dt>
                  <dd>{selectedCandidate.candidate_type}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{selectedCandidate.status}</dd>
                </div>
                <div>
                  <dt>Decision</dt>
                  <dd>{formatDecision(selectedCandidate)}</dd>
                </div>
                <div>
                  <dt>Destination</dt>
                  <dd>{selectedCandidate.destination}</dd>
                </div>
                <div>
                  <dt>Promotion status</dt>
                  <dd>
                    {selectedCandidatePromotions.length > 0
                      ? formatCount(selectedCandidatePromotions.length, 'record')
                      : selectedCandidate.promotion_status?.eligible
                        ? 'Eligible flag set'
                        : 'No promotion record'}
                  </dd>
                </div>
                <div>
                  <dt>Created</dt>
                  <dd>{formatDate(selectedCandidate.created_at)}</dd>
                </div>
                <div>
                  <dt>Updated</dt>
                  <dd>{formatDate(selectedCandidate.updated_at)}</dd>
                </div>
              </dl>

              <div className="omi-detail-card">
                <h4>Provenance</h4>
                {provenanceRows(selectedCandidate.provenance).length === 0 ? (
                  <p className="muted-copy">No provenance recorded.</p>
                ) : (
                  <dl className="omi-provenance-grid">
                    {provenanceRows(selectedCandidate.provenance).map(([label, value]) => (
                      <div key={label}>
                        <dt>{label}</dt>
                        <dd>{formatValue(value)}</dd>
                      </div>
                    ))}
                  </dl>
                )}
              </div>

              <div className="omi-detail-card">
                <h4>Evidence</h4>
                <p className="muted-copy">{evidenceSummary(selectedCandidate.evidence)}</p>
                {Array.isArray(selectedCandidate.evidence) && selectedCandidate.evidence.length > 0 && (
                  <pre className="omi-json-preview">
                    {JSON.stringify(selectedCandidate.evidence, null, 2)}
                  </pre>
                )}
              </div>
            </div>

            <div className="omi-detail-grid">
              <div className="omi-detail-card">
                <h4>Promotion readiness</h4>
                {selectedCandidateReadiness && (
                  <>
                    <ul className="omi-checklist">
                      {promotionRequirementRows(
                        selectedCandidate,
                        selectedCandidateReadiness,
                      ).map((requirement) => (
                        <li
                          className={requirement.met ? 'is-met' : 'is-blocked'}
                          key={requirement.label}
                        >
                          <strong>{requirement.label}</strong>
                          <span>{requirement.detail}</span>
                        </li>
                      ))}
                    </ul>

                    {selectedCandidateReadiness.blockedReasons.length > 0 && (
                      <div className="omi-readiness">
                        <strong>Blockers</strong>
                        <ul>
                          {selectedCandidateReadiness.blockedReasons.map((reason) => (
                            <li key={reason}>{reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>

              <div className="omi-detail-card">
                <h4>Candidate content</h4>
                <pre className="omi-json-preview">
                  {JSON.stringify(selectedCandidate.candidate_content ?? {}, null, 2)}
                </pre>
              </div>
            </div>
          </>
        )}
      </section>

      <div className="omi-list" aria-label="OMI promotion records">
        <h3>Promotion records</h3>
        {promotions.length === 0 ? (
          <p className="muted-copy">No OMI promotion records yet.</p>
        ) : (
          promotions.map((promotion) => (
            <article className="omi-record" key={promotion.promotion_id}>
              <div className="omi-record-header">
                <strong>{promotion.promotion_id}</strong>
                <span>{promotion.status}</span>
              </div>
              <dl className="omi-metadata">
                <div>
                  <dt>Candidate</dt>
                  <dd>{promotion.candidate_id}</dd>
                </div>
                <div>
                  <dt>Destination</dt>
                  <dd>{promotion.destination}</dd>
                </div>
                <div>
                  <dt>Target</dt>
                  <dd>{promotion.target_file ?? promotion.target_path}</dd>
                </div>
              </dl>
              <small>Confirmed {formatDate(promotion.confirmed_at)}</small>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
