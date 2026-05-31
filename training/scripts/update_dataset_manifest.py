from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
SCHEMA_DIR = TRAINING_DIR / "schemas"
DEFAULT_OUTPUT = TRAINING_DIR / "data" / "dataset_manifest.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_dataset


ELIGIBLE_FOR_TRAINING = "eligible_for_training"
ELIGIBLE_FOR_EVAL_ONLY = "eligible_for_eval_only"
DRAFT_NEEDS_HUMAN_REVIEW = "draft_needs_human_review"
BLOCKED_PENDING_OWNER_DECISION = "blocked_pending_owner_decision"
MISSING_TRAINING_ELIGIBILITY = "missing_training_eligibility"
MISSING_SOURCE_ALIGNMENT_STATUS = "missing_source_alignment_status"

TASK_MIX_TARGETS = {
    "story_check": {"min_percent": 40, "max_percent": 45},
    "throughline_classification": {"min_percent": 25, "max_percent": 30},
    "writer_questions": {"min_percent": 20, "max_percent": 25},
    "out_of_scope_refusal": {"min_percent": 5, "max_percent": 10},
}

TRAINING_READY_MINIMUM = 500
TRAINING_READY_TARGET_MAXIMUM = 1000
REVIEW_CANDIDATE_TOKENS = ("review_candidates", "eval_review_candidates")
ALLOWED_SOURCE_TYPES = {
    "internal_project",
    "external_dataset",
    "synthetic_refusal",
    "review_candidate",
}
UNRESOLVED_SOURCE_MARKERS = (
    "OWNER_DECISION_REQUIRED",
    "INSUFFICIENT_SOURCE_EVIDENCE",
    "Candidate only",
)
EMBER_CROWN_MARKERS = (
    "Ember Crown",
    "ember_crown",
    "Quest for the Ember Crown",
    "projects/example/storyform.json",
)


@dataclass(frozen=True)
class ValidationSummary:
    status: str
    error_count: int
    warning_count: int
    notes: list[str]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the dataset manifest for training and eval JSONL files."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Manifest JSON output path. Defaults to training/data/dataset_manifest.json.",
    )
    parser.add_argument(
        "--schemas",
        type=Path,
        default=SCHEMA_DIR,
        help="Path to training schemas. Defaults to training/schemas.",
    )
    return parser.parse_args(argv)


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, f"could_not_read: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"invalid_json: {exc.msg} at line {exc.lineno} column {exc.colno}"


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []

    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        return records, [f"could_not_read: {exc}"]

    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"line {line_number}: invalid_json: {exc.msg} at column {exc.colno}"
                )
                continue
            if not isinstance(value, dict):
                errors.append(f"line {line_number}: JSONL record must be an object")
                continue
            records.append(value)

    return records, errors


def metadata_for(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def sorted_nonempty(values: set[str]) -> list[str]:
    return sorted(value for value in values if value)


def is_messages_file(path: Path, records: list[dict[str, Any]]) -> bool:
    return path.name.endswith(".messages.jsonl") or any("messages" in record for record in records)


def is_review_candidate_file(path: Path) -> bool:
    normalized = path.as_posix()
    return any(token in normalized for token in REVIEW_CANDIDATE_TOKENS)


def record_source_type(path: Path, record: dict[str, Any]) -> str:
    metadata = metadata_for(record)
    metadata_source_type = metadata.get("source_type")
    if metadata_source_type in ALLOWED_SOURCE_TYPES:
        return str(metadata_source_type)
    if "external" in path.parts:
        return "external_dataset"
    if is_review_candidate_file(path):
        return "review_candidate"
    if record.get("task") == "out_of_scope_refusal":
        return "synthetic_refusal"
    return "internal_project"


def file_source_type(source_type_counts: Counter[str]) -> str:
    if not source_type_counts:
        return "internal_project"
    if len(source_type_counts) == 1:
        return next(iter(source_type_counts))
    if source_type_counts.get("review_candidate"):
        return "review_candidate"
    return "internal_project"


def infer_included_splits(path: Path) -> dict[str, bool]:
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    is_review_candidate = is_review_candidate_file(path)
    return {
        "train": name.endswith(".messages.jsonl") or name.endswith(".promoted.jsonl") or "train" in name,
        "eval": "eval" in parts and not is_review_candidate,
        "test": "test" in name or "test" in parts,
    }


def source_marker_count(records: list[dict[str, Any]], markers: tuple[str, ...]) -> int:
    count = 0
    for record in records:
        text = json.dumps(record, ensure_ascii=False)
        count += sum(text.count(marker) for marker in markers)
    return count


def record_has_unresolved_source(record: dict[str, Any]) -> bool:
    metadata = metadata_for(record)
    fields = [
        metadata.get("source_alignment_status"),
        metadata.get("source_alignment_notes"),
        metadata.get("human_review_notes"),
        record.get("storyform_context"),
    ]
    text = json.dumps(fields, ensure_ascii=False)
    return any(marker in text for marker in UNRESOLVED_SOURCE_MARKERS)


def record_uses_ember_crown(record: dict[str, Any]) -> bool:
    metadata = metadata_for(record)
    source_paths = [
        metadata.get("source_scene_path"),
        metadata.get("source_bible_path"),
        metadata.get("source_storyform_path"),
    ]
    source_context = {
        "storyform_context": record.get("storyform_context"),
        "bible_summary": record.get("bible_summary"),
    }
    text = json.dumps(
        {"source_paths": source_paths, "source_context": source_context},
        ensure_ascii=False,
    )
    return any(marker in text for marker in EMBER_CROWN_MARKERS)


def validate_sft_records(
    path: Path,
    validators: validate_dataset.Validators | None,
    read_errors: list[str],
) -> ValidationSummary:
    if read_errors:
        return ValidationSummary(
            status="failed",
            error_count=len(read_errors),
            warning_count=0,
            notes=read_errors,
        )
    if validators is None:
        return ValidationSummary(
            status="not_run",
            error_count=0,
            warning_count=0,
            notes=["schema validators were not available"],
        )

    record_count, findings = validate_dataset.validate_jsonl(path, validators, strict=True)
    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    notes = [
        f"validated {record_count} record(s) against SFT/task schemas with strict safety checks"
    ]
    if error_count or warning_count:
        notes.extend(
            f"line {finding.line}: {finding.severity}: {finding.message}"
            if finding.line is not None
            else f"{finding.severity}: {finding.message}"
            for finding in findings[:20]
        )
    return ValidationSummary(
        status="passed" if error_count == 0 else "failed",
        error_count=error_count,
        warning_count=warning_count,
        notes=notes,
    )


def validate_messages_records(
    records: list[dict[str, Any]],
    read_errors: list[str],
) -> ValidationSummary:
    errors = list(read_errors)
    for index, record in enumerate(records, start=1):
        messages = record.get("messages")
        if not isinstance(messages, list) or len(messages) != 3:
            errors.append(f"line {index}: messages must contain exactly 3 chat turns")
            continue
        roles = [message.get("role") for message in messages if isinstance(message, dict)]
        if roles != ["system", "user", "assistant"]:
            errors.append(f"line {index}: messages roles must be system, user, assistant")
        if not isinstance(record.get("task"), str):
            errors.append(f"line {index}: task is missing or not a string")
        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            errors.append(f"line {index}: metadata is missing or not an object")
    return ValidationSummary(
        status="passed" if not errors else "failed",
        error_count=len(errors),
        warning_count=0,
        notes=["validated chat messages JSONL shape"] + errors[:20],
    )


def summarize_jsonl_file(
    path: Path,
    validators: validate_dataset.Validators | None,
) -> dict[str, Any]:
    records, read_errors = read_jsonl(path)
    messages_file = is_messages_file(path, records)
    validation = (
        validate_messages_records(records, read_errors)
        if messages_file
        else validate_sft_records(path, validators, read_errors)
    )

    task_counts: Counter[str] = Counter()
    eligibility_counts: Counter[str] = Counter()
    human_review_counts: Counter[str] = Counter()
    alignment_counts: Counter[str] = Counter()
    source_type_counts: Counter[str] = Counter()
    source_scene_paths: set[str] = set()
    source_bible_paths: set[str] = set()
    source_storyform_paths: set[str] = set()
    unresolved_source_records = 0
    ember_crown_records = 0
    external_license_review_counts: Counter[str] = Counter()

    for record in records:
        metadata = metadata_for(record)
        task_counts[str(record.get("task", "missing_task"))] += 1
        eligibility_counts[
            str(metadata.get("training_eligibility") or MISSING_TRAINING_ELIGIBILITY)
        ] += 1
        if metadata.get("human_review_required") is True:
            human_review_counts["required"] += 1
        elif metadata.get("human_review_required") is False:
            human_review_counts["not_required"] += 1
        else:
            human_review_counts["missing"] += 1
        alignment_counts[
            str(metadata.get("source_alignment_status") or MISSING_SOURCE_ALIGNMENT_STATUS)
        ] += 1
        source_type_counts[record_source_type(path, record)] += 1

        source_scene_paths.add(str(metadata.get("source_scene_path") or ""))
        source_bible_paths.add(str(metadata.get("source_bible_path") or ""))
        source_storyform_paths.add(str(metadata.get("source_storyform_path") or ""))

        if record_has_unresolved_source(record):
            unresolved_source_records += 1
        if record_uses_ember_crown(record):
            ember_crown_records += 1

        external_status = metadata.get("external_license_provenance_reviewed")
        if external_status is True:
            external_license_review_counts["reviewed"] += 1
        elif external_status is False:
            external_license_review_counts["not_reviewed"] += 1
        elif record_source_type(path, record) == "external_dataset":
            external_license_review_counts["missing"] += 1

    source_type = file_source_type(source_type_counts)
    included_splits = infer_included_splits(path)
    human_review_status = (
        "complete"
        if records and human_review_counts.get("required", 0) == 0 and human_review_counts.get("missing", 0) == 0
        else "required"
        if human_review_counts.get("required", 0)
        else "missing"
        if human_review_counts.get("missing", 0)
        else "not_applicable_empty_file"
    )
    external_review_status = (
        "not_applicable"
        if source_type != "external_dataset"
        else "reviewed"
        if external_license_review_counts.get("reviewed") == len(records)
        else "not_reviewed_or_incomplete"
    )

    return {
        "path": relative_path(path),
        "dataset_kind": "messages_jsonl" if messages_file else "sft_or_eval_jsonl",
        "record_count": len(records),
        "source_type": source_type,
        "source_type_counts": counter_to_dict(source_type_counts),
        "source_scene": sorted_nonempty(source_scene_paths),
        "source_bible": sorted_nonempty(source_bible_paths),
        "source_storyform": sorted_nonempty(source_storyform_paths),
        "source_alignment_status": counter_to_dict(alignment_counts),
        "task_counts": counter_to_dict(task_counts),
        "validation_status": asdict(validation),
        "human_review_status": {
            "status": human_review_status,
            "counts": counter_to_dict(human_review_counts),
        },
        "training_eligibility_counts": counter_to_dict(eligibility_counts),
        "included_in_train_eval_test": included_splits,
        "included_in_review_candidates": is_review_candidate_file(path),
        "ember_crown_source_used": ember_crown_records > 0,
        "ember_crown_source_use_reason": (
            "Dataset content references Ember Crown or projects/example/storyform.json."
            if ember_crown_records
            else "No Ember Crown source detected in this dataset file."
        ),
        "active_example_project_still_mismatched": active_example_project_mismatch(),
        "external_source_license_provenance_reviewed": external_review_status,
        "unresolved_source_marker_count": source_marker_count(records, UNRESOLVED_SOURCE_MARKERS),
        "unresolved_source_record_count": unresolved_source_records,
    }


def load_validators(schema_dir: Path) -> validate_dataset.Validators | None:
    try:
        return validate_dataset.load_validators(schema_dir)
    except ValueError as exc:
        print(f"update_dataset_manifest.py: warning: could not load validators: {exc}", file=sys.stderr)
        return None


def collect_dataset_paths() -> list[Path]:
    paths: set[Path] = set()
    for pattern in (
        "training/data/sft/*.jsonl",
        "training/data/eval/*.jsonl",
        "training/data/sft/*.messages.jsonl",
    ):
        paths.update(REPO_ROOT.glob(pattern))
    return sorted(paths, key=lambda item: relative_path(item))


def active_seed_path() -> Path | None:
    v2 = TRAINING_DIR / "data" / "sft" / "elena_seed_020.v2.jsonl"
    original = TRAINING_DIR / "data" / "sft" / "elena_seed_020.jsonl"
    if v2.exists():
        return v2
    if original.exists():
        return original
    return None


def training_gate_paths() -> list[Path]:
    paths: list[Path] = []
    seed_path = active_seed_path()
    if seed_path is not None:
        paths.append(seed_path)
    paths.extend(sorted((TRAINING_DIR / "data" / "sft").glob("*.promoted.jsonl")))
    return paths


def eligible_task_counts_for_training_gate() -> tuple[int, Counter[str], Counter[str], list[str]]:
    task_counts: Counter[str] = Counter()
    eligibility_counts: Counter[str] = Counter()
    counted_paths: list[str] = []
    for path in training_gate_paths():
        records, _errors = read_jsonl(path)
        counted_paths.append(relative_path(path))
        for record in records:
            metadata = metadata_for(record)
            eligibility = str(metadata.get("training_eligibility") or MISSING_TRAINING_ELIGIBILITY)
            eligibility_counts[eligibility] += 1
            if eligibility == ELIGIBLE_FOR_TRAINING:
                task_counts[str(record.get("task", "missing_task"))] += 1

    return eligibility_counts[ELIGIBLE_FOR_TRAINING], task_counts, eligibility_counts, counted_paths


def task_mix_percentages(task_counts: Counter[str]) -> dict[str, float]:
    total = sum(task_counts.values())
    if total == 0:
        return {task: 0.0 for task in TASK_MIX_TARGETS}
    return {
        task: round((task_counts.get(task, 0) / total) * 100, 2)
        for task in TASK_MIX_TARGETS
    }


def task_mix_within_target(task_mix: dict[str, float]) -> bool:
    for task, bounds in TASK_MIX_TARGETS.items():
        value = task_mix.get(task, 0.0)
        if value < bounds["min_percent"] or value > bounds["max_percent"]:
            return False
    return True


def train_records(dataset_files: list[dict[str, Any]]) -> list[tuple[dict[str, Any], str]]:
    records: list[tuple[dict[str, Any], str]] = []
    for dataset_file in dataset_files:
        if not dataset_file["included_in_train_eval_test"]["train"]:
            continue
        path = REPO_ROOT / dataset_file["path"]
        file_records, _errors = read_jsonl(path)
        records.extend((record, record_source_type(path, record)) for record in file_records)
    return records


def records_by_eligibility(records: list[tuple[dict[str, Any], str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record, _source_type in records:
        eligibility = metadata_for(record).get("training_eligibility") or MISSING_TRAINING_ELIGIBILITY
        counts[str(eligibility)] += 1
    return counts


def active_example_project_mismatch() -> bool:
    example_dir = REPO_ROOT / "projects" / "example"
    scene_text = read_text(example_dir / "scenes" / "scene_001.md")
    bible_text = read_text(example_dir / "bible.json")
    storyform_text = read_text(example_dir / "storyform.json")
    has_elena_scene_or_bible = "Elena" in scene_text or "Elena" in bible_text
    has_ember_storyform = any(marker in storyform_text for marker in EMBER_CROWN_MARKERS)
    return has_elena_scene_or_bible and has_ember_storyform


def active_example_project_status() -> dict[str, Any]:
    mismatch = active_example_project_mismatch()
    return {
        "path": "projects/example",
        "active_example_project_still_mismatched": mismatch,
        "status": "mismatched" if mismatch else "not_mismatched_or_not_detected",
        "details": (
            "projects/example scene or bible contains Elena material while storyform.json "
            "still contains Ember Crown fixture material."
            if mismatch
            else "No Elena/Ember Crown mismatch detected by the manifest scanner."
        ),
    }


def scan_external_metadata() -> list[dict[str, Any]]:
    metadata_dir = TRAINING_DIR / "data" / "external" / "metadata"
    entries: list[dict[str, Any]] = []
    if not metadata_dir.exists():
        return entries

    for path in sorted(metadata_dir.glob("*.json")):
        data, error = read_json(path)
        if error:
            entries.append(
                {
                    "path": relative_path(path),
                    "source_type": "external_dataset",
                    "validation_status": {
                        "status": "failed",
                        "error_count": 1,
                        "warning_count": 0,
                        "notes": [error],
                    },
                    "source_url": None,
                    "license_or_provenance_status": "not_reviewed_or_unavailable",
                    "external_source_license_provenance_reviewed": False,
                    "human_review_status": "missing",
                    "transformation_notes_present": False,
                }
            )
            continue

        if not isinstance(data, dict):
            data = {}
        source_url = data.get("source_url") or data.get("url")
        license_status = data.get("license_status") or data.get("license")
        provenance_status = data.get("provenance_status") or data.get("provenance")
        license_reviewed = bool(
            data.get("license_reviewed")
            or data.get("provenance_reviewed")
            or data.get("license_provenance_reviewed")
        )
        human_review_status = data.get("human_review_status") or data.get("human_review")
        transformation_notes = data.get("transformation_notes")
        entries.append(
            {
                "path": relative_path(path),
                "source_type": "external_dataset",
                "source_url": source_url,
                "license_or_provenance_status": {
                    "license": license_status,
                    "provenance": provenance_status,
                },
                "external_source_license_provenance_reviewed": license_reviewed,
                "human_review_status": human_review_status or "missing",
                "transformation_notes_present": bool(transformation_notes),
                "validation_status": {
                    "status": "passed",
                    "error_count": 0,
                    "warning_count": 0,
                    "notes": ["metadata JSON parsed"],
                },
            }
        )
    return entries


def scan_external_config() -> dict[str, Any]:
    path = TRAINING_DIR / "configs" / "external_dataset_sources.yaml"
    if not path.exists():
        return {
            "path": relative_path(path),
            "exists": False,
            "parse_status": "not_present",
            "external_source_license_provenance_reviewed": "not_applicable_no_config",
        }

    text = read_text(path)
    parsed: Any | None = None
    parse_status = "parsed"
    try:
        import yaml  # type: ignore[import-not-found]

        parsed = yaml.safe_load(text)
    except ImportError:
        parse_status = "present_but_yaml_parser_unavailable"
    except Exception as exc:  # pragma: no cover - defensive for malformed local YAML
        parse_status = f"parse_failed: {exc}"

    reviewed = "unknown"
    if isinstance(parsed, dict):
        reviewed = bool(
            parsed.get("license_provenance_reviewed")
            or parsed.get("provenance_reviewed")
            or parsed.get("license_reviewed")
        )
    return {
        "path": relative_path(path),
        "exists": True,
        "parse_status": parse_status,
        "external_source_license_provenance_reviewed": reviewed,
    }


def external_review_status(
    metadata_entries: list[dict[str, Any]],
    external_config: dict[str, Any],
) -> str:
    if not metadata_entries and not external_config.get("exists"):
        return "not_applicable_no_external_sources_registered"
    metadata_reviewed = all(
        entry.get("external_source_license_provenance_reviewed") is True
        for entry in metadata_entries
    )
    config_reviewed = external_config.get("external_source_license_provenance_reviewed")
    if metadata_entries and metadata_reviewed and config_reviewed in {True, "unknown"}:
        return "reviewed"
    return "not_reviewed_or_incomplete"


def ember_crown_status(dataset_files: list[dict[str, Any]]) -> dict[str, Any]:
    used_in_dataset = any(file["ember_crown_source_used"] for file in dataset_files)
    active_mismatch = active_example_project_mismatch()
    return {
        "used_in_dataset_records": used_in_dataset,
        "active_example_project_uses_ember_crown_fixture": active_mismatch,
        "used_as_elena_truth": used_in_dataset,
        "why": (
            "Ember Crown appears in one or more dataset records and must be audited."
            if used_in_dataset
            else "No dataset record uses Ember Crown as Elena truth. Ember Crown remains only as "
            "the active projects/example storyform fixture while the Elena scene and bible remain "
            "mismatched in that example project."
        ),
    }


def ready_gate(dataset_files: list[dict[str, Any]]) -> dict[str, Any]:
    eligible_count, eligible_task_counts, training_gate_eligibility_counts, counted_paths = (
        eligible_task_counts_for_training_gate()
    )
    task_mix = task_mix_percentages(eligible_task_counts)
    train_jsonl_records = train_records(dataset_files)
    train_eligibility_counts = records_by_eligibility(train_jsonl_records)
    validation_error_count = sum(
        file["validation_status"]["error_count"] for file in dataset_files
    )
    eval_holdout_count = sum(
        file["record_count"]
        for file in dataset_files
        if file["included_in_train_eval_test"]["eval"]
    )
    unresolved_train_records = sum(
        1 for record, _source_type in train_jsonl_records if record_has_unresolved_source(record)
    )
    ember_crown_train_records = sum(
        1 for record, _source_type in train_jsonl_records if record_uses_ember_crown(record)
    )
    external_train_records = [
        record
        for record, source_type in train_jsonl_records
        if source_type == "external_dataset"
    ]
    external_metadata_complete = all(
        bool(metadata_for(record).get("source_url"))
        and metadata_for(record).get("external_license_provenance_reviewed") is True
        and bool(metadata_for(record).get("transformation_notes"))
        and metadata_for(record).get("human_review_required") is False
        for record in external_train_records
    )

    checks = [
        {
            "name": "at_least_500_eligible_for_training_records",
            "passed": eligible_count >= TRAINING_READY_MINIMUM,
            "actual": eligible_count,
            "required_minimum": TRAINING_READY_MINIMUM,
        },
        {
            "name": "target_task_mix_within_range",
            "passed": task_mix_within_target(task_mix),
            "actual_percentages": task_mix,
            "required_percentages": TASK_MIX_TARGETS,
        },
        {
            "name": "refusal_examples_present",
            "passed": eligible_task_counts.get("out_of_scope_refusal", 0) > 0,
            "actual": eligible_task_counts.get("out_of_scope_refusal", 0),
        },
        {
            "name": "holdout_eval_set_present",
            "passed": eval_holdout_count > 0,
            "actual": eval_holdout_count,
        },
        {
            "name": "no_validation_errors",
            "passed": validation_error_count == 0,
            "actual_error_count": validation_error_count,
        },
        {
            "name": "no_blocked_records_in_train_split",
            "passed": train_eligibility_counts.get(BLOCKED_PENDING_OWNER_DECISION, 0) == 0
            and not any(key.startswith("blocked_") for key in train_eligibility_counts),
            "train_eligibility_counts": counter_to_dict(train_eligibility_counts),
        },
        {
            "name": "no_eval_only_records_in_train_split",
            "passed": train_eligibility_counts.get(ELIGIBLE_FOR_EVAL_ONLY, 0) == 0,
            "train_eligibility_counts": counter_to_dict(train_eligibility_counts),
        },
        {
            "name": "no_draft_needs_human_review_records_in_train_split",
            "passed": train_eligibility_counts.get(DRAFT_NEEDS_HUMAN_REVIEW, 0) == 0,
            "train_eligibility_counts": counter_to_dict(train_eligibility_counts),
        },
        {
            "name": "no_unresolved_source_records_in_train_split",
            "passed": unresolved_train_records == 0,
            "actual": unresolved_train_records,
        },
        {
            "name": "no_ember_crown_records_used_as_elena_truth",
            "passed": ember_crown_train_records == 0,
            "actual": ember_crown_train_records,
        },
        {
            "name": "external_dataset_records_metadata_complete",
            "passed": external_metadata_complete,
            "actual_external_train_records": len(external_train_records),
            "required_metadata": [
                "source_url",
                "license/provenance status",
                "transformation_notes",
                "human_review_status",
            ],
        },
    ]
    return {
        "status": "ready" if all(check["passed"] for check in checks) else "blocked",
        "active_seed_file": relative_path(active_seed_path()) if active_seed_path() else None,
        "training_gate_files": counted_paths,
        "active_seed_training_eligibility_counts": counter_to_dict(
            training_gate_eligibility_counts
        ),
        "eligible_for_training_records_counted_toward_500_gate": eligible_count,
        "eligible_task_counts_counted_toward_gate": counter_to_dict(eligible_task_counts),
        "eligible_task_mix_percentages": task_mix,
        "target_record_range": {
            "minimum": TRAINING_READY_MINIMUM,
            "maximum": TRAINING_READY_TARGET_MAXIMUM,
        },
        "checks": checks,
    }


def build_manifest(schema_dir: Path) -> dict[str, Any]:
    validators = load_validators(schema_dir)
    dataset_files = [
        summarize_jsonl_file(path, validators)
        for path in collect_dataset_paths()
    ]
    metadata_entries = scan_external_metadata()
    external_config = scan_external_config()
    gate = ready_gate(dataset_files)

    return {
        "manifest_version": 1,
        "generated_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "generator": "training/scripts/update_dataset_manifest.py",
        "dataset_policy": {
            "target_examples": {
                "minimum": TRAINING_READY_MINIMUM,
                "maximum": TRAINING_READY_TARGET_MAXIMUM,
            },
            "task_mix_targets_percent": TASK_MIX_TARGETS,
            "analysis_only": True,
            "new_scene_prose_generation_allowed": False,
            "external_dataset_policy": (
                "External datasets may be used only as source material or annotation "
                "scaffolding until converted into the local schema and reviewed."
            ),
        },
        "current_readiness": gate,
        "dataset_files": dataset_files,
        "external_sources": {
            "metadata_files": metadata_entries,
            "config_file": external_config,
            "external_source_license_provenance_reviewed": external_review_status(
                metadata_entries,
                external_config,
            ),
        },
        "ember_crown_source_use": ember_crown_status(dataset_files),
        "active_example_project": active_example_project_status(),
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = build_manifest(args.schemas)
    write_manifest(args.output, manifest)
    print(f"Wrote {relative_path(args.output)}")
    print(
        "Current full fine-tune readiness: "
        f"{manifest['current_readiness']['status']} "
        f"({manifest['current_readiness']['eligible_for_training_records_counted_toward_500_gate']} "
        "eligible_for_training record(s) counted toward the 500-record gate)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
