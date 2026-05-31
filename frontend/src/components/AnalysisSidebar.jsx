function getScoreClass(score) {
  if (score > 7) {
    return 'score-good';
  }

  if (score >= 4) {
    return 'score-warning';
  }

  return 'score-danger';
}

function getList(value) {
  return Array.isArray(value) ? value : [];
}

function hasValidReport(report) {
  const warnings = Array.isArray(report?.warnings) ? report.warnings : [];

  return report
    && typeof report === 'object'
    && !Array.isArray(report)
    && !report.error
    && !warnings.includes('Failed to parse LLM response')
    && Number.isFinite(Number(report.coherence_score));
}

export default function AnalysisSidebar({
  report,
  selectedSceneId,
  isAnalyzing,
  onRunStoryCheck,
}) {
  const isValidReport = hasValidReport(report);
  const score = isValidReport ? Number(report.coherence_score) : null;
  const warnings = isValidReport ? getList(report.warnings) : [];
  const suggestions = isValidReport ? getList(report.suggestions) : [];

  return (
    <aside className="analysis-sidebar" aria-label="Analysis sidebar">
      <div className="panel-header">
        <p className="eyebrow">Analysis</p>
        <h2>Story Check</h2>
      </div>

      <div className="analysis-stack">
        {!selectedSceneId && <p className="muted-copy">Select a scene to run analysis.</p>}
        {isAnalyzing && <p className="muted-copy">Analyzing...</p>}
        {!isAnalyzing && isValidReport && (
          <>
            <div className="analysis-row">
              <span>Coherence Score</span>
              <strong className={getScoreClass(score)}>{score}/10</strong>
            </div>

            <section className="analysis-section">
              <h3>Warnings</h3>
              {warnings.length > 0 ? (
                <ul>
                  {warnings.map((warning, index) => (
                    <li key={`${warning}-${index}`}>{warning}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted-copy">No warnings.</p>
              )}
            </section>

            <section className="analysis-section">
              <h3>Suggestions</h3>
              {suggestions.length > 0 ? (
                <ul>
                  {suggestions.map((suggestion, index) => (
                    <li key={`${suggestion}-${index}`}>{suggestion}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted-copy">No suggestions.</p>
              )}
            </section>

            <section className="analysis-section">
              <h3>JSON Result</h3>
              <pre className="raw-response">{JSON.stringify(report, null, 2)}</pre>
            </section>
          </>
        )}
        {!isAnalyzing && report && !isValidReport && (
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
