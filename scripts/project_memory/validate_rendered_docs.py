#!/usr/bin/env python3
"""Semantic rendered-documentation validator for Project Memory.

Validates that rendered Markdown pages structurally and semantically match
the tracked normalized task registry.  Structural hashes alone are
insufficient; the rendered task state must converge with registry truth.

Uses only Python standard-library modules.  Deterministic and read-only.

Usage:
  python3 scripts/project_memory/validate_rendered_docs.py \
    --repo-root . \
    --snapshot-dir <SNAPSHOT_DIR> \
    --render-dir <RENDER_DIR> \
    --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def _bootstrap_direct_execution_import_path() -> None:
    """Make absolute project imports available only for direct script execution."""
    if __package__ not in (None, ""):
        return
    repository_root = str(Path(__file__).resolve().parents[2])
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)


_bootstrap_direct_execution_import_path()

RENDERED_PAGE_NAMES: tuple[str, ...] = (
    "index.md",
    "application-overview.md",
    "product-boundaries.md",
    "features.md",
    "capabilities.md",
    "current-roadmap.md",
    "remaining-work.md",
    "dependencies.md",
    "decisions.md",
    "assets.md",
    "evidence.md",
    "risks-and-open-questions.md",
    "convergence-findings.md",
    "technical-annex.md",
)

RESULT_PASS = "PASS"
RESULT_PASS_WITH_FINDINGS = "PASS_WITH_FINDINGS"
RESULT_BLOCKED = "BLOCKED"

_ALLOWED_RESULTS = frozenset([RESULT_PASS, RESULT_PASS_WITH_FINDINGS, RESULT_BLOCKED])

_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

_EXACT_GENERATED_EVIDENCE_BANNER = "# Generated Evidence — Not Project Authority"

_GENERATED_SUBJECT = (
    r"(?:(?:this|the)\s+)?(?:generated\s+)?"
    r"(?:page|render|snapshot|package|documentation|docs|output|publication)"
    r"|generated\s+evidence"
)

_FORBIDDEN_AUTHORITY_RULES: tuple[tuple[str, str, str, re.Pattern[str]], ...] = (
    (
        "generated_self_authority",
        "generated_evidence_self_authority_claim",
        "Generated evidence must not claim authoritative, project-authority, "
        "project-truth, or source-of-truth status.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b\s+"
            r"(?:is|are|becomes?|constitutes?|represents?|serves\s+as)\s+"
            r"(?:an?\s+|the\s+)?"
            r"(?:authoritative|project\s+authority|project\s+truth|"
            r"(?:(?:project|roadmap)\s+)?source\s+of\s+truth)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "generated_controls_task_status",
        "generated_evidence_controls_task_status",
        "Generated documentation must not control, determine, set, or govern roadmap/task status.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b[^.;|]{{0,80}}\b"
            r"(?:controls?|determines?|sets?|governs?)\s+(?:the\s+)?"
            r"(?:roadmap|task|project)\s+status\b",
            re.IGNORECASE,
        ),
    ),
    (
        "generated_overrides_tracked_sources",
        "generated_evidence_overrides_tracked_sources",
        "Generated evidence must not override or outrank tracked roadmap records or sources.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b[^.;|]{{0,80}}\b"
            r"(?:overrides?|supersedes?|outranks?|takes?\s+precedence\s+over)\s+"
            r"(?:the\s+)?(?:accepted\s+)?(?:tracked\s+)?"
            r"(?:roadmap|records?|sources?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "generated_resolves_owner_decisions",
        "generated_evidence_resolves_owner_decisions",
        "Generated output must not resolve owner decisions.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b[^.;|]{{0,80}}\b"
            r"resolves?\s+(?:the\s+)?owner\s+decisions?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "generated_establishes_canon",
        "generated_evidence_establishes_canon",
        "Generated output must not establish canon.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b[^.;|]{{0,80}}\b"
            r"establish(?:es)?\s+(?:the\s+)?canon\b",
            re.IGNORECASE,
        ),
    ),
    (
        "generated_approves_candidates",
        "generated_evidence_approves_candidates",
        "Generated output must not automatically approve or promote candidates.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b[^.;|]{{0,80}}\b"
            r"automatically\s+(?:approves?|promotes?)\s+(?:the\s+)?candidates?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "generated_equal_or_greater_authority",
        "generated_evidence_equal_or_greater_authority",
        "Generated evidence must not claim authority equal to or greater than tracked sources.",
        re.compile(
            rf"\b(?:{_GENERATED_SUBJECT})\b[^.;|]{{0,80}}\b"
            r"(?:has|holds|carries|possesses|is\s+assigned)\s+"
            r"(?:equal(?:\s+or\s+greater)?|equivalent|same|greater|higher)\s+authority\b",
            re.IGNORECASE,
        ),
    ),
)

_PM_TASK_ORDER: tuple[str, ...] = (
    "PHASE8-IMPL-026-T001",
    "PHASE8-IMPL-026-T002",
    "PHASE8-IMPL-026-T003",
    "PHASE8-IMPL-026-T004",
    "PHASE8-IMPL-026-T004A",
    "PHASE8-IMPL-026-T004B",
    "PHASE8-IMPL-026-T004C",
    "PHASE8-IMPL-026-T005",
)

_PM_PARENT = "PHASE8-IMPL-026"


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.rstrip("\n")


def _read_git_blob(repo_root: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=str(repo_root),
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"Snapshot-bound registry is unavailable: {path}: {detail}")
    return result.stdout


def _load_snapshot_bound_registries(
    repo_root: Path,
    snapshot_dir: Path,
    snapshot_bundle: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and hash-check normalized registries at the snapshot's bound commit."""
    if snapshot_bundle is None:
        from scripts.project_memory.render_docs import validate_snapshot_package

        snapshot_bundle = validate_snapshot_package(str(snapshot_dir), repo_root)

    snapshot = snapshot_bundle.get("snapshot", {})
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot package has malformed snapshot.json")
    bound_commit = snapshot.get("bound_commit", "")
    branch = snapshot.get("branch", "")
    registry_hashes = snapshot.get("registry_hashes")
    if not _GIT_SHA_RE.fullmatch(str(bound_commit)):
        raise ValueError("Snapshot package has invalid bound_commit")
    if not isinstance(branch, str) or not branch:
        raise ValueError("Snapshot package has invalid branch")
    if not isinstance(registry_hashes, dict) or not registry_hashes:
        raise ValueError("Snapshot package is missing registry_hashes")

    required_paths = (
        "docs/project-memory/registries/tasks.json",
        "docs/project-memory/registries/owner-decisions.json",
    )
    loaded: dict[str, Any] = {}
    for path in required_paths:
        expected_hash = registry_hashes.get(path)
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            raise ValueError(f"Snapshot registry hash missing or malformed: {path}")
        blob = _read_git_blob(repo_root, bound_commit, path)
        actual_hash = hashlib.sha256(blob).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Snapshot registry hash mismatch at bound commit: {path}")
        try:
            data = json.loads(blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Snapshot-bound registry is malformed: {path}: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("records"), list):
            raise ValueError(f"Snapshot-bound registry has invalid records: {path}")
        loaded[Path(path).name] = data

    head = _run_git(repo_root, ["rev-parse", "HEAD"])
    current = bound_commit == head
    if current:
        for path, expected_hash in sorted(registry_hashes.items()):
            if not isinstance(path, str) or not path.startswith("docs/project-memory/registries/"):
                raise ValueError(f"Unsupported snapshot registry path: {path}")
            tracked_path = repo_root / path
            if not tracked_path.is_file():
                raise ValueError(f"Current tracked registry is missing: {path}")
            if _compute_sha256(tracked_path) != expected_hash:
                raise ValueError(
                    f"Current publication snapshot differs from current tracked registry: {path}"
                )

    return loaded, {
        "bound_commit": bound_commit,
        "branch": branch,
        "head_commit": head,
        "repository_currentness": "current" if current else "historical",
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_markdown_line(line: str, *, strip_inline_code: bool) -> str:
    """Return deterministic visible Markdown text for authority inspection."""
    text = re.sub(r"!?(?:\[([^\]]*)\])\([^)]*\)", r"\1", line)
    if strip_inline_code:
        text = re.sub(r"`[^`]*`", "", text)
    else:
        text = text.replace("`", "")
    text = re.sub(r"^[\s#>*+\-]+", "", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("|", " ")
    return " ".join(text.split())


def _authority_allowed_classification(original: str, visible: str) -> str:
    """Classify a legitimate authority reference, or return an empty string."""
    lower = visible.lower()
    original_lower = original.lower()

    if _EXACT_GENERATED_EVIDENCE_BANNER.lower() in original_lower:
        return "generated_evidence_banner"
    if re.search(r"\bauthority_class\b[^\n]*\bgenerated_evidence\b", lower):
        return "generated_evidence_classification"
    if re.search(r"\bauthority(?:\s+context)?\s*:\s*authoritative\b", lower):
        return "tracked_record_authority_metadata"
    if "historical" in lower and (
        "quotation" in lower or "quote" in lower or original.lstrip().startswith(">")
    ):
        return "historical_quotation"
    if any(term in lower for term in (
        "validator", "validation", "validation rule", "forbidden pattern",
        "rejected pattern", "rejects the pattern", "detects the claim",
        "test case", "technical documentation",
    )):
        return "technical_validation_description"
    if "authority hierarchy" in lower or re.search(r"\btier\s+[1-7]\b", lower):
        return "authority_hierarchy_description"
    if "trust class" in lower or re.fullmatch(
        r"(?:authoritative|accepted_evidence|generated_evidence|historical|"
        r"superseded|uncertain|owner_pending|untrusted)(?:\s*:\s*\d+)?", lower,
    ):
        return "trust_class_description"
    if re.search(
        r"\b(?:generated evidence|generated (?:page|render|snapshot|package|output|documentation)|"
        r"this (?:generated )?(?:page|render|snapshot|package|output))\b[^.;|]{0,100}"
        r"\b(?:not|never|non-authoritative|cannot|can't|must not|does not|isn't|aren't)\b",
        lower,
    ) or re.search(
        r"\b(?:not|never|cannot|can't|must not|does not)\b[^.;|]{0,100}"
        r"\b(?:authoritative|project authority|project truth|source of truth|canon)\b",
        lower,
    ):
        return "generated_evidence_non_authority"
    if re.search(
        r"\b(?:model|agent) output\b[^.;|]{0,100}\b(?:not|cannot|can't|must not|never)\b"
        r"[^.;|]{0,100}\b(?:truth|canon|authoritative)\b",
        lower,
    ):
        return "candidate_non_authority_boundary"
    if re.search(
        r"\b(?:roadmap|tracked sources?|accepted (?:roadmap|owner decisions?|decisions?)|"
        r"owner decisions?)\b[^.;|]{0,120}\b(?:authoritative|authority)\b",
        lower,
    ) or re.search(
        r"\b(?:authoritative|authority)\b[^.;|]{0,120}"
        r"\b(?:roadmap|tracked sources?|owner decisions?)\b",
        lower,
    ):
        return "higher_authority_tracked_source"
    if "no automatic mutation of authoritative state" in lower:
        return "authority_mutation_prohibition"
    if "authoritative" in lower or "authority" in lower:
        return "authority_context_reference"
    if "truth" in lower or "canon" in lower:
        return "truth_or_canon_boundary"
    return ""


def analyze_authority_claims(docs_dir: str | Path) -> dict[str, Any]:
    """Inspect rendered pages for subject-aware generated-evidence authority claims."""
    docs_path = Path(docs_dir)
    allowed_references: list[dict[str, Any]] = []
    forbidden_claims: list[dict[str, Any]] = []

    for page in RENDERED_PAGE_NAMES:
        page_path = docs_path / page
        if not page_path.is_file():
            continue
        in_fence = False
        fence_marker = ""
        for line_number, original in enumerate(_read_text(page_path).splitlines(), start=1):
            stripped = original.lstrip()
            fence_match = re.match(r"(```+|~~~+)", stripped)
            if fence_match:
                marker = fence_match.group(1)[0]
                if not in_fence:
                    in_fence = True
                    fence_marker = marker
                elif marker == fence_marker:
                    in_fence = False
                    fence_marker = ""
                continue
            if in_fence:
                continue

            visible_with_code = _normalize_markdown_line(original, strip_inline_code=False)
            visible = _normalize_markdown_line(original, strip_inline_code=True)
            if not visible and not visible_with_code:
                continue

            searchable = visible.lower()
            authority_terms = (
                "authorit", "truth", "canon", "roadmap status", "task status",
                "owner decision", "candidates", "override", "supersede", "outrank",
                "precedence", "establish", "resolve", "approve", "promote",
            )
            if not any(term in searchable for term in authority_terms):
                if "authorit" in visible_with_code.lower():
                    contextual_class = _authority_allowed_classification(
                        original, visible_with_code
                    )
                    allowed_references.append({
                        "page": page,
                        "line": line_number,
                        "text": original.strip(),
                        "classification": (
                            contextual_class
                            if contextual_class != "authority_context_reference"
                            else "inline_code_reference"
                        ),
                    })
                continue

            allowed_class = _authority_allowed_classification(original, visible_with_code)
            if allowed_class in {
                "historical_quotation", "technical_validation_description",
                "generated_evidence_banner", "generated_evidence_classification",
                "tracked_record_authority_metadata", "authority_hierarchy_description",
                "trust_class_description", "generated_evidence_non_authority",
                "candidate_non_authority_boundary", "higher_authority_tracked_source",
                "authority_mutation_prohibition",
            }:
                allowed_references.append({
                    "page": page,
                    "line": line_number,
                    "text": original.strip(),
                    "classification": allowed_class,
                })
                continue

            matched_forbidden = False
            for rule_id, classification, reason, pattern in _FORBIDDEN_AUTHORITY_RULES:
                if pattern.search(visible):
                    forbidden_claims.append({
                        "page": page,
                        "line": line_number,
                        "text": original.strip(),
                        "rule": rule_id,
                        "classification": classification,
                        "reason": reason,
                    })
                    matched_forbidden = True
                    break
            if matched_forbidden:
                continue

            if allowed_class:
                allowed_references.append({
                    "page": page,
                    "line": line_number,
                    "text": original.strip(),
                    "classification": allowed_class,
                })

    return {
        "result": "fail" if forbidden_claims else "pass",
        "matches": list(forbidden_claims),
        "allowed_references": allowed_references,
        "forbidden_claims": forbidden_claims,
    }


def derive_expected_task_states(
    tasks: list[dict[str, Any]],
    owner_decisions: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    expected: dict[str, dict[str, Any]] = {}
    task_by_id: dict[str, dict[str, Any]] = {}
    for t in tasks:
        task_by_id[t.get("task_id", "")] = t

    dynamic_order = list(_PM_TASK_ORDER)
    for task in sorted(tasks, key=lambda item: item.get("task_id", "")):
        tid = task.get("task_id", "")
        if tid.startswith(_PM_PARENT + "-T") and tid not in dynamic_order:
            dynamic_order.append(tid)

    for tid in dynamic_order:
        rec = task_by_id.get(tid)
        if rec is None:
            expected[tid] = {"error": "missing"}
            continue
        lc = rec.get("lifecycle", {})
        status = lc.get("status", "")
        notes = rec.get("notes", "")
        parent = rec.get("parent_task_id", "")
        expected[tid] = {
            "task_id": tid,
            "lifecycle": status,
            "notes": notes,
            "parent_task_id": parent,
            "is_complete": status == "complete",
            "is_planned": status == "planned",
            "is_in_progress": status == "in_progress",
        }

    try:
        from scripts.project_memory.render_docs import _derive_pm_task_behavior

        behavior = _derive_pm_task_behavior(tasks, owner_decisions or [])
        for tid, derived in behavior["states"].items():
            if tid in expected:
                expected[tid].update(derived)
        next_task = behavior["next_actionable_task"]
        expected["_pm_next_task"] = {
            "task_id": next_task.get("task_id") if next_task else None,
            "lifecycle": (
                next_task.get("lifecycle", {}).get("status", "")
                if next_task else "none"
            ),
        }
    except ValueError as exc:
        expected["_derivation_error"] = {"error": str(exc)}
        expected["_pm_next_task"] = {"task_id": None, "lifecycle": "invalid"}

    ph25 = task_by_id.get("PHASE8-IMPL-025")
    if ph25:
        expected["_ph25_active"] = ph25.get("lifecycle", {}).get("status") not in ("planned",)
    else:
        expected["_ph25_active"] = False

    return expected


def _check_structural(
    render_dir: Path,
    snapshot_dir: Path | None,
    snapshot_bundle: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    docs_dir = render_dir / "docs"
    if not docs_dir.is_dir():
        checks.append({"check": "docs_dir", "result": "fail", "detail": "docs/ not found"})
        return checks
    checks.append({"check": "docs_dir", "result": "pass"})

    actual_pages: set[str] = set()
    for entry in docs_dir.iterdir():
        if entry.is_file() and entry.name.endswith(".md"):
            actual_pages.add(entry.name)
    expected = set(RENDERED_PAGE_NAMES)
    missing = expected - actual_pages
    extra = actual_pages - expected
    if missing:
        checks.append({"check": "page_set", "result": "fail",
                       "detail": f"Missing pages: {sorted(missing)}"})
    elif extra:
        checks.append({"check": "page_set", "result": "fail",
                       "detail": f"Extra pages: {sorted(extra)}"})
    else:
        checks.append({"check": "page_set", "result": "pass", "detail": f"{len(actual_pages)} pages"})

    for fn in ("build-manifest.json", "source-snapshot.json",
               "FILE-INVENTORY.txt", "SHA256SUMS"):
        fpath = render_dir / fn
        if fpath.is_file():
            checks.append({"check": f"file:{fn}", "result": "pass"})
        else:
            checks.append({"check": f"file:{fn}", "result": "fail",
                           "detail": "Missing"})

    for fn in ("build-manifest.json", "source-snapshot.json"):
        fpath = render_dir / fn
        if fpath.is_file():
            try:
                _load_json(fpath)
                checks.append({"check": f"json:{fn}", "result": "pass"})
            except Exception as e:
                checks.append({"check": f"json:{fn}", "result": "fail",
                               "detail": str(e)})

    manifest_path = render_dir / "build-manifest.json"
    if manifest_path.is_file():
        manifest = _load_json(manifest_path)
        ac = manifest.get("authority_class", "")
        if ac == "generated_evidence":
            checks.append({"check": "manifest_authority_class", "result": "pass"})
        else:
            checks.append({"check": "manifest_authority_class", "result": "fail",
                           "detail": f"Got {ac}"})

        page_hashes = manifest.get("page_hashes", {})
        for page in RENDERED_PAGE_NAMES:
            fpath = docs_dir / page
            if fpath.is_file() and page in page_hashes:
                actual = _compute_sha256(fpath)
                expected_hash = page_hashes[page]
                if actual == expected_hash:
                    checks.append({"check": f"page_hash:{page}", "result": "pass"})
                else:
                    checks.append({"check": f"page_hash:{page}", "result": "fail",
                                   "detail": "Hash mismatch"})

        freshness = manifest.get("freshness", "")
        checks.append({"check": "freshness", "result": "pass", "detail": freshness})

        mode = manifest.get("mode", "")
        checks.append({"check": "mode", "result": "pass", "detail": mode})

        pub_eligible = manifest.get("publication_eligible", False)
        checks.append({"check": "publication_eligible", "result": "pass",
                       "detail": str(pub_eligible)})

        bc = manifest.get("target_commit", "")
        if _GIT_SHA_RE.match(bc):
            checks.append({"check": "commit_binding", "result": "pass", "detail": bc[:12]})
        else:
            checks.append({"check": "commit_binding", "result": "fail",
                           "detail": "Invalid or missing commit"})

    sha_path = render_dir / "SHA256SUMS"
    if sha_path.is_file():
        checks.append({"check": "sha256sums_present", "result": "pass"})

    for page in RENDERED_PAGE_NAMES:
        fpath = docs_dir / page
        if not fpath.is_file():
            continue
        text = _read_text(fpath)
        if _EXACT_GENERATED_EVIDENCE_BANNER in text:
            checks.append({"check": f"banner:{page}", "result": "pass"})
        else:
            checks.append({"check": f"banner:{page}", "result": "fail",
                           "detail": "Missing exact generated-evidence banner"})

    for page in RENDERED_PAGE_NAMES:
        fpath = docs_dir / page
        if not fpath.is_file():
            continue
        text = _read_text(fpath)
        if "javascript:" in text.lower() or "<script" in text.lower():
            checks.append({"check": f"unsafe_content:{page}", "result": "fail",
                           "detail": "Potentially unsafe content"})
        else:
            checks.append({"check": f"unsafe_content:{page}", "result": "pass"})

    for page in RENDERED_PAGE_NAMES:
        fpath = docs_dir / page
        if not fpath.is_file():
            continue
        text = _read_text(fpath)
        for match in re.finditer(r"\]\(([^)]+)\)", text):
            link = match.group(1)
            if link.startswith("http://") or link.startswith("https://"):
                continue
            if ".." in link.replace("\\", "/").split("/"):
                checks.append({"check": f"unsafe_link:{page}", "result": "fail",
                               "detail": f"Traversal link: {link}"})

    return checks


def validate_rendered_package(
    repo_root: str,
    snapshot_dir: str,
    render_dir: str,
    registries: dict[str, Any] | None = None,
    snapshot_bundle: dict[str, Any] | None = None,
    expected_task_states: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    render_path = Path(render_dir).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    nonblocking_findings: list[dict[str, Any]] = []
    snapshot_context = {
        "bound_commit": "",
        "branch": "",
        "head_commit": "",
        "repository_currentness": "unknown",
    }

    if snapshot_bundle is not None:
        convergence_findings = snapshot_bundle.get("findings", [])
    else:
        convergence_path = Path(snapshot_dir) / "convergence-findings.json"
        if convergence_path.is_file():
            convergence_data = _load_json(convergence_path)
            convergence_findings = convergence_data.get("findings", [])
        else:
            convergence_findings = []
    for finding in convergence_findings:
        if not isinstance(finding, dict):
            continue
        if finding.get("severity") == "warning" and not finding.get("blocks_publication", False):
            diagnostic = {
                "code": finding.get("code", "unknown"),
                "finding_id": finding.get("finding_id", ""),
                "severity": "warning",
                "title": finding.get("title", ""),
            }
            nonblocking_findings.append(diagnostic)
            warnings.append(
                f"{diagnostic['code']}: {diagnostic['finding_id']}: {diagnostic['title']}"
            )

    strict_snapshot_binding = registries is None or snapshot_bundle is not None
    if strict_snapshot_binding:
        try:
            bound_registries, snapshot_context = _load_snapshot_bound_registries(
                root, Path(snapshot_dir), snapshot_bundle
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"Snapshot-bound registry validation failed: {exc}")
            return _blocked_result(errors, warnings, {})
        tasks_data = bound_registries.get("tasks.json", {})
        owner_data = bound_registries.get("owner-decisions.json", {})
    elif registries is not None:
        tasks_data = registries.get("tasks.json", {})
        owner_data = registries.get("owner-decisions.json", {})
    else:
        tasks_data = {}
        owner_data = {}

    task_records = tasks_data.get("records", []) if isinstance(tasks_data, dict) else []
    owner_records = owner_data.get("records", []) if isinstance(owner_data, dict) else []
    tasks_by_id = {task.get("task_id"): task for task in task_records}

    def is_descendant(task: dict[str, Any], parent_task_id: str) -> bool:
        seen: set[str] = set()
        current = task.get("parent_task_id")
        while isinstance(current, str) and current not in seen:
            if current == parent_task_id:
                return True
            seen.add(current)
            current = tasks_by_id.get(current, {}).get("parent_task_id")
        return False

    application_frontiers = [
        task.get("task_id")
        for task in task_records
        if is_descendant(task, "PHASE8-IMPL-024")
        and task.get("is_application_frontier") is True
    ]
    if len(application_frontiers) != 1:
        errors.append(
            "Task registry must declare exactly one PHASE8-IMPL-024 descendant as "
            "the application frontier"
        )
        return _blocked_result(errors, warnings, {})
    expected_app_frontier = application_frontiers[0]
    if expected_task_states is None:
        task_states = derive_expected_task_states(task_records, owner_records)
    else:
        task_states = expected_task_states

    derivation_error = task_states.get("_derivation_error", {}).get("error")
    if derivation_error:
        errors.append(f"Task-state derivation failed: {derivation_error}")
        return _blocked_result(errors, warnings, task_states)

    missing_tasks = [tid for tid in _PM_TASK_ORDER
                     if task_states.get(tid, {}).get("error") == "missing"]
    if missing_tasks:
        errors.append(f"Required task records missing from registry: {missing_tasks}")
        return {
            "result": RESULT_BLOCKED,
            "errors": errors,
            "warnings": warnings,
            "target_commit": "",
            "target_branch": "",
            "snapshot_commit": "",
            "snapshot_branch": "",
            "render_commit": "",
            "render_branch": "",
            "page_count": 0,
            "structural_checks": [],
            "semantic_checks": [],
            "expected_task_states": task_states,
            "observed_task_states": {},
            "application_frontier_check": "fail",
            "ph8_impl_025_check": "fail",
            "remaining_work_check": "fail",
            "authority_check": "not_run",
            "authority": {
                "result": "not_run", "matches": [],
                "allowed_references": [], "forbidden_claims": [],
            },
        }

    dup_ids: dict[str, int] = {}
    for t in task_records:
        tid = t.get("task_id", "")
        dup_ids[tid] = dup_ids.get(tid, 0) + 1
    duplicates = [tid for tid, cnt in dup_ids.items() if cnt > 1]
    if duplicates:
        errors.append(f"Duplicate task IDs in registry: {duplicates}")
        return _blocked_result(errors, warnings, task_states)

    snap = Path(snapshot_dir) if snapshot_dir else None
    structural_checks = _check_structural(render_path, snap, snapshot_bundle)
    for sc in structural_checks:
        if sc.get("result") == "fail":
            errors.append(f"Structural check failed: {sc.get('check')} — {sc.get('detail', '')}")

    docs_dir = render_path / "docs"

    r_branch = ""
    r_commit = ""
    if (render_path / "build-manifest.json").is_file():
        manifest = _load_json(render_path / "build-manifest.json")
        r_branch = manifest.get("target_branch", "")
        r_commit = manifest.get("target_commit", "")
    if (render_path / "source-snapshot.json").is_file():
        ss = _load_json(render_path / "source-snapshot.json")
        s_branch = ss.get("branch", "")
        s_commit = ss.get("bound_commit", "")
    else:
        s_branch = ""
        s_commit = ""

    snapshot_commit = snapshot_context.get("bound_commit", "") or s_commit
    snapshot_branch = snapshot_context.get("branch", "") or s_branch
    if strict_snapshot_binding:
        if not r_commit or r_commit != snapshot_commit:
            errors.append("Render target commit differs from selected snapshot commit")
        if not s_commit or s_commit != snapshot_commit:
            errors.append("Render source-snapshot commit differs from selected snapshot commit")
        if not r_branch or r_branch != snapshot_branch or s_branch != snapshot_branch:
            errors.append("Render branch differs from selected snapshot branch")

    page_count = 0
    for page in RENDERED_PAGE_NAMES:
        if (docs_dir / page).is_file():
            page_count += 1

    semantic_checks: list[dict[str, Any]] = []

    def _read_page(name: str) -> str:
        pp = docs_dir / name
        return _read_text(pp) if pp.is_file() else ""

    index_text = _read_page("index.md")
    roadmap_text = _read_page("current-roadmap.md")
    remaining_text = _read_page("remaining-work.md")

    task_ids_to_check = [
        tid for tid in task_states
        if isinstance(tid, str) and tid.startswith(_PM_PARENT + "-T")
    ]
    task_ids_to_check.sort()
    for tid in task_ids_to_check:
        expected = task_states.get(tid, {})
        if not expected or expected.get("error"):
            continue
        es = expected.get("lifecycle", "")
        task_id_short = tid.replace("PHASE8-IMPL-026-", "")

        if es == "complete":
            if f"{task_id_short} (" in index_text and "in progress" in index_text:
                t4_check = _check_page_for_task(index_text, tid, "in progress")
                if t4_check:
                    errors.append(f"Semantic: {tid} rendered as 'in progress' but registry says complete")
                    semantic_checks.append({"check": f"task:{tid}_not_in_progress", "result": "fail"})
                else:
                    semantic_checks.append({"check": f"task:{tid}_not_in_progress", "result": "pass"})
            else:
                semantic_checks.append({"check": f"task:{tid}_not_in_progress", "result": "pass"})

        if es != "planned" and f"T004C" in index_text:
            if _check_page_for_task(index_text, "PHASE8-IMPL-026-T004C", "planned"):
                errors.append("Semantic: T004C rendered as 'planned' but registry says complete")
                semantic_checks.append({"check": "task:T004C_not_planned", "result": "fail"})
            else:
                semantic_checks.append({"check": "task:T004C_not_planned", "result": "pass"})
        else:
            semantic_checks.append({"check": "task:T004C_not_planned", "result": "pass"})

        if strict_snapshot_binding:
            short = tid.replace(_PM_PARENT + "-", "")
            table_lines = [
                line for line in index_text.splitlines()
                if line.startswith(f"| {short} (")
            ]
            if len(table_lines) != 1:
                errors.append(f"Semantic: {tid} must appear exactly once in the index status table")
                semantic_checks.append({"check": f"task:{tid}_index_state", "result": "fail"})
            else:
                line = table_lines[0].lower()
                state = expected.get("state", "")
                lifecycle_ok = (
                    (es == "complete" and "complete" in line and "planned" not in line)
                    or (es == "planned" and "planned" in line and "complete" not in line)
                    or (es == "in_progress" and ("active" in line or "in progress" in line))
                )
                state_ok = (
                    state != "owner_deferred_contingent"
                    or ("contingent" in line and "owner-deferred" in line and "inactive" in line)
                )
                if lifecycle_ok and state_ok:
                    semantic_checks.append({"check": f"task:{tid}_index_state", "result": "pass"})
                else:
                    errors.append(f"Semantic: {tid} index status contradicts its snapshot-bound state")
                    semantic_checks.append({"check": f"task:{tid}_index_state", "result": "fail"})

    t4_calls_in_progress = False
    for line in index_text.split("\n"):
        if "T004" in line and "Human-readable memory" in line and "in progress" in line:
            t4_calls_in_progress = True
            break
    if t4_calls_in_progress:
        errors.append("Semantic: T004 rendered as 'in progress' in index")
        semantic_checks.append({"check": "t004_not_in_progress_index", "result": "fail"})
    else:
        semantic_checks.append({"check": "t004_not_in_progress_index", "result": "pass"})

    t4c_calls_planned = False
    for line in index_text.split("\n"):
        if "T004C" in line and "Clean-HEAD" in line and "planned" in line:
            t4c_calls_planned = True
            break
    if t4c_calls_planned:
        errors.append("Semantic: T004C rendered as 'planned' in index")
        semantic_checks.append({"check": "t004c_not_planned_index", "result": "fail"})
    else:
        semantic_checks.append({"check": "t004c_not_planned_index", "result": "pass"})

    if "T004B" in roadmap_text and "Current Project Memory child" in roadmap_text:
        if "Current Project Memory child: T004B" in roadmap_text:
            errors.append("Semantic: T004B rendered as current PM child")
            semantic_checks.append({"check": "t004b_not_current_child", "result": "fail"})
        else:
            semantic_checks.append({"check": "t004b_not_current_child", "result": "pass"})
    else:
        semantic_checks.append({"check": "t004b_not_current_child", "result": "pass"})

    next_task = task_states.get("_pm_next_task", {})
    next_tid = next_task.get("task_id", "")
    if next_tid:
        short_next = next_tid.replace(_PM_PARENT + "-", "")
        accepted_next_markers = (
            f"Next Project Memory task:** {short_next}",
            f"Next actionable Project Memory task:** {short_next}",
            f"Active Project Memory task:** {short_next}",
        )
        if not any(marker in roadmap_text for marker in accepted_next_markers):
            errors.append(f"Semantic: Next PM task {short_next} absent from current-roadmap")
            semantic_checks.append({"check": "next_task_in_roadmap", "result": "fail"})
        else:
            semantic_checks.append({"check": "next_task_in_roadmap", "result": "pass"})
    else:
        if "Next actionable Project Memory task:** none" not in roadmap_text and "all complete" not in roadmap_text:
            errors.append("Semantic: No actionable PM task is not explicit in current-roadmap")
            semantic_checks.append({"check": "next_task_none_explicit", "result": "fail"})
        else:
            semantic_checks.append({"check": "next_task_none_explicit", "result": "pass"})

    for tid in task_ids_to_check:
        state = task_states.get(tid, {}).get("state", "")
        short = tid.replace(_PM_PARENT + "-", "")
        if state == "owner_deferred_contingent":
            if short not in roadmap_text or short not in remaining_text:
                errors.append(f"Semantic: Deferred contingent task {short} is not visible")
                semantic_checks.append({"check": f"task:{short}_deferred_visible", "result": "fail"})
            elif next_tid == tid:
                errors.append(f"Semantic: Deferred contingent task {short} selected as actionable")
                semantic_checks.append({"check": f"task:{short}_not_actionable", "result": "fail"})
            else:
                semantic_checks.append({"check": f"task:{short}_deferred_visible", "result": "pass"})

    ph25_active = task_states.get("_ph25_active", False)
    if ph25_active:
        errors.append("Semantic: PHASE8-IMPL-025 appears activated but must remain inactive")
        semantic_checks.append({"check": "ph25_inactive", "result": "fail"})
    else:
        semantic_checks.append({"check": "ph25_inactive", "result": "pass"})

    app_frontier_ok = expected_app_frontier in roadmap_text or expected_app_frontier in index_text
    if not app_frontier_ok:
        errors.append(f"Semantic: Application frontier {expected_app_frontier} not found in rendered pages")
        semantic_checks.append({"check": "app_frontier", "result": "fail"})
    else:
        semantic_checks.append({"check": "app_frontier", "result": "pass"})

    t4_rec = task_states.get("PHASE8-IMPL-026-T004", {})
    if t4_rec.get("is_complete"):
        if "T004" in remaining_text or "PHASE8-IMPL-026-T004" in remaining_text:
            t4_in_remaining = False
            for line in remaining_text.split("\n"):
                if ("PHASE8-IMPL-026-T004" in line or "T004" in line) and line.strip().startswith("-"):
                    t4_in_remaining = True
                    break
            if t4_in_remaining:
                errors.append("Semantic: T004 appears in remaining work but is complete")
                semantic_checks.append({"check": "t004_not_in_remaining", "result": "fail"})
            else:
                semantic_checks.append({"check": "t004_not_in_remaining", "result": "pass"})
        else:
            semantic_checks.append({"check": "t004_not_in_remaining", "result": "pass"})
    else:
        semantic_checks.append({"check": "t004_not_in_remaining", "result": "pass"})

    if next_tid:
        short_next = next_tid.replace(_PM_PARENT + "-", "")
        t5_in_remaining = f"PHASE8-IMPL-026-{short_next}" in remaining_text or short_next in remaining_text
        if not t5_in_remaining:
            errors.append(f"Semantic: Next task {short_next} missing from remaining-work")
            semantic_checks.append({"check": "next_task_in_remaining", "result": "fail"})
        else:
            semantic_checks.append({"check": "next_task_in_remaining", "result": "pass"})

    authority = analyze_authority_claims(docs_dir)
    authority_ok = authority["result"] == "pass"
    semantic_checks.append({"check": "non_authoritative", "result": "pass" if authority_ok else "fail"})
    if not authority_ok:
        for claim in authority["forbidden_claims"]:
            errors.append(
                "Authority: forbidden generated-evidence claim at "
                f"{claim['page']}:{claim['line']} [{claim['rule']}]: {claim['text']}"
            )

    observed = {}
    for tid in _PM_TASK_ORDER:
        observed[tid] = {"found_in_index": tid in index_text,
                         "found_in_roadmap": tid in roadmap_text}

    if errors:
        result = RESULT_BLOCKED
    elif warnings:
        result = RESULT_PASS_WITH_FINDINGS
    else:
        result = RESULT_PASS

    return {
        "result": result,
        "errors": errors,
        "warnings": warnings,
        "nonblocking_findings": nonblocking_findings,
        "target_commit": r_commit,
        "target_branch": r_branch,
        "snapshot_commit": snapshot_commit,
        "snapshot_branch": snapshot_branch,
        "render_commit": r_commit,
        "render_branch": r_branch,
        "page_count": page_count,
        "structural_checks": structural_checks,
        "semantic_checks": semantic_checks,
        "expected_task_states": task_states,
        "observed_task_states": observed,
        "application_frontier_check": "pass" if app_frontier_ok else "fail",
        "ph8_impl_025_check": "fail" if ph25_active else "pass",
        "remaining_work_check": "pass",
        "authority_check": "pass" if authority_ok else "fail",
        "authority": authority,
        "repository_currentness": snapshot_context.get("repository_currentness", "unknown"),
    }


def _check_page_for_task(text: str, task_id: str, term: str) -> bool:
    short = task_id.replace("PHASE8-IMPL-026-", "")
    lines = text.split("\n")
    for line in lines:
        if short in line and term in line:
            return True
    return False


def _blocked_result(
    errors: list[str], warnings: list[str], task_states: dict[str, Any]
) -> dict[str, Any]:
    return {
        "result": RESULT_BLOCKED,
        "errors": errors,
        "warnings": warnings,
        "target_commit": "",
        "target_branch": "",
        "snapshot_commit": "",
        "snapshot_branch": "",
        "render_commit": "",
        "render_branch": "",
        "page_count": 0,
        "structural_checks": [],
        "semantic_checks": [],
        "expected_task_states": task_states,
        "observed_task_states": {},
        "application_frontier_check": "fail",
        "ph8_impl_025_check": "fail",
        "remaining_work_check": "fail",
        "authority_check": "not_run",
        "authority": {
            "result": "not_run", "matches": [],
            "allowed_references": [], "forbidden_claims": [],
        },
    }


def _build_result(
    errors: list[str],
    warnings: list[str],
    target_commit: str,
    target_branch: str,
    snap_commit: str,
    snap_branch: str,
    page_count: int,
    structural_checks: list[dict[str, Any]],
    semantic_checks: list[dict[str, Any]],
    task_states: dict[str, Any],
    observed: dict[str, Any],
    app_frontier_ok: bool,
    ph25_active: bool,
    remaining_ok: bool,
    authority_ok: bool,
) -> dict[str, Any]:
    if errors:
        overall = RESULT_BLOCKED
    elif warnings:
        overall = RESULT_PASS_WITH_FINDINGS
    else:
        overall = RESULT_PASS
    return {
        "result": overall,
        "errors": errors,
        "warnings": warnings,
        "target_commit": target_commit,
        "target_branch": target_branch,
        "snapshot_commit": snap_commit,
        "snapshot_branch": snap_branch,
        "render_commit": target_commit,
        "render_branch": target_branch,
        "page_count": page_count,
        "structural_checks": structural_checks,
        "semantic_checks": semantic_checks,
        "expected_task_states": task_states,
        "observed_task_states": observed,
        "application_frontier_check": "pass" if app_frontier_ok else "fail",
        "ph8_impl_025_check": "fail" if ph25_active else "pass",
        "remaining_work_check": "fail" if not remaining_ok else "pass",
        "authority_check": "pass" if authority_ok else "fail",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantic rendered-documentation validator.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--snapshot-dir", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_rendered_package(
        repo_root=args.repo_root,
        snapshot_dir=args.snapshot_dir,
        render_dir=args.render_dir,
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Result: {result['result']}")
        for e in result.get("errors", []):
            print(f"  ERROR: {e}")
        for w in result.get("warnings", []):
            print(f"  WARNING: {w}")

    return 0 if result["result"] != RESULT_BLOCKED else 1


if __name__ == "__main__":
    sys.exit(main())
