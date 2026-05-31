from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
REPORTS_DIR = TRAINING_DIR / "reports"
MODEL_SOURCES = TRAINING_DIR / "configs" / "model_sources.yaml"
MODEL_MANIFEST_DIR = TRAINING_DIR / "models" / "manifests"
DATASET_MANIFEST = TRAINING_DIR / "data" / "dataset_manifest.json"

BLOCKED_TRAIN_ELIGIBILITIES = {
    "draft",
    "draft_needs_human_review",
    "blocked",
    "eval-only",
    "eligible_for_eval_only",
    "unresolved-source",
    "unresolved_source",
    "review-candidate",
    "review_candidate",
    "external-license-unreviewed",
    "external_license_unreviewed",
}
REQUIRED_CONFIG_KEYS = {
    "model_id",
    "model_source_url",
    "fallback_model_id",
    "fallback_model_source_url",
    "model_cache_dir",
    "require_local_model",
    "min_full_training_records",
    "allow_smoke_training_below_gate",
    "quantization",
    "max_seq_length",
    "lora_r",
    "lora_alpha",
    "lora_dropout",
    "target_modules",
    "learning_rate",
    "num_train_epochs",
    "per_device_train_batch_size",
    "gradient_accumulation_steps",
    "eval_steps",
    "save_steps",
    "seed",
    "output_dir",
}


@dataclass
class Gate:
    name: str
    passed: bool
    detail: str


@dataclass
class JsonlSummary:
    path: Path
    record_count: int
    format_name: str
    task_counts: Counter[str]
    eligibility_counts: Counter[str]
    blocked_eligibilities: Counter[str]
    errors: list[str]


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected a boolean value, got {value!r}.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Strict-gated Unsloth QLoRA trainer for the Dramatica analyst model. "
            "Dry-run mode validates readiness without loading a model or training."
        )
    )
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--train-file", type=Path)
    parser.add_argument("--eval-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-steps", type=int)
    parser.add_argument("--use-fallback-model", action="store_true")
    parser.add_argument("--allow-download", nargs="?", const="true", default="false", type=parse_bool)
    parser.add_argument("--allow-smoke-below-gate", action="store_true")
    parser.add_argument("--require-full-gate", action="store_true")
    parser.add_argument(
        "--cloud-or-larger-gpu-confirmed",
        action="store_true",
        help="Acknowledge that full primary-model training is running on a suitable non-local GPU path.",
    )
    return parser.parse_args(argv)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_path(value: str | Path | None, default: Path | None = None) -> Path:
    if value is None:
        if default is None:
            raise ValueError("Path value is required.")
        return default
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def sanitized_repo_id(repo_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", repo_id).strip("_")


def scalar(value: str) -> Any:
    raw = value.strip().strip("'\"")
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)(?:e[+-]?\d+)?", raw, re.IGNORECASE):
        return float(raw)
    if re.fullmatch(r"-?\d+(?:e[+-]?\d+)", raw, re.IGNORECASE):
        return float(raw)
    return raw


def read_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"Could not read YAML file {path}: {exc}") from exc

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"{path}:{line_number}: list item without a list key")
            data[current_list_key].append(scalar(stripped[2:].strip()))
            continue
        current_list_key = None
        if line.startswith(" "):
            continue
        if ":" not in line:
            raise ValueError(f"{path}:{line_number}: expected key: value")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            data[key] = scalar(value)
        else:
            data[key] = []
            current_list_key = key
    return data


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def import_available(module_name: str) -> tuple[bool, str]:
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            importlib.import_module(module_name)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, "import ok"


def torch_gpu_summary() -> tuple[bool, str | None, float | None, str]:
    ok, detail = import_available("torch")
    if not ok:
        return False, None, None, f"torch unavailable: {detail}"
    import torch  # type: ignore[import-not-found]

    if not torch.cuda.is_available():
        return False, None, None, "CUDA unavailable"
    name = torch.cuda.get_device_name(0)
    props = torch.cuda.get_device_properties(0)
    vram_gib = props.total_memory / (1024**3)
    return True, name, vram_gib, f"{name}; {vram_gib:.1f} GiB VRAM"


def model_manifest_path(repo_id: str, role: str) -> Path:
    return MODEL_MANIFEST_DIR / f"{role}_{sanitized_repo_id(repo_id)}.manifest.json"


def selected_model(config: dict[str, Any], use_fallback: bool) -> tuple[str, str, str]:
    if use_fallback:
        return (
            str(config["fallback_model_id"]),
            str(config["fallback_model_source_url"]),
            "fallback",
        )
    return str(config["model_id"]), str(config["model_source_url"]), "primary"


def verify_model_sources(config: dict[str, Any]) -> Gate:
    if not MODEL_SOURCES.exists():
        return Gate("model_sources.yaml", False, f"{rel(MODEL_SOURCES)} is missing")
    try:
        sources = read_simple_yaml(MODEL_SOURCES)
    except ValueError as exc:
        return Gate("model_sources.yaml", False, str(exc))
    expected = {
        "primary_model_id": config["model_id"],
        "primary_model_url": config["model_source_url"],
        "fallback_model_id": config["fallback_model_id"],
        "fallback_model_url": config["fallback_model_source_url"],
    }
    mismatches = [
        f"{key} expected {value!r}, found {sources.get(key)!r}"
        for key, value in expected.items()
        if sources.get(key) != value
    ]
    if mismatches:
        return Gate("model_sources.yaml", False, "; ".join(mismatches))
    return Gate("model_sources.yaml", True, rel(MODEL_SOURCES))


def verify_local_model(config: dict[str, Any], use_fallback: bool) -> tuple[Gate, Path | None, Path]:
    repo_id, _, role = selected_model(config, use_fallback)
    manifest = model_manifest_path(repo_id, role)
    manifest_data = read_json(manifest)
    if manifest_data is None:
        return Gate("local model manifest", False, f"{rel(manifest)} is missing or invalid"), None, manifest
    if manifest_data.get("retrieval_status") not in {"verified", "downloaded", "retrieved"}:
        return (
            Gate(
                "local model manifest",
                False,
                f"{rel(manifest)} retrieval_status={manifest_data.get('retrieval_status')!r}",
            ),
            None,
            manifest,
        )
    local_path_value = manifest_data.get("local_path")
    if not isinstance(local_path_value, str) or not local_path_value:
        local_path = resolve_path(config["model_cache_dir"]) / sanitized_repo_id(repo_id)
    else:
        local_path = resolve_path(local_path_value)
    if not local_path.exists():
        return Gate("local model path", False, f"{rel(local_path)} is missing"), local_path, manifest
    required_files = ["config.json", "tokenizer_config.json"]
    missing = [filename for filename in required_files if not (local_path / filename).exists()]
    if missing:
        return Gate("local model path", False, f"{rel(local_path)} missing {', '.join(missing)}"), local_path, manifest
    return Gate("local model path", True, f"{rel(local_path)} via {rel(manifest)}"), local_path, manifest


def record_eligibility(record: dict[str, Any]) -> str:
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("training_eligibility")
        if isinstance(value, str) and value:
            return value
        if metadata.get("human_review_required") is True:
            return "draft_needs_human_review"
    return "missing_training_eligibility"


def normalize_eligibility(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def is_blocked_for_train(value: str) -> bool:
    normalized = normalize_eligibility(value)
    if normalized.startswith("blocked-"):
        return True
    return value in BLOCKED_TRAIN_ELIGIBILITIES or normalized in BLOCKED_TRAIN_ELIGIBILITIES


def record_train_blockers(record: dict[str, Any], eligibility: str) -> list[str]:
    blockers: list[str] = []
    if is_blocked_for_train(eligibility):
        blockers.append(eligibility)
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        return blockers
    if metadata.get("human_review_required") is True:
        blockers.append("draft_needs_human_review")
    if metadata.get("source_type") == "review_candidate":
        blockers.append("review_candidate")
    license_status = metadata.get("external_source_license_provenance_reviewed")
    if license_status in {False, "false", "no", "unreviewed", "external-license-unreviewed"}:
        blockers.append("external_license_unreviewed")
    for key in ("unresolved_source_marker_count", "unresolved_source_record_count"):
        value = metadata.get(key)
        if isinstance(value, int) and value > 0:
            blockers.append("unresolved_source")
    source_alignment = metadata.get("source_alignment_status")
    if isinstance(source_alignment, str) and "unresolved" in source_alignment.lower():
        blockers.append("unresolved_source")
    return blockers


def validate_messages(record: dict[str, Any], line_number: int, errors: list[str]) -> None:
    messages = record.get("messages")
    if not isinstance(messages, list) or len(messages) < 3:
        errors.append(f"line {line_number}: messages must contain at least system, user, assistant")
        return
    roles = [message.get("role") for message in messages if isinstance(message, dict)]
    if roles[:3] != ["system", "user", "assistant"]:
        errors.append(f"line {line_number}: first three message roles must be system, user, assistant")
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            errors.append(f"line {line_number}: messages[{index}] is not an object")
            continue
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            errors.append(f"line {line_number}: messages[{index}].content must be non-empty text")


def validate_raw_sft(record: dict[str, Any], line_number: int, errors: list[str]) -> None:
    required = ["task", "storyform_context", "bible_summary", "scene_text", "user_request", "gold_output"]
    for key in required:
        if key not in record:
            errors.append(f"line {line_number}: raw SFT record missing {key}")


def summarize_jsonl(path: Path) -> JsonlSummary:
    errors: list[str] = []
    task_counts: Counter[str] = Counter()
    eligibility_counts: Counter[str] = Counter()
    blocked_eligibilities: Counter[str] = Counter()
    format_name = "unknown"
    records = 0

    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        return JsonlSummary(path, 0, format_name, task_counts, eligibility_counts, blocked_eligibilities, [str(exc)])

    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            records += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_number}: JSONL record must be an object")
                continue
            current_format = "messages" if "messages" in record else "raw_sft"
            if format_name == "unknown":
                format_name = current_format
            elif format_name != current_format:
                errors.append(f"line {line_number}: mixed JSONL formats are not supported")
            if current_format == "messages":
                validate_messages(record, line_number, errors)
            else:
                validate_raw_sft(record, line_number, errors)
            task = record.get("task")
            task_counts[str(task) if isinstance(task, str) and task else "missing_task"] += 1
            eligibility = record_eligibility(record)
            eligibility_counts[eligibility] += 1
            for blocker in record_train_blockers(record, eligibility):
                blocked_eligibilities[blocker] += 1
    return JsonlSummary(path, records, format_name, task_counts, eligibility_counts, blocked_eligibilities, errors)


def dataset_manifest_gate(minimum: int) -> tuple[Gate, int, dict[str, int]]:
    manifest = read_json(DATASET_MANIFEST)
    if manifest is None:
        return Gate("dataset manifest", False, f"{rel(DATASET_MANIFEST)} is missing or invalid"), 0, {}
    readiness = manifest.get("current_readiness")
    if not isinstance(readiness, dict):
        return Gate("dataset gate", False, "current_readiness is missing"), 0, {}
    count = int(readiness.get("eligible_for_training_records_counted_toward_500_gate") or 0)
    eligibility_counts = readiness.get("active_seed_training_eligibility_counts")
    status = str(readiness.get("status", "unknown"))
    detail = f"{count}/{minimum} eligible_for_training; current_readiness.status={status}"
    checks = readiness.get("checks")
    if isinstance(checks, list):
        failed = [
            str(check.get("name"))
            for check in checks
            if isinstance(check, dict) and check.get("passed") is False and check.get("name")
        ]
        if failed:
            detail += f"; failed_checks={failed}"
    return Gate("dataset gate", count >= minimum and status == "ready", detail), count, (
        eligibility_counts if isinstance(eligibility_counts, dict) else {}
    )


def run_env_check() -> tuple[bool, str]:
    command = [sys.executable, str(TRAINING_DIR / "scripts" / "check_training_env.py")]
    try:
        result = subprocess.run(command, check=False, text=True, capture_output=True, cwd=REPO_ROOT)
    except OSError as exc:
        return False, f"Could not run check_training_env.py: {exc}"
    output = (result.stdout + result.stderr).strip()
    env_ready = "Environment ready: yes" in output
    return env_ready, output


def write_report(path: Path, lines: list[str]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_blocked_reports(
    *,
    dataset_gate: Gate,
    model_gate: Gate,
    env_gate: Gate,
    vram_gate: Gate,
    selected_repo_id: str,
    selected_role: str,
    gpu_detail: str,
    eligible_count: int,
    minimum: int,
    smoke: bool,
) -> list[Path]:
    written: list[Path] = []
    generated_paths = {
        "dataset": REPORTS_DIR / "BLOCKED_training_dataset_gate.md",
        "vram": REPORTS_DIR / "BLOCKED_training_vram_primary_model.md",
        "model": REPORTS_DIR / "BLOCKED_training_model_not_retrieved.md",
        "env": REPORTS_DIR / "BLOCKED_training_env_not_ready.md",
    }
    if not dataset_gate.passed:
        path = generated_paths["dataset"]
        write_report(
            path,
            [
                "# BLOCKED: Training Dataset Gate",
                "",
                f"- Required eligible records: {minimum}",
                f"- Current eligible records: {eligible_count}",
                f"- Gate detail: {dataset_gate.detail}",
                f"- smoke_only_not_final_model: {'true' if smoke else 'false'}",
                "",
                "Full training must not run until the manifest reports at least 500 "
                "`eligible_for_training` records and readiness is `ready`.",
            ],
        )
        written.append(path)
    else:
        generated_paths["dataset"].unlink(missing_ok=True)
    if not vram_gate.passed:
        path = generated_paths["vram"]
        write_report(
            path,
            [
                "# BLOCKED: Training VRAM Primary Model",
                "",
                f"- Selected model: `{selected_repo_id}`",
                f"- Selected role: `{selected_role}`",
                f"- GPU: {gpu_detail}",
                f"- Gate detail: {vram_gate.detail}",
                "",
                "The current 4GB-class local GPU is likely too small for primary 7B "
                "QLoRA training. Use the fallback model only after retrieving it locally, "
                "or run training on a larger GPU/cloud host.",
            ],
        )
        written.append(path)
    else:
        generated_paths["vram"].unlink(missing_ok=True)
    if not model_gate.passed:
        path = generated_paths["model"]
        write_report(
            path,
            [
                "# BLOCKED: Training Model Not Retrieved",
                "",
                f"- Selected model: `{selected_repo_id}`",
                f"- Selected role: `{selected_role}`",
                f"- Gate detail: {model_gate.detail}",
                "",
                "Training is configured to use local model artifacts. Retrieve or verify "
                "the selected model before running without `--allow-download`.",
            ],
        )
        written.append(path)
    else:
        generated_paths["model"].unlink(missing_ok=True)
    if not env_gate.passed:
        path = generated_paths["env"]
        write_report(
            path,
            [
                "# BLOCKED: Training Environment Not Ready",
                "",
                f"- Gate detail: {env_gate.detail}",
                "",
                "CUDA, Unsloth, `datasets`, and `trl` must be available before any "
                "training run can load a model.",
            ],
        )
        written.append(path)
    else:
        generated_paths["env"].unlink(missing_ok=True)
    return written


def write_readiness_report(
    *,
    args: argparse.Namespace,
    config: dict[str, Any],
    selected_repo_id: str,
    selected_role: str,
    gates: list[Gate],
    train_summary: JsonlSummary | None,
    eval_summary: JsonlSummary | None,
    gpu_detail: str,
    env_output: str,
    blocked_reports: list[Path],
    smoke: bool,
) -> None:
    lines = [
        "# Training Script Readiness Report",
        "",
        "- training_script: `training/scripts/train_unsloth_qwen25_7b.py`",
        f"- config: `{rel(resolve_path(args.config))}`",
        f"- selected_model: `{selected_repo_id}`",
        f"- selected_role: `{selected_role}`",
        f"- output_dir: `{rel(resolve_path(args.output_dir or config.get('output_dir')))}`",
        f"- dry_run: {str(args.dry_run).lower()}",
        f"- smoke_only_not_final_model: {'true' if smoke else 'false'}",
        f"- gpu: {gpu_detail}",
        "",
        "## Gates",
        "",
        "| Gate | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for gate in gates:
        status = "PASS" if gate.passed else "BLOCKED"
        lines.append(f"| {gate.name} | {status} | {gate.detail.replace('|', '/')} |")
    lines.extend(["", "## Dataset Files", ""])
    for label, summary in (("train", train_summary), ("eval", eval_summary)):
        if summary is None:
            lines.append(f"- {label}: not supplied")
            continue
        lines.append(
            f"- {label}: `{rel(summary.path)}`; records={summary.record_count}; "
            f"format={summary.format_name}; eligibility={dict(summary.eligibility_counts)}"
        )
        if summary.errors:
            lines.append(f"- {label}_validation_errors: {summary.errors}")
    lines.extend(["", "## Blocked Reports", ""])
    if blocked_reports:
        for path in blocked_reports:
            lines.append(f"- `{rel(path)}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Environment Check", "", "```text", env_output[-4000:], "```"])
    write_report(REPORTS_DIR / "training_script_readiness_report.md", lines)


def validate_config(path: Path) -> tuple[dict[str, Any], Gate]:
    try:
        config = read_simple_yaml(path)
    except ValueError as exc:
        return {}, Gate("config", False, str(exc))
    missing = sorted(REQUIRED_CONFIG_KEYS - set(config))
    if missing:
        return config, Gate("config", False, f"missing keys: {', '.join(missing)}")
    if config.get("analysis_only") is not True:
        return config, Gate("config", False, "analysis_only must be true")
    expected_modules = {"q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}
    modules = set(config.get("target_modules") if isinstance(config.get("target_modules"), list) else [])
    if modules != expected_modules:
        return config, Gate("config", False, f"target_modules mismatch: {sorted(modules)}")
    return config, Gate("config", True, rel(path))


def make_env_gate() -> tuple[Gate, str]:
    env_ready, output = run_env_check()
    needed = ["unsloth import", "datasets import", "trl import"]
    missing = [label for label in needed if f"[PASS] {label}" not in output]
    if missing:
        return Gate("environment", False, f"missing readiness checks: {', '.join(missing)}"), output
    if not env_ready:
        return Gate("environment", False, "check_training_env.py did not report Environment ready: yes"), output
    return Gate("environment", True, "CUDA and required imports are ready"), output


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = resolve_path(args.config)
    config, config_gate = validate_config(config_path)
    if not config_gate.passed and not config:
        print(f"[BLOCKED] {config_gate.name}: {config_gate.detail}")
        return 2

    output_dir = resolve_path(args.output_dir or config.get("output_dir"))
    selected_repo_id, _, selected_role = selected_model(config, args.use_fallback_model)
    minimum = int(config.get("min_full_training_records", 500))
    smoke = bool(args.allow_smoke_below_gate and args.max_steps)

    model_sources_gate = verify_model_sources(config)
    model_gate, local_model_path, _ = verify_local_model(config, args.use_fallback_model)
    dataset_gate, eligible_count, manifest_eligibility_counts = dataset_manifest_gate(minimum)
    env_gate, env_output = make_env_gate()
    cuda_ready, gpu_name, vram_gib, gpu_detail = torch_gpu_summary()

    train_summary = summarize_jsonl(resolve_path(args.train_file)) if args.train_file else None
    eval_summary = summarize_jsonl(resolve_path(args.eval_file)) if args.eval_file else None
    file_gates: list[Gate] = []
    for label, summary in (("train file", train_summary), ("eval file", eval_summary)):
        if summary is None:
            continue
        ok = not summary.errors
        detail = f"{summary.record_count} records; format={summary.format_name}"
        if summary.eligibility_counts:
            detail += f"; training_eligibility={dict(summary.eligibility_counts)}"
        if summary.errors:
            detail += f"; errors={summary.errors[:3]}"
        file_gates.append(Gate(label, ok, detail))

    if train_summary and train_summary.blocked_eligibilities:
        file_gates.append(
            Gate(
                "train split eligibility",
                False,
                f"blocked train records found: {dict(train_summary.blocked_eligibilities)}",
            )
        )
    elif train_summary:
        file_gates.append(Gate("train split eligibility", True, "no blocked/eval-only/draft train records found"))

    if not args.dry_run and train_summary is None:
        file_gates.append(Gate("train file required", False, "--train-file is required for training mode"))

    if args.require_full_gate and not dataset_gate.passed:
        full_gate = Gate("required full dataset gate", False, dataset_gate.detail)
    elif not dataset_gate.passed and not smoke:
        full_gate = Gate("smoke gate", False, "--allow-smoke-below-gate and --max-steps are required below 500 records")
    elif not dataset_gate.passed:
        full_gate = Gate("smoke gate", True, "smoke run allowed below full gate; smoke_only_not_final_model: true")
    else:
        full_gate = Gate("full dataset gate", True, dataset_gate.detail)

    if not cuda_ready:
        cuda_gate = Gate("CUDA", False, gpu_detail)
    else:
        cuda_gate = Gate("CUDA", True, gpu_detail)

    if (
        selected_role == "primary"
        and vram_gib is not None
        and vram_gib < 12
        and not args.cloud_or_larger_gpu_confirmed
    ):
        vram_gate = Gate(
            "primary model VRAM",
            False,
            f"{gpu_detail}; primary 7B QLoRA should use a larger GPU or explicit fallback/cloud path",
        )
    else:
        vram_gate = Gate("selected GPU VRAM", True, gpu_detail)

    download_gate = Gate(
        "local model download policy",
        model_gate.passed or bool(args.allow_download),
        "local model present or download explicitly allowed"
        if model_gate.passed or args.allow_download
        else "selected model is not locally retrieved and --allow-download is false",
    )

    gates = [
        config_gate,
        model_sources_gate,
        model_gate,
        download_gate,
        dataset_gate,
        full_gate,
        env_gate,
        cuda_gate,
        vram_gate,
        *file_gates,
    ]

    blocked_reports = write_blocked_reports(
        dataset_gate=dataset_gate if not dataset_gate.passed or not full_gate.passed else Gate("dataset gate", True, dataset_gate.detail),
        model_gate=download_gate,
        env_gate=env_gate if not env_gate.passed or not cuda_gate.passed else Gate("environment", True, env_gate.detail),
        vram_gate=vram_gate,
        selected_repo_id=selected_repo_id,
        selected_role=selected_role,
        gpu_detail=gpu_detail,
        eligible_count=eligible_count,
        minimum=minimum,
        smoke=smoke,
    )
    write_readiness_report(
        args=args,
        config=config,
        selected_repo_id=selected_repo_id,
        selected_role=selected_role,
        gates=gates,
        train_summary=train_summary,
        eval_summary=eval_summary,
        gpu_detail=gpu_detail,
        env_output=env_output,
        blocked_reports=blocked_reports,
        smoke=smoke,
    )

    print("Unsloth QLoRA training readiness")
    print(f"Selected model: {selected_repo_id} ({selected_role})")
    print(f"Output directory: {rel(output_dir)}")
    print(f"GPU: {gpu_detail}")
    print(f"Dataset manifest eligibility: {eligible_count}/{minimum}; counts={manifest_eligibility_counts}")
    for gate in gates:
        status = "PASS" if gate.passed else "BLOCKED"
        print(f"[{status}] {gate.name}: {gate.detail}")
    if args.dry_run:
        print("Dry run complete: model was not loaded and training was not run.")
        return 0

    hard_blocked = [gate for gate in gates if not gate.passed]
    if args.allow_download:
        hard_blocked = [
            gate
            for gate in hard_blocked
            if gate.name not in {"local model manifest", "local model path"}
        ]
    if hard_blocked:
        print("Training refused before model loading because one or more gates are blocked.")
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)
    print("Gates passed; starting bounded Unsloth training.")
    train_with_unsloth(
        config=config,
        model_path=local_model_path if local_model_path is not None else selected_repo_id,
        train_file=resolve_path(args.train_file),
        eval_file=resolve_path(args.eval_file) if args.eval_file else None,
        output_dir=output_dir,
        max_steps=args.max_steps,
        smoke=smoke,
        allow_download=bool(args.allow_download),
    )
    return 0


def train_with_unsloth(
    *,
    config: dict[str, Any],
    model_path: Path | str,
    train_file: Path,
    eval_file: Path | None,
    output_dir: Path,
    max_steps: int | None,
    smoke: bool,
    allow_download: bool,
) -> None:
    from datasets import load_dataset  # type: ignore[import-not-found]
    from transformers import EarlyStoppingCallback  # type: ignore[import-not-found]
    from trl import SFTConfig, SFTTrainer  # type: ignore[import-not-found]
    from unsloth import FastLanguageModel  # type: ignore[import-not-found]

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(model_path),
        max_seq_length=int(config["max_seq_length"]),
        dtype=None,
        load_in_4bit=True,
        local_files_only=bool(config.get("require_local_model", True)) and not allow_download,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=int(config["lora_r"]),
        target_modules=list(config["target_modules"]),
        lora_alpha=int(config["lora_alpha"]),
        lora_dropout=float(config["lora_dropout"]),
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=int(config["seed"]),
    )

    data_files: dict[str, str] = {"train": str(train_file)}
    if eval_file is not None:
        data_files["validation"] = str(eval_file)
    dataset = load_dataset("json", data_files=data_files)

    def formatting_prompts_func(example: dict[str, Any]) -> str:
        messages = example.get("messages")
        if isinstance(messages, list):
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        text = example.get("text")
        return text if isinstance(text, str) else json.dumps(example, ensure_ascii=False)

    callbacks = [EarlyStoppingCallback(early_stopping_patience=3)] if eval_file is not None else []
    args = SFTConfig(
        output_dir=str(output_dir),
        per_device_train_batch_size=int(config["per_device_train_batch_size"]),
        gradient_accumulation_steps=int(config["gradient_accumulation_steps"]),
        learning_rate=float(config["learning_rate"]),
        num_train_epochs=float(config["num_train_epochs"]),
        max_steps=max_steps if max_steps is not None else -1,
        eval_strategy="steps" if eval_file is not None else "no",
        eval_steps=int(config["eval_steps"]),
        save_steps=int(config["save_steps"]),
        logging_steps=10,
        seed=int(config["seed"]),
        fp16=True,
        report_to="none",
        max_length=int(config["max_seq_length"]),
    )
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset.get("validation"),
        formatting_func=formatting_prompts_func,
        args=args,
        callbacks=callbacks,
    )
    trainer.train()
    trainer.save_model(str(output_dir))
    if smoke:
        (output_dir / "SMOKE_ONLY_NOT_FINAL_MODEL.json").write_text(
            json.dumps({"smoke_only_not_final_model": True}, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    raise SystemExit(main())
