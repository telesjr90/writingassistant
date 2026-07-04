import { buildFieldEvidenceScope } from './OMIEvidenceDrawer.jsx';

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

function formatStoredValue(value, missingLabel = 'Missing') {
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

function normalizeFieldRows(candidate) {
  const storedRows = asArray(
    candidate?.field_review_rows
      ?? candidate?.field_reviews
      ?? candidate?.fields
      ?? candidate?.structured_fields,
  );

  if (storedRows.length > 0) {
    return storedRows.map((field, index) => {
      const fieldName = firstPresent(field?.field, field?.field_name, field?.name, field?.key);
      return {
        id: firstPresent(field?.id, field?.field_id, fieldName, `field-${index + 1}`),
        storedField: field,
        field: formatStoredValue(fieldName, 'Missing'),
        proposedValue: formatStoredValue(
          firstPresent(
            field?.proposed_value,
            field?.value,
            field?.structured_value,
            field?.structured_field_summary,
          ),
          'Missing',
        ),
        decision: formatStoredValue(
          firstPresent(field?.decision, field?.owner_decision, field?.review_status),
          'Missing',
        ),
        evidence: formatStoredValue(
          firstPresent(field?.evidence, field?.evidence_summary, field?.evidence_refs),
          'Not linked',
        ),
        provenance: formatStoredValue(
          firstPresent(field?.provenance, field?.provenance_summary, field?.source_locator),
          'Not linked',
        ),
        duplicateDependency: formatStoredValue(
          firstPresent(field?.duplicate_dependency, field?.duplicate_state, field?.dependency_state),
          'Unavailable',
        ),
        ownerNote: formatStoredValue(
          firstPresent(field?.owner_note, field?.note, field?.review_note),
          'Unavailable',
        ),
        disabledReason: formatStoredValue(
          firstPresent(field?.disabled_reason, field?.approval_disabled_reason),
          'Disabled: field approval requires stored decision, evidence, provenance, and duplicate/dependency review.',
        ),
      };
    });
  }

  return [
    {
      id: 'missing-field-review-row',
      storedField: {},
      field: 'Missing',
      proposedValue: 'Missing',
      decision: 'Required field decisions unresolved',
      evidence: 'Missing evidence',
      provenance: 'Missing provenance',
      duplicateDependency: 'Dependency unresolved',
      ownerNote: 'Unavailable',
      disabledReason:
        'Disabled: field approval requires stored decision, evidence, provenance, and duplicate/dependency review.',
    },
  ];
}

export default function OMICandidateFieldTable({ candidate, onOpenEvidence = () => {} }) {
  const rows = normalizeFieldRows(candidate);

  return (
    <section className="omi-candidate-panel" aria-label="Field review table">
      <div className="section-heading">
        <div>
          <h2>Field review table</h2>
          <p className="muted-copy">
            Stored review metadata only. Missing values show Missing / Not linked / Unavailable.
          </p>
        </div>
        <span className="omi-status-badge">Confidence indicates support strength, not truth.</span>
      </div>
      <div className="omi-field-table-wrap">
        <table
          className="omi-candidate-field-table"
          data-testid="omi-candidate-field-table"
        >
          <caption>Candidate field-level review rows</caption>
          <thead>
            <tr>
              <th scope="col">Field</th>
              <th scope="col">Proposed value</th>
              <th scope="col">Decision</th>
              <th scope="col">Evidence</th>
              <th scope="col">Provenance</th>
              <th scope="col">Duplicate/dependency</th>
              <th scope="col">Owner note</th>
              <th scope="col">Field action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const reasonId = `omi-field-approval-disabled-${row.id}`;
              return (
                <tr key={row.id}>
                  <th scope="row">{row.field}</th>
                  <td>{row.proposedValue}</td>
                  <td>{row.decision}</td>
                  <td>{row.evidence}</td>
                  <td>{row.provenance}</td>
                  <td>{row.duplicateDependency}</td>
                  <td>{row.ownerNote}</td>
                  <td>
                    <button
                      className="secondary-button"
                      type="button"
                      data-testid="omi-field-evidence-drawer-trigger"
                      aria-label={`Open evidence drawer for field ${row.field}`}
                      aria-haspopup="dialog"
                      onClick={(event) => onOpenEvidence(
                        buildFieldEvidenceScope(candidate, row.storedField),
                        event.currentTarget,
                      )}
                    >
                      Open evidence
                    </button>
                    <button
                      className="secondary-button"
                      type="button"
                      disabled
                      aria-label={`Approve field ${row.field} for handoff`}
                      aria-describedby={reasonId}
                    >
                      Approve field
                    </button>
                    <p
                      id={reasonId}
                      className="omi-disabled-reason"
                      data-testid="omi-field-approval-disabled-reason"
                    >
                      {row.disabledReason}
                    </p>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
