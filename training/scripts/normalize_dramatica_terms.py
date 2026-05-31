from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGETS_JSON = REPO_ROOT / "training" / "knowledge" / "dramatica_task_b_targets.json"
DEFAULT_INPUT_RAW = REPO_ROOT / "training" / "knowledge" / "dramatica_terms_raw.jsonl"
DEFAULT_RAW_SUMMARY = REPO_ROOT / "training" / "reports" / "dramatica_terms_raw_extraction_summary.md"
DEFAULT_OUTPUT_NORMALIZED = REPO_ROOT / "training" / "knowledge" / "dramatica_terms_normalized.jsonl"
DEFAULT_REPORT = REPO_ROOT / "training" / "reports" / "dramatica_term_extraction_report.md"
BLOCKED_MISSING_RAW = REPO_ROOT / "training" / "reports" / "BLOCKED_dramatica_task_b3_missing_raw_terms.md"
BLOCKED_INVALID_RAW = REPO_ROOT / "training" / "reports" / "BLOCKED_dramatica_task_b3_invalid_raw_terms.md"

RAW_REQUIRED = {
    "record_id",
    "target_family_id",
    "target_term",
    "matched_alias",
    "source_path",
    "source_relative_path",
    "source_priority_rank",
    "source_family",
    "source_location",
    "raw_excerpt",
    "extraction_status",
    "notes",
    "safety_flags",
}

NORM_FIELDS = [
    "term_id",
    "canonical_term",
    "aliases",
    "target_family_ids",
    "definition_note",
    "recommended_primary_source",
    "sources",
    "source_priority_summary",
    "packet_fields_supported",
    "caution_flags",
    "may_be_used_as_scene_evidence",
    "requires_owner_approval_for_packet_use",
    "review_status",
    "unresolved_conflicts",
    "owner_review_questions",
    "notes",
]

KNOWN_ALIAS_GROUPS = [
    {"Overall Story Throughline", "Objective Story Throughline"},
    {"Impact Character", "Influence Character", "Obstacle Character"},
    {"Impact Character Throughline", "Influence Character Throughline"},
    {"Relationship Story", "Relationship Story Throughline", "Main vs. Impact Story Throughline", "Main vs. Impact Character's Throughline", "Subjective Story Throughline", "relationship throughline"},
    {"Situation", "Universe"},
    {"Activity", "Physics"},
    {"Manipulation", "Psychology"},
    {"Fixed Attitude", "Mind"},
    {"Story Point", "Appreciation"},
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize B2 raw Dramatica term records.")
    parser.add_argument("--targets-json", type=Path, default=DEFAULT_TARGETS_JSON)
    parser.add_argument("--input-raw", type=Path, default=DEFAULT_INPUT_RAW)
    parser.add_argument("--raw-summary", type=Path, default=DEFAULT_RAW_SUMMARY)
    parser.add_argument("--output-normalized", type=Path, default=DEFAULT_OUTPUT_NORMALIZED)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--repair", action="store_true")
    return parser.parse_args(argv)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_blocked(path: Path, title: str, lines: list[str]) -> None:
    write_text(path, "\n".join([f"# {title}", "", *lines]))


def read_raw_jsonl(path: Path, repair: bool) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    repairs: list[str] = []
    seen_ids: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: JSONDecodeError: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"line {line_no}: row is not an object")
            continue
        missing = RAW_REQUIRED - set(row)
        extra = set(row) - RAW_REQUIRED
        if extra and repair:
            row = {key: row[key] for key in row if key in RAW_REQUIRED}
            repairs.append(f"line {line_no}: removed extra fields {sorted(extra)}")
            extra = set()
        if missing or extra:
            errors.append(f"line {line_no}: missing={sorted(missing)} extra={sorted(extra)}")
            continue
        if not isinstance(row.get("safety_flags"), list):
            if repair:
                row["safety_flags"] = []
                repairs.append(f"line {line_no}: repaired safety_flags to empty list")
            else:
                errors.append(f"line {line_no}: safety_flags is not a list")
                continue
        record_id = str(row.get("record_id") or "")
        if not record_id:
            errors.append(f"line {line_no}: record_id missing")
            continue
        if record_id in seen_ids:
            errors.append(f"line {line_no}: duplicate record_id {record_id}")
            continue
        seen_ids.add(record_id)
        if str(row.get("source_relative_path", "")).startswith("recu33/"):
            errors.append(f"line {line_no}: recu33 archival duplicate not allowed")
            continue
        if str(row.get("source_relative_path", "")).endswith(("data.json", "schema.json")):
            if row.get("extraction_status") not in {"skipped_deprioritized_source", "not_found"}:
                errors.append(f"line {line_no}: data.json/schema.json cannot be definition authority")
                continue
        rows.append(row)
    return rows, errors, repairs


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def stable_term_id(canonical_term: str) -> str:
    digest = hashlib.sha1(canonical_term.lower().encode("utf-8")).hexdigest()[:10]
    return f"dram_term_{slug(canonical_term)[:50]}_{digest}"


def target_metadata(targets: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    families: dict[str, dict[str, Any]] = {}
    term_aliases: dict[str, set[str]] = defaultdict(set)
    term_families: dict[str, set[str]] = defaultdict(set)
    term_packet_fields: dict[str, set[str]] = defaultdict(set)
    for family in targets.get("target_families", []):
        if not isinstance(family, dict):
            continue
        family_id = str(family.get("family_id") or "")
        if not family_id:
            continue
        families[family_id] = family
        fields = [item for item in family.get("packet_fields_supported", []) if isinstance(item, str)]
        alias_map = family.get("aliases") if isinstance(family.get("aliases"), dict) else {}
        for term in family.get("target_terms", []):
            if not isinstance(term, str):
                continue
            term_families[term].add(family_id)
            term_aliases[term].add(term)
            term_packet_fields[term].update(fields)
            aliases = alias_map.get(term) if isinstance(alias_map, dict) else None
            if isinstance(aliases, list):
                term_aliases[term].update(alias for alias in aliases if isinstance(alias, str))
    for group in KNOWN_ALIAS_GROUPS:
        for term in list(term_aliases):
            if term in group:
                term_aliases[term].update(group)
    return families, term_aliases, term_families, term_packet_fields


def is_low_quality_excerpt(text: str) -> bool:
    if not text.strip():
        return True
    noisy_patterns = [
        r"\.{3,}",
        r"\b[a-zA-Z]+-\s+[a-zA-Z]+",
        r"[|_]{2,}",
        r"THroughline",
        r"\b\w\s+\w\s+\w\b",
    ]
    if any(re.search(pattern, text) for pattern in noisy_patterns):
        return True
    words = text.split()
    if len(words) < 4:
        return True
    punctuation_ratio = sum(1 for char in text if not char.isalnum() and not char.isspace()) / max(len(text), 1)
    return punctuation_ratio > 0.22


def raw_source_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": row["record_id"],
        "source_path": row["source_path"],
        "source_relative_path": row["source_relative_path"],
        "source_priority_rank": row["source_priority_rank"],
        "source_family": row["source_family"],
        "source_location": row["source_location"],
        "matched_alias": row["matched_alias"],
        "extraction_status": row["extraction_status"],
        "raw_excerpt": row["raw_excerpt"],
    }


def source_priority_summary(best: dict[str, Any], sources: list[dict[str, Any]]) -> str:
    families = {source["source_family"] for source in sources}
    if best["source_family"] == "primary_dictionary":
        if families - {"primary_dictionary"}:
            return "dictionary-backed with supporting sources"
        return "dictionary-backed"
    if best["source_family"] == "theory_book":
        return "theory-backed"
    if best["source_family"] in {"structural_corroboration", "original_table_or_chart"}:
        return "structurally corroborated"
    if best["source_family"] == "secondary_explanation":
        return "secondary-only"
    return "unresolved"


def conservative_definition_note(term: str, best: dict[str, Any], low_quality: bool) -> str:
    if low_quality:
        return f"Raw source match for `{term}` needs human review before any definition note is trusted."
    return (
        f"Reference-only raw source match for `{term}` from {best['source_relative_path']} "
        f"at {best['source_location']}; normalize and review before packet use."
    )


def owner_questions(term: str, aliases: set[str], family_ids: set[str]) -> list[str]:
    text = " ".join([term, *aliases, *family_ids]).lower()
    questions: list[str] = []
    if "main character" in text or "protagonist" in text:
        questions.append("Has the owner approved whether this player is Main Character, Protagonist, both, or neither?")
    if any(token in text for token in ("impact character", "influence character", "obstacle character", "antagonist")):
        questions.append("Has the owner distinguished Influence/Impact Character pressure from antagonist opposition?")
    if "relationship" in text or "subjective story" in text:
        questions.append("Has the owner approved a Relationship Story label rather than a generic relationship fact?")
    if any(token in text for token in ("theme", "issue", "variation")):
        questions.append("Has the owner mapped this theme language to a Dramatica Issue or Variation?")
    if "belief" in text or "fixed attitude" in text or term == "Mind":
        questions.append("Has the owner approved any Mind/Fixed Attitude domain claim rather than a generic belief-system note?")
    if term == "Analysis":
        questions.append("Is this the Dramatica Analysis variation, not the product's generic analysis feature?")
    if "overall story" in text or "main character throughline" in text:
        questions.append("Has the owner confirmed whether evidence belongs to Overall Story or Main Character perspective?")
    return list(dict.fromkeys(questions))


def unresolved_conflicts(term: str, aliases: set[str], best: dict[str, Any], sources: list[dict[str, Any]], low_quality: bool) -> list[str]:
    conflicts: list[str] = []
    if len(aliases) > 1:
        conflicts.append("naming_aliases_require_review")
    if best["source_family"] == "secondary_explanation" or all(source["source_family"] == "secondary_explanation" for source in sources):
        conflicts.append("found_only_or_best_in_secondary_source")
    if low_quality:
        conflicts.append("raw_excerpt_low_quality")
    if "see" in best.get("raw_excerpt", "").lower() and "reference" in best.get("raw_excerpt", "").lower():
        conflicts.append("possible_see_reference_only")
    return list(dict.fromkeys(conflicts))


def normalize_records(targets: dict[str, Any], raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families, term_aliases, term_families, term_packet_fields = target_metadata(targets)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in raw_rows:
        grouped[str(row["target_term"])].append(row)

    normalized: list[dict[str, Any]] = []
    for term in sorted(grouped):
        rows = sorted(grouped[term], key=lambda row: (int(row["source_priority_rank"]), row["source_relative_path"], row["source_location"]))
        best = rows[0]
        aliases = set(term_aliases.get(term, {term}))
        aliases.update(str(row["matched_alias"]) for row in rows if row.get("matched_alias"))
        family_ids = set(term_families.get(term, set()))
        family_ids.update(str(row["target_family_id"]) for row in rows)
        packet_fields = set(term_packet_fields.get(term, set()))
        for family_id in family_ids:
            family = families.get(family_id, {})
            packet_fields.update(item for item in family.get("packet_fields_supported", []) if isinstance(item, str))
        caution_flags = {
            "definition_only_not_scene_evidence",
            "requires_owner_approval",
            "do_not_use_data_json_or_schema_json_as_definition_authority",
            "ignore_recu33_archival_duplicates_unless_canonical_missing",
        }
        for row in rows:
            caution_flags.update(flag for flag in row.get("safety_flags", []) if isinstance(flag, str))
        low_quality = any(is_low_quality_excerpt(str(row.get("raw_excerpt", ""))) for row in rows)
        if low_quality:
            caution_flags.add("source_excerpt_low_quality")
        if all(row["source_family"] == "secondary_explanation" for row in rows):
            caution_flags.add("secondary_only")
        if "see" in best.get("raw_excerpt", "").lower() and "reference" in best.get("raw_excerpt", "").lower():
            caution_flags.add("see_reference_only")
        sources = [raw_source_ref(row) for row in rows]
        recommended = {
            "source_path": best["source_path"],
            "source_relative_path": best["source_relative_path"],
            "source_priority_rank": best["source_priority_rank"],
            "source_family": best["source_family"],
            "source_location": best["source_location"],
        }
        conflicts = unresolved_conflicts(term, aliases, best, sources, low_quality)
        notes = "Normalized from B2 raw records only. Definition/reference candidate; not scene evidence or packet approval."
        if low_quality:
            notes += " One or more raw excerpts are fragmented or OCR-like and need human review."
        record = {
            "term_id": stable_term_id(term),
            "canonical_term": term,
            "aliases": sorted(aliases),
            "target_family_ids": sorted(family_ids),
            "definition_note": conservative_definition_note(term, best, low_quality),
            "recommended_primary_source": recommended,
            "sources": sources,
            "source_priority_summary": source_priority_summary(best, sources),
            "packet_fields_supported": sorted(packet_fields),
            "caution_flags": sorted(caution_flags),
            "may_be_used_as_scene_evidence": False,
            "requires_owner_approval_for_packet_use": True,
            "review_status": "draft_needs_human_review",
            "unresolved_conflicts": conflicts,
            "owner_review_questions": owner_questions(term, aliases, family_ids),
            "notes": notes,
        }
        normalized.append({field: record[field] for field in NORM_FIELDS})
    return normalized


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def raw_summary_sections(raw_summary: str) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    missing: list[str] = []
    current = None
    for line in raw_summary.splitlines():
        if line.startswith("## Target Terms Not Found"):
            current = "missing"
            continue
        if line.startswith("## JSON Parsing Errors Or Warnings"):
            current = "warnings"
            continue
        if line.startswith("## ") and current:
            current = None
        if current == "missing" and line.startswith("- "):
            missing.append(line[2:])
        if current == "warnings" and line.startswith("- "):
            warnings.append(line[2:])
    return missing, warnings


def make_report(
    *,
    targets_path: Path,
    raw_path: Path,
    raw_summary_path: Path,
    normalized_path: Path,
    raw_rows: list[dict[str, Any]],
    normalized: list[dict[str, Any]],
    raw_summary: str,
    repairs: list[str],
) -> str:
    missing_terms, warnings = raw_summary_sections(raw_summary)
    by_raw_source = Counter(row["source_relative_path"] for row in raw_rows)
    by_raw_family = Counter(row["target_family_id"] for row in raw_rows)
    by_norm_family = Counter(fid for row in normalized for fid in row["target_family_ids"])
    by_primary_family = Counter(row["recommended_primary_source"]["source_family"] for row in normalized)
    caution_counts = Counter(flag for row in normalized for flag in row["caution_flags"])
    unresolved = [row for row in normalized if row["unresolved_conflicts"]]
    high_value = [
        row["canonical_term"]
        for row in normalized
        if row["recommended_primary_source"]["source_family"] in {"primary_dictionary", "theory_book"}
    ][:40]
    packet_terms = [
        row["canonical_term"]
        for row in normalized
        if row["packet_fields_supported"]
    ][:60]
    caution_only = [
        row["canonical_term"]
        for row in normalized
        if not row["packet_fields_supported"] or "source_excerpt_low_quality" in row["caution_flags"]
    ][:60]
    defer = [
        row["canonical_term"]
        for row in normalized
        if row["source_priority_summary"] == "secondary-only" or "source_excerpt_low_quality" in row["caution_flags"]
    ][:60]

    lines = [
        "# Dramatica Term Extraction Report",
        "",
        "## Purpose",
        "",
        "Normalize B2 raw Dramatica term extraction records into a compact review-draft catalog for later retrieval/indexing. All records remain definition/reference only.",
        "",
        "## Inputs Read",
        "",
        f"- targets_json: `{targets_path}`",
        f"- input_raw: `{raw_path}`",
        f"- raw_summary: `{raw_summary_path}`",
        f"- output_normalized: `{normalized_path}`",
        "",
        "## B1/B2/B3 Pipeline Summary",
        "",
        "- B1 created target families, canonical source priority, caution flags, and planned schemas.",
        "- B2 extracted bounded raw source matches from canonical Dramatica JSON files only.",
        "- B3 validated raw JSONL and normalized raw matches by canonical target term.",
        "",
        "## Source Priority Used",
        "",
        "Primary dictionary records are preferred, followed by theory book, structural corroboration, original tables/charts, and secondary explanation.",
        "",
        "## Target Term Families Used",
        "",
    ]
    for family, count in sorted(by_norm_family.items()):
        lines.append(f"- `{family}`: {count}")
    lines.extend(["", "## Raw Extraction Summary", ""])
    lines.append(f"- raw_records_read: {len(raw_rows)}")
    lines.append("")
    lines.append("Raw records by source file:")
    for source, count in sorted(by_raw_source.items()):
        lines.append(f"- `{source}`: {count}")
    lines.append("")
    lines.append("Raw records by target family:")
    for family, count in sorted(by_raw_family.items()):
        lines.append(f"- `{family}`: {count}")
    lines.append("")
    lines.append("B2 missing terms:")
    lines.extend(f"- {item}" for item in missing_terms) if missing_terms else lines.append("- none")
    lines.append("")
    lines.append("B2 warnings:")
    lines.extend(f"- {item}" for item in warnings) if warnings else lines.append("- none")
    lines.extend(["", "## Normalization Summary", ""])
    lines.append(f"- normalized_terms_produced: {len(normalized)}")
    lines.append("")
    lines.append("Normalized terms by target family:")
    for family, count in sorted(by_norm_family.items()):
        lines.append(f"- `{family}`: {count}")
    lines.append("")
    lines.append("Normalized terms by recommended primary source family:")
    for family, count in sorted(by_primary_family.items()):
        lines.append(f"- `{family}`: {count}")
    lines.append("")
    lines.append("Terms with caution flags:")
    for flag, count in sorted(caution_counts.items()):
        lines.append(f"- `{flag}`: {count}")
    lines.append("")
    lines.append(f"Terms with unresolved conflicts: {len(unresolved)}")
    lines.extend(["", "## High-Value Terms Successfully Normalized", ""])
    lines.extend(f"- {term}" for term in high_value) if high_value else lines.append("- none")
    lines.extend(["", "## Target Terms Not Found Or Unresolved", ""])
    lines.extend(f"- {item}" for item in missing_terms) if missing_terms else lines.append("- none")
    if unresolved:
        lines.append("")
        lines.append("Unresolved normalized terms:")
        for row in unresolved[:80]:
            lines.append(f"- {row['canonical_term']}: {', '.join(row['unresolved_conflicts'])}")
    lines.extend(["", "## Source Conflicts Or Alias/Naming Issues", ""])
    lines.append("- Objective Story / Overall Story aliases require review.")
    lines.append("- Impact / Influence / Obstacle Character aliases require review.")
    lines.append("- Subjective Story / Relationship Story / Main vs. Impact terminology requires review.")
    lines.append("- Generic product labels such as theme, goal, relationship, character, act, and scene must not be upgraded to Dramatica story points.")
    lines.extend(["", "## Terms Useful For Packet Filling", ""])
    lines.extend(f"- {term}" for term in packet_terms) if packet_terms else lines.append("- none")
    lines.extend(["", "## Terms Useful Only As Warnings/Cautions", ""])
    lines.extend(f"- {term}" for term in caution_only) if caution_only else lines.append("- none")
    lines.extend(["", "## Terms To Defer From Task C Indexing", ""])
    lines.extend(f"- {term}" for term in defer) if defer else lines.append("- none")
    lines.extend(
        [
            "",
            "## Recommendations For Task C Retrieval Index",
            "",
            "- Index normalized records only after human review of low-quality excerpts and unresolved aliases.",
            "- Keep source citations and caution flags in every retrieval chunk.",
            "- Exclude any record marked `source_excerpt_low_quality` from high-confidence retrieval until reviewed.",
            "- Do not index raw excerpts as scene evidence.",
            "- Keep `data.json`, `schema.json`, and `recu33/...` duplicates out of the retrieval authority set.",
            "",
            "## Repair Notes",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in repairs) if repairs else lines.append("- none")
    lines.extend(
        [
            "",
            "## Confirmations",
            "",
            "- No packet files were edited.",
            "- No SFT records were created.",
            "- No backend/frontend files were modified.",
            "- No example project files were modified.",
            "- All extracted terms are definition/reference only.",
            "- No extracted term may be used as scene evidence.",
            "- Owner approval remains required for packet use.",
            "",
            "## Next Recommended Task",
            "",
            "Task C: build retrieval chunks/index from normalized terms after reviewing caution-heavy records.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    targets_path = resolve_repo_path(args.targets_json)
    raw_path = resolve_repo_path(args.input_raw)
    raw_summary_path = resolve_repo_path(args.raw_summary)
    normalized_path = resolve_repo_path(args.output_normalized)
    report_path = resolve_repo_path(args.report)

    if not raw_path.exists():
        write_blocked(
            BLOCKED_MISSING_RAW,
            "BLOCKED: Dramatica Task B3 Missing Raw Terms",
            [f"- expected_raw_jsonl: `{raw_path}`", "", "Run B2 before B3. No normalized files were created."],
        )
        print(f"Missing raw JSONL: {raw_path}")
        return 2

    raw_rows, errors, repairs = read_raw_jsonl(raw_path, args.repair)
    if errors:
        write_blocked(
            BLOCKED_INVALID_RAW,
            "BLOCKED: Dramatica Task B3 Invalid Raw Terms",
            ["Raw JSONL validation failed:", "", *[f"- {error}" for error in errors[:80]]],
        )
        print(f"Invalid raw JSONL: {len(errors)} error(s)")
        return 1

    targets = load_json(targets_path)
    normalized = normalize_records(targets, raw_rows)
    raw_summary = raw_summary_path.read_text(encoding="utf-8") if raw_summary_path.exists() else ""
    write_jsonl(normalized_path, normalized)
    write_text(
        report_path,
        make_report(
            targets_path=targets_path,
            raw_path=raw_path,
            raw_summary_path=raw_summary_path,
            normalized_path=normalized_path,
            raw_rows=raw_rows,
            normalized=normalized,
            raw_summary=raw_summary,
            repairs=repairs,
        ),
    )
    BLOCKED_MISSING_RAW.unlink(missing_ok=True)
    BLOCKED_INVALID_RAW.unlink(missing_ok=True)
    print(f"Raw rows read: {len(raw_rows)}")
    print(f"Normalized terms: {len(normalized)}")
    print(f"Wrote {normalized_path}")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
