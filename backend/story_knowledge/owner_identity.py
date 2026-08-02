"""Read-only server-authoritative project owner identity."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any

from backend.story_knowledge.apply_contract import (
    ApplyContractError,
    MAX_REQUEST_BYTES,
    canonical_sha256,
    require_closed_object,
    require_integer,
    require_string,
    strict_json_loads,
    validate_safe_id,
    validate_timestamp,
)


OWNER_CONFIG_RELATIVE_PATH = Path("writer_assistant/config/local_owner.json")


def owner_config_path(project_dir: str | Path) -> Path:
    return Path(project_dir) / OWNER_CONFIG_RELATIVE_PATH


def _read_safe_regular_file(project_dir: Path, path: Path) -> bytes:
    try:
        root = project_dir.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ApplyContractError("OWNER_CONFIGURATION_REQUIRED") from exc

    candidate = root
    for component in OWNER_CONFIG_RELATIVE_PATH.parts:
        candidate = candidate / component
        if candidate.is_symlink():
            raise ApplyContractError("OWNER_CONFIGURATION_UNSAFE")
    try:
        metadata = os.lstat(candidate)
    except FileNotFoundError as exc:
        raise ApplyContractError("OWNER_CONFIGURATION_REQUIRED") from exc
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or metadata.st_size > MAX_REQUEST_BYTES
    ):
        raise ApplyContractError("OWNER_CONFIGURATION_UNSAFE")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, ValueError) as exc:
        raise ApplyContractError("OWNER_CONFIGURATION_UNSAFE") from exc
    if resolved != path.resolve(strict=True):
        raise ApplyContractError("OWNER_CONFIGURATION_UNSAFE")
    return resolved.read_bytes()


def validate_owner_config(value: Any, *, project_id: str) -> dict[str, Any]:
    config = require_closed_object(
        value,
        required={
            "schema_version",
            "project_id",
            "owner_id",
            "display_name",
            "config_version",
            "updated_at",
        },
        label="local owner configuration",
    )
    if config["schema_version"] != "local_owner_identity.v1":
        raise ApplyContractError("OWNER_CONFIGURATION_INVALID")
    validate_safe_id(project_id, "project_id")
    if validate_safe_id(config["project_id"], "project_id") != project_id:
        raise ApplyContractError("OWNER_CONFIGURATION_PROJECT_MISMATCH")
    validate_safe_id(config["owner_id"], "owner_id")
    require_string(config["display_name"], label="display_name", minimum=1, maximum=160)
    require_integer(
        config["config_version"],
        label="config_version",
        minimum=1,
        maximum=2_147_483_647,
    )
    validate_timestamp(config["updated_at"], "updated_at")
    return dict(config)


def load_local_owner_identity(
    project_dir: str | Path,
    *,
    project_id: str,
) -> dict[str, Any]:
    """Load the sole owner identity source without creating or mutating files."""

    project_root = Path(project_dir)
    path = owner_config_path(project_root)
    raw = _read_safe_regular_file(project_root, path)
    config = validate_owner_config(
        strict_json_loads(raw, max_bytes=MAX_REQUEST_BYTES),
        project_id=project_id,
    )
    return {
        "actor_type": "owner",
        "owner_id": config["owner_id"],
        "display_name": config["display_name"],
        "identity_source": "project_local_owner_config",
        "config_version": config["config_version"],
        "config_hash": canonical_sha256(config),
    }


__all__ = (
    "OWNER_CONFIG_RELATIVE_PATH",
    "load_local_owner_identity",
    "owner_config_path",
    "validate_owner_config",
)
