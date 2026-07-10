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
    live runtimes. T014C adds a live spaCy adapter behind
    ``OMI_LIVE_TOOLS_ENABLED`` + ``OMI_LIVE_SPACY_ENABLED`` env flags that
    imports spaCy lazily inside the live runner path. T017B adds a live
    BookNLP adapter behind ``OMI_LIVE_TOOLS_ENABLED`` +
    ``OMI_LIVE_BOOKNLP_ENABLED`` env flags that imports
    ``booknlp.booknlp.BookNLP`` lazily, writes the owner raw idea to a
    temporary file, runs BookNLP against a temporary output directory,
    and converts the parsed ``.entities`` / ``.quotes`` / ``.tokens``
    rows into the existing T007
    ``omi_booknlp_local_nlp_extraction.v1`` envelope shape. The live
    BookNLP adapter does NOT persist raw BookNLP output, mutate
    Memory/Canon, create promotion records, run apply-promotion, or
    generate story prose. T017C must later perform manual real BookNLP
    processing on owner-authored text to prove the live BookNLP MVP
    path.
  - Wires ``story_check`` through a fixture-only diagnostic handoff contract
    that normalizes evidence-backed structural diagnostics/questions into
    candidate-review support without importing or running Story Check.
    T016C adds a live Story Check adapter behind
    ``OMI_LIVE_TOOLS_ENABLED`` + ``OMI_LIVE_STORY_CHECK_ENABLED`` env flags
    that lazily calls ``backend.analysis_engine.run_story_check`` and
    converts the legacy response into the existing T008 fixture
    envelope shape before validation/normalization.
  - Wires ``ncp``, ``subtxt``, and ``dramatica_flow`` through fixture-only
    diagnostic/context handoff contracts that normalize evidence-backed
    support into candidate-review material without importing or running any
    live NCP, Subtxt, or dramatica-flow runtime.
  - Stubs every adapter without a fixture/runner as fail-closed: unavailable
    adapters return ``unavailable`` / ``skipped`` / ``failed_closed`` with an
    explanation and never fabricate candidates.
  - Enforces a no-prose guard against adapter outputs: any prose-like,
    continuation-like, rewrite-like, or draft-like free-text output that could
    be confused with story prose is rejected as ``failed_closed`` with no
    persisted candidates. The prose guard is NOT applied to owner-authored
    raw idea input; owner text is treated as untrusted data to analyze,
    not as executable instructions, and may legitimately look like prose.
  - Defines and implements the T010 fixture-only fusion/dedupe/conflict/
    uncertainty pass over normalized findings. The pass groups equivalent
    candidates, marks duplicates, assigns deterministic conflict groups, and
    labels uncertainty without deleting evidence, deciding truth, persisting
    candidates, or mutating Memory/Canon.

Boundaries (non-negotiable):

  - No Ollama, Story Check, BookNLP, NCP, Subtxt, or dramatica-flow
    live runtime calls. This module does not import or invoke any of them
    at module import time. Live spaCy (T014C) is available only behind
    explicit runtime flags (OMI_LIVE_TOOLS_ENABLED, OMI_LIVE_SPACY_ENABLED)
    and imports spaCy lazily inside the live runner path. Live Ollama
    (T015C) is available only behind explicit runtime flags
    (OMI_LIVE_TOOLS_ENABLED, OMI_LIVE_OLLAMA_ENABLED) and uses
    ``urllib.request`` lazily inside the live runner path. Live Story
    Check (T016C) is available only behind explicit runtime flags
    (OMI_LIVE_TOOLS_ENABLED, OMI_LIVE_STORY_CHECK_ENABLED) and imports
    ``backend.analysis_engine.run_story_check`` lazily inside the live
    runner path. Live BookNLP (T017B) is available only behind explicit
    runtime flags (OMI_LIVE_TOOLS_ENABLED, OMI_LIVE_BOOKNLP_ENABLED) and
    imports ``booknlp.booknlp.BookNLP`` lazily inside the live runner
    path. No automatic promotion, Memory/Canon mutation,
    apply-promotion, or candidate approval.
  - No Memory/Canon mutation.
  - No promotion records, no apply-promotion, no canon promotion.
  - No story prose generation, rewriting, continuation, drafting, polishing,
    improvement, expansion, or imitation.
  - No package installs, no new external dependencies.
  - No filesystem writes beyond existing project_manager helpers when the
    caller opts into candidate-only OMI persistence.

All helpers are pure (standard library only, deterministic, no side effects
beyond what ``project_manager`` performs through the existing OMI
candidate-first storage path when ``persist_candidates=True`` and source
context is sufficient.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping

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
            "suggestions, no story text, no Memory/Canon mutation, and no "
            "promotion/apply-promotion operations. Fixture/mock diagnostic "
            "handoff only in T008; live Story Check remains unavailable."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "structural_diagnostic",
            "storyform_context",
            "throughline_context",
            "plot_thread",
            "relationship",
            "conflict_diagnostic",
            "diagnostic_question",
            "continuity_warning",
            "open_question",
            "ambiguity",
            "world_rule",
            "evidence_note",
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
            "fixture-only structural/context handoff support; project/story, "
            "storyform, scene/moment, throughline, authorial-intent, "
            "relationship, open-question/ambiguity, and source-mapping "
            "support only; NOT a truth export; fails closed on missing fixture "
            "or invalid/unsafe output. No live NCP runtime calls in T009."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "story_fact",
            "storyform_context",
            "throughline_context",
            "relationship",
            "open_question",
            "ambiguity",
            "diagnostic_question",
            "evidence_note",
        ),
    },
    "subtxt": {
        "behavior": (
            "fixture-only diagnostic/rubric handoff support; structural, "
            "conflict, throughline, story-point/context, source-of-conflict, "
            "subject-vs-conflict, uncertainty/insufficient-evidence, and "
            "owner-review diagnostic questions only; NOT automatic Dramatica "
            "truth; fails closed on missing fixture or invalid/unsafe output. "
            "No live Subtxt runtime calls in T009."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "structural_diagnostic",
            "conflict_diagnostic",
            "throughline_context",
            "storyform_context",
            "open_question",
            "ambiguity",
            "diagnostic_question",
            "evidence_note",
        ),
    },
    "dramatica_flow": {
        "behavior": (
            "fixture-only analysis-pattern handoff support for causal chains, "
            "promise/payoff and setup/payoff support, foreshadowing/mystery/"
            "question support, conflict threads, emotional arcs, relationship "
            "networks, timeline/thread activity, information boundaries, and "
            "uncertainty/conflict-group diagnostics; generation/revision/"
            "continuation remain disabled; no outlines or story text. No live "
            "dramatica-flow runtime calls in T009."
        ),
        "produces_candidates": True,
        "supports_finding_types": (
            "plot_thread",
            "story_fact",
            "open_question",
            "diagnostic_question",
            "continuity_warning",
            "conflict_diagnostic",
            "relationship",
            "timeline_event",
            "evidence_note",
            "ambiguity",
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
        "structural_diagnostic",
        "throughline_context",
        "conflict_diagnostic",
        "ambiguity",
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
    normalized.sort(key=lambda item: (item["excerpt"], item["locator"]))
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


def validate_owner_raw_idea_input(raw_idea: Any) -> str:
    """Validate owner-authored raw idea input for the OMI orchestrator.

    The owner-authored raw idea text is the source material that the OMI
    orchestrator analyzes. It may legitimately look like prose — owners
    often capture scenes, beats, and dialogue fragments as raw planning
    notes. The orchestrator therefore accepts prose-shaped owner input
    as analyzable data and treats it as untrusted text, not as executable
    instructions.

    This validator enforces the type/baseline checks that should still
    apply to owner input:

      - ``raw_idea`` must be a string. Non-string input raises
        ``ValueError`` (this matches the existing pre-existing
        ``OMI orchestrator raw_idea must be a string`` behavior).
      - Empty/whitespace-only input is NOT rejected here. The caller
        (the orchestrator entrypoint) short-circuits empty raw idea
        text to ``analysis_status == "empty"`` and never invokes
        any adapter.

    It does NOT call ``is_prose_like_text`` on the content. The prose guard
    remains strict only on AI/tool/model output (``extracted_claim`` and
    envelope values) where the safety boundary is the strict JSON/schema
    validator (``validate_ollama_model_envelope`` and the equivalent
    per-adapter envelope validators). Owner prose-shaped input flows
    through the orchestrator and is sent to the model as a user message
    so the model can analyze the text instead of being asked to write it.

    Returns the stripped string. Raises ``ValueError`` on non-string input.
    """
    if not isinstance(raw_idea, str):
        raise ValueError("OMI orchestrator raw_idea must be a string")
    return raw_idea.strip()


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


_OMI_FUSION_CLAIM_STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "and",
        "appear",
        "appears",
        "as",
        "candidate",
        "candidates",
        "context",
        "diagnostic",
        "entity",
        "evidence",
        "finding",
        "for",
        "flagged",
        "identified",
        "in",
        "is",
        "mention",
        "mentions",
        "of",
        "only",
        "or",
        "review",
        "source",
        "strength",
        "support",
        "supported",
        "supporting",
        "supports",
        "the",
        "to",
    }
)

_OMI_FUSION_TOKEN_SYNONYMS: dict[str, str] = {
    "event": "timeline_event",
    "events": "timeline_event",
    "group": "organization",
    "groups": "organization",
    "item": "object",
    "items": "object",
    "loc": "location",
    "org": "organization",
    "per": "character",
    "person": "character",
    "people": "character",
    "place": "location",
    "places": "location",
    "thing": "object",
    "things": "object",
}


def _fusion_zero_summary() -> dict[str, Any]:
    return {
        "total_input_findings": 0,
        "total_output_findings": 0,
        "duplicate_group_count": 0,
        "duplicate_finding_count": 0,
        "conflict_group_count": 0,
        "uncertain_finding_count": 0,
        "adapters_contributing_findings": [],
    }


def _fusion_tokens(value: Any) -> list[str]:
    text = str(value or "").strip().lower()
    if not text:
        return []
    return re.sub(r"[^a-z0-9]+", " ", text).split()


def _normalize_fusion_label(value: Any) -> str:
    return "".join(_fusion_tokens(value))


def _normalize_fusion_candidate_type(value: Any) -> str:
    return str(value or "").strip().lower()


def _fusion_identity_key(finding: dict[str, Any]) -> tuple[str, str]:
    return (
        _normalize_fusion_candidate_type(finding.get("candidate_type")),
        _normalize_fusion_label(finding.get("label")),
    )


def _fusion_claim_signature(finding: dict[str, Any]) -> str:
    """Return a deterministic support-claim signature for grouping.

    This is intentionally shallow: it only normalizes punctuation/case,
    removes adapter boilerplate and the label tokens, and folds a tiny set of
    type synonyms. It is not semantic similarity and never resolves truth.
    """
    label_tokens = set(_fusion_tokens(finding.get("label")))
    kept: list[str] = []
    for token in _fusion_tokens(finding.get("extracted_claim")):
        if token in label_tokens or token in _OMI_FUSION_CLAIM_STOPWORDS:
            continue
        kept.append(_OMI_FUSION_TOKEN_SYNONYMS.get(token, token))
    if not kept:
        identity = _fusion_identity_key(finding)
        return "|".join(part for part in identity if part) or "support"
    return " ".join(kept)


def _fusion_candidate_fingerprint(finding: dict[str, Any]) -> str:
    return candidate_fingerprint(
        str(finding["candidate_type"]),
        str(finding["label"]),
        _fusion_claim_signature(finding),
    )


def _fusion_conflict_group_id(
    identity_key: tuple[str, str],
    claim_signatures: list[str],
) -> str:
    payload = json.dumps(
        {
            "candidate_type": identity_key[0],
            "label": identity_key[1],
            "claim_signatures": sorted(set(claim_signatures)),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"omi-conflict-{digest[:16]}"


def _fusion_uncertainty_label_for_finding(
    finding: dict[str, Any],
) -> str | None:
    candidate_type = str(finding.get("candidate_type", "")).strip().lower()
    support_values = [
        finding.get("support_label"),
        finding.get("support"),
        finding.get("confidence"),
        finding.get("extracted_claim"),
        finding.get("label"),
    ]
    provenance = finding.get("provenance")
    if isinstance(provenance, dict):
        support_values.append(provenance.get("support"))
    text = " ".join(str(value or "") for value in support_values).lower()
    claim = str(finding.get("extracted_claim", "")).strip()

    if "conflict" in text or "contradiction" in text or "contradict" in text:
        return "conflict_support"
    if (
        "insufficient" in text
        or "weak support" in text
        or "weak evidence" in text
        or "limited evidence" in text
        or "not enough evidence" in text
    ):
        return "insufficient_evidence_support"
    if "low support" in text or "low confidence" in text:
        return "low_support"
    if (
        candidate_type == "diagnostic_question"
        or claim.endswith("?")
        or "diagnostic question" in text
    ):
        return "diagnostic_question_support"
    if candidate_type == "open_question" or "open question" in text:
        return "open_question_support"
    if (
        candidate_type == "ambiguity"
        or "ambiguous" in text
        or "ambiguity" in text
        or "unresolved" in text
    ):
        return "ambiguous_source_support"
    if (
        "possible" in text
        or "context-only" in text
        or "context only" in text
    ):
        return "possible_context_only_support"
    return None


def fuse_normalized_findings(
    findings: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Annotate normalized findings with deterministic fusion metadata.

    The pass preserves every input finding. It never decides truth, never
    deletes evidence, and never mutates/persists candidates. Duplicate and
    conflict IDs are derived only from normalized finding fields, so adapter
    ordering cannot change grouping metadata.
    """
    findings = _require_list(findings, "normalized findings")
    if not findings:
        return [], _fusion_zero_summary()

    fused: list[dict[str, Any]] = []
    duplicate_groups: dict[tuple[tuple[str, str], str], list[str]] = {}
    identity_groups: dict[tuple[str, str], list[str]] = {}
    signature_by_id: dict[str, str] = {}
    by_id: dict[str, dict[str, Any]] = {}

    for original in findings:
        finding = _require_dict(original, "normalized finding")
        item = dict(finding)
        item["candidate_fingerprint"] = _fusion_candidate_fingerprint(item)
        item["evidence_fingerprint"] = evidence_fingerprint(item["evidence"])
        item["normalized_finding_id"] = normalized_finding_id(
            str(item["source_adapter"]),
            str(item["raw_finding_id"]),
            item["candidate_fingerprint"],
        )
        item["duplicate_of"] = list(item.get("duplicate_of") or [])
        item["related_finding_ids"] = list(item.get("related_finding_ids") or [])
        item["conflict_group_id"] = None
        item["uncertainty_label"] = _fusion_uncertainty_label_for_finding(item)

        finding_id = item["normalized_finding_id"]
        identity_key = _fusion_identity_key(item)
        claim_signature = _fusion_claim_signature(item)
        duplicate_key = (identity_key, claim_signature)
        duplicate_groups.setdefault(duplicate_key, []).append(finding_id)
        identity_groups.setdefault(identity_key, []).append(finding_id)
        signature_by_id[finding_id] = claim_signature
        by_id[finding_id] = item
        fused.append(item)

    duplicate_group_count = 0
    duplicate_finding_count = 0
    for group_ids in duplicate_groups.values():
        if len(group_ids) < 2:
            continue
        duplicate_group_count += 1
        ordered_ids = sorted(group_ids)
        canonical_id = ordered_ids[0]
        duplicate_finding_count += len(ordered_ids) - 1
        for finding_id in ordered_ids:
            related = set(by_id[finding_id].get("related_finding_ids") or [])
            related.update(other_id for other_id in ordered_ids if other_id != finding_id)
            by_id[finding_id]["related_finding_ids"] = sorted(related)
            if finding_id != canonical_id:
                duplicate_of = set(by_id[finding_id].get("duplicate_of") or [])
                duplicate_of.add(canonical_id)
                by_id[finding_id]["duplicate_of"] = sorted(duplicate_of)

    conflict_group_ids: set[str] = set()
    for identity_key, group_ids in identity_groups.items():
        claim_signatures = sorted({signature_by_id[finding_id] for finding_id in group_ids})
        if len(claim_signatures) < 2:
            continue
        conflict_id = _fusion_conflict_group_id(identity_key, claim_signatures)
        conflict_group_ids.add(conflict_id)
        ordered_ids = sorted(group_ids)
        for finding_id in ordered_ids:
            related = set(by_id[finding_id].get("related_finding_ids") or [])
            related.update(other_id for other_id in ordered_ids if other_id != finding_id)
            by_id[finding_id]["related_finding_ids"] = sorted(related)
            by_id[finding_id]["conflict_group_id"] = conflict_id
            by_id[finding_id]["uncertainty_label"] = "conflict_support"

    for item in fused:
        item["duplicate_of"] = sorted(set(item.get("duplicate_of") or []))
        item["related_finding_ids"] = sorted(set(item.get("related_finding_ids") or []))

    summary = {
        "total_input_findings": len(findings),
        "total_output_findings": len(fused),
        "duplicate_group_count": duplicate_group_count,
        "duplicate_finding_count": duplicate_finding_count,
        "conflict_group_count": len(conflict_group_ids),
        "uncertain_finding_count": sum(
            1 for item in fused if item.get("uncertainty_label")
        ),
        "adapters_contributing_findings": sorted(
            {
                str(item.get("source_adapter"))
                for item in fused
                if item.get("source_adapter")
            }
        ),
    }
    return fused, summary


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
        elif field in {"conflict_group_id", "uncertainty_label"} and value is None:
            fusion_fields[field] = value
            continue
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
    for optional_metadata_field in (
        "support",
        "confidence",
        "support_score",
        "support_metadata",
    ):
        if optional_metadata_field not in finding:
            continue
        optional_value = finding[optional_metadata_field]
        if isinstance(optional_value, str) and is_truth_label(optional_value):
            raise ValueError(
                f"normalized finding {optional_metadata_field} implies "
                "truth/canon/approval; must remain support only"
            )
        normalized[optional_metadata_field] = optional_value
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
                "confidence": confidence_text,
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
        "confidence": finding.get("confidence", support_label),
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


# ---------------------------------------------------------------------------
# Story Check diagnostic-only fixture handoff contract (T008)
# ---------------------------------------------------------------------------

OMI_STORY_CHECK_SCHEMA_VERSION = "omi_story_check_diagnostic_handoff.v1"
OMI_STORY_CHECK_ADAPTER_NAME = "story_check"
OMI_STORY_CHECK_SUPPORT_LABEL = "Story Check diagnostic support only"
OMI_STORY_CHECK_ALLOWED_STATUSES: frozenset[str] = frozenset(
    {"succeeded", "empty", "failed_closed", "error"}
)
OMI_STORY_CHECK_ENVELOPE_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "adapter",
    "status",
    "provenance",
    "findings",
)

_OMI_STORY_CHECK_TYPE_FIELD_NAMES: tuple[str, ...] = (
    "candidate_type",
    "finding_type",
    "diagnostic_type",
    "type",
    "kind",
    "category",
)
_OMI_STORY_CHECK_LABEL_FIELD_NAMES: tuple[str, ...] = (
    "label",
    "name",
    "title",
    "question_label",
)
_OMI_STORY_CHECK_CLAIM_FIELD_NAMES: tuple[str, ...] = (
    "diagnostic_claim",
    "extracted_claim",
    "claim",
    "support_claim",
    "observation",
    "diagnostic",
    "question",
    "diagnostic_question",
)
_OMI_STORY_CHECK_EVIDENCE_EXCERPT_FIELD_NAMES: tuple[str, ...] = (
    "source_excerpt",
    "evidence_excerpt",
    "excerpt",
    "source_text",
    "owner_authored_excerpt",
    "quote",
    "quote_text",
)
_OMI_STORY_CHECK_EVIDENCE_VALUE_KEYS: frozenset[str] = frozenset(
    {
        "source_excerpt",
        "evidence_excerpt",
        "excerpt",
        "source_text",
        "owner_authored_excerpt",
        "quote",
        "quote_text",
        "sentence",
        "sentence_text",
        "source_locator",
        "locator",
    }
)
_OMI_STORY_CHECK_FORBIDDEN_OPERATION_FIELD_NAME_SUBSTRINGS: tuple[str, ...] = (
    "operation",
    "action",
    "command",
    "persist candidate",
    "persist candidates",
    "candidate persistence",
    "persisted candidate",
    "save candidate",
    "operation request",
    "tool operation",
    "write request",
    "memory mutation",
    "canon mutation",
    "promotion record",
    "apply promotion",
    "promote to canon",
)
_OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE = re.compile(
    r"(persist(?:ed)?\s+candidates?|save\s+candidates?|"
    r"candidate\s+persistence|apply[-_\s]?promotion|promotion\s+record|"
    r"promote\s+to\s+canon|mutat(?:e|ion)\s+(?:memory|canon)|"
    r"write\s+(?:candidate|memory|canon)|"
    r"perform(?:ing)?\s+(?:an\s+)?operation)",
    re.IGNORECASE,
)
_OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE = re.compile(
    r"\b("
    r"rewrite|rewritten|continue|continuation|expand|expanded|polish|"
    r"polished|outline|draft|revise|revised|write\s+(?:the\s+)?"
    r"(?:story|scene|chapter|prose)|generate\s+(?:a\s+)?"
    r"(?:story|scene|chapter|outline|draft|prose)|what\s+happens\s+next|"
    r"what\s+should\s+happen\s+next|next\s+scene\s+should|"
    r"next\s+chapter\s+should"
    r")\b",
    re.IGNORECASE,
)
_OMI_STORY_CHECK_FINAL_TRUTH_LABEL_RE = re.compile(
    r"\b(final|finalized|finalised|definitive|accepted|locked|"
    r"canon|canonical|truth|approved|promoted|confirmed_fact)\b",
    re.IGNORECASE,
)


def _coerce_story_check_candidate_type(finding: dict[str, Any]) -> str:
    raw_type = _first_non_empty_string(
        finding, _OMI_STORY_CHECK_TYPE_FIELD_NAMES
    )
    if raw_type in OMI_ORCHESTRATOR_FINDING_TYPES:
        return raw_type

    token = _normalize_local_nlp_type_token(raw_type)
    if token in {
        "structural_diagnostic",
        "structural_observation",
        "structure",
        "structure_diagnostic",
        "diagnostic",
        "diagnostic_observation",
    }:
        return "structural_diagnostic"
    if token in {
        "storyform",
        "storyform_context",
        "storyform_support",
        "context_support",
        "storyform_context_support",
    }:
        return "storyform_context"
    if token in {
        "throughline",
        "throughline_context",
        "throughline_support",
        "throughline_context_support",
    }:
        return "throughline_context"
    if token in {
        "conflict",
        "conflict_diagnostic",
        "uncertainty",
        "uncertainty_diagnostic",
    }:
        return "conflict_diagnostic"
    if token in {
        "question",
        "diagnostic_question",
        "review_question",
        "owner_question",
    }:
        return "diagnostic_question"
    if token in {"open_question", "ambiguity", "ambiguous_support"}:
        return "open_question"
    if token in {"plot", "plot_thread", "plot_thread_diagnostic", "thread"}:
        return "plot_thread"
    if token in {
        "relationship",
        "relationship_diagnostic",
        "relationship_support",
    }:
        return "relationship"
    if token in {"warning", "continuity_warning", "continuity"}:
        return "continuity_warning"
    if token in {"world_rule", "rule"}:
        return "world_rule"
    if token in {"candidate_support", "evidence_support", "evidence_note"}:
        return "evidence_note"

    raise ValueError(
        f"Story Check finding unknown candidate/finding type {raw_type!r}; "
        f"fixture outputs must map to one of "
        f"{sorted(OMI_ORCHESTRATOR_FINDING_TYPES)}."
    )


def _story_check_string_has_truth_final_label(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return is_truth_label(value) or bool(
        _OMI_STORY_CHECK_FINAL_TRUTH_LABEL_RE.search(value)
    )


def _validate_story_check_no_truth_final_label_in_value(
    value: Any,
    *,
    path: str,
    current_key: str = "",
) -> None:
    key_token = current_key.strip().lower()
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_story_check_no_truth_final_label_in_value(
                child,
                path=f"{path}.{key}",
                current_key=str(key),
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_story_check_no_truth_final_label_in_value(
                child,
                path=f"{path}[{idx}]",
                current_key=current_key,
            )
        return
    if key_token in _OMI_STORY_CHECK_EVIDENCE_VALUE_KEYS:
        return
    if isinstance(value, str) and _story_check_string_has_truth_final_label(value):
        raise ValueError(
            f"Story Check envelope contains truth/canon/final/approval label "
            f"at {path!r}: {value!r}; Story Check output is diagnostic "
            f"support only and must never be canon, final, or approved."
        )


def _validate_story_check_payload_no_forbidden_operations(
    value: Any,
    *,
    path: str,
    current_key: str = "",
) -> None:
    key_token = current_key.strip().lower().replace("-", " ").replace("_", " ")
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key).strip().lower().replace("-", " ").replace("_", " ")
            for forbidden in _OMI_STORY_CHECK_FORBIDDEN_OPERATION_FIELD_NAME_SUBSTRINGS:
                if forbidden in normalized_key:
                    raise ValueError(
                        f"Story Check output contains forbidden operation "
                        f"field {path}.{key}; Story Check diagnostics must "
                        f"not persist candidates, mutate Memory/Canon, create "
                        f"promotion records, or run/enable apply-promotion."
                    )
            _validate_story_check_payload_no_forbidden_operations(
                child,
                path=f"{path}.{key}",
                current_key=str(key),
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_story_check_payload_no_forbidden_operations(
                child,
                path=f"{path}[{idx}]",
                current_key=current_key,
            )
        return
    if key_token in _OMI_STORY_CHECK_EVIDENCE_VALUE_KEYS:
        return
    if isinstance(value, str) and _OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE.search(value):
        raise ValueError(
            f"Story Check output contains forbidden operation text at {path}; "
            f"Story Check diagnostics must return support only, not perform "
            f"candidate persistence, Memory/Canon mutation, promotion, or "
            f"apply-promotion operations."
        )


def _validate_story_check_payload_no_generation_language(
    value: Any,
    *,
    path: str,
    current_key: str = "",
) -> None:
    key_token = current_key.strip().lower()
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_story_check_payload_no_generation_language(
                child,
                path=f"{path}.{key}",
                current_key=str(key),
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_story_check_payload_no_generation_language(
                child,
                path=f"{path}[{idx}]",
                current_key=current_key,
            )
        return
    if key_token in _OMI_STORY_CHECK_EVIDENCE_VALUE_KEYS:
        return
    if isinstance(value, str) and _OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE.search(value):
        raise ValueError(
            f"Story Check output contains prose-generation/revision language "
            f"at {path}; diagnostic questions may only support review and "
            f"must not ask for rewriting, continuation, outlining, drafting, "
            f"polishing, expansion, or revision."
        )


def _validate_story_check_review_status_fields(
    finding: dict[str, Any],
) -> None:
    for status_key in ("review_status", "candidate_status"):
        if status_key not in finding:
            continue
        status_value = _require_non_empty_string(
            finding[status_key], f"Story Check finding {status_key}"
        )
        if status_value not in OMI_FINDING_REVIEW_STATUSES:
            raise ValueError(
                f"Story Check finding {status_key}={status_value!r} is not "
                f"a review-pending candidate status; Story Check output must "
                f"not imply approval, finality, canon, or truth."
            )


def _validate_story_check_provenance(provenance: Any) -> dict[str, str]:
    normalized = _validate_finding_provenance(provenance)
    if normalized["adapter"] != OMI_STORY_CHECK_ADAPTER_NAME:
        raise ValueError(
            "Story Check provenance.adapter must match the story_check identity"
        )
    if normalized["tool_source"] != OMI_STORY_CHECK_ADAPTER_NAME:
        raise ValueError(
            "Story Check provenance.tool_source must match the story_check identity"
        )
    return normalized


def _normalize_story_check_evidence(
    finding: dict[str, Any],
    *,
    source_locator: str,
) -> list[dict[str, Any]]:
    raw_evidence = finding.get("evidence")
    evidence_items: list[Any] = []
    if isinstance(raw_evidence, list):
        evidence_items = list(raw_evidence)
    elif isinstance(raw_evidence, dict):
        evidence_items = [dict(raw_evidence)]
    else:
        excerpt = _first_non_empty_string(
            finding, _OMI_STORY_CHECK_EVIDENCE_EXCERPT_FIELD_NAMES
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
            "Story Check finding requires evidence with source_excerpt and "
            "source_locator"
        )

    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            raise ValueError(f"Story Check evidence item {idx} must be an object")
        item_copy = dict(item)
        excerpt = _first_non_empty_string(
            item_copy, _OMI_STORY_CHECK_EVIDENCE_EXCERPT_FIELD_NAMES
        )
        locator = _first_non_empty_string(
            item_copy, ("source_locator", "locator")
        ) or source_locator
        if not excerpt:
            raise ValueError(
                f"Story Check evidence item {idx} requires source_excerpt"
            )
        if not locator:
            raise ValueError(
                f"Story Check evidence item {idx} requires source_locator"
            )
        item_copy["source_excerpt"] = excerpt
        item_copy["source_locator"] = locator
        normalized.append(item_copy)
    return normalized


def _validate_story_check_owner_decision(
    owner_decision: Any,
) -> dict[str, Any]:
    if owner_decision is None:
        return {
            "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
            "approved": False,
        }
    if not isinstance(owner_decision, dict):
        raise ValueError("Story Check owner_decision must be an object")
    decision = owner_decision.get("decision")
    if decision is not None and decision not in {"pending", "needs_review"}:
        raise ValueError(
            "Story Check finding carries a non-pending owner_decision; "
            "diagnostic output is support only and must never approve, reject, "
            "promote, or finalize findings."
        )
    if owner_decision.get("approved") is True:
        raise ValueError(
            "Story Check finding owner_decision.approved=true; adapters must "
            "not auto-approve findings."
        )
    return {
        "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
        "approved": False,
    }


def _normalize_story_check_support_label(
    finding: dict[str, Any],
    provenance: dict[str, str],
) -> str:
    support_value = (
        finding.get("support_label")
        or finding.get("confidence")
        or finding.get("support")
        or provenance.get("support")
        or OMI_STORY_CHECK_SUPPORT_LABEL
    )
    if isinstance(support_value, (int, float)):
        support_label = f"Story Check support metadata: {support_value}"
    elif isinstance(support_value, str) and support_value.strip():
        support_label = support_value.strip()
        if "support" not in support_label.lower():
            support_label = f"Story Check support metadata: {support_label}"
    else:
        support_label = OMI_STORY_CHECK_SUPPORT_LABEL
    if _story_check_string_has_truth_final_label(support_label):
        raise ValueError(
            "Story Check support/confidence implies truth/canon/final/"
            "approval; must remain support metadata only."
        )
    return support_label


def _validate_story_check_finding(
    finding: Any,
    *,
    envelope_provenance: dict[str, str],
) -> dict[str, Any]:
    finding = _require_dict(finding, "Story Check finding")
    _validate_ollama_field_names_no_prose(
        finding, path="story_check_finding"
    )
    _validate_story_check_payload_no_forbidden_operations(
        finding, path="story_check_finding"
    )
    _validate_story_check_no_truth_final_label_in_value(
        finding, path="story_check_finding"
    )
    _validate_story_check_payload_no_generation_language(
        finding, path="story_check_finding"
    )
    _validate_story_check_review_status_fields(finding)

    candidate_type = _coerce_story_check_candidate_type(finding)
    label = _first_non_empty_string(finding, _OMI_STORY_CHECK_LABEL_FIELD_NAMES)
    if candidate_type == "diagnostic_question":
        extracted_claim = _first_non_empty_string(
            finding,
            (
                "question",
                "diagnostic_question",
                "diagnostic_claim",
                "extracted_claim",
                "claim",
                "support_claim",
                "observation",
                "diagnostic",
            ),
        )
    else:
        extracted_claim = _first_non_empty_string(
            finding, _OMI_STORY_CHECK_CLAIM_FIELD_NAMES
        )
    if not label and candidate_type in {"diagnostic_question", "open_question"}:
        label = extracted_claim
    if not label:
        raise ValueError("Story Check finding requires label/name/title")
    if not extracted_claim:
        raise ValueError(
            "Story Check finding requires diagnostic_claim, extracted_claim, "
            "support_claim, observation, or diagnostic question"
        )
    if is_prose_like_text(extracted_claim):
        raise ValueError(
            "Story Check finding extracted_claim looks like story prose / "
            "rewrite / polish / continuation / draft; OMI must analyze, not "
            "write. Rejecting as failed_closed."
        )

    source_locator = _require_non_empty_string(
        finding.get("source_locator"),
        "Story Check finding source_locator",
    )
    evidence = _normalize_story_check_evidence(
        finding,
        source_locator=source_locator,
    )

    finding_provenance = finding.get("provenance", envelope_provenance)
    provenance = _validate_story_check_provenance(finding_provenance)
    support_label = _normalize_story_check_support_label(finding, provenance)
    owner_decision = _validate_story_check_owner_decision(
        finding.get("owner_decision")
    )
    raw_finding_id = finding.get("raw_finding_id") or (
        f"{OMI_STORY_CHECK_ADAPTER_NAME}::{label}::{source_locator}"
    )
    if not isinstance(raw_finding_id, str) or not raw_finding_id.strip():
        raw_finding_id = (
            f"{OMI_STORY_CHECK_ADAPTER_NAME}::fixture::{source_locator}"
        )

    return {
        "candidate_type": candidate_type,
        "label": label,
        "extracted_claim": extracted_claim,
        "evidence": evidence,
        "source_locator": source_locator,
        "provenance": {
            "tool_source": OMI_STORY_CHECK_ADAPTER_NAME,
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "support": support_label,
        },
        "source_adapter": OMI_STORY_CHECK_ADAPTER_NAME,
        "support_label": support_label,
        "confidence": finding.get("confidence", support_label),
        "owner_decision": owner_decision,
        "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
        "raw_finding_id": raw_finding_id,
        "candidate_fingerprint": candidate_fingerprint(
            candidate_type,
            label,
            extracted_claim,
        ),
    }


def validate_story_check_fixture_envelope(payload: Any) -> dict[str, Any]:
    """Validate a Story Check diagnostic fixture envelope and normalize findings.

    T008 is fixture/mock handoff only. This function never imports or runs
    Story Check and rejects invalid schemas, missing evidence/source locators,
    missing provenance, unsafe prose/revision language, truth/canon/final/
    approved labels, Memory/Canon mutation, candidate persistence requests,
    promotion records, and apply-promotion requests.
    """
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Story Check envelope must be a JSON object; could not parse "
                f"string payload as JSON: {exc}"
            ) from exc
        payload = parsed

    envelope = _require_dict(payload, "Story Check envelope")
    _validate_ollama_field_names_no_prose(
        envelope, path="story_check_envelope"
    )
    _validate_story_check_payload_no_forbidden_operations(
        envelope, path="story_check_envelope"
    )
    _validate_story_check_no_truth_final_label_in_value(
        envelope, path="story_check_envelope"
    )
    _validate_story_check_payload_no_generation_language(
        envelope, path="story_check_envelope"
    )

    missing = [
        field for field in OMI_STORY_CHECK_ENVELOPE_REQUIRED_FIELDS
        if field not in envelope
    ]
    if missing:
        raise ValueError(
            f"Story Check envelope missing required fields: {missing}; "
            f"Story Check fixtures require schema_version, adapter, status, "
            f"provenance, and findings."
        )

    schema_version = _require_non_empty_string(
        envelope["schema_version"], "Story Check envelope schema_version"
    )
    if schema_version != OMI_STORY_CHECK_SCHEMA_VERSION:
        raise ValueError(
            f"Story Check envelope schema_version={schema_version!r} is not "
            f"supported; only {OMI_STORY_CHECK_SCHEMA_VERSION!r} is accepted."
        )
    adapter = _require_non_empty_string(
        envelope["adapter"], "Story Check envelope adapter"
    )
    if adapter != OMI_STORY_CHECK_ADAPTER_NAME:
        raise ValueError(
            f"Story Check envelope adapter={adapter!r} must be "
            f"{OMI_STORY_CHECK_ADAPTER_NAME!r}; mismatched adapter "
            f"identities fail closed."
        )
    status = _require_non_empty_string(
        envelope["status"], "Story Check envelope status"
    )
    if status not in OMI_STORY_CHECK_ALLOWED_STATUSES:
        raise ValueError(
            f"Story Check envelope status={status!r} is not allowed; must be "
            f"one of {sorted(OMI_STORY_CHECK_ALLOWED_STATUSES)}."
        )
    findings_value = envelope["findings"]
    if not isinstance(findings_value, list):
        raise ValueError("Story Check envelope findings must be an array")
    if status != "succeeded" and findings_value:
        raise ValueError(
            f"Story Check envelope carries findings in status={status!r}; "
            f"only 'succeeded' may carry findings."
        )

    envelope_provenance = _validate_story_check_provenance(
        envelope["provenance"]
    )
    normalized_findings = [
        _validate_story_check_finding(
            finding,
            envelope_provenance=envelope_provenance,
        )
        for finding in findings_value
    ]
    return {
        "schema_version": schema_version,
        "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
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


def _build_story_check_fixture_runner(
    fixture: Any,
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a safe fixture-only runner for Story Check diagnostic handoff."""
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")
    cached_envelope: dict[str, Any] | None = None
    cached_error: str | None = None

    def _try_validate() -> dict[str, Any]:
        try:
            return validate_story_check_fixture_envelope(fixture)
        except ValueError as exc:
            raise ValueError(
                f"Story Check fixture failed strict validation: {exc}"
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
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
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
                    "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
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
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "state": state,
            "explanation": (
                envelope["explanation"]
                or (
                    "Story Check fixture envelope validated against "
                    f"{OMI_STORY_CHECK_SCHEMA_VERSION}; orchestrator never "
                    f"performs live Story Check calls."
                )
            ),
            "candidates": envelope["findings"],
        }

    return _runner


# ---------------------------------------------------------------------------
# NCP / Subtxt / dramatica-flow diagnostic/context fixture contracts (T009)
# ---------------------------------------------------------------------------

OMI_NCP_SCHEMA_VERSION = "omi_ncp_context_handoff.v1"
OMI_SUBTXT_SCHEMA_VERSION = "omi_subtxt_diagnostic_handoff.v1"
OMI_DRAMATICA_FLOW_SCHEMA_VERSION = "omi_dramatica_flow_analysis_handoff.v1"
OMI_CONTEXT_ADAPTER_NAMES: frozenset[str] = frozenset(
    {"ncp", "subtxt", "dramatica_flow"}
)
OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER: dict[str, str] = {
    "ncp": OMI_NCP_SCHEMA_VERSION,
    "subtxt": OMI_SUBTXT_SCHEMA_VERSION,
    "dramatica_flow": OMI_DRAMATICA_FLOW_SCHEMA_VERSION,
}
OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER: dict[str, str] = {
    "ncp": "NCP context support only",
    "subtxt": "Subtxt diagnostic support only",
    "dramatica_flow": "dramatica-flow analysis support only",
}
OMI_CONTEXT_ALLOWED_STATUSES: frozenset[str] = frozenset(
    {"succeeded", "empty", "failed_closed", "error"}
)
OMI_CONTEXT_ENVELOPE_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "adapter",
    "status",
    "provenance",
    "findings",
)
OMI_CONTEXT_ALLOWED_NORMALIZED_TYPES_BY_ADAPTER: dict[str, frozenset[str]] = {
    "ncp": frozenset(
        {
            "story_fact",
            "storyform_context",
            "throughline_context",
            "relationship",
            "open_question",
            "ambiguity",
            "diagnostic_question",
            "evidence_note",
        }
    ),
    "subtxt": frozenset(
        {
            "structural_diagnostic",
            "conflict_diagnostic",
            "throughline_context",
            "storyform_context",
            "open_question",
            "ambiguity",
            "diagnostic_question",
            "evidence_note",
        }
    ),
    "dramatica_flow": frozenset(
        {
            "plot_thread",
            "story_fact",
            "open_question",
            "diagnostic_question",
            "continuity_warning",
            "conflict_diagnostic",
            "relationship",
            "timeline_event",
            "evidence_note",
            "ambiguity",
        }
    ),
}

_OMI_CONTEXT_TYPE_FIELD_NAMES: tuple[str, ...] = (
    "candidate_type",
    "finding_type",
    "diagnostic_type",
    "context_type",
    "analysis_type",
    "support_type",
    "type",
    "kind",
    "category",
)
_OMI_CONTEXT_LABEL_FIELD_NAMES: tuple[str, ...] = (
    "label",
    "name",
    "title",
    "question_label",
)
_OMI_CONTEXT_CLAIM_FIELD_NAMES: tuple[str, ...] = (
    "diagnostic_claim",
    "context_claim",
    "analysis_claim",
    "extracted_claim",
    "claim",
    "support_claim",
    "observation",
    "diagnostic",
    "question",
    "diagnostic_question",
)
_OMI_CONTEXT_QUESTION_CLAIM_FIELD_NAMES: tuple[str, ...] = (
    "question",
    "diagnostic_question",
    "diagnostic_claim",
    "context_claim",
    "analysis_claim",
    "extracted_claim",
    "claim",
    "support_claim",
    "observation",
    "diagnostic",
)
_OMI_CONTEXT_EVIDENCE_EXCERPT_FIELD_NAMES: tuple[str, ...] = (
    "source_excerpt",
    "evidence_excerpt",
    "excerpt",
    "source_text",
    "owner_authored_excerpt",
    "quote",
    "quote_text",
    "sentence",
    "sentence_text",
)
_OMI_CONTEXT_EVIDENCE_VALUE_KEYS: frozenset[str] = frozenset(
    {
        "source_excerpt",
        "evidence_excerpt",
        "excerpt",
        "source_text",
        "owner_authored_excerpt",
        "quote",
        "quote_text",
        "sentence",
        "sentence_text",
        "source_locator",
        "locator",
    }
)
_OMI_CONTEXT_FORBIDDEN_OPERATION_FIELD_NAME_SUBSTRINGS: tuple[str, ...] = (
    "operation",
    "action",
    "command",
    "persist candidate",
    "persist candidates",
    "candidate persistence",
    "persisted candidate",
    "save candidate",
    "operation request",
    "tool operation",
    "write request",
    "memory mutation",
    "canon mutation",
    "promotion record",
    "apply promotion",
    "promote to canon",
)
_OMI_CONTEXT_FORBIDDEN_OPERATION_VALUE_RE = re.compile(
    r"(persist(?:ed)?\s+candidates?|save\s+candidates?|"
    r"candidate\s+persistence|apply[-_\s]?promotion|promotion\s+record|"
    r"promote\s+to\s+canon|mutat(?:e|ion)\s+(?:memory|canon)|"
    r"write\s+(?:candidate|memory|canon)|"
    r"perform(?:ing)?\s+(?:an\s+)?operation)",
    re.IGNORECASE,
)
_OMI_CONTEXT_FORBIDDEN_GENERATION_VALUE_RE = re.compile(
    r"\b("
    r"rewrite|rewritten|continue|continuation|expand|expanded|polish|"
    r"polished|outline|draft|revise|revised|improve|improved|"
    r"improvement|suggest(?:ion)?\s+(?:for\s+)?(?:the\s+)?"
    r"(?:story|scene|chapter|prose|outline|draft)|"
    r"write\s+(?:the\s+)?(?:story|scene|chapter|prose)|"
    r"generate\s+(?:a\s+)?(?:story|scene|chapter|outline|draft|prose)|"
    r"what\s+happens\s+next|what\s+should\s+happen\s+next|"
    r"next\s+scene\s+should|next\s+chapter\s+should|make\s+it\s+better"
    r")\b",
    re.IGNORECASE,
)
_OMI_CONTEXT_TYPE_ALIASES_BY_ADAPTER: dict[str, dict[str, str]] = {
    "ncp": {
        "project_context": "story_fact",
        "project_story_context": "story_fact",
        "project_story_context_support": "story_fact",
        "story_context": "story_fact",
        "story_context_support": "story_fact",
        "context_support": "story_fact",
        "storyform": "storyform_context",
        "storyform_support": "storyform_context",
        "storyform_context_support": "storyform_context",
        "moment_context": "evidence_note",
        "moment_scene_context": "evidence_note",
        "moment_scene_context_support": "evidence_note",
        "scene_context": "evidence_note",
        "scene_context_support": "evidence_note",
        "throughline": "throughline_context",
        "throughline_support": "throughline_context",
        "throughline_context_support": "throughline_context",
        "authorial_intent": "evidence_note",
        "authorial_intent_context": "evidence_note",
        "authorial_intent_support": "evidence_note",
        "relationship_context": "relationship",
        "relationship_support": "relationship",
        "open_question_support": "open_question",
        "question": "open_question",
        "ambiguity_support": "ambiguity",
        "source_mapping": "evidence_note",
        "source_map": "evidence_note",
        "source_mapping_support": "evidence_note",
        "review_question": "diagnostic_question",
        "owner_review_question": "diagnostic_question",
    },
    "subtxt": {
        "structural": "structural_diagnostic",
        "structure": "structural_diagnostic",
        "structure_diagnostic": "structural_diagnostic",
        "structural_observation": "structural_diagnostic",
        "conflict": "conflict_diagnostic",
        "source_of_conflict": "conflict_diagnostic",
        "source_of_conflict_diagnostic": "conflict_diagnostic",
        "subject_vs_conflict": "conflict_diagnostic",
        "subject_vs_conflict_diagnostic": "conflict_diagnostic",
        "throughline": "throughline_context",
        "throughline_diagnostic": "throughline_context",
        "throughline_support": "throughline_context",
        "story_point": "storyform_context",
        "story_point_context": "storyform_context",
        "story_point_support": "storyform_context",
        "storyform": "storyform_context",
        "context_support": "evidence_note",
        "uncertainty": "ambiguity",
        "uncertainty_diagnostic": "ambiguity",
        "insufficient_evidence": "ambiguity",
        "insufficient_evidence_diagnostic": "ambiguity",
        "review_question": "diagnostic_question",
        "owner_review_question": "diagnostic_question",
        "question": "diagnostic_question",
        "evidence_support": "evidence_note",
    },
    "dramatica_flow": {
        "causal_chain": "plot_thread",
        "causal_chain_support": "plot_thread",
        "cause_effect": "plot_thread",
        "promise_payoff": "plot_thread",
        "promise_payoff_support": "plot_thread",
        "setup_payoff": "plot_thread",
        "setup_payoff_support": "plot_thread",
        "foreshadowing": "open_question",
        "foreshadowing_support": "open_question",
        "mystery": "open_question",
        "mystery_question": "open_question",
        "question": "open_question",
        "conflict_thread": "conflict_diagnostic",
        "conflict_thread_support": "conflict_diagnostic",
        "conflict_group": "conflict_diagnostic",
        "conflict_group_diagnostic": "conflict_diagnostic",
        "uncertainty_conflict_group": "conflict_diagnostic",
        "emotional_arc": "plot_thread",
        "emotional_arc_support": "plot_thread",
        "arc": "plot_thread",
        "relationship_network": "relationship",
        "relationship_network_support": "relationship",
        "relationship_support": "relationship",
        "timeline_activity": "timeline_event",
        "timeline_thread_activity": "timeline_event",
        "thread_activity": "timeline_event",
        "information_boundary": "evidence_note",
        "information_boundary_support": "evidence_note",
        "uncertainty": "ambiguity",
        "uncertainty_support": "ambiguity",
        "review_question": "diagnostic_question",
        "owner_review_question": "diagnostic_question",
        "warning": "continuity_warning",
    },
}


def _context_adapter_display_name(adapter_name: str) -> str:
    return {
        "ncp": "NCP",
        "subtxt": "Subtxt",
        "dramatica_flow": "dramatica-flow",
    }.get(adapter_name, adapter_name)


def _coerce_context_adapter_candidate_type(
    adapter_name: str,
    finding: dict[str, Any],
) -> str:
    raw_type = _first_non_empty_string(finding, _OMI_CONTEXT_TYPE_FIELD_NAMES)
    allowed_types = OMI_CONTEXT_ALLOWED_NORMALIZED_TYPES_BY_ADAPTER[adapter_name]
    if raw_type in allowed_types:
        return raw_type
    if raw_type in OMI_ORCHESTRATOR_FINDING_TYPES:
        raise ValueError(
            f"{_context_adapter_display_name(adapter_name)} finding type "
            f"{raw_type!r} is not allowed for this adapter contract."
        )

    token = _normalize_local_nlp_type_token(raw_type)
    mapped_type = _OMI_CONTEXT_TYPE_ALIASES_BY_ADAPTER[adapter_name].get(token)
    if mapped_type and mapped_type in allowed_types:
        return mapped_type

    raise ValueError(
        f"{_context_adapter_display_name(adapter_name)} finding unknown "
        f"candidate/finding type {raw_type!r}; fixture outputs must map to "
        f"one of {sorted(allowed_types)}."
    )


def _context_adapter_string_has_truth_final_label(value: str) -> bool:
    return _story_check_string_has_truth_final_label(value)


def _validate_context_adapter_no_truth_final_label_in_value(
    value: Any,
    *,
    adapter_name: str,
    path: str,
    current_key: str = "",
) -> None:
    key_token = current_key.strip().lower()
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_context_adapter_no_truth_final_label_in_value(
                child,
                adapter_name=adapter_name,
                path=f"{path}.{key}",
                current_key=str(key),
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_context_adapter_no_truth_final_label_in_value(
                child,
                adapter_name=adapter_name,
                path=f"{path}[{idx}]",
                current_key=current_key,
            )
        return
    if key_token in _OMI_CONTEXT_EVIDENCE_VALUE_KEYS:
        return
    if isinstance(value, str) and _context_adapter_string_has_truth_final_label(value):
        display_name = _context_adapter_display_name(adapter_name)
        raise ValueError(
            f"{display_name} envelope contains truth/canon/final/approval "
            f"label at {path!r}: {value!r}; {display_name} output is "
            f"support only and must never be canon, final, or approved."
        )


def _validate_context_adapter_payload_no_forbidden_operations(
    value: Any,
    *,
    adapter_name: str,
    path: str,
    current_key: str = "",
) -> None:
    key_token = current_key.strip().lower().replace("-", " ").replace("_", " ")
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key).strip().lower().replace("-", " ").replace("_", " ")
            for forbidden in _OMI_CONTEXT_FORBIDDEN_OPERATION_FIELD_NAME_SUBSTRINGS:
                if forbidden in normalized_key:
                    display_name = _context_adapter_display_name(adapter_name)
                    raise ValueError(
                        f"{display_name} output contains forbidden operation "
                        f"field {path}.{key}; diagnostic/context adapters "
                        f"must not persist candidates, mutate Memory/Canon, "
                        f"create promotion records, or run/enable "
                        f"apply-promotion."
                    )
            _validate_context_adapter_payload_no_forbidden_operations(
                child,
                adapter_name=adapter_name,
                path=f"{path}.{key}",
                current_key=str(key),
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_context_adapter_payload_no_forbidden_operations(
                child,
                adapter_name=adapter_name,
                path=f"{path}[{idx}]",
                current_key=current_key,
            )
        return
    if key_token in _OMI_CONTEXT_EVIDENCE_VALUE_KEYS:
        return
    if isinstance(value, str) and _OMI_CONTEXT_FORBIDDEN_OPERATION_VALUE_RE.search(value):
        display_name = _context_adapter_display_name(adapter_name)
        raise ValueError(
            f"{display_name} output contains forbidden operation text at "
            f"{path}; diagnostic/context adapters must return support only, "
            f"not perform candidate persistence, Memory/Canon mutation, "
            f"promotion, or apply-promotion operations."
        )


def _validate_context_adapter_payload_no_generation_language(
    value: Any,
    *,
    adapter_name: str,
    path: str,
    current_key: str = "",
) -> None:
    key_token = current_key.strip().lower()
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_context_adapter_payload_no_generation_language(
                child,
                adapter_name=adapter_name,
                path=f"{path}.{key}",
                current_key=str(key),
            )
        return
    if isinstance(value, list):
        for idx, child in enumerate(value):
            _validate_context_adapter_payload_no_generation_language(
                child,
                adapter_name=adapter_name,
                path=f"{path}[{idx}]",
                current_key=current_key,
            )
        return
    if key_token in _OMI_CONTEXT_EVIDENCE_VALUE_KEYS:
        return
    if isinstance(value, str) and _OMI_CONTEXT_FORBIDDEN_GENERATION_VALUE_RE.search(value):
        display_name = _context_adapter_display_name(adapter_name)
        raise ValueError(
            f"{display_name} output contains prose-generation/revision "
            f"language at {path}; diagnostic questions may only support "
            f"review and must not ask for rewriting, continuation, "
            f"outlining, drafting, polishing, expansion, improvement, or "
            f"revision."
        )


def _validate_context_adapter_review_status_fields(
    adapter_name: str,
    finding: dict[str, Any],
) -> None:
    display_name = _context_adapter_display_name(adapter_name)
    for status_key in ("review_status", "candidate_status"):
        if status_key not in finding:
            continue
        status_value = _require_non_empty_string(
            finding[status_key], f"{display_name} finding {status_key}"
        )
        if status_value not in OMI_FINDING_REVIEW_STATUSES:
            raise ValueError(
                f"{display_name} finding {status_key}={status_value!r} is "
                f"not a review-pending candidate status; adapter output must "
                f"not imply approval, finality, canon, or truth."
            )


def _validate_context_adapter_provenance(
    provenance: Any,
    *,
    adapter_name: str,
) -> dict[str, str]:
    normalized = _validate_finding_provenance(provenance)
    display_name = _context_adapter_display_name(adapter_name)
    if normalized["adapter"] != adapter_name:
        raise ValueError(
            f"{display_name} provenance.adapter must match the "
            f"{adapter_name} identity"
        )
    if normalized["tool_source"] != adapter_name:
        raise ValueError(
            f"{display_name} provenance.tool_source must match the "
            f"{adapter_name} identity"
        )
    return normalized


def _normalize_context_adapter_evidence(
    adapter_name: str,
    finding: dict[str, Any],
    *,
    source_locator: str,
) -> list[dict[str, Any]]:
    raw_evidence = finding.get("evidence")
    evidence_items: list[Any] = []
    if isinstance(raw_evidence, list):
        evidence_items = list(raw_evidence)
    elif isinstance(raw_evidence, dict):
        evidence_items = [dict(raw_evidence)]
    else:
        excerpt = _first_non_empty_string(
            finding, _OMI_CONTEXT_EVIDENCE_EXCERPT_FIELD_NAMES
        )
        if excerpt:
            evidence_items = [
                {
                    "source_excerpt": excerpt,
                    "source_locator": source_locator,
                }
            ]

    display_name = _context_adapter_display_name(adapter_name)
    if not evidence_items:
        raise ValueError(
            f"{display_name} finding requires evidence with source_excerpt "
            f"and source_locator"
        )

    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            raise ValueError(f"{display_name} evidence item {idx} must be an object")
        item_copy = dict(item)
        excerpt = _first_non_empty_string(
            item_copy, _OMI_CONTEXT_EVIDENCE_EXCERPT_FIELD_NAMES
        )
        locator = _first_non_empty_string(
            item_copy, ("source_locator", "locator")
        ) or source_locator
        if not excerpt:
            raise ValueError(
                f"{display_name} evidence item {idx} requires source_excerpt"
            )
        if not locator:
            raise ValueError(
                f"{display_name} evidence item {idx} requires source_locator"
            )
        item_copy["source_excerpt"] = excerpt
        item_copy["source_locator"] = locator
        normalized.append(item_copy)
    return normalized


def _validate_context_adapter_owner_decision(
    owner_decision: Any,
    *,
    adapter_name: str,
) -> dict[str, Any]:
    display_name = _context_adapter_display_name(adapter_name)
    if owner_decision is None:
        return {
            "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
            "approved": False,
        }
    if not isinstance(owner_decision, dict):
        raise ValueError(f"{display_name} owner_decision must be an object")
    decision = owner_decision.get("decision")
    if decision is not None and decision not in {"pending", "needs_review"}:
        raise ValueError(
            f"{display_name} finding carries a non-pending owner_decision; "
            f"diagnostic/context output is support only and must never "
            f"approve, reject, promote, or finalize findings."
        )
    if owner_decision.get("approved") is True:
        raise ValueError(
            f"{display_name} finding owner_decision.approved=true; adapters "
            f"must not auto-approve findings."
        )
    return {
        "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
        "approved": False,
    }


def _normalize_context_adapter_support_label(
    adapter_name: str,
    finding: dict[str, Any],
    provenance: dict[str, str],
) -> str:
    support_value = (
        finding.get("support_label")
        or finding.get("confidence")
        or finding.get("support")
        or provenance.get("support")
        or OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER[adapter_name]
    )
    if isinstance(support_value, (int, float)):
        support_label = f"{adapter_name} support metadata: {support_value}"
    elif isinstance(support_value, str) and support_value.strip():
        support_label = support_value.strip()
        if "support" not in support_label.lower():
            support_label = f"{adapter_name} support metadata: {support_label}"
    else:
        support_label = OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER[adapter_name]
    if _context_adapter_string_has_truth_final_label(support_label):
        display_name = _context_adapter_display_name(adapter_name)
        raise ValueError(
            f"{display_name} support/confidence implies truth/canon/final/"
            f"approval; must remain support metadata only."
        )
    return support_label


def _validate_context_adapter_finding(
    finding: Any,
    *,
    adapter_name: str,
    envelope_provenance: dict[str, str],
) -> dict[str, Any]:
    display_name = _context_adapter_display_name(adapter_name)
    finding = _require_dict(finding, f"{display_name} finding")
    _validate_ollama_field_names_no_prose(
        finding, path=f"{adapter_name}_finding"
    )
    _validate_context_adapter_payload_no_forbidden_operations(
        finding,
        adapter_name=adapter_name,
        path=f"{adapter_name}_finding",
    )
    _validate_context_adapter_no_truth_final_label_in_value(
        finding,
        adapter_name=adapter_name,
        path=f"{adapter_name}_finding",
    )
    _validate_context_adapter_payload_no_generation_language(
        finding,
        adapter_name=adapter_name,
        path=f"{adapter_name}_finding",
    )
    _validate_context_adapter_review_status_fields(adapter_name, finding)

    candidate_type = _coerce_context_adapter_candidate_type(
        adapter_name, finding
    )
    label = _first_non_empty_string(finding, _OMI_CONTEXT_LABEL_FIELD_NAMES)
    if candidate_type in {"diagnostic_question", "open_question"}:
        extracted_claim = _first_non_empty_string(
            finding, _OMI_CONTEXT_QUESTION_CLAIM_FIELD_NAMES
        )
    else:
        extracted_claim = _first_non_empty_string(
            finding, _OMI_CONTEXT_CLAIM_FIELD_NAMES
        )
    if not label and candidate_type in {
        "diagnostic_question",
        "open_question",
        "ambiguity",
    }:
        label = extracted_claim
    if not label:
        raise ValueError(f"{display_name} finding requires label/name/title")
    if not extracted_claim:
        raise ValueError(
            f"{display_name} finding requires diagnostic_claim, "
            f"context_claim, analysis_claim, extracted_claim, support_claim, "
            f"observation, or diagnostic question"
        )
    if is_prose_like_text(extracted_claim):
        raise ValueError(
            f"{display_name} finding extracted_claim looks like story prose / "
            f"rewrite / polish / continuation / draft; OMI must analyze, not "
            f"write. Rejecting as failed_closed."
        )

    source_locator = _require_non_empty_string(
        finding.get("source_locator"),
        f"{display_name} finding source_locator",
    )
    evidence = _normalize_context_adapter_evidence(
        adapter_name,
        finding,
        source_locator=source_locator,
    )

    finding_provenance = finding.get("provenance", envelope_provenance)
    provenance = _validate_context_adapter_provenance(
        finding_provenance,
        adapter_name=adapter_name,
    )
    support_label = _normalize_context_adapter_support_label(
        adapter_name,
        finding,
        provenance,
    )
    owner_decision = _validate_context_adapter_owner_decision(
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
        "confidence": finding.get("confidence", support_label),
        "owner_decision": owner_decision,
        "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
        "raw_finding_id": raw_finding_id,
        "candidate_fingerprint": candidate_fingerprint(
            candidate_type,
            label,
            extracted_claim,
        ),
    }


def validate_context_adapter_fixture_envelope(
    payload: Any,
    *,
    adapter_name: str,
) -> dict[str, Any]:
    """Validate a T009 diagnostic/context fixture envelope and findings.

    This contract is fixture/mock output only. It never imports or runs NCP,
    Subtxt, or dramatica-flow and rejects invalid schemas, missing evidence,
    missing source locators, missing provenance, unsafe prose/revision
    language, truth/canon/final/approved labels, Memory/Canon mutation,
    candidate persistence requests, promotion records, and apply-promotion
    requests.
    """
    if adapter_name not in OMI_CONTEXT_ADAPTER_NAMES:
        raise ValueError(f"Unsupported diagnostic/context adapter: {adapter_name}")
    display_name = _context_adapter_display_name(adapter_name)
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{display_name} envelope must be a JSON object; could not "
                f"parse string payload as JSON: {exc}"
            ) from exc
        payload = parsed

    envelope = _require_dict(payload, f"{display_name} envelope")
    _validate_ollama_field_names_no_prose(
        envelope, path=f"{adapter_name}_envelope"
    )
    _validate_context_adapter_payload_no_forbidden_operations(
        envelope,
        adapter_name=adapter_name,
        path=f"{adapter_name}_envelope",
    )
    _validate_context_adapter_no_truth_final_label_in_value(
        envelope,
        adapter_name=adapter_name,
        path=f"{adapter_name}_envelope",
    )
    _validate_context_adapter_payload_no_generation_language(
        envelope,
        adapter_name=adapter_name,
        path=f"{adapter_name}_envelope",
    )

    missing = [
        field for field in OMI_CONTEXT_ENVELOPE_REQUIRED_FIELDS
        if field not in envelope
    ]
    if missing:
        raise ValueError(
            f"{display_name} envelope missing required fields: {missing}; "
            f"T009 fixtures require schema_version, adapter, status, "
            f"provenance, and findings."
        )

    schema_version = _require_non_empty_string(
        envelope["schema_version"], f"{display_name} envelope schema_version"
    )
    expected_schema = OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER[adapter_name]
    if schema_version != expected_schema:
        raise ValueError(
            f"{display_name} envelope schema_version={schema_version!r} is "
            f"not supported; only {expected_schema!r} is accepted."
        )
    envelope_adapter = _require_non_empty_string(
        envelope["adapter"], f"{display_name} envelope adapter"
    )
    if envelope_adapter != adapter_name:
        raise ValueError(
            f"{display_name} envelope adapter={envelope_adapter!r} must be "
            f"{adapter_name!r}; mismatched adapter identities fail closed."
        )
    status = _require_non_empty_string(
        envelope["status"], f"{display_name} envelope status"
    )
    if status not in OMI_CONTEXT_ALLOWED_STATUSES:
        raise ValueError(
            f"{display_name} envelope status={status!r} is not allowed; "
            f"must be one of {sorted(OMI_CONTEXT_ALLOWED_STATUSES)}."
        )
    findings_value = envelope["findings"]
    if not isinstance(findings_value, list):
        raise ValueError(f"{display_name} envelope findings must be an array")
    if status != "succeeded" and findings_value:
        raise ValueError(
            f"{display_name} envelope carries findings in status={status!r}; "
            f"only 'succeeded' may carry findings."
        )

    envelope_provenance = _validate_context_adapter_provenance(
        envelope["provenance"],
        adapter_name=adapter_name,
    )
    normalized_findings = [
        _validate_context_adapter_finding(
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


def _build_context_adapter_fixture_runner(
    adapter_name: str,
    fixture: Any,
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a safe fixture-only runner for a T009 context adapter."""
    if adapter_name not in OMI_CONTEXT_ADAPTER_NAMES:
        raise ValueError(f"Unsupported diagnostic/context adapter: {adapter_name}")
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")
    cached_envelope: dict[str, Any] | None = None
    cached_error: str | None = None

    def _try_validate() -> dict[str, Any]:
        try:
            return validate_context_adapter_fixture_envelope(
                fixture,
                adapter_name=adapter_name,
            )
        except ValueError as exc:
            display_name = _context_adapter_display_name(adapter_name)
            raise ValueError(
                f"{display_name} fixture failed strict validation: {exc}"
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
                    f"{_context_adapter_display_name(adapter_name)} fixture "
                    f"envelope validated against "
                    f"{OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER[adapter_name]}; "
                    f"orchestrator never performs live {adapter_name} calls."
                )
            ),
            "candidates": envelope["findings"],
        }

    return _runner


# ---------------------------------------------------------------------------
# Live spaCy adapter runner (T014C) — behind explicit env flags
# ---------------------------------------------------------------------------

_OMI_LIVE_TOOLS_ENABLED_ENV = "OMI_LIVE_TOOLS_ENABLED"
_OMI_LIVE_SPACY_ENABLED_ENV = "OMI_LIVE_SPACY_ENABLED"
_OMI_LIVE_SPACY_BLOCKED_ENV = "OMI_LIVE_SPACY_BLOCKED"
_OMI_LIVE_SPACY_BLOCKED_REASON_ENV = "OMI_LIVE_SPACY_BLOCKED_REASON"
_OMI_LIVE_SPACY_MODEL_ENV = "OMI_LIVE_SPACY_MODEL"
_OMI_LIVE_SPACY_MODEL_DEFAULT = "en_core_web_sm"

# ---------------------------------------------------------------------------
# Live Ollama structured extraction adapter (T015C) — behind explicit env
# flags
# ---------------------------------------------------------------------------

_OMI_LIVE_OLLAMA_ENABLED_ENV = "OMI_LIVE_OLLAMA_ENABLED"
_OMI_LIVE_OLLAMA_BLOCKED_ENV = "OMI_LIVE_OLLAMA_BLOCKED"
_OMI_LIVE_OLLAMA_BLOCKED_REASON_ENV = "OMI_LIVE_OLLAMA_BLOCKED_REASON"
_OMI_LIVE_OLLAMA_BASE_URL_ENV = "OMI_LIVE_OLLAMA_BASE_URL"
_OMI_LIVE_OLLAMA_BASE_URL_DEFAULT = "http://127.0.0.1:11434"
_OMI_LIVE_OLLAMA_MODEL_ENV = "OMI_LIVE_OLLAMA_MODEL"
_OMI_LIVE_OLLAMA_MODEL_DEFAULT = "qwen3:8b"
_OMI_LIVE_OLLAMA_MODEL_NAME_ENV = "OMI_LIVE_OLLAMA_MODEL_NAME"
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_ENV = "OMI_LIVE_OLLAMA_TIMEOUT_SECONDS"
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_DEFAULT = 180.0
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MIN = 1.0
_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX = 1800.0

_OMI_LIVE_OLLAMA_SYSTEM_PROMPT = (
    "You are a strictly JSON-only structured extraction assistant. "
    "Analyze the owner-provided raw idea text below. "
    "Return ONLY valid JSON. No markdown, no explanation, no prose. "
    "The JSON must conform to the schema 'omi_ollama_structured_extraction.v1': "
    '{"schema_version": "omi_ollama_structured_extraction.v1", '
    '"adapter": "ollama_model", '
    '"status": "succeeded" or "empty", '
    '"explanation": "brief extraction note", '
    '"findings": [{"candidate_type": "...", "label": "...", '
    '"extracted_claim": "...", '
    '"evidence": [{"source_excerpt": "...", "source_locator": "..."}], '
    '"source_locator": "..."}]}. '
    "Allowed candidate types: character, location, organization, object, "
    "timeline_event, relationship, plot_thread, story_fact, open_question, "
    "storyform_context, diagnostic_question. "
    "Rules: extract only from the provided text. "
    "Do NOT rewrite, continue, brainstorm, suggest, invent facts, or make "
    "canon/truth/approval claims. Do NOT mutate Memory/Canon or create "
    "promotion records. Every finding must include evidence from the source "
    "text. If nothing can be extracted, set status to 'empty' with an empty "
    "findings list."
)

# ---------------------------------------------------------------------------
# Live Story Check diagnostic adapter (T016C) — behind explicit env flags
# ---------------------------------------------------------------------------

_OMI_LIVE_STORY_CHECK_ENABLED_ENV = "OMI_LIVE_STORY_CHECK_ENABLED"
_OMI_LIVE_STORY_CHECK_BLOCKED_ENV = "OMI_LIVE_STORY_CHECK_BLOCKED"
_OMI_LIVE_STORY_CHECK_BLOCKED_REASON_ENV = "OMI_LIVE_STORY_CHECK_BLOCKED_REASON"
_OMI_LIVE_STORY_CHECK_SCENE_ID_ENV = "OMI_LIVE_STORY_CHECK_SCENE_ID"

# ---------------------------------------------------------------------------
# Live BookNLP local NLP adapter (T017B) — behind explicit env flags
# ---------------------------------------------------------------------------

_OMI_LIVE_BOOKNLP_ENABLED_ENV = "OMI_LIVE_BOOKNLP_ENABLED"
_OMI_LIVE_BOOKNLP_BLOCKED_ENV = "OMI_LIVE_BOOKNLP_BLOCKED"
_OMI_LIVE_BOOKNLP_BLOCKED_REASON_ENV = "OMI_LIVE_BOOKNLP_BLOCKED_REASON"
_OMI_LIVE_BOOKNLP_MODEL_ENV = "OMI_LIVE_BOOKNLP_MODEL"
_OMI_LIVE_BOOKNLP_MODEL_DEFAULT = "small"
_OMI_LIVE_BOOKNLP_PIPELINE_ENV = "OMI_LIVE_BOOKNLP_PIPELINE"
_OMI_LIVE_BOOKNLP_PIPELINE_DEFAULT = "entity,quote,supersense,event"
_OMI_LIVE_BOOKNLP_INPUT_BOOK_ID = "omi_booknlp_input"
_OMI_LIVE_BOOKNLP_INPUT_FILENAME = "omi_booknlp_input.txt"
_OMI_LIVE_BOOKNLP_MAX_FINDINGS = 64
_OMI_LIVE_BOOKNLP_MAX_EVIDENCE_CHARS = 240

# T017C1 narrow compatibility shim for BookNLP/transformers state-dict
# ``bert.embeddings.position_ids`` key.
#
# BookNLP 1.0.8 was written against a transformers version in which
# ``BertEmbeddings.position_ids`` was a persistent buffer and therefore
# part of the saved state_dict. The newer installed transformers
# (>=4.13ish, here transformers==5.5.0) registers ``position_ids`` as a
# non-persistent buffer in ``BertEmbeddings`` so it is NOT part of the
# model's ``state_dict()``. When BookNLP's
# ``LitBankEntityTagger`` / ``LitBankCoref`` / ``QuotationAttribution``
# classes do
# ``self.model.load_state_dict(torch.load(model_file, map_location=device))``
# with ``strict=True`` (the default), the saved ``position_ids`` key is
# reported as an unexpected key and BookNLP fails closed at the entity
# tagger constructor.
#
# The shim is narrowly scoped: it wraps ``torch.load`` ONLY for the
# duration of the BookNLP constructor inside the live runner, and it
# removes ONLY the single known-incompatible non-trainable key
# ``bert.embeddings.position_ids`` from any returned state_dict-like
# dict that contains it. All other keys are preserved, and
# ``load_state_dict`` is still called with ``strict=True`` so any
# other unexpected key still fails closed. The shim is not a broad
# ``strict=False`` workaround.
_BOOKNLP_STATE_DICT_SHIM_TOLERATED_KEYS: frozenset[str] = frozenset({
    "bert.embeddings.position_ids",
})

_OMI_BOOKNLP_LIVE_ENTITY_CATEGORY_TO_CANDIDATE_TYPE: dict[str, str] = {
    "PER": "character",
    "GPE": "location",
    "LOC": "location",
    "FAC": "location",
    "ORG": "organization",
    "VEH": "object",
}

_OMI_BOOKNLP_LIVE_SKIP_ENTITY_TEXTS: frozenset[str] = frozenset({
    "i", "me", "my", "mine", "you", "your", "yours",
    "he", "him", "his", "she", "her", "hers",
    "they", "them", "their", "theirs",
    "we", "us", "our", "ours",
    "it", "its", "this", "that", "these", "those",
})


# ---------------------------------------------------------------------------
# Live NCP candidate-import validation adapter (T018B) — behind explicit env
# flags
# ---------------------------------------------------------------------------
#
# NCP is treated as a schema/interchange validation surface (NOT an automatic
# analysis runtime, NOT canon/truth). The T018B live adapter is therefore
# strictly owner-controlled:
#
#   * Disabled by default.
#   * Reachable only when OMI_LIVE_TOOLS_ENABLED + OMI_LIVE_NCP_ENABLED are
#     set, OMI_LIVE_NCP_BLOCKED is unset, AND an explicit
#     OMI_LIVE_NCP_INPUT_PATH points to an owner-selected NCP JSON file.
#   * The adapter does not scan project data, does not walk ``projects/``,
#     does not run ``npm install``/``npm audit fix``/``npm run validate:file``
#     over project data, and does not start a Node server.
#   * The optional ``OMI_LIVE_NCP_VALIDATE_WITH_NODE=1`` opt-in would
#     invoke the in-repo ``node`` validator as a child process. The opt-in
#     is opt-in only, must point at the explicit safe input file, and must
#     be mocked in tests.

_OMI_LIVE_NCP_ENABLED_ENV = "OMI_LIVE_NCP_ENABLED"
_OMI_LIVE_NCP_BLOCKED_ENV = "OMI_LIVE_NCP_BLOCKED"
_OMI_LIVE_NCP_BLOCKED_REASON_ENV = "OMI_LIVE_NCP_BLOCKED_REASON"
_OMI_LIVE_NCP_INPUT_PATH_ENV = "OMI_LIVE_NCP_INPUT_PATH"
_OMI_LIVE_NCP_VALIDATE_WITH_NODE_ENV = "OMI_LIVE_NCP_VALIDATE_WITH_NODE"

# Maximum number of NCP-derived candidate findings the runner will produce
# from a single NCP JSON file. The cap protects against unbounded NCP
# payloads leaking large numbers of candidates into the orchestrator.
_OMI_LIVE_NCP_MAX_FINDINGS = 64

# Maximum number of characters from a single NCP field value to surface as a
# source excerpt in the candidate finding. The cap keeps evidence snippets
# short and within the existing T009 contract.
_OMI_LIVE_NCP_MAX_EVIDENCE_CHARS = 240

# Mapping from NCP JSON keys (within ``narratives[].subtext.players[]``,
# ``narratives[].subtext.storypoints[]``, ``narratives[].subtext.storybeats[]``,
# ``narratives[].subtext.appreciations[]``, and the corresponding
# ``narratives[].storytelling.overviews`` block) to the candidate-only
# ``candidate_type`` the T009 fixture envelope will accept. Anything that
# does not map is skipped (fail-closed, no candidates).
#
# The T009 ``omi_ncp_context_handoff.v1`` envelope only accepts the narrow
# NCP-specific types in ``OMI_CONTEXT_ALLOWED_NORMALIZED_TYPES_BY_ADAPTER``
# (``story_fact``, ``storyform_context``, ``throughline_context``,
# ``relationship``, ``open_question``, ``ambiguity``,
# ``diagnostic_question``, ``evidence_note``). Per-item NCP character /
# location / organization / object / timeline_event / plot_thread
# content is therefore mapped to ``evidence_note`` (or ``story_fact`` for
# beat/point items) so the T009 envelope validator remains authoritative
# and the candidate still carries a JSON pointer and an evidence excerpt.
_OMI_LIVE_NCP_FIELD_TO_CANDIDATE_TYPE: dict[str, str] = {
    # Players / characters -> evidence_note (NCP player/character items
    # become evidence_note candidate findings).
    "players": "evidence_note",
    "player": "evidence_note",
    "characters": "evidence_note",
    "character": "evidence_note",
    "cast": "evidence_note",
    "roles": "evidence_note",
    # Locations / organizations / objects -> evidence_note.
    "locations": "evidence_note",
    "location": "evidence_note",
    "settings": "evidence_note",
    "world_locations": "evidence_note",
    "organizations": "evidence_note",
    "organization": "evidence_note",
    "factions": "evidence_note",
    "groups": "evidence_note",
    "objects": "evidence_note",
    "object": "evidence_note",
    "items": "evidence_note",
    "artifacts": "evidence_note",
    # Storybeats / moments -> story_fact (beat-level items become
    # story_fact candidate findings).
    "storybeats": "story_fact",
    "storybeat": "story_fact",
    "beats": "story_fact",
    "moments": "story_fact",
    "moment": "story_fact",
    # Storypoints / appreciations / plot threads -> story_fact.
    "storypoints": "story_fact",
    "storypoint": "story_fact",
    "appreciations": "story_fact",
    "appreciation": "story_fact",
    "plot_threads": "story_fact",
    "plot_thread": "story_fact",
    # Dynamics / vectors -> open_question (interpreted as open
    # structural questions for owner review).
    "dynamics": "open_question",
    "vectors": "open_question",
    # Overviews -> throughline_context (overview rows become
    # throughline_context candidate findings).
    "overviews": "throughline_context",
    # Relationships -> relationship candidate findings.
    "relationships": "relationship",
    "relationship": "relationship",
    # Open / diagnostic questions -> matching candidate types.
    "diagnostic_questions": "diagnostic_question",
    "diagnostic_question": "diagnostic_question",
    "open_questions": "open_question",
    "open_question": "open_question",
}


_OMI_SPACY_LIVE_ENTITY_LABEL_TO_CANDIDATE_TYPE: dict[str, str] = {
    "PERSON": "character",
    "GPE": "location",
    "LOC": "location",
    "FAC": "location",
    "ORG": "organization",
    "EVENT": "timeline_event",
}

_OMI_SPACY_LIVE_SKIP_NOUN_CHUNK_TEXTS: frozenset[str] = frozenset({
    "it", "he", "she", "they", "we", "you", "i", "me", "him", "her",
    "them", "us", "this", "that", "these", "those",
})


def _env_bool(env: Mapping[str, str], name: str, default: bool = False) -> bool:
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_positive_float(
    env: Mapping[str, str],
    name: str,
    *,
    default: float,
    min_value: float,
    max_value: float,
) -> float:
    """Return a positive finite float from ``env[name]`` with safe fallback.

    The orchestrator never raises on a bad timeout value. Missing, blank,
    non-numeric, zero, negative, non-finite, sub-``min_value``, or
    over-``max_value`` inputs all fall back to ``default`` so the live
    Ollama HTTP call always has a finite, positive timeout.
    """
    raw_value = env.get(name)
    if raw_value is None:
        return float(default)
    text = str(raw_value).strip()
    if not text:
        return float(default)
    try:
        parsed = float(text)
    except (TypeError, ValueError):
        return float(default)
    import math as _math
    if not _math.isfinite(parsed):
        return float(default)
    if parsed < float(min_value) or parsed > float(max_value):
        return float(default)
    return float(parsed)


# ---------------------------------------------------------------------------
# Live NCP candidate-import validation adapter (T018B) — helpers
# ---------------------------------------------------------------------------


def _ncp_safe_excerpt(value: Any, *, max_chars: int) -> str:
    """Return a short, plain trimmed string excerpt from arbitrary input.

    Used to build ``source_excerpt`` snippets for live NCP findings. The
    helper does NOT rewrite or sanitize the text. The caller is responsible
    for verifying the result is safe before using it as a candidate value
    (e.g., via the existing T009 ``validate_context_adapter_fixture_envelope``).
    The maximum length is hard-capped to keep evidence snippets short and
    within the existing T009 contract.
    """
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text:
        return ""
    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."
    return text


def _ncp_label_is_safe(value: Any) -> bool:
    """Return True iff ``value`` is a safe short NCP label/identifier.

    The check rejects truth/canon/final/approved/promoted/apply-promotion
    labels so an NCP node carrying a forbidden string cannot leak through
    as a candidate label.
    """
    if not isinstance(value, str):
        return False
    token = value.strip()
    if not token:
        return False
    if is_truth_label(token):
        return False
    if _PROSE_INTENT_PREFIX_RE.match(token):
        return False
    if len(token) > 240:
        return False
    return True


def _ncp_claim_is_safe(value: Any) -> bool:
    """Return True iff ``value`` is safe to surface as an NCP claim snippet.

    The check rejects empty/blank values, truth/canon/final/approved/
    promoted labels, prose-like text, and overly long snippets. Prose-like
    text is allowed only when the value is a short noun phrase or a single
    sentence-length description that does not look like story prose.
    """
    if not isinstance(value, str):
        return False
    token = value.strip()
    if not token:
        return False
    if is_truth_label(token):
        return False
    if _PROSE_INTENT_PREFIX_RE.match(token):
        return False
    if len(token) > 240:
        return False
    if is_prose_like_text(token):
        return False
    return True


def _ncp_path_is_relative_to(child: Path, parent: Path) -> bool:
    """Return True iff ``child`` is the same as or inside ``parent``.

    Uses :py:meth:`pathlib.PurePath.is_relative_to` when available
    (Python 3.9+); otherwise falls back to a safe
    :py:meth:`pathlib.PurePath.relative_to` + ``ValueError`` check.
    """
    is_relative_to = getattr(child, "is_relative_to", None)
    if callable(is_relative_to):
        try:
            return bool(child.is_relative_to(parent))
        except (OSError, ValueError):
            return False
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _ncp_resolve_allowed_input_path(
    raw_path: Any,
    *,
    repo_root: Path | None = None,
) -> Path | None:
    """Return an absolute, resolved Path for the owner-selected NCP file.

    The resolver is fail-closed and intentionally strict. It accepts only:

      * repo-local safe fixture/test paths under ``tests/``,
      * temporary paths under ``tempfile.gettempdir()``,
      * the in-repo ``.external_sources/narrative-context-protocol/examples``
        or ``.external_sources/narrative-context-protocol/tests`` trees,
      * the NCP schema fixtures in
        ``.external_sources/narrative-context-protocol/examples/invalid``.

    The resolver:

      * Rejects empty/non-string values.
      * Rejects symlinks (the input must be a regular file, not a symlink).
      * Rejects directories, hidden unsafe locations, traversal segments,
        and project-data trees (``projects/``).
      * Rejects paths actually inside the resolved
        ``repo_root / "projects"``,
        ``repo_root / "artifacts"``,
        ``repo_root / "graphify-out"``,
        ``repo_root / "ai_context"``, or
        ``repo_root / ".codex-context"`` trees.
      * Returns ``None`` (the runner treats this as fail-closed) for any
        value that does not satisfy the allowlist.

    Forbid-tree rejection uses a strict resolved-root check
    (``is_relative_to`` / ``relative_to`` + ``ValueError``) against the
    resolved forbidden roots, so a path under
    ``repo_root / ".external_sources"`` whose absolute
    :py:attr:`Path.parts` include an ancestor directory named
    ``projects`` (e.g., the workspace parent directory itself is named
    ``projects``) is still accepted — the resolver only rejects paths
    that are actually inside the resolved forbidden repo-local roots.

    This is the only path-resolution helper that can introduce a path into
    the NCP live runner. Tests must mock this helper.
    """
    if not isinstance(raw_path, str):
        return None
    stripped = raw_path.strip()
    if not stripped:
        return None

    if repo_root is None:
        from . import omi_analysis_orchestrator as _self_ref  # noqa: F401
        # Use the on-disk location of this module as the repo root anchor
        # when no explicit root is provided. The orchestrator module always
        # lives at ``<repo>/backend/omi_analysis_orchestrator.py``.
        repo_root = Path(__file__).resolve().parent.parent

    try:
        candidate = Path(stripped).expanduser()
    except (TypeError, ValueError):
        return None

    # Disallow obvious traversal segments before resolution.
    if ".." in candidate.parts:
        return None

    try:
        resolved = candidate.resolve(strict=False)
    except OSError:
        return None

    # The resolved path must be a regular file, not a symlink, not a
    # directory, and not a hidden unsafe location. The symlink check
    # runs against the unresolved candidate AND the resolved path
    # because ``Path.resolve`` follows symlinks and would otherwise
    # hide the symlink.
    try:
        if candidate.is_symlink() or resolved.is_symlink():
            return None
    except OSError:
        return None
    try:
        if not resolved.is_file():
            return None
    except OSError:
        return None

    # Project data trees and generated-context trees are NEVER valid
    # NCP input paths. The check is a strict resolved-root containment
    # check (``is_relative_to``) against each resolved forbidden root,
    # so only paths actually inside those repo-local forbidden trees
    # are rejected. A safe allowlisted path whose absolute
    # ``Path.parts`` happen to include an ancestor directory named
    # ``projects`` / ``artifacts`` / ``graphify-out`` / ``ai_context`` /
    # ``.codex-context`` outside the repo is NOT mis-rejected.
    forbidden_roots: tuple[Path, ...] = tuple(
        (repo_root / name).resolve(strict=False)
        for name in (
            "projects",
            "artifacts",
            "graphify-out",
            "ai_context",
            ".codex-context",
        )
    )
    for forbidden_root in forbidden_roots:
        if _ncp_path_is_relative_to(resolved, forbidden_root):
            return None

    # Candidate allowed roots, all relative to ``repo_root`` or the system
    # temp directory.
    try:
        temp_root = Path(tempfile.gettempdir()).resolve(strict=False)
    except OSError:
        temp_root = None

    try:
        external_root = (repo_root / ".external_sources").resolve(strict=False)
    except OSError:
        external_root = None

    try:
        tests_root = (repo_root / "tests").resolve(strict=False)
    except OSError:
        tests_root = None

    allowed = False
    for root in (tests_root, temp_root, external_root):
        if root is None:
            continue
        if not _ncp_path_is_relative_to(resolved, root):
            continue
        allowed = True
        break
    if not allowed:
        return None

    return resolved


def _ncp_json_pointer_for_path(parts: tuple[str, ...]) -> str:
    """Return a JSON pointer (RFC 6901) for a tuple of path segments.

    Empty segments, ``/``, ``~`` are escaped per RFC 6901. The empty
    pointer ``""`` is returned when ``parts`` is empty.
    """
    if not parts:
        return ""
    encoded: list[str] = []
    for segment in parts:
        text = str(segment)
        text = text.replace("~", "~0").replace("/", "~1")
        encoded.append("/" + text)
    return "".join(encoded)


def _ncp_extract_field(
    node: Any,
    field_names: tuple[str, ...],
) -> Any:
    """Return the first non-empty value found in ``node`` under any of
    ``field_names``. Returns ``None`` when no field is present or when
    every value is empty/blank/non-scalar.
    """
    if not isinstance(node, dict):
        return None
    for name in field_names:
        if name not in node:
            continue
        value = node[name]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
            continue
        if isinstance(value, (int, float, bool)):
            return value
    return None


def _ncp_collect_narrative_subtext_lists(
    ncp_doc: Any,
) -> list[tuple[str, list[Any]]]:
    """Return the list of (label, items) pairs the live NCP runner will
    scan for candidate evidence.

    Only subtext and storytelling fields the NCP schema explicitly defines
    as list-valued containers are scanned. Free-form ``narratives[].*`` or
    ``story.*`` fields are NEVER auto-walked; the runner never performs a
    project-wide scan.
    """
    pairs: list[tuple[str, list[Any]]] = []
    if not isinstance(ncp_doc, dict):
        return pairs

    narratives = ncp_doc.get("narratives")
    if not isinstance(narratives, list):
        narratives = []
    if not narratives:
        story = ncp_doc.get("story")
        if isinstance(story, dict):
            nested = story.get("narratives")
            if isinstance(nested, list):
                narratives = nested

    allowed_subtext_lists: dict[str, tuple[str, ...]] = {
        "players": ("players",),
        "storypoints": ("storypoints",),
        "storybeats": ("storybeats",),
        "appreciations": ("appreciations",),
        "dynamics": ("dynamics",),
        "vectors": ("vectors",),
    }
    allowed_storytelling_lists: dict[str, tuple[str, ...]] = {
        "overviews": ("overviews",),
        "relationships": ("relationships",),
        "open_questions": ("open_questions",),
        "diagnostic_questions": ("diagnostic_questions",),
    }
    allowed_story_lists: dict[str, tuple[str, ...]] = {
        "moments": ("moments",),
    }

    for narrative_index, narrative in enumerate(narratives):
        if not isinstance(narrative, dict):
            continue
        subtext = narrative.get("subtext")
        if isinstance(subtext, dict):
            for label, key_tuple in allowed_subtext_lists.items():
                container = subtext.get(key_tuple[0])
                if isinstance(container, list):
                    pairs.append((label, container))
        storytelling = narrative.get("storytelling")
        if isinstance(storytelling, dict):
            for label, key_tuple in allowed_storytelling_lists.items():
                container = storytelling.get(key_tuple[0])
                if isinstance(container, list):
                    pairs.append((label, container))
        _ = narrative_index  # currently unused; kept for future per-narrative pointer stability

    story = ncp_doc.get("story")
    if isinstance(story, dict):
        for label, key_tuple in allowed_story_lists.items():
            container = story.get(key_tuple[0])
            if isinstance(container, list):
                pairs.append((label, container))

    return pairs


def _ncp_safe_field_for_candidate_type(field_label: str) -> str | None:
    """Map an NCP subtext/storytelling list label to a candidate type.

    Returns the candidate type (T009 allowed) or ``None`` when the label
    is not in the safe mapping. The runner treats ``None`` as a skip, not
    as a fail-closed.
    """
    return _OMI_LIVE_NCP_FIELD_TO_CANDIDATE_TYPE.get(field_label)


def _ncp_validate_with_node_opt_in(
    *,
    absolute_input_path: Path,
) -> bool:
    """Opt-in Node ``validate:file`` check for an explicit safe NCP file.

    This helper is intentionally minimal and fail-closed:

      * Returns ``True`` only when the owner has opted in via
        ``OMI_LIVE_NCP_VALIDATE_WITH_NODE=1`` AND
        ``OMI_LIVE_NCP_INPUT_PATH`` is set AND the resolved file path
        satisfies ``_ncp_resolve_allowed_input_path``.
      * Otherwise returns ``False``. It never raises.

    The actual ``node tests/validate-file.js`` invocation is delegated to
    tests; production callers may pass a custom ``subprocess_runner`` in
    the future. The current production behavior is to return ``False``
    unless the opt-in is set, the file is allowed, and the caller wires
    in a custom runner. The helper exists so the live runner has a
    single, mockable entry point for the opt-in Node validation step.
    """
    if not isinstance(absolute_input_path, Path):
        return False
    try:
        if not absolute_input_path.is_file():
            return False
    except OSError:
        return False
    env = os.environ
    if not _env_bool(env, _OMI_LIVE_NCP_VALIDATE_WITH_NODE_ENV):
        return False
    # The opt-in is intentionally a no-op stub for T018B. The full Node
    # invocation is mocked in tests. Future tasks may extend this helper
    # to actually shell out to ``node tests/validate-file.js`` against the
    # explicit safe input file, but only with the same opt-in + explicit
    # file + mocked subprocess contract. T018B does not perform that
    # subprocess invocation.
    return False


def _ncp_build_finding_from_item(
    *,
    candidate_type: str,
    item: Any,
    container_pointer: str,
    item_index: int,
    adapter_name: str,
) -> dict[str, Any] | None:
    """Build a single T009-shaped finding dict from one NCP list item.

    Returns ``None`` when the item is empty, not a dict, or carries
    unsafe/prose-like/truth-labeled text in any of the candidate label,
    claim, or excerpt fields. The builder never raises.
    """
    if not isinstance(item, dict):
        return None
    label = _ncp_extract_field(
        item,
        (
            "name",
            "title",
            "label",
            "id",
            "identifier",
            "code",
            "moment_id",
            "moment_label",
            "summary",
        ),
    )
    if not _ncp_label_is_safe(label):
        return None

    claim = _ncp_extract_field(
        item,
        (
            "summary",
            "description",
            "narrative_function",
            "question",
            "moment_text",
            "narrative",
            "note",
            "observation",
        ),
    )
    if claim is None:
        claim = label
    if not _ncp_claim_is_safe(claim):
        return None

    excerpt_source = _ncp_extract_field(
        item,
        (
            "summary",
            "description",
            "narrative_function",
            "question",
            "moment_text",
            "narrative",
            "note",
            "observation",
        ),
    )
    excerpt = _ncp_safe_excerpt(
        excerpt_source if isinstance(excerpt_source, str) else "",
        max_chars=_OMI_LIVE_NCP_MAX_EVIDENCE_CHARS,
    )
    if not excerpt:
        excerpt = _ncp_safe_excerpt(
            label if isinstance(label, str) else "",
            max_chars=_OMI_LIVE_NCP_MAX_EVIDENCE_CHARS,
        )
    if not excerpt:
        return None

    item_id = _ncp_extract_field(item, ("id", "identifier", "code"))
    pointer_parts: tuple[str, ...] = (container_pointer, str(item_index))
    if item_id:
        pointer_parts = (container_pointer, str(item_index), str(item_id))
    source_locator = _ncp_json_pointer_for_path(pointer_parts)
    if not source_locator.startswith("/"):
        source_locator = "/" + source_locator

    return {
        "raw_finding_id": (
            f"ncp-live-{candidate_type}-"
            f"{item_index}-"
            f"{str(item_id) if item_id else 'no_id'}"
        ),
        "finding_type": candidate_type,
        "label": str(label),
        "context_claim": str(claim),
        "extracted_claim": str(claim),
        "evidence": [
            {
                "source_excerpt": excerpt,
                "source_locator": source_locator,
            }
        ],
        "source_locator": source_locator,
        "support_label": OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER[adapter_name],
        "confidence": "medium support",
    }


def _build_ncp_live_runner(
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a live NCP candidate-import validation adapter runner.

    T018B scope:

      * Disabled by default; reachable only via
        ``OMI_LIVE_TOOLS_ENABLED`` + ``OMI_LIVE_NCP_ENABLED`` +
        not ``OMI_LIVE_NCP_BLOCKED`` AND an explicit
        ``OMI_LIVE_NCP_INPUT_PATH``.
      * Reads the owner-selected NCP JSON file (no project-data scan).
      * Validates the JSON shape with a minimal Python-side schema/readiness
        check (no Node, no npm, no ``.external_sources`` writes).
      * Optionally invokes a Node ``validate:file`` subprocess ONLY when
        ``OMI_LIVE_NCP_VALIDATE_WITH_NODE=1`` is set AND the explicit
        safe input file is set. The subprocess call is bounded, fail-closed,
        and mocked in tests. The current T018B implementation returns
        ``False`` from the opt-in helper; tests that need a real
        subprocess call must monkeypatch ``_ncp_validate_with_node_opt_in``.
      * Maps a small, evidence-backed subset of NCP fields into the
        existing T009 ``omi_ncp_context_handoff.v1`` envelope shape and
        validates the converted envelope through
        ``validate_context_adapter_fixture_envelope``. The T009 validator
        remains authoritative; any T009 validation failure fails the
        runner closed with no findings.
      * Fail-closed on missing/empty/unsafe/unreadable/invalid-JSON input.
      * Never mutates ``.external_sources``, never persists NCP-derived
        candidates on its own, never mutates Memory/Canon, never creates
        promotion records, never runs apply-promotion, and never
        generates story prose.
      * NCP is treated as a schema/interchange surface only; candidate
        output is support-only evidence and never claims truth, canon,
        final, approved, or promoted status.

    The caller (``_resolve_adapter_runner``) must check env flags before
    building this runner. This runner does not re-check flags.
    """
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        _ = project_name
        _ = raw_idea
        _ = source_idea_id

        # Re-validate the explicit owner-selected input path inside the
        # runner so the runner is never reachable with an unsafe path.
        raw_path = os.environ.get(_OMI_LIVE_NCP_INPUT_PATH_ENV)
        if not isinstance(raw_path, str) or not raw_path.strip():
            return {
                "adapter": "ncp",
                "state": "unavailable",
                "explanation": (
                    f"Live NCP runner requested but {_OMI_LIVE_NCP_INPUT_PATH_ENV} "
                    "is unset/empty. The live NCP adapter requires an explicit "
                    "owner-selected NCP JSON path and does not auto-scan project "
                    "data. Failing closed with no candidates and no live call."
                ),
                "candidates": [],
            }
        absolute_path = _ncp_resolve_allowed_input_path(raw_path)
        if absolute_path is None:
            return {
                "adapter": "ncp",
                "state": "unavailable",
                "explanation": (
                    f"Live NCP runner received an unsafe or unresolvable "
                    f"{_OMI_LIVE_NCP_INPUT_PATH_ENV}: {raw_path!r}. The live NCP "
                    "adapter only accepts explicit owner-selected paths inside "
                    "the allowlisted test/temp/.external_sources trees and "
                    "refuses project data, traversal, symlinks, directories, "
                    "and hidden unsafe locations. Failing closed with no "
                    "candidates."
                ),
                "candidates": [],
            }

        # Opt-in Node validation step. The opt-in is intentionally a no-op
        # for T018B (the helper returns ``False`` unless tests monkeypatch
        # a custom subprocess runner in). Fail-closed if the opt-in is
        # enabled but the subprocess path is unavailable or fails.
        opt_in_enabled = _env_bool(
            os.environ, _OMI_LIVE_NCP_VALIDATE_WITH_NODE_ENV
        )
        if opt_in_enabled:
            try:
                opt_in_ok = _ncp_validate_with_node_opt_in(
                    absolute_input_path=absolute_path
                )
            except Exception as exc:  # pragma: no cover - defensive
                opt_in_ok = False
                _ = exc
            if not opt_in_ok:
                return {
                    "adapter": "ncp",
                    "state": "failed_closed",
                    "explanation": (
                        "Live NCP runner requested Node validation via "
                        f"{_OMI_LIVE_NCP_VALIDATE_WITH_NODE_ENV}=1, but the "
                        "opt-in subprocess path did not succeed. Failing "
                        "closed with no candidates, no Memory/Canon "
                        "mutation, and no project-data scan."
                    ),
                    "candidates": [],
                }

        # Read the NCP JSON file.
        try:
            with open(absolute_path, "r", encoding="utf-8") as handle:
                raw_text = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            return {
                "adapter": "ncp",
                "state": "failed_closed",
                "explanation": (
                    f"Live NCP runner could not read the explicit input "
                    f"file {absolute_path}: {type(exc).__name__}: {exc}. "
                    "Failing closed with no candidates."
                ),
                "candidates": [],
            }

        try:
            parsed = json.loads(raw_text)
        except ValueError as exc:
            return {
                "adapter": "ncp",
                "state": "failed_closed",
                "explanation": (
                    f"Live NCP runner could not parse the explicit input "
                    f"file {absolute_path} as JSON: {exc}. Failing closed "
                    "with no candidates."
                ),
                "candidates": [],
            }

        if not isinstance(parsed, dict):
            return {
                "adapter": "ncp",
                "state": "failed_closed",
                "explanation": (
                    f"Live NCP runner expected the top-level value of "
                    f"{absolute_path} to be a JSON object; got "
                    f"{type(parsed).__name__}. Failing closed with no "
                    "candidates."
                ),
                "candidates": [],
            }

        # Minimal Python-side schema/readiness check. The T018B runner
        # never requires a Node validator; it only requires the NCP
        # document carry the canonical ``schema_version`` and a
        # ``narratives`` (or ``story``) container. The NCP schema is
        # referenced as a static file in ``.external_sources/`` only and
        # is never imported, never installed, and never invoked.
        schema_version = parsed.get("schema_version")
        if not isinstance(schema_version, str) or not schema_version.strip():
            return {
                "adapter": "ncp",
                "state": "failed_closed",
                "explanation": (
                    "Live NCP runner requires a non-empty top-level "
                    "schema_version in the NCP JSON; got "
                    f"{schema_version!r}. Failing closed with no candidates."
                ),
                "candidates": [],
            }

        if (
            not isinstance(parsed.get("narratives"), list)
            and not isinstance(parsed.get("story"), dict)
        ):
            return {
                "adapter": "ncp",
                "state": "failed_closed",
                "explanation": (
                    "Live NCP runner requires either a top-level "
                    "'narratives' list or a top-level 'story' object in "
                    "the NCP JSON. Failing closed with no candidates."
                ),
                "candidates": [],
            }

        # Walk only the explicit, allow-listed subtext/storytelling
        # containers. No project data, no ``projects/`` traversal, no
        # ``.external_sources/`` mutation.
        candidate_pairs = _ncp_collect_narrative_subtext_lists(parsed)
        if not candidate_pairs:
            return {
                "adapter": "ncp",
                "state": "empty",
                "explanation": (
                    f"Live NCP runner found no allowlisted NCP subtext/"
                    f"storytelling containers in {absolute_path}; produced "
                    "no candidates."
                ),
                "candidates": [],
            }

        candidate_findings: list[dict[str, Any]] = []
        for label, items in candidate_pairs:
            candidate_type = _ncp_safe_field_for_candidate_type(label)
            if candidate_type is None:
                continue
            container_pointer = (
                f"/narratives/*/subtext/{label}"
                if label
                in {
                    "players",
                    "storypoints",
                    "storybeats",
                    "appreciations",
                    "dynamics",
                    "vectors",
                }
                else f"/narratives/*/storytelling/{label}"
                if label
                in {
                    "overviews",
                    "relationships",
                    "open_questions",
                    "diagnostic_questions",
                }
                else f"/story/{label}"
            )
            for item_index, item in enumerate(items):
                if len(candidate_findings) >= _OMI_LIVE_NCP_MAX_FINDINGS:
                    break
                finding = _ncp_build_finding_from_item(
                    candidate_type=candidate_type,
                    item=item,
                    container_pointer=container_pointer,
                    item_index=item_index,
                    adapter_name="ncp",
                )
                if finding is None:
                    continue
                candidate_findings.append(finding)
            if len(candidate_findings) >= _OMI_LIVE_NCP_MAX_FINDINGS:
                break

        if not candidate_findings:
            return {
                "adapter": "ncp",
                "state": "empty",
                "explanation": (
                    f"Live NCP runner found no safe/evidence-backed items "
                    f"in {absolute_path}; produced no candidates."
                ),
                "candidates": [],
            }

        envelope = {
            "schema_version": OMI_NCP_SCHEMA_VERSION,
            "adapter": "ncp",
            "status": "succeeded",
            "explanation": (
                f"Live NCP candidate-import adapter read the owner-selected "
                f"NCP JSON file {absolute_path} and converted "
                f"{len(candidate_findings)} evidence-backed item(s) into "
                "candidate-only NCP findings through the existing T009 "
                "fixture envelope shape. NCP output is schema/interchange "
                "support only; all findings are pending owner decision and "
                "must be reviewed before any use."
            ),
            "provenance": {
                "tool_source": "ncp",
                "adapter": "ncp",
                "support": OMI_CONTEXT_SUPPORT_LABEL_BY_ADAPTER["ncp"],
            },
            "findings": candidate_findings,
        }

        try:
            validated = validate_context_adapter_fixture_envelope(
                envelope, adapter_name="ncp"
            )
        except ValueError as exc:
            return {
                "adapter": "ncp",
                "state": "failed_closed",
                "explanation": (
                    "Live NCP converted envelope failed T009 validation: "
                    f"{exc}. Failing closed with no candidates."
                ),
                "candidates": [],
            }

        env_status = validated["status"]
        if env_status == "succeeded":
            state = "succeeded" if validated["findings"] else "empty"
        else:
            state = env_status

        return {
            "adapter": "ncp",
            "state": state,
            "explanation": (
                validated["explanation"]
                or "Live NCP candidate-import adapter completed."
            ),
            "candidates": validated["findings"],
        }

    return _runner


def _build_spacy_live_runner(
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a live spaCy adapter runner behind explicit runtime flags.

    The runner:

    - Imports spaCy lazily (never at module import time).
    - Loads the configured model from ``OMI_LIVE_SPACY_MODEL`` (default
      ``en_core_web_sm``). Does not download models.
    - Processes the raw idea text and extracts entities and noun chunks.
    - Converts entity labels: PERSON -> character, GPE/LOC/FAC -> location,
      ORG -> organization, EVENT -> timeline_event.
    - Converts non-overlapping noun chunks into object candidates.
    - Constructs a valid ``omi_spacy_local_nlp_extraction.v1`` envelope
      and normalizes it through the existing fixture validation pipeline.
    - Fail-closed on ImportError, OSError (model missing), runtime
      processing exception, or empty/malformed input.

    The caller (``_resolve_adapter_runner``) must check env flags before
    building this runner. This runner does not re-check flags.
    """
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        _ = project_name
        _ = source_idea_id

        if not isinstance(raw_idea, str) or not raw_idea.strip():
            return {
                "adapter": "spacy",
                "state": "empty",
                "explanation": (
                    "Live spaCy runner received empty raw idea text; "
                    "no entities or noun chunks to extract."
                ),
                "candidates": [],
            }

        raw_text = raw_idea.strip()

        try:
            import spacy  # lazy import

            model_name = os.environ.get(
                _OMI_LIVE_SPACY_MODEL_ENV, _OMI_LIVE_SPACY_MODEL_DEFAULT
            )
            nlp = spacy.load(model_name)
            doc = nlp(raw_text)
        except ImportError:
            return {
                "adapter": "spacy",
                "state": "unavailable",
                "explanation": (
                    "Live spaCy requested but the spaCy Python package is not "
                    "installed. Failing closed with no candidates."
                ),
                "candidates": [],
            }
        except OSError as exc:
            return {
                "adapter": "spacy",
                "state": "unavailable",
                "explanation": (
                    "Live spaCy requested but the configured model is not "
                    f"available/loadable: {exc}. Failing closed with no "
                    "candidates."
                ),
                "candidates": [],
            }
        except Exception as exc:
            return {
                "adapter": "spacy",
                "state": "failed_closed",
                "explanation": (
                    "Live spaCy runtime processing failed: "
                    f"{type(exc).__name__}: {exc}. "
                    "Failing closed with no candidates."
                ),
                "candidates": [],
            }

        findings: list[dict[str, Any]] = []
        seen_entity_texts: set[str] = set()
        entity_counter = 0

        for ent in doc.ents:
            candidate_type = _OMI_SPACY_LIVE_ENTITY_LABEL_TO_CANDIDATE_TYPE.get(
                ent.label_
            )
            if candidate_type is None:
                continue

            label_text = ent.text.strip()
            if not label_text:
                continue
            label_lower = label_text.lower()
            if label_lower in seen_entity_texts:
                continue
            seen_entity_texts.add(label_lower)

            entity_counter += 1
            sentence = doc.text
            if ent.sent and ent.sent.text:
                sentence = ent.sent.text

            source_locator = (
                f"raw_idea:L1:C{ent.start_char}-{ent.end_char}"
            )

            finding: dict[str, Any] = {
                "raw_finding_id": (
                    f"spacy-live-{ent.label_.lower()}-{entity_counter}"
                ),
                "spacy_label": ent.label_,
                "text": label_text,
                "claim": (
                    f"{label_text} appears as a {ent.label_} entity candidate"
                ),
                "sentence": sentence,
                "source_locator": source_locator,
                "confidence": "spaCy live support only",
            }
            findings.append(finding)

        noun_chunk_counter = 0
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            if not chunk_text:
                continue
            chunk_lower = chunk_text.lower()
            if chunk_lower in seen_entity_texts:
                continue

            overlaps = False
            for ent in doc.ents:
                if chunk.start < ent.end and chunk.end > ent.start:
                    overlaps = True
                    break
            if overlaps:
                continue

            chunk_tokens = chunk_text.split()
            if len(chunk_tokens) < 2:
                if chunk_lower in _OMI_SPACY_LIVE_SKIP_NOUN_CHUNK_TEXTS:
                    continue
            if len(chunk_tokens) > 6:
                continue

            noun_chunk_counter += 1
            chunk_sentence = doc.text
            if chunk.sent and chunk.sent.text:
                chunk_sentence = chunk.sent.text

            chunk_locator = (
                f"raw_idea:L1:C{chunk.start_char}-{chunk.end_char}"
            )

            finding = {
                "raw_finding_id": (
                    f"spacy-live-noun-chunk-{noun_chunk_counter}"
                ),
                "spacy_label": "NOUN_CHUNK",
                "text": chunk_text,
                "claim": (
                    f"{chunk_text} appears as a noun chunk candidate"
                ),
                "sentence": chunk_sentence,
                "source_locator": chunk_locator,
                "confidence": "spaCy live support only",
            }
            findings.append(finding)

        if not findings:
            return {
                "adapter": "spacy",
                "state": "empty",
                "explanation": (
                    "Live spaCy found no entities or noun chunks in the "
                    "raw idea text."
                ),
                "candidates": [],
            }

        envelope = {
            "schema_version": OMI_SPACY_SCHEMA_VERSION,
            "adapter": "spacy",
            "status": "succeeded",
            "explanation": "Live spaCy local NLP extraction.",
            "provenance": {
                "tool_source": "spacy",
                "adapter": "spacy",
                "support": "spaCy live support only",
            },
            "findings": findings,
        }

        try:
            validated = validate_local_nlp_fixture_envelope(
                envelope,
                adapter_name="spacy",
            )
        except ValueError as exc:
            return {
                "adapter": "spacy",
                "state": "failed_closed",
                "explanation": (
                    "Live spaCy envelope failed normalization: "
                    f"{exc}. Failing closed with no candidates."
                ),
                "candidates": [],
            }

        state = "succeeded" if validated["findings"] else "empty"
        return {
            "adapter": "spacy",
            "state": state,
            "explanation": (
                validated["explanation"]
                or "Live spaCy local NLP extraction succeeded."
            ),
            "candidates": validated["findings"],
        }

    return _runner


# ---------------------------------------------------------------------------
# Live Ollama structured extraction adapter runner (T015C)
# ---------------------------------------------------------------------------


def _build_ollama_model_live_runner(
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a live Ollama structured extraction adapter runner.

    The runner:

    - Reads ``OMI_LIVE_OLLAMA_BASE_URL`` (default ``http://127.0.0.1:11434``),
      ``OMI_LIVE_OLLAMA_MODEL`` (default ``qwen3:8b``), and falls back to
      ``OMI_LIVE_OLLAMA_MODEL_NAME`` for compatibility.
    - Reads ``OMI_LIVE_OLLAMA_TIMEOUT_SECONDS`` (default ``180``) and clamps
      the value to a finite positive range (clamped to the
      ``[min, max]`` bounds; falls back to the default on missing,
      blank, non-numeric, zero, negative, non-finite, or out-of-range
      values). The HTTP call always uses a finite, positive timeout.
    - Calls Ollama ``/api/chat`` with system instructions that require strict
      JSON output conforming to ``omi_ollama_structured_extraction.v1``.
    - Sends top-level ``think: false`` so Qwen3 thinking-mode output does not
      consume the response budget and leave ``message.content`` empty.
    - Uses ``stream=false``, a low output token limit, and a finite timeout.
    - Parses the response, extracts the message content, and validates it
      through ``validate_ollama_model_envelope``. ``message.thinking`` is
      never parsed as extraction output.
    - Treats non-JSON, malformed, prose-like, or unsafe output as fail-closed
      with no findings.
    - Uses Python standard library only (``urllib.request``).

    The caller (``_resolve_adapter_runner``) must check env flags before
    building this runner. This runner does not re-check flags.
    """
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        _ = project_name
        _ = source_idea_id

        if not isinstance(raw_idea, str) or not raw_idea.strip():
            return {
                "adapter": OMI_OLLAMA_ADAPTER_NAME,
                "state": "empty",
                "explanation": (
                    "Live Ollama runner received empty raw idea text; "
                    "no extraction possible."
                ),
                "candidates": [],
            }

        raw_text = raw_idea.strip()
        base_url = os.environ.get(
            _OMI_LIVE_OLLAMA_BASE_URL_ENV,
            _OMI_LIVE_OLLAMA_BASE_URL_DEFAULT,
        )
        model = (
            os.environ.get(_OMI_LIVE_OLLAMA_MODEL_ENV)
            or os.environ.get(_OMI_LIVE_OLLAMA_MODEL_NAME_ENV)
            or _OMI_LIVE_OLLAMA_MODEL_DEFAULT
        )
        timeout_seconds = _env_positive_float(
            os.environ,
            _OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_ENV,
            default=_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_DEFAULT,
            min_value=_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MIN,
            max_value=_OMI_LIVE_OLLAMA_TIMEOUT_SECONDS_MAX,
        )
        clean_base = base_url.rstrip("/")
        chat_url = f"{clean_base}/api/chat"

        messages = [
            {"role": "system", "content": _OMI_LIVE_OLLAMA_SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ]

        request_body = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {"num_predict": 2048},
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                chat_url,
                data=request_body,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                response_data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            return {
                "adapter": OMI_OLLAMA_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": (
                    f"Live Ollama HTTP call failed: "
                    f"{type(exc).__name__}: {exc}. "
                    "Failing closed with no candidates."
                ),
                "candidates": [],
            }

        try:
            message_content = response_data["message"]["content"]
        except (KeyError, TypeError, IndexError) as exc:
            return {
                "adapter": OMI_OLLAMA_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": (
                    f"Live Ollama response missing message content: "
                    f"{type(exc).__name__}: {exc}. "
                    "Failing closed with no candidates."
                ),
                "candidates": [],
            }

        try:
            validated = validate_ollama_model_envelope(message_content)
        except ValueError as exc:
            return {
                "adapter": OMI_OLLAMA_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": (
                    f"Live Ollama output failed validation: {exc}. "
                    "Failing closed with no candidates."
                ),
                "candidates": [],
            }

        env_status = validated["status"]
        if env_status == "succeeded":
            state = "succeeded" if validated["findings"] else "empty"
        else:
            state = env_status

        return {
            "adapter": OMI_OLLAMA_ADAPTER_NAME,
            "state": state,
            "explanation": (
                validated["explanation"]
                or "Live Ollama structured extraction completed."
            ),
            "candidates": validated["findings"],
        }

    return _runner


# ---------------------------------------------------------------------------
# Live Story Check diagnostic adapter (T016C)
# ---------------------------------------------------------------------------

# T016C1 boundary: the live adapter must NOT rewrite legacy Story Check
# output text to remove forbidden truth/canon/final/approved/promoted
# labels, apply-promotion operation text, or rewrite/continue/outline/draft
# generation language. The T008 validator is authoritative. Unsafe legacy
# text must be SKIPPED at the item level, not sanitized into acceptable
# text. The safety checker below classifies legacy text as safe/unsafe
# against the same T008 patterns the T008 validator uses. The legacy
# ``run_story_check`` callable surface is treated as an untrusted model
# output boundary.


def _story_check_legacy_text_is_safe(value: Any) -> bool:
    """Return True iff ``value`` is a non-empty plain string with no
    truth/canon/final/approved/promoted labels, no apply-promotion/promotion
    operation text, no rewrite/continue/outline/draft generation language,
    and no prose-shaped free text.

    The T008 contract rejects these labels in any non-evidence string value.
    The live Story Check adapter must NOT rewrite the legacy text to
    remove them. If the text is unsafe, the adapter SKIPS the item
    entirely; if all items are unsafe, the adapter returns ``failed_closed``
    with no findings.

    This checker reuses the same forbidden patterns the T008 validator
    uses, so safe/unsafe classification is consistent with T008.
    """
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    if is_prose_like_text(text):
        return False
    if is_truth_label(text):
        return False
    if _OMI_STORY_CHECK_FINAL_TRUTH_LABEL_RE.search(text):
        return False
    if _OMI_STORY_CHECK_FORBIDDEN_OPERATION_VALUE_RE.search(text):
        return False
    if _OMI_STORY_CHECK_FORBIDDEN_GENERATION_VALUE_RE.search(text):
        return False
    return True


def _story_check_safe_excerpt_text(value: Any, *, max_chars: int = 240) -> str:
    """Return a plain trimmed string from arbitrary input.

    This helper does NOT sanitize the text. The caller is responsible for
    verifying the result is safe before using it as a
    ``diagnostic_claim``, ``extracted_claim``, ``question``, or
    ``evidence.source_excerpt`` value (e.g., via
    ``_story_check_legacy_text_is_safe``). T016C1 tightened this boundary
    so the live adapter never rewrites unsafe legacy text.
    """
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text:
        return ""
    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."
    return text


def _story_check_extract_excerpts_from_value(
    value: Any,
    *,
    max_items: int = 5,
    max_chars: int = 240,
) -> list[str]:
    """Extract a small list of SAFE evidence excerpt strings from a legacy value.

    Accepts ``list[str]`` (truncated to ``max_items``), ``str`` (treated as
    a single excerpt), or ``dict`` with a known excerpt-like key. Returns a
    deduplicated, order-preserving list of safe strings.

    Safety boundary (T016C1): the helper does NOT rewrite or sanitize
    legacy text. Items whose text fails
    ``_story_check_legacy_text_is_safe`` are SKIPPED entirely (not
    converted to a safe phrase). T008 ``validate_story_check_fixture_envelope``
    remains the authoritative validator downstream.
    """
    excerpts: list[str] = []

    def _add_if_safe(raw_text: Any) -> None:
        if len(excerpts) >= max_items:
            return
        if not _story_check_legacy_text_is_safe(raw_text):
            return
        excerpt = _story_check_safe_excerpt_text(raw_text, max_chars=max_chars)
        if excerpt and excerpt not in excerpts:
            excerpts.append(excerpt)

    if isinstance(value, list):
        for item in value:
            _add_if_safe(item)
    elif isinstance(value, str):
        _add_if_safe(value)
    elif isinstance(value, dict):
        for key in (
            "source_excerpt",
            "evidence_excerpt",
            "excerpt",
            "source_text",
            "owner_authored_excerpt",
            "quote",
            "quote_text",
            "sentence",
            "sentence_text",
        ):
            if key in value:
                _add_if_safe(value.get(key))
                if len(excerpts) >= max_items:
                    break
    return excerpts


def _story_check_classify_candidate_type(
    raw_type: str,
    *,
    key_hint: str = "",
) -> str:
    """Map a legacy Story Check key/label to a T008 orchestrator finding type.

    Returns one of the recognized orchestrator finding types. The mapping is
    conservative: ambiguous legacy keys fall back to ``structural_diagnostic``
    so the resulting finding is still classified as a candidate-only
    diagnostic (never canon, never truth).
    """
    token = _normalize_local_nlp_type_token(raw_type)
    if token in {
        "structural_diagnostic",
        "structural_observation",
        "structure",
        "structure_diagnostic",
        "diagnostic",
        "diagnostic_observation",
        "warning",
        "concern",
    }:
        return "structural_diagnostic"
    if token in {
        "storyform",
        "storyform_context",
        "storyform_support",
        "context_support",
        "theme",
        "theme_drift",
        "storyform_context_support",
    }:
        return "storyform_context"
    if token in {
        "throughline",
        "throughline_context",
        "throughline_support",
        "throughline_context_support",
        "main_character",
        "influence_character",
        "relationship_story",
        "overall_story",
    }:
        return "throughline_context"
    if token in {
        "conflict",
        "conflict_diagnostic",
        "uncertainty",
        "uncertainty_diagnostic",
    }:
        return "conflict_diagnostic"
    if token in {
        "question",
        "diagnostic_question",
        "review_question",
        "owner_question",
        "owner_review_question",
        "suggestion",
    }:
        return "diagnostic_question"
    if token in {"open_question", "ambiguity", "ambiguous_support"}:
        return "open_question"
    if token in {"plot", "plot_thread", "plot_thread_diagnostic", "thread"}:
        return "plot_thread"
    if token in {
        "relationship",
        "relationship_diagnostic",
        "relationship_support",
    }:
        return "relationship"
    if token in {
        "continuity_warning",
        "continuity",
        "character_consistency",
    }:
        return "continuity_warning"
    if token in {"world_rule", "rule"}:
        return "world_rule"
    if token in {
        "candidate_support",
        "evidence_support",
        "evidence_note",
        "insufficient_evidence",
        "reason",
        "status",
    }:
        return "evidence_note"

    key_token = _normalize_local_nlp_type_token(key_hint)
    if key_token in {"suggestions", "questions"}:
        return "diagnostic_question"
    if key_token in {"warnings", "concerns"}:
        return "structural_diagnostic"
    if key_token in {"insufficient_evidence", "reasons"}:
        return "evidence_note"
    if key_token in {"evidence"}:
        return "evidence_note"

    return "structural_diagnostic"


def _story_check_make_finding(
    *,
    candidate_type: str,
    label: str,
    diagnostic_claim: str,
    evidence_excerpts: list[str],
    source_locator: str,
    support_label: str = "Story Check diagnostic support only",
) -> dict[str, Any] | None:
    """Build one T008-shaped finding dict for the live Story Check adapter.

    Returns ``None`` when the inputs cannot be turned into a T008-compatible
    finding (empty label or empty diagnostic_claim or no usable evidence or
    unsafe label/claim/evidence text). T016C1 boundary: the helper
    re-validates the safety of the label, claim, and evidence excerpts
    against ``_story_check_legacy_text_is_safe``. Unsafe text is rejected
    here as a defense-in-depth check so the T008 validator never sees
    rewritten/sanitized AI/tool/model output text.
    """
    if not isinstance(label, str) or not label.strip():
        return None
    if not isinstance(diagnostic_claim, str) or not diagnostic_claim.strip():
        return None
    if not evidence_excerpts:
        return None
    if not isinstance(source_locator, str) or not source_locator.strip():
        return None

    if not _story_check_legacy_text_is_safe(diagnostic_claim):
        return None
    for excerpt in evidence_excerpts:
        if not _story_check_legacy_text_is_safe(excerpt):
            return None

    excerpt = evidence_excerpts[0]
    secondary = evidence_excerpts[1] if len(evidence_excerpts) > 1 else ""

    evidence_items: list[dict[str, Any]] = [
        {
            "source_excerpt": excerpt,
            "source_locator": source_locator,
        }
    ]
    if secondary and secondary != excerpt:
        evidence_items.append(
            {
                "source_excerpt": secondary,
                "source_locator": source_locator,
            }
        )

    return {
        "raw_finding_id": (
            f"story_check_live::{label.strip()[:80]}::{source_locator}"
        ),
        "candidate_type": candidate_type,
        "label": label.strip()[:240],
        "diagnostic_claim": diagnostic_claim.strip(),
        "extracted_claim": diagnostic_claim.strip(),
        "question": diagnostic_claim.strip()
        if candidate_type == "diagnostic_question"
        else "",
        "evidence": evidence_items,
        "source_locator": source_locator,
        "support_label": support_label,
        "confidence": support_label,
        "provenance": {
            "tool_source": OMI_STORY_CHECK_ADAPTER_NAME,
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "support": support_label,
        },
        "source_adapter": OMI_STORY_CHECK_ADAPTER_NAME,
        "owner_decision": {
            "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
            "approved": False,
        },
        "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
    }


def _story_check_warning_label(category: str) -> str:
    """Return a generic converter-owned label for a legacy diagnostic item.

    T016C1 boundary: the label does NOT include any legacy text. The
    legacy text is used only as ``diagnostic_claim`` and
    ``evidence.source_excerpt`` after the safety check, never inside the
    label. The label is intentionally generic so the T008 validator
    cannot reject it on truth/canon/final/approved/promoted/operation/
    generation grounds.
    """
    if "warning" in category:
        return "Story Check warning"
    if "concern" in category:
        return "Story Check concern"
    if "insufficient" in category or "evidence_note" in category:
        return "Story Check insufficient evidence"
    if "question" in category:
        return "Story Check question"
    if "throughline" in category:
        return "Story Check throughline diagnostic"
    if "storyform" in category or "theme" in category:
        return "Story Check storyform diagnostic"
    if "character" in category:
        return "Story Check character consistency diagnostic"
    return "Story Check diagnostic"


def _story_check_resolve_scene_locator(
    *,
    project_name: str,
    scene_id: str,
) -> str:
    """Build a safe ``source_locator`` for live Story Check findings.

    The locator is project-scoped and scene-scoped. It does NOT include the
    raw scene text or any owner-authored content. The locator only identifies
    the project/scene surface that the Story Check diagnostic was anchored to.
    """
    safe_project = _require_non_empty_string(project_name, "project_name")
    safe_scene = _require_non_empty_string(scene_id, "scene_id")
    return f"project:{safe_project}::scene:{safe_scene}"


def _story_check_result_to_envelope(
    legacy_result: Any,
    *,
    project_name: str,
    scene_id: str,
) -> dict[str, Any]:
    """Convert a legacy Story Check result into a T008 envelope dict.

    The converter is intentionally conservative. It does NOT pass through
    legacy prose fields as candidate findings, and it does NOT parse
    candidate findings from unstructured narrative prose. It only emits
    candidate findings when the legacy result carries structured evidence
    (warnings/concerns/suggestions/insufficient_evidence as a list, or a
    ``throughline_alignment``/``theme_drift``/``character_consistency``
    object with evidence or concerns or a status/reason). Free-form prose,
    empty/None/string/NoneType payloads, payloads with only a ``task`` or
    ``coherence_score``, and any payload that cannot be mapped to at least
    one T008-shaped finding are converted to a fail-closed envelope with
    ``status="failed_closed"`` and an empty ``findings`` list.

    T016C1 safety boundary: the converter does NOT rewrite or sanitize
    legacy text to remove forbidden labels. Every legacy item
    (warning/concern/suggestion/insufficient_evidence/throughline
    evidence/throughline concern/theme_drift reason/character_consistency
    reason) is checked against ``_story_check_legacy_text_is_safe``
    before it is used as a ``diagnostic_claim`` or
    ``evidence.source_excerpt`` value. Unsafe items are SKIPPED
    individually; if every structured item is unsafe, the converter
    returns ``failed_closed`` with no findings. The converter never
    synthesizes placeholder text from ``present``/``status``/``reason``
    flags alone. The T008 ``validate_story_check_fixture_envelope`` is
    the authoritative downstream validator.

    The returned envelope has shape::

        {
            "schema_version": "omi_story_check_diagnostic_handoff.v1",
            "adapter": "story_check",
            "status": "succeeded" | "empty" | "failed_closed" | "error",
            "explanation": "...",
            "provenance": {"tool_source": "story_check", ...},
            "findings": [<T008-shaped finding>, ...],
        }

    The caller MUST then validate this envelope through
    ``validate_story_check_fixture_envelope`` before returning it to the
    orchestrator. The T008 validator is authoritative and remains the
    source of truth for evidence/provenance/owner-decision/review-status
    semantics.
    """
    base_explanation = (
        "Live Story Check adapter bridged the OMI orchestrator to "
        "backend.analysis_engine.run_story_check and converted the legacy "
        "result into the existing omi_story_check_diagnostic_handoff.v1 "
        "envelope shape. The T008 fixture validator remains authoritative."
    )

    provenance: dict[str, str] = {
        "tool_source": OMI_STORY_CHECK_ADAPTER_NAME,
        "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
        "support": OMI_STORY_CHECK_SUPPORT_LABEL,
    }

    if legacy_result is None or not isinstance(legacy_result, dict):
        return {
            "schema_version": OMI_STORY_CHECK_SCHEMA_VERSION,
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "status": "failed_closed",
            "explanation": (
                base_explanation
                + " Legacy result was not a JSON object; failing closed with "
                "no findings."
            ),
            "provenance": provenance,
            "findings": [],
        }

    if "error" in legacy_result and isinstance(legacy_result["error"], str):
        return {
            "schema_version": OMI_STORY_CHECK_SCHEMA_VERSION,
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "status": "error",
            "explanation": (
                base_explanation
                + " Legacy Story Check returned an error shape: "
                f"{legacy_result['error'][:240]}. Failing closed with no findings."
            ),
            "provenance": provenance,
            "findings": [],
        }

    locator = _story_check_resolve_scene_locator(
        project_name=project_name, scene_id=scene_id
    )

    findings: list[dict[str, Any]] = []

    warnings_value = legacy_result.get("warnings")
    if isinstance(warnings_value, list):
        for warning in warnings_value:
            if not _story_check_legacy_text_is_safe(warning):
                continue
            excerpt = _story_check_safe_excerpt_text(warning, max_chars=240)
            if not excerpt:
                continue
            label = _story_check_warning_label("warning")
            claim = "Story Check warning: " + excerpt
            finding = _story_check_make_finding(
                candidate_type="structural_diagnostic",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=[excerpt],
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    concerns_value = legacy_result.get("concerns")
    if isinstance(concerns_value, list):
        for concern in concerns_value:
            if not _story_check_legacy_text_is_safe(concern):
                continue
            excerpt = _story_check_safe_excerpt_text(concern, max_chars=240)
            if not excerpt:
                continue
            label = _story_check_warning_label("concern")
            claim = "Story Check concern: " + excerpt
            finding = _story_check_make_finding(
                candidate_type="structural_diagnostic",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=[excerpt],
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    suggestions_value = legacy_result.get("suggestions")
    if isinstance(suggestions_value, list):
        for suggestion in suggestions_value:
            if not _story_check_legacy_text_is_safe(suggestion):
                continue
            excerpt = _story_check_safe_excerpt_text(suggestion, max_chars=240)
            if not excerpt:
                continue
            label = _story_check_warning_label("question")
            claim = excerpt
            finding = _story_check_make_finding(
                candidate_type="diagnostic_question",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=[excerpt],
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    insufficient_evidence_value = legacy_result.get("insufficient_evidence")
    if isinstance(insufficient_evidence_value, list):
        for item in insufficient_evidence_value:
            if not _story_check_legacy_text_is_safe(item):
                continue
            excerpt = _story_check_safe_excerpt_text(item, max_chars=240)
            if not excerpt:
                continue
            label = _story_check_warning_label("insufficient_evidence")
            claim = "Story Check insufficient evidence: " + excerpt
            finding = _story_check_make_finding(
                candidate_type="evidence_note",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=[excerpt],
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    throughline_value = legacy_result.get("throughline_alignment")
    if isinstance(throughline_value, dict):
        for throughline_name in (
            "overall_story",
            "main_character",
            "influence_character",
            "relationship_story",
        ):
            entry = throughline_value.get(throughline_name)
            if not isinstance(entry, dict):
                continue
            entry_status = entry.get("present")
            evidence_list = _story_check_extract_excerpts_from_value(
                entry.get("evidence"), max_items=2, max_chars=240
            )
            concern_list = _story_check_extract_excerpts_from_value(
                entry.get("concerns"), max_items=2, max_chars=240
            )
            base_excerpts = evidence_list + concern_list
            # T016C1: the converter must NOT synthesize placeholder text
            # (e.g. "marked present" / "marked not present") from the
            # present flag alone. If no safe legacy evidence or concerns
            # are available, skip the throughline item rather than
            # generate text on its own.
            if not base_excerpts:
                continue
            claim = (
                f"Throughline '{throughline_name}' diagnostic: "
                f"present={entry_status}; concerns={len(concern_list)}; "
                f"evidence_items={len(evidence_list)}."
            )
            label = _story_check_warning_label("throughline")
            finding = _story_check_make_finding(
                candidate_type="throughline_context",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=base_excerpts,
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    theme_drift_value = legacy_result.get("theme_drift")
    if isinstance(theme_drift_value, dict):
        reason = theme_drift_value.get("reason")
        status = theme_drift_value.get("status")
        # T016C1: only proceed when a SAFE ``reason`` excerpt is available.
        # The converter must NOT synthesize placeholder text from the
        # ``status`` flag alone, and it must NOT use an unsafe ``reason``
        # as evidence. If the reason is missing or unsafe, skip the
        # theme_drift item entirely.
        excerpt = ""
        if isinstance(reason, str) and _story_check_legacy_text_is_safe(reason):
            excerpt = _story_check_safe_excerpt_text(reason, max_chars=240)
        if excerpt:
            claim = (
                f"Story Check theme drift diagnostic: status={status!r}; "
                f"reason={excerpt}."
            )
            label = _story_check_warning_label("storyform")
            finding = _story_check_make_finding(
                candidate_type="storyform_context",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=[excerpt],
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    character_consistency_value = legacy_result.get("character_consistency")
    if isinstance(character_consistency_value, dict):
        reason = character_consistency_value.get("reason")
        status = character_consistency_value.get("status")
        # T016C1: same boundary as theme_drift above. Only proceed when a
        # SAFE ``reason`` excerpt is available. The converter must NOT
        # synthesize placeholder text and must NOT use an unsafe
        # ``reason`` as evidence.
        excerpt = ""
        if isinstance(reason, str) and _story_check_legacy_text_is_safe(reason):
            excerpt = _story_check_safe_excerpt_text(reason, max_chars=240)
        if excerpt:
            claim = (
                f"Story Check character consistency diagnostic: "
                f"status={status!r}; reason={excerpt}."
            )
            label = _story_check_warning_label("character")
            finding = _story_check_make_finding(
                candidate_type="continuity_warning",
                label=label,
                diagnostic_claim=claim,
                evidence_excerpts=[excerpt],
                source_locator=locator,
            )
            if finding is not None:
                findings.append(finding)

    if not findings:
        return {
            "schema_version": OMI_STORY_CHECK_SCHEMA_VERSION,
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "status": "failed_closed",
            "explanation": (
                base_explanation
                + " Legacy Story Check result carried no structured "
                "diagnostics that could be safely mapped to T008 candidate "
                "findings (no warnings/concerns/suggestions/insufficient_"
                "evidence/throughline_alignment/theme_drift/character_"
                "consistency shape, or every structured item carried "
                "unsafe truth/canon/final/approved/promoted/apply-promotion"
                "/rewrite/continue/outline/draft/generation language and "
                "was skipped by the T016C1 safety boundary). Free-form "
                "prose and the legacy coherence_score alone are not used "
                "as candidate findings. Failing closed with no findings."
            ),
            "provenance": provenance,
            "findings": [],
        }

    return {
        "schema_version": OMI_STORY_CHECK_SCHEMA_VERSION,
        "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
        "status": "succeeded",
        "explanation": (
            base_explanation
            + f" Converted {len(findings)} candidate-only diagnostic "
            "findings from the legacy Story Check response shape into the "
            "T008 envelope; existing T008 validator remains authoritative."
        ),
        "provenance": provenance,
        "findings": findings,
    }


def _build_story_check_live_runner(
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a live Story Check adapter runner behind explicit runtime flags.

    The runner:

    - Imports ``backend.analysis_engine.run_story_check`` lazily (never at
      module import time and never when live flags are disabled).
    - Resolves ``project_name`` from the orchestrator entrypoint and
      ``scene_id`` from an explicit ``story_check_scene_id`` argument (when
      supplied by the caller) or from the ``OMI_LIVE_STORY_CHECK_SCENE_ID``
      environment variable. The explicit argument wins over the env var when
      both are present. If neither is available, the runner fails closed
      with ``unavailable`` and an explanation; it does NOT invent a scene
      id and does NOT call ``run_story_check``.
    - Calls ``run_story_check(project_name, scene_id)`` through the existing
      in-repo callable surface. The runner does NOT call the legacy
      ``POST /api/projects/{project_name}/story-check/{scene_id}`` route
      and does NOT post to Ollama directly; the existing surface owns
      scene text/bible/storyform loading, prompt rendering, and Ollama
      HTTP behavior.
    - Converts the legacy rich-Story-Check response (warnings, concerns,
      suggestions, insufficient_evidence, throughline_alignment,
      theme_drift, character_consistency) into the existing T008
      ``omi_story_check_diagnostic_handoff.v1`` envelope shape through
      ``_story_check_result_to_envelope``. Free-form prose, the legacy
      ``task``/``coherence_score`` alone, malformed/None/dict/string
      values, and ``{"error": ...}`` shapes all fail closed.
    - Validates the converted envelope through
      ``validate_story_check_fixture_envelope``. The T008 validator
      remains authoritative; any T008 validation failure fails the
      runner closed with no findings.
    - Fail-closed on ImportError, runtime exceptions, missing context
      (project name or scene id), blocked flag, or malformed legacy
      output. The runner never persists candidates, never mutates
      Memory/Canon, never creates promotion records, never runs
      apply-promotion, and never generates story prose.
    """
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        _ = raw_idea
        _ = source_idea_id

        if not isinstance(project_name, str) or not project_name.strip():
            return {
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                "state": "unavailable",
                "explanation": (
                    "Live Story Check runner received an empty/missing "
                    "project name; required context for "
                    "backend.analysis_engine.run_story_check is not "
                    "available. Failing closed with no findings and no "
                    "live call."
                ),
                "candidates": [],
            }

        scene_id = _adapter_config_scene_id(adapter_config)
        if scene_id is None:
            env_scene_id = os.environ.get(_OMI_LIVE_STORY_CHECK_SCENE_ID_ENV)
            if isinstance(env_scene_id, str) and env_scene_id.strip():
                scene_id = env_scene_id.strip()

        if not scene_id:
            return {
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                "state": "unavailable",
                "explanation": (
                    "Live Story Check runner has no scene id: caller did "
                    "not pass story_check_scene_id and "
                    f"{_OMI_LIVE_STORY_CHECK_SCENE_ID_ENV} is unset. "
                    "Required context for "
                    "backend.analysis_engine.run_story_check is not "
                    "available. Failing closed with no findings and no "
                    "live call."
                ),
                "candidates": [],
            }

        try:
            from backend import analysis_engine  # lazy import

            run_story_check = getattr(analysis_engine, "run_story_check", None)
            if not callable(run_story_check):
                return {
                    "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                    "state": "unavailable",
                    "explanation": (
                        "Live Story Check runner could not import "
                        "backend.analysis_engine.run_story_check; the "
                        "function is not callable from this environment. "
                        "Failing closed with no findings."
                    ),
                    "candidates": [],
                }
        except ImportError as exc:
            return {
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                "state": "unavailable",
                "explanation": (
                    "Live Story Check runner could not import "
                    "backend.analysis_engine.run_story_check: "
                    f"{type(exc).__name__}: {exc}. Failing closed with no "
                    "findings."
                ),
                "candidates": [],
            }

        try:
            legacy_result = run_story_check(
                project_name.strip(), scene_id
            )
        except Exception as exc:
            return {
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": (
                    "Live Story Check runtime call to "
                    "backend.analysis_engine.run_story_check raised: "
                    f"{type(exc).__name__}: {exc}. Failing closed with no "
                    "findings, no persistence, and no Memory/Canon "
                    "mutation."
                ),
                "candidates": [],
            }

        if not isinstance(legacy_result, dict):
            return {
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": (
                    "Live Story Check runtime returned a non-dict value "
                    f"({type(legacy_result).__name__}); cannot be safely "
                    "converted into the T008 envelope. Failing closed with "
                    "no findings."
                ),
                "candidates": [],
            }

        envelope = _story_check_result_to_envelope(
            legacy_result,
            project_name=project_name.strip(),
            scene_id=scene_id,
        )

        try:
            validated = validate_story_check_fixture_envelope(envelope)
        except ValueError as exc:
            return {
                "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
                "state": "failed_closed",
                "explanation": (
                    "Live Story Check converted envelope failed T008 "
                    f"validation: {exc}. Failing closed with no findings."
                ),
                "candidates": [],
            }

        env_status = validated["status"]
        if env_status == "succeeded":
            state = "succeeded" if validated["findings"] else "empty"
        else:
            state = env_status

        return {
            "adapter": OMI_STORY_CHECK_ADAPTER_NAME,
            "state": state,
            "explanation": (
                validated["explanation"]
                or "Live Story Check diagnostic adapter completed."
            ),
            "candidates": validated["findings"],
        }

    return _runner


# ---------------------------------------------------------------------------
# Live BookNLP local NLP adapter (T017B) — helpers
# ---------------------------------------------------------------------------


def _booknlp_safe_text_excerpt(value: Any, *, max_chars: int) -> str:
    """Return a short, plain trimmed string excerpt from arbitrary input.

    Used to build ``source_excerpt``/``extracted_claim`` snippets for live
    BookNLP findings. The helper does NOT rewrite or sanitize the text. The
    caller is responsible for verifying the result is safe before using it
    as a candidate value (e.g., via ``is_prose_like_text`` and
    ``is_truth_label``). The maximum length is hard-capped to keep evidence
    snippets short and within the existing T007/T014C contract.
    """
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if not text:
        return ""
    if len(text) > max_chars:
        text = text[: max_chars - 3].rstrip() + "..."
    return text


def _booknlp_entity_category_is_safe(value: str) -> bool:
    """Return True iff ``value`` is a safe BookNLP entity category token.

    BookNLP entity categories are short tokens such as ``PER``, ``GPE``,
    ``LOC``, ``FAC``, ``ORG``, ``VEH``, ``PROP_PER``, ``NOM_LOC``, etc.
    Anything else is rejected so a BookNLP row carrying a truth/canon/
    approved/promoted label or a non-canon code cannot leak through.
    """
    if not isinstance(value, str):
        return False
    token = value.strip().upper()
    if not token:
        return False
    if is_truth_label(token):
        return False
    if _PROSE_INTENT_PREFIX_RE.match(token):
        return False
    if len(token) > 32:
        return False
    for ch in token:
        if not (
            ch.isalnum()
            or ch == "_"
            or ch == "-"
        ):
            return False
    return True


def _booknlp_parse_entities_file(path: Any) -> list[dict[str, Any]]:
    """Parse a BookNLP ``.entities`` file into a list of row dicts.

    BookNLP writes ``.entities`` as TSV with a header row::

        COREF   start_token  end_token  prop  cat  text

    Malformed rows, rows missing required fields, rows whose category is not
    a safe short token, and rows whose text is empty/blank are silently
    skipped. The parser never raises. The returned list is empty if the
    file is missing, unreadable, or contains only a header.
    """
    rows: list[dict[str, Any]] = []
    if not isinstance(path, str) or not path:
        return rows
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return rows

    if not lines:
        return rows

    header = [col.strip() for col in lines[0].rstrip("\n").split("\t")]
    for raw_line in lines[1:]:
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < len(header):
            continue
        row: dict[str, str] = {}
        for idx, col in enumerate(header):
            if idx < len(parts):
                row[col] = parts[idx]
            else:
                row[col] = ""
        if not row.get("text", "").strip():
            continue
        cat = row.get("cat", "").strip()
        if not cat:
            continue
        if not _booknlp_entity_category_is_safe(cat):
            continue
        rows.append(row)
    return rows


def _booknlp_entity_candidate_type_from_category(cat: str) -> str | None:
    """Map a BookNLP entity category to an orchestrator finding type.

    BookNLP category format is ``<PROP|NOM|PRON>_<PER|GPE|LOC|FAC|ORG|VEH>``
    (and other variants). Only the suffix is mapped to keep the logic
    conservative. Returns ``None`` for unsupported categories.
    """
    if not isinstance(cat, str):
        return None
    token = cat.strip().upper()
    if not token:
        return None
    suffix = token.split("_", 1)[-1] if "_" in token else token
    return _OMI_BOOKNLP_LIVE_ENTITY_CATEGORY_TO_CANDIDATE_TYPE.get(suffix)


def _booknlp_safe_locator(parts: dict[str, Any], *, fallback: str) -> str:
    """Return a safe ``source_locator`` built from short token/locator parts.

    The locator is purely a numeric token locator. It never embeds raw text
    or owner-authored content. Falls back to ``fallback`` when no usable
    parts are present.
    """
    pieces: list[str] = []
    for key in ("start_token", "end_token", "byte_onset", "byte_offset"):
        value = parts.get(key)
        if isinstance(value, str) and value.strip().isdigit():
            pieces.append(f"{key}={value.strip()}")
        elif isinstance(value, int) and value >= 0:
            pieces.append(f"{key}={value}")
    if not pieces:
        return fallback
    return "raw_idea:" + ";".join(pieces)


def _booknlp_parse_tokens_file(path: Any) -> list[dict[str, str]]:
    """Parse a BookNLP ``.tokens`` file into a list of token row dicts.

    The tokens file is a TSV with a header row
    (``paragraph_ID``, ``sentence_ID``, ``token_ID_within_sentence``,
    ``token_ID_within_document``, ``word``, ``lemma``, ``byte_onset``,
    ``byte_offset``, ``POS_tag``, ``fine_POS_tag``, ``dependency_relation``,
    ``syntactic_head_ID``, ``event``). Malformed rows are silently
    skipped. The parser never raises. Returns an empty list when the file
    is missing, unreadable, or contains only a header.
    """
    rows: list[dict[str, str]] = []
    if not isinstance(path, str) or not path:
        return rows
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return rows
    if not lines:
        return rows
    header = [col.strip() for col in lines[0].rstrip("\n").split("\t")]
    for raw_line in lines[1:]:
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < len(header):
            continue
        row: dict[str, str] = {}
        for idx, col in enumerate(header):
            if idx < len(parts):
                row[col] = parts[idx]
            else:
                row[col] = ""
        rows.append(row)
    return rows


def _booknlp_resolve_token_locator(
    tokens: list[dict[str, str]],
    *,
    start_token: str,
    end_token: str,
) -> str:
    """Return a ``raw_idea:L1:C<onset>-<offset>`` locator from token rows.

    Uses the first row matching ``start_token`` for ``byte_onset`` and the
    last row matching ``end_token`` for ``byte_offset``. Missing or
    non-numeric values fall back to the token ids themselves. Returns an
    empty string when no usable rows are present.
    """
    if not tokens:
        return ""
    start_row: dict[str, str] | None = None
    end_row: dict[str, str] | None = None
    for row in tokens:
        if start_row is None and row.get("token_ID_within_document", "") == start_token:
            start_row = row
        if row.get("token_ID_within_document", "") == end_token:
            end_row = row

    if start_row is None or end_row is None:
        return ""

    onset = start_row.get("byte_onset", "").strip()
    offset = end_row.get("byte_offset", "").strip()
    if not onset.isdigit() or not offset.isdigit():
        return ""

    return f"raw_idea:L1:C{onset}-{offset}"


def _booknlp_parse_quotes_file(path: Any) -> list[dict[str, str]]:
    """Parse a BookNLP ``.quotes`` file into a list of quote row dicts.

    The quotes file is a TSV with a header row
    (``quote_start``, ``quote_end``, ``mention_start``, ``mention_end``,
    ``mention_phrase``, ``char_id``, ``quote``). Malformed rows are
    silently skipped. The parser never raises. Returns an empty list when
    the file is missing, unreadable, or contains only a header.
    """
    rows: list[dict[str, str]] = []
    if not isinstance(path, str) or not path:
        return rows
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return rows
    if not lines:
        return rows
    header = [col.strip() for col in lines[0].rstrip("\n").split("\t")]
    for raw_line in lines[1:]:
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < len(header):
            continue
        row: dict[str, str] = {}
        for idx, col in enumerate(header):
            if idx < len(parts):
                row[col] = parts[idx]
            else:
                row[col] = ""
        rows.append(row)
    return rows


def _booknlp_make_entity_finding(
    *,
    label: str,
    cat: str,
    ner_prop: str,
    coref: str,
    raw_text: str,
    source_locator: str,
    sentence: str,
) -> dict[str, Any] | None:
    """Build a T007-shaped BookNLP entity finding dict.

    Returns ``None`` when the inputs cannot be turned into a T007-compatible
    finding (empty label, unsupported category, unsafe claim/excerpt, or
    truth-labeled claim). This is a defense-in-depth safety helper. The
    T007 ``validate_local_nlp_fixture_envelope`` is the authoritative
    downstream validator.
    """
    candidate_type = _booknlp_entity_candidate_type_from_category(cat)
    if candidate_type is None:
        return None
    safe_label = label.strip()
    if not safe_label:
        return None
    if safe_label.lower() in _OMI_BOOKNLP_LIVE_SKIP_ENTITY_TEXTS:
        return None
    if len(safe_label) > 240:
        return None

    safe_excerpt = _booknlp_safe_text_excerpt(
        sentence, max_chars=_OMI_LIVE_BOOKNLP_MAX_EVIDENCE_CHARS
    )
    if not safe_excerpt:
        return None
    if is_prose_like_text(safe_excerpt):
        return None
    if is_truth_label(safe_excerpt):
        return None

    claim = (
        f"BookNLP entity candidate: {safe_label} ({ner_prop or 'N/A'}/"
        f"{cat}) in COREF cluster {coref or 'N/A'}"
    )
    if is_prose_like_text(claim):
        return None
    if is_truth_label(claim):
        return None

    raw_finding_id = (
        f"booknlp-live::{candidate_type}::{safe_label}::{source_locator}"
    )

    return {
        "raw_finding_id": raw_finding_id,
        "finding_type": cat.lower(),
        "booknlp_type": cat.lower(),
        "candidate_type": candidate_type,
        "label": safe_label,
        "text": safe_label,
        "entity_text": safe_label,
        "extracted_claim": claim,
        "claim": claim,
        "evidence": [
            {
                "source_excerpt": safe_excerpt,
                "source_locator": source_locator,
            }
        ],
        "source_locator": source_locator,
        "provenance": {
            "tool_source": "booknlp",
            "adapter": "booknlp",
            "support": "BookNLP live support only",
        },
        "source_adapter": "booknlp",
        "support_label": "BookNLP live support only",
        "confidence": "BookNLP live support only",
        "owner_decision": {
            "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
            "approved": False,
        },
        "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
        "booknlp_ner_prop": ner_prop,
        "booknlp_coref": coref,
        "raw_text": _booknlp_safe_text_excerpt(
            raw_text, max_chars=_OMI_LIVE_BOOKNLP_MAX_EVIDENCE_CHARS
        ),
    }


def _booknlp_make_quote_finding(
    *,
    quote_text: str,
    mention_phrase: str,
    char_id: str,
    source_locator: str,
) -> dict[str, Any] | None:
    """Build a T007-shaped BookNLP quote attribution finding dict.

    BookNLP quote rows may carry a ``char_id`` (e.g. ``42``) and a
    ``mention_phrase`` (e.g. ``he``). This helper emits a
    ``diagnostic_question``/``relationship``-style finding only when the
    quote text, mention phrase, and speaker id are all safe. It does NOT
    treat the coref/char_id as canon or truth.
    """
    safe_quote = _booknlp_safe_text_excerpt(
        quote_text, max_chars=_OMI_LIVE_BOOKNLP_MAX_EVIDENCE_CHARS
    )
    if not safe_quote:
        return None
    if is_prose_like_text(safe_quote):
        return None
    if is_truth_label(safe_quote):
        return None

    safe_mention = _booknlp_safe_text_excerpt(
        mention_phrase, max_chars=80
    )
    if not safe_mention:
        return None
    if is_prose_like_text(safe_mention):
        return None
    if is_truth_label(safe_mention):
        return None

    safe_char_id = char_id.strip() if isinstance(char_id, str) else ""
    if not safe_char_id:
        return None
    if not safe_char_id.isalnum():
        return None
    if len(safe_char_id) > 16:
        return None

    claim = (
        f"BookNLP dialogue attribution candidate: quote attributed to "
        f"mention '{safe_mention}' (char_id={safe_char_id})"
    )
    if is_prose_like_text(claim):
        return None
    if is_truth_label(claim):
        return None

    raw_finding_id = (
        f"booknlp-live::quote::{safe_char_id}::{source_locator}"
    )

    return {
        "raw_finding_id": raw_finding_id,
        "finding_type": "quote_attribution",
        "booknlp_type": "quote_attribution",
        "candidate_type": "diagnostic_question",
        "label": "BookNLP dialogue attribution",
        "text": safe_quote,
        "extracted_claim": claim,
        "claim": claim,
        "evidence": [
            {
                "source_excerpt": safe_quote,
                "source_locator": source_locator,
            }
        ],
        "source_locator": source_locator,
        "provenance": {
            "tool_source": "booknlp",
            "adapter": "booknlp",
            "support": "BookNLP live support only",
        },
        "source_adapter": "booknlp",
        "support_label": "BookNLP live support only",
        "confidence": "BookNLP live support only",
        "owner_decision": {
            "decision": OMI_FINDING_OWNER_DECISION_DEFAULT,
            "approved": False,
        },
        "review_status": OMI_FINDING_REVIEW_STATUS_DEFAULT,
        "booknlp_char_id": safe_char_id,
        "booknlp_mention_phrase": safe_mention,
    }


def _booknlp_live_result_to_envelope(
    *,
    entities: list[dict[str, str]],
    quotes: list[dict[str, str]],
    tokens: list[dict[str, str]],
) -> dict[str, Any]:
    """Convert parsed BookNLP output into the T007 fixture envelope shape.

    The converter is intentionally conservative. It only emits candidate
    findings when the BookNLP row carries a non-empty ``text``/``cat``
    pair (entities) or a non-empty ``quote`` + ``mention_phrase`` +
    ``char_id`` triple (quotes). The resulting envelope carries the T007
    ``omi_booknlp_local_nlp_extraction.v1`` schema version and runs
    through ``validate_local_nlp_fixture_envelope`` downstream. Unsafe
    or malformed rows are skipped at the item level; if every row is
    unsafe, the converter returns ``failed_closed`` with an empty
    findings list.
    """
    base_explanation = (
        "Live BookNLP adapter bridged the OMI orchestrator to "
        "booknlp.booknlp.BookNLP, wrote the owner raw idea to a temporary "
        ".txt file, ran BookNLP against a temporary output directory, and "
        "converted the parsed .entities / .quotes / .tokens output into "
        "the existing T007 omi_booknlp_local_nlp_extraction.v1 envelope "
        "shape. The T007 fixture validator remains authoritative."
    )
    provenance = {
        "tool_source": "booknlp",
        "adapter": "booknlp",
        "support": "BookNLP live support only",
    }

    findings: list[dict[str, Any]] = []

    for row in entities:
        if len(findings) >= _OMI_LIVE_BOOKNLP_MAX_FINDINGS:
            break
        label = row.get("text", "")
        cat = row.get("cat", "")
        ner_prop = cat.split("_", 1)[0] if "_" in cat else ""
        coref = row.get("COREF", "")
        start_token = row.get("start_token", "")
        end_token = row.get("end_token", "")
        source_locator = _booknlp_resolve_token_locator(
            tokens, start_token=start_token, end_token=end_token
        )
        if not source_locator:
            source_locator = _booknlp_safe_locator(
                row,
                fallback=f"raw_idea:L1:C{token_id_for_locator(start_token)}-"
                f"{token_id_for_locator(end_token)}",
            )
        sentence = ""
        if tokens:
            for tok in tokens:
                tok_id = tok.get("token_ID_within_document", "")
                if tok_id == start_token:
                    sentence_word = tok.get("word", "")
                    if sentence_word:
                        sentence = sentence_word
                        break
        finding = _booknlp_make_entity_finding(
            label=label,
            cat=cat,
            ner_prop=ner_prop,
            coref=coref,
            raw_text=label,
            source_locator=source_locator,
            sentence=sentence,
        )
        if finding is not None:
            findings.append(finding)

    for row in quotes:
        if len(findings) >= _OMI_LIVE_BOOKNLP_MAX_FINDINGS:
            break
        quote_text = row.get("quote", "")
        mention_phrase = row.get("mention_phrase", "")
        char_id = row.get("char_id", "")
        start_token = row.get("quote_start", "")
        end_token = row.get("quote_end", "")
        source_locator = _booknlp_resolve_token_locator(
            tokens, start_token=start_token, end_token=end_token
        )
        if not source_locator:
            source_locator = _booknlp_safe_locator(
                row,
                fallback=f"raw_idea:L1:C{start_token}-{end_token}",
            )
        finding = _booknlp_make_quote_finding(
            quote_text=quote_text,
            mention_phrase=mention_phrase,
            char_id=char_id,
            source_locator=source_locator,
        )
        if finding is not None:
            findings.append(finding)

    if not findings:
        return {
            "schema_version": OMI_BOOKNLP_SCHEMA_VERSION,
            "adapter": "booknlp",
            "status": "failed_closed",
            "explanation": (
                base_explanation
                + " Parsed .entities/.quotes rows carried no safe evidence-"
                "backed candidate text after the T017B safety boundary "
                "filtered empty/malformed/unsafe rows. Free-form BookNLP "
                "support, referential gender, and coreference/alias "
                "evidence-only handling are deferred; failing closed with "
                "no findings."
            ),
            "provenance": provenance,
            "findings": [],
        }

    return {
        "schema_version": OMI_BOOKNLP_SCHEMA_VERSION,
        "adapter": "booknlp",
        "status": "succeeded",
        "explanation": (
            base_explanation
            + f" Converted {len(findings)} candidate-only findings from "
            "the parsed BookNLP .entities / .quotes rows into the T007 "
            "envelope; existing T007 validator remains authoritative."
        ),
        "provenance": provenance,
        "findings": findings,
    }


def _booknlp_entity_result_to_envelope(
    entities: list[dict[str, str]],
    tokens: list[dict[str, str]],
) -> dict[str, Any]:
    """Convert parsed BookNLP ``.entities`` (+ ``.tokens``) output to envelope.

    Quote attribution is intentionally excluded from this helper. It is
    used by the live runner when the parsed BookNLP output carries no
    attributable quote rows. The full envelope helper
    ``_booknlp_live_result_to_envelope`` combines both kinds of rows.
    """
    return _booknlp_live_result_to_envelope(
        entities=entities,
        quotes=[],
        tokens=tokens,
    )


def token_id_for_locator(token_id: str) -> str:
    """Return a safe token-id segment for fallback source locators.

    Returns ``"?"`` when the token id is missing or non-numeric. This is
    only used when the BookNLP ``.tokens`` file is unavailable and the
    runner must still produce a non-empty locator; the ``.tokens``-based
    locator is preferred whenever possible.
    """
    if isinstance(token_id, str) and token_id.strip().isdigit():
        return token_id.strip()
    return "?"


def _filter_state_dict_for_booknlp_compat(
    state_dict: Any,
) -> tuple[Any, tuple[str, ...]]:
    """Return a copy of ``state_dict`` with only the known-tolerated keys removed.

    The shim is narrowly scoped to the T017C1 compatibility repair: it
    removes ONLY keys in :data:`_BOOKNLP_STATE_DICT_SHIM_TOLERATED_KEYS`
    (currently just ``bert.embeddings.position_ids``) from a state-dict-like
    dict and returns the modified copy plus the sorted tuple of removed
    keys. Non-dict inputs are returned unchanged with an empty removed-keys
    tuple, so wrapping ``torch.load`` remains safe even when BookNLP
    loads non-state-dict artifacts.

    Any other unexpected key in the returned state_dict is preserved
    exactly, so ``load_state_dict`` will still fail closed on
    strict=True for unrelated incompatibilities.
    """
    if not isinstance(state_dict, dict):
        return state_dict, ()
    removed: list[str] = []
    cleaned: dict[Any, Any] = {}
    for key, value in state_dict.items():
        if isinstance(key, str) and key in _BOOKNLP_STATE_DICT_SHIM_TOLERATED_KEYS:
            removed.append(key)
            continue
        cleaned[key] = value
    if not removed:
        return state_dict, ()
    return cleaned, tuple(sorted(removed))


def _booknlp_state_dict_shim_install() -> tuple[Any, Any]:
    """Install a narrow ``torch.load`` wrapper for the BookNLP constructor.

    Returns ``(original_torch_load, (torch_module, original_load_name))``
    so the caller can call :func:`_booknlp_state_dict_shim_uninstall`
    with the same pair. The wrapper preserves the original
    ``torch.load`` callable's behavior and only filters the single
    known-incompatible non-trainable key from returned state_dict-like
    dicts. Non-state-dict returns pass through unchanged.

    The shim is fail-closed: any unexpected error inside the wrapper
    re-raises, the runner fails closed, and the test suite proves the
    shim does not silently swallow other unexpected state-dict keys.
    """
    import torch  # local import: orchestrator is torch-free at import time

    original_load = torch.load

    def _wrapped(*args: Any, **kwargs: Any) -> Any:
        result = original_load(*args, **kwargs)
        return _filter_state_dict_for_booknlp_compat(result)[0]

    torch.load = _wrapped
    return original_load, torch


def _booknlp_state_dict_shim_uninstall(
    original_load: Any,
    torch_module: Any,
) -> None:
    """Restore the original ``torch.load`` after the BookNLP constructor."""
    try:
        torch_module.load = original_load
    except (AttributeError, TypeError):
        pass


def _booknlp_construct_with_state_dict_shim(
    language: str,
    model_params: dict[str, Any],
) -> Any:
    """Construct ``BookNLP(language, model_params)`` under the T017C1 shim.

    The wrapper installs a narrow ``torch.load`` shim for the duration of
    the constructor only, then restores the original. The shim removes
    ONLY ``bert.embeddings.position_ids`` from any returned state_dict;
    any other unexpected key is preserved and still triggers a
    ``strict=True`` failure. The shim is restored even on construction
    failure.
    """
    from booknlp.booknlp import BookNLP  # lazy import (runner-only)

    original_load, torch_module = _booknlp_state_dict_shim_install()
    try:
        return BookNLP(language, model_params)
    finally:
        _booknlp_state_dict_shim_uninstall(original_load, torch_module)


def _build_booknlp_live_runner(
    *,
    adapter_config: dict[str, Any] | None = None,
) -> Callable[..., dict[str, Any]]:
    """Build a live BookNLP adapter runner behind explicit runtime flags.

    The runner:

    - Imports ``booknlp.booknlp.BookNLP`` lazily (never at module import
      time and never when live flags are disabled).
    - Writes the owner-authored ``raw_idea`` text to a temporary input
      ``.txt`` file under a temporary directory. The book id is the
      deterministic ``omi_booknlp_input`` token; the runner does NOT use
      any owner-authored text as a filename or book id.
    - Calls ``BookNLP("en", model_params).process(input_file, output_dir,
      book_id)`` with conservative CPU-first model params
      (``pipeline="entity,quote,supersense,event"``, ``model="small"``)
      unless ``OMI_LIVE_BOOKNLP_MODEL`` / ``OMI_LIVE_BOOKNLP_PIPELINE``
      override them.
    - Reads the temporary ``.entities``, ``.quotes``, and ``.tokens``
      files written by BookNLP. No BookNLP output is written outside
      the temporary directory; the temporary directory is cleaned up
      after processing.
    - Parses only evidence-backed rows (entity ``text`` + ``cat``,
      quote ``quote`` + ``mention_phrase`` + ``char_id``) and converts
      them into the existing T007
      ``omi_booknlp_local_nlp_extraction.v1`` envelope shape.
    - Validates the converted envelope through
      ``validate_local_nlp_fixture_envelope``. The T007 validator
      remains authoritative; any T007 validation failure fails the
      runner closed with no findings.
    - Fails closed on ``ImportError``, ``OSError`` (BookNLP package
      missing or model files missing), runtime processing exception,
      empty/malformed raw idea, or malformed BookNLP output.
    - The runner never persists raw BookNLP output, never mutates
      Memory/Canon, never creates promotion records, never runs
      apply-promotion, and never generates story prose.

    The caller (``_resolve_adapter_runner``) must check env flags before
    building this runner. This runner does not re-check flags.
    """
    if not isinstance(adapter_config, dict) and adapter_config is not None:
        raise ValueError("adapter_config must be a dict or None")

    def _runner(
        *,
        project_name: str,
        raw_idea: str,
        source_idea_id: str | None,
    ) -> dict[str, Any]:
        _ = project_name
        _ = source_idea_id

        if not isinstance(raw_idea, str) or not raw_idea.strip():
            return {
                "adapter": "booknlp",
                "state": "empty",
                "explanation": (
                    "Live BookNLP runner received empty raw idea text; "
                    "no entities or quotes to extract."
                ),
                "candidates": [],
            }

        raw_text = raw_idea.strip()

        model_name = os.environ.get(
            _OMI_LIVE_BOOKNLP_MODEL_ENV, _OMI_LIVE_BOOKNLP_MODEL_DEFAULT
        )
        if not isinstance(model_name, str) or not model_name.strip():
            model_name = _OMI_LIVE_BOOKNLP_MODEL_DEFAULT
        if model_name not in {"small", "big", "custom"}:
            model_name = _OMI_LIVE_BOOKNLP_MODEL_DEFAULT

        pipeline_value = os.environ.get(
            _OMI_LIVE_BOOKNLP_PIPELINE_ENV, _OMI_LIVE_BOOKNLP_PIPELINE_DEFAULT
        )
        if not isinstance(pipeline_value, str) or not pipeline_value.strip():
            pipeline_value = _OMI_LIVE_BOOKNLP_PIPELINE_DEFAULT
        safe_pipes: list[str] = []
        for raw_pipe in pipeline_value.split(","):
            pipe = raw_pipe.strip().lower()
            if pipe in {"entity", "event", "supersense", "quote", "coref"}:
                if pipe not in safe_pipes:
                    safe_pipes.append(pipe)
        if "entity" not in safe_pipes:
            safe_pipes.insert(0, "entity")
        safe_pipeline = ",".join(safe_pipes)

        model_params: dict[str, Any] = {
            "pipeline": safe_pipeline,
            "model": model_name,
        }

        tmp_dir_obj = tempfile.TemporaryDirectory(prefix="omi_booknlp_live_")
        tmp_dir = tmp_dir_obj.name
        input_path = os.path.join(tmp_dir, _OMI_LIVE_BOOKNLP_INPUT_FILENAME)
        output_dir = tmp_dir
        book_id = _OMI_LIVE_BOOKNLP_INPUT_BOOK_ID

        try:
            try:
                with open(input_path, "w", encoding="utf-8") as handle:
                    handle.write(raw_text)
                    if not raw_text.endswith("\n"):
                        handle.write("\n")
            except OSError as exc:
                return {
                    "adapter": "booknlp",
                    "state": "failed_closed",
                    "explanation": (
                        "Live BookNLP runner could not write the temporary "
                        f"input file: {type(exc).__name__}: {exc}. "
                        "Failing closed with no findings."
                    ),
                    "candidates": [],
                }

            try:
                # T017C1 narrow compatibility shim: install a torch.load
                # wrapper that drops ONLY ``bert.embeddings.position_ids``
                # from any returned state_dict-like dict, for the duration
                # of the BookNLP constructor only. Any other unexpected
                # key still triggers a strict=True failure. See
                # _booknlp_construct_with_state_dict_shim for details.
                booknlp_instance = _booknlp_construct_with_state_dict_shim(
                    "en", model_params
                )
                booknlp_instance.process(input_path, output_dir, book_id)
            except ImportError as exc:
                return {
                    "adapter": "booknlp",
                    "state": "unavailable",
                    "explanation": (
                        "Live BookNLP requested but the BookNLP Python "
                        f"package is not installed: {type(exc).__name__}: "
                        f"{exc}. Failing closed with no candidates."
                    ),
                    "candidates": [],
                }
            except OSError as exc:
                return {
                    "adapter": "booknlp",
                    "state": "unavailable",
                    "explanation": (
                        "Live BookNLP requested but the model assets or "
                        "temporary directory are not available/loadable: "
                        f"{type(exc).__name__}: {exc}. Failing closed with "
                        "no candidates."
                    ),
                    "candidates": [],
                }
            except Exception as exc:
                return {
                    "adapter": "booknlp",
                    "state": "failed_closed",
                    "explanation": (
                        "Live BookNLP runtime processing failed: "
                        f"{type(exc).__name__}: {exc}. Failing closed with "
                        "no candidates."
                    ),
                    "candidates": [],
                }

            entities_path = os.path.join(output_dir, f"{book_id}.entities")
            quotes_path = os.path.join(output_dir, f"{book_id}.quotes")
            tokens_path = os.path.join(output_dir, f"{book_id}.tokens")

            entities_rows = _booknlp_parse_entities_file(entities_path)
            quotes_rows = _booknlp_parse_quotes_file(quotes_path)
            tokens_rows = _booknlp_parse_tokens_file(tokens_path)

            if not entities_rows and not quotes_rows:
                return {
                    "adapter": "booknlp",
                    "state": "empty",
                    "explanation": (
                        "Live BookNLP produced no parseable .entities or "
                        ".quotes rows. Failing closed with no findings."
                    ),
                    "candidates": [],
                }

            envelope = _booknlp_live_result_to_envelope(
                entities=entities_rows,
                quotes=quotes_rows,
                tokens=tokens_rows,
            )
        finally:
            try:
                tmp_dir_obj.cleanup()
            except OSError:
                pass

        try:
            validated = validate_local_nlp_fixture_envelope(
                envelope,
                adapter_name="booknlp",
            )
        except ValueError as exc:
            return {
                "adapter": "booknlp",
                "state": "failed_closed",
                "explanation": (
                    "Live BookNLP converted envelope failed T007 "
                    f"validation: {exc}. Failing closed with no findings."
                ),
                "candidates": [],
            }

        env_status = validated["status"]
        if env_status == "succeeded":
            state = "succeeded" if validated["findings"] else "empty"
        else:
            state = env_status

        return {
            "adapter": "booknlp",
            "state": state,
            "explanation": (
                validated["explanation"]
                or "Live BookNLP local NLP extraction completed."
            ),
            "candidates": validated["findings"],
        }

    return _runner


def _adapter_config_scene_id(
    adapter_config: dict[str, Any] | None,
) -> str | None:
    """Return the explicit ``scene_id`` from ``adapter_config`` if any.

    The orchestrator entrypoint stores the explicit
    ``story_check_scene_id`` kwarg on ``adapter_config`` (a dict) under the
    key ``"story_check_scene_id"``. Non-string, blank, or missing values
    return ``None`` so the caller can fall back to the env var.
    """
    if not isinstance(adapter_config, dict):
        return None
    value = adapter_config.get("story_check_scene_id")
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


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

    T006/T007/T008/T009 extension-point behavior:

    - If an explicit ``adapter_runners[adapter]`` callable was supplied by
      the caller, return it. The caller is responsible for honoring the
      no-live-call safety contract (T006 callers pass mock/fixture runners
      only; the orchestrator never imports or invokes a live Ollama client).
    - If ``adapter`` is ``ollama_model``, ``story_check``, ``booknlp``,
      ``spacy``, ``ncp``, ``subtxt``, or ``dramatica_flow`` AND
      ``adapter_fixture_outputs`` carries a matching entry, return a runner
      that produces a validated adapter envelope from that fixture. The
      fixture may be either a parsed JSON object (dict) or a JSON string; both
      forms go through the strict envelope validator and fail closed on any
      invalid or unsafe output. Fixture paths are the only paths that let
      these adapters succeed in tests.
    - T014C/T015C/T016C/T017B/T018B live adapter branches (each gated by
      its own runtime env flags) may return a live runner when the
      corresponding ``adapter`` is requested, no fixture was supplied,
      and the live flags are all enabled. Each live branch is fail-closed
      on missing/unsafe input. T018B specifically requires an explicit
      ``OMI_LIVE_NCP_INPUT_PATH`` pointing to an allowlisted owner-selected
      NCP JSON file.
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
    if adapter in {
        "ollama_model",
        "story_check",
        "booknlp",
        "spacy",
        "ncp",
        "subtxt",
        "dramatica_flow",
    }:
        if adapter_fixture_outputs is not None:
            if not isinstance(adapter_fixture_outputs, dict):
                raise ValueError(
                    "adapter_fixture_outputs must be a dict[str, Any]"
                )
            if adapter in adapter_fixture_outputs:
                if adapter == "ollama_model":
                    return _build_ollama_model_fixture_runner(
                        adapter_fixture_outputs[adapter],
                        adapter_config=adapter_config,
                    )
                if adapter == "story_check":
                    return _build_story_check_fixture_runner(
                        adapter_fixture_outputs[adapter],
                        adapter_config=adapter_config,
                    )
                if adapter in OMI_CONTEXT_ADAPTER_NAMES:
                    return _build_context_adapter_fixture_runner(
                        adapter,
                        adapter_fixture_outputs[adapter],
                        adapter_config=adapter_config,
                    )
                return _build_local_nlp_fixture_runner(
                    adapter,
                    adapter_fixture_outputs[adapter],
                    adapter_config=adapter_config,
                )
        # T014C: live spaCy path behind explicit env flags.
        if adapter == "spacy":
            env = os.environ
            if (
                _env_bool(env, _OMI_LIVE_TOOLS_ENABLED_ENV)
                and _env_bool(env, _OMI_LIVE_SPACY_ENABLED_ENV)
                and not _env_bool(env, _OMI_LIVE_SPACY_BLOCKED_ENV)
            ):
                return _build_spacy_live_runner(
                    adapter_config=adapter_config,
                )
        # T015C: live Ollama path behind explicit env flags.
        if adapter == "ollama_model":
            env = os.environ
            if (
                _env_bool(env, _OMI_LIVE_TOOLS_ENABLED_ENV)
                and _env_bool(env, _OMI_LIVE_OLLAMA_ENABLED_ENV)
                and not _env_bool(env, _OMI_LIVE_OLLAMA_BLOCKED_ENV)
            ):
                return _build_ollama_model_live_runner(
                    adapter_config=adapter_config,
                )
        # T016C: live Story Check path behind explicit env flags. Bridges
        # the OMI orchestrator to the existing in-repo
        # ``backend.analysis_engine.run_story_check`` callable surface and
        # converts the legacy rich-Story-Check response into the existing
        # T008 ``omi_story_check_diagnostic_handoff.v1`` envelope shape.
        if adapter == "story_check":
            env = os.environ
            if (
                _env_bool(env, _OMI_LIVE_TOOLS_ENABLED_ENV)
                and _env_bool(env, _OMI_LIVE_STORY_CHECK_ENABLED_ENV)
                and not _env_bool(env, _OMI_LIVE_STORY_CHECK_BLOCKED_ENV)
            ):
                return _build_story_check_live_runner(
                    adapter_config=adapter_config,
                )
        # T017B: live BookNLP path behind explicit env flags. The runner
        # imports ``booknlp.booknlp.BookNLP`` lazily, writes the owner raw
        # idea to a temporary file, runs BookNLP against a temporary
        # output directory, and converts parsed ``.entities`` /
        # ``.quotes`` / ``.tokens`` rows into the existing T007
        # ``omi_booknlp_local_nlp_extraction.v1`` envelope shape. The T007
        # ``validate_local_nlp_fixture_envelope`` is the authoritative
        # downstream validator. The runner does NOT persist raw BookNLP
        # output, mutate Memory/Canon, create promotion records, run
        # apply-promotion, or generate story prose. T017C must later
        # perform manual real BookNLP processing on owner-authored text
        # to prove the live BookNLP MVP path.
        if adapter == "booknlp":
            env = os.environ
            if (
                _env_bool(env, _OMI_LIVE_TOOLS_ENABLED_ENV)
                and _env_bool(env, _OMI_LIVE_BOOKNLP_ENABLED_ENV)
                and not _env_bool(env, _OMI_LIVE_BOOKNLP_BLOCKED_ENV)
            ):
                return _build_booknlp_live_runner(
                    adapter_config=adapter_config,
                )
        # T018B: live NCP candidate-import validation path behind explicit
        # env flags. The runner reads the owner-selected NCP JSON file
        # pointed to by ``OMI_LIVE_NCP_INPUT_PATH`` (explicit, allowlisted
        # path only), performs a minimal Python-side schema/readiness
        # check, and maps a small, evidence-backed subset of NCP fields
        # into the existing T009 ``omi_ncp_context_handoff.v1`` envelope
        # shape through ``validate_context_adapter_fixture_envelope``. The
        # T009 validator remains authoritative. The runner does NOT
        # auto-scan project data, does NOT walk ``projects/``, does NOT
        # run ``npm install``/``npm audit fix``/``npm run validate:file``
        # over project data, does NOT start a Node server, does NOT
        # mutate ``.external_sources/``, does NOT mutate Memory/Canon,
        # does NOT create promotion records, does NOT run apply-promotion,
        # and does NOT generate story prose. T018C must later perform
        # manual real NCP validation against an owner-selected NCP JSON
        # file to prove the live NCP MVP path.
        if adapter == "ncp":
            env = os.environ
            if (
                _env_bool(env, _OMI_LIVE_TOOLS_ENABLED_ENV)
                and _env_bool(env, _OMI_LIVE_NCP_ENABLED_ENV)
                and not _env_bool(env, _OMI_LIVE_NCP_BLOCKED_ENV)
            ):
                return _build_ncp_live_runner(
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
    story_check_scene_id: str | None = None,
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
        When True, fused evidence-backed findings may be persisted as
        pending OMI candidate records through the existing candidate-first
        storage path. Persistence requires a valid source OMI idea and raw
        idea snapshot match; otherwise the orchestrator returns a
        non-persistence status with zero writes.
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
        ``"spacy"`` fixtures; T008 honors ``"story_check"`` diagnostic
        fixtures; T009 honors ``"ncp"``, ``"subtxt"``, and
        ``"dramatica_flow"`` diagnostic/context fixtures. Strict schema
        validation, no-prose guard, no-truth-label guard, evidence/
        source-locator/provenance requirements, no Memory/Canon mutation, no
        promotion/apply-promotion, and fail-closed behavior all apply. The
        orchestrator never calls a live Ollama, Story Check, BookNLP, spaCy,
        NCP, Subtxt, or dramatica-flow runtime and never reads environment
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
        - ``fusion_contract``: dict of fusion field names -> null.
        - ``fusion_summary``: deterministic counts for T010 fusion/dedupe/
          conflict/uncertainty annotations.
        - ``persisted_candidate_ids``: list[str] (empty unless persistence ran).
        - ``persistence_status``: persistence boundary outcome.
        - ``persistence_explanation``: non-empty persistence explanation.
        - ``safety``: static orchestrator safety envelope.

    Persistence boundary:
      Fused findings may persist only as candidate-only OMI review records
      when ``persist_candidates`` is True and source context is sufficient.
      AI/tool adapter outputs are candidate-only evidence and never mutate
      Memory/Canon, create promotion records, call apply-promotion, or write
      canon. No real model/tool calls occur.

    Fail-closed behavior:
      Empty raw idea input -> ``empty`` with explanation and zero writes.
      Non-string raw idea input raises ``ValueError`` (treated as fatal
      by callers). Owner-authored raw idea text is accepted as analyzable
      data even when it looks like prose; the prose guard is intentionally
      NOT applied to owner input. The prose guard remains strict on
      AI/tool/model ``extracted_claim`` output and on forbidden envelope
      field names, so the model can never smuggle generated prose,
      rewrites, continuations, outlines, drafts, polish, expansions,
      imitations, revisions, truth/canon/approval claims, Memory/Canon
      mutation requests, promotion records, or apply-promotion
      instructions through the orchestrator boundary.
      Unknown adapter identities, malformed normalized findings,
      prose-shaped ``extracted_claim`` output, truth-labeled support,
      or auto-approval all raise ``ValueError`` (treated as fatal by
      callers).
    """
    if not isinstance(project_name, str) or not project_name.strip():
        raise ValueError("OMI orchestrator project_name must be a non-empty string")
    project_name = project_name.strip()

    if not isinstance(raw_idea, str):
        raise ValueError("OMI orchestrator raw_idea must be a string")
    raw_idea_text = raw_idea.strip()

    if not isinstance(persist_candidates, bool):
        raise ValueError("OMI orchestrator persist_candidates must be a bool")

    if (
        story_check_scene_id is not None
        and (
            not isinstance(story_check_scene_id, str)
            or not story_check_scene_id.strip()
        )
    ):
        raise ValueError(
            "OMI orchestrator story_check_scene_id must be a non-empty string when provided"
        )

    effective_adapter_config: dict[str, Any] | None = adapter_config
    if isinstance(adapter_config, dict):
        merged_config: dict[str, Any] = dict(adapter_config)
    elif adapter_config is None:
        merged_config = {}
    else:
        merged_config = {}
    if story_check_scene_id is not None:
        merged_config["story_check_scene_id"] = story_check_scene_id.strip()
    if merged_config:
        effective_adapter_config = merged_config

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
    persistence_status = "not_requested"
    persistence_explanation = (
        "persist_candidates=False; fused findings were returned without "
        "candidate persistence."
    )
    new_candidate_ids: list[str] = []
    reused_candidate_ids: list[str] = []

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
            "fusion_summary": _fusion_zero_summary(),
            "persisted_candidate_ids": [],
            "persistence_status": (
                "no_candidates_persisted"
                if persist_candidates
                else "not_requested"
            ),
            "persistence_explanation": (
                "Empty raw idea; no findings or OMI candidates were persisted."
            ),
            "new_candidate_ids": [],
            "reused_candidate_ids": [],
            "safety": safety,
        }

    # Owner-authored raw idea text is accepted regardless of whether it
    # looks like prose. Owners legitimately capture scenes, beats, and
    # dialogue fragments as raw planning notes; the orchestrator treats
    # this text as untrusted input data to analyze, not as executable
    # instructions. The prose guard remains strict on AI/tool/model
    # ``extracted_claim`` output and on forbidden envelope field names
    # so the model can never smuggle generated prose, rewrites,
    # continuations, outlines, drafts, polish, expansions, imitations,
    # revisions, truth/canon/approval claims, Memory/Canon mutation
    # requests, promotion records, or apply-promotion instructions
    # through the orchestrator boundary.
    raw_idea_text = validate_owner_raw_idea_input(raw_idea_text)

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

        # All other adapters are stubbed by default unless a fixture/mock
        # runner is supplied. Live implementations remain out of scope here.
        runner = _resolve_adapter_runner(
            adapter,
            adapter_runners=adapter_runners,
            adapter_fixture_outputs=adapter_fixture_outputs,
            adapter_config=effective_adapter_config,
        )
        if runner is None:
            # No fixture/runner supplied -> adapters remain unavailable.
            if adapter == "ollama_model":
                unavailable_explanation = (
                    f"Adapter '{adapter}' requires either a T006 fixture "
                    f"via ``adapter_fixture_outputs`` or live Ollama env "
                    f"flags (OMI_LIVE_TOOLS_ENABLED + "
                    f"OMI_LIVE_OLLAMA_ENABLED). Neither was supplied. "
                    f"Returning 'unavailable' with no candidates."
                )
            elif adapter == "story_check":
                unavailable_explanation = (
                    f"Adapter '{adapter}' is available through the T008 "
                    f"{OMI_STORY_CHECK_SCHEMA_VERSION} fixture/mock "
                    f"diagnostic handoff contract only; no fixture was "
                    f"supplied via ``adapter_fixture_outputs``. The "
                    f"orchestrator does not perform live Story Check calls, "
                    f"does not import Story Check runtime code, and does not "
                    f"write Story Check output. Returning 'unavailable' with "
                    f"no candidates."
                )
            elif adapter in {"booknlp", "spacy"}:
                if adapter == "spacy":
                    unavailable_explanation = (
                        f"Adapter '{adapter}' requires either a T007 fixture "
                        f"via ``adapter_fixture_outputs`` or live spaCy env "
                        f"flags (OMI_LIVE_TOOLS_ENABLED + "
                        f"OMI_LIVE_SPACY_ENABLED). Neither was supplied. "
                        f"Returning 'unavailable' with no candidates."
                    )
                else:
                    unavailable_explanation = (
                        f"Adapter '{adapter}' requires either a T007 fixture "
                        f"via ``adapter_fixture_outputs`` or live BookNLP env "
                        f"flags (OMI_LIVE_TOOLS_ENABLED + "
                        f"OMI_LIVE_BOOKNLP_ENABLED, with "
                        f"OMI_LIVE_BOOKNLP_BLOCKED unset). Neither was "
                        f"supplied. The orchestrator does not perform live "
                        f"BookNLP calls by default and does not import or "
                        f"install BookNLP automatically. "
                        f"Returning 'unavailable' with no candidates."
                    )
            elif adapter in OMI_CONTEXT_ADAPTER_NAMES:
                runtime_name = _context_adapter_display_name(adapter)
                if adapter == "ncp":
                    unavailable_explanation = (
                        f"Adapter '{adapter}' is available through the T009 "
                        f"{OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER[adapter]} "
                        f"fixture/mock diagnostic/context handoff contract or "
                        f"the T018B live NCP candidate-import validation "
                        f"adapter; neither was supplied. T018B live NCP "
                        f"requires OMI_LIVE_TOOLS_ENABLED + "
                        f"OMI_LIVE_NCP_ENABLED, OMI_LIVE_NCP_BLOCKED unset, "
                        f"AND an explicit owner-selected "
                        f"{_OMI_LIVE_NCP_INPUT_PATH_ENV}. The orchestrator "
                        f"does not auto-scan project data, does not run "
                        f"``npm install``/``npm audit fix``/a Node server, "
                        f"and does not write NCP output outside the "
                        f"converted T009 envelope. Returning 'unavailable' "
                        f"with no candidates."
                    )
                else:
                    unavailable_explanation = (
                        f"Adapter '{adapter}' is available through the T009 "
                        f"{OMI_CONTEXT_SCHEMA_VERSION_BY_ADAPTER[adapter]} "
                        f"fixture/mock diagnostic/context handoff contract only; "
                        f"no fixture was supplied via ``adapter_fixture_outputs``. "
                        f"The orchestrator does not perform live {runtime_name} "
                        f"calls, does not import {runtime_name} runtime code, and "
                        f"does not write {runtime_name} output. Returning "
                        f"'unavailable' with no candidates."
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

    findings, fusion_summary = fuse_normalized_findings(findings)

    if persist_candidates:
        if findings:
            # T011 persistence: fused AI/tool findings can be written only as
            # pending OMI candidate records tied to an existing source idea.
            from backend import project_manager  # local import

            persistence = project_manager.persist_omi_tool_assisted_findings_as_candidates(
                project_name,
                raw_idea=raw_idea_text,
                source_idea_id=source_idea_id,
                findings=findings,
            )
            persisted_candidate_ids = list(
                persistence.get("persisted_candidate_ids", []) or []
            )
            new_candidate_ids = list(persistence.get("new_candidate_ids", []) or [])
            reused_candidate_ids = list(
                persistence.get("reused_candidate_ids", []) or []
            )
            persistence_status = str(
                persistence.get("persistence_status") or "no_candidates_persisted"
            )
            persistence_explanation = str(
                persistence.get("persistence_explanation")
                or "No AI/tool candidates were persisted."
            )
        else:
            persistence_status = "no_candidates_persisted"
            persistence_explanation = (
                "persist_candidates=True but no fused findings were available "
                "for candidate persistence."
            )
        explanation_parts.append(
            f"candidate persistence: status={persistence_status}; "
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
        "fusion_summary": fusion_summary,
        "persisted_candidate_ids": persisted_candidate_ids,
        "persistence_status": persistence_status,
        "persistence_explanation": persistence_explanation,
        "new_candidate_ids": new_candidate_ids,
        "reused_candidate_ids": reused_candidate_ids,
        "safety": safety,
    }
