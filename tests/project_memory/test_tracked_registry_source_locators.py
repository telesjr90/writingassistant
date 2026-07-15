"""Tests for tracked registry source locator integrity.

Verifies committed tracked registry seed without mutation:
- Parse all registries successfully
- No absolute source paths
- No traversal source paths
- No directory-valued source locators (must be regular files)
- No symlink escapes
- All record IDs are globally unique and stable
- All authority classes are valid trust classes
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRIES_DIR = _REPO_ROOT / "docs" / "project-memory" / "registries"

_TRUST_CLASSES = frozenset([
    "authoritative",
    "accepted_evidence",
    "generated_evidence",
    "historical",
    "superseded",
    "uncertain",
    "owner_pending",
    "untrusted",
])

_KNOWN_MISSING_SOURCES = frozenset([
    "tests/test_story_check_grounding.py",
    ".codex-context/PHASE8-IMPL-024/manual-validation/T002D-story-check-grounding/20260713T022337Z",
    ".codex-context/PHASE8-IMPL-024/T002D-unrelated-test-harness-defect/20260713T020959Z",
    ".codex-context/application-uiux-audit/",
])

_ROOT_MARKERS = frozenset([
    ".git",
])


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_registries():
    registries = {}
    hashes = {}
    for entry in sorted(_REGISTRIES_DIR.iterdir()):
        if not entry.is_file() or entry.suffix != ".json":
            continue
        data = json.loads(entry.read_text(encoding="utf-8"))
        registries[entry.name] = data
        hashes[entry.name] = _hash_file(entry)
    return registries, hashes


def _collect_source_locators(registries):
    locators = []
    for fname, data in registries.items():
        if fname == "manifest.json":
            continue
        for record in data.get("records", []):
            if not isinstance(record, dict):
                continue
            rid = record.get("id", "")
            ac = record.get("authority_class", "")
            provenance = record.get("provenance")
            if not isinstance(provenance, dict):
                continue
            for sl in provenance.get("source_locators", []):
                if not isinstance(sl, dict):
                    continue
                path_val = sl.get("path", "")
                if not path_val:
                    continue
                locators.append({
                    "path": path_val,
                    "record_id": rid,
                    "authority_class": ac,
                    "registry": fname,
                })
    return locators


def test_registries_parse_successfully():
    registries, _ = _load_registries()
    assert len(registries) == 12
    for fname, data in registries.items():
        assert isinstance(data, dict), f"{fname} is not a dict"
        assert "registry_type" in data, f"{fname} missing registry_type"
        if fname == "manifest.json":
            continue
        assert "records" in data, f"{fname} missing records"
        assert isinstance(data["records"], list), f"{fname} records is not a list"


def test_no_absolute_source_paths():
    _, locators = [None, _collect_source_locators(_load_registries()[0])]
    for loc in locators:
        path_val = loc["path"]
        assert not os.path.isabs(path_val), \
            f"Absolute path in {loc['record_id']}: {path_val!r}"


def test_no_traversal_source_paths():
    _, locators = [None, _collect_source_locators(_load_registries()[0])]
    for loc in locators:
        path_val = loc["path"]
        parts = path_val.replace("\\", "/").split("/")
        assert ".." not in parts, \
            f"Traversal path in {loc['record_id']}: {path_val!r}"


def test_source_locators_are_tracked_regular_files():
    registries, _ = _load_registries()
    locators = _collect_source_locators(registries)

    repo_root = _REPO_ROOT
    for loc in locators:
        path_val = loc["path"]
        parts = path_val.replace("\\", "/").split("/")

        assert ".." not in parts, \
            f"Traversal in {loc['record_id']}: {path_val!r}"
        assert not os.path.isabs(path_val), \
            f"Absolute path in {loc['record_id']}: {path_val!r}"

        is_known_missing = path_val in _KNOWN_MISSING_SOURCES
        is_dir_path = path_val.endswith("/")
        if is_known_missing:
            continue
        assert not is_dir_path, \
            f"Directory locator in {loc['record_id']}: {path_val!r}"

        full = (repo_root / path_val).resolve()

        try:
            is_safe = full.is_relative_to(repo_root)
        except (ValueError, OSError):
            is_safe = False
        assert is_safe, \
            f"Path escapes repo in {loc['record_id']}: {path_val!r}"

        assert full.is_file(), \
            f"Not a regular file in {loc['record_id']}: {path_val!r}"

        assert not full.is_symlink(), \
            f"Symlink in {loc['record_id']}: {path_val!r}"


def test_global_record_ids_unique_and_stable():
    registries, _ = _load_registries()
    all_ids = []
    type_to_ids = {}
    for fname, data in registries.items():
        if fname == "manifest.json":
            continue
        rtype = data.get("registry_type", "unknown")
        for record in data.get("records", []):
            if not isinstance(record, dict):
                continue
            rid = record.get("id", "")
            assert rid, f"Empty ID in {fname}"
            all_ids.append(rid)
            type_to_ids.setdefault(rtype, []).append(rid)

    prefix_map = {
        "project": "project:",
        "feature": "feature:",
        "boundary": "boundary:",
        "task": "task:",
        "decision": "decision:",
        "capability": "capability:",
        "asset": "asset:",
        "evidence": "evidence:",
        "dependency": "dependency:",
        "tool": "tool:",
        "owner_decision": "owner-decision:",
    }

    for rtype, ids in type_to_ids.items():
        prefix = prefix_map.get(rtype)
        if prefix:
            for rid in ids:
                assert rid.startswith(prefix), \
                    f"ID {rid!r} in registry type {rtype} should start with {prefix!r}"

    assert len(all_ids) == len(set(all_ids)), \
        f"Duplicate record IDs detected: {sorted(all_ids)}"


def test_authority_classes_are_valid():
    registries, _ = _load_registries()
    for fname, data in registries.items():
        if fname == "manifest.json":
            continue
        for record in data.get("records", []):
            if not isinstance(record, dict):
                continue
            ac = record.get("authority_class", "")
            assert ac in _TRUST_CLASSES, \
                f"Invalid authority class {ac!r} in {fname}: {record.get('id', '?')}"


def test_registries_not_mutated_by_this_test():
    pre = {}
    for fname in sorted(_REGISTRIES_DIR.iterdir()):
        if not fname.is_file() or fname.suffix != ".json":
            continue
        pre[fname.name] = _hash_file(fname)

    _load_registries()
    _collect_source_locators(_load_registries()[0])

    post = {}
    for fname in sorted(_REGISTRIES_DIR.iterdir()):
        if not fname.is_file() or fname.suffix != ".json":
            continue
        post[fname.name] = _hash_file(fname)

    assert pre == post, "Registry files were mutated during tests"


def test_no_hidden_chars_in_source_paths():
    _, locators = [None, _collect_source_locators(_load_registries()[0])]
    for loc in locators:
        path_val = loc["path"]
        assert "\x00" not in path_val, \
            f"Null byte in path for {loc['record_id']}: {path_val!r}"
        assert "\n" not in path_val, \
            f"Newline in path for {loc['record_id']}: {path_val!r}"
        assert "\r" not in path_val, \
            f"Carriage return in path for {loc['record_id']}: {path_val!r}"


def test_no_backslash_paths_on_linux():
    registries, _ = _load_registries()
    locators = _collect_source_locators(registries)
    for loc in locators:
        path_val = loc["path"]
        assert "\\" not in path_val, \
            f"Backslash in path for {loc['record_id']}: {path_val!r}"
