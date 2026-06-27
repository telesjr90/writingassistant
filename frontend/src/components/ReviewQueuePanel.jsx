import { useEffect, useMemo, useState } from 'react';
import {
  fetchReviewQueueEntries,
  submitReviewQueueAction,
} from '../api.js';
import OwnerActionReviewControls from './OwnerActionReviewControls.jsx';

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

function candidateEvidenceRows(entry) {
  return [
    ['Evidence', entry?.evidence_summary],
    ['Evidence refs', entry?.evidence_refs],
    ['Provenance', entry?.provenance_summary],
    ['Provenance refs', entry?.provenance_refs],
    ['Source document', entry?.source_document],
    ['Source locator', entry?.source_locator],
  ];
}

export default function ReviewQueuePanel({ projectId }) {
  const [entries, setEntries] = useState([]);
  const [selectedQueueEntryId, setSelectedQueueEntryId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('Ready');

  useEffect(() => {
    let isMounted = true;

    async function loadReviewQueue() {
      setIsLoading(true);
      setError('');
      setStatus('Loading review queue');

      try {
        const payload = await fetchReviewQueueEntries(projectId);
        const nextEntries = Array.isArray(payload?.entries) ? payload.entries : [];
        if (!isMounted) {
          return;
        }
        setEntries(nextEntries);
        setSelectedQueueEntryId((currentId) => (
          nextEntries.some((entry) => entry.queue_entry_id === currentId)
            ? currentId
            : nextEntries[0]?.queue_entry_id ?? ''
        ));
        setStatus('Review queue loaded');
      } catch (loadError) {
        if (!isMounted) {
          return;
        }
        setEntries([]);
        setSelectedQueueEntryId('');
        setError(loadError instanceof Error ? loadError.message : 'Review queue load failed.');
        setStatus('Review queue unavailable');
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadReviewQueue();

    return () => {
      isMounted = false;
    };
  }, [projectId]);

  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.queue_entry_id === selectedQueueEntryId) ?? entries[0] ?? null,
    [entries, selectedQueueEntryId],
  );

  async function handleSubmitAction(command) {
    const response = await submitReviewQueueAction({
      projectId,
      ...command,
    });
    setStatus('Owner review command accepted as workflow metadata only.');
    return response;
  }

  return (
    <section className="review-queue-panel" aria-label="Owner review queue">
      <div className="section-heading">
        <div>
          <h2>Owner review queue</h2>
          <p className="muted-copy">
            This is a candidate-only, no-canon review surface. queue presence, confidence,
            and review status are not canon and are not project truth.
          </p>
        </div>
        <span className="context-status">{isLoading ? 'Loading' : status}</span>
      </div>

      {error && (
        <p className="error-copy" role="alert">
          {error}
        </p>
      )}

      <div className="review-queue-layout">
        <div className="review-queue-list" aria-label="Read-only review queue entries">
          <h3>Read-only candidates</h3>
          {entries.length === 0 ? (
            <p className="muted-copy">
              Review action controls are unavailable until a queue entry is present.
            </p>
          ) : (
            entries.map((entry) => (
              <button
                className={
                  selectedEntry?.queue_entry_id === entry.queue_entry_id
                    ? 'review-queue-entry is-active'
                    : 'review-queue-entry'
                }
                key={entry.queue_entry_id}
                type="button"
                onClick={() => setSelectedQueueEntryId(entry.queue_entry_id)}
              >
                <strong>{entry.queue_entry_id}</strong>
                <span>{entry.review_status}</span>
                <small>
                  Confidence {formatValue(entry.confidence)}; not canon.
                </small>
              </button>
            ))
          )}
        </div>

        <div className="review-queue-detail" aria-label="Read-only candidate details">
          {!selectedEntry ? (
            <p className="muted-copy">
              Select a candidate queue entry to review evidence, provenance, and source locator
              context before sending an owner command.
            </p>
          ) : (
            <>
              <div className="review-boundary-note">
                Candidate details are read-only. This panel preserves evidence/provenance/source
                locator context and does not perform canon or memory mutation.
              </div>

              <dl className="omi-metadata">
                <div>
                  <dt>Queue entry</dt>
                  <dd>{formatValue(selectedEntry.queue_entry_id)}</dd>
                </div>
                <div>
                  <dt>Candidate</dt>
                  <dd>{formatValue(selectedEntry.candidate_record_id)}</dd>
                </div>
                <div>
                  <dt>Type</dt>
                  <dd>{formatValue(selectedEntry.candidate_type)}</dd>
                </div>
                <div>
                  <dt>Target category</dt>
                  <dd>{formatValue(selectedEntry.target_category)}</dd>
                </div>
                <div>
                  <dt>Review status</dt>
                  <dd>{formatValue(selectedEntry.review_status)}; not canon</dd>
                </div>
                <div>
                  <dt>Confidence</dt>
                  <dd>{formatValue(selectedEntry.confidence)}; not canon</dd>
                </div>
                <div>
                  <dt>Lifecycle</dt>
                  <dd>{formatValue(selectedEntry.lifecycle_state)}</dd>
                </div>
                <div>
                  <dt>Normalization</dt>
                  <dd>{formatValue(selectedEntry.normalization_status)}</dd>
                </div>
                <div>
                  <dt>Updated</dt>
                  <dd>{formatValue(selectedEntry.updated_at)}</dd>
                </div>
              </dl>

              <div className="omi-detail-card">
                <h4>Evidence, provenance, and source locator</h4>
                <dl className="omi-provenance-grid">
                  {candidateEvidenceRows(selectedEntry).map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{formatValue(value)}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <OwnerActionReviewControls
                projectId={projectId}
                queueEntry={selectedEntry}
                disabled={isLoading}
                onSubmitAction={handleSubmitAction}
              />
            </>
          )}
        </div>
      </div>
    </section>
  );
}
