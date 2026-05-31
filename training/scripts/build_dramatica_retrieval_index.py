from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "training" / "knowledge" / "dramatica_terms_normalized.jsonl"
DEFAULT_CHUNKS = REPO_ROOT / "training" / "knowledge" / "dramatica_retrieval_chunks.jsonl"
DEFAULT_SQLITE = REPO_ROOT / "training" / "knowledge" / "dramatica_retrieval_index.sqlite"
DEFAULT_REPORT = REPO_ROOT / "training" / "reports" / "dramatica_retrieval_index_report.md"
BLOCKED_MISSING = REPO_ROOT / "training" / "reports" / "BLOCKED_dramatica_retrieval_index_missing_normalized_terms.md"
BLOCKED_EMPTY = REPO_ROOT / "training" / "reports" / "BLOCKED_dramatica_retrieval_index_no_safe_terms.md"

REQUIRED_NORM = {
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
}

CHUNK_FIELDS = [
    "chunk_id",
    "canonical_term",
    "aliases",
    "target_family_ids",
    "chunk_type",
    "retrieval_text",
    "definition_note",
    "packet_fields_supported",
    "caution_flags",
    "owner_review_questions",
    "recommended_primary_source",
    "sources",
    "safe_for_packet_reference",
    "may_be_used_as_scene_evidence",
    "requires_owner_approval_for_packet_use",
    "review_status",
    "notes",
]

BASE_FLAGS = {
    "definition_only_not_scene_evidence",
    "requires_owner_approval",
    "do_not_use_data_json_or_schema_json_as_definition_authority",
    "ignore_recu33_archival_duplicates_unless_canonical_missing",
}

HIGH_PRIORITY = {
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
    parser = argparse.ArgumentParser(description="Build a safe SQLite/JSONL retrieval layer for Dramatica terms.")
    parser.add_argument("--input-normalized", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--output-sqlite", type=Path, default=DEFAULT_SQLITE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_normalized(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = REQUIRED_NORM - set(row)
            extra = set(row) - REQUIRED_NORM
            if missing or extra:
                raise ValueError(f"{path}:{line_no}: missing={sorted(missing)} extra={sorted(extra)}")
            rows.append(row)
    return rows


def filter_terms(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    safe: list[dict[str, Any]] = []
    skipped: dict[str, list[str]] = {
        "deferred": [],
        "low_quality": [],
        "safety_mismatch": [],
    }
    for row in rows:
        term = row["canonical_term"]
        flags = row.get("caution_flags", [])
        blocked = False
        if "defer_from_task_c_indexing" in flags:
            skipped["deferred"].append(term)
            blocked = True
        if "source_excerpt_low_quality" in flags:
            skipped["low_quality"].append(term)
        if (
            row.get("may_be_used_as_scene_evidence") is not False
            or row.get("requires_owner_approval_for_packet_use") is not True
            or row.get("review_status") != "draft_needs_human_review"
        ):
            skipped["safety_mismatch"].append(term)
            blocked = True
        if blocked or "source_excerpt_low_quality" in flags:
            continue
        safe.append(row)
    return safe, skipped


def source_summary(row: dict[str, Any]) -> str:
    primary = row.get("recommended_primary_source", {})
    return f"{primary.get('source_family')} at {primary.get('source_relative_path')} {primary.get('source_location')}"


def compact_list(label: str, values: list[str]) -> str:
    return f"{label}: {', '.join(values)}" if values else f"{label}: none"


def retrieval_text(row: dict[str, Any], chunk_type: str) -> str:
    parts = [
        f"Term: {row['canonical_term']}",
        compact_list("Aliases", row["aliases"]),
        compact_list("Families", row["target_family_ids"]),
        f"Definition: {row['definition_note']}",
        compact_list("Packet fields", row["packet_fields_supported"]),
        compact_list("Cautions", row["caution_flags"]),
        compact_list("Owner review questions", row["owner_review_questions"]),
        f"Source priority: {row['source_priority_summary']}; {source_summary(row)}",
        "Safety: definition/reference only; not scene evidence; owner approval required for packet labels.",
    ]
    if chunk_type == "aliases":
        parts.insert(3, "Alias guidance: use naming variants for lookup only; aliases do not approve packet labels.")
    elif chunk_type == "packet_field_guidance":
        parts.insert(3, "Packet guidance: these fields can be explained by the term, but values remain owner-approved only.")
    elif chunk_type == "cautions":
        parts.insert(3, "Caution guidance: avoid conflating product labels, generic scene facts, or app feature presence with storyform proof.")
    elif chunk_type == "owner_review_questions":
        parts.insert(3, "Owner review guidance: ask these questions before using the term in packet work.")
    return " ".join(parts)


def chunk_id(term_id: str, chunk_type: str) -> str:
    return f"{term_id}__{chunk_type}"


def make_chunk(row: dict[str, Any], chunk_type: str) -> dict[str, Any]:
    chunk = {
        "chunk_id": chunk_id(row["term_id"], chunk_type),
        "canonical_term": row["canonical_term"],
        "aliases": row["aliases"],
        "target_family_ids": row["target_family_ids"],
        "chunk_type": chunk_type,
        "retrieval_text": retrieval_text(row, chunk_type),
        "definition_note": row["definition_note"],
        "packet_fields_supported": row["packet_fields_supported"],
        "caution_flags": row["caution_flags"],
        "owner_review_questions": row["owner_review_questions"],
        "recommended_primary_source": row["recommended_primary_source"],
        "sources": row["sources"],
        "safe_for_packet_reference": True,
        "may_be_used_as_scene_evidence": False,
        "requires_owner_approval_for_packet_use": True,
        "review_status": "draft_needs_human_review",
        "notes": "Retrieval chunk for definition/reference use only. Not packet approval or scene evidence.",
    }
    return {field: chunk[field] for field in CHUNK_FIELDS}


def make_chunks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for row in rows:
        chunks.append(make_chunk(row, "definition"))
        if len(row["aliases"]) > 1:
            chunks.append(make_chunk(row, "aliases"))
        if row["packet_fields_supported"]:
            chunks.append(make_chunk(row, "packet_field_guidance"))
        meaningful = [flag for flag in row["caution_flags"] if flag not in BASE_FLAGS]
        if meaningful:
            chunks.append(make_chunk(row, "cautions"))
        if row["owner_review_questions"]:
            chunks.append(make_chunk(row, "owner_review_questions"))
    return chunks


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build_sqlite(path: Path, chunks: list[dict[str, Any]], metadata: dict[str, str]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                canonical_term TEXT,
                aliases_json TEXT,
                target_family_ids_json TEXT,
                chunk_type TEXT,
                retrieval_text TEXT,
                definition_note TEXT,
                packet_fields_supported_json TEXT,
                caution_flags_json TEXT,
                owner_review_questions_json TEXT,
                recommended_primary_source_json TEXT,
                sources_json TEXT,
                safe_for_packet_reference INTEGER,
                may_be_used_as_scene_evidence INTEGER,
                requires_owner_approval_for_packet_use INTEGER,
                review_status TEXT,
                notes TEXT
            )
            """
        )
        conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
        for chunk in chunks:
            conn.execute(
                """
                INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk["chunk_id"],
                    chunk["canonical_term"],
                    json.dumps(chunk["aliases"], ensure_ascii=False),
                    json.dumps(chunk["target_family_ids"], ensure_ascii=False),
                    chunk["chunk_type"],
                    chunk["retrieval_text"],
                    chunk["definition_note"],
                    json.dumps(chunk["packet_fields_supported"], ensure_ascii=False),
                    json.dumps(chunk["caution_flags"], ensure_ascii=False),
                    json.dumps(chunk["owner_review_questions"], ensure_ascii=False),
                    json.dumps(chunk["recommended_primary_source"], ensure_ascii=False),
                    json.dumps(chunk["sources"], ensure_ascii=False),
                    int(chunk["safe_for_packet_reference"]),
                    int(chunk["may_be_used_as_scene_evidence"]),
                    int(chunk["requires_owner_approval_for_packet_use"]),
                    chunk["review_status"],
                    chunk["notes"],
                ),
            )
        fts_enabled = True
        try:
            conn.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(chunk_id, canonical_term, retrieval_text)")
            conn.executemany(
                "INSERT INTO chunks_fts (chunk_id, canonical_term, retrieval_text) VALUES (?, ?, ?)",
                [(c["chunk_id"], c["canonical_term"], c["retrieval_text"]) for c in chunks],
            )
        except sqlite3.OperationalError:
            fts_enabled = False
            conn.execute("CREATE TABLE chunks_fts (chunk_id TEXT, canonical_term TEXT, retrieval_text TEXT)")
            conn.executemany(
                "INSERT INTO chunks_fts VALUES (?, ?, ?)",
                [(c["chunk_id"], c["canonical_term"], c["retrieval_text"]) for c in chunks],
            )
        metadata = dict(metadata)
        metadata["sqlite_fts_enabled"] = str(fts_enabled).lower()
        for key, value in metadata.items():
            conn.execute("INSERT INTO metadata VALUES (?, ?)", (key, str(value)))
        conn.commit()
        return fts_enabled
    finally:
        conn.close()


def run_sample_query(sqlite_path: Path, query: str, top_k: int = 3) -> list[str]:
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "training" / "scripts" / "query_dramatica_knowledge.py"),
            "--index",
            str(sqlite_path),
            "--query",
            query,
            "--top-k",
            str(top_k),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"query failed: {result.stderr.strip() or result.stdout.strip()}"]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ["query returned non-json output"]
    return [item["canonical_term"] for item in payload.get("results", [])]


def make_report(
    *,
    input_path: Path,
    chunks_path: Path,
    sqlite_path: Path,
    rows: list[dict[str, Any]],
    safe_rows: list[dict[str, Any]],
    skipped: dict[str, list[str]],
    chunks: list[dict[str, Any]],
    fts_enabled: bool,
    sample_results: dict[str, list[str]],
) -> str:
    by_type = Counter(chunk["chunk_type"] for chunk in chunks)
    by_family = Counter(fid for chunk in chunks for fid in chunk["target_family_ids"])
    indexed_terms = [row["canonical_term"] for row in safe_rows]
    high_indexed = sorted(set(indexed_terms) & HIGH_PRIORITY)
    high_not = sorted(HIGH_PRIORITY - set(indexed_terms))
    lines = [
        "# Dramatica Retrieval Index Report",
        "",
        "## Purpose",
        "",
        "Build a filtered retrieval chunk file and SQLite index over repaired Dramatica term definitions for future packet-reference retrieval.",
        "",
        "## Inputs Read",
        "",
        f"- input_normalized: `{input_path}`",
        "",
        "## Filtering Rules Applied",
        "",
        "- Excluded `defer_from_task_c_indexing`.",
        "- Excluded `source_excerpt_low_quality`.",
        "- Required `may_be_used_as_scene_evidence: false`.",
        "- Required `requires_owner_approval_for_packet_use: true`.",
        "- Required `review_status: draft_needs_human_review`.",
        "",
        "## Terms Indexed",
        "",
    ]
    lines.extend(f"- {term}" for term in indexed_terms)
    lines.extend(["", "## Terms Skipped Because defer_from_task_c_indexing", ""])
    lines.extend(f"- {term}" for term in skipped["deferred"]) if skipped["deferred"] else lines.append("- none")
    lines.extend(["", "## Terms Skipped Because source_excerpt_low_quality", ""])
    lines.extend(f"- {term}" for term in skipped["low_quality"]) if skipped["low_quality"] else lines.append("- none")
    lines.extend(["", "## Terms Skipped For Safety Field Mismatch", ""])
    lines.extend(f"- {term}" for term in skipped["safety_mismatch"]) if skipped["safety_mismatch"] else lines.append("- none")
    lines.extend(["", "## Chunk Counts By chunk_type", ""])
    for key, value in sorted(by_type.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Chunk Counts By target_family", ""])
    for key, value in sorted(by_family.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## SQLite Index",
            "",
            f"- path: `{sqlite_path}`",
            f"- fts5_enabled: {str(fts_enabled).lower()}",
            "",
            "## Sample Queries Run",
            "",
        ]
    )
    for query, terms in sample_results.items():
        lines.append(f"- `{query}` -> {', '.join(terms) if terms else 'no results'}")
    lines.extend(["", "## Sample Query Results Summary", ""])
    lines.append("Sample queries returned compact definition/reference chunks with packet-safety reminders.")
    lines.extend(["", "## High-Priority Packet Terms Indexed", ""])
    lines.extend(f"- {term}" for term in high_indexed) if high_indexed else lines.append("- none")
    lines.extend(["", "## High-Priority Packet Terms Not Indexed", ""])
    lines.extend(f"- {term}" for term in high_not) if high_not else lines.append("- none")
    lines.extend(
        [
            "",
            "## Known Limitations",
            "",
            "- Influence Character Throughline is not directly indexed as its own authoritative term if still unresolved.",
            "- Deferred dynamics may need later repair before indexing.",
            "- Retrieval output is reference only, not packet approval.",
            "",
            "## Confirmations",
            "",
            "- No packet files were edited.",
            "- No SFT records were created.",
            "- No backend/frontend files were modified.",
            "- No example project files were modified.",
            "- All chunks are definition/reference only.",
            "- No chunk may be used as scene evidence.",
            "- Owner approval remains required for packet use.",
            "",
            "## Next Recommended Task",
            "",
            "Task D create packet-field retrieval mapping, or Task E retrieve packet-specific context for packet_001 only after Task D.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = resolve(args.input_normalized)
    chunks_path = resolve(args.output_chunks)
    sqlite_path = resolve(args.output_sqlite)
    report_path = resolve(args.report)
    if not input_path.exists():
        write_text(BLOCKED_MISSING, "# BLOCKED: Dramatica Retrieval Index Missing Normalized Terms\n\nNormalized term file is missing. Run B3/B3.1 first.")
        print(f"Missing normalized terms: {input_path}")
        return 2
    rows = load_normalized(input_path)
    safe_rows, skipped = filter_terms(rows)
    if not safe_rows:
        write_text(BLOCKED_EMPTY, "# BLOCKED: Dramatica Retrieval Index No Safe Terms\n\nAll normalized terms were filtered out. No empty index was created.")
        print("No safe terms to index.")
        return 2
    chunks = make_chunks(safe_rows)
    metadata = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_normalized": str(input_path),
        "chunk_count": str(len(chunks)),
        "indexed_term_count": str(len(safe_rows)),
        "skipped_deferred_count": str(len(skipped["deferred"])),
        "skipped_low_quality_count": str(len(skipped["low_quality"])),
        "safety_note": "Retrieved Dramatica terms are definition/reference material only. They are not scene evidence and do not approve packet labels.",
    }
    fts_enabled = False
    sample_results: dict[str, list[str]] = {}
    if not args.dry_run:
        write_jsonl(chunks_path, chunks)
        fts_enabled = build_sqlite(sqlite_path, chunks, metadata)
        for query in (
            "Main Character versus Protagonist",
            "Relationship Story versus generic relationship",
            "Overall Story Throughline",
            "Domain Class Situation Activity Mind Psychology",
        ):
            sample_results[query] = run_sample_query(sqlite_path, query)
        write_text(
            report_path,
            make_report(
                input_path=input_path,
                chunks_path=chunks_path,
                sqlite_path=sqlite_path,
                rows=rows,
                safe_rows=safe_rows,
                skipped=skipped,
                chunks=chunks,
                fts_enabled=fts_enabled,
                sample_results=sample_results,
            ),
        )
        BLOCKED_MISSING.unlink(missing_ok=True)
        BLOCKED_EMPTY.unlink(missing_ok=True)
    print(f"Indexed terms: {len(safe_rows)}")
    print(f"Retrieval chunks: {len(chunks)}")
    print(f"Skipped deferred: {len(skipped['deferred'])}")
    print(f"Skipped low quality: {len(skipped['low_quality'])}")
    print(f"FTS5 enabled: {str(fts_enabled).lower()}")
    if args.dry_run:
        print("Dry run only; no files written.")
    else:
        print(f"Wrote {chunks_path}")
        print(f"Wrote {sqlite_path}")
        print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
