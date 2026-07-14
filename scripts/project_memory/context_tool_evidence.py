#!/usr/bin/env python3
"""Read-only adapters for existing context-tool evidence.

The adapters inventory already-generated Repomix, Graphify, and CCE artifacts.
They never execute a context tool, access the network, call a model, modify a
source artifact, or mutate Project Memory registries.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ADAPTER_NAME = "project_memory_context_tool_import"
ADAPTER_VERSION = "1.0.0"
ENVELOPE_VERSION = "1.0.0"
PACKAGE_VERSION = "1.0.0"

AUTHORITY_CLASS = "generated_evidence"
UNKNOWN_TOOL = "unknown_generated_context"
KNOWN_TOOLS = ("repomix", "graphify", "cce")
SOURCE_ROOTS = (".codex-context", "ai_context", "graphify-out")
EXACT_PACKAGE_FILES = (
    "FILE-INVENTORY.txt",
    "SHA256SUMS",
    "artifact-envelopes.json",
    "artifact-inventory.json",
    "findings.json",
    "run-metadata.json",
    "summary.md",
    "tool-inventory.json",
)

MAX_METADATA_BYTES = 1_048_576
MAX_SNIFF_BYTES = 16_384
MAX_INVENTORY_ENTRIES = 20_000

_METADATA_NAMES = frozenset({
    "manifest.json",
    "task_manifest.json",
    "evidence_manifest.json",
    "context-manifest.json",
    "context_manifest.json",
    "metadata.json",
    "run-metadata.json",
    "snapshot.json",
    "build-manifest.json",
    "command.txt",
    "commands.txt",
    "collection_plan.md",
    "evidence-collection-addendum.md",
    "summary.md",
    "README.md",
    "FILE-INVENTORY.txt",
    "SHA256SUMS",
    ".graphify_version",
})

_SECRET_NAMES = frozenset({
    ".env",
    "credentials",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "secrets.json",
})
_EXCLUDED_DIR_NAMES = frozenset({
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    "cache",
    "caches",
    "venv",
    "env",
    "models",
    "checkpoints",
    "datasets",
    "training",
})
_MODEL_OR_DATA_SUFFIXES = frozenset({
    ".bin", ".ckpt", ".gguf", ".jsonl", ".onnx", ".pt", ".pth",
    ".safetensors", ".sqlite", ".tflite",
})
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_RUN_ID_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$")


def _canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _write_json(path: Path, data: Any) -> None:
    path.write_text(_canonical_json(data), encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(value: str) -> bool:
    if not value or "\x00" in value:
        return False
    candidate = Path(value)
    return not candidate.is_absolute() and ".." not in candidate.parts


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _read_bounded(path: Path, limit: int = MAX_METADATA_BYTES) -> str:
    size = path.stat().st_size
    if size > limit:
        raise ValueError(f"metadata exceeds {limit} bytes")
    return path.read_text(encoding="utf-8", errors="replace")


def _finding(
    code: str,
    message: str,
    *,
    severity: str = "warning",
    blocks_consumption: bool = False,
) -> dict[str, Any]:
    return {
        "blocks_consumption": blocks_consumption,
        "code": code,
        "message": message,
        "severity": severity,
    }


def _resolve_repo_root(requested: str | Path) -> Path:
    root = Path(requested).resolve(strict=True)
    if not root.is_dir() or not (root / ".git").exists():
        raise ValueError(f"Not a Git repository: {root}")
    return root


def _git_dir(repo_root: Path) -> Path:
    marker = repo_root / ".git"
    if marker.is_dir():
        return marker.resolve()
    if marker.is_file():
        text = _read_bounded(marker, 4096).strip()
        if not text.startswith("gitdir:"):
            raise ValueError("Malformed .git file")
        value = text.split(":", 1)[1].strip()
        git_dir = Path(value)
        if not git_dir.is_absolute():
            git_dir = marker.parent / git_dir
        return git_dir.resolve(strict=True)
    raise ValueError("Missing .git metadata")


def _read_git_identity(repo_root: Path) -> tuple[str, str]:
    """Read current branch and commit without invoking Git."""
    git_dir = _git_dir(repo_root)
    common_dir = git_dir
    common_dir_marker = git_dir / "commondir"
    if common_dir_marker.is_file():
        common_value = _read_bounded(common_dir_marker, 4096).strip()
        common_candidate = Path(common_value)
        if not common_candidate.is_absolute():
            common_candidate = git_dir / common_candidate
        common_dir = common_candidate.resolve(strict=True)
    head = _read_bounded(git_dir / "HEAD", 4096).strip()
    branch = "DETACHED"
    if head.startswith("ref:"):
        ref = head.split(":", 1)[1].strip()
        branch = ref.removeprefix("refs/heads/")
        ref_path = common_dir / ref
        if ref_path.is_file():
            commit = _read_bounded(ref_path, 4096).strip()
        else:
            commit = ""
            packed = common_dir / "packed-refs"
            if packed.is_file():
                for line in _read_bounded(packed).splitlines():
                    if line.startswith(("#", "^")) or " " not in line:
                        continue
                    sha, packed_ref = line.split(" ", 1)
                    if packed_ref.strip() == ref:
                        commit = sha
                        break
    else:
        commit = head
    if not _GIT_SHA_RE.fullmatch(commit):
        raise ValueError("Git HEAD does not resolve to a full commit")
    return branch, commit


def _tracked_policy_text(repo_root: Path) -> tuple[str, list[str]]:
    policy_paths = (
        ".gitignore",
        ".graphifyignore",
        "docs/roadmap/context_tool_policy.md",
        "docs/roadmap/context_execution_standard.md",
    )
    chunks: list[str] = []
    sources: list[str] = []
    for rel in policy_paths:
        path = repo_root / rel
        if path.is_file() and not path.is_symlink():
            chunks.append(_read_bounded(path))
            sources.append(rel)
    return "\n".join(chunks), sources


def _allowed_source_roots(repo_root: Path) -> tuple[list[str], list[str]]:
    policy, sources = _tracked_policy_text(repo_root)
    allowed = [root for root in SOURCE_ROOTS if root in policy]
    return allowed, sources


def discover_context_artifacts(repo_root: str | Path) -> list[dict[str, Any]]:
    """Discover bounded artifact packages under policy-approved generated roots.

    Discovery records paths only. It does not execute collectors or load pack
    bodies. The Project Memory output root is always excluded to avoid recursive
    evidence ingestion.
    """
    root = _resolve_repo_root(repo_root)
    allowed_roots, policy_sources = _allowed_source_roots(root)
    artifacts: list[dict[str, Any]] = []

    for source_root in sorted(allowed_roots):
        base = root / source_root
        if not base.exists() and not base.is_symlink():
            continue
        if source_root == "graphify-out":
            artifacts.append({
                "artifact_id": _artifact_id(source_root),
                "discovery_basis": "policy_approved_generated_root",
                "policy_sources": policy_sources,
                "source_package_path": source_root,
                "source_root": source_root,
            })
            continue
        if not base.is_dir() or base.is_symlink():
            artifacts.append({
                "artifact_id": _artifact_id(source_root),
                "discovery_basis": "policy_approved_generated_root",
                "policy_sources": policy_sources,
                "source_package_path": source_root,
                "source_root": source_root,
            })
            continue
        for entry in sorted(base.iterdir(), key=lambda item: item.name):
            rel = entry.relative_to(root).as_posix()
            if rel == ".codex-context/project-memory":
                continue
            artifacts.append({
                "artifact_id": _artifact_id(rel),
                "discovery_basis": "direct_child_of_policy_approved_generated_root",
                "policy_sources": policy_sources,
                "source_package_path": rel,
                "source_root": source_root,
            })
    return artifacts


def _artifact_id(rel_path: str) -> str:
    suffix = hashlib.sha256(rel_path.encode("utf-8")).hexdigest()[:16]
    return f"context-artifact:{suffix}"


def _unsafe_component_reason(rel: Path) -> str | None:
    lowered = [part.lower() for part in rel.parts]
    for part in lowered:
        if part in _EXCLUDED_DIR_NAMES or part.startswith(".venv"):
            return f"excluded path component: {part}"
        if part == ".env" or part.startswith(".env.") or part in _SECRET_NAMES:
            return f"secret-bearing path component: {part}"
        if "credential" in part or part in {"secret", "secrets", "token", "tokens"}:
            return f"credential-bearing path component: {part}"
    if rel.suffix.lower() in _MODEL_OR_DATA_SUFFIXES:
        return f"excluded model or dataset suffix: {rel.suffix.lower()}"
    if len(lowered) >= 2 and lowered[0] == ".codex-context" and lowered[1] == "project-memory":
        return "recursively nested Project Memory package"
    return None


def _inventory_artifact(
    repo_root: Path, artifact_path: Path, source_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inventory: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    def inspect_entry(path: Path) -> bool:
        rel_repo = path.relative_to(repo_root)
        reason = _unsafe_component_reason(rel_repo)
        if reason:
            findings.append(_finding(
                "excluded_or_sensitive_path", f"{rel_repo.as_posix()}: {reason}",
                blocks_consumption=True,
            ))
            return False
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            findings.append(_finding(
                "unreadable_source", f"{rel_repo.as_posix()}: {exc}",
                blocks_consumption=True,
            ))
            return False
        if stat.S_ISLNK(mode):
            try:
                resolved = path.resolve(strict=True)
            except OSError as exc:
                findings.append(_finding(
                    "unsafe_symlink", f"{rel_repo.as_posix()}: {exc}",
                    blocks_consumption=True,
                ))
                return False
            if not _is_relative_to(resolved, source_root.resolve()):
                findings.append(_finding(
                    "symlink_escape", f"{rel_repo.as_posix()} escapes {source_root.relative_to(repo_root)}",
                    blocks_consumption=True,
                ))
            else:
                findings.append(_finding(
                    "symlink_not_imported", f"{rel_repo.as_posix()} is a symlink",
                    blocks_consumption=True,
                ))
            return False
        if stat.S_ISREG(mode):
            inventory.append({
                "path": path.relative_to(artifact_path).as_posix() if artifact_path.is_dir() else path.name,
                "size": path.stat().st_size,
                "type": "file",
            })
            return True
        if stat.S_ISDIR(mode):
            return True
        findings.append(_finding(
            "special_file", f"{rel_repo.as_posix()} is not a regular file or directory",
            blocks_consumption=True,
        ))
        return False

    if not inspect_entry(artifact_path):
        return inventory, findings
    if artifact_path.is_file():
        return inventory, findings

    count = 0
    for current, dir_names, file_names in os.walk(artifact_path, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in sorted(dir_names):
            child = current_path / name
            if inspect_entry(child):
                kept_dirs.append(name)
        dir_names[:] = kept_dirs
        for name in sorted(file_names):
            count += 1
            if count > MAX_INVENTORY_ENTRIES:
                findings.append(_finding(
                    "inventory_limit_exceeded",
                    f"Artifact contains more than {MAX_INVENTORY_ENTRIES} files",
                    blocks_consumption=True,
                ))
                return sorted(inventory, key=lambda item: item["path"]), findings
            inspect_entry(current_path / name)
    return sorted(inventory, key=lambda item: item["path"]), findings


def _metadata_paths(artifact_path: Path, inventory: list[dict[str, Any]]) -> list[Path]:
    if artifact_path.is_file():
        return [artifact_path]
    paths: list[Path] = []
    for entry in inventory:
        rel = Path(entry["path"])
        if rel.name in _METADATA_NAMES:
            paths.append(artifact_path / rel)
    return sorted(paths, key=lambda path: path.relative_to(artifact_path).as_posix())


def _flatten_strings(value: Any, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from _flatten_strings(value[key], child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _flatten_strings(item, f"{prefix}[{index}]")
    elif isinstance(value, (str, int, float, bool)):
        yield prefix, str(value)


def _load_metadata(
    artifact_path: Path, inventory: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    documents: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for path in _metadata_paths(artifact_path, inventory):
        rel = path.name if artifact_path.is_file() else path.relative_to(artifact_path).as_posix()
        try:
            limit = MAX_SNIFF_BYTES if artifact_path.is_file() and path.suffix.lower() not in {".json", ".md", ".txt"} else MAX_METADATA_BYTES
            if path.stat().st_size > limit:
                if artifact_path.is_file() and path.suffix.lower() not in {".json", ".md", ".txt"}:
                    with path.open("rb") as stream:
                        text = stream.read(limit).decode("utf-8", errors="replace")
                    documents.append({"path": rel, "data": text, "partial": True})
                    continue
                raise ValueError(f"metadata exceeds {limit} bytes")
            text = _read_bounded(path, limit)
            if path.suffix.lower() == ".json":
                data: Any = json.loads(text)
            else:
                data = text
            documents.append({"path": rel, "data": data, "partial": False})
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            findings.append(_finding(
                "malformed_or_oversized_metadata", f"{rel}: {exc}",
                blocks_consumption=True,
            ))
    return documents, findings


def _tracked_conventions(repo_root: Path) -> dict[str, Any]:
    conventions: dict[str, Any] = {"repomix_paths": set(), "graphify": False, "cce": False}
    for rel in ("repomix.config.json", "repomix.workspace-docs.config.json"):
        path = repo_root / rel
        if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_METADATA_BYTES:
            continue
        try:
            data = json.loads(_read_bounded(path))
        except (ValueError, json.JSONDecodeError):
            continue
        output = data.get("output", {}) if isinstance(data, dict) else {}
        file_path = output.get("filePath") if isinstance(output, dict) else None
        if isinstance(file_path, str) and _safe_relative(file_path):
            conventions["repomix_paths"].add(Path(file_path).as_posix())
    script = repo_root / "scripts/generate_ai_context.sh"
    if script.is_file() and not script.is_symlink():
        text = _read_bounded(script)
        if "repomix" in text:
            for match in re.findall(r"ai_context/repomix-[A-Za-z0-9._-]+", text):
                conventions["repomix_paths"].add(match)
    command_record = repo_root / "scripts/roadmap_enrichment/tool_commands.md"
    if command_record.is_file() and not command_record.is_symlink():
        text = _read_bounded(command_record)
        conventions["graphify"] = "graphify-out/graph.json" in text and "graphify query" in text
        conventions["cce"] = "cce search" in text and "cce-findings.md" in text
    standard = repo_root / "docs/roadmap/context_execution_standard.md"
    if standard.is_file() and not standard.is_symlink():
        text = _read_bounded(standard)
        conventions["graphify"] = conventions["graphify"] or (
            "graphify-out/graph.json" in text and "Graphify" in text
        )
        conventions["cce"] = conventions["cce"] or (
            "cce-findings.md" in text and "CCE" in text
        )
    return conventions


def _document_text(documents: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for document in documents:
        data = document["data"]
        if isinstance(data, str):
            parts.append(data)
        else:
            parts.extend(value for _, value in _flatten_strings(data))
    return "\n".join(parts)


def _tool_claims(
    repo_root: Path,
    source_path: str,
    inventory: list[dict[str, Any]],
    documents: list[dict[str, Any]],
) -> tuple[list[str], list[dict[str, str]]]:
    claims: set[str] = set()
    evidence: list[dict[str, str]] = []
    text = _document_text(documents)
    lower = text.lower()

    patterns = {
        "repomix": r"(?:^|[\s`'\"])(?:npx\s+(?:--yes\s+)?(?:repomix(?:@[^\s]+)?)|repomix(?:@[^\s]+)?)(?:\s|$)",
        "graphify": r"(?:^|[\s`'\"])graphify\s+(?:query|path|explain|update|extract)(?:\s|$)",
        "cce": r"(?:^|[\s`'\"])(?:cce|code-context-engine)\s+(?:search|index|status)(?:\s|$)",
    }
    for tool, pattern in patterns.items():
        if re.search(pattern, lower, flags=re.MULTILINE):
            claims.add(tool)
            evidence.append({"kind": "recorded_command_or_metadata", "source": source_path, "tool": tool})

    for document in documents:
        data = document["data"]
        if not isinstance(data, dict):
            continue
        for key, value in _flatten_strings(data):
            key_lower = key.lower()
            value_lower = value.strip().lower()
            if not any(token in key_lower for token in ("tool", "generator", "producer", "adapter")):
                continue
            for tool in KNOWN_TOOLS:
                if tool in value_lower:
                    claims.add(tool)
                    evidence.append({"kind": "tool_specific_metadata", "source": document["path"], "tool": tool})

    conventions = _tracked_conventions(repo_root)
    if source_path in conventions["repomix_paths"]:
        claims.add("repomix")
        evidence.append({"kind": "tracked_output_convention", "source": source_path, "tool": "repomix"})
    inventory_paths = {entry["path"] for entry in inventory}
    if source_path == "graphify-out" and "graph.json" in inventory_paths and conventions["graphify"]:
        claims.add("graphify")
        evidence.append({"kind": "tracked_output_convention", "source": "graphify-out/graph.json", "tool": "graphify"})
    if (
        source_path.startswith(".codex-context/")
        and "cce-findings.md" in inventory_paths
        and conventions["cce"]
    ):
        claims.add("cce")
        evidence.append({"kind": "tracked_output_convention", "source": "cce-findings.md", "tool": "cce"})
    return sorted(claims), sorted(evidence, key=lambda item: (item["tool"], item["kind"], item["source"]))


def _extract_metadata_fields(documents: list[dict[str, Any]]) -> dict[str, Any]:
    aliases = {
        "recorded_repository": {"repository", "repository_root", "repo_root", "source_repository"},
        "recorded_branch": {"branch", "source_branch", "target_branch", "repository_branch"},
        "recorded_commit": {"commit", "head_sha", "bound_commit", "target_commit", "source_commit", "repository_commit"},
        "generated_at": {"generated_at", "created_at", "collected_at"},
        "authority_claims": {"authority_class", "trust_class"},
        "freshness_claims": {"freshness", "freshness_state", "preservation_status"},
        "included_scope": {"included_scope", "included_scopes", "include", "includes"},
        "excluded_scope": {"excluded_scope", "excluded_scopes", "exclusions", "exclude", "ignore"},
        "tool_versions": {"tool_version", "generator_version", "producer_version"},
    }
    collected: dict[str, list[str]] = {key: [] for key in aliases}
    for document in documents:
        data = document["data"]
        if not isinstance(data, dict):
            continue
        for key, value in _flatten_strings(data):
            key_without_indexes = re.sub(r"\[\d+\]", "", key)
            leaf = key_without_indexes.rsplit(".", 1)[-1].lower()
            for target, names in aliases.items():
                if leaf in names:
                    collected[target].append(value)
            if key_without_indexes.lower().endswith(("tool.version", "generator.version", "producer.version")):
                collected["tool_versions"].append(value)
    result: dict[str, Any] = {}
    for key, values in collected.items():
        unique = sorted(set(value for value in values if value != ""))
        if key in {"included_scope", "excluded_scope", "authority_claims", "freshness_claims", "tool_versions"}:
            result[key] = unique
        elif len(unique) == 1:
            result[key] = unique[0]
        elif len(unique) > 1:
            result[key] = None
            result[f"{key}_conflicts"] = unique
        else:
            result[key] = None
    return result


def _parse_checksum_lines(text: str) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError(f"invalid checksum line: {line[:120]}")
        parsed.append((match.group(1), match.group(2)))
    return parsed


def _validate_declared_checksums(
    artifact_path: Path, documents: list[dict[str, Any]],
) -> tuple[str, list[dict[str, str]], list[dict[str, Any]]]:
    checksum_docs = [doc for doc in documents if Path(doc["path"]).name == "SHA256SUMS"]
    if not checksum_docs:
        return "absent", [], [_finding("checksum_absent", "No declared checksums were found")]
    if artifact_path.is_file():
        return "invalid", [], [_finding(
            "checksum_invalid", "A file artifact cannot contain an internal SHA256SUMS manifest",
            blocks_consumption=True,
        )]
    declared: list[dict[str, str]] = []
    findings: list[dict[str, Any]] = []
    try:
        pairs = _parse_checksum_lines(str(checksum_docs[0]["data"]))
    except ValueError as exc:
        return "invalid", [], [_finding("checksum_invalid", str(exc), blocks_consumption=True)]
    for expected, rel in pairs:
        if not _safe_relative(rel):
            findings.append(_finding(
                "checksum_unsafe_path", f"Unsafe checksum path: {rel}", blocks_consumption=True,
            ))
            continue
        path = artifact_path / rel
        try:
            resolved = path.resolve(strict=True)
        except OSError:
            findings.append(_finding(
                "checksum_missing_file", f"Checksum target is missing: {rel}", blocks_consumption=True,
            ))
            continue
        if not _is_relative_to(resolved, artifact_path.resolve()) or path.is_symlink() or not path.is_file():
            findings.append(_finding(
                "checksum_unsafe_path", f"Unsafe checksum target: {rel}", blocks_consumption=True,
            ))
            continue
        actual = _sha256(path)
        declared.append({"path": rel, "sha256": expected, "validation": "valid" if actual == expected else "invalid"})
        if actual != expected:
            findings.append(_finding(
                "checksum_mismatch", f"Checksum mismatch: {rel}", blocks_consumption=True,
            ))
    return ("valid" if not any(f["blocks_consumption"] for f in findings) else "invalid"), sorted(declared, key=lambda item: item["path"]), findings


def inspect_context_artifact(
    repo_root: str | Path,
    artifact: dict[str, Any] | str,
) -> dict[str, Any]:
    """Inspect bounded metadata and inventory without modifying the artifact."""
    root = _resolve_repo_root(repo_root)
    descriptor = {"source_package_path": artifact} if isinstance(artifact, str) else dict(artifact)
    rel = descriptor.get("source_package_path", "")
    source_root_rel = descriptor.get("source_root", Path(rel).parts[0] if rel else "")
    findings: list[dict[str, Any]] = []
    if not isinstance(rel, str) or not _safe_relative(rel):
        findings.append(_finding("unsafe_source_path", f"Unsafe source path: {rel}", blocks_consumption=True))
        return {**descriptor, "findings": findings, "inventory": [], "metadata": {}}
    if source_root_rel not in SOURCE_ROOTS:
        findings.append(_finding("unapproved_source_root", f"Unapproved source root: {source_root_rel}", blocks_consumption=True))
        return {**descriptor, "findings": findings, "inventory": [], "metadata": {}}
    path = root / rel
    source_root = root / source_root_rel
    try:
        resolved = path.resolve(strict=True)
        source_resolved = source_root.resolve(strict=True)
    except OSError as exc:
        findings.append(_finding("missing_source", f"{rel}: {exc}", blocks_consumption=True))
        return {**descriptor, "findings": findings, "inventory": [], "metadata": {}}
    if not _is_relative_to(resolved, source_resolved):
        findings.append(_finding("source_root_escape", f"{rel} escapes {source_root_rel}", blocks_consumption=True))
        return {**descriptor, "findings": findings, "inventory": [], "metadata": {}}

    inventory, inventory_findings = _inventory_artifact(root, path, source_root)
    findings.extend(inventory_findings)
    documents, metadata_findings = _load_metadata(path, inventory)
    findings.extend(metadata_findings)
    claims, attribution_evidence = _tool_claims(root, rel, inventory, documents)
    fields = _extract_metadata_fields(documents)
    checksum_status, declared_checksums, checksum_findings = _validate_declared_checksums(path, documents)
    findings.extend(checksum_findings)

    if len(claims) == 0:
        tool_identity = UNKNOWN_TOOL
        attribution = "unknown"
        findings.append(_finding(
            "unknown_tool_origin", "No deterministic tool attribution evidence was found",
            blocks_consumption=True,
        ))
    elif len(claims) > 1:
        tool_identity = UNKNOWN_TOOL
        attribution = "ambiguous"
        findings.append(_finding(
            "ambiguous_tool_origin", f"Conflicting tool identities: {', '.join(claims)}",
            blocks_consumption=True,
        ))
    else:
        tool_identity = claims[0]
        attribution = "strong"

    for key in ("recorded_repository", "recorded_branch", "recorded_commit", "generated_at"):
        conflicts = fields.get(f"{key}_conflicts", [])
        if conflicts:
            findings.append(_finding(
                "contradictory_metadata", f"Conflicting {key}: {', '.join(conflicts)}",
                blocks_consumption=True,
            ))
    authority_claims = {value.lower() for value in fields.get("authority_claims", [])}
    text_authority_claims = {
        match.group(1).lower()
        for match in re.finditer(
            r"(?:authority_class|trust_class)\s*[:=]\s*[`\"']?([a-z_]+)",
            _document_text(documents),
            flags=re.IGNORECASE,
        )
    }
    authority_claims.update(text_authority_claims)
    if authority_claims and authority_claims != {AUTHORITY_CLASS}:
        findings.append(_finding(
            "authority_self_claim", f"Generated package claims authority classes: {sorted(authority_claims)}",
            blocks_consumption=True,
        ))

    return {
        **descriptor,
        "artifact_id": descriptor.get("artifact_id", _artifact_id(rel)),
        "attribution": attribution,
        "attribution_evidence": attribution_evidence,
        "declared_checksums": declared_checksums,
        "checksum_status": checksum_status,
        "findings": sorted(findings, key=lambda item: (item["code"], item["message"])),
        "inventory": inventory,
        "metadata": fields,
        "metadata_files_read": [doc["path"] for doc in documents],
        "tool_identity": tool_identity,
        "tool_identity_candidates": claims,
    }


def _classify_freshness(
    inspected: dict[str, Any], current_branch: str, current_commit: str,
) -> tuple[str, list[dict[str, Any]]]:
    fields = inspected.get("metadata", {})
    findings: list[dict[str, Any]] = []
    if any(f.get("blocks_consumption") for f in inspected.get("findings", [])):
        return "unusable", findings
    if any(str(value).lower() == "historical" for value in fields.get("freshness_claims", [])):
        return "historical", findings
    commit = fields.get("recorded_commit")
    branch = fields.get("recorded_branch")
    if not commit or not branch:
        missing = []
        if not commit:
            missing.append("commit")
        if not branch:
            missing.append("branch")
        findings.append(_finding(
            "freshness_unbound", f"Recorded {' and '.join(missing)} unavailable",
            blocks_consumption=True,
        ))
        return "unknown", findings
    if not _GIT_SHA_RE.fullmatch(str(commit)):
        findings.append(_finding(
            "invalid_recorded_commit", "Recorded commit is not a full lowercase Git SHA",
            blocks_consumption=True,
        ))
        return "unusable", findings
    if commit != current_commit:
        findings.append(_finding(
            "stale_commit", f"Recorded commit {commit} differs from current commit {current_commit}",
            blocks_consumption=True,
        ))
        if branch != current_branch:
            findings.append(_finding(
                "branch_mismatch", f"Recorded branch {branch} differs from current branch {current_branch}",
                blocks_consumption=True,
            ))
        return "stale", findings
    if branch != current_branch:
        findings.append(_finding(
            "branch_mismatch", f"Recorded branch {branch} differs from current branch {current_branch}",
            blocks_consumption=True,
        ))
        return "unusable", findings
    return "current", findings


def normalize_context_artifact(
    inspected: dict[str, Any],
    *,
    current_branch: str,
    current_commit: str,
) -> dict[str, Any]:
    """Normalize an inspection record into a deterministic evidence envelope."""
    findings = list(inspected.get("findings", []))
    freshness, freshness_findings = _classify_freshness(inspected, current_branch, current_commit)
    findings.extend(freshness_findings)
    fields = inspected.get("metadata", {})
    included_scope = sorted(set(fields.get("included_scope", [])))
    excluded_scope = sorted(set(fields.get("excluded_scope", [])))
    scope_bounded = bool(included_scope and excluded_scope)
    if not scope_bounded:
        findings.append(_finding(
            "scope_unbounded", "Both included and excluded scope metadata are required for default consumption",
            blocks_consumption=True,
        ))
    safety = "unsafe" if any(
        finding.get("code") in {
            "authority_self_claim", "checksum_unsafe_path", "excluded_or_sensitive_path",
            "source_root_escape", "special_file", "symlink_escape", "symlink_not_imported",
            "unsafe_source_path",
        }
        for finding in findings
    ) else "safe"
    blocking = sorted({f["code"] for f in findings if f.get("blocks_consumption")})
    eligible = (
        inspected.get("attribution") == "strong"
        and inspected.get("tool_identity") in KNOWN_TOOLS
        and freshness == "current"
        and inspected.get("checksum_status") != "invalid"
        and scope_bounded
        and safety == "safe"
        and not blocking
    )
    quarantine_reasons = [] if eligible else blocking or ["not_default_consumption_eligible"]

    return {
        "adapter": {"name": ADAPTER_NAME, "version": ADAPTER_VERSION},
        "artifact_id": inspected.get("artifact_id"),
        "authority_class": AUTHORITY_CLASS,
        "consumption": {
            "default_eligible": eligible,
            "live_execution_approved": False,
            "quarantine_reasons": quarantine_reasons,
            "read_import_approved": True,
            "status": "eligible" if eligible else "quarantined",
        },
        "current_repository": {
            "branch": current_branch,
            "commit": current_commit,
        },
        "declared_checksums": inspected.get("declared_checksums", []),
        "envelope_version": ENVELOPE_VERSION,
        "file_inventory": inspected.get("inventory", []),
        "findings": sorted(findings, key=lambda item: (item["code"], item["message"])),
        "freshness": freshness,
        "included_scope": included_scope,
        "excluded_scope": excluded_scope,
        "limitations": sorted({
            f["message"] for f in findings
            if f["code"] in {"checksum_absent", "freshness_unbound", "scope_unbounded", "unknown_tool_origin"}
        }),
        "provenance": {
            "attribution": inspected.get("attribution"),
            "attribution_evidence": inspected.get("attribution_evidence", []),
            "checksum_status": inspected.get("checksum_status"),
            "generated_at": fields.get("generated_at"),
            "manifest_or_command_evidence": inspected.get("metadata_files_read", []),
            "recorded_branch": fields.get("recorded_branch"),
            "recorded_commit": fields.get("recorded_commit"),
            "recorded_repository": fields.get("recorded_repository"),
            "source_package_path": inspected.get("source_package_path"),
        },
        "safety": safety,
        "scope_bounded": scope_bounded,
        "tool": {
            "identity": inspected.get("tool_identity", UNKNOWN_TOOL),
            "identity_candidates": inspected.get("tool_identity_candidates", []),
            "version": fields.get("tool_versions", [None])[0] if fields.get("tool_versions") else None,
        },
        "trust_class": AUTHORITY_CLASS,
        "validation_status": "valid" if eligible else "quarantined",
    }


def _validate_output_root(repo_root: Path, output_root: str | Path) -> Path:
    requested = Path(output_root)
    if not requested.is_absolute():
        requested = repo_root / requested
    requested = requested.resolve()
    expected = (repo_root / ".codex-context" / "project-memory").resolve()
    if requested != expected:
        raise ValueError("Output root must be .codex-context/project-memory inside the repository")
    return requested


def _generated_at_from_run_id(run_id: str) -> str:
    match = _RUN_ID_RE.fullmatch(run_id)
    if not match:
        raise ValueError("run_id must use UTC YYYYMMDDTHHMMSSZ format")
    value = datetime(
        *(int(part) for part in match.groups()), tzinfo=timezone.utc,
    )
    return value.isoformat().replace("+00:00", "Z")


def _tool_inventory(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(envelope["tool"]["identity"] for envelope in envelopes)
    records: list[dict[str, Any]] = []
    for tool in (*KNOWN_TOOLS, UNKNOWN_TOOL):
        records.append({
            "artifact_count": counts.get(tool, 0),
            "default_eligible_artifact_count": sum(
                1 for envelope in envelopes
                if envelope["tool"]["identity"] == tool and envelope["consumption"]["default_eligible"]
            ),
            "live_execution_approved": False,
            "read_import_approved": tool in KNOWN_TOOLS,
            "tool_identity": tool,
        })
    return records


def _summary_markdown(metadata: dict[str, Any], envelopes: list[dict[str, Any]], findings: list[dict[str, Any]]) -> str:
    tools = Counter(envelope["tool"]["identity"] for envelope in envelopes)
    freshness = Counter(envelope["freshness"] for envelope in envelopes)
    lines = [
        "# Existing Context-Tool Evidence Import",
        "",
        "Generated Evidence — Not Project Authority",
        "",
        f"- Result: {metadata['result']}",
        f"- Task: `{metadata['task_id']}`",
        f"- Run: `{metadata['run_id']}`",
        f"- Branch: `{metadata['current_branch']}`",
        f"- Commit: `{metadata['current_commit']}`",
        f"- Artifacts: {len(envelopes)}",
        f"- Default eligible: {sum(1 for item in envelopes if item['consumption']['default_eligible'])}",
        f"- Quarantined: {sum(1 for item in envelopes if not item['consumption']['default_eligible'])}",
        "- Tool execution performed: false",
        "- Network access performed: false",
        "- Model call performed: false",
        "- Registry mutation performed: false",
        "",
        "## Artifact Counts by Tool",
        "",
    ]
    for key in sorted(tools):
        lines.append(f"- `{key}`: {tools[key]}")
    if not tools:
        lines.append("- None discovered")
    lines += ["", "## Artifact Counts by Freshness", ""]
    for key in sorted(freshness):
        lines.append(f"- `{key}`: {freshness[key]}")
    if not freshness:
        lines.append("- None discovered")
    lines += ["", "## Findings", ""]
    if findings:
        counts = Counter((item["severity"], item["code"]) for item in findings)
        for (severity, code), count in sorted(counts.items()):
            lines.append(f"- [{severity.upper()}] `{code}`: {count}")
    else:
        lines.append("- None")
    lines += [
        "",
        "## Boundary",
        "",
        "This package inventories existing generated artifacts read-only. It does not install or execute Repomix, Graphify, CCE, or any other context tool. Generated output is evidence only and cannot update project truth.",
        "",
    ]
    return "\n".join(lines)


def validate_context_evidence_package(package_dir: str | Path) -> dict[str, Any]:
    """Validate exact package membership, JSON, checksums, and safety flags."""
    path = Path(package_dir)
    errors: list[str] = []
    actual = sorted(item.name for item in path.iterdir() if item.is_file()) if path.is_dir() else []
    if actual != list(EXACT_PACKAGE_FILES):
        errors.append(f"Exact package mismatch: {actual}")
    if path.is_dir() and any(not item.is_file() for item in path.iterdir()):
        errors.append("Package contains a non-file entry")
    json_names = (
        "artifact-envelopes.json", "artifact-inventory.json", "findings.json",
        "run-metadata.json", "tool-inventory.json",
    )
    loaded: dict[str, Any] = {}
    for name in json_names:
        try:
            loaded[name] = json.loads((path / name).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid JSON {name}: {exc}")
    try:
        inventory = (path / "FILE-INVENTORY.txt").read_text(encoding="utf-8").splitlines()
        if inventory != list(EXACT_PACKAGE_FILES):
            errors.append("FILE-INVENTORY.txt does not match the exact package")
    except OSError as exc:
        errors.append(f"Cannot read FILE-INVENTORY.txt: {exc}")
    try:
        checksum_pairs = _parse_checksum_lines((path / "SHA256SUMS").read_text(encoding="utf-8"))
        expected_hashed = [name for name in EXACT_PACKAGE_FILES if name != "SHA256SUMS"]
        if sorted(name for _, name in checksum_pairs) != sorted(expected_hashed):
            errors.append("SHA256SUMS coverage mismatch")
        for expected, name in checksum_pairs:
            if not _safe_relative(name) or Path(name).name != name:
                errors.append(f"Unsafe package checksum path: {name}")
            elif _sha256(path / name) != expected:
                errors.append(f"Package checksum mismatch: {name}")
    except (OSError, ValueError) as exc:
        errors.append(f"Invalid SHA256SUMS: {exc}")

    metadata = loaded.get("run-metadata.json", {})
    required_flags = {
        "authority_class": AUTHORITY_CLASS,
        "model_call_performed": False,
        "network_access_performed": False,
        "registry_mutation_performed": False,
        "tool_execution_performed": False,
    }
    for key, expected in required_flags.items():
        if metadata.get(key) != expected:
            errors.append(f"run-metadata.json {key} must be {expected!r}")
    envelopes = loaded.get("artifact-envelopes.json", {}).get("artifacts", [])
    inventory_records = loaded.get("artifact-inventory.json", {}).get("artifacts", [])
    if len(envelopes) != len(inventory_records):
        errors.append("One envelope is required per discovered artifact")
    for envelope in envelopes:
        if envelope.get("authority_class") != AUTHORITY_CLASS or envelope.get("trust_class") != AUTHORITY_CLASS:
            errors.append(f"Envelope authority invalid: {envelope.get('artifact_id')}")
        if envelope.get("freshness") not in {"current", "stale", "historical", "unknown", "unusable"}:
            errors.append(f"Envelope freshness invalid: {envelope.get('artifact_id')}")
        if "default_eligible" not in envelope.get("consumption", {}):
            errors.append(f"Envelope eligibility missing: {envelope.get('artifact_id')}")
    return {"errors": errors, "result": "PASS" if not errors else "BLOCKED"}


def build_context_evidence_package(
    repo_root: str | Path,
    output_root: str | Path,
    task_id: str,
    run_id: str,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build one deterministic, ignored, atomic generated-evidence package."""
    root = _resolve_repo_root(repo_root)
    output = _validate_output_root(root, output_root)
    generated_at = generated_at or _generated_at_from_run_id(run_id)
    current_branch, current_commit = _read_git_identity(root)
    descriptors = discover_context_artifacts(root)
    inspections = [inspect_context_artifact(root, descriptor) for descriptor in descriptors]
    envelopes = [
        normalize_context_artifact(
            inspection, current_branch=current_branch, current_commit=current_commit,
        )
        for inspection in inspections
    ]
    envelopes.sort(key=lambda item: item["provenance"]["source_package_path"])
    all_findings: list[dict[str, Any]] = []
    for envelope in envelopes:
        for finding in envelope["findings"]:
            all_findings.append({
                **finding,
                "artifact_id": envelope["artifact_id"],
                "source_package_path": envelope["provenance"]["source_package_path"],
            })
    all_findings.sort(key=lambda item: (item["severity"], item["code"], item["source_package_path"], item["message"]))
    result = "PASS_WITH_FINDINGS" if all_findings else "PASS"
    run_dir = output / task_id / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")

    metadata = {
        "adapter_name": ADAPTER_NAME,
        "adapter_version": ADAPTER_VERSION,
        "authority_class": AUTHORITY_CLASS,
        "command": f"python3 scripts/project_memory/build_context_tool_evidence.py --repo-root . --output-root .codex-context/project-memory --task-id {task_id} --run-id {run_id} --json",
        "current_branch": current_branch,
        "current_commit": current_commit,
        "generated_at": generated_at,
        "model_call_performed": False,
        "network_access_performed": False,
        "package_version": PACKAGE_VERSION,
        "registry_mutation_performed": False,
        "repository_root": str(root),
        "result": result,
        "run_id": run_id,
        "source_roots": list(SOURCE_ROOTS),
        "task_id": task_id,
        "tool_execution_performed": False,
    }
    artifact_inventory = {
        "artifact_count": len(envelopes),
        "artifacts": [
            {
                "artifact_id": envelope["artifact_id"],
                "consumption_status": envelope["consumption"]["status"],
                "freshness": envelope["freshness"],
                "source_package_path": envelope["provenance"]["source_package_path"],
                "tool_identity": envelope["tool"]["identity"],
            }
            for envelope in envelopes
        ],
        "excluded_roots": [".codex-context/project-memory"],
    }
    findings_data = {
        "by_code": dict(sorted(Counter(item["code"] for item in all_findings).items())),
        "by_severity": dict(sorted(Counter(item["severity"] for item in all_findings).items())),
        "finding_count": len(all_findings),
        "findings": all_findings,
        "result": result,
    }

    temp_parent = output.parent
    temp_parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"context_evidence_{task_id}_", dir=temp_parent))
    try:
        tmp_run = tmp_dir / task_id / run_id
        tmp_run.mkdir(parents=True, exist_ok=False)
        _write_json(tmp_run / "run-metadata.json", metadata)
        _write_json(tmp_run / "tool-inventory.json", {"tools": _tool_inventory(envelopes)})
        _write_json(tmp_run / "artifact-inventory.json", artifact_inventory)
        _write_json(tmp_run / "artifact-envelopes.json", {"artifacts": envelopes, "envelope_version": ENVELOPE_VERSION})
        _write_json(tmp_run / "findings.json", findings_data)
        (tmp_run / "summary.md").write_text(
            _summary_markdown(metadata, envelopes, all_findings), encoding="utf-8",
        )
        (tmp_run / "FILE-INVENTORY.txt").write_text(
            "\n".join(EXACT_PACKAGE_FILES) + "\n", encoding="utf-8",
        )
        checksum_lines = [
            f"{_sha256(tmp_run / name)}  {name}"
            for name in EXACT_PACKAGE_FILES if name != "SHA256SUMS"
        ]
        (tmp_run / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
        validation = validate_context_evidence_package(tmp_run)
        if validation["result"] != "PASS":
            raise RuntimeError("Generated package validation failed: " + "; ".join(validation["errors"]))
        output.mkdir(parents=True, exist_ok=True)
        task_dir = output / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        os.rename(tmp_run, run_dir)
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return {
        "artifact_count": len(envelopes),
        "authority_class": AUTHORITY_CLASS,
        "bound_branch": current_branch,
        "bound_commit": current_commit,
        "default_eligible_count": sum(1 for item in envelopes if item["consumption"]["default_eligible"]),
        "finding_count": len(all_findings),
        "model_call_performed": False,
        "network_access_performed": False,
        "output_directory": str(run_dir),
        "quarantined_count": sum(1 for item in envelopes if not item["consumption"]["default_eligible"]),
        "registry_mutation_performed": False,
        "result": result,
        "run_id": run_id,
        "task_id": task_id,
        "tool_execution_performed": False,
    }
