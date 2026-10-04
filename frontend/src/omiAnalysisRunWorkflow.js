const SAFE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;
const SAFE_NCP_DESTINATION_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const DESTRUCTIVE_DESTINATION_TOKENS = new Set([
  'delete',
  'overwrite',
  'purge',
  'replace',
]);

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

export function validateNcpDestinationIdentifier(value) {
  if (typeof value !== 'string' || value === '') {
    return {
      valid: false,
      code: 'destination_required',
      message: 'Enter a new opaque target identifier.',
    };
  }

  if (
    value === '.'
    || value === '..'
    || !SAFE_NCP_DESTINATION_PATTERN.test(value)
    || value.includes('/')
    || value.includes('\\')
  ) {
    return {
      valid: false,
      code: 'unsafe_destination_identifier',
      message: 'Use only letters, numbers, dots, underscores, or hyphens. Filesystem paths are not accepted.',
    };
  }

  const normalizedValue = value.toLowerCase();
  if ([...DESTRUCTIVE_DESTINATION_TOKENS].some((token) => normalizedValue.includes(token))) {
    return {
      valid: false,
      code: 'destructive_destination_semantics',
      message: 'Overwrite, replace, delete, and purge semantics are disabled pending an owner decision.',
    };
  }

  return {
    valid: true,
    code: 'operator_selected_new_target',
    message: 'Safe opaque identifier selected for a new target. No path or write is authorized.',
  };
}

export function describeNcpInterfaceState(state) {
  const normalized = typeof state === 'string' ? state : '';
  const states = {
    loading: { tone: '', label: 'Loading interface contract', operable: false },
    empty: { tone: 'is-warning', label: 'No gateway record', operable: false },
    invalid: { tone: 'is-error', label: 'Validation blocked', operable: false },
    unavailable: { tone: 'is-warning', label: 'Interface unavailable', operable: false },
    request_failure: { tone: 'is-error', label: 'Interface check failed', operable: false },
    success: { tone: 'is-success', label: 'Diagnostics available', operable: true },
  };

  return states[normalized] ?? states.unavailable;
}
