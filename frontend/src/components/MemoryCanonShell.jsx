export const APPROVED_MEMORY_CATEGORIES = Object.freeze([
  {
    id: 'characters',
    label: 'Characters',
    description: 'Approved character records for this project.',
    emptyTitle: 'No approved character records yet.',
    emptyBody:
      'This approved-only empty state does not show candidate records as canon.',
  },
  {
    id: 'locations_settings',
    label: 'Locations / Settings',
    description: 'Approved location and setting records for this project.',
    emptyTitle: 'No approved location or setting records yet.',
    emptyBody:
      'Locations and settings remain outside Memory / Canon until they are approved records.',
  },
  {
    id: 'timeline',
    label: 'Timeline',
    description: 'Approved timeline records for this project.',
    emptyTitle: 'No approved timeline records yet.',
    emptyBody: 'Candidate timeline data remains in OMI/candidate review.',
  },
  {
    id: 'plot_threads',
    label: 'Plot Threads',
    description: 'Approved plot thread records for this project.',
    emptyTitle: 'No approved plot thread records yet.',
    emptyBody: 'Plot thread candidates are not approved project truth here.',
  },
  {
    id: 'continuity_consistency',
    label: 'Continuity / Consistency',
    description: 'Approved continuity and consistency records for this project.',
    emptyTitle: 'No approved continuity or consistency records yet.',
    emptyBody: 'Review notes and candidate issues remain outside approved canon.',
  },
  {
    id: 'open_questions',
    label: 'Open Questions',
    description: 'Approved open question records for this project.',
    emptyTitle: 'No approved open question records yet.',
    emptyBody: 'Candidate questions remain planning data until a future owner-approved step.',
  },
  {
    id: 'relationships',
    label: 'Relationships',
    description: 'Approved relationship records for this project.',
    emptyTitle: 'No approved relationship records yet.',
    emptyBody: 'Relationship candidates remain candidate-only and are not canon here.',
  },
  {
    id: 'organizations_groups',
    label: 'Organizations / Groups',
    description: 'Approved organization and group records for this project.',
    emptyTitle: 'No approved organization or group records yet.',
    emptyBody: 'Group candidates remain in review until they become approved records.',
  },
  {
    id: 'objects_items',
    label: 'Objects / Items',
    description: 'Approved object and item records for this project.',
    emptyTitle: 'No approved object or item records yet.',
    emptyBody: 'Object and item candidates are not Memory / Canon records here.',
  },
]);

function getCategoryRecords(approvedRecordsByCategory, categoryId) {
  if (!approvedRecordsByCategory || typeof approvedRecordsByCategory !== 'object') {
    return [];
  }

  const records = approvedRecordsByCategory[categoryId];
  return Array.isArray(records) ? records : [];
}

function getRecordLabel(record, index) {
  if (!record || typeof record !== 'object') {
    return `Approved record ${index + 1}`;
  }

  const label =
    record.label ??
    record.name ??
    record.title ??
    record.canonical_name ??
    record.record_id ??
    record.id;

  return typeof label === 'string' && label.trim()
    ? label.trim()
    : `Approved record ${index + 1}`;
}

export default function MemoryCanonShell({
  projectTitle,
  approvedRecordsByCategory = {},
  className = '',
}) {
  const shellClassName = ['memory-canon-shell', className].filter(Boolean).join(' ');
  const safeProjectTitle =
    typeof projectTitle === 'string' && projectTitle.trim()
      ? projectTitle.trim()
      : 'Current project';

  return (
    <section className={shellClassName} aria-label="Memory / Canon">
      <header className="memory-canon-shell__header">
        <p className="memory-canon-shell__eyebrow">Approved-only read-only shell</p>
        <h2>Memory / Canon</h2>
        <p>{safeProjectTitle}</p>
        <p>
          This shell shows approved records only. Candidate records remain in
          OMI/candidate review, and promotion/audit records are not canon by
          themselves.
        </p>
        <p>No apply-promotion in this phase. No memory/canon mutation in this phase.</p>
      </header>

      <div className="memory-canon-shell__categories">
        {APPROVED_MEMORY_CATEGORIES.map((category) => {
          const records = getCategoryRecords(approvedRecordsByCategory, category.id);

          return (
            <section
              className="memory-canon-shell__category"
              aria-label={category.label}
              key={category.id}
            >
              <h3>{category.label}</h3>
              <p>{category.description}</p>
              {records.length > 0 ? (
                <div className="memory-canon-shell__records">
                  <p>{records.length} approved records</p>
                  <ul>
                    {records.map((record, index) => (
                      <li key={getRecordLabel(record, index)}>
                        {getRecordLabel(record, index)}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="memory-canon-shell__empty-state">
                  <p>{category.emptyTitle}</p>
                  <p>{category.emptyBody}</p>
                </div>
              )}
            </section>
          );
        })}
      </div>
    </section>
  );
}
