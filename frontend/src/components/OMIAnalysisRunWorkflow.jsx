import { useEffect, useMemo, useState } from 'react';
import {
  fetchOmiAnalysisRunResult,
  fetchOmiAnalysisRunStatus,
  fetchOmiAnalysisTools,
  submitOmiAnalysisRun,
} from '../api.js';
import {
  analysisToolReason,
  buildAnalysisSourceOptions,
  describeAnalysisRunState,
  isAnalysisToolRunnable,
  makeAnalysisIdempotencyKey,
} from '../omiAnalysisRunWorkflow.js';

const NO_APPLY_BOUNDARY =
  'Live analysis never approves candidates, creates promotions, applies promotion, or changes approved Memory/Canon.';

function text(value, fallback = 'Not reported') {
  return typeof value === 'string' && value.trim() !== '' ? value : fallback;
}

function formatToolName(adapterId) {
  return text(adapterId, 'Unknown tool').replaceAll('_', ' ');
}

function MetadataList({ entries }) {
  return (
    <dl className="omi-analysis-metadata">
      {entries.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd><code>{text(value)}</code></dd>
        </div>
      ))}
    </dl>
  );
}

function ReferenceInspection({ run, resultRecord }) {
  const manifest = resultRecord?.manifest_ref ?? run?.manifest_ref;
  const artifact = resultRecord?.raw_artifact_ref ?? run?.raw_artifact_ref;
  const ledger = resultRecord?.evidence_ledger_ref ?? run?.evidence_ledger_ref;

  return (
    <div className="omi-analysis-inspection-grid">
      <section className="omi-analysis-card" aria-labelledby="omi-run-manifest-heading">
        <h4 id="omi-run-manifest-heading">Manifest reference</h4>
        {manifest ? (
          <MetadataList entries={[
            ['Contract version', manifest.contract_version],
            ['Manifest hash', manifest.manifest_hash],
            ['Safe relative path', manifest.relative_path],
          ]} />
        ) : <p className="muted-copy">No manifest reference is available.</p>}
      </section>
      <section className="omi-analysis-card" aria-labelledby="omi-run-artifact-heading">
        <h4 id="omi-run-artifact-heading">Raw artifact reference</h4>
        {artifact ? (
          <MetadataList entries={[
            ['Artifact ID', artifact.artifact_id],
            ['Manifest hash', artifact.manifest_hash],
            ['Bundle hash', artifact.bundle_hash],
          ]} />
        ) : <p className="muted-copy">No artifact reference is available.</p>}
        <p className="muted-copy">References only; raw bytes and hidden filesystem paths are not exposed.</p>
      </section>
      <section className="omi-analysis-card" aria-labelledby="omi-run-ledger-heading">
        <h4 id="omi-run-ledger-heading">Evidence ledger</h4>
        {ledger ? (
          <MetadataList entries={[
            ['Finalized event count', String(ledger.event_count_at_finalization ?? '')],
            ['Current event count', String(ledger.current_event_count ?? '')],
            ['Finalized head hash', ledger.head_hash_at_finalization],
            ['Current head hash', ledger.current_head_hash],
          ]} />
        ) : <p className="muted-copy">No evidence-ledger reference is available.</p>}
      </section>
    </div>
  );
}

function ResultInspection({ resultRecord }) {
  const result = resultRecord?.result;
  const adapters = Array.isArray(result?.adapter_results) ? result.adapter_results : [];
  const findings = Array.isArray(result?.findings) ? result.findings : [];

  if (!resultRecord) {
    return <p className="muted-copy">No result has been requested yet.</p>;
  }
  if (resultRecord.result_available !== true || !result) {
    return (
      <div className="omi-analysis-notice is-warning" role="status">
        <strong>Result content unavailable.</strong>
        <span>
          Artifact state: {text(resultRecord.artifact_status)}. References remain visible for audit.
        </span>
      </div>
    );
  }

  return (
    <div className="omi-analysis-results">
      <p className="muted-copy">
        Analysis status: <strong>{text(result.analysis_status)}</strong>. Findings are candidate-only
        support material and are not persisted into the review queue by this workflow.
      </p>
      <div className="omi-analysis-adapter-grid" aria-label="Contributor results">
        {adapters.length === 0 ? (
          <p className="muted-copy">No contributor results were returned.</p>
        ) : adapters.map((adapter, index) => (
          <article className="omi-analysis-card" key={`${adapter?.adapter ?? 'adapter'}-${index}`}>
            <h4>{formatToolName(adapter?.adapter)}</h4>
            <span className={`omi-status-badge ${adapter?.state === 'succeeded' ? 'is-success' : 'is-warning'}`}>
              {text(adapter?.state)}
            </span>
            <p>{text(adapter?.explanation, 'No contributor explanation was returned.')}</p>
            <p className="muted-copy">
              Candidate outputs: {Array.isArray(adapter?.candidates) ? adapter.candidates.length : 0}
            </p>
          </article>
        ))}
      </div>
      <section className="omi-analysis-findings" aria-labelledby="omi-analysis-findings-heading">
        <h4 id="omi-analysis-findings-heading">Normalized findings</h4>
        {findings.length === 0 ? (
          <p className="muted-copy">No normalized findings were returned.</p>
        ) : (
          <ol>
            {findings.map((finding, index) => {
              const claim = finding?.extracted_claim
                ?? finding?.diagnostic_claim
                ?? finding?.label
                ?? 'Unnamed finding';
              return (
                <li key={finding?.normalized_finding_id ?? finding?.raw_finding_id ?? index}>
                  <strong>{claim}</strong>
                  <span>Source locator: {text(finding?.source_locator)}</span>
                  <span>
                    Evidence references: {Array.isArray(finding?.evidence) ? finding.evidence.length : 0}
                  </span>
                  <span>
                    Provenance: {text(finding?.provenance?.tool_source ?? finding?.source_adapter)}
                  </span>
                </li>
              );
            })}
          </ol>
        )}
      </section>
    </div>
  );
}

export default function OMIAnalysisRunWorkflow({
  activeProjectId,
  ideas = [],
  candidates = [],
  onBackToDashboard = () => {},
  onOpenCandidateReview = () => {},
  onOpenGroupedReview = () => {},
}) {
  const sources = useMemo(() => buildAnalysisSourceOptions(ideas), [ideas]);
  const [selectedSourceId, setSelectedSourceId] = useState('');
  const [toolsReport, setToolsReport] = useState(null);
  const [selectedTools, setSelectedTools] = useState([]);
  const [ownerConfirmed, setOwnerConfirmed] = useState(false);
  const [phase, setPhase] = useState('preflight');
  const [error, setError] = useState('');
  const [run, setRun] = useState(null);
  const [resultRecord, setResultRecord] = useState(null);
  const [lastSubmission, setLastSubmission] = useState(null);
  const selectedSource = sources.find((source) => source.id === selectedSourceId) ?? null;
  const tools = Array.isArray(toolsReport?.tools) ? toolsReport.tools : [];
  const runnableTools = tools.filter(isAnalysisToolRunnable);
  const runState = describeAnalysisRunState(run?.state);
  const candidateCount = Array.isArray(candidates) ? candidates.length : 0;

  async function loadPreflight() {
    setPhase('preflight');
    setError('');
    try {
      const report = await fetchOmiAnalysisTools(activeProjectId);
      setToolsReport(report);
      setSelectedTools((current) => current.filter((toolId) => (
        report.tools?.some((tool) => tool.adapter_id === toolId && isAnalysisToolRunnable(tool))
      )));
      setPhase('ready');
    } catch (preflightError) {
      setToolsReport(null);
      setSelectedTools([]);
      setError(preflightError.message);
      setPhase('preflight_failed');
    }
  }

  useEffect(() => {
    setSelectedSourceId('');
    setSelectedTools([]);
    setOwnerConfirmed(false);
    setRun(null);
    setResultRecord(null);
    setLastSubmission(null);
    loadPreflight();
  }, [activeProjectId]);

  function toggleTool(toolId) {
    const tool = tools.find((item) => item.adapter_id === toolId);
    if (!isAnalysisToolRunnable(tool)) {
      return;
    }
    setSelectedTools((current) => (
      current.includes(toolId)
        ? current.filter((value) => value !== toolId)
        : [...current, toolId].sort()
    ));
    setOwnerConfirmed(false);
  }

  async function inspectRun(runId, statusRecord = null) {
    setPhase('inspecting');
    setError('');
    try {
      const status = statusRecord ?? await fetchOmiAnalysisRunStatus(activeProjectId, runId);
      setRun(status);
      const result = await fetchOmiAnalysisRunResult(activeProjectId, runId);
      setResultRecord(result);
      setPhase('complete');
    } catch (inspectionError) {
      setError(`${inspectionError.message} The durable run can be reinspected without rerunning it.`);
      setPhase('inspection_failed');
    }
  }

  async function executeSubmission(payload) {
    setPhase('submitting');
    setError('');
    setResultRecord(null);
    try {
      const submitted = await submitOmiAnalysisRun(activeProjectId, payload);
      setRun(submitted);
      await inspectRun(submitted.run_id, submitted);
    } catch (submissionError) {
      setError(submissionError.message);
      setPhase('submission_failed');
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (!selectedSource || selectedTools.length === 0 || !ownerConfirmed) {
      setError('Select a stored source and at least one enabled tool, then confirm the owner action.');
      return;
    }
    const payload = {
      raw_idea: selectedSource.rawIdea,
      source_idea_id: selectedSource.id,
      requested_adapters: [...selectedTools],
      allow_deterministic_fallback: false,
      idempotency_key: makeAnalysisIdempotencyKey(activeProjectId, selectedSource.id),
    };
    setLastSubmission(payload);
    executeSubmission(payload);
  }

  const submitting = phase === 'submitting' || phase === 'inspecting';
  const canSubmit = Boolean(
    selectedSource
    && selectedTools.length > 0
    && ownerConfirmed
    && !submitting,
  );

  return (
    <section className="omi-analysis-run" aria-labelledby="omi-analysis-run-heading">
      <div className="omi-analysis-header">
        <div>
          <p className="eyebrow">Owner-controlled analysis control plane</p>
          <h2 id="omi-analysis-run-heading">Run analysis on a stored owner source</h2>
          <p className="muted-copy">
            Readiness is checked before selection. Submission is synchronous and does not persist candidates.
          </p>
        </div>
        <button className="secondary-button" type="button" onClick={onBackToDashboard}>
          Back to OMI Dashboard
        </button>
      </div>

      <section className="omi-analysis-boundary" aria-labelledby="omi-analysis-boundary-heading">
        <h3 id="omi-analysis-boundary-heading">Live-run boundary</h3>
        <p>{NO_APPLY_BOUNDARY}</p>
        <p>Partial and successful outputs remain evidence/provenance-backed review material, not project truth.</p>
      </section>

      <form className="omi-analysis-form" onSubmit={handleSubmit}>
        <section className="omi-analysis-card" aria-labelledby="omi-analysis-source-heading">
          <h3 id="omi-analysis-source-heading">1. Select the exact owner source</h3>
          {sources.length === 0 ? (
            <div className="omi-analysis-notice is-warning" role="status">
              No stored owner-authored OMI idea is available. Add owner input before submitting analysis.
            </div>
          ) : (
            <label className="omi-analysis-field" htmlFor="omi-analysis-source">
              Stored owner source
              <select
                id="omi-analysis-source"
                value={selectedSourceId}
                onChange={(event) => {
                  setSelectedSourceId(event.target.value);
                  setOwnerConfirmed(false);
                }}
              >
                <option value="">Select a source</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.id}: {source.label}
                  </option>
                ))}
              </select>
            </label>
          )}
          {selectedSource ? (
            <div className="omi-analysis-source-preview">
              <strong>Exact selected source</strong>
              <p>{selectedSource.rawIdea}</p>
              <span>Source identity: {selectedSource.id}; status: {selectedSource.status}</span>
              <span>
                Provenance: {text(selectedSource.provenance?.source_label, 'Owner-authored OMI input')};
                {' '}created by {text(selectedSource.provenance?.created_by, 'owner')}.
              </span>
            </div>
          ) : null}
        </section>

        <section className="omi-analysis-card" aria-labelledby="omi-analysis-tools-heading">
          <div className="omi-analysis-section-heading">
            <div>
              <h3 id="omi-analysis-tools-heading">2. Review readiness and select tools</h3>
              <p className="muted-copy">Only backend-enabled tools can be selected.</p>
            </div>
            <button className="secondary-button" type="button" onClick={loadPreflight} disabled={submitting}>
              Recheck readiness
            </button>
          </div>
          <div aria-live="polite" aria-atomic="true">
            {phase === 'preflight' ? <p className="omi-loading-state">Checking runtime readiness…</p> : null}
            {phase === 'preflight_failed' ? (
              <div className="omi-analysis-notice is-error" role="alert">
                <strong>Readiness check failed.</strong>
                <span>{error}</span>
              </div>
            ) : null}
          </div>
          {tools.length > 0 ? (
            <fieldset className="omi-analysis-tool-list">
              <legend>Backend-reported analysis tools</legend>
              {tools.map((tool) => {
                const runnable = isAnalysisToolRunnable(tool);
                const reasonId = `omi-tool-${tool.adapter_id}-reason`;
                return (
                  <label className={`omi-analysis-tool ${runnable ? '' : 'is-disabled'}`} key={tool.adapter_id}>
                    <input
                      type="checkbox"
                      checked={selectedTools.includes(tool.adapter_id)}
                      disabled={!runnable || submitting}
                      aria-describedby={reasonId}
                      onChange={() => toggleTool(tool.adapter_id)}
                    />
                    <span>
                      <strong>{formatToolName(tool.adapter_id)}</strong>
                      <span className={`omi-status-badge ${runnable ? 'is-success' : 'is-warning'}`}>
                        {text(tool.preflight_status)}
                      </span>
                      <small id={reasonId}>{analysisToolReason(tool)}</small>
                    </span>
                  </label>
                );
              })}
            </fieldset>
          ) : phase === 'ready' ? (
            <div className="omi-analysis-notice is-warning" role="status">
              The backend reported no analysis tools.
            </div>
          ) : null}
          {toolsReport ? (
            <p className="muted-copy">
              Execution mode: {text(toolsReport.execution_mode)}. Timeout and cancellation are
              {toolsReport.timeout?.supported || toolsReport.cancellation?.supported ? ' backend-defined' : ' not supported'}.
              {runnableTools.length === 0 ? ' No tool is currently enabled for submission.' : ''}
            </p>
          ) : null}
        </section>

        <section className="omi-analysis-card" aria-labelledby="omi-analysis-submit-heading">
          <h3 id="omi-analysis-submit-heading">3. Confirm owner submission</h3>
          <label className="omi-analysis-confirmation">
            <input
              type="checkbox"
              checked={ownerConfirmed}
              disabled={!selectedSource || selectedTools.length === 0 || submitting}
              onChange={(event) => setOwnerConfirmed(event.target.checked)}
            />
            <span>
              I confirm this exact source and tool selection. I understand the result is non-canon
              review material and will not be approved, promoted, or applied automatically.
            </span>
          </label>
          <div className="omi-analysis-actions">
            <button className="primary-button" type="submit" disabled={!canSubmit}>
              {submitting ? 'Submission in progress…' : 'Submit analysis run'}
            </button>
            <span className="muted-copy">
              No run starts until this button is activated. No progress percentage is fabricated.
            </span>
          </div>
        </section>
      </form>

      <section className="omi-analysis-card" aria-labelledby="omi-analysis-progress-heading">
        <div className="omi-analysis-section-heading">
          <div>
            <h3 id="omi-analysis-progress-heading">Run progress and recovery</h3>
            <p className="muted-copy">The backend completes submissions synchronously and reports a final state.</p>
          </div>
          <span className={`omi-status-badge ${runState.tone}`} role="status" aria-live="polite">
            {submitting ? (phase === 'submitting' ? 'Submitting' : 'Inspecting result') : runState.label}
          </span>
        </div>
        {error && phase !== 'preflight_failed' ? (
          <div className="omi-analysis-notice is-error" role="alert">
            <strong>{phase === 'inspection_failed' ? 'Inspection failed.' : 'Submission failed.'}</strong>
            <span>{error}</span>
          </div>
        ) : null}
        <div className="omi-analysis-actions">
          {phase === 'submission_failed' && lastSubmission ? (
            <button className="secondary-button" type="button" onClick={() => executeSubmission(lastSubmission)}>
              Retry same request safely
            </button>
          ) : null}
          {run?.run_id && phase === 'inspection_failed' ? (
            <button className="secondary-button" type="button" onClick={() => inspectRun(run.run_id)}>
              Reinspect durable run
            </button>
          ) : null}
          <button className="secondary-button" type="button" disabled aria-describedby="omi-no-cancel-reason">
            Cancel run
          </button>
          <span id="omi-no-cancel-reason" className="muted-copy">
            Cancellation and timeout actions are unavailable because the backend exposes no such route.
          </span>
        </div>
        {run ? (
          <MetadataList entries={[
            ['Run ID', run.run_id],
            ['Source idea ID', lastSubmission?.source_idea_id],
            ['Selected tools', lastSubmission?.requested_adapters?.join(', ')],
            ['Coverage', run.coverage],
            ['Analysis status', run.analysis_status],
            ['Created', run.created_at],
            ['Finalized', run.finalized_at],
            ['Idempotent replay', String(run.idempotent_replay === true)],
            ['Candidate persistence performed', String(run.candidate_persistence_performed === true)],
            ['Automatic approval/promotion performed', String(run.automatic_approval_or_promotion_performed === true)],
            ['Memory/Canon mutation performed', String(run.memory_canon_mutation_performed === true)],
            ['Story prose generated', String(run.story_prose_generated === true)],
          ]} />
        ) : null}
      </section>

      <section className="omi-analysis-card" aria-labelledby="omi-analysis-results-heading">
        <h3 id="omi-analysis-results-heading">Result inspection</h3>
        <ResultInspection resultRecord={resultRecord} />
      </section>

      <section className="omi-analysis-inspection" aria-labelledby="omi-analysis-audit-heading">
        <h3 id="omi-analysis-audit-heading">Provenance, manifest, and evidence audit</h3>
        <ReferenceInspection run={run} resultRecord={resultRecord} />
      </section>

      <section className="omi-analysis-card" aria-labelledby="omi-analysis-handoff-heading">
        <h3 id="omi-analysis-handoff-heading">Candidate-review handoff</h3>
        <p>
          This run persisted no candidates. Existing stored candidates remain separate and require explicit owner review.
        </p>
        <div className="omi-analysis-actions">
          <button
            className="secondary-button"
            type="button"
            disabled={candidateCount === 0}
            aria-describedby={candidateCount === 0 ? 'omi-no-candidates-reason' : undefined}
            onClick={onOpenCandidateReview}
          >
            Open existing candidate review
          </button>
          <button className="secondary-button" type="button" onClick={onOpenGroupedReview}>
            Open grouped owner review
          </button>
          {candidateCount === 0 ? (
            <span id="omi-no-candidates-reason" className="muted-copy">
              No stored candidate is available for handoff.
            </span>
          ) : null}
        </div>
      </section>

      <section className="omi-analysis-boundary" aria-labelledby="omi-analysis-apply-heading">
        <h3 id="omi-analysis-apply-heading">Apply-promotion remains separate</h3>
        <p>{NO_APPLY_BOUNDARY}</p>
        <button className="secondary-button" type="button" disabled aria-describedby="omi-analysis-apply-reason">
          Apply to Memory/Canon
        </button>
        <p id="omi-analysis-apply-reason" className="muted-copy">
          Disabled here. Apply-promotion requires a separately prepared, approved, and confirmed promotion contract.
        </p>
      </section>
    </section>
  );
}
