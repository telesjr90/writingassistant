from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
DEFAULT_CONFIG = TRAINING_DIR / "configs" / "model_sources.yaml"
DEFAULT_MANIFEST_DIR = TRAINING_DIR / "models" / "manifests"

MODEL_FIELDS = {
    "primary": ("primary_model_id", "primary_model_url"),
    "fallback": ("fallback_model_id", "fallback_model_url"),
}

DISALLOWED_MODEL_MARKERS = {
    "qwen3:8b",
    "qwen/qwen3:8b",
}

AUTH_ERROR_MARKERS = (
    "401",
    "403",
    "authorization",
    "authentication",
    "credentials",
    "forbidden",
    "gated",
    "login",
    "private",
    "token",
    "unauthorized",
)

TOKENIZER_FILENAMES = {
    "tokenizer.json",
    "tokenizer.model",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "spiece.model",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve or verify explicit Hugging Face model artifacts for Phase 3 "
            "fine-tuning preparation. This script does not train models."
        )
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to training/configs/model_sources.yaml.",
    )
    parser.add_argument("--primary", action="store_true", help="Select the primary base model.")
    parser.add_argument("--fallback", action="store_true", help="Select the fallback model.")
    parser.add_argument("--all", action="store_true", help="Select primary and fallback models.")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify local cached artifacts without downloading missing files.",
    )
    parser.add_argument(
        "--local-dir",
        type=Path,
        help="Override the configured local cache directory.",
    )
    return parser.parse_args(argv)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relative_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_workspace_path(value: str | Path | None, default: Path) -> Path:
    if value is None or str(value).strip() == "":
        return default
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def sanitized_repo_id(repo_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", repo_id).strip("_")


def local_model_dir(cache_dir: Path, repo_id: str) -> Path:
    return cache_dir / sanitized_repo_id(repo_id)


def load_config(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        raise ValueError(f"could not read config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"could not parse YAML config {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level mapping")

    required = [
        "primary_model_id",
        "primary_model_url",
        "fallback_model_id",
        "fallback_model_url",
        "local_cache_dir",
    ]
    missing = [key for key in required if not isinstance(data.get(key), str) or not data[key]]
    if missing:
        raise ValueError(f"{path} is missing required string field(s): {', '.join(missing)}")

    for key in ("primary_model_id", "fallback_model_id"):
        normalized = str(data[key]).strip().lower()
        if normalized in DISALLOWED_MODEL_MARKERS:
            raise ValueError(
                f"{path} references disallowed model {data[key]!r}; qwen3:8b must not be retrieved."
            )

    return data


def selected_model_roles(args: argparse.Namespace) -> list[str]:
    roles: list[str] = []
    if args.all:
        roles.extend(["primary", "fallback"])
    else:
        if args.primary:
            roles.append("primary")
        if args.fallback:
            roles.append("fallback")

    if not roles:
        raise ValueError("select at least one model with --primary, --fallback, or --all")

    return roles


def model_entry(config: dict[str, Any], role: str) -> dict[str, str]:
    id_key, url_key = MODEL_FIELDS[role]
    return {
        "role": role,
        "repo_id": str(config[id_key]),
        "source_url": str(config[url_key]),
    }


def is_auth_error(exc: BaseException | str) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in AUTH_ERROR_MARKERS)


def import_hf() -> tuple[Any | None, Any | None, str | None]:
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        return None, None, str(exc)
    return HfApi, snapshot_download, None


def inspect_local_path(local_path: Path | None) -> dict[str, Any]:
    if local_path is None or not local_path.exists():
        return {
            "local_path_exists": False,
            "files_present": [],
            "file_count": 0,
            "config_status": {
                "config_json_present": False,
                "generation_config_json_present": False,
                "ok": False,
            },
            "tokenizer_status": {
                "files_present": [],
                "ok": False,
            },
        }

    files = sorted(path for path in local_path.rglob("*") if path.is_file())
    relative_files = [path.relative_to(local_path).as_posix() for path in files]
    file_names = {path.name for path in files}
    tokenizer_files = sorted(file_names.intersection(TOKENIZER_FILENAMES))

    return {
        "local_path_exists": True,
        "files_present": relative_files,
        "file_count": len(relative_files),
        "config_status": {
            "config_json_present": "config.json" in file_names,
            "generation_config_json_present": "generation_config.json" in file_names,
            "ok": "config.json" in file_names,
        },
        "tokenizer_status": {
            "files_present": tokenizer_files,
            "ok": bool(tokenizer_files),
        },
    }


def fetch_model_metadata(repo_id: str) -> dict[str, Any]:
    HfApi, _snapshot_download, import_error = import_hf()
    if import_error:
        return {
            "available": False,
            "error": f"huggingface_hub unavailable: {import_error}",
            "authentication_required": None,
        }

    try:
        info = HfApi().model_info(repo_id=repo_id)
    except Exception as exc:  # pragma: no cover - depends on network/auth state
        return {
            "available": False,
            "error": str(exc),
            "authentication_required": True if is_auth_error(exc) else None,
        }

    gated = getattr(info, "gated", None)
    private = bool(getattr(info, "private", False))
    authentication_required = private or gated not in (None, False, "false")
    siblings = [s.rfilename for s in (getattr(info, "siblings", None) or [])]

    return {
        "available": True,
        "sha": getattr(info, "sha", None),
        "gated": gated,
        "private": private,
        "authentication_required": bool(authentication_required),
        "siblings_count": len(siblings),
        "sample_siblings": siblings[:50],
    }


def build_manifest(
    entry: dict[str, str],
    cache_dir: Path,
    mode: str,
    local_path: Path | None,
    retrieval_status: str,
    metadata: dict[str, Any] | None,
    warnings: list[str],
    errors: list[str],
    previous_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inspection = inspect_local_path(local_path)
    authentication_required = None
    if metadata and "authentication_required" in metadata:
        authentication_required = metadata["authentication_required"]
    if authentication_required is None and previous_manifest:
        previous_auth = previous_manifest.get("authentication_required")
        if previous_auth is not None:
            authentication_required = previous_auth
    if authentication_required is not True and any(is_auth_error(error) for error in errors):
        authentication_required = True

    owner_action = None
    if authentication_required is True:
        owner_action = "Run huggingface-cli login, then rerun this script."

    final_metadata = metadata or {}
    if previous_manifest and final_metadata.get("note"):
        previous_metadata = previous_manifest.get("metadata")
        if isinstance(previous_metadata, dict) and previous_metadata.get("available"):
            final_metadata = {
                **final_metadata,
                "last_successful_download_metadata": previous_metadata,
            }

    last_successful_retrieval = None
    if previous_manifest and previous_manifest.get("retrieval_status") == "retrieved":
        last_successful_retrieval = {
            "retrieval_timestamp": previous_manifest.get("retrieval_timestamp"),
            "local_path": previous_manifest.get("local_path"),
            "authentication_required": previous_manifest.get("authentication_required"),
            "metadata": previous_manifest.get("metadata", {}),
        }

    manifest = {
        "manifest_version": 1,
        "retrieval_timestamp": utc_now(),
        "retriever": relative_path(Path(__file__).resolve()),
        "mode": mode,
        "retrieval_status": retrieval_status,
        "repo_id": entry["repo_id"],
        "source_url": entry["source_url"],
        "role": entry["role"],
        "repo_type": "model",
        "local_cache_dir": relative_path(cache_dir),
        "local_path": relative_path(local_path),
        "authentication_required": authentication_required,
        "authentication_note": owner_action,
        "metadata": final_metadata,
        "last_successful_retrieval": last_successful_retrieval,
        "warnings": warnings,
        "errors": errors,
    }
    manifest.update(inspection)
    return manifest


def manifest_path_for(manifest_dir: Path, entry: dict[str, str]) -> Path:
    filename = f"{entry['role']}_{sanitized_repo_id(entry['repo_id'])}.manifest.json"
    return manifest_dir / filename


def read_existing_manifest(manifest_dir: Path, entry: dict[str, str]) -> dict[str, Any] | None:
    manifest_path = manifest_path_for(manifest_dir, entry)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def write_manifest(manifest_dir: Path, entry: dict[str, str], manifest: dict[str, Any]) -> Path:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_path_for(manifest_dir, entry)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return manifest_path


def verify_local_snapshot(entry: dict[str, str], cache_dir: Path) -> tuple[Path | None, list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    target_dir = local_model_dir(cache_dir, entry["repo_id"])
    _HfApi, snapshot_download, import_error = import_hf()
    if import_error:
        errors.append(f"huggingface_hub unavailable: {import_error}")
        return None, warnings, errors

    try:
        local_path = Path(
            snapshot_download(
                repo_id=entry["repo_id"],
                repo_type="model",
                local_dir=str(target_dir),
                local_files_only=True,
            )
        )
        return local_path, warnings, errors
    except Exception as exc:  # pragma: no cover - cache state varies
        if target_dir.exists() and any(target_dir.rglob("*")):
            warnings.append(f"Official local snapshot check failed, but files exist in local_dir: {exc}")
            return target_dir, warnings, errors
        warnings.append(f"Local snapshot is not available yet: {exc}")
        return None, warnings, errors


def retrieve_snapshot(
    entry: dict[str, str],
    cache_dir: Path,
) -> tuple[Path | None, dict[str, Any] | None, str, list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    metadata = fetch_model_metadata(entry["repo_id"])
    target_dir = local_model_dir(cache_dir, entry["repo_id"])
    _HfApi, snapshot_download, import_error = import_hf()
    if import_error:
        errors.append(f"huggingface_hub unavailable: {import_error}")
        return None, metadata, "failed", warnings, errors

    try:
        local_path = Path(
            snapshot_download(
                repo_id=entry["repo_id"],
                repo_type="model",
                local_dir=str(target_dir),
            )
        )
        return local_path, metadata, "retrieved", warnings, errors
    except Exception as exc:  # pragma: no cover - depends on network/auth state
        errors.append(str(exc))
        if is_auth_error(exc):
            warnings.append("Authentication or access approval may be required; run huggingface-cli login.")
        local_path = target_dir if target_dir.exists() else None
        return local_path, metadata, "failed", warnings, errors


def process_model(
    entry: dict[str, str],
    cache_dir: Path,
    manifest_dir: Path,
    verify_only: bool,
) -> tuple[Path, bool]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    mode = "verify-only" if verify_only else "download"

    if verify_only:
        local_path, warnings, errors = verify_local_snapshot(entry, cache_dir)
        inspection = inspect_local_path(local_path)
        if local_path is None:
            status = "not_cached"
        elif inspection["config_status"]["ok"] and inspection["tokenizer_status"]["ok"]:
            status = "verified"
        else:
            status = "incomplete"
        metadata = {
            "authentication_required": None,
            "note": "Network metadata was not fetched in verify-only mode.",
        }
    else:
        local_path, metadata, status, warnings, errors = retrieve_snapshot(entry, cache_dir)

    previous_manifest = read_existing_manifest(manifest_dir, entry)
    manifest = build_manifest(
        entry=entry,
        cache_dir=cache_dir,
        mode=mode,
        local_path=local_path,
        retrieval_status=status,
        metadata=metadata,
        warnings=warnings,
        errors=errors,
        previous_manifest=previous_manifest,
    )
    manifest_path = write_manifest(manifest_dir, entry, manifest)
    ok = status in {"retrieved", "verified", "not_cached"} and not errors
    print(
        f"{entry['role']}: {entry['repo_id']} -> {status}; "
        f"manifest={relative_path(manifest_path)}; local_path={relative_path(local_path)}"
    )
    if manifest.get("authentication_required") is True:
        print("Authentication required or likely required. Run huggingface-cli login.", file=sys.stderr)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return manifest_path, ok


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        roles = selected_model_roles(args)
    except ValueError as exc:
        print(f"retrieve_hf_models.py: error: {exc}", file=sys.stderr)
        return 2

    cache_dir = resolve_workspace_path(args.local_dir, resolve_workspace_path(config["local_cache_dir"], TRAINING_DIR / "models" / "hf_cache"))
    manifest_dir = DEFAULT_MANIFEST_DIR
    entries = [model_entry(config, role) for role in roles]

    all_ok = True
    for entry in entries:
        _manifest_path, ok = process_model(
            entry=entry,
            cache_dir=cache_dir,
            manifest_dir=manifest_dir,
            verify_only=args.verify_only,
        )
        all_ok = all_ok and ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
