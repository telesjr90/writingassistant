"""OMI AI/tool-assisted analysis orchestrator contract and adapter boundaries.

T005 scope (PHASE8-IMPL-023):

  - Defines the orchestrator entrypoint ``analyze_omi_raw_idea_with_tools``.
  - Declares the allowed OMI tool adapter identities, each adapter's per-tool
    contract, and the allowed adapter result states.
  - Defines the common normalized finding schema that every adapter output must
    conform to before candidate normalization runs.
  - Wires ``deterministic_fallback`` to the existing
    ``project_manager.extract_omi_candidates_from_raw_idea`` marker extractor
    as fallback/safety baseline ONLY (the corrected MVP path is
    AI/tool-assisted, not deterministic-marker-only).
  - Wires ``booknlp`` and ``spacy`` through fixture-only local NLP contracts
    that normalize evidence-backed entity/event/object/relationship-style
    support into candidate-only OMI findings without importing or running
    live runtimes.
  - Stubs every other adapter as fail-closed: unimplemented adapters return
    ``unavailable`` / ``skipped`` / ``failed_closed`` with an explanation and
    never fabricate candidates.
  - Enforces a no-prose guard against adapter outputs: any prose-like,
    continuation-like, rewrite-like, or draft-like free-text output that could
    be confused with story prose is rejected as ``failed_closed`` with no
    persisted candidates.
  - Defines fusion/dedupe contract fields even though full fusion is deferred
    to T010 (T005 ships the field contract and a deterministic fingerprint
    helper only).

Boundaries (non-negotiable):

  - No Ollama, Story Check, BookNLP, spaCy, NCP, Subtxt, or dramatica-flow
    live runtime calls. This module does not import or invoke any of them.
  - No Memory/Canon mutation.
  - No promotion records, no apply-promotion, no canon promotion.
  - No story prose generation, rewriting, continuation, drafting, polishing,
    improvement, expansion, or imitation.
  - No package installs, no new external dependencies.
  - No filesystem writes beyond existing project_manager helpers when the
    caller opts into persistence via ``project_manager.extract_omi_candidates_from_raw_idea``.

All helpers are pure (standard library only, deterministic, no side effects
beyond what ``extract_omi_candidates_from_raw_idea`` already performs through
``project_manager`` when ``persist_candidates=True``).
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Adapter identity and result-state constants
# ---------------------------------------------------------------------------

OMI_TOOL_ADAPTER_IDENTITIES: frozenset[str] = frozenset(
    {
        "ollama_model",
        "story_check",
        "booknlp",
        "spacy",
        "ncp",
        "subtxt",
        "dramatica_flow",
        "deterministic_fallback",
    }
)

OMI_ADAPTER_RESULT_STATES: frozenset[str] = frozenset(
    {
        "succeeded",
        "empty",
        "skipped",
        "unavailable",
        "failed_closed",
        "error",
    }
)

# Adapter result states that mean a real run could not happen and therefore
# must not produce any candidate findings.
OMI_ADAPTER_NO_CANDIDATE_RESULT_STATES: frozenset[str] = frozenset(
    {
        "empty",
        "skipped",
        "unavailable",
        "failed_closed",
        "error",
    }
)

# Adapter result states that mean a real run completed and may produce
# candidate findings (succeeded) or may simply have found nothing (empty).
OMI_ADAPTER_PRODUCING_RESULT_STATES: frozenset[str] = frozenset({"succeeded"})

# Deterministic fallback identity and contract notes.
OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME = "deterministic_fallback"
OMI_DETERMINISTIC_FALLBACK_EXPLANATION = (
    "deterministic_fallback is fallback/safety baseline only; "
    "it wraps project_manager.extract_omi_candidates_from_raw_idea and is "
    "NOT the corrected MVP OMI analysis path."
)

# Default adapter order: deterministic_fallback runs LAST as a safety baseline
# if and only if the orchestrator is configured to allow it and all requested
# AI/tool adapters return empty/skipped/unavailable/failed_closed/error with
# no produced findings. Real AI/tool adapters would run first in T006+.
OMI_DEFAULT_ADAPTERS: tuple[str, ...] = (
    "ollama_model",
    "story_check",
    "booknlp",
    "spacy",
    "ncp",
    "subtxt",
    "dramatica_flow",
)

# Per-tool adapter behavior contracts. These describe what a real adapter
# implementation MUST do at the boundary; they are NOT exercised here.
OMI_ADAPTER_CONTRACTS: dict[str, dict[str, Any]] = {
    "ollama_model": {
        "behavior": (
            "structured JSON extraction only; schema-bound; no prose, no rewrite, "
            "no continuation, no outline, no drafting, no improvement suggestion; "
            "fail closed on invalid schema or unsafe prose-like output."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "character",
            "location",
            "organization",
            "object",
            "timeline_event",
            "relationship",
            "plot_thread",
            "story_fact",
            "open_question",
            "storyform_context",
            "diagnostic_question",
        ),
    },
    "story_check": {
        "behavior": (
            "diagnostic-only structural observations and questions; no prose "
            "suggestions; requires storyform/context to be available; fails "
            "closed if storyform context is missing."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "storyform_context",
            "diagnostic_question",
            "continuity_warning",
            "open_question",
            "world_rule",
        ),
    },
    "booknlp": {
        "behavior": (
            "local NLP entities, entity-like mentions, events, and coreference-style "
            "support only; every finding must point to a source excerpt or "
            "source_locator; no canon claims."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "character",
            "location",
            "organization",
            "object",
            "timeline_event",
            "relationship",
            "evidence_note",
        ),
    },
    "spacy": {
        "behavior": (
            "local NLP entities, noun-chunk mentions, and sentence-segmentation "
            "support only; every finding must point to a source excerpt or "
            "source_locator; no canon claims."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "character",
            "location",
            "organization",
            "object",
            "timeline_event",
            "evidence_note",
        ),
    },
    "ncp": {
        "behavior": (
            "structural context candidate mapping and import/export candidate "
            "representation only; NOT a truth export; fails closed on missing "
            "NCP storyform context."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "storyform_context",
            "world_rule",
            "open_question",
            "diagnostic_question",
        ),
    },
    "subtxt": {
        "behavior": (
            "rubric/reference guidance for diagnostic structural interpretation "
            "only; NOT automatic Dramatica truth; fails closed if Subtxt "
            "context is unavailable."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "storyform_context",
            "world_rule",
            "diagnostic_question",
        ),
    },
    "dramatica_flow": {
        "behavior": (
            "analysis-pattern reference only for narrative-state patterns, "
            "promises, mysteries, causal chains, thread activity, relationship "
            "shifts; generation/revision/continuation remain disabled; no "
            "outlines or story text."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "plot_thread",
            "story_fact",
            "open_question",
            "diagnostic_question",
            "continuity_warning",
        ),
    },
    "deterministic_fallback": {
        "behavior": (
            "wraps the existing project_manager.extract_omi_candidates_from_raw_idea "
            "marker extractor (PHASE8-IMPL-023-T004) as fallback/safety "
            "baseline ONLY. Not the corrected MVP OMI analysis path."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "character",
            "location",
            "organization",
            "object",
            "timeline_event",
            "relationship",
            "plot_thread",
            "story_fact",
            "open_question",
            "storyform_context",
        ),
    },
}


# ---------------------------------------------------------------------------
# Normalized finding / candidate schema
# ---------------------------------------------------------------------------

# Allowed adapter/normalization candidate types. Subset of OMI_EXTRACTED_
# CANDIDATE_TYPES plus non-canon diagnostic/evidence types. The orchestrator
# is the bridge between raw adapter output and the existing OMI candidate
# schema in project_manager; for fusion/dedupe purposes every finding
# carries one of these types.
OMI_ORCHESTRATOR_FINDING_TYPES: frozenset[str] = frozenset(
    {
        "character",
        "location",
        "organization",
        "object",
        "timeline_event",
        "relationship",
        "plot_thread",
        "story_fact",
        "open_question",
        "storyform_context",
        "diagnostic_question",
        "continuity_warning",
        "world_rule",
        "evidence_note",
    }
)

# Required normalized-finding fields. Every finding, after normalization,
# must carry these. Persistence to project_manager requires the existing
# OMI candidate schema; this orchestrator does NOT persist fused candidates
# (that is deferred to T011).
OMI_NORMALIZED_FINDING_REQUIRED_FIELDS: tuple[str, ...] = (
    "candidate_type",
    "label",
    "extracted_claim",
    "evidence",
    "source_locator",
    "provenance",
    "source_adapter",
    "support_label",
    "owner_decision",
    "review_status",
    "raw_finding_id",
)

# Allowed owner-decision states carried on every normalized finding. The
# default is "pending"; approval is never automatic at the orchestrator
# layer.
OMI_FINDING_OWNER_DECISION_STATES: frozenset[str] = frozenset(
    {"pending", "approve", "reject", "revise", "needs_review"}
)

OMI_FINDING_OWNER_DECISION_DEFAULT = "pending"

# Allowed review_status / candidate_status on normalized findings. All such
# statuses are review-pending; canon/approved/promoted are forbidden here.
OMI_FINDING_REVIEW_STATUSES: frozenset[str] = frozenset(
    {"candidate", "review_pending", "candidate_review_pending"}
)

OMI_FINDING_REVIEW_STATUS_DEFAULT = "candidate_review_pending"

# Required evidence fields. Evidence must point to source excerpt or
# source_locator (or both); without evidence a finding is rejected as
# failed_closed.
OMI_FINDING_EVIDENCE_REQUIRED_FIELDS: tuple[str, ...] = (
    "source_excerpt_or_locator",
)

# Required provenance fields. provenance.tool_source must be the adapter
# name; provenance.adapter must match it; provenance.support is support
# strength only (never called "truth" or "canonical").
OMI_FINDING_PROVENANCE_REQUIRED_FIELDS: tuple[str, ...] = (
    "tool_source",
    "adapter",
    "support",
)

# Fusion / dedupe contract fields. T010 implements the full fusion algorithm;
# T005 ships the field contract and a deterministic fingerprint helper.
OMI_FUSION_FINDING_FIELDS: tuple[str, ...] = (
    "normalized_finding_id",
    "source_adapter",
    "evidence_fingerprint",
    "candidate_fingerprint",
    "duplicate_of",
    "related_finding_ids",
    "conflict_group_id",
    "uncertainty_label",
    "support_label",
)

# Forbid labels that imply truth/canon/approval/confirmation. These must
# never appear in any orchestrator-produced field.
_OMI_FORBIDDEN_TRUTH_LABELS = (
    "truth",
    "canon",
    "canonical",
    "approved",
    "promoted",
    "confirmed_fact",
)

# Heuristic prose-like prefixes/patterns. The orchestrator rejects findings
# whose extracted_claim looks like story prose. The patterns here are
# conservative: they catch only obvious prose-shaped output. They never
# judge legitimate structural-extraction claims (which are short noun
# phrases or evidence-anchored sentences).
_PROSE_LIKE_PREFIX_RE = re.compile(
    r"^(the\s+room|the\s+chapter|the\s+scene|in\s+chapter|in\s+scene|"
    r"once\s+upon|it\s+was\s+a|there\s+was\s+a|two\s+days\s+later|"
    r"meanwhile|later\s+that|finally|chapter\s+\d|scene\s+\d)\b",
    re.IGNORECASE,
)
# A claim is considered prose-like if it is long, ends in a period, contains
# dialogue-style double quotes, or starts with a capitalized narrative verb
# and contains more than ~20 words.
_DIALOGUE_QUOTE_RE = re.compile(r"[“”‘’\"]")
# Prose-intent prefixes that indicate the adapter/model is producing
# story-prose output (rewriting, polishing, continuing, drafting, improving,
# expanding, imitating, revising, outlining, generating). T006 rejects these
# so adapters cannot smuggle generated prose through "support only" labels.
_PROSE_INTENT_PREFIX_RE = re.compile(
    r"^\s*("
    r"here\s+is\s+a\s+(better|polished|revised|improved|expanded|cleaner)\s+version"
    r"|here'?s\s+a\s+(better|polished|revised|improved|expanded|cleaner)\s+version"
    r"|polished\s+(version|scene|chapter|draft|passage)"
    r"|revised\s+(version|scene|chapter|draft|passage)"
    r"|rewritten\s+(version|scene|chapter|draft|passage)"
    r"|improved\s+(version|scene|chapter|draft|passage)"
    r"|expanded\s+(version|scene|chapter|draft|passage)"
    r"|continuation\s*:"
    r"|rewrite\s*:"
    r"|outline\s*:"
    r"|draft\s*:"
    r"|expanded\s+scene"
    r"|chapter\s+\d+\s*[:\-]"
    r"|scene\s+\d+\s*[:\-]"
    r"|proceeding\s+with\s+the\s+(scene|chapter|story|narrative)"
    r")",
    re.IGNORECASE,
)


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return dict(value)


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    return list(value)


# ---------------------------------------------------------------------------
# Public helpers (alphabetical)
# ---------------------------------------------------------------------------


def adapter_contract(adapter_name: str) -> dict[str, Any]:
    """Return the per-tool contract document for ``adapter_name``.

    Raises ``ValueError`` if ``adapter_name`` is not a known OMI tool adapter.
    """
    _require_non_empty_string(adapter_name, "OMI tool adapter name")
    if adapter_name not in OMI_TOOL_ADAPTER_IDENTITIES:
        raise ValueError(f"Unknown OMI tool adapter: {adapter_name}")
    return dict(OMI_ADAPTER_CONTRACTS[adapter_name])


def build_orchestrator_safety_envelope() -> dict[str, Any]:
    """Return a static safety-envelope summary for logs / audit records.

    This helper is intentionally side-effect free: it does not perform any
    analysis or I/O and does not mutate any global state.
    """
    return {
        "no_prose": True,
        "no_memory_canon_mutation": True,
        "no_apply_promotion": True,
        "no_canon_promotion": True,
        "no_real_tool_calls": True,
        "no_package_installs": True,
        "no_story_prose_generation": True,
        "candidate_presence_is_not_canon": True,
        "queue_presence_is_not_approval": True,
        "support_is_not_truth": True,
        "tool_output_is_not_canon": True,
    }


def candidate_fingerprint(
    candidate_type: str,
    label: str,
    normalized_claim: str,
) -> str:
    """Compute a deterministic fingerprint of a candidate across all adapters.

    The fingerprint is used by T010 fusion/dedupe to detect cross-adapter
    equivalence. It is stable, hash-based, and never an identifier of truth
    or approval.
    """
    _require_non_empty_string(candidate_type, "candidate_type")
    _require_non_empty_string(label, "label")
    _require_non_empty_string(normalized_claim, "normalized_claim")
    payload = (
        candidate_type.strip().lower()
        + "|"
        + label.strip().lower()
        + "|"
        + " ".join(normalized_claim.strip().lower().split())
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"omi-cand-{digest[:16]}"


def evidence_fingerprint(evidence_items: list[dict[str, Any]]) -> str:
    """Compute a deterministic fingerprint of an evidence list.

    Used by T010 fusion/dedupe to detect same-evidence candidates across
    adapters. Empty or malformed evidence raises ``ValueError``; the
    orchestrator layer rejects findings with empty evidence before this is
    ever called.
    """
    evidence_items = _require_list(evidence_items, "evidence")
    if not evidence_items:
        raise ValueError("evidence must be a non-empty array for fingerprinting")
    normalized: list[dict[str, str]] = []
    for item in evidence_items:
        if not isinstance(item, dict):
            raise ValueError("evidence items must be JSON objects")
        excerpt = str(item.get("source_excerpt", item.get("excerpt", "")) or "").strip()
        locator = str(
            item.get("source_locator", item.get("locator", "")) or ""
        ).strip()
        if not excerpt and not locator:
            raise ValueError(
                "evidence items require source_excerpt or source_locator"
            )
        normalized.append({"excerpt": excerpt.lower(), "locator": locator})
    payload = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"omi-evid-{digest[:16]}"


def is_prose_like_text(value: str) -> bool:
    """Return True if ``value`` looks like story prose / continuation / drafting.

    Conservative heuristic. Used by ``validate_normalized_finding`` to reject
    unsafe adapter outputs.
    """
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    if _DIALOGUE_QUOTE_RE.search(text):
        return True
    if _PROSE_LIKE_PREFIX_RE.match(text):
        return True
    if _PROSE_INTENT_PREFIX_RE.match(text):
        return True
    if text.endswith(".") and len(text.split()) >= 24:
        return True
    return False


def is_truth_label(value: str) -> bool:
    """Return True if ``value`` is a label that implies canon / truth / approval."""
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    return any(forbidden in lowered for forbidden in _OMI_FORBIDDEN_TRUTH_LABELS)


def normalized_finding_id(
    adapter_name: str,
    raw_finding_id: str,
    candidate_fingerprint_value: str,
) -> str:
    """Build a stable normalized-finding ID for ``adapter_name`` + raw finding.

    The ID is ``omi-find-<adapter>-<sha-prefix>`` and is used by T010 fusion.
    It is never a truth, canon, or approval identifier.
    """
    _require_non_empty_string(adapter_name, "adapter_name")
    _require_non_empty_string(raw_finding_id, "raw_finding_id")
    _require_non_empty_string(candidate_fingerprint_value, "candidate_fingerprint")
    payload = (
        adapter_name.strip().lower()
        + "|"
        + raw_finding_id.strip()
        + "|"
        + candidate_fingerprint_value.strip()
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"omi-find-{adapter_name.strip().lower()}-{digest[:16]}"


def stub_adapter_result(
    adapter_name: str,
    *,
    state: str = "unavailable",
    explanation: str = "",
) -> dict[str, Any]:
    """Build a stub adapter result for an unimplemented or unavailable tool.

    Stub results NEVER carry candidate findings. Real adapter implementations
    are out of scope for T005 (deferred to T006-T009). This helper exists so
    that ``analyze_omi_raw_idea_with_tools`` can return bounded, fail-closed
    adapter envelopes for every identity in ``OMI_TOOL_ADAPTER_IDENTITIES``.
    """
    if adapter_name not in OMI_TOOL_ADAPTER_IDENTITIES:
        raise ValueError(f"Unknown OMI tool adapter: {adapter_name}")
    if state not in OMI_ADAPTER_RESULT_STATES:
        raise ValueError(f"Unknown OMI adapter result state: {state}")
    if state == "succeeded":
        # succeeded requires real candidates; stubs can never supply them.
        raise ValueError(
            "stub_adapter_result cannot be 'succeeded'; "
            "real adapter implementations are deferred to T006-T009"
        )
    if not explanation.strip():
        explanation = (
            f"Adapter '{adapter_name}' is not implemented in T005; "
            f"returning '{state}' with no candidates. Adapters fail "
            f"closed until T006-T009 wire real implementations."
        )
    return {
        "adapter": adapter_name,
        "state": state,
        "explanation": explanation,
        "candidates": [],
    }


def validate_adapter_result(result: Any) -> dict[str, Any]:
    """Validate an adapter-result envelope shape.

    Adapter envelopes have::

        {
            "adapter": "<adapter_name>",
            "state": "<one of OMI_ADAPTER_RESULT_STATES>",
            "explanation": "<non-empty string>",
            "candidates": [<normalized-finding dict>, ...]
        }

    Only ``state == "succeeded"`` may carry non-empty ``candidates``. Other
    states must carry an empty ``candidates`` list. Failures to enforce that
    boundary raise ``ValueError``.
    """
    result = _require_dict(result, "OMI adapter result")
    adapter = _require_non_empty_string(result.get("adapter"), "adapter result adapter")
    if adapter not in OMI_TOOL_ADAPTER_IDENTITIES:
        raise ValueError(f"Unknown OMI tool adapter: {adapter}")
    state = _require_non_empty_string(result.get("state"), "adapter result state")
    if state not in OMI_ADAPTER_RESULT_STATES:
        raise ValueError(f"Unknown OMI adapter result state: {state}")
    explanation = _require_non_empty_string(
        result.get("explanation"), "adapter result explanation"
    )
    candidates = _require_list(result.get("candidates"), "adapter result candidates")
    if state != "succeeded" and candidates:
        raise ValueError(
            f"Adapter '{adapter}' returned state '{state}' with non-empty "
            f"candidates; only state='succeeded' may carry candidates. "
            f"Failing closed to prevent placeholder findings."
        )
    if state == "succeeded" and not candidates:
        # succeeded with no candidates is allowed as a degenerate shape,
        # but it is downgraded by the orchestrator to "empty" at the run
        # envelope level. We accept and pass through here.
        pass
    # Preserve orchestrator-level metadata fields (e.g. ``fallback_only``)
    # that real adapter implementations may set, but reject any other
    # unknown extra fields.
    allowed_extras = {"fallback_only"}
    extras: dict[str, Any] = {}
    for key, value in result.items():
        if key in {"adapter", "state", "explanation", "candidates"}:
            continue
        if key not in allowed_extras:
            raise ValueError(
                f"adapter result has unsupported extra field: {key}"
            )
        extras[key] = value
    return {
        "adapter": adapter,
        "state": state,
        "explanation": explanation,
        "candidates": candidates,
        **extras,
    }


def validate_normalized_finding(finding: Any) -> dict[str, Any]:
    """Validate a normalized finding against the orchestrator finding schema.

    Required fields: candidate_type, label, extracted_claim, evidence,
    source_locator, provenance, source_adapter, support_label,
    owner_decision, review_status, raw_finding_id.

    Additional safety validation:

      - candidate_type must be one of OMI_ORCHESTRATOR_FINDING_TYPES.
      - evidence must be a non-empty list of items each carrying
        source_excerpt or source_locator.
      - provenance must carry tool_source, adapter, support.
      - provenance.adapter must match source_adapter.
      - source_locator must be a non-empty string.
      - owner_decision must be a pending/review-pending state (never
        approve/approved/truth).
      - review_status must be one of OMI_FINDING_REVIEW_STATUSES and
        never imply approval/canon/promoted.
      - extracted_claim must NOT look like story prose; if it does, the
        finding is rejected as failed-closed.
      - support_label must contain "support" and NOT contain "truth" or
        "canon" or "approved" or "promoted".
    """
    finding = _require_dict(finding, "OMI normalized finding")

    missing = [
        field for field in OMI_NORMALIZED_FINDING_REQUIRED_FIELDS
        if field not in finding
    ]
    if missing:
        raise ValueError(
            f"OMI normalized finding missing required fields: {missing}"
        )

    candidate_type = _require_non_empty_string(
        finding["candidate_type"], "normalized finding candidate_type"
    )
    if candidate_type not in OMI_ORCHESTRATOR_FINDING_TYPES:
        raise ValueError(
            f"Unsupported normalized finding candidate_type: {candidate_type}"
        )

    label = _require_non_empty_string(finding["label"], "normalized finding label")
    extracted_claim = _require_non_empty_string(
        finding["extracted_claim"], "normalized finding extracted_claim"
    )

    if is_prose_like_text(extracted_claim):
        raise ValueError(
            "normalized finding extracted_claim looks like story prose; "
            "rejected as failed_closed. Adapters must produce structural "
            "claims only, not draft/continuation/rewrite/polish text."
        )

    evidence = _validate_finding_evidence(finding["evidence"])

    source_locator = _require_non_empty_string(
        finding["source_locator"], "normalized finding source_locator"
    )

    provenance = _validate_finding_provenance(finding["provenance"])
    source_adapter = _require_non_empty_string(
        finding["source_adapter"], "normalized finding source_adapter"
    )
    if source_adapter != provenance["adapter"]:
        raise ValueError(
            "normalized finding source_adapter must match provenance.adapter"
        )
    if source_adapter not in OMI_TOOL_ADAPTER_IDENTITIES:
        raise ValueError(f"Unknown normalized finding source_adapter: {source_adapter}")
    if provenance["tool_source"] != source_adapter:
        raise ValueError(
            "normalized finding provenance.tool_source must match source_adapter"
        )

    support_label = _require_non_empty_string(
        finding["support_label"], "normalized finding support_label"
    )
    lowered_support = support_label.lower()
    if "support" not in lowered_support:
        raise ValueError(
            "normalized finding support_label must include 'support' "
            "(confidence/support is support only, not truth)"
        )
    if is_truth_label(support_label):
        raise ValueError(
            "normalized finding support_label implies truth/canon/approval; "
            "must remain support only"
        )

    owner_decision = _require_dict(
        finding["owner_decision"], "normalized finding owner_decision"
    )
    decision_state = _require_non_empty_string(
        owner_decision.get("decision", ""), "owner_decision.decision"
    )
    if decision_state not in OMI_FINDING_OWNER_DECISION_STATES:
        raise ValueError(
            f"Unsupported owner_decision state: {decision_state}; "
            f"orchestrator leaves every finding in pending/review state"
        )
    if owner_decision.get("approved") is True:
        raise ValueError(
            "normalized finding owner_decision must not auto-approve; "
            "the orchestrator never approves findings"
        )

    review_status = _require_non_empty_string(
        finding["review_status"], "normalized finding review_status"
    )
    if review_status not in OMI_FINDING_REVIEW_STATUSES:
        raise ValueError(
            f"Unsupported normalized finding review_status: {review_status}"
        )

    raw_finding_id = _require_non_empty_string(
        finding["raw_finding_id"], "normalized finding raw_finding_id"
    )

    # Optional fusion fields. If present they must pass shape validation;
    # if absent, T010 will assign them. T005 only enforces the field
    # contract surface.
    fusion_fields: dict[str, Any] = {}
    for field in OMI_FUSION_FINDING_FIELDS:
        if field not in finding:
            continue
        value = finding[field]
        if field in {"duplicate_of", "related_finding_ids"}:
            if not isinstance(value, list) or not all(
                isinstance(item, str) for item in value
            ):
                raise ValueError(f"normalized finding {field} must be a list[str]")
        elif field in {"normalized_finding_id", "evidence_fingerprint",
                       "candidate_fingerprint", "conflict_group_id",
                       "uncertainty_label"}:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"normalized finding {field} must be a non-empty string")
        fusion_fields[field] = value

    normalized = {
        "candidate_type": candidate_type,
        "label": label,
        "extracted_claim": extracted_claim,
        "evidence": evidence,
        "source_locator": source_locator,
        "provenance": provenance,
        "source_adapter": source_adapter,
        "support_label": support_label,
        "owner_decision": {
            "decision": decision_state,
            "approved": False,
            **{
                k: v for k, v in owner_decision.items()
                if k not in {"decision", "approved"}
            },
        },
        "review_status": review_status,
        "raw_finding_id": raw_finding_id,
        # T005 ships the fusion-contract fields; T010 fills them. T005
        # only precomputes the deterministic candidate fingerprint so the
        # orchestrator output is T010-ready without re-implementation.
        "candidate_fingerprint": candidate_fingerprint(
            candidate_type, label, extracted_claim
        ),
    }
    if "evidence_fingerprint" not in normalized:
        normalized["evidence_fingerprint"] = evidence_fingerprint(evidence)
    if "normalized_finding_id" not in normalized:
        normalized["normalized_finding_id"] = normalized_finding_id(
            source_adapter, raw_finding_id, normalized["candidate_fingerprint"]
        )
    if "duplicate_of" not in normalized:
        normalized["duplicate_of"] = []
    if "related_finding_ids" not in normalized:
        normalized["related_finding_ids"] = []
    if "conflict_group_id" not in normalized:
        normalized["conflict_group_id"] = None
    if "uncertainty_label" not in normalized:
        normalized["uncertainty_label"] = None
    normalized.update(fusion_fields)
    return normalized


# ---------------------------------------------------------------------------
# Orchestrator entrypoint
# ---------------------------------------------------------------------------


def _validate_finding_evidence(evidence: Any) -> list[dict[str, Any]]:
    if not isinstance(evidence, list) or not evidence:
        raise ValueError(
            "OMI normalized finding evidence must be a non-empty array; "
            "evidence-backed findings require source_excerpt or "
            "source_locator on every item"
        )
    normalized: list[dict[str, Any]] = []
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("OMI evidence items must be JSON objects")
        excerpt = item.get("source_excerpt", item.get("excerpt"))
        locator = item.get("source_locator", item.get("locator"))
        if not (
            (isinstance(excerpt, str) and excerpt.strip())
            or (isinstance(locator, str) and locator.strip())
        ):
            raise ValueError(
                "OMI evidence item requires source_excerpt or source_locator"
            )
        normalized.append(dict(item))
    return normalized


def _validate_finding_provenance(provenance: Any) -> dict[str, Any]:
    provenance = _require_dict(provenance, "normalized finding provenance")
    missing = [
        field for field in OMI_FINDING_PROVENANCE_REQUIRED_FIELDS
        if field not in provenance
    ]
    if missing:
        raise ValueError(
            f"OMI normalized finding provenance missing required fields: {missing}"
        )
    tool_source = _require_non_empty_string(
        provenance["tool_source"], "normalized finding provenance.tool_source"
    )
    adapter = _require_non_empty_string(
        provenance["adapter"], "normalized finding provenance.adapter"
    )
    support = _require_non_empty_string(
        provenance["support"], "normalized finding provenance.support"
    )
    if is_truth_label(support):
        raise ValueError(
            "normalized finding provenance.support implies truth/canon; "
            "must remain support only"
        )
    if "support" not in support.lower():
        raise ValueError(
            "normalized finding provenance.support must include 'support'"
        )
    return {
        "tool_source": tool_source,
        "adapter": adapter,
        "support": support,
    }


def _coerce_requested_adapters(
    requested_adapters: Any,
) -> list[str]:
    if requested_adapters is None:
        requested = list(OMI_DEFAULT_ADAPTERS)
    elif isinstance(requested_adapters, (list, tuple)):
        requested = list(requested_adapters)
        for adapter in requested:
            if adapter not in OMI_TOOL_ADAPTER_IDENTITIES:
                raise ValueError(f"Unknown OMI tool adapter: {adapter}")
    else:
        raise ValueError(
            "requested_adapters must be None, a list, or a tuple of adapter names"
        )
    return requested


def _deterministic_fallback_findings(
    raw_idea: str,
    project_name: str,
    source_idea_id: str | None,
) -> tuple[list[dict[str, Any]], str]:
    """Run the existing deterministic marker extractor as fallback-only.

    Imported lazily here to keep the orchestrator module import-time safe
    even if project_manager ever grows heavy imports. Returns
    ``(findings, raw_extraction_explanation)``. ``findings`` is a list of
    normalized-finding dicts ready to flow into ``validate_normalized_finding``.
    """
    from backend import project_manager  # local import to avoid cycles

    extraction = project_manager.extract_omi_candidates_from_raw_idea(
        project_name,
        raw_idea,
        source_idea_id=source_idea_id,
        persist_candidates=False,
        provenance={
            "adapter": OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME,
            "tool_source": OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME,
            "support": "deterministic-fallback support strength only",
            "fallback_only": True,
            "extractor": project_manager.OMI_DETERMINISTIC_EXTRACTOR_NAME,
            "extractor_version": project_manager.OMI_DETERMINISTIC_EXTRACTOR_VERSION,
        },
    )
    raw_candidates = extraction.get("candidates", []) or []
    findings: list[dict[str, Any]] = []
    for raw in raw_candidates:
        if not isinstance(raw, dict):
            continue
        candidate_type = raw.get("candidate_type")
        label = raw.get("label") or raw.get("name") or ""
        extracted_claim = raw.get("extracted_claim", "")
        evidence = raw.get("evidence", [])
        source_locator = raw.get("source_locator", "")
        if not candidate_type or not label or not extracted_claim:
            continue
        if not isinstance(evidence, list) or not evidence:
            continue
        if not source_locator:
            source_locator = (
                f"{OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME}::fallback-marker"
            )
        adapter_name = OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME
        cand_fp = candidate_fingerprint(
            str(candidate_type), str(label), str(extracted_claim)
        )
        raw_finding_id = (
            f"{adapter_name}::"
            f"{raw.get('raw_finding_id') or str(raw.get('label') or cand_fp)}"
        )
        findings.append(
            {
                "candidate_type": str(candidate_type),
                "label": str(label),
                "extracted_claim": str(extracted_claim),
                "evidence": list(evidence),
                "source_locator": str(source_locator),
                "provenance": {
                    "tool_source": adapter_name,
                    "adapter": adapter_name,
                    "support": "deterministic-fallback support strength only",
                },
                "source_adapter": adapter_name,
                "support_label": "support strength only (deterministic fallback)",
                "owner_decision": {
                    "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
                    "approved": False,
                },
                "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
                "raw_finding_id": raw_finding_id,
                "fallback_marker": True,
                "candidate_fingerprint": cand_fp,
            }
        )
    explanation = (
        "deterministic_fallback wraps the T004 deterministic marker "
        "extractor as a fallback/safety baseline only. "
        f"Source extraction_status={extraction.get('extraction_status')!s}; "
        f"raw candidate count={len(raw_candidates)}; "
        f"normalized finding count={len(findings)}."
    )
    return findings, explanation


# ---------------------------------------------------------------------------
# Ollama / model-assisted structured extraction contract (T006)
# ---------------------------------------------------------------------------

OMI_OLLAMA_SCHEMA_VERSION = "omi_ollama_structured_extraction.v1"
OMI_OLLAMA_ADAPTER_NAME = "ollama_model"
OMI_OLLAMA_SUPPORT_LABEL = "ollama model support strength only"

# Required top-level fields in the Ollama JSON envelope. Top-level payload
# MUST be a JSON object with these keys; arrays/scalars are rejected.
OMI_OLLAMA_ENVELOPE_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "adapter",
    "status",
    "findings",
)
# Allowed status values in the Ollama envelope. ``succeeded`` indicates
# real structured output (may carry zero findings when the model found
# nothing, in which case the orchestrator downgrades to ``empty``).
# ``empty`` / ``failed_closed`` / ``error`` MUST carry zero findings.
OMI_OLLAMA_ALLOWED_STATUSES: frozenset[str] = frozenset(
    {"succeeded", "empty", "failed_closed", "error"}
)
# Required fields per Ollama finding. ``evidence`` must be a non-empty list
# of items each carrying source_excerpt or source_locator.
OMI_OLLAMA_FINDING_REQUIRED_FIELDS: tuple[str, ...] = (
    "candidate_type",
    "label",
    "extracted_claim",
    "evidence",
    "source_locator",
)
# Forbidden truth/canon/approved/promoted labels in any Ollama field.
OMI_OLLAMA_FORBIDDEN_FIELD_NAME_SUBSTRINGS: tuple[str, ...] = (
    "rewrite",
    "continue",
    "continuation",
    "outline",
    "draft",
    "polish",
    "improve",
    "improved",
    "improvement",
    "expand",
    "expanded",
    "expansion",
    "imitate",
    "imitation",
    "revise",
    "revised",
    "revision",
    "better version",
    "story passage",
    "story text",
    "scene prose",
    "chapter prose",
)


def _validate_ollama_field_name_no_prose(field_name: str) -> None:
    """Reject Ollama finding/envelope field names that request story prose.

    The model may not smuggle prose shapes through fields like ``rewrite``,
    ``continuation``, ``outline``, ``draft``, ``polish``, ``improve``,
    ``expand``, ``imitate``, ``revise``, ``better_version``, ``story_text``,
    ``scene_prose``, or ``chapter_prose``.
    """
    if not isinstance(field_name, str):
        return
    lowered = field_name.strip().lower().replace("-", " ").replace("_", " ")
    for forbidden in OMI_OLLAMA_FORBIDDEN_FIELD_NAME_SUBSTRINGS:
        if forbidden in lowered:
            raise ValueError(
                f"Ollama envelope contains forbidden prose-intent field "
                f"name {field_name!r}; adapters must not request/provide "
                f"story prose, rewriting, continuation, outline, draft, "
                f"polish, improvement, expansion, imitation, or revision."
            )


def _validate_ollama_field_names_no_prose(value: Any, *, path: str) -> None:
    """Walk an Ollama payload and reject prose-intent field names anywhere."""
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_ollama_field_name_no_prose(str(key))
            _validate_ollama_field_names_no_prose(
                child, path=f"{path}.{key}"
            )
        return
    if isinstance(value, list):
        for idx, item in enumerate(value):
            _validate_ollama_field_names_no_prose(
                item, path=f"{path}[{idx}]"
            )


def _validate_ollama_no_truth_label_in_value(
    value: Any,
    *,
    path: str,
) -> None:
    """Walk an Ollama payload and reject any truth/canon/approved labels."""
    if isinstance(value, dict):
        for k, v in value.items():
            _validate_ollama_no_truth_label_in_value(
                v, path=f"{path}.{k}"
            )
        return
    if isinstance(value, list):
        for idx, item in enumerate(value):
            _validate_ollama_no_truth_label_in_value(
                item, path=f"{path}[{idx}]"
            )
        return
    if isinstance(value, str):
        if is_truth_label(value):
            raise ValueError(
                f"Ollama envelope contains truth/canon/approved/promoted "
                f"label at {path!r}: {value!r}; Ollama output is support "
                f"only and must never be promoted to canon/approval."
            )


def _validate_ollama_finding(finding: Any) -> dict[str, Any]:
    """Validate a single Ollama finding against the strict T006 schema.

    Returns the validated finding dict. Raises ``ValueError`` on any
    invalid/unsafe output. The finding dict is normalized into the
    T005 schema by the caller; this validator only enforces envelope
    shape, evidence/source_locator requirements, no-prose, no-truth-label,
    no-prose-intent-field-name, and no-auto-approval rules.
    """
    finding = _require_dict(finding, "Ollama finding")
    _validate_ollama_field_names_no_prose(
        finding, path="ollama_finding"
    )
    # Required fields
    missing = [
        field for field in OMI_OLLAMA_FINDING_REQUIRED_FIELDS
        if field not in finding
    ]
    if missing:
        raise ValueError(
            f"Ollama finding missing required fields: {missing}; "
            f"every Ollama finding must carry candidate_type, label, "
            f"extracted_claim, evidence, and source_locator."
        )
    candidate_type = _require_non_empty_string(
        finding["candidate_type"], "Ollama finding candidate_type"
    )
    if candidate_type not in OMI_ORCHESTRATOR_FINDING_TYPES:
        raise ValueError(
            f"Ollama finding unknown candidate_type: {candidate_type!r}; "
            f"must be one of {sorted(OMI_ORCHESTRATOR_FINDING_TYPES)}"
        )
    label = _require_non_empty_string(
        finding["label"], "Ollama finding label"
    )
    extracted_claim = _require_non_empty_string(
        finding["extracted_claim"], "Ollama finding extracted_claim"
    )
    if is_prose_like_text(extracted_claim):
        raise ValueError(
            "Ollama finding extracted_claim looks like story prose / "
            "rewrite / polish / continuation / draft; OMI must analyze, "
            "not write. Rejecting as failed_closed."
        )
    evidence = _validate_finding_evidence(finding["evidence"])
    source_locator = _require_non_empty_string(
        finding["source_locator"], "Ollama finding source_locator"
    )
    # Reject any auto-approved/approved owner_decision on the finding.
    owner_decision = finding.get("owner_decision")
    if isinstance(owner_decision, dict):
        decision = owner_decision.get("decision")
        if decision in {"approve", "approved", "promote", "promoted"}:
            raise ValueError(
                "Ollama finding carries auto-approved owner_decision; "
                "Ollama output is support only and must never approve "
                "findings automatically."
            )
        if owner_decision.get("approved") is True:
            raise ValueError(
                "Ollama finding owner_decision.approved=true; adapters "
                "must not auto-approve findings."
            )
    # Walk the finding for any truth-label values.
    _validate_ollama_no_truth_label_in_value(
        finding, path="ollama_finding"
    )
    return {
        "candidate_type": candidate_type,
        "label": label,
        "extracted_claim": extracted_claim,
        "evidence": evidence,
        "source_locator": source_locator,
        "raw_finding": dict(finding),
    }


def validate_ollama_model_envelope(payload: Any) -> dict[str, Any]:
    """Validate an Ollama JSON envelope against the strict T006 schema.

    Returns a dict with shape::

        {
            "schema_version": "omi_ollama_structured_extraction.v1",
            "adapter": "ollama_model",
            "status": "<one of OMI_OLLAMA_ALLOWED_STATUSES>",
            "explanation": "<non-empty str>",
            "diagnostics": [<str>, ...],
            "findings": [<normalized finding dict>, ...],
        }

    Raises ``ValueError`` on any invalid/unsafe output (non-JSON,
    wrong schema_version, wrong adapter, prose-intent field name,
    truth-label value, prose-like extracted_claim, missing evidence /
    source_locator, auto-approved owner_decision, etc.).
    """
    if isinstance(payload, str):
        # Allow callers to pass a JSON-encoded string. The orchestrator
        # MUST NOT call any external parser; parse via stdlib json only
        # when ``parse_strings=True`` (default for fixture inputs).
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Ollama envelope must be a JSON object; could not parse "
                f"string payload as JSON: {exc}"
            ) from exc
        payload = parsed
    envelope = _require_dict(payload, "Ollama envelope")
    _validate_ollama_field_names_no_prose(
        envelope, path="ollama_envelope"
    )
    # Required top-level fields
    missing = [
        field for field in OMI_OLLAMA_ENVELOPE_REQUIRED_FIELDS
        if field not in envelope
    ]
    if missing:
        raise ValueError(
            f"Ollama envelope missing required fields: {missing}; "
            f"every envelope must carry schema_version, adapter, "
            f"status, and findings."
        )
    schema_version = _require_non_empty_string(
        envelope["schema_version"], "Ollama envelope schema_version"
    )
    if schema_version != OMI_OLLAMA_SCHEMA_VERSION:
        raise ValueError(
            f"Ollama envelope schema_version={schema_version!r} is not "
            f"supported; only {OMI_OLLAMA_SCHEMA_VERSION!r} is accepted. "
            f"Unknown or future schema versions fail closed."
        )
    adapter = _require_non_empty_string(
        envelope["adapter"], "Ollama envelope adapter"
    )
    if adapter != OMI_OLLAMA_ADAPTER_NAME:
        raise ValueError(
            f"Ollama envelope adapter={adapter!r} is not "
            f"{OMI_OLLAMA_ADAPTER_NAME!r}; the envelope must identify "
            f"its producing adapter. Unknown or mismatched adapter "
            f"identities fail closed."
        )
    status = _require_non_empty_string(
        envelope["status"], "Ollama envelope status"
    )
    if status not in OMI_OLLAMA_ALLOWED_STATUSES:
        raise ValueError(
            f"Ollama envelope status={status!r} is not allowed; must be "
            f"one of {sorted(OMI_OLLAMA_ALLOWED_STATUSES)}. Unknown "
            f"status values fail closed."
        )
    findings_value = envelope["findings"]
    if not isinstance(findings_value, list):
        raise ValueError(
            "Ollama envelope 'findings' must be a JSON array; "
            "non-array findings fail closed."
        )
    if status != "succeeded" and findings_value:
        raise ValueError(
            f"Ollama envelope carries findings in status={status!r}; "
            f"only 'succeeded' may carry findings. "
            f"Non-succeeded statuses must carry an empty findings list. "
            f"Failing closed to prevent placeholder findings."
        )
    if status == "succeeded" and not findings_value:
        # succeeded with zero findings is allowed as the model-found-
        # nothing shape; the orchestrator downgrades to 'empty'.
        pass
    explanation_value = envelope.get("explanation", "")
    if not isinstance(explanation_value, str):
        explanation_value = ""
    diagnostics_value = envelope.get("diagnostics", [])
    if not isinstance(diagnostics_value, list):
        diagnostics_value = []
    # Walk the payload for truth-label values.
    _validate_ollama_no_truth_label_in_value(
        envelope, path="ollama_envelope"
    )
    # Validate every finding (only meaningful when status='succeeded').
    normalized_findings: list[dict[str, Any]] = []
    for finding in findings_value:
        validated = _validate_ollama_finding(finding)
        raw = validated.pop("raw_finding")
        # Build the normalized finding using the existing T005 schema.
        # provenance is set deterministically to ollama_model; support
        # label is support only; owner_decision is pending; review_status
        # is candidate/review pending; raw_finding_id defaults to a
        # deterministic label-derived ID when not supplied.
        raw_finding_id = raw.get("raw_finding_id") or (
            f"{OMI_OLLAMA_ADAPTER_NAME}::"
            f"{validated['label']}::{validated['source_locator']}"
        )
        if not isinstance(raw_finding_id, str) or not raw_finding_id.strip():
            raw_finding_id = (
                f"{OMI_OLLAMA_ADAPTER_NAME}::fixture::{validated['source_locator']}"
            )
        # Optional explicit diagnostics on the envelope. We do not
        # expose these as findings; they are audit notes only.
        owner_decision_override = raw.get("owner_decision")
        owner_decision: dict[str, Any]
        if isinstance(owner_decision_override, dict):
            owner_decision = {
                "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
                "approved": False,
            }
        else:
            owner_decision = {
                "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
                "approved": False,
            }
        support_label_value = raw.get("support_label") or (
            f"{OMI_OLLAMA_SUPPORT_LABEL}"
        )
        if not isinstance(support_label_value, str) or not support_label_value.strip():
            support_label_value = OMI_OLLAMA_SUPPORT_LABEL
        if is_truth_label(support_label_value):
            raise ValueError(
                "Ollama finding support_label implies truth/canon; "
                "must remain support only."
            )
        if "support" not in support_label_value.lower():
            raise ValueError(
                "Ollama finding support_label must include 'support' "
                "(confidence/support is support only, not truth)."
            )
        confidence_value = raw.get("confidence") or raw.get("support")
        confidence_text = (
            str(confidence_value)
            if isinstance(confidence_value, str) and confidence_value.strip()
            else OMI_OLLAMA_SUPPORT_LABEL
        )
        if is_truth_label(confidence_text):
            raise ValueError(
                "Ollama finding confidence/support implies truth/canon; "
                "must remain support only."
            )
        normalized_findings.append(
            {
                "candidate_type": validated["candidate_type"],
                "label": validated["label"],
                "extracted_claim": validated["extracted_claim"],
                "evidence": validated["evidence"],
                "source_locator": validated["source_locator"],
                "provenance": {
                    "tool_source": OMI_OLLAMA_ADAPTER_NAME,
                    "adapter": OMI_OLLAMA_ADAPTER_NAME,
                    "support": OMI_OLLAMA_SUPPORT_LABEL,
                },
                "source_adapter": OMI_OLLAMA_ADAPTER_NAME,
                "support_label": support_label_value,
                "support": confidence_text,
                "owner_decision": owner_decision,
                "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
                "raw_finding_id": raw_finding_id,
                "candidate_fingerprint": candidate_fingerprint(
                    validated["candidate_type"],
                    validated["label"],
                    validated["extracted_claim"],
                ),
            }
        )
    return {
        "schema_version": schema_version,
        "adapter": adapter,
        "status": status,
        "explanation": explanation_value,
        "diagnostics": diagnostics_value,
        "findings": normalized_findings,
    }


def _build_ollama_model_fixture_runner(
    fixture: Any,
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a safe Ollama fixture-only runner.

    The returned runner is invoked by ``analyze_omi_raw_idea_with_tools``
    exactly like a real adapter runner. The runner ignores the live
    ``raw_idea`` content (this is by design; we never call Ollama), and
    returns an adapter-envelope dict that:

    - Has been validated against ``OMI_OLLAMA_SCHEMA_VERSION``.
    - Has its findings pre-normalized to the T005 normalized-finding
      schema (via ``validate_ollama_model_envelope``), so the orchestrator
      validates them via ``validate_normalized_finding``.
    - Fails closed (returns ``unavailable``-style envelope with empty
      ``candidates`` list) on any invalid fixture.

    The ``adapter_config`` argument is accepted for forward compatibility
    (e.g., future live-mode configuration) but is currently unused.
    """
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")
    cached_envelope: dict[str, Any] | None = None
    cached_error: str | None = None

    def _try_validate() -> dict[str, Any]:
        # Validate the static fixture once; failures are cached so the
        # runner never crashes the orchestrator on a bad test fixture.
        try:
            return validate_ollama_model_envelope(fixture)
        except ValueError as exc:
            raise ValueError(
                f"Ollama fixture failed strict validation: {exc}"
            ) from exc

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        nonlocal cached_envelope, cached_error
        _ = project_name  # intentionally unused for T006 fixture mode
        _ = raw_idea  # intentionally unused for T006 fixture mode
        _ = source_idea_id  # intentionally unused for T006 fixture mode
        if cached_error is not None:
            # Fixture invalid -> return failed_closed envelope with no
            # candidates. We do NOT raise from the runner; the envelope
            # shape is a valid fail-closed state.
            return {
                "adapter": OMI_OLLAMA_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": cached_error,
                "candidates": [],
            }
        if cached_envelope is None:
            try:
                cached_envelope = _try_validate()
            except ValueError as exc:
                cached_error = str(exc)
                return {
                    "adapter": OMI_OLLAMA_ADAPTER_NAME,
                    "state": "failed_closed",
                    "explanation": cached_error,
                    "candidates": [],
                }
        envelope = cached_envelope
        env_status = envelope["status"]
        # Map Ollama status -> adapter envelope state. succeeded carries
        # normalized findings; empty/failed_closed/error do not.
        if env_status == "succeeded":
            if envelope["findings"]:
                state = "succeeded"
            else:
                state = "empty"
        else:
            state = env_status
        return {
            "adapter": OMI_OLLAMA_ADAPTER_NAME,
            "state": state,
            "explanation": (
                envelope["explanation"]
                or (
                    "Ollama fixture envelope validated against "
                    f"{OMI_OLLAMA_SCHEMA_VERSION}; orchestrator never "
                    f"performs live Ollama calls."
                )
            ),
            "candidates": envelope["findings"],
        }

    return _runner


# ---------------------------------------------------------------------------
# BookNLP / spaCy local NLP fixture extraction contracts (T007)
# ---------------------------------------------------------------------------

OMI_BOOKNLP_SCHEMA_VERSION = "omi_booknlp_local_nlp_extraction.v1"
OMI_SPACY_SCHEMA_VERSION = "omi_spacy_local_nlp_extraction.v1"
OMI_LOCAL_NLP_ADAPTER_NAMES: frozenset[str] = frozenset({"booknlp", "spacy"})
OMI_LOCAL_NLP_SCHEMA_VERSION_BY_ADAPTER: dict[str, str] = {
    "booknlp": OMI_BOOKNLP_SCHEMA_VERSION,
    "spacy": OMI_SPACY_SCHEMA_VERSION,
}
OMI_LOCAL_NLP_SUPPORT_LABEL_BY_ADAPTER: dict[str, str] = {
    "booknlp": "BookNLP fixture support only",
    "spacy": "spaCy fixture support only",
}
OMI_LOCAL_NLP_ALLOWED_STATUSES: frozenset[str] = frozenset(
    {"succeeded", "empty", "failed_closed", "error"}
)
OMI_LOCAL_NLP_ENVELOPE_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "adapter",
    "status",
    "provenance",
    "findings",
)

_OMI_LOCAL_NLP_CANDIDATE_TYPE_FIELD_NAMES: tuple[str, ...] = (
    "candidate_type",
    "finding_type",
    "entity_type",
    "spacy_label",
    "booknlp_type",
    "type",
    "kind",
    "category",
)
_OMI_LOCAL_NLP_LABEL_FIELD_NAMES: tuple[str, ...] = (
    "label",
    "name",
    "text",
    "mention",
    "entity",
    "entity_text",
    "span_text",
)
_OMI_LOCAL_NLP_CLAIM_FIELD_NAMES: tuple[str, ...] = (
    "extracted_claim",
    "claim",
    "support_claim",
    "owner_authored_support_claim",
    "observation",
)
_OMI_LOCAL_NLP_EVIDENCE_EXCERPT_FIELD_NAMES: tuple[str, ...] = (
    "source_excerpt",
    "evidence_excerpt",
    "excerpt",
    "sentence",
    "sentence_text",
    "quote",
    "quote_text",
)

_OMI_FORBIDDEN_OPERATION_FIELD_NAME_SUBSTRINGS: tuple[str, ...] = (
    "memory mutation",
    "canon mutation",
    "promotion record",
    "apply promotion",
    "promote to canon",
    "write memory",
    "write canon",
    "enable apply promotion",
)
_OMI_FORBIDDEN_OPERATION_VALUE_RE = re.compile(
    r"(apply[-_\s]?promotion|promotion\s+record|promote\s+to\s+canon|"
    r"mutat(?:e|ion)\s+(?:memory|canon)|write\s+(?:memory|canon)|"
    r"enable\s+apply[-_\s]?promotion)",
    re.IGNORECASE,
)


def _first_non_empty_string(
    mapping: dict[str, Any],
    field_names: tuple[str, ...],
) -> str:
    for field_name in field_names:
        value = mapping.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalize_local_nlp_type_token(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _coerce_local_nlp_candidate_type(
    adapter_name: str,
    finding: dict[str, Any],
) -> str:
    raw_type = _first_non_empty_string(
        finding, _OMI_LOCAL_NLP_CANDIDATE_TYPE_FIELD_NAMES
    )
    if raw_type in OMI_ORCHESTRATOR_FINDING_TYPES:
        return raw_type

    token = _normalize_local_nlp_type_token(raw_type)
    if adapter_name == "spacy":
        if token in {"person", "per"}:
            return "character"
        if token in {"gpe", "loc", "location", "fac", "facility", "place"}:
            return "location"
        if token in {"org", "organization", "group"}:
            return "organization"
        if token == "event" or "event" in token:
            return "timeline_event"
        if token in {
            "object",
            "concrete_noun",
            "noun",
            "noun_chunk",
            "thing",
            "item",
            "product",
        } or "object" in token or "concrete" in token:
            return "object"
    else:
        if (
            token in {"person", "per", "character", "speaker"}
            or "person" in token
            or "character" in token
            or "speaker" in token
        ):
            return "character"
        if token in {
            "location",
            "loc",
            "gpe",
            "place",
            "setting",
            "fac",
            "facility",
        } or "location" in token:
            return "location"
        if token in {"org", "organization", "group"} or "organization" in token:
            return "organization"
        if "event" in token or "timeline" in token:
            return "timeline_event"
        if "coref" in token or "relation" in token:
            return "relationship"
        if (
            token in {"object", "thing", "item", "prop", "concrete_thing"}
            or "object" in token
            or "thing" in token
            or "concrete" in token
        ):
            return "object"
        if (
            token in {"named_entity", "entity", "mention", "entity_mention"}
            or "quote" in token
            or "evidence" in token
            or "support" in token
        ):
            return "evidence_note"

    raise ValueError(
        f"{adapter_name} finding unknown candidate/finding type {raw_type!r}; "
        f"fixture outputs must map to one of "
        f"{sorted(OMI_ORCHESTRATOR_FINDING_TYPES)}."
    )


def _validate_tool_payload_no_forbidden_operations(
    value: Any,
    *,
    path: str,
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).strip().lower().replace("-", " ").replace("_", " ")
            for forbidden in _OMI_FORBIDDEN_OPERATION_FIELD_NAME_SUBSTRINGS:
                if forbidden in key_text:
                    raise ValueError(
                        f"Tool output contains forbidden operation field "
                        f"{path}.{key}; adapters must not mutate Memory/Canon, "
                        f"create promotion records, or run/enable apply-promotion."
                    )
            _validate_tool_payload_no_forbidden_operations(
                child, path=f"{path}.{key}"
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_tool_payload_no_forbidden_operations(
                child, path=f"{path}[{idx}]"
            )
        return
    if isinstance(value, str) and _OMI_FORBIDDEN_OPERATION_VALUE_RE.search(value):
        raise ValueError(
            f"Tool output contains forbidden operation text at {path}; "
            f"adapters must not mutate Memory/Canon, create promotion records, "
            f"or run/enable apply-promotion."
        )


def _validate_local_nlp_provenance(
    provenance: Any,
    *,
    adapter_name: str,
) -> dict[str, str]:
    normalized = _validate_finding_provenance(provenance)
    if normalized["adapter"] != adapter_name:
        raise ValueError(
            f"{adapter_name} provenance.adapter must match the adapter identity"
        )
    if normalized["tool_source"] != adapter_name:
        raise ValueError(
            f"{adapter_name} provenance.tool_source must match the adapter identity"
        )
    return normalized


def _normalize_local_nlp_evidence(
    finding: dict[str, Any],
    *,
    source_locator: str,
    adapter_name: str,
) -> list[dict[str, Any]]:
    raw_evidence = finding.get("evidence")
    evidence_items: list[Any] = []
    if isinstance(raw_evidence, list):
        evidence_items = list(raw_evidence)
    elif isinstance(raw_evidence, dict):
        evidence_items = [dict(raw_evidence)]
    else:
        span_value = finding.get("span") or finding.get("token_span")
        if isinstance(span_value, dict):
            span_excerpt = _first_non_empty_string(
                span_value,
                (
                    "source_excerpt",
                    "excerpt",
                    "text",
                    "sentence",
                    "sentence_text",
                ),
            )
            span_locator = _first_non_empty_string(
                span_value,
                ("source_locator", "locator"),
            ) or source_locator
            if span_excerpt:
                evidence_items = [
                    {
                        "source_excerpt": span_excerpt,
                        "source_locator": span_locator,
                        "span": dict(span_value),
                    }
                ]
        excerpt = _first_non_empty_string(
            finding, _OMI_LOCAL_NLP_EVIDENCE_EXCERPT_FIELD_NAMES
        )
        if excerpt:
            evidence_items = [
                {
                    "source_excerpt": excerpt,
                    "source_locator": source_locator,
                }
            ]

    if not evidence_items:
        raise ValueError(
            f"{adapter_name} finding requires evidence with a source excerpt "
            f"and source locator"
        )

    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            raise ValueError(f"{adapter_name} evidence item {idx} must be an object")
        item_copy = dict(item)
        excerpt = _first_non_empty_string(
            item_copy,
            (
                "source_excerpt",
                "excerpt",
                "text",
                "sentence",
                "sentence_text",
            ),
        )
        locator = _first_non_empty_string(
            item_copy,
            ("source_locator", "locator"),
        )
        if not locator:
            locator = source_locator
        if not excerpt:
            raise ValueError(
                f"{adapter_name} evidence item {idx} requires source_excerpt"
            )
        if not locator:
            raise ValueError(
                f"{adapter_name} evidence item {idx} requires source_locator"
            )
        item_copy["source_excerpt"] = excerpt
        item_copy["source_locator"] = locator
        normalized.append(item_copy)
    return normalized


def _validate_local_nlp_owner_decision(
    owner_decision: Any,
    *,
    adapter_name: str,
) -> dict[str, Any]:
    if owner_decision is None:
        return {
            "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
            "approved": False,
        }
    if not isinstance(owner_decision, dict):
        raise ValueError(f"{adapter_name} owner_decision must be an object")
    decision = owner_decision.get("decision")
    if decision in {"approve", "approved", "promote", "promoted"}:
        raise ValueError(
            f"{adapter_name} finding carries auto-approved owner_decision; "
            f"local NLP output is support only and must never approve findings."
        )
    if owner_decision.get("approved") is True:
        raise ValueError(
            f"{adapter_name} finding owner_decision.approved=true; adapters "
            f"must not auto-approve findings."
        )
    return {
        "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
        "approved": False,
    }


def _normalize_local_nlp_support_label(
    finding: dict[str, Any],
    provenance: dict[str, str],
    *,
    adapter_name: str,
) -> str:
    support_value = (
        finding.get("support_label")
        or finding.get("confidence")
        or finding.get("support")
        or provenance.get("support")
        or OMI_LOCAL_NLP_SUPPORT_LABEL_BY_ADAPTER[adapter_name]
    )
    if isinstance(support_value, (int, float)):
        support_label = f"{adapter_name} support metadata: {support_value}"
    elif isinstance(support_value, str) and support_value.strip():
        support_label = support_value.strip()
        if "support" not in support_label.lower():
            support_label = f"{adapter_name} support metadata: {support_label}"
    else:
        support_label = OMI_LOCAL_NLP_SUPPORT_LABEL_BY_ADAPTER[adapter_name]
    if is_truth_label(support_label):
        raise ValueError(
            f"{adapter_name} support/confidence implies truth/canon/approval; "
            f"must remain support metadata only."
        )
    return support_label


def _validate_local_nlp_finding(
    finding: Any,
    *,
    adapter_name: str,
    envelope_provenance: dict[str, str],
) -> dict[str, Any]:
    finding = _require_dict(finding, f"{adapter_name} finding")
    _validate_ollama_field_names_no_prose(
        finding, path=f"{adapter_name}_finding"
    )
    _validate_tool_payload_no_forbidden_operations(
        finding, path=f"{adapter_name}_finding"
    )
    _validate_ollama_no_truth_label_in_value(
        finding, path=f"{adapter_name}_finding"
    )

    candidate_type = _coerce_local_nlp_candidate_type(adapter_name, finding)
    label = _first_non_empty_string(finding, _OMI_LOCAL_NLP_LABEL_FIELD_NAMES)
    if not label:
        raise ValueError(f"{adapter_name} finding requires label/name/text")
    extracted_claim = _first_non_empty_string(
        finding, _OMI_LOCAL_NLP_CLAIM_FIELD_NAMES
    )
    if not extracted_claim:
        raise ValueError(
            f"{adapter_name} finding requires extracted_claim or support claim"
        )
    if is_prose_like_text(extracted_claim):
        raise ValueError(
            f"{adapter_name} finding extracted_claim looks like story prose / "
            f"rewrite / polish / continuation / draft; OMI must analyze, "
            f"not write. Rejecting as failed_closed."
        )

    source_locator = _require_non_empty_string(
        finding.get("source_locator"),
        f"{adapter_name} finding source_locator",
    )
    evidence = _normalize_local_nlp_evidence(
        finding,
        source_locator=source_locator,
        adapter_name=adapter_name,
    )

    finding_provenance = finding.get("provenance", envelope_provenance)
    provenance = _validate_local_nlp_provenance(
        finding_provenance,
        adapter_name=adapter_name,
    )
    support_label = _normalize_local_nlp_support_label(
        finding,
        provenance,
        adapter_name=adapter_name,
    )
    owner_decision = _validate_local_nlp_owner_decision(
        finding.get("owner_decision"),
        adapter_name=adapter_name,
    )
    raw_finding_id = finding.get("raw_finding_id") or (
        f"{adapter_name}::{label}::{source_locator}"
    )
    if not isinstance(raw_finding_id, str) or not raw_finding_id.strip():
        raw_finding_id = f"{adapter_name}::fixture::{source_locator}"

    return {
        "candidate_type": candidate_type,
        "label": label,
        "extracted_claim": extracted_claim,
        "evidence": evidence,
        "source_locator": source_locator,
        "provenance": {
            "tool_source": adapter_name,
            "adapter": adapter_name,
            "support": support_label,
        },
        "source_adapter": adapter_name,
        "support_label": support_label,
        "owner_decision": owner_decision,
        "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
        "raw_finding_id": raw_finding_id,
        "candidate_fingerprint": candidate_fingerprint(
            candidate_type,
            label,
            extracted_claim,
        ),
    }


def validate_local_nlp_fixture_envelope(
    payload: Any,
    *,
    adapter_name: str,
) -> dict[str, Any]:
    """Validate a BookNLP/spaCy fixture envelope and normalize findings.

    This T007 contract accepts only fixture/mock/local deterministic payloads;
    it never imports or runs BookNLP/spaCy. Invalid shape, missing evidence,
    missing source locators, missing provenance, unsafe prose-like claims,
    truth/canon/approval labels, owner auto-approval, Memory/Canon mutation
    requests, promotion records, and apply-promotion requests all fail closed.
    """
    if adapter_name not in OMI_LOCAL_NLP_ADAPTER_NAMES:
        raise ValueError(f"Unsupported local NLP adapter: {adapter_name}")
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{adapter_name} envelope must be a JSON object; could not "
                f"parse string payload as JSON: {exc}"
            ) from exc
        payload = parsed

    envelope = _require_dict(payload, f"{adapter_name} envelope")
    _validate_ollama_field_names_no_prose(
        envelope, path=f"{adapter_name}_envelope"
    )
    _validate_tool_payload_no_forbidden_operations(
        envelope, path=f"{adapter_name}_envelope"
    )
    _validate_ollama_no_truth_label_in_value(
        envelope, path=f"{adapter_name}_envelope"
    )

    missing = [
        field for field in OMI_LOCAL_NLP_ENVELOPE_REQUIRED_FIELDS
        if field not in envelope
    ]
    if missing:
        raise ValueError(
            f"{adapter_name} envelope missing required fields: {missing}; "
            f"local NLP fixtures require schema_version, adapter, status, "
            f"provenance, and findings."
        )

    schema_version = _require_non_empty_string(
        envelope["schema_version"], f"{adapter_name} envelope schema_version"
    )
    expected_schema = OMI_LOCAL_NLP_SCHEMA_VERSION_BY_ADAPTER[adapter_name]
    if schema_version != expected_schema:
        raise ValueError(
            f"{adapter_name} envelope schema_version={schema_version!r} is "
            f"not supported; only {expected_schema!r} is accepted."
        )
    envelope_adapter = _require_non_empty_string(
        envelope["adapter"], f"{adapter_name} envelope adapter"
    )
    if envelope_adapter != adapter_name:
        raise ValueError(
            f"{adapter_name} envelope adapter={envelope_adapter!r} must be "
            f"{adapter_name!r}; mismatched adapter identities fail closed."
        )
    status = _require_non_empty_string(
        envelope["status"], f"{adapter_name} envelope status"
    )
    if status not in OMI_LOCAL_NLP_ALLOWED_STATUSES:
        raise ValueError(
            f"{adapter_name} envelope status={status!r} is not allowed; "
            f"must be one of {sorted(OMI_LOCAL_NLP_ALLOWED_STATUSES)}."
        )
    findings_value = envelope["findings"]
    if not isinstance(findings_value, list):
        raise ValueError(f"{adapter_name} envelope findings must be an array")
    if status != "succeeded" and findings_value:
        raise ValueError(
            f"{adapter_name} envelope carries findings in status={status!r}; "
            f"only 'succeeded' may carry findings."
        )

    envelope_provenance = _validate_local_nlp_provenance(
        envelope["provenance"],
        adapter_name=adapter_name,
    )
    normalized_findings = [
        _validate_local_nlp_finding(
            finding,
            adapter_name=adapter_name,
            envelope_provenance=envelope_provenance,
        )
        for finding in findings_value
    ]
    return {
        "schema_version": schema_version,
        "adapter": adapter_name,
        "status": status,
        "explanation": (
            envelope["explanation"]
            if isinstance(envelope.get("explanation"), str)
            else ""
        ),
        "diagnostics": (
            list(envelope["diagnostics"])
            if isinstance(envelope.get("diagnostics"), list)
            else []
        ),
        "findings": normalized_findings,
    }


def _build_local_nlp_fixture_runner(
    adapter_name: str,
    fixture: Any,
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a safe fixture-only runner for BookNLP/spaCy local NLP output."""
    if adapter_name not in OMI_LOCAL_NLP_ADAPTER_NAMES:
        raise ValueError(f"Unsupported local NLP fixture adapter: {adapter_name}")
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")
    cached_envelope: dict[str, Any] | None = None
    cached_error: str | None = None

    def _try_validate() -> dict[str, Any]:
        try:
            return validate_local_nlp_fixture_envelope(
                fixture,
                adapter_name=adapter_name,
            )
        except ValueError as exc:
            raise ValueError(
                f"{adapter_name} fixture failed strict validation: {exc}"
            ) from exc

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        nonlocal cached_envelope, cached_error
        _ = project_name
        _ = raw_idea
        _ = source_idea_id
        if cached_error is not None:
            return {
                "adapter": adapter_name,
                "state": "failed_closed",
                "explanation": cached_error,
                "candidates": [],
            }
        if cached_envelope is None:
            try:
                cached_envelope = _try_validate()
            except ValueError as exc:
                cached_error = str(exc)
                return {
                    "adapter": adapter_name,
                    "state": "failed_closed",
                    "explanation": cached_error,
                    "candidates": [],
                }
        envelope = cached_envelope
        env_status = envelope["status"]
        if env_status == "succeeded":
            state = "succeeded" if envelope["findings"] else "empty"
        else:
            state = env_status
        return {
            "adapter": adapter_name,
            "state": state,
            "explanation": (
                envelope["explanation"]
                or (
                    f"{adapter_name} fixture envelope validated against "
                    f"{OMI_LOCAL_NLP_SCHEMA_VERSION_BY_ADAPTER[adapter_name]}; "
                    f"orchestrator never performs live {adapter_name} calls."
                )
            ),
            "candidates": envelope["findings"],
        }

    return _runner


def _resolve_adapter_runner(
    adapter: str,
    *,
    adapter_runners: dict[str, Callable[..., dict[str, Any]]] | None = None,
    adapter_fixture_outputs: dict[str, Any] | None = None,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]] | None:
    """Return the fixture/mock adapter runner for ``adapter``, or ``None``.

    T005 shipped no real adapter runners. ``deterministic_fallback`` is wired
    to the deterministic marker extractor at the orchestrator-call layer, not
    here.

    T006/T007 extension-point behavior:

    - If an explicit ``adapter_runners[adapter]`` callable was supplied by
      the caller, return it. The caller is responsible for honoring the
      no-live-call safety contract (T006 callers pass mock/fixture runners
      only; the orchestrator never imports or invokes a live Ollama client).
    - If ``adapter`` is ``ollama_model``, ``booknlp``, or ``spacy`` AND
      ``adapter_fixture_outputs`` carries a matching entry, return a runner
      that produces a validated adapter envelope from that fixture. The fixture
      may be either a parsed JSON object (dict) or a JSON string; both forms go
      through the strict envelope validator and fail closed on any invalid or
      unsafe output. Fixture paths are the only paths that let these adapters
      succeed in tests.
    - Otherwise return ``None`` so the existing T005 stub/unavailable path
      runs unchanged.
    """
    if adapter_runners is not None:
        if not isinstance(adapter_runners, dict):
            raise ValueError("adapter_runners must be a dict[str, Callable]")
        if adapter in adapter_runners:
            runner = adapter_runners[adapter]
            if not callable(runner):
                raise ValueError(
                    f"adapter_runners[{adapter!r}] must be callable"
                )
            return runner
    if adapter in {"ollama_model", "booknlp", "spacy"}:
        if adapter_fixture_outputs is None:
            return None
        if not isinstance(adapter_fixture_outputs, dict):
            raise ValueError(
                "adapter_fixture_outputs must be a dict[str, Any]"
            )
        if adapter not in adapter_fixture_outputs:
            return None
        if adapter == "ollama_model":
            return _build_ollama_model_fixture_runner(
                adapter_fixture_outputs[adapter],
                adapter_config=adapter_config,
            )
        return _build_local_nlp_fixture_runner(
            adapter,
            adapter_fixture_outputs[adapter],
            adapter_config=adapter_config,
        )
    return None


def analyze_omi_raw_idea_with_tools(
    project_name: str,
    raw_idea: str,
    *,
    source_idea_id: str | None = None,
    persist_candidates: bool = False,
    requested_adapters: list[str] | tuple[str, ...] | None = None,
    allow_deterministic_fallback: bool = False,
    adapter_fixture_outputs: dict[str, Any] | None = None,
    adapter_runners: dict[str, Callable[..., dict[str, Any]]] | None = None,
    adapter_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the AI/tool-assisted OMI analysis orchestrator on ``raw_idea``.

    Parameters
    ----------
    project_name:
        Owning project; must be a single safe path component.
    raw_idea:
        Free-form raw idea text. Empty input short-circuits to ``empty``.
    source_idea_id:
        Optional OMI idea id to use as the canonical raw_idea source.
    persist_candidates:
        When True and the deterministic_fallback adapter is allowed AND
        produces findings, candidates are persisted via the existing
        ``project_manager.extract_omi_candidates_from_raw_idea`` helper
        with ``persist_candidates=True``. Other adapters never persist.
    requested_adapters:
        Optional list of adapter names to run. Defaults to the AI/tool
        adapters (deterministic_fallback is opt-in via
        ``allow_deterministic_fallback``). Unknown adapters raise ValueError.
    allow_deterministic_fallback:
        When True, ``deterministic_fallback`` is appended to the adapter
        list (after the requested AI/tool adapters) as a safety baseline.
        The corrected MVP path is AI/tool-assisted, not deterministic-only,
        so deterministic_fallback is OFF by default.
    adapter_fixture_outputs:
        Optional ``dict[str, Any]`` keyed by adapter name. T006 honors
        ``"ollama_model"`` fixtures; T007 honors ``"booknlp"`` and
        ``"spacy"`` fixtures. Strict schema validation, no-prose guard,
        no-truth-label guard, evidence/source-locator/provenance
        requirements, no Memory/Canon mutation, no promotion/apply-promotion,
        and fail-closed behavior all apply. The orchestrator never calls a
        live Ollama, BookNLP, or spaCy runtime and never reads environment
        variables to silently enable live calls.
    adapter_runners:
        Optional ``dict[str, Callable[..., dict[str, Any]]]`` keyed by
        adapter name. Test-only extension point that lets callers inject
        mock runners for any adapter. Each runner must honor the standard
        adapter-envelope contract; results go through the same validators.
        T006 callers pass mock/fixture runners only; live Ollama runs are
        not authorized at T006.
    adapter_config:
        Optional ``dict[str, Any]`` reserved for future live-adapter
        configuration. T006 ignores ``adapter_config`` for adapter runs
        (the orchestrator never enables live calls); it is accepted for
        forward compatibility only.

    Returns
    -------
    dict with keys:

        - ``analysis_status``: ``succeeded`` / ``empty`` / ``fail_closed`` /
          ``error``
        - ``explanation``: human-readable explanation (always non-empty).
        - ``source_idea_id``: str | None.
        - ``adapter_results``: list of validated adapter envelopes.
        - ``findings``: list of validated normalized findings (may be empty).
        - ``fusion_contract``: dict of fusion field names -> null (T010 fills).
        - ``persisted_candidate_ids``: list[str] (empty unless persistence ran).
        - ``safety``: static orchestrator safety envelope.

    Persistence boundary:
      Only deterministic_fallback may persist candidates, and only when
      ``allow_deterministic_fallback`` AND ``persist_candidates`` are both
      True. AI/tool adapter outputs are candidate-only evidence and never
      mutate Memory/Canon, create promotion records, call apply-promotion,
      or write canon. No real model/tool calls occur.

    Fail-closed behavior:
      Empty / unsupported / unsafe-prose input -> ``empty`` / ``fail_closed``
      with explanation and zero writes. Unknown adapter identities, malformed
      normalized findings, prose-shaped claims, truth-labeled support, or
      auto-approval all raise ``ValueError`` (treated as fatal by callers).
    """
    if not isinstance(project_name, str) or not project_name.strip():
        raise ValueError("OMI orchestrator project_name must be a non-empty string")
    project_name = project_name.strip()

    if not isinstance(raw_idea, str):
        raise ValueError("OMI orchestrator raw_idea must be a string")
    raw_idea_text = raw_idea.strip()

    if not isinstance(persist_candidates, bool):
        raise ValueError("OMI orchestrator persist_candidates must be a bool")

    requested = _coerce_requested_adapters(requested_adapters)
    if (
        allow_deterministic_fallback
        and OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME not in requested
    ):
        requested.append(OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME)

    safety = build_orchestrator_safety_envelope()

    explanation_parts: list[str] = []
    adapter_results: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    any_produced = False
    any_succeeded_real = False
    deterministic_fallback_produced = False
    persisted_candidate_ids: list[str] = []

    if not raw_idea_text:
        # Short-circuit empty raw idea -> empty result with zero writes.
        for adapter in requested:
            adapter_results.append(
                stub_adapter_result(adapter, state="skipped",
                                    explanation="empty raw_idea; adapter skipped")
            )
        return {
            "analysis_status": "empty",
            "explanation": (
                "No raw idea text was provided; the OMI analysis orchestrator "
                "returned an empty result with no adapter runs, no findings, "
                "and no persisted candidates."
            ),
            "source_idea_id": source_idea_id,
            "adapter_results": adapter_results,
            "findings": [],
            "fusion_contract": {field: None for field in OMI_FUSION_FINDING_FIELDS},
            "persisted_candidate_ids": [],
            "safety": safety,
        }

    if is_prose_like_text(raw_idea_text):
        # Raw idea itself looks like prose / continuation / drafting input.
        # Refuse before running anything.
        for adapter in requested:
            adapter_results.append(
                stub_adapter_result(
                    adapter,
                    state="failed_closed",
                    explanation=(
                        "Raw idea text looks like story prose / continuation; "
                        "OMI must analyze, not write. Adapter execution "
                        "refused; no candidates were extracted or persisted."
                    ),
                )
            )
        return {
            "analysis_status": "fail_closed",
            "explanation": (
                "Raw idea text resembles story prose / continuation; the OMI "
                "orchestrator refused to run analysis. OMI is analysis-only and "
                "never writes, continues, drafts, expands, polishes, imitates, "
                "or revises story prose."
            ),
            "source_idea_id": source_idea_id,
            "adapter_results": adapter_results,
            "findings": [],
            "fusion_contract": {field: None for field in OMI_FUSION_FINDING_FIELDS},
            "persisted_candidate_ids": [],
            "safety": safety,
        }

    # Run requested adapters. Real AI/tool adapters are stubbed at T005;
    # deterministic_fallback (if allowed) is wired to the marker extractor.
    for adapter in requested:
        if adapter == OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME:
            explanation_parts.append(
                f"adapter={adapter} notes={OMI_DETERMINISTIC_FALLBACK_EXPLANATION}"
            )
            fallback_findings, fallback_explanation = (
                _deterministic_fallback_findings(
                    raw_idea_text, project_name, source_idea_id
                )
            )
            explanation_parts.append(
                f"deterministic_fallback: {fallback_explanation}"
            )
            envelope = {
                "adapter": adapter,
                "state": "succeeded" if fallback_findings else "empty",
                "explanation": fallback_explanation,
                "candidates": fallback_findings,
                "fallback_only": True,
            }
            try:
                envelope = validate_adapter_result(envelope)
            except ValueError as exc:
                envelope = {
                    "adapter": adapter,
                    "state": "failed_closed",
                    "explanation": (
                        f"deterministic_fallback envelope failed contract "
                        f"validation: {exc}"
                    ),
                    "candidates": [],
                    "fallback_only": True,
                }
            adapter_results.append(envelope)
            if envelope["state"] == "succeeded" and envelope["candidates"]:
                deterministic_fallback_produced = True
                any_produced = True
                for finding in envelope["candidates"]:
                    findings.append(validate_normalized_finding(finding))
            continue

        # All other adapters are stubbed by default. Real implementations
        # are deferred to T006 (Ollama/local model), T007 (spaCy/BookNLP),
        # T008 (Story Check), T009 (NCP/Subtxt/dramatica-flow).
        runner = _resolve_adapter_runner(
            adapter,
            adapter_runners=adapter_runners,
            adapter_fixture_outputs=adapter_fixture_outputs,
            adapter_config=adapter_config,
        )
        if runner is None:
            # No fixture/runner supplied -> adapters remain unavailable.
            if adapter == "ollama_model":
                unavailable_explanation = (
                    f"Adapter '{adapter}' is available through the "
                    f"{OMI_OLLAMA_SCHEMA_VERSION} fixture contract only; "
                    f"no fixture was supplied via "
                    f"``adapter_fixture_outputs``. The orchestrator does "
                    f"not perform live Ollama calls and does not read "
                    f"environment variables to enable them. Returning "
                    f"'unavailable' with no candidates."
                )
            elif adapter in {"booknlp", "spacy"}:
                runtime_name = "BookNLP" if adapter == "booknlp" else "spaCy"
                unavailable_explanation = (
                    f"Adapter '{adapter}' is available through the T007 "
                    f"fixture/mock local NLP contract only; no fixture was "
                    f"supplied via ``adapter_fixture_outputs``. The "
                    f"orchestrator does not perform live {runtime_name} calls "
                    f"and does not import or install {runtime_name}. "
                    f"Returning 'unavailable' with no candidates."
                )
            else:
                unavailable_explanation = (
                    f"Adapter '{adapter}' is not implemented at T006; "
                    f"real implementation deferred to "
                    f"{'T007' if adapter in {'booknlp', 'spacy'} else ''}"
                    f"{'T008' if adapter == 'story_check' else ''}"
                    f"{'T009' if adapter in {'ncp', 'subtxt', 'dramatica_flow'} else ''}"
                    f". Returning 'unavailable' with no candidates."
                )
            envelope = stub_adapter_result(
                adapter,
                state="unavailable",
                explanation=unavailable_explanation,
            )
            adapter_results.append(envelope)
            continue

        # If a real runner is wired in a future child, it would be called
        # here. Today this branch is unreachable; kept for shape.
        result = runner(
            project_name=project_name,
            raw_idea=raw_idea_text,
            source_idea_id=source_idea_id,
        )
        envelope = validate_adapter_result(result)
        adapter_results.append(envelope)
        if envelope["state"] == "succeeded" and envelope["candidates"]:
            any_succeeded_real = True
            any_produced = True
            for finding in envelope["candidates"]:
                findings.append(validate_normalized_finding(finding))

    # Persistence: only deterministic_fallback may persist, only when
    # explicitly enabled, and only if it produced findings.
    if (
        allow_deterministic_fallback
        and persist_candidates
        and deterministic_fallback_produced
    ):
        # Re-run the deterministic extractor with persist_candidates=True;
        # this is the canonical T004 path. We do NOT persist fused AI/tool
        # adapter findings at T005; that is deferred to T011.
        from backend import project_manager  # local import

        extraction = project_manager.extract_omi_candidates_from_raw_idea(
            project_name,
            raw_idea_text,
            source_idea_id=source_idea_id,
            persist_candidates=True,
            provenance={
                "adapter": OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME,
                "tool_source": OMI_DETERMINISTIC_FALLBACK_ADAPTER_NAME,
                "support": "deterministic-fallback support strength only",
                "fallback_only": True,
                "orchestrator": "analyze_omi_raw_idea_with_tools",
                "extractor": project_manager.OMI_DETERMINISTIC_EXTRACTOR_NAME,
                "extractor_version": project_manager.OMI_DETERMINISTIC_EXTRACTOR_VERSION,
            },
        )
        persisted_candidate_ids = list(
            extraction.get("persisted_candidate_ids", []) or []
        )
        explanation_parts.append(
            f"deterministic_fallback persistence: "
            f"persisted_candidate_ids={persisted_candidate_ids}"
        )

    if not any_produced:
        # All adapters returned empty/skipped/unavailable/failed_closed/error
        # with no findings. The orchestrator fail-closes without writing.
        analysis_status = "fail_closed"
        explanation = (
            "All OMI tool adapters returned empty/skipped/unavailable/"
            "failed_closed/error with no produced findings. The orchestrator "
            "did not write any candidates, did not mutate Memory/Canon, did "
            "not call apply-promotion, and did not generate story prose. "
            "Real AI/tool adapter implementations are deferred to T006-T009; "
            + (
                "deterministic_fallback also returned no findings."
                if not allow_deterministic_fallback
                else "deterministic_fallback returned no findings either."
            )
            + " Details: " + " | ".join(explanation_parts)
        )
    else:
        analysis_status = "succeeded"
        explanation = (
            "OMI analysis orchestrator ran the requested adapters and "
            "produced evidence-backed candidate findings. Findings are "
            "candidate-only and must be reviewed by the owner before any "
            "Memory/Canon mutation or apply-promotion. Confidence/support is "
            "support only, not truth. Details: " + " | ".join(explanation_parts)
        )

    return {
        "analysis_status": analysis_status,
        "explanation": explanation,
        "source_idea_id": source_idea_id,
        "adapter_results": adapter_results,
        "findings": findings,
        "fusion_contract": {field: None for field in OMI_FUSION_FINDING_FIELDS},
        "persisted_candidate_ids": persisted_candidate_ids,
        "safety": safety,
    }
