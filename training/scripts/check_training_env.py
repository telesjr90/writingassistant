from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.metadata
import io
import json
import platform
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
MODEL_CONFIG = TRAINING_DIR / "configs" / "model_sources.yaml"
MODEL_MANIFEST_DIR = TRAINING_DIR / "models" / "manifests"
DATASET_MANIFEST = TRAINING_DIR / "data" / "dataset_manifest.json"
MIN_PYTHON = (3, 10)
MAX_SUPPORTED_PYTHON = (3, 13)
DEFAULT_TRAINING_GATE = 500


@dataclass
class Check:
    name: str
    status: str
    detail: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check the isolated Unsloth training environment, local Hugging Face "
            "model cache, and dataset gate. This script does not train models."
        )
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when environment or model checks fail.",
    )
    return parser.parse_args(argv)


def status_line(check: Check) -> str:
    return f"[{check.status}] {check.name}: {check.detail}"


def sanitized_repo_id(repo_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", repo_id).strip("_")


def relative_path(path: Path | None) -> str:
    if path is None:
        return "not found"
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_workspace_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def read_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#") or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def package_version(module_name: str, package_name: str | None = None) -> str:
    package = package_name or module_name
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        module = sys.modules.get(module_name)
        version = getattr(module, "__version__", None)
        return str(version) if version else "version unknown"


def import_check(module_name: str, package_name: str | None = None) -> tuple[bool, str]:
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            importlib.import_module(module_name)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, package_version(module_name, package_name)


def check_python() -> Check:
    version = sys.version_info
    detail = f"{platform.python_version()} at {sys.executable}"
    if version < MIN_PYTHON:
        return Check("Python version", "FAIL", f"{detail}; expected Python 3.10+")
    if version[:2] > MAX_SUPPORTED_PYTHON:
        return Check("Python version", "WARN", f"{detail}; validate Unsloth support for this version")
    return Check("Python version", "PASS", detail)


def check_platform() -> Check:
    system = platform.system()
    detail = platform.platform()
    if system == "Linux":
        return Check("Platform", "PASS", detail)
    if system == "Windows":
        return Check("Platform", "WARN", f"{detail}; WSL/Linux is recommended for Unsloth QLoRA")
    return Check("Platform", "WARN", f"{detail}; WSL/Linux with NVIDIA CUDA is recommended")


def check_torch_and_cuda() -> tuple[list[Check], bool]:
    ok, detail = import_check("torch")
    if not ok:
        return [Check("torch import", "FAIL", detail)], False

    import torch  # type: ignore[import-not-found]

    checks = [Check("torch import", "PASS", detail)]
    cuda_version = getattr(torch.version, "cuda", None)
    cuda_available = bool(torch.cuda.is_available())
    if cuda_available:
        checks.append(Check("CUDA availability", "PASS", f"torch CUDA={cuda_version}; CUDA is available"))
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            memory_gib = props.total_memory / (1024**3)
            checks.append(
                Check(
                    f"GPU {index}",
                    "PASS",
                    f"{torch.cuda.get_device_name(index)}; {memory_gib:.1f} GiB total memory",
                )
            )
    else:
        checks.append(
            Check(
                "CUDA availability",
                "FAIL",
                f"torch CUDA={cuda_version}; CUDA is not available to this Python environment",
            )
        )
    return checks, cuda_available


def check_imports() -> list[Check]:
    checks: list[Check] = []
    for module_name, package_name in (
        ("unsloth", None),
        ("transformers", None),
        ("datasets", None),
        ("trl", None),
        ("huggingface_hub", None),
    ):
        ok, detail = import_check(module_name, package_name)
        checks.append(
            Check(
                f"{module_name} import",
                "PASS" if ok else "FAIL",
                detail,
            )
        )
    return checks


def primary_model_paths() -> tuple[Path, Path | None, str]:
    config = read_simple_yaml(MODEL_CONFIG)
    repo_id = config.get("primary_model_id", "Qwen/Qwen2.5-7B-Instruct")
    cache_dir = resolve_workspace_path(
        config.get("local_cache_dir"),
        TRAINING_DIR / "models" / "hf_cache",
    )
    manifest = MODEL_MANIFEST_DIR / f"primary_{sanitized_repo_id(repo_id)}.manifest.json"
    manifest_data = read_json(manifest)
    local_path_value = None
    if manifest_data:
        local_path = manifest_data.get("local_path")
        if isinstance(local_path, str) and local_path:
            local_path_value = local_path
    local_path = resolve_workspace_path(
        local_path_value,
        cache_dir / sanitized_repo_id(repo_id),
    )
    return manifest, local_path, repo_id


def check_primary_model() -> tuple[list[Check], bool]:
    manifest, local_path, repo_id = primary_model_paths()
    checks: list[Check] = []
    manifest_data = read_json(manifest)
    if manifest.exists() and manifest_data is not None:
        status = str(manifest_data.get("retrieval_status", "unknown"))
        checks.append(
            Check(
                "Primary model manifest",
                "PASS",
                f"{relative_path(manifest)} for {repo_id}; retrieval_status={status}",
            )
        )
    elif manifest.exists():
        checks.append(Check("Primary model manifest", "FAIL", f"{relative_path(manifest)} is not valid JSON"))
    else:
        checks.append(Check("Primary model manifest", "FAIL", f"{relative_path(manifest)} is missing"))

    if local_path.exists():
        checks.append(Check("Local primary model path", "PASS", relative_path(local_path)))
        model_ready = manifest_data is not None
    else:
        checks.append(Check("Local primary model path", "FAIL", f"{relative_path(local_path)} is missing"))
        model_ready = False

    return checks, model_ready


def check_dataset_gate() -> tuple[Check, bool]:
    manifest = read_json(DATASET_MANIFEST)
    if manifest is None:
        return (
            Check(
                "Dataset eligibility gate",
                "WARN",
                f"{relative_path(DATASET_MANIFEST)} is unavailable; run training/scripts/update_dataset_manifest.py",
            ),
            False,
        )

    readiness = manifest.get("current_readiness")
    if not isinstance(readiness, dict):
        return Check("Dataset eligibility gate", "WARN", "current_readiness is missing"), False

    count = int(readiness.get("eligible_for_training_records_counted_toward_500_gate") or 0)
    target = readiness.get("target_record_range")
    minimum = DEFAULT_TRAINING_GATE
    if isinstance(target, dict):
        minimum = int(target.get("minimum") or DEFAULT_TRAINING_GATE)
    status = str(readiness.get("status", "unknown"))
    active_seed = readiness.get("active_seed_file")
    detail = (
        f"{count}/{minimum} eligible_for_training records; "
        f"current_readiness.status={status}; active_seed_file={active_seed}"
    )
    if count >= minimum and status == "ready":
        return Check("Dataset eligibility gate", "PASS", detail), True
    return Check("Dataset eligibility gate", "BLOCKED", detail), False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    checks: list[Check] = [check_python(), check_platform()]
    torch_checks, cuda_ready = check_torch_and_cuda()
    checks.extend(torch_checks)
    checks.extend(check_imports())
    model_checks, model_ready = check_primary_model()
    checks.extend(model_checks)
    dataset_check, dataset_ready = check_dataset_gate()
    checks.append(dataset_check)

    print("Unsloth training environment check")
    print(f"Repository: {REPO_ROOT}")
    for check in checks:
        print(status_line(check))

    environment_ready = cuda_ready and all(
        check.status == "PASS"
        for check in checks
        if check.name.endswith("import") or check.name in {"Python version"}
    )
    print()
    print(f"Environment ready: {'yes' if environment_ready else 'no'}")
    print(f"Primary model ready: {'yes' if model_ready else 'no'}")
    print(f"Full training ready: {'yes' if environment_ready and model_ready and dataset_ready else 'no'}")
    if not dataset_ready:
        print("Full training remains blocked until the dataset manifest shows 500+ eligible_for_training records.")

    if args.strict and any(check.status == "FAIL" for check in checks):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
