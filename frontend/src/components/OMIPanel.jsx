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

function formatDate(value) {
  if (!value) {
    return 'No timestamp';
  }

  return value;
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

export default function OMIPanel({
  omiData,
  isLoading,
  status,
  error,
  isCreatingIdea,
  isCreatingCandidate,
  isUpdating,
  onCreateIdea,
  onCreateCandidate,
  onUpdateIdeaDecision,
  onUpdateCandidateDecision,
}) {
  const ideas = useMemo(() => omiData?.ideas ?? [], [omiData]);
  const candidates = useMemo(() => omiData?.candidates ?? [], [omiData]);
  const [rawIdea, setRawIdea] = useState('');
  const [selectedIdeaId, setSelectedIdeaId] = useState('');
  const [candidateType, setCandidateType] = useState('planning_note');
  const [destination, setDestination] = useState('planning_notes');
  const [candidateContent, setCandidateContent] = useState('{\n  "summary": "",\n  "fields": []\n}');
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (!selectedIdeaId && ideas.length > 0) {
      setSelectedIdeaId(ideas[0].idea_id);
    }
  }, [ideas, selectedIdeaId]);

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
      await onCreateCandidate({
        idea_id: selectedIdeaId,
        candidate_type: candidateType,
        candidate_content: parsedContent,
        destination,
        evidence: [],
      });
      setCandidateContent('{\n  "summary": "",\n  "fields": []\n}');
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
                    <dt>Type</dt>
                    <dd>{candidate.candidate_type}</dd>
                  </div>
                  <div>
                    <dt>Destination</dt>
                    <dd>{candidate.destination}</dd>
                  </div>
                  <div>
                    <dt>Promotion</dt>
                    <dd>{candidate.promotion_status?.eligible ? 'Eligible' : 'Blocked'}</dd>
                  </div>
                  <div>
                    <dt>Decision</dt>
                    <dd>{candidate.owner_decision?.decision ?? 'pending'}</dd>
                  </div>
                  <div>
                    <dt>Approved</dt>
                    <dd>{candidate.owner_decision?.approved ? 'Yes' : 'No'}</dd>
                  </div>
                </dl>
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
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
