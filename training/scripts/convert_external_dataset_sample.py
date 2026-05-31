from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from validate_dataset import load_validators, validate_record


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

SUPPORTED_DATASET_ID = "moral_stories"
OUTPUT_STEM = "moral_stories_first_batch"
REQUIRED_SOURCE_FIELDS = [
    "ID",
    "norm",
    "situation",
    "intention",
    "moral_action",
    "moral_consequence",
    "immoral_action",
    "immoral_consequence",
]
TASK_TARGETS = [
    ("story_check", 12),
    ("writer_questions", 8),
    ("out_of_scope_refusal", 5),
]
REFUSAL_MESSAGE = (
    "I can analyze structure and ask diagnostic questions, but I cannot write or rewrite story prose."
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a local Moral Stories external sample into schema-valid draft "
            "review-candidate SFT records."
        )
    )
    parser.add_argument("--dataset-id", required=True, help="External dataset id. Must be moral_stories.")
    parser.add_argument("--input-sample", required=True, type=Path, help="Path to local sample JSONL.")
    parser.add_argument("--metadata", required=True, type=Path, help="Path to local metadata manifest JSON.")
    parser.add_argument("--schemas", required=True, type=Path, help="Path to training/schemas.")
    parser.add_argument("--output", required=True, type=Path, help="Output JSONL path.")
    parser.add_argument("--max-records", required=True, type=int, help="Maximum records to convert.")
    return parser.parse_args(argv)


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} must be a JSON object.")
            rows.append(value)
    return rows


def is_usable_row(row: dict[str, Any]) -> bool:
    return all(isinstance(row.get(field), str) and row[field].strip() for field in REQUIRED_SOURCE_FIELDS)


def task_plan(max_records: int, usable_count: int) -> list[str]:
    if max_records < 1:
        return []
    expanded = [task for task, count in TASK_TARGETS for _ in range(count)]
    return expanded[: min(max_records, usable_count, len(expanded))]


def source_license(metadata: dict[str, Any]) -> str:
    return str(metadata.get("license_found") or metadata.get("expected_license") or "UNKNOWN")


def source_url(metadata: dict[str, Any]) -> str:
    return str(metadata.get("source_url") or "https://huggingface.co/datasets/demelin/moral_stories")


def storyform_context() -> dict[str, Any]:
    no_storyform = (
        "INSUFFICIENT_EVIDENCE: Moral Stories source rows do not provide approved "
        "Dramatica/NCP storyform truth for this field."
    )
    return {
        "throughlines": {
            throughline: {
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
            for throughline in (
                "overall_story",
                "main_character",
                "influence_character",
                "relationship_story",
            )
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
        "source_fields": {
            "norm": row["norm"],
            "situation": row["situation"],
            "intention": row["intention"],
            "moral_action": row["moral_action"],
            "moral_consequence": row["moral_consequence"],
            "immoral_action": row["immoral_action"],
            "immoral_consequence": row["immoral_consequence"],
        },
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
    input_sample: Path,
    metadata_path: Path,
    output_index: int,
) -> dict[str, Any]:
    return {
        "source_type": "external_dataset",
        "source_dataset_id": SUPPORTED_DATASET_ID,
        "source_dataset_name": "Moral Stories",
        "source_url": source_url(metadata),
        "source_license": source_license(metadata),
        "license_provenance_reviewed": False,
        "source_provenance_status": "retrieved_metadata_pending_license_provenance_review",
        "source_record_id": row["ID"],
        "source_fields_used": list(REQUIRED_SOURCE_FIELDS),
        "source_sample_path": relative_path(input_sample),
        "source_metadata_path": relative_path(metadata_path),
        "source_alignment_status": "external_source_no_dramatica_storyform",
        "transformation_notes": [
            f"Converted as {task} draft review candidate from structured Moral Stories fields.",
            "No Dramatica/NCP storyform labels were inferred from the source row.",
            "Gold output is analysis-only and does not write, rewrite, continue, imitate, or improve prose.",
        ],
        "human_review_required": True,
        "training_eligibility": "draft_needs_human_review",
        "external_dataset_conversion_status": "draft_review_candidate",
        "can_promote_without_license_review": False,
        "conversion_batch": OUTPUT_STEM,
        "conversion_output_index": output_index,
    }


def throughline_alignment() -> dict[str, Any]:
    concern = (
        "No approved Dramatica/NCP storyform exists for this external row; do not treat "
        "the Moral Stories fields as throughline truth."
    )
    return {
        "overall_story": {"present": False, "evidence": [], "concerns": [concern]},
        "main_character": {"present": False, "evidence": [], "concerns": [concern]},
        "influence_character": {"present": False, "evidence": [], "concerns": [concern]},
        "relationship_story": {"present": False, "evidence": [], "concerns": [concern]},
    }


def story_check_output(row: dict[str, Any], variant: int) -> dict[str, Any]:
    warning_sets = [
        [
            "[Plot/Temporal] The row provides parallel action and consequence fields, but no act position, driver, or sequence context for a full storyform check.",
            "[Character] The actor's intention is visible as source context, but no Main Character throughline, resolve, or internal arc is approved.",
            "[Factual] Human review should verify the causal plausibility of both consequence fields before any training use.",
        ],
        [
            "[Character] The intention/action/consequence chain can be checked for local consistency, but it cannot establish a Dramatica character function.",
            "[Plot/Temporal] The source row has a compact before/after structure, not enough temporal context to infer story turns.",
            "[Worldbuilding] The social norm is contextual guidance only; it is not an approved thematic Issue or Problem.",
        ],
        [
            "[Factual] The moral and divergent paths may encode dataset assumptions that need human review before reuse.",
            "[Character] The actor pressure is source-visible, but the row does not identify a Main Character, Influence Character, or Relationship Story role.",
            "[Plot/Temporal] Consequences are available as source fields, but their larger plot function is missing.",
        ],
    ]
    suggestion_sets = [
        [
            "What approved storyform facts would be needed before scoring theme drift with confidence?",
            "Which source fields should a reviewer treat as causal evidence rather than moral classification labels?",
            "What owner decision would distinguish external conflict from Main Character pressure in this scenario?",
        ],
        [
            "What structural context would show whether the intention/action/consequence chain belongs to an Overall Story throughline?",
            "Which consequence facts require human verification before becoming training supervision?",
            "What missing storyform decision would justify any Influence Character or Relationship Story reading?",
        ],
        [
            "What larger goal, stakes, and opposition would be needed to map this row into a storyform?",
            "Which actor pressure is source-grounded, and which interpretation would require owner approval?",
            "What evidence would let a reviewer separate thematic material from social-norm annotation?",
        ],
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
                "Local intention/action/consequence consistency can be reviewed, but the "
                "source does not approve character roles, arc dynamics, or continuity facts."
            ),
        },
        "warnings": warning_sets[variant % len(warning_sets)],
        "suggestions": suggestion_sets[variant % len(suggestion_sets)],
        "insufficient_evidence": [
            "Approved Overall Story, Main Character, Influence Character, and Relationship Story assignments.",
            "Approved Dramatica domains, concerns, issues, problems, and solutions.",
            "Approved story dynamics, including resolve, outcome, judgment, driver, and limit.",
            "Human-reviewed license/provenance decision for this external transformation.",
        ],
    }


def writer_questions_output(row: dict[str, Any], variant: int) -> dict[str, Any]:
    question_sets = [
        [
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
                "question": "What owner decision would be required before identifying a Main Character, Influence Character, or Relationship Story role?",
            },
        ],
        [
            {
                "throughline": "overall_story",
                "story_point": "goal and stakes",
                "diagnostic_purpose": "Ask whether the row can support external-conflict analysis after review.",
                "question": "What larger goal, stakes, and opposition would a reviewer need before treating the scenario as Overall Story material?",
            },
            {
                "throughline": "insufficient_evidence",
                "story_point": "theme evidence",
                "diagnostic_purpose": "Avoid confusing a source norm with an approved thematic Issue.",
                "question": "What evidence would show whether the norm field reflects a thematic Issue, a local value judgment, or only dataset annotation?",
            },
            {
                "throughline": "mixed",
                "story_point": "consequence logic",
                "diagnostic_purpose": "Check whether consequences support structural pressure after human review.",
                "question": "Which consequence facts need verification before they can be used as supervision for structural analysis?",
            },
        ],
        [
            {
                "throughline": "main_character",
                "story_point": "personal pressure",
                "diagnostic_purpose": "Ask what would be needed before assigning internal character function.",
                "question": "What internal viewpoint evidence would be needed before treating the actor's intention as Main Character pressure?",
            },
            {
                "throughline": "influence_character",
                "story_point": "pressure source",
                "diagnostic_purpose": "Prevent unsupported Influence Character assignment.",
                "question": "What recurring pressure from another perspective would be needed before considering an Influence Character reading?",
            },
            {
                "throughline": "relationship_story",
                "story_point": "relationship arc",
                "diagnostic_purpose": "Identify missing relationship evidence.",
                "question": "What relationship continuity would be needed before identifying a Relationship Story throughline?",
            },
        ],
    ]
    return {
        "task": "writer_questions",
        "questions": question_sets[variant % len(question_sets)],
        "no_prose_generated": True,
    }


def refusal_request(variant: int) -> tuple[str, str]:
    requests = [
        (
            "Write a short scene that continues this moral scenario and shows what happens next.",
            "prose_generation",
        ),
        (
            "Rewrite the scenario as polished story prose with more emotion.",
            "prose_rewrite",
        ),
        (
            "Generate dialogue between the characters in this situation.",
            "prose_generation",
        ),
        (
            "Revise this text into a more dramatic paragraph.",
            "prose_rewrite",
        ),
        (
            "Compose an ending for the story using the same style.",
            "prose_generation",
        ),
    ]
    return requests[variant % len(requests)]


def refusal_output(request_type: str) -> dict[str, Any]:
    return {
        "task": "out_of_scope_refusal",
        "request_type": request_type,
        "allowed_help": ["analysis", "diagnostic questions", "structural classification"],
        "message": REFUSAL_MESSAGE,
    }


def make_record(
    row: dict[str, Any],
    task: str,
    output_index: int,
    task_index: int,
    metadata: dict[str, Any],
    input_sample: Path,
    metadata_path: Path,
) -> dict[str, Any]:
    if task == "story_check":
        user_request = (
            "Return a schema-valid Story Check diagnostic for this Moral Stories row. "
            "Focus on source-field consistency, causal pressure, and missing Dramatica/NCP evidence."
        )
        gold_output = story_check_output(row, task_index)
    elif task == "writer_questions":
        user_request = (
            "Return diagnostic questions about what structural information is missing before "
            "this Moral Stories row could be mapped into a storyform."
        )
        gold_output = writer_questions_output(row, task_index)
    elif task == "out_of_scope_refusal":
        user_request, request_type = refusal_request(task_index)
        gold_output = refusal_output(request_type)
    else:
        raise ValueError(f"Unsupported task: {task}")

    return {
        "id": f"{OUTPUT_STEM}_{output_index:03d}",
        "task": task,
        "storyform_context": storyform_context(),
        "bible_summary": bible_summary(row),
        "scene_text": scene_text(row),
        "user_request": user_request,
        "gold_output": gold_output,
        "metadata": common_metadata(
            row=row,
            task=task,
            metadata=metadata,
            input_sample=input_sample,
            metadata_path=metadata_path,
            output_index=output_index,
        ),
    }


def validate_records(records: list[dict[str, Any]], schema_dir: Path) -> None:
    validators = load_validators(schema_dir)
    errors: list[str] = []
    for line_number, record in enumerate(records, start=1):
        for finding in validate_record(record, line_number, validators, strict=True):
            if finding.severity == "error":
                line = f":{finding.line}" if finding.line is not None else ""
                errors.append(f"{line}: {finding.message}")
    if errors:
        joined = "\n".join(errors)
        raise ValueError(f"Generated records failed validation:\n{joined}")


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False))
            handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.dataset_id != SUPPORTED_DATASET_ID:
        raise ValueError(f"--dataset-id must be {SUPPORTED_DATASET_ID!r}.")

    metadata = read_json(args.metadata)
    rows = read_jsonl(args.input_sample)
    usable_rows = [row for row in rows if is_usable_row(row)]
    selected_tasks = task_plan(args.max_records, len(usable_rows))

    task_indices: Counter[str] = Counter()
    records: list[dict[str, Any]] = []
    for output_index, (row, task) in enumerate(zip(usable_rows, selected_tasks), start=1):
        task_indices[task] += 1
        records.append(
            make_record(
                row=row,
                task=task,
                output_index=output_index,
                task_index=task_indices[task] - 1,
                metadata=metadata,
                input_sample=args.input_sample,
                metadata_path=args.metadata,
            )
        )

    validate_records(records, args.schemas)
    write_jsonl(records, args.output)

    counts = Counter(record["task"] for record in records)
    print(f"Wrote {len(records)} record(s) to {args.output}")
    print(f"story_check: {counts.get('story_check', 0)}")
    print(f"writer_questions: {counts.get('writer_questions', 0)}")
    print(f"out_of_scope_refusal: {counts.get('out_of_scope_refusal', 0)}")
    print(f"throughline_classification: {counts.get('throughline_classification', 0)}")
    if len(records) < min(args.max_records, sum(count for _, count in TASK_TARGETS)):
        print(
            "Shortfall: local sample did not contain enough usable rows to meet the requested "
            f"maximum. Usable rows: {len(usable_rows)}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
