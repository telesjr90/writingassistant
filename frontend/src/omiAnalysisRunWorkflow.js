const SAFE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;

const RUN_STATE_LABELS = Object.freeze({
  complete: 'Succeeded',
  partial: 'Partial results',
  degraded: 'Degraded',
  error: 'Failed',
  timeout: 'Timed out',
});

export function buildAnalysisSourceOptions(ideas) {
  if (!Array.isArray(ideas)) {
    return [];
  }

  return ideas
    .filter((idea) => (
      idea
      && typeof idea.idea_id === 'string'
      && SAFE_ID_PATTERN.test(idea.idea_id)
      && typeof idea.raw_idea === 'string'
      && idea.raw_idea.trim() !== ''
    ))
    .map((idea) => ({
      id: idea.idea_id,
      rawIdea: idea.raw_idea,
      label: idea.raw_idea.trim().replace(/\s+/g, ' ').slice(0, 88),
      status: typeof idea.status === 'string' ? idea.status : 'stored',
      provenance: idea.provenance ?? null,
    }));
}

export function isAnalysisToolRunnable(tool) {
  return Boolean(
    tool
    && tool.selectable === true
    && tool.preflight_status === 'enabled'
    && tool.readiness?.runtime_enabled === true
    && tool.readiness?.blocked !== true,
  );
}

export function analysisToolReason(tool) {
  if (!tool || typeof tool !== 'object') {
    return 'Tool readiness record is unavailable.';
  }
  if (tool.readiness?.blocked === true || tool.preflight_status === 'blocked') {
    return tool.readiness?.blocked_reason || 'Blocked by runtime configuration.';
  }
  if (tool.preflight_status === 'enabled' && tool.readiness?.runtime_enabled === true) {
    return 'Enabled by the backend for an explicit owner submission.';
  }
  if (tool.preflight_status === 'available') {
    return 'Dependency detected, but live runtime flags are disabled.';
  }
  if (tool.preflight_status === 'not_configured') {
    return 'Runtime is not configured.';
  }
  if (tool.preflight_status === 'unavailable') {
    return 'Runtime dependency is unavailable.';
  }
  if (tool.preflight_status === 'error') {
    return 'Readiness check failed closed.';
  }
  return tool.readiness?.explanation || 'Runtime is disabled by default.';
}

export function describeAnalysisRunState(state) {
  const normalized = typeof state === 'string' ? state.toLowerCase() : '';
  return {
    state: normalized || 'not_started',
    label: RUN_STATE_LABELS[normalized] ?? 'Not started',
    tone: normalized === 'complete'
      ? 'is-success'
      : normalized === 'error' || normalized === 'timeout'
        ? 'is-error'
        : normalized === 'partial' || normalized === 'degraded'
          ? 'is-warning'
          : '',
  };
}

export function makeAnalysisIdempotencyKey(projectId, sourceId) {
  const randomPart = globalThis.crypto?.randomUUID?.().replaceAll('-', '')
    ?? `${Date.now()}${Math.random().toString(16).slice(2)}`;
  const projectPart = SAFE_ID_PATTERN.test(projectId ?? '') ? projectId : 'project';
  const sourcePart = SAFE_ID_PATTERN.test(sourceId ?? '') ? sourceId : 'source';
  return `owner-run-${projectPart}-${sourcePart}-${randomPart}`.slice(0, 256);
}
