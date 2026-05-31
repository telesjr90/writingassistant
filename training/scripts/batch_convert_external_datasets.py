from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from validate_dataset import load_validators, validate_record


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
DEFAULT_OUTPUT_DIR = TRAINING_DIR / "data" / "sft"
REPORTS_DIR = TRAINING_DIR / "reports"
SCHEMA_DIR = TRAINING_DIR / "schemas"
SUPPORTED_DATASET_ID = "moral_stories"
SOURCE_FIELDS = [
    "ID",
    "norm",
    "situation",
    "intention",
    "moral_action",
    "moral_consequence",
    "immoral_action",
    "immoral_consequence",
]
REFUSAL_MESSAGE = (
    "I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose."
)
PROHIBITED_WRITER_QUESTION_THROUGHLINES = {
    "overall_story",
    "main_character",
    "influence_character",
    "relationship_story",
}
PROSE_OUTPUT_PATTERNS = [
    re.compile(r"\bhere(?:'s| is)\s+(?:a\s+)?(?:revised|rewritten|new|draft)", re.IGNORECASE),
    re.compile(r"\b(?:revised|rewritten|replacement)\s+(?:scene|dialogue|passage|paragraph|prose)", re.IGNORECASE),
    re.compile(r"\btry this\s+(?:version|draft|line|dialogue)", re.IGNORECASE),
]
SENSITIVE_SOURCE_PATTERNS = [
    re.compile(r"\bgender\b", re.IGNORECASE),
    re.compile(r"\btransgender\b", re.IGNORECASE),
    re.compile(r"\bbody odor\b", re.IGNORECASE),
    re.compile(r"\bugly\b|\blumpy\b", re.IGNORECASE),
]


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
        description="Create bounded external-dataset review batches from local retrieved artifacts."
    )
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--batch-size", required=True, type=int)
    parser.add_argument("--start-offset", required=True, type=int)
    parser.add_argument("--max-batches", required=True, type=int)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--input-sample",
        type=Path,
        help="Optional local Moral Stories sample JSONL. Defaults to the largest local Moral Stories sample.",
    )
    parser.add_argument("--review-only", nargs="?", const="true", default="true", type=parse_bool)
    parser.add_argument(
        "--promote-only-if-license-reviewed",
        nargs="?",
        const="true",
        default="false",
        type=parse_bool,
    )
    parser.add_argument("--schemas", type=Path, default=SCHEMA_DIR)
    return parser.parse_args(argv)


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: JSONL record must be an object.")
            records.append(value)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False))
            handle.write("\n")


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def source_license(metadata: dict[str, Any]) -> str:
    return str(metadata.get("license_found") or metadata.get("expected_license") or "UNKNOWN")


def source_url(metadata: dict[str, Any]) -> str:
    return str(metadata.get("source_url") or "https://huggingface.co/datasets/demelin/moral_stories")


def is_license_reviewed(config_text: str, dataset_id: str) -> bool:
    marker = f"- id: {dataset_id}"
    index = config_text.find(marker)
    if index < 0:
        return False
    next_dataset = config_text.find("\n  - id:", index + len(marker))
    block = config_text[index:] if next_dataset < 0 else config_text[index:next_dataset]
    return "license_provenance_reviewed: true" in block and (
        "approved_for_derived_analysis_training" in block
    )


def largest_moral_stories_sample() -> Path:
    samples_dir = TRAINING_DIR / "data" / "external" / "samples"
    candidates = sorted(samples_dir.glob("moral_stories_sample*.jsonl"))
    if not candidates:
        return samples_dir / "moral_stories_sample.jsonl"
    return max(candidates, key=lambda path: len(read_jsonl(path)))


def load_moral_stories_artifacts(input_sample: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any], bool, Path]:
    sample_path = resolve(input_sample) if input_sample else largest_moral_stories_sample()
    metadata_path = TRAINING_DIR / "data" / "external" / "metadata" / "moral_stories_manifest.json"
    config_path = TRAINING_DIR / "configs" / "external_dataset_sources.yaml"
    rows = read_jsonl(sample_path)
    metadata = read_json(metadata_path)
    license_reviewed = is_license_reviewed(config_path.read_text(encoding="utf-8"), SUPPORTED_DATASET_ID)
    return rows, metadata, license_reviewed, sample_path


def existing_source_record_ids(output_dir: Path) -> set[str]:
    ids: set[str] = set()
    for path in sorted(resolve(output_dir).glob("*.jsonl")):
        for record in read_jsonl(path):
            metadata = record.get("metadata")
            if isinstance(metadata, dict) and metadata.get("source_dataset_id") == SUPPORTED_DATASET_ID:
                source_id = metadata.get("source_record_id")
                if isinstance(source_id, str) and source_id:
                    ids.add(source_id)
    return ids


def is_usable_row(row: dict[str, Any]) -> bool:
    return all(isinstance(row.get(field), str) and row[field].strip() for field in SOURCE_FIELDS)


def storyform_context() -> dict[str, Any]:
    no_storyform = (
        "INSUFFICIENT_EVIDENCE: Moral Stories source rows do not provide approved "
        "Dramatica/NCP storyform truth for this field."
    )
    return {
        "throughlines": {
            key: {
                "domain": no_storyform,
                "concern": no_storyform,
                "issue": no_storyform,
                "problem": no_storyform,
                "solution": no_storyform,
                "summary": (
                    "External source supplies social norm, situation, intention, action, "
                    "and consequence fields only; no throughline assignment is approved."
                ),
            }
            for key in ("overall_story", "main_character", "influence_character", "relationship_story")
        },
        "dynamics": {
            "main_character_resolve": "INSUFFICIENT_EVIDENCE: no Change or Steadfast truth is provided.",
            "story_outcome": "INSUFFICIENT_EVIDENCE: no Success or Failure truth is provided.",
            "story_judgment": "INSUFFICIENT_EVIDENCE: no Good or Bad truth is provided.",
            "story_driver": "INSUFFICIENT_EVIDENCE: no Action or Decision driver truth is provided.",
            "story_limit": "INSUFFICIENT_EVIDENCE: no Timelock or Optionlock truth is provided.",
        },
        "central_inequity": {
            "problem": "INSUFFICIENT_EVIDENCE: no approved Dramatica problem element is provided.",
            "solution": "INSUFFICIENT_EVIDENCE: no approved Dramatica solution element is provided.",
        },
        "external_source_context": {
            "dataset_id": SUPPORTED_DATASET_ID,
            "source_alignment_status": "external_source_no_dramatica_storyform",
        },
    }


def bible_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_dataset": "Moral Stories",
        "source_record_id": row["ID"],
        "source_fields": {field: row[field] for field in SOURCE_FIELDS if field != "ID"},
        "review_limitation": (
            "The row is structured source context, not approved Dramatica or NCP storyform truth."
        ),
    }


def scene_text(row: dict[str, Any]) -> str:
    labels = [
        ("Norm", "norm"),
        ("Situation", "situation"),
        ("Intention", "intention"),
        ("Normative action", "moral_action"),
        ("Normative consequence", "moral_consequence"),
        ("Divergent action", "immoral_action"),
        ("Divergent consequence", "immoral_consequence"),
    ]
    return "\n".join(f"{label}: {row[field]}" for label, field in labels)


def common_metadata(
    row: dict[str, Any],
    task: str,
    metadata: dict[str, Any],
    batch_name: str,
    output_index: int,
    sample_path: Path,
) -> dict[str, Any]:
    return {
        "source_type": "external_dataset",
        "source_dataset_id": SUPPORTED_DATASET_ID,
        "source_dataset_name": "Moral Stories",
        "source_url": source_url(metadata),
        "source_license": source_license(metadata),
        "license_provenance_reviewed": False,
        "external_license_provenance_reviewed": False,
        "source_provenance_status": "retrieved_metadata_pending_record_review",
        "source_record_id": row["ID"],
        "source_fields_used": list(SOURCE_FIELDS),
        "source_sample_path": relative_path(sample_path),
        "source_metadata_path": "training/data/external/metadata/moral_stories_manifest.json",
        "source_alignment_status": "external_source_no_dramatica_storyform",
        "transformation_notes": [
            f"Converted as {task} draft review candidate from structured Moral Stories fields.",
            "No Dramatica/NCP storyform labels were inferred from the source row.",
            "Gold output is analysis-only and does not write, rewrite, continue, imitate, or improve prose.",
        ],
        "human_review_required": True,
        "human_review_status": "required",
        "training_eligibility": "draft_needs_human_review",
        "external_dataset_conversion_status": "draft_review_candidate",
        "can_promote_without_license_review": False,
        "conversion_batch": batch_name,
        "conversion_output_index": output_index,
    }


def throughline_alignment() -> dict[str, Any]:
    concern = (
        "No approved Dramatica/NCP storyform exists for this external row; do not treat "
        "the Moral Stories fields as throughline truth."
    )
    return {
        key: {"present": False, "evidence": [], "concerns": [concern]}
        for key in ("overall_story", "main_character", "influence_character", "relationship_story")
    }


def story_check_output(variant: int) -> dict[str, Any]:
    warnings = [
        "[Plot/Temporal] The row provides action and consequence fields, but no act position, driver, or sequence context for a full storyform check.",
        "[Character] The actor's intention is visible as source context, but no Main Character throughline, resolve, or internal arc is approved.",
        "[Factual] Human review should verify causal plausibility before any training use.",
    ]
    suggestions = [
        "What approved storyform facts would be needed before scoring theme drift with confidence?",
        "Which source fields should a reviewer treat as causal evidence rather than moral classification labels?",
        "What owner decision would distinguish external conflict from Main Character pressure in this scenario?",
    ]
    if variant % 2:
        warnings = [
            "[Character] The intention/action/consequence chain can be checked for local consistency, but it cannot establish a Dramatica character function.",
            "[Plot/Temporal] The source row has a compact before/after structure, not enough temporal context to infer story turns.",
            "[Worldbuilding] The social norm is contextual guidance only; it is not an approved thematic Issue or Problem.",
        ]
        suggestions = [
            "What structural context would show whether this causal chain belongs to any throughline?",
            "Which consequence facts require human verification before becoming training supervision?",
            "What missing storyform decision would justify any character or relationship reading?",
        ]
    return {
        "task": "story_check",
        "coherence_score": 4,
        "throughline_alignment": throughline_alignment(),
        "theme_drift": {
            "status": "insufficient_evidence",
            "reason": (
                "The source row contains norm, intention, action, and consequence fields, "
                "but no approved thematic Issue, Problem, Solution, or throughline map."
            ),
        },
        "character_consistency": {
            "status": "insufficient_evidence",
            "reason": (
                "Local intention/action/consequence consistency can be reviewed, but the source "
                "does not approve character roles, arc dynamics, or continuity facts."
            ),
        },
        "warnings": warnings,
        "suggestions": suggestions,
        "insufficient_evidence": [
            "Approved Overall Story, Main Character, Influence Character, and Relationship Story assignments.",
            "Approved Dramatica domains, concerns, issues, problems, and solutions.",
            "Approved story dynamics, including resolve, outcome, judgment, driver, and limit.",
            "Record-level human review for this external transformation.",
        ],
    }


def writer_questions_output() -> dict[str, Any]:
    return {
        "task": "writer_questions",
        "questions": [
            {
                "throughline": "insufficient_evidence",
                "story_point": "source-to-storyform mapping",
                "diagnostic_purpose": "Identify missing storyform facts before classification.",
                "question": "What approved storyform context would be needed before mapping this Moral Stories row to any throughline?",
            },
            {
                "throughline": "mixed",
                "story_point": "causal pressure",
                "diagnostic_purpose": "Separate source-field causality from Dramatica interpretation.",
                "question": "Which intention, action, and consequence facts should a reviewer treat as causal pressure rather than as final storyform labels?",
            },
            {
                "throughline": "insufficient_evidence",
                "story_point": "owner decision",
                "diagnostic_purpose": "Prevent unapproved structural inference.",
                "question": "What owner decision would be required before identifying a character or relationship role?",
            },
        ],
        "no_prose_generated": True,
    }


def refusal_request(variant: int) -> tuple[str, str]:
    requests = [
        ("Write a short scene that continues this moral scenario and shows what happens next.", "prose_generation"),
        ("Rewrite the scenario as polished story prose with more emotion.", "prose_rewrite"),
        ("Generate dialogue between the characters in this situation.", "prose_generation"),
        ("Revise this text into a more dramatic paragraph.", "prose_rewrite"),
        ("Compose an ending for the story using the same style.", "prose_generation"),
    ]
    return requests[variant % len(requests)]


def refusal_output(request_type: str) -> dict[str, Any]:
    return {
        "task": "out_of_scope_refusal",
        "request_type": request_type,
        "allowed_help": ["analysis", "diagnostic questions", "structural classification"],
        "message": REFUSAL_MESSAGE,
    }


def task_for_index(index: int) -> str:
    cycle = ("story_check", "story_check", "writer_questions")
    return cycle[index % len(cycle)]


def make_record(
    row: dict[str, Any],
    task: str,
    batch_name: str,
    output_index: int,
    global_index: int,
    metadata: dict[str, Any],
    sample_path: Path,
) -> dict[str, Any]:
    if task == "story_check":
        user_request = (
            "Return a schema-valid Story Check diagnostic for this Moral Stories row. "
            "Focus on source-field consistency, causal pressure, and missing Dramatica/NCP evidence."
        )
        gold_output = story_check_output(global_index)
    elif task == "writer_questions":
        user_request = (
            "Return diagnostic questions about what structural information is missing before "
            "this Moral Stories row could be mapped into a storyform."
        )
        gold_output = writer_questions_output()
    elif task == "out_of_scope_refusal":
        user_request, request_type = refusal_request(global_index)
        gold_output = refusal_output(request_type)
    else:
        raise ValueError(f"Unsupported task: {task}")
    return {
        "id": f"{batch_name}_{output_index:03d}",
        "task": task,
        "storyform_context": storyform_context(),
        "bible_summary": bible_summary(row),
        "scene_text": scene_text(row),
        "user_request": user_request,
        "gold_output": gold_output,
        "metadata": common_metadata(row, task, metadata, batch_name, output_index, sample_path),
    }


def validate_records(records: list[dict[str, Any]], schema_dir: Path) -> list[str]:
    validators = load_validators(schema_dir)
    errors: list[str] = []
    for line_number, record in enumerate(records, start=1):
        for finding in validate_record(record, line_number, validators, strict=True):
            if finding.severity == "error":
                errors.append(f"line {finding.line}: {finding.message}")
    return errors


def has_complete_provenance(record: dict[str, Any]) -> bool:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        return False
    required = ("source_record_id", "source_url", "source_license", "source_provenance_status", "transformation_notes")
    return all(bool(metadata.get(key)) for key in required)


def contains_prose_output(record: dict[str, Any]) -> bool:
    output_text = json.dumps(record.get("gold_output"), ensure_ascii=False)
    return any(pattern.search(output_text) for pattern in PROSE_OUTPUT_PATTERNS)


def has_confident_throughline_label(record: dict[str, Any]) -> bool:
    if record.get("task") == "throughline_classification":
        primary = ((record.get("gold_output") or {}).get("primary_throughline") or "").lower()
        return primary in PROHIBITED_WRITER_QUESTION_THROUGHLINES
    if record.get("task") == "writer_questions":
        questions = (record.get("gold_output") or {}).get("questions")
        if isinstance(questions, list):
            return any(
                isinstance(item, dict)
                and str(item.get("throughline", "")).lower() in PROHIBITED_WRITER_QUESTION_THROUGHLINES
                for item in questions
            )
    return False


def sensitive_source(record: dict[str, Any]) -> bool:
    text = json.dumps(record.get("bible_summary", {}).get("source_fields", {}), ensure_ascii=False)
    return any(pattern.search(text) for pattern in SENSITIVE_SOURCE_PATTERNS)


def promotion_rejection_reasons(record: dict[str, Any], license_reviewed: bool) -> list[str]:
    reasons: list[str] = []
    if not license_reviewed:
        reasons.append("license_not_reviewed")
    if not has_complete_provenance(record):
        reasons.append("incomplete_provenance")
    if contains_prose_output(record):
        reasons.append("prose_output_risk")
    if has_confident_throughline_label(record):
        reasons.append("confident_throughline_label")
    if sensitive_source(record):
        reasons.append("sensitive_source_requires_manual_review")
    return reasons


def promote_record(record: dict[str, Any]) -> dict[str, Any]:
    promoted = deepcopy(record)
    metadata = promoted["metadata"]
    metadata["training_eligibility"] = "eligible_for_training"
    metadata["human_review_required"] = False
    metadata["human_review_status"] = "complete"
    metadata["license_provenance_reviewed"] = True
    metadata["external_license_provenance_reviewed"] = True
    metadata["source_provenance_status"] = "license_provenance_reviewed_approved_for_derived_analysis_training"
    metadata["external_dataset_conversion_status"] = "promoted_analysis_only_training"
    metadata["promotion_review_status"] = "promoted_for_analysis_only_training"
    metadata["promotion_review_notes"] = (
        "Promoted by conservative external-dataset batch converter after schema, provenance, "
        "license, no-prose, and no-confident-throughline checks."
    )
    return promoted


def write_review_notes(
    batch_name: str,
    review_path: Path | None,
    promoted_path: Path | None,
    records: list[dict[str, Any]],
    promoted: list[dict[str, Any]],
    rejected: dict[str, list[str]],
    skipped_reason: str | None,
) -> None:
    counts = Counter(record["task"] for record in records)
    promoted_counts = Counter(record["task"] for record in promoted)
    lines = [
        f"# {batch_name.replace('_', ' ').title()} Review Notes",
        "",
        f"- Dataset: `{SUPPORTED_DATASET_ID}`",
        f"- Review output: `{relative_path(review_path) if review_path else 'not written'}`",
        f"- Promoted output: `{relative_path(promoted_path) if promoted_path else 'not written'}`",
        f"- Review records created: {len(records)}",
        f"- Promoted records created: {len(promoted)}",
        f"- Review task counts: {dict(counts)}",
        f"- Promoted task counts: {dict(promoted_counts)}",
        f"- throughline_classification records created: {counts.get('throughline_classification', 0)}",
        "",
        "Moral Stories records are external source material only. They do not provide Dramatica/NCP storyform truth.",
        "",
    ]
    if skipped_reason:
        lines.extend(["## Skipped", "", skipped_reason, ""])
    if rejected:
        lines.extend(["## Promotion Holds", ""])
        for record_id, reasons in rejected.items():
            lines.append(f"- `{record_id}`: {', '.join(reasons)}")
        lines.append("")
    write_report(REPORTS_DIR / f"{batch_name}_review_notes.md", lines)


def convert_batches(args: argparse.Namespace) -> tuple[int, int]:
    if args.dataset_id != SUPPORTED_DATASET_ID:
        raise ValueError(f"Only {SUPPORTED_DATASET_ID!r} is currently supported.")
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive.")
    if args.max_batches < 1:
        raise ValueError("--max-batches must be positive.")
    if args.start_offset < 0:
        raise ValueError("--start-offset must be non-negative.")

    output_dir = resolve(args.output_dir)
    rows, metadata, license_reviewed, sample_path = load_moral_stories_artifacts(args.input_sample)
    existing_ids = existing_source_record_ids(output_dir)
    usable_rows = [row for row in rows if is_usable_row(row)]
    unused_rows = [row for row in usable_rows if row["ID"] not in existing_ids]
    selected_pool = unused_rows[args.start_offset :]
    validators_errors: list[str] = []
    newly_reviewed = 0
    newly_promoted = 0

    for batch_index in range(args.max_batches):
        batch_number = 2 + batch_index
        batch_name = f"moral_stories_batch_{batch_number:03d}"
        start = batch_index * args.batch_size
        batch_rows = selected_pool[start : start + args.batch_size]
        skipped_reason = None
        review_path: Path | None = None
        promoted_path: Path | None = None
        records: list[dict[str, Any]] = []
        promoted: list[dict[str, Any]] = []
        rejected: dict[str, list[str]] = {}

        if not batch_rows:
            skipped_reason = (
                "No unused local Moral Stories source rows were available. "
                f"Local usable rows: {len(usable_rows)}; existing Moral Stories source_record_id values: {len(existing_ids)}. "
                "Retrieve or provide additional reviewed local source rows before creating more records."
            )
        else:
            for output_index, row in enumerate(batch_rows, start=1):
                task = task_for_index(output_index - 1)
                records.append(
                    make_record(
                        row=row,
                        task=task,
                        batch_name=batch_name,
                        output_index=output_index,
                        global_index=start + output_index - 1,
                        metadata=metadata,
                        sample_path=sample_path,
                    )
                )
            validators_errors = validate_records(records, resolve(args.schemas))
            if validators_errors:
                raise ValueError("Generated records failed validation:\n" + "\n".join(validators_errors))
            review_path = output_dir / f"{batch_name}.review.jsonl"
            write_jsonl(review_path, records)
            newly_reviewed += len(records)

            if not args.review_only and args.promote_only_if_license_reviewed:
                for record in records:
                    reasons = promotion_rejection_reasons(record, license_reviewed)
                    if reasons:
                        rejected[record["id"]] = reasons
                    else:
                        promoted.append(promote_record(record))
                if promoted:
                    promoted_path = output_dir / f"{batch_name}.promoted.jsonl"
                    promoted_errors = validate_records(promoted, resolve(args.schemas))
                    if promoted_errors:
                        raise ValueError("Promoted records failed validation:\n" + "\n".join(promoted_errors))
                    write_jsonl(promoted_path, promoted)
                    newly_promoted += len(promoted)
                    write_promotion_report(batch_name, promoted_path, promoted, rejected)
            elif not args.review_only:
                skipped_reason = (
                    "Promotion was not attempted because --promote-only-if-license-reviewed was false."
                )

        write_review_notes(batch_name, review_path, promoted_path, records, promoted, rejected, skipped_reason)

    return newly_reviewed, newly_promoted


def write_promotion_report(
    batch_name: str,
    promoted_path: Path,
    promoted: list[dict[str, Any]],
    rejected: dict[str, list[str]],
) -> None:
    counts = Counter(record["task"] for record in promoted)
    lines = [
        f"# {batch_name.replace('_', ' ').title()} Promotion Report",
        "",
        f"- Promoted output: `{relative_path(promoted_path)}`",
        f"- Promoted count: {len(promoted)}",
        f"- Promoted task counts: {dict(counts)}",
        f"- throughline_classification promoted: {counts.get('throughline_classification', 0)}",
        "- License/provenance: reviewed and approved for derived analysis-only training",
        "- No prose-generation outputs promoted.",
        "- No confident Dramatica throughline labels promoted.",
        "- Moral Stories cannot supply Dramatica/NCP storyform truth.",
        "",
    ]
    if rejected:
        lines.extend(["## Held Records", ""])
        for record_id, reasons in rejected.items():
            lines.append(f"- `{record_id}`: {', '.join(reasons)}")
        lines.append("")
    write_report(REPORTS_DIR / f"{batch_name}_promotion_report.md", lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    reviewed, promoted = convert_batches(args)
    print(f"New review records: {reviewed}")
    print(f"New promoted records: {promoted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
