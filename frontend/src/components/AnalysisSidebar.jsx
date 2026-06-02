function getScoreClass(score) {
  if (score > 7) {
    return 'score-good';
  }

  if (score >= 4) {
    return 'score-warning';
  }

  return 'score-danger';
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function asSafeScore(value) {
  const score = Number(value);

  if (!Number.isFinite(score) || score < 0 || score > 10) {
    return null;
  }

  return score;
}

function isReportObject(report) {
  return report && typeof report === 'object' && !Array.isArray(report);
}

function formatPresent(value) {
  if (value === true) {
    return 'yes';
  }

  if (value === false) {
    return 'no';
  }

  return 'unknown';
}

function getDiagnosticEntries(diagnostics) {
  if (!diagnostics || typeof diagnostics !== 'object' || Array.isArray(diagnostics)) {
    return [];
  }

  return Object.entries(diagnostics).filter(([, value]) => {
    if (Array.isArray(value)) {
      return value.length > 0 && value.length <= 5;
    }

    return ['string', 'number', 'boolean'].includes(typeof value) || value === null;
  });
}

function formatValue(value) {
  if (typeof value === 'string') {
    return value;
  }

  if (value === null || ['number', 'boolean'].includes(typeof value)) {
    return String(value);
  }

  return JSON.stringify(value) ?? String(value);
}

function renderList(items, emptyText) {
  return items.length > 0 ? (
    <ul>
      {items.map((item, index) => (
        <li key={`${formatValue(item)}-${index}`}>{formatValue(item)}</li>
      ))}
    </ul>
  ) : (
    <p className="muted-copy">{emptyText}</p>
  );
}

function renderStatusReason(title, value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return (
      <section className="analysis-section">
        <h3>{title}</h3>
        <p className="muted-copy">No diagnostic status returned.</p>
      </section>
    );
  }

  return (
    <section className="analysis-section">
      <h3>{title}</h3>
      <dl className="analysis-metadata">
        <div>
          <dt>Status</dt>
          <dd>{value.status ?? 'unknown'}</dd>
        </div>
        <div>
          <dt>Reason</dt>
          <dd>{value.reason ?? 'No reason returned.'}</dd>
        </div>
      </dl>
    </section>
  );
}

function renderThroughline(title, value) {
  const throughline = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  const evidence = asArray(throughline.evidence);
  const concerns = asArray(throughline.concerns);

  return (
    <div className="throughline-diagnostic">
      <h4>{title}</h4>
      <dl className="analysis-metadata">
        <div>
          <dt>Present</dt>
          <dd>{formatPresent(throughline.present)}</dd>
        </div>
      </dl>
      <div>
        <p className="mini-heading">Evidence</p>
        {renderList(evidence, 'Evidence shown only when present. Missing evidence does not mean the throughline is absent.')}
      </div>
      <div>
        <p className="mini-heading">Concerns</p>
        {renderList(concerns, 'No concerns returned for this candidate diagnostic.')}
      </div>
    </div>
  );
}

export default function AnalysisSidebar({
  report,
  selectedSceneId,
  isAnalyzing,
  onRunStoryCheck,
}) {
  const hasReport = isReportObject(report);
  const score = hasReport ? asSafeScore(report.coherence_score) : null;
  const warnings = hasReport ? asArray(report.warnings) : [];
  const suggestions = hasReport ? asArray(report.suggestions) : [];
  const insufficientEvidence = hasReport ? asArray(report.insufficient_evidence) : [];
  const diagnostics = hasReport ? getDiagnosticEntries(report.diagnostics) : [];
  const throughlineAlignment = hasReport && report.throughline_alignment
    && typeof report.throughline_alignment === 'object'
    && !Array.isArray(report.throughline_alignment)
    ? report.throughline_alignment
    : null;

  return (
    <aside className="analysis-sidebar" aria-label="Analysis sidebar">
      <div className="panel-header">
        <p className="eyebrow">Analysis</p>
        <h2>Story Check</h2>
      </div>

      <div className="analysis-stack">
        {!selectedSceneId && <p className="muted-copy">Select a scene to run analysis.</p>}
        {isAnalyzing && <p className="muted-copy">Analyzing...</p>}
        {!isAnalyzing && hasReport && (
          <>
            {report.error && (
              <section className="analysis-section">
                <h3>Story Check Error</h3>
                <p className="error-copy">{report.error}</p>
              </section>
            )}

            <p className="analysis-note">
              Story Check is candidate analysis. It does not change project truth.
            </p>

            <div className="analysis-row">
              <span>Coherence Score</span>
              {score === null ? (
                <strong>Unavailable</strong>
              ) : (
                <strong className={getScoreClass(score)}>{score}/10</strong>
              )}
            </div>

            <section className="analysis-section">
              <h3>Warnings</h3>
              {renderList(warnings, 'No warnings returned.')}
            </section>

            <section className="analysis-section">
              <h3>Diagnostic Suggestions</h3>
              {renderList(suggestions, 'No diagnostic suggestions returned.')}
            </section>

            <section className="analysis-section">
              <h3>Throughline Alignment</h3>
              <p className="muted-copy">Candidate diagnostic. Evidence shown only when present.</p>
              {throughlineAlignment ? (
                <div className="throughline-grid">
                  {renderThroughline('Overall Story', throughlineAlignment.overall_story)}
                  {renderThroughline('Main Character', throughlineAlignment.main_character)}
                  {renderThroughline('Influence Character', throughlineAlignment.influence_character)}
                  {renderThroughline('Relationship Story', throughlineAlignment.relationship_story)}
                </div>
              ) : (
                <p className="muted-copy">Throughline details were not returned.</p>
              )}
            </section>

            {renderStatusReason('Theme Drift', report.theme_drift)}
            {renderStatusReason('Character Consistency', report.character_consistency)}

            <section className="analysis-section insufficient-evidence">
              <h3>Insufficient Evidence</h3>
              {renderList(insufficientEvidence, 'No insufficient-evidence notes returned.')}
            </section>

            {diagnostics.length > 0 && (
              <section className="analysis-section">
                <h3>Diagnostics</h3>
                <dl className="analysis-metadata">
                  {diagnostics.map(([key, value]) => (
                    <div key={key}>
                      <dt>{key}</dt>
                      <dd>{Array.isArray(value) ? value.join(', ') : String(value)}</dd>
                    </div>
                  ))}
                </dl>
              </section>
            )}

            <section className="analysis-section">
              <details className="raw-details">
                <summary>Raw JSON</summary>
                <pre className="raw-response">{JSON.stringify(report, null, 2)}</pre>
              </details>
            </section>
          </>
        )}
        {!isAnalyzing && report && !hasReport && (
          <section className="analysis-section">
            <h3>Raw Response</h3>
            <pre className="raw-response">{JSON.stringify(report, null, 2)}</pre>
          </section>
        )}
      </div>

      <button
        className="primary-action"
        type="button"
        disabled={!selectedSceneId || isAnalyzing}
        onClick={onRunStoryCheck}
      >
        {isAnalyzing ? 'Analyzing...' : 'Run Story Check'}
      </button>
    </aside>
  );
}
