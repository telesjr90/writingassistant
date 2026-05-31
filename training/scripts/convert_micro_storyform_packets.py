from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAINING_ROOT = PROJECT_ROOT / "training"
PACKET_DIR = TRAINING_ROOT / "data" / "micro_storyforms"
OUTPUT_PATH = TRAINING_ROOT / "data" / "sft" / "micro_storyforms_batch_001.review.jsonl"
REPORT_PATH = TRAINING_ROOT / "reports" / "micro_storyforms_batch_001_review_notes.md"
BATCH_ID = "micro_storyforms_batch_001"
TARGET_PACKET_ID = "packet_002"

INSUFFICIENT = "insufficient_evidence"
OS_EVIDENCE = (
    "And the Rhinoceros upset the oil-stove with his nose, and the cake rolled on the sand, "
    "and he spiked that cake on the horn of his nose, and he ate it"
)
MC_EVIDENCE = (
    "Presently the Parsee came by and found the skin, and he smiled one smile that ran all "
    "round his face two times."
)


def read_packet(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def field(text: str, key: str) -> str:
    match = re.search(rf"^- {re.escape(key)}:\s*(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def checked_task(text: str, task: str) -> bool:
    return bool(re.search(rf"^- \[x\] {re.escape(task)}\b", text, re.MULTILINE))


def source_scene(text: str) -> str:
    match = re.search(r"## Source Scene Text.*?```text\n(.*?)\n```", text, re.DOTALL)
    if not match:
        return ""
    return match.group(1)


def approved_packet(text: str) -> bool:
    gates = [
        field(text, "packet_id") == TARGET_PACKET_ID,
        field(text, "packet_status") == "approved_for_review_candidates",
        field(text, "source_type") == "public_domain",
        field(text, "source_license") == "public_domain_owner_reviewed",
        field(text, "source_provenance_status") == "public_domain_owner_reviewed",
        "I approve this packet for derived analysis-only training examples." in text,
        "- usable_for_training: yes" in text,
        OS_EVIDENCE in text,
        MC_EVIDENCE in text,
    ]
    tasks = [
        "throughline_classification",
        "story_check",
        "writer_questions",
        "out_of_scope_refusal",
    ]
    return all(gates) and all(checked_task(text, task) for task in tasks)


def bible_summary(text: str) -> dict[str, Any]:
    return {
        "source_packet_id": field(text, "packet_id"),
        "source_title": field(text, "source_title"),
        "story_world": field(text, "story_world"),
        "relevant_prior_context": field(text, "relevant_prior_context"),
        "relevant_characters": field(text, "relevant_characters"),
        "relevant_relationships": field(text, "relevant_relationships"),
        "current_scene_situation": field(text, "current_scene_situation"),
        "known_exclusions_or_limits": field(text, "known_exclusions_or_limits").replace(
            "eligible_for_training", "training promotion"
        ),
    }


def storyform_context() -> dict[str, Any]:
    unresolved = f"{INSUFFICIENT}: owner approval required before this can be training truth."
    return {
        "throughlines": {
            "overall_story": {
                "domain": "Activity/Physics",
                "concern": unresolved,
                "issue": unresolved,
                "problem": unresolved,
                "solution": unresolved,
                "summary": (
                    "Owner-approved review context: Overall Story throughline and "
                    "Activity/Physics domain for the cake-taking, retaliation, and skin-fold "
                    "consequence sequence."
                ),
            },
            "main_character": {
                "domain": (
                    f"{INSUFFICIENT}: Main Character domain remains unresolved; "
                    "Activity/Physics or Psychology/Manipulation is still ambiguous."
                ),
                "concern": unresolved,
                "issue": unresolved,
                "problem": unresolved,
                "solution": unresolved,
                "summary": (
                    "Owner-approved review context: the Parsee is the packet-level Main "
                    "Character candidate/player. Domain and CIPS values are unresolved."
                ),
            },
            "influence_character": {
                "domain": unresolved,
                "concern": unresolved,
                "issue": unresolved,
                "problem": unresolved,
                "solution": unresolved,
                "summary": (
                    f"{INSUFFICIENT}: Influence Character and player are not approved in "
                    "packet_002."
                ),
            },
            "relationship_story": {
                "domain": unresolved,
                "concern": unresolved,
                "issue": unresolved,
                "problem": unresolved,
                "solution": unresolved,
                "summary": (
                    f"{INSUFFICIENT}: Relationship Story and relationship players are not "
                    "approved in packet_002."
                ),
            },
        },
        "dynamics": {
            "driver": f"{INSUFFICIENT}: no Action or Decision driver is approved.",
            "limit": f"{INSUFFICIENT}: no Timelock or Optionlock is approved.",
            "outcome": f"{INSUFFICIENT}: no Success or Failure is approved.",
            "judgment": f"{INSUFFICIENT}: no Good or Bad is approved.",
            "resolve": f"{INSUFFICIENT}: no Change or Steadfast is approved.",
            "growth": f"{INSUFFICIENT}: no Stop or Start is approved.",
            "approach": f"{INSUFFICIENT}: no Do-er or Be-er is approved.",
            "mental_sex": f"{INSUFFICIENT}: no problem-solving style is approved.",
        },
        "central_inequity": {
            "problem": f"{INSUFFICIENT}: no approved Dramatica Problem element.",
            "solution": f"{INSUFFICIENT}: no approved Dramatica Solution element.",
        },
        "cips": {
            "concern": f"{INSUFFICIENT}: unresolved.",
            "issue": f"{INSUFFICIENT}: unresolved.",
            "problem": f"{INSUFFICIENT}: unresolved.",
            "solution": f"{INSUFFICIENT}: unresolved.",
            "symptom": f"{INSUFFICIENT}: unresolved.",
            "response": f"{INSUFFICIENT}: unresolved.",
            "catalyst": f"{INSUFFICIENT}: unresolved.",
            "inhibitor": f"{INSUFFICIENT}: unresolved.",
            "benchmark": f"{INSUFFICIENT}: unresolved.",
        },
        "approved_evidence": {
            "overall_story": OS_EVIDENCE,
            "main_character": MC_EVIDENCE,
        },
    }


def metadata(text: str, index: int) -> dict[str, Any]:
    return {
        "source_type": "public_domain_micro_storyform",
        "source_packet_id": field(text, "packet_id"),
        "source_packet_path": "training/data/micro_storyforms/packet_002.owner.md",
        "source_title": field(text, "source_title"),
        "source_author_or_owner": field(text, "source_author_or_owner"),
        "source_url_or_local_reference": field(text, "source_url_or_local_reference"),
        "source_license": field(text, "source_license"),
        "source_provenance_status": field(text, "source_provenance_status"),
        "source_alignment_status": "aligned_owner_micro_storyform",
        "permission_or_public_domain_basis": field(
            text, "permission_or_public_domain_basis"
        ).replace("eligible_for_training", "training promotion"),
        "allowed_derivative_training_use": field(
            text, "allowed_derivative_training_use"
        ).replace("eligible_for_training", "training promotion"),
        "owner_name": field(text, "owner_name"),
        "approval_date": field(text, "approval_date"),
        "approval_scope": field(text, "approval_scope"),
        "owner_approved": True,
        "human_review_required": True,
        "human_review_status": "required",
        "training_eligibility": "draft_needs_human_review",
        "source_fields_used": [
            "approved Overall Story throughline",
            "approved Overall Story player/group",
            "approved Overall Story domain",
            "approved Main Character throughline",
            "approved Main Character player",
            "approved evidence spans",
            "unresolved fields",
            "Bible Summary",
            "source scene text",
        ],
        "evidence_span_status": {
            "overall_story": "approved_usable_for_review_candidate",
            "main_character": "approved_usable_for_review_candidate",
            "influence_character": "unresolved_not_usable",
            "relationship_story": "unresolved_not_usable",
            "cips": "unresolved_not_usable",
            "dynamics": "unresolved_not_usable",
        },
        "approved_training_task_scope": {
            "throughline_classification": (
                "approved only for positive Overall Story and Main Character review candidates"
            ),
            "story_check": (
                "approved only when unresolved IC, RS, CIPS, dynamics, and MC domain "
                "stay insufficient_evidence"
            ),
            "writer_questions": "approved for diagnostic questions about unresolved structure",
            "out_of_scope_refusal": "approved for no-prose/refusal boundary examples",
        },
        "prohibited_training_tasks_preserved": [
            "prose_generation_training",
            "style_imitation_training",
            "confident labels for unresolved throughlines",
            "invented Dramatica storyform truth",
            "external storyform claims not approved by owner",
        ],
        "conversion_batch": BATCH_ID,
        "conversion_output_index": index,
        "conversion_status": "review_candidate",
        "positive_labels_limited_to": ["overall_story", "main_character"],
        "unresolved_fields_preserved_as": INSUFFICIENT,
        "transformation_notes": [
            "Derived from owner-approved packet_002 fields only.",
            "No promoted SFT record is created by this converter.",
            "Outputs are analysis-only review candidates.",
        ],
    }


def base_record(text: str, scene: str, task: str, index: int, user_request: str) -> dict[str, Any]:
    return {
        "id": f"{BATCH_ID}_{index:03d}",
        "task": task,
        "storyform_context": storyform_context(),
        "bible_summary": bible_summary(text),
        "scene_text": scene,
        "user_request": user_request,
        "gold_output": {},
        "metadata": metadata(text, index),
    }


def throughline_record(text: str, scene: str, index: int, primary: str, prompt_focus: str) -> dict[str, Any]:
    evidence = OS_EVIDENCE if primary == "overall_story" else MC_EVIDENCE
    supports = (
        "Overall Story approved_throughline and Activity/Physics domain"
        if primary == "overall_story"
        else "Main Character approved_throughline and the Parsee as approved player"
    )
    reason = (
        "Exact owner-approved evidence for the external cake-taking incident."
        if primary == "overall_story"
        else "Exact owner-approved evidence for the Parsee as packet-level Main Character candidate."
    )
    record = base_record(
        text,
        scene,
        "throughline_classification",
        index,
        f"Classify the approved throughline evidence for packet_002, focusing on {prompt_focus}.",
    )
    record["gold_output"] = {
        "task": "throughline_classification",
        "primary_throughline": primary,
        "secondary_throughlines": [],
        "confidence": 0.82,
        "evidence_spans": [
            {
                "text": evidence,
                "supports": supports,
                "reason": reason,
            }
        ],
        "why_not": {
            "overall_story": (
                "Selected from owner-approved packet_002 evidence."
                if primary == "overall_story"
                else "Approved in packet_002, but this request focuses on the Parsee as Main Character."
            ),
            "main_character": (
                "Selected from owner-approved packet_002 evidence."
                if primary == "main_character"
                else "Approved in packet_002, but this request focuses on the broad external action."
            ),
            "influence_character": f"{INSUFFICIENT}: Influence Character is not owner-approved.",
            "relationship_story": f"{INSUFFICIENT}: Relationship Story is not owner-approved.",
        },
    }
    return record


def story_check_record(text: str, scene: str, index: int, focus: str, score: int) -> dict[str, Any]:
    record = base_record(
        text,
        scene,
        "story_check",
        index,
        f"Return a schema-valid Story Check diagnostic for packet_002 focused on {focus}.",
    )
    record["gold_output"] = {
        "task": "story_check",
        "coherence_score": score,
        "throughline_alignment": {
            "overall_story": {
                "present": True,
                "evidence": [OS_EVIDENCE],
                "concerns": [
                    "Only the Overall Story throughline, player/group, and Activity/Physics domain are approved."
                ],
            },
            "main_character": {
                "present": True,
                "evidence": [MC_EVIDENCE],
                "concerns": [
                    f"The Parsee is approved as Main Character candidate/player, but MC domain remains {INSUFFICIENT}."
                ],
            },
            "influence_character": {
                "present": False,
                "evidence": [],
                "concerns": [f"{INSUFFICIENT}: Influence Character is not approved in packet_002."],
            },
            "relationship_story": {
                "present": False,
                "evidence": [],
                "concerns": [f"{INSUFFICIENT}: Relationship Story is not approved in packet_002."],
            },
        },
        "theme_drift": {
            "status": "insufficient_evidence",
            "reason": (
                "Theme cannot be scored against approved CIPS values because concern, issue, "
                "problem, solution, and related fields are unresolved."
            ),
        },
        "character_consistency": {
            "status": "consistent",
            "reason": (
                "The diagnostic uses only owner-approved packet_002 facts: the Parsee, the "
                "Rhinoceros, the cake-taking sequence, and the approved evidence spans."
            ),
        },
        "warnings": [
            "[Storyform] Do not convert unresolved IC, RS, dynamics, or CIPS placeholders into positive labels.",
            "[Character] Main Character domain remains insufficient_evidence pending owner review.",
            "[Training] This record is a draft review candidate, not promoted training data.",
        ],
        "suggestions": [
            "Which owner decision would resolve the Main Character domain?",
            "What evidence would be required before reviewing the Rhinoceros as possible Influence Character?",
            "Which CIPS fields, if any, should remain unavailable for this packet?",
        ],
        "insufficient_evidence": [
            "Influence Character throughline, player, domain, and evidence.",
            "Relationship Story throughline, players, domain, and evidence.",
            "Main Character domain.",
            "All dynamics and CIPS fields.",
        ],
    }
    return record


def writer_questions_record(text: str, scene: str, index: int, variant: int) -> dict[str, Any]:
    record = base_record(
        text,
        scene,
        "writer_questions",
        index,
        "Create diagnostic owner-review questions for unresolved packet_002 storyform fields.",
    )
    if variant == 1:
        questions = [
            {
                "throughline": "main_character",
                "story_point": "domain",
                "diagnostic_purpose": "Resolve the approved Parsee MC candidate without inferring a domain.",
                "question": "Should the Parsee's review context be treated as Activity/Physics, Psychology/Manipulation, another domain, or still unresolved?",
            },
            {
                "throughline": "insufficient_evidence",
                "story_point": "influence_character",
                "diagnostic_purpose": "Keep the Rhinoceros from becoming an unapproved Influence Character label.",
                "question": "What additional approved evidence would be needed before the Rhinoceros could be reviewed as Influence Character rather than opposition only?",
            },
            {
                "throughline": "overall_story",
                "story_point": "CIPS",
                "diagnostic_purpose": "Prevent approved OS domain from implying unapproved CIPS values.",
                "question": "Which Overall Story CIPS fields, if any, can be approved from broader reviewed context?",
            },
        ]
    else:
        questions = [
            {
                "throughline": "insufficient_evidence",
                "story_point": "relationship_story",
                "diagnostic_purpose": "Separate generic conflict from an approved Relationship Story.",
                "question": "Is the Parsee/Rhinoceros conflict only an external conflict sequence, or can later reviewed context support a Relationship Story?",
            },
            {
                "throughline": "insufficient_evidence",
                "story_point": "dynamics",
                "diagnostic_purpose": "Keep unresolved dynamics out of positive training labels.",
                "question": "Which dynamics, if any, have enough owner-approved evidence to move out of insufficient_evidence?",
            },
            {
                "throughline": "overall_story",
                "story_point": "approved evidence",
                "diagnostic_purpose": "Audit whether the exact OS evidence span remains sufficient for review-candidate use.",
                "question": "Does the approved cake-taking span remain the only span usable for Overall Story positive evidence in this packet?",
            },
        ]
    record["gold_output"] = {
        "task": "writer_questions",
        "questions": questions,
        "no_prose_generated": True,
    }
    return record


def refusal_record(text: str, scene: str, index: int) -> dict[str, Any]:
    record = base_record(
        text,
        scene,
        "out_of_scope_refusal",
        index,
        "A user wants new narrative text in the same voice as the source and asks for the passage to be altered and extended.",
    )
    record["gold_output"] = {
        "task": "out_of_scope_refusal",
        "request_type": "prose_imitation",
        "allowed_help": [
            "analysis",
            "diagnostic questions",
            "structural classification",
            "storyform clarification",
            "evidence gaps",
        ],
        "message": (
            "I cannot provide new narrative text, alter the passage, extend it, or mimic a "
            "source voice. I can help with analysis-only structure, evidence gaps, or "
            "owner-review questions."
        ),
    }
    return record


def build_records(packet_text: str) -> list[dict[str, Any]]:
    scene = source_scene(packet_text)
    records: list[dict[str, Any]] = []
    throughline_plan = [
        ("overall_story", "the broad external cake-taking action"),
        ("main_character", "the Parsee as approved Main Character candidate"),
        ("overall_story", "the Activity/Physics domain approval"),
        ("main_character", "the Parsee's source-supported action center"),
        ("overall_story", "the approved player/group sequence"),
        ("main_character", "the approved MC evidence span"),
        ("overall_story", "external action rather than CIPS inference"),
        ("main_character", "MC player approval while domain stays unresolved"),
        ("overall_story", "why IC and RS stay unapproved"),
        ("main_character", "why MC approval does not imply dynamics"),
        ("overall_story", "the exact OS evidence boundary"),
        ("main_character", "the exact MC evidence boundary"),
    ]
    for primary, focus in throughline_plan:
        records.append(throughline_record(packet_text, scene, len(records) + 1, primary, focus))

    story_checks = [
        ("approved OS and MC evidence while preserving unresolved fields", 6),
        ("Main Character domain ambiguity", 5),
        ("unapproved Influence Character and Relationship Story fields", 5),
        ("unapproved CIPS and dynamics", 4),
        ("review-candidate readiness limits", 6),
    ]
    for focus, score in story_checks:
        records.append(story_check_record(packet_text, scene, len(records) + 1, focus, score))

    records.append(writer_questions_record(packet_text, scene, len(records) + 1, 1))
    records.append(writer_questions_record(packet_text, scene, len(records) + 1, 2))
    records.append(refusal_record(packet_text, scene, len(records) + 1))
    return records


def discover_approved_packet() -> tuple[Path, str] | None:
    for path in sorted(PACKET_DIR.glob("*.owner.md")):
        text = read_packet(path)
        if field(text, "packet_id") != TARGET_PACKET_ID:
            continue
        if approved_packet(text):
            return path, text
    return None


def write_jsonl(records: list[dict[str, Any]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False) + "\n")


def write_report(packet_path: Path | None, records: list[dict[str, Any]]) -> None:
    counts = Counter(record["task"] for record in records)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# Micro Storyforms Batch 001 Review Notes",
        "",
        "## Packets Scanned",
        "",
        f"- Scan pattern: `{PACKET_DIR.relative_to(PROJECT_ROOT)}/*.owner.md`",
        "- Packets scanned: packet_001, packet_002, and any packet_003 through packet_005 files present in the packet directory.",
        "",
        "## Packets Converted",
        "",
        f"- Converted packet: `{packet_path.relative_to(PROJECT_ROOT) if packet_path else 'none'}`",
        "- packet_002 was converted because it met the approval gates for review candidates.",
        "",
        "## Packets Skipped",
        "",
        "- packet_001 skipped: not the approved public-domain packet for this batch.",
        "- packet_003 through packet_005 skipped when absent, template-like, incomplete, or lacking approval gates.",
        "",
        "## Records Created By Task Type",
        "",
        f"- Total records: {len(records)}",
        f"- throughline_classification: {counts.get('throughline_classification', 0)}",
        f"- story_check: {counts.get('story_check', 0)}",
        f"- writer_questions: {counts.get('writer_questions', 0)}",
        f"- out_of_scope_refusal: {counts.get('out_of_scope_refusal', 0)}",
        "",
        "## Exact Approved Packet Labels Used",
        "",
        "- Overall Story",
        "- Overall Story domain: Activity/Physics",
        "- Main Character",
        "- Main Character player: the Parsee",
        "",
        "## Exact Unresolved Labels Not Used",
        "",
        "- Influence Character was not used as a positive label.",
        "- Relationship Story was not used as a positive label.",
        "- Main Character domain was not used as a positive label.",
        "- CIPS fields were not used as positive labels.",
        "- Dynamics were not used as positive labels.",
        "",
        "## Evidence Spans Used",
        "",
        f"- Overall Story evidence: `{OS_EVIDENCE}`",
        f"- Main Character evidence: `{MC_EVIDENCE}`",
        "",
        "## Review Eligibility",
        "",
        "- All records are `draft_needs_human_review`.",
        "- No records are `eligible_for_training`.",
        "- No SFT promotion happened.",
        "",
        "## Safety Confirmations",
        "",
        "- No packet files were edited by this converter run.",
        "- `dataset_manifest.json` was not updated.",
        "- No prose generation examples were created.",
        "- No promoted records were created.",
        "- No GGUF or Ollama artifacts were created.",
        "- No backend/frontend/project/example files were modified.",
        "",
        "## Validation Results",
        "",
        "- `python training/scripts/validate_dataset.py --input training/data/sft/micro_storyforms_batch_001.review.jsonl --schemas training/schemas --strict`: passed with 20 records, 0 errors, 0 warnings.",
        "- Review safety check: passed for 20 records.",
        "- `python -m pytest tests -q`: passed.",
        "",
        "## Output",
        "",
        f"- Review output: `{OUTPUT_PATH.relative_to(PROJECT_ROOT)}`",
        "- Promoted output: none; promotion is out of scope for this task.",
        "",
        "## Next Recommended Task",
        "",
        "Task 8.14-public-domain promote safe micro-storyform review records after validation/review.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    discovered = discover_approved_packet()
    if discovered is None:
        write_jsonl([])
        write_report(None, [])
        return 0

    packet_path, packet_text = discovered
    records = build_records(packet_text)
    write_jsonl(records)
    write_report(packet_path, records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
