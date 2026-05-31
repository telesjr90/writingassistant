from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_NORMALIZED = REPO_ROOT / "training" / "knowledge" / "dramatica_terms_normalized.jsonl"
DEFAULT_INPUT_RAW = REPO_ROOT / "training" / "knowledge" / "dramatica_terms_raw.jsonl"
DEFAULT_TARGETS_JSON = REPO_ROOT / "training" / "knowledge" / "dramatica_task_b_targets.json"
DEFAULT_CATALOG = Path("/mnt/e/project-test-readiness/docs/analysis-review/12-targeted-dramatica-definition-catalog.md")
DEFAULT_REPORT = REPO_ROOT / "training" / "reports" / "dramatica_terms_normalized_repair_report.md"

REQUIRED_FIELDS = [
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

GENERIC_RISK_TERMS = {
    "Act",
    "Analysis",
    "Approach",
    "Concern",
    "Scene",
    "Sequence",
    "Good",
    "Bad",
    "Change",
    "Start",
    "Stop",
}

HIGH_PRIORITY_TERMS = {
    "Throughline",
    "Overall Story Throughline",
    "Objective Story Throughline",
    "Main Character Throughline",
    "Main Character",
    "Impact Character",
    "Impact Character Throughline",
    "Influence Character",
    "Influence Character Throughline",
    "Obstacle Character",
    "Relationship Story Throughline",
    "Main vs. Impact Story Throughline",
    "Subjective Story Throughline",
    "Class",
    "Domain",
    "Situation",
    "Universe",
    "Activity",
    "Physics",
    "Manipulation",
    "Psychology",
    "Fixed Attitude",
    "Mind",
    "Type",
    "Concern",
    "Issue",
    "Variation",
    "Theme",
    "Problem",
    "Solution",
    "Goal",
    "Storyform",
    "Story Mind",
    "Story Point",
    "Appreciation",
    "Protagonist",
    "Antagonist",
    "Archetypal Characters",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair low-quality normalized Dramatica term notes.")
    parser.add_argument("--input-normalized", type=Path, default=DEFAULT_INPUT_NORMALIZED)
    parser.add_argument("--input-raw", type=Path, default=DEFAULT_INPUT_RAW)
    parser.add_argument("--targets-json", type=Path, default=DEFAULT_TARGETS_JSON)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output-normalized", type=Path, default=DEFAULT_INPUT_NORMALIZED)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = set(REQUIRED_FIELDS) - set(row)
            extra = set(row) - set(REQUIRED_FIELDS)
            if missing or extra:
                raise ValueError(f"{path}:{line_no}: missing={sorted(missing)} extra={sorted(extra)}")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps({field: row[field] for field in REQUIRED_FIELDS}, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def clean_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r"`([^`]+)`", r"\1", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    reader = csv.reader(io.StringIO(stripped), delimiter="|")
    return [clean_cell(cell) for cell in next(reader)]


def load_catalog(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = parse_markdown_row(line)
        if len(cells) < 6 or cells[0] in {"Term", "---"} or cells[0].startswith("---"):
            continue
        term, normalized, aliases, definition, best_source, location = cells[:6]
        if not term or not definition:
            continue
        record = {
            "term": term,
            "normalized": normalized,
            "aliases": aliases,
            "definition": definition,
            "best_source": best_source,
            "location": location,
        }
        keys = {term, normalized}
        for part in re.split(r";|,|/|\\bor\\b|\\balso\\b", aliases):
            part = part.strip()
            if part and not part.lower().startswith("current "):
                keys.add(part)
        if "/" in term:
            keys.update(part.strip() for part in term.split("/") if part.strip())
        for key in keys:
            rows.setdefault(normalize_key(key), record)
    return rows


def catalog_match(row: dict[str, Any], catalog: dict[str, dict[str, str]]) -> dict[str, str] | None:
    candidates = [row["canonical_term"], *row.get("aliases", [])]
    for candidate in candidates:
        match = catalog.get(normalize_key(str(candidate)))
        if match:
            return match
    return None


def true_dictionary_entry(row: dict[str, Any]) -> dict[str, Any] | None:
    term = row["canonical_term"]
    pattern = re.compile("^" + re.escape(term) + r"\s+(?:--|\[)", re.IGNORECASE)
    for source in row.get("sources", []):
        if source.get("source_family") != "primary_dictionary":
            continue
        excerpt = str(source.get("raw_excerpt", "")).strip()
        if pattern.search(excerpt):
            return source
        if f"{term} --" in excerpt or f"{term} [" in excerpt:
            return source
    return None


def compact_catalog_note(term: str, match: dict[str, str]) -> str:
    definition = match["definition"].rstrip(".")
    return f"{term}: {definition}. Reference-only; packet use still requires owner approval and scene evidence."


def compact_dictionary_note(term: str, source: dict[str, Any]) -> str:
    return (
        f"{term}: dictionary-backed Dramatica reference term from "
        f"{source.get('source_relative_path')} at {source.get('source_location')}. "
        "Review the source before packet use; owner approval remains required."
    )


def add_catalog_source(row: dict[str, Any], catalog_path: Path, match: dict[str, str]) -> None:
    source_ref = {
        "record_id": f"catalog::{normalize_key(match['term']).replace(' ', '_')}",
        "source_path": str(catalog_path.resolve()),
        "source_relative_path": str(catalog_path),
        "source_priority_rank": 0,
        "source_family": "analysis_review_doc",
        "source_location": match.get("location") or "targeted catalog row",
        "matched_alias": match["term"],
        "extraction_status": "catalog_repair",
        "raw_excerpt": "",
    }
    existing = {(s.get("source_path"), s.get("record_id")) for s in row.get("sources", []) if isinstance(s, dict)}
    if (source_ref["source_path"], source_ref["record_id"]) not in existing:
        row["sources"].insert(0, source_ref)


def remove_low_quality(row: dict[str, Any]) -> None:
    row["caution_flags"] = [flag for flag in row["caution_flags"] if flag != "source_excerpt_low_quality"]
    row["unresolved_conflicts"] = [
        conflict for conflict in row["unresolved_conflicts"] if conflict != "raw_excerpt_low_quality"
    ]


def ensure_flag(row: dict[str, Any], flag: str) -> None:
    if flag not in row["caution_flags"]:
        row["caution_flags"].append(flag)
        row["caution_flags"].sort()


def repair_rows(rows: list[dict[str, Any]], catalog: dict[str, dict[str, str]], catalog_path: Path) -> dict[str, Any]:
    repaired_catalog: list[str] = []
    repaired_dictionary: list[str] = []
    still_low_quality: list[str] = []
    deferred: list[str] = []

    for row in rows:
        term = row["canonical_term"]
        match = catalog_match(row, catalog)
        if match:
            row["definition_note"] = compact_catalog_note(term, match)
            add_catalog_source(row, catalog_path, match)
            remove_low_quality(row)
            row["notes"] += " Repaired from targeted definition catalog."
            repaired_catalog.append(term)
        else:
            source = true_dictionary_entry(row)
            if source and term not in GENERIC_RISK_TERMS:
                row["definition_note"] = compact_dictionary_note(term, source)
                remove_low_quality(row)
                row["notes"] += " Repaired from clear dictionary-style raw entry."
                repaired_dictionary.append(term)

        low_quality = "source_excerpt_low_quality" in row["caution_flags"]
        if low_quality:
            still_low_quality.append(term)
        if low_quality or (term in GENERIC_RISK_TERMS and not match):
            ensure_flag(row, "defer_from_task_c_indexing")
            deferred.append(term)

        row["may_be_used_as_scene_evidence"] = False
        row["requires_owner_approval_for_packet_use"] = True
        row["review_status"] = "draft_needs_human_review"

    return {
        "repaired_catalog": sorted(set(repaired_catalog)),
        "repaired_dictionary": sorted(set(repaired_dictionary)),
        "still_low_quality": sorted(set(still_low_quality)),
        "deferred": sorted(set(deferred)),
    }


def count_state(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(rows),
        "source_excerpt_low_quality": sum("source_excerpt_low_quality" in row["caution_flags"] for row in rows),
        "unresolved_conflicts": sum(bool(row["unresolved_conflicts"]) for row in rows),
        "defer_from_task_c_indexing": sum("defer_from_task_c_indexing" in row["caution_flags"] for row in rows),
    }


def target_missing_terms(targets_path: Path, rows: list[dict[str, Any]]) -> list[str]:
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    wanted = {
        (family["family_id"], term)
        for family in targets.get("target_families", [])
        for term in family.get("target_terms", [])
    }
    present = {
        (family_id, row["canonical_term"])
        for row in rows
        for family_id in row.get("target_family_ids", [])
    }
    return [f"{family}: {term}" for family, term in sorted(wanted - present)]


def report(
    *,
    input_normalized: Path,
    input_raw: Path,
    targets_json: Path,
    catalog_path: Path,
    before: dict[str, int],
    after: dict[str, int],
    result: dict[str, list[str]],
    rows: list[dict[str, Any]],
    missing: list[str],
) -> str:
    high_present = {row["canonical_term"]: row for row in rows if row["canonical_term"] in HIGH_PRIORITY_TERMS}
    high_usable = [
        term for term, row in sorted(high_present.items())
        if "defer_from_task_c_indexing" not in row["caution_flags"] and "source_excerpt_low_quality" not in row["caution_flags"]
    ]
    high_not = sorted(HIGH_PRIORITY_TERMS - set(high_usable))
    lines = [
        "# Dramatica Normalized Terms Repair Report",
        "",
        "## Purpose",
        "",
        "Repair weak normalized definition notes before Task C retrieval indexing while preserving all packet-safety boundaries.",
        "",
        "## Inputs Read",
        "",
        f"- input_normalized: `{input_normalized}`",
        f"- input_raw: `{input_raw}`",
        f"- targets_json: `{targets_json}`",
        "",
        "## Catalog Path Used",
        "",
        f"- `{catalog_path}`" if catalog_path.exists() else "- catalog missing",
        "",
        "## Terms Reviewed",
        "",
        f"- {after['total']}",
        "",
        "## Terms Repaired From Catalog",
        "",
    ]
    lines.extend(f"- {term}" for term in result["repaired_catalog"]) if result["repaired_catalog"] else lines.append("- none")
    lines.extend(["", "## Terms Repaired From Dictionary Entry", ""])
    lines.extend(f"- {term}" for term in result["repaired_dictionary"]) if result["repaired_dictionary"] else lines.append("- none")
    lines.extend(["", "## Terms Still Low Quality", ""])
    lines.extend(f"- {term}" for term in result["still_low_quality"]) if result["still_low_quality"] else lines.append("- none")
    lines.extend(["", "## Terms Marked defer_from_task_c_indexing", ""])
    lines.extend(f"- {term}" for term in result["deferred"]) if result["deferred"] else lines.append("- none")
    lines.extend(["", "## Remaining Missing/Unresolved Target Terms", ""])
    lines.extend(f"- {item}" for item in missing) if missing else lines.append("- none")
    lines.extend(
        [
            "",
            "## Counts Before/After",
            "",
            "| Metric | Before | After |",
            "| --- | ---: | ---: |",
            f"| total normalized terms | {before['total']} | {after['total']} |",
            f"| source_excerpt_low_quality count | {before['source_excerpt_low_quality']} | {after['source_excerpt_low_quality']} |",
            f"| unresolved_conflicts count | {before['unresolved_conflicts']} | {after['unresolved_conflicts']} |",
            f"| defer_from_task_c_indexing count | {before['defer_from_task_c_indexing']} | {after['defer_from_task_c_indexing']} |",
            "",
            "## High-Priority Packet Terms Now Usable For Task C",
            "",
        ]
    )
    lines.extend(f"- {term}" for term in high_usable) if high_usable else lines.append("- none")
    lines.extend(["", "## High-Priority Packet Terms Still Not Usable For Task C", ""])
    lines.extend(f"- {term}" for term in high_not) if high_not else lines.append("- none")
    lines.extend(
        [
            "",
            "## Confirmations",
            "",
            "- No packet files were edited.",
            "- No SFT records were created.",
            "- No backend/frontend/example files were modified.",
            "- No retrieval index was built.",
            "- All terms remain definition/reference only.",
            "- No term may be used as scene evidence.",
            "- Owner approval remains required for packet use.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_normalized = resolve_repo_path(args.input_normalized)
    input_raw = resolve_repo_path(args.input_raw)
    targets_json = resolve_repo_path(args.targets_json)
    output_normalized = resolve_repo_path(args.output_normalized)
    report_path = resolve_repo_path(args.report)
    catalog_path = args.catalog

    rows = read_jsonl(input_normalized)
    before = count_state(rows)
    catalog = load_catalog(catalog_path)
    result = repair_rows(rows, catalog, catalog_path)
    after = count_state(rows)
    missing = target_missing_terms(targets_json, rows)
    write_jsonl(output_normalized, rows)
    write_text(
        report_path,
        report(
            input_normalized=input_normalized,
            input_raw=input_raw,
            targets_json=targets_json,
            catalog_path=catalog_path,
            before=before,
            after=after,
            result=result,
            rows=rows,
            missing=missing,
        ),
    )
    print(f"terms reviewed: {after['total']}")
    print(f"repaired from catalog: {len(result['repaired_catalog'])}")
    print(f"repaired from dictionary: {len(result['repaired_dictionary'])}")
    print(f"still low quality: {after['source_excerpt_low_quality']}")
    print(f"deferred from Task C: {after['defer_from_task_c_indexing']}")
    print(f"Wrote {output_normalized}")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
