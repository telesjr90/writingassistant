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

export default function OMIPanel({
  omiData,
  isLoading,
  status,
  error,
  isCreatingIdea,
  isCreatingCandidate,
  onCreateIdea,
  onCreateCandidate,
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
                </dl>
                <pre className="omi-json-preview">
                  {JSON.stringify(candidate.candidate_content ?? {}, null, 2)}
                </pre>
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
