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

function hasValidEvidenceReference(reference, sourceIdentity) {
  return reference
    && typeof reference === 'object'
    && !Array.isArray(reference)
    && reference.source_id === sourceIdentity?.source_id
    && reference.source_sha256 === sourceIdentity?.source_sha256
    && Number.isInteger(reference.start_byte)
    && Number.isInteger(reference.end_byte)
    && reference.start_byte >= 0
    && reference.end_byte > reference.start_byte
    && typeof reference.excerpt === 'string'
    && reference.offset_basis === 'utf-8-bytes-zero-based-half-open';
}

export function getGroundedStoryCheckDiagnostics(report) {
  const grounding = report?.grounding;
  if (!grounding || typeof grounding !== 'object' || Array.isArray(grounding)) {
    return [];
  }
  if (grounding.status !== 'completed' || !Array.isArray(grounding.diagnostics)) {
    return [];
  }

  return grounding.diagnostics.filter((diagnostic) => (
    diagnostic && typeof diagnostic === 'object' && typeof diagnostic.message === 'string'
  ));
}

export function getGroundingPresentationState(diagnostic, sourceIdentity) {
  const factual = diagnostic?.classification === 'factual_warning';
  if (diagnostic?.verification_state === 'quarantined') {
    return 'quarantined';
  }
  if (diagnostic?.verification_state !== 'verified') {
    return 'unverified';
  }

  const validator = diagnostic?.validator_result;
  const evidence = Array.isArray(diagnostic?.evidence) ? diagnostic.evidence : [];
  const validVerifiedState = validator?.outcome === 'supported'
    && validator?.direct_evidence_matched === true
    && evidence.length > 0
    && evidence.every((reference) => hasValidEvidenceReference(reference, sourceIdentity));
  if (validVerifiedState) {
    return 'verified';
  }

  return factual ? 'quarantined' : 'unverified';
}

function DiagnosticEvidence({ diagnostic, sourceIdentity }) {
  const evidence = asArray(diagnostic.evidence);
  const validator = diagnostic.validator_result && typeof diagnostic.validator_result === 'object'
    ? diagnostic.validator_result
    : {};

  return (
    <details className="grounding-evidence-details">
      <summary>Source and evidence details</summary>
      <dl className="analysis-metadata">
        <div>
          <dt>Source ID</dt>
          <dd><code>{sourceIdentity?.source_id ?? 'unavailable'}</code></dd>
        </div>
        <div>
          <dt>Source SHA-256</dt>
          <dd><code>{sourceIdentity?.source_sha256 ?? 'unavailable'}</code></dd>
        </div>
        <div>
          <dt>Validator outcome</dt>
          <dd>{validator.outcome ?? 'not available'}</dd>
        </div>
        <div>
          <dt>Reason codes</dt>
          <dd>{asArray(validator.reason_codes).join(', ') || 'none supplied'}</dd>
        </div>
      </dl>
      {evidence.length > 0 ? evidence.map((reference, index) => (
        <div className="grounding-evidence-reference" key={`${reference?.start_byte}-${index}`}>
          <p className="mini-heading">Exact UTF-8 evidence {index + 1}</p>
          <p><q>{reference?.excerpt}</q></p>
          <p className="muted-copy">
            Bytes {reference?.start_byte}–{reference?.end_byte}; {reference?.offset_basis}
          </p>
        </div>
      )) : (
        <p className="muted-copy">No validated direct evidence reference is attached.</p>
      )}
    </details>
  );
}

function GroundedDiagnosticList({ title, state, diagnostics, sourceIdentity, description }) {
  return (
    <section
      className={`analysis-section grounded-diagnostic-group is-${state}`}
      aria-label={`${title}: ${state}`}
    >
      <h3>{title}</h3>
      <p className="muted-copy">{description}</p>
      {diagnostics.length > 0 ? (
        <ul className="grounded-diagnostic-list">
          {diagnostics.map(({ diagnostic, presentationState }, index) => (
            <li key={diagnostic.diagnostic_id ?? `${state}-${index}`}>
              <p className={`grounding-status is-${presentationState}`}>
                Status: {presentationState}
              </p>
              <p className="grounded-diagnostic-text">{diagnostic.message}</p>
              <p className="muted-copy">Classification: {diagnostic.classification ?? 'unknown'}</p>
              <DiagnosticEvidence diagnostic={diagnostic} sourceIdentity={sourceIdentity} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted-copy">No {state} diagnostics returned.</p>
      )}
    </section>
  );
}

function GroundedStoryCheckDiagnostics({ report }) {
  const diagnostics = getGroundedStoryCheckDiagnostics(report);
  const sourceIdentity = report?.grounding?.source_identity;
  const grouped = { verified: [], unverified: [], quarantined: [] };
  diagnostics.forEach((diagnostic) => {
    const presentationState = getGroundingPresentationState(diagnostic, sourceIdentity);
    grouped[presentationState].push({ diagnostic, presentationState });
  });

  return (
    <div className="grounded-diagnostics" data-testid="story-check-grounded-diagnostics">
      <GroundedDiagnosticList
        title="Verified Findings"
        state="verified"
        diagnostics={grouped.verified}
        sourceIdentity={sourceIdentity}
        description="Verified means the deterministic validator matched direct evidence to this exact source identity."
      />
      <GroundedDiagnosticList
        title="Unverified Diagnostics"
        state="unverified"
        diagnostics={grouped.unverified}
        sourceIdentity={sourceIdentity}
        description="Useful structural diagnostics, questions, and observations remain visible but are not confirmed facts."
      />
      <GroundedDiagnosticList
        title="Quarantined Factual Warnings"
        state="quarantined"
        diagnostics={grouped.quarantined}
        sourceIdentity={sourceIdentity}
        description="Quarantined output is unsupported or mismatched model output. It is not confirmation or project truth."
      />
    </div>
  );
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

function refuseForbiddenProseIntent(intent) {
  return {
    refused: true,
    intent,
    boundary: 'analysis-only no-prose boundary',
    message: `forbidden intent: ${intent}; no generated story prose.`,
  };
}

function NoProseRefusal() {
  return (
    <section
      className="analysis-section"
      data-testid="ux2-no-prose-refusal-panel"
      aria-label="No-prose refusal boundary"
    >
      <h3>No-Prose Boundary</h3>
      <p className="muted-copy">
        This is an analysis-only no-prose boundary: no generated story prose.
      </p>
      <p
        className="muted-copy"
        data-testid="ux2-no-arbitrary-prompt-route"
      >
        arbitrary prompt route is unavailable.
      </p>
      <dl className="analysis-metadata">
        <div data-testid="ux2-no-prose-rewrite-refused">
          <dt>{refuseForbiddenProseIntent('rewrite').boundary}</dt>
          <dd>forbidden intent: rewrite; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-continue-refused">
          <dt>{refuseForbiddenProseIntent('continue').boundary}</dt>
          <dd>forbidden intent: continue; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-outline-refused">
          <dt>{refuseForbiddenProseIntent('outline').boundary}</dt>
          <dd>forbidden intent: outline; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-draft-refused">
          <dt>{refuseForbiddenProseIntent('draft').boundary}</dt>
          <dd>forbidden intent: draft; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-polish-refused">
          <dt>{refuseForbiddenProseIntent('polish').boundary}</dt>
          <dd>forbidden intent: polish; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-improve-refused">
          <dt>{refuseForbiddenProseIntent('improve').boundary}</dt>
          <dd>forbidden intent: improve; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-expand-refused">
          <dt>{refuseForbiddenProseIntent('expand').boundary}</dt>
          <dd>forbidden intent: expand; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-imitate-refused">
          <dt>{refuseForbiddenProseIntent('imitate').boundary}</dt>
          <dd>forbidden intent: imitate; no generated story prose.</dd>
        </div>
        <div data-testid="ux2-no-prose-generate-prose-refused">
          <dt>{refuseForbiddenProseIntent('generate prose').boundary}</dt>
          <dd>forbidden intent: generate prose; no generated story prose.</dd>
        </div>
      </dl>
    </section>
  );
}

function RuntimeArtifactEvidencePanel({ status }) {
  const evidenceStatus = status && typeof status === 'object' ? status : {};

  return (
    <section className="analysis-section" aria-label="Raw artifact evidence status">
      <h3>Raw Artifact Evidence</h3>
      <p
        className="muted-copy"
        data-testid="ux2-runtime-extraction-unavailable"
      >
        runtime extraction unavailable.
      </p>
      <dl
        className="analysis-metadata"
        data-testid="ux2-raw-artifact-read-only-evidence"
      >
        <div>
          <dt>Status</dt>
          <dd>{evidenceStatus.evidence_status ?? 'read-only raw artifact evidence'}</dd>
        </div>
        <div>
          <dt>Boundary</dt>
          <dd>{evidenceStatus.support_data_boundary ?? 'raw artifacts are support data only'}</dd>
        </div>
        <div>
          <dt>Canon</dt>
          <dd>{evidenceStatus.canon_boundary ?? 'raw artifacts are not canon'}</dd>
        </div>
        <div>
          <dt>Mutation</dt>
          <dd>
            {evidenceStatus.mutation_boundary
              ?? 'raw artifact inspection does not mutate memory or canon'}
          </dd>
        </div>
      </dl>
    </section>
  );
}

function AnalysisRuntimeStatusPanel() {
  return (
    <section
      className="analysis-section"
      data-testid="ux2-analysis-runtime-status"
      aria-label="Analysis runtime status"
    >
      <h3>Analysis Runtime Status</h3>
      <p className="muted-copy">
        analysis runtime labels only; runtime execution is not exposed.
      </p>
      <dl className="analysis-metadata">
        <div>
          <dt>NCP: NOT_EXPOSED</dt>
          <dd>NCP is structured context interchange only.</dd>
        </div>
        <div>
          <dt>Subtxt: NOT_EXPOSED</dt>
          <dd>Subtxt is rubric/diagnostic guidance only.</dd>
        </div>
        <div>
          <dt>dramatica-flow: NOT_EXPOSED</dt>
          <dd>dramatica-flow is audited allowlist only.</dd>
        </div>
        <div>
          <dt>Execution</dt>
          <dd>no runtime execution path.</dd>
        </div>
      </dl>
    </section>
  );
}

export default function AnalysisSidebar({
  report,
  selectedSceneId,
  selectedStoryCheckSourceId,
  selectedStoryCheckSource,
  rawArtifactEvidenceStatus,
  isAnalyzing,
  onRunStoryCheck,
}) {
  const hasReport = isReportObject(report);
  const score = hasReport ? asSafeScore(report.coherence_score) : null;
  const warnings = hasReport ? asArray(report.warnings) : [];
  const suggestions = hasReport ? asArray(report.suggestions) : [];
  const insufficientEvidence = hasReport ? asArray(report.insufficient_evidence) : [];
  const hasGroundedResult = hasReport
    && report?.grounding?.status === 'completed'
    && Array.isArray(report?.grounding?.diagnostics);
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
        {!selectedStoryCheckSourceId && (
          <section className="analysis-section">
            <h3>Selected Source Required</h3>
            <p className="muted-copy">
              Story Check requires a selected owner-authored source before analysis can run.
            </p>
          </section>
        )}
        {selectedStoryCheckSourceId && (
          <section
            className="analysis-section"
            data-testid="ux2-story-check-selected-source"
          >
            <h3>Project-scoped selected source</h3>
            <dl className="analysis-metadata">
              <div>
                <dt>Source</dt>
                <dd>{selectedStoryCheckSourceId}</dd>
              </div>
              <div>
                <dt>Owner control</dt>
                <dd>{selectedStoryCheckSource?.source_kind ?? 'owner-authored source'}</dd>
              </div>
              <div>
                <dt>Boundary</dt>
                <dd>Selection is not canon, memory, training data, or approved truth.</dd>
              </div>
            </dl>
            <p className="muted-copy">
              Story Check runs diagnostic-only against this owner-authored source.
            </p>
          </section>
        )}
        <section
          className="analysis-section"
          data-testid="ux2-story-check-diagnostic-result"
        >
          <h3>Diagnostic Result Boundary</h3>
          <p className="muted-copy">
            Story Check returns a diagnostic-only analysis-only result. model output is not canon,
            confidence is not truth, and output cannot become approved memory automatically.
          </p>
        </section>
        {!selectedSceneId && !selectedStoryCheckSourceId && (
          <p className="muted-copy">Select or import a source to run analysis.</p>
        )}
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
              The analysis-only result is diagnostic-only: model output is not canon,
              confidence is not truth, and output cannot become approved memory automatically.
            </p>

            <div className="analysis-row">
              <span>Coherence Score</span>
              {score === null ? (
                <strong>Unavailable</strong>
              ) : (
                <strong className={getScoreClass(score)}>{score}/10</strong>
              )}
            </div>

            {hasGroundedResult ? (
              <GroundedStoryCheckDiagnostics report={report} />
            ) : (
              <section className="analysis-section grounded-diagnostic-group is-quarantined">
                <h3>Legacy Ungrounded Output</h3>
                <p className="muted-copy">
                  Status: unverified. This response has no completed grounding contract and cannot be treated as verified.
                </p>
                <h4>Warnings</h4>
                {renderList(warnings, 'No warnings returned.')}
                <h4>Diagnostic Suggestions</h4>
                {renderList(suggestions, 'No diagnostic suggestions returned.')}
              </section>
            )}

            <section className="analysis-section">
              <h3>Throughline Alignment (unverified diagnostic context)</h3>
              <p className="muted-copy">Candidate diagnostic context. These legacy fields are not verified evidence.</p>
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

            {renderStatusReason('Theme Drift (unverified)', report.theme_drift)}
            {renderStatusReason('Character Consistency (unverified)', report.character_consistency)}

            {!hasGroundedResult && (
              <section className="analysis-section insufficient-evidence">
                <h3>Insufficient Evidence</h3>
                {renderList(insufficientEvidence, 'No insufficient-evidence notes returned.')}
              </section>
            )}

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
        <RuntimeArtifactEvidencePanel status={rawArtifactEvidenceStatus} />
        <AnalysisRuntimeStatusPanel />
        <NoProseRefusal />
      </div>

      <button
        className="primary-action"
        type="button"
        data-testid="ux2-story-check-run"
        disabled={!selectedStoryCheckSourceId || isAnalyzing}
        onClick={onRunStoryCheck}
      >
        {isAnalyzing ? 'Analyzing...' : 'Run Story Check'}
      </button>
    </aside>
  );
}
