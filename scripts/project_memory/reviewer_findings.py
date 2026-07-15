#!/usr/bin/env python3
"""Validate and normalize supplied specialized-reviewer findings.

This module performs exact structural, scope, binding, and evidence checks. It
does not invoke a model, decide semantic truth, or alter Plan Integrity state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any


AUTHORITY_CLASS = "generated_evidence"
AUTHORIZED_DOMAINS = (
    "backend_contracts",
    "frontend_ui",
    "test_coverage",
    "roadmap_consistency",
    "enrichment_accuracy",
    "decision_coherence",
)
RESULTS = (
    "CONCERN",
    "NO_CONCERN",
    "INSUFFICIENT_EVIDENCE",
    "CONFLICT",
    "OWNER_REVIEW_REQUIRED",
)
SEVERITIES = ("info", "warning", "error", "critical")
OWNER_DECISION_STATUSES = (
    "not_required",
    "accepted_recorded",
    "owner_pending",
    "unresolved",
)
SOURCE_CLASSES = (
    "authoritative",
    "accepted_evidence",
    "generated_evidence",
    "historical",
    "superseded",
    "uncertain",
    "owner_pending",
    "untrusted",
)
FRESHNESS_VALUES = ("current", "historical")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^review-finding-[0-9a-f]{20}$")
_SEVERITY_RANK = {name: index for index, name in enumerate(reversed(SEVERITIES))}

_REQUEST_FIELDS = {
    "repository_root",
    "expected_branch",
    "expected_full_commit",
    "reviewer_domain",
    "task_or_feature_scope",
    "maximum_file_scope",
    "allowed_source_classes",
    "protected_paths",
    "accepted_plan_integrity_report_path",
    "freshness_requirement",
    "historical_evidence_permission",
    "owner_decision_requirement",
}
_STATE_FIELDS = {
    "repository_root",
    "branch",
    "full_commit",
    "dirty",
    "staged",
}
_FINDING_FIELDS = {
    "finding_id",
    "content_type",
    "reviewer_domain",
    "rule_or_concern_id",
    "title",
    "bounded_claim",
    "result",
    "status",
    "severity",
    "blocking_recommendation",
    "affected_ids",
    "evidence_locators",
    "facts",
    "inferences",
    "uncertainty_or_conflicting_evidence",
    "owner_decision_status",
    "recommended_deterministic_follow_up",
    "authority_declaration",
}
_LOCATOR_FIELDS = {
    "path",
    "line_start",
    "line_end",
    "sha256",
    "authority_class",
    "freshness",
    "bound_commit",
}
_PROHIBITED_CONTENT_KEYS = {
    "confidence",
    "confidence_score",
    "probability",
    "story_prose",
    "prose",
    "narrative_text",
    "rewritten_story",
    "continued_story",
}
_PROHIBITED_CLAIM_PATTERNS = (
    re.compile(r"\b(this finding|reviewer output)\s+is\s+(authoritative|accepted|approved|canon)\b", re.I),
    re.compile(r"\btask\b.{0,80}\b(is|should be|must be)\s+(closed|complete|activated|active)\b", re.I),
    re.compile(r"\bautomatically\s+(mutate|update|change|activate|close|reorder|approve|accept|promote)\b", re.I),
    re.compile(r"\b(run|perform|execute)\s+apply[- ]promotion\b", re.I),
    re.compile(r"\b(write|mutate|update)\s+(the\s+)?(Memory/Canon|roadmap|registr(?:y|ies))\b", re.I),
)


class ReviewerFindingsError(ValueError):
    """A deterministic reviewer-finding contract violation."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise ReviewerFindingsError(code, detail)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("malformed_input", f"{name} must be an object")
    return value


def _require_exact_fields(value: dict[str, Any], expected: set[str], name: str) -> None:
    actual = set(value)
    if actual != expected:
        _fail("malformed_input", f"{name} fields differ: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")


def _require_nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("malformed_input", f"{name} must be a non-empty string")
    return value.strip()


def _safe_relative_path(value: Any, *, allow_directory_prefix: bool = False) -> str:
    if not isinstance(value, str) or not value or "\\" in value or os.path.isabs(value):
        _fail("unsafe_path", repr(value))
    if value.startswith("/") or (value.endswith("/") and not allow_directory_prefix):
        _fail("unsafe_path", value)
    candidate = value[:-1] if allow_directory_prefix and value.endswith("/") else value
    parts = PurePosixPath(candidate).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        _fail("unsafe_path", value)
    return value


def _in_scope(path: str, scopes: tuple[str, ...]) -> bool:
    return any(
        path == scope or (scope.endswith("/") and path.startswith(scope))
        for scope in scopes
    )


def _is_protected(path: str, protected: tuple[str, ...]) -> bool:
    return any(
        path == item.rstrip("/") or path.startswith(item.rstrip("/") + "/")
        for item in protected
    )


def _load_json(path: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("missing_or_malformed_evidence", f"{name}: {exc}")
    return _require_object(value, name)


def _validate_plan_integrity_report(
    root: Path,
    relative_path: str,
    *,
    expected_branch: str,
    expected_commit: str,
    protected: tuple[str, ...],
) -> None:
    relative_path = _safe_relative_path(relative_path)
    if _is_protected(relative_path, protected):
        _fail("protected_path", relative_path)
    report_dir = root / relative_path
    if not report_dir.is_dir() or report_dir.is_symlink():
        _fail("missing_or_malformed_evidence", relative_path)
    metadata = _load_json(report_dir / "run-metadata.json", "Plan Integrity run metadata")
    readiness = _load_json(report_dir / "readiness.json", "Plan Integrity readiness")
    if metadata.get("authority_class") != AUTHORITY_CLASS:
        _fail("authority_violation", "Plan Integrity report must be generated_evidence")
    if metadata.get("branch") != expected_branch or metadata.get("bound_commit") != expected_commit:
        _fail("stale_binding", relative_path)
    if readiness.get("result") not in {"READY", "READY_WITH_ADVISORIES"}:
        _fail("plan_integrity_blocked", str(readiness.get("result")))


def _validate_request(document: dict[str, Any], root: Path) -> tuple[dict[str, Any], dict[str, Any], tuple[str, ...], tuple[str, ...]]:
    if set(document) != {"request", "repository_state", "findings"}:
        _fail("malformed_input", "top-level fields must be request, repository_state, and findings")
    request = _require_object(document["request"], "request")
    state = _require_object(document["repository_state"], "repository_state")
    _require_exact_fields(request, _REQUEST_FIELDS, "request")
    _require_exact_fields(state, _STATE_FIELDS, "repository_state")

    requested_root = Path(_require_nonempty_string(request["repository_root"], "repository_root")).resolve()
    state_root = Path(_require_nonempty_string(state["repository_root"], "repository_state.repository_root")).resolve()
    if requested_root != root or state_root != root:
        _fail("repository_root_mismatch", f"expected {root}")
    branch = _require_nonempty_string(request["expected_branch"], "expected_branch")
    commit = _require_nonempty_string(request["expected_full_commit"], "expected_full_commit")
    if not _SHA40.fullmatch(commit):
        _fail("unbound_commit", commit)
    domain = request["reviewer_domain"]
    if domain not in AUTHORIZED_DOMAINS:
        _fail("unsupported_domain", repr(domain))
    _require_nonempty_string(request["task_or_feature_scope"], "task_or_feature_scope")
    if request["freshness_requirement"] != "current_clean_head":
        _fail("unsupported_freshness_requirement", repr(request["freshness_requirement"]))
    if not isinstance(request["historical_evidence_permission"], bool):
        _fail("malformed_input", "historical_evidence_permission must be boolean")
    if not isinstance(request["owner_decision_requirement"], bool):
        _fail("malformed_input", "owner_decision_requirement must be boolean")
    if state["branch"] != branch or state["full_commit"] != commit:
        _fail("stale_binding", "repository state does not match expected branch/full commit")
    if not isinstance(state["dirty"], bool) or not isinstance(state["staged"], bool):
        _fail("malformed_input", "dirty and staged must be boolean")
    if state["dirty"] or state["staged"]:
        _fail("unclean_input", "current_clean_head requires empty worktree and staging")

    scopes_value = request["maximum_file_scope"]
    if not isinstance(scopes_value, list) or not scopes_value:
        _fail("unsupported_scope", "maximum_file_scope must be a non-empty list")
    scopes = tuple(sorted({_safe_relative_path(item, allow_directory_prefix=True) for item in scopes_value}))
    protected_value = request["protected_paths"]
    if not isinstance(protected_value, list):
        _fail("malformed_input", "protected_paths must be a list")
    protected = tuple(sorted({_safe_relative_path(item, allow_directory_prefix=True) for item in protected_value}))
    if any(_is_protected(scope.rstrip("/"), protected) for scope in scopes):
        _fail("protected_path", "maximum_file_scope overlaps protected_paths")

    classes = request["allowed_source_classes"]
    if not isinstance(classes, list) or not classes or any(item not in SOURCE_CLASSES for item in classes):
        _fail("unsupported_source_class", repr(classes))
    request["allowed_source_classes"] = sorted(set(classes))
    request["maximum_file_scope"] = list(scopes)
    request["protected_paths"] = list(protected)
    _validate_plan_integrity_report(
        root,
        request["accepted_plan_integrity_report_path"],
        expected_branch=branch,
        expected_commit=commit,
        protected=protected,
    )
    return request, state, scopes, protected


def _validate_text_safety(finding: dict[str, Any]) -> None:
    prohibited_keys = set(finding) & _PROHIBITED_CONTENT_KEYS
    if prohibited_keys:
        _fail("prohibited_content", f"prohibited fields: {sorted(prohibited_keys)}")
    strings = [
        finding.get("title", ""),
        finding.get("bounded_claim", ""),
        finding.get("recommended_deterministic_follow_up", ""),
        *finding.get("facts", []),
        *finding.get("inferences", []),
        *finding.get("uncertainty_or_conflicting_evidence", []),
    ]
    combined = "\n".join(item for item in strings if isinstance(item, str))
    for pattern in _PROHIBITED_CLAIM_PATTERNS:
        if pattern.search(combined):
            _fail("prohibited_claim", pattern.pattern)


def _validate_string_list(value: Any, name: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        _fail("malformed_input", f"{name} must be {'a non-empty' if nonempty else 'a'} list")
    normalized = [_require_nonempty_string(item, name) for item in value]
    if len(normalized) != len(set(normalized)):
        _fail("malformed_input", f"{name} contains duplicates")
    return sorted(normalized)


def _validate_locator(
    locator: Any,
    *,
    root: Path,
    scopes: tuple[str, ...],
    protected: tuple[str, ...],
    allowed_classes: set[str],
    expected_commit: str,
    historical_permitted: bool,
) -> dict[str, Any]:
    item = _require_object(locator, "evidence locator")
    _require_exact_fields(item, _LOCATOR_FIELDS, "evidence locator")
    path = _safe_relative_path(item["path"])
    if not _in_scope(path, scopes):
        _fail("unsupported_scope", path)
    if _is_protected(path, protected):
        _fail("protected_path", path)
    full = root / path
    try:
        resolved = full.resolve(strict=True)
    except OSError as exc:
        _fail("missing_locator", f"{path}: {exc}")
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail("external_locator", path)
    if full.is_symlink() or not resolved.is_file():
        _fail("unsafe_locator", path)
    authority = item["authority_class"]
    if authority not in allowed_classes:
        _fail("unsupported_source_class", f"{path}: {authority!r}")
    freshness = item["freshness"]
    if freshness not in FRESHNESS_VALUES:
        _fail("stale_or_unbound_locator", f"{path}: {freshness!r}")
    bound_commit = item["bound_commit"]
    if not isinstance(bound_commit, str) or not _SHA40.fullmatch(bound_commit):
        _fail("unbound_commit", path)
    if freshness == "current" and bound_commit != expected_commit:
        _fail("stale_binding", path)
    if freshness == "historical" and not historical_permitted:
        _fail("historical_evidence_denied", path)
    digest = item["sha256"]
    actual_digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest) or digest != actual_digest:
        _fail("locator_hash_mismatch", path)
    start, end = item["line_start"], item["line_end"]
    if not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int) or isinstance(end, bool):
        _fail("malformed_locator", f"{path}: line range must be integers")
    try:
        line_count = len(resolved.read_text(encoding="utf-8").splitlines())
    except UnicodeError as exc:
        _fail("malformed_locator", f"{path}: {exc}")
    if start < 1 or end < start or end > line_count:
        _fail("malformed_locator", f"{path}:{start}-{end} outside 1-{line_count}")
    return {
        "path": path,
        "line_start": start,
        "line_end": end,
        "sha256": digest,
        "authority_class": authority,
        "freshness": freshness,
        "bound_commit": bound_commit,
    }


def deterministic_finding_id(finding: dict[str, Any]) -> str:
    """Return the stable ID for one already-normalized finding."""
    identity = {
        "reviewer_domain": finding["reviewer_domain"],
        "rule_or_concern_id": finding["rule_or_concern_id"],
        "title": finding["title"],
        "bounded_claim": finding["bounded_claim"],
        "affected_ids": finding["affected_ids"],
        "evidence_locations": [
            [item["path"], item["line_start"], item["line_end"]]
            for item in finding["evidence_locators"]
        ],
    }
    digest = hashlib.sha256(_canonical_json(identity).encode("utf-8")).hexdigest()[:20]
    return f"review-finding-{digest}"


def _normalize_finding(
    value: Any,
    *,
    request: dict[str, Any],
    root: Path,
    scopes: tuple[str, ...],
    protected: tuple[str, ...],
) -> dict[str, Any]:
    finding = _require_object(value, "finding")
    prohibited_keys = set(finding) & _PROHIBITED_CONTENT_KEYS
    if prohibited_keys:
        _fail("prohibited_content", f"prohibited fields: {sorted(prohibited_keys)}")
    actual_fields = set(finding)
    allowed_fields = _FINDING_FIELDS
    if actual_fields not in (allowed_fields, allowed_fields - {"finding_id"}):
        _fail("malformed_input", f"finding fields differ: {sorted(actual_fields ^ allowed_fields)}")
    if finding["content_type"] != "plan_integrity_review_finding":
        _fail("story_prose_rejected", "content_type must be plan_integrity_review_finding")
    if finding["reviewer_domain"] != request["reviewer_domain"]:
        _fail("unsupported_domain", repr(finding["reviewer_domain"]))
    if finding["result"] not in RESULTS or finding["status"] != "proposed":
        _fail("prohibited_status", f"{finding['result']!r}/{finding['status']!r}")
    if finding["severity"] not in SEVERITIES:
        _fail("malformed_input", f"unsupported severity {finding['severity']!r}")
    if not isinstance(finding["blocking_recommendation"], bool):
        _fail("malformed_input", "blocking_recommendation must be boolean")
    if finding["authority_declaration"] != AUTHORITY_CLASS:
        _fail("authority_violation", repr(finding["authority_declaration"]))
    for name in ("rule_or_concern_id", "title", "bounded_claim", "recommended_deterministic_follow_up"):
        finding[name] = _require_nonempty_string(finding[name], name)
    finding["affected_ids"] = _validate_string_list(finding["affected_ids"], "affected_ids", nonempty=True)
    finding["facts"] = _validate_string_list(finding["facts"], "facts", nonempty=True)
    finding["inferences"] = _validate_string_list(finding["inferences"], "inferences")
    finding["uncertainty_or_conflicting_evidence"] = _validate_string_list(
        finding["uncertainty_or_conflicting_evidence"],
        "uncertainty_or_conflicting_evidence",
    )
    if set(finding["facts"]) & set(finding["inferences"]):
        _fail("fact_inference_overlap", "facts and inferences must remain distinct")
    if finding["owner_decision_status"] not in OWNER_DECISION_STATUSES:
        _fail("malformed_input", "unsupported owner_decision_status")
    if request["owner_decision_requirement"] and finding["owner_decision_status"] != "accepted_recorded":
        _fail("owner_decision_required", finding["owner_decision_status"])
    locators = finding["evidence_locators"]
    if not isinstance(locators, list) or not locators:
        _fail("missing_evidence", finding["rule_or_concern_id"])
    finding["evidence_locators"] = sorted(
        (
            _validate_locator(
                item,
                root=root,
                scopes=scopes,
                protected=protected,
                allowed_classes=set(request["allowed_source_classes"]),
                expected_commit=request["expected_full_commit"],
                historical_permitted=request["historical_evidence_permission"],
            )
            for item in locators
        ),
        key=lambda item: (item["path"], item["line_start"], item["line_end"], item["authority_class"]),
    )
    _validate_text_safety(finding)
    expected_id = deterministic_finding_id(finding)
    supplied_id = finding.get("finding_id")
    if supplied_id is not None and (not isinstance(supplied_id, str) or not _ID.fullmatch(supplied_id) or supplied_id != expected_id):
        _fail("finding_id_mismatch", repr(supplied_id))
    finding["finding_id"] = expected_id
    return {key: finding[key] for key in sorted(_FINDING_FIELDS)}


def normalize_reviewer_findings(document: dict[str, Any], repo_root: str | Path) -> dict[str, Any]:
    """Validate and deterministically normalize a supplied reviewer document."""
    root = Path(repo_root).resolve(strict=True)
    document = _require_object(document, "document")
    request, state, scopes, protected = _validate_request(document, root)
    raw_findings = document["findings"]
    if not isinstance(raw_findings, list):
        _fail("malformed_input", "findings must be a list")
    findings = [
        _normalize_finding(
            item,
            request=request,
            root=root,
            scopes=scopes,
            protected=protected,
        )
        for item in raw_findings
    ]
    findings.sort(key=lambda item: (
        AUTHORIZED_DOMAINS.index(item["reviewer_domain"]),
        _SEVERITY_RANK[item["severity"]],
        item["rule_or_concern_id"],
        item["finding_id"],
    ))
    return {
        "schema_version": "1.0.0",
        "authority_class": AUTHORITY_CLASS,
        "bound_branch": state["branch"],
        "bound_commit": state["full_commit"],
        "reviewer_domain": request["reviewer_domain"],
        "finding_count": len(findings),
        "findings": findings,
        "t009_readiness_mutation_performed": False,
        "owner_decision_created": False,
        "semantic_truth_selected": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input", required=True, help="Supplied reviewer JSON document")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        document = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = normalize_reviewer_findings(document, args.repo_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ReviewerFindingsError) as exc:
        error = {"result": "BLOCKED", "error": str(exc)}
        print(json.dumps(error, indent=2, sort_keys=True) if args.json else error["error"])
        return 1
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
