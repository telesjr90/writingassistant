from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from query_dramatica_knowledge import SAFETY, query_index


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIELD_MAP = REPO_ROOT / "training" / "knowledge" / "dramatica_packet_field_map.json"
DEFAULT_INDEX = REPO_ROOT / "training" / "knowledge" / "dramatica_retrieval_index.sqlite"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Dramatica retrieval context by owner packet field.",
        epilog=(
            "Examples:\n"
            "  python training/scripts/query_packet_field_context.py --section \"Storyform Context\" --top-k 5\n"
            "  python training/scripts/query_packet_field_context.py --section \"Storyform Context: Main Character\" --top-k 5\n"
            "  python training/scripts/query_packet_field_context.py --section \"Storyform Context: Relationship Story\" --top-k 5\n"
            "  python training/scripts/query_packet_field_context.py --section \"Evidence Spans\" --top-k 5"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--field-map", type=Path, default=DEFAULT_FIELD_MAP)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--section")
    parser.add_argument("--field")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def load_field_map(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_mappings(field_map: dict[str, Any], section: str | None, field: str | None) -> list[dict[str, Any]]:
    mappings = field_map.get("field_mappings", [])
    selected = []
    for mapping in mappings:
        if section and section.lower() not in mapping["packet_section"].lower():
            continue
        if field and field.lower() != mapping["packet_field"].lower():
            continue
        selected.append(mapping)
    return selected


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "chunk_id": result["chunk_id"],
        "canonical_term": result["canonical_term"],
        "chunk_type": result["chunk_type"],
        "retrieval_text": result["retrieval_text"],
        "packet_fields_supported": result["packet_fields_supported"],
        "caution_flags": result["caution_flags"],
        "owner_review_questions": result["owner_review_questions"],
        "recommended_primary_source": result["recommended_primary_source"],
    }


def run_mapping_queries(conn: sqlite3.Connection, mapping: dict[str, Any], index_path: Path, top_k_override: int | None) -> dict[str, Any]:
    query_results = []
    top_k = top_k_override or mapping.get("recommended_query_top_k", 5)
    for query in mapping.get("retrieval_queries", []):
        args = argparse.Namespace(
            index=index_path,
            query=query,
            top_k=top_k,
            family=None,
            term=None,
            json=False,
            dedupe_terms=True,
            prefer_definition=True,
            max_chunks_per_term=2,
            all_chunks=False,
        )
        results = [compact_result(row) for row in query_index(conn, args)]
        query_results.append({"query": query, "results": results})
    return {
        "packet_section": mapping["packet_section"],
        "packet_field": mapping["packet_field"],
        "field_purpose": mapping["field_purpose"],
        "fill_guidance": mapping["fill_guidance"],
        "do_not_do": mapping["do_not_do"],
        "requires_owner_approval": mapping["requires_owner_approval"],
        "requires_scene_evidence": mapping["requires_scene_evidence"],
        "may_use_retrieved_definitions_as_scene_evidence": mapping["may_use_retrieved_definitions_as_scene_evidence"],
        "owner_review_questions": mapping["owner_review_questions"],
        "query_results": query_results,
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [SAFETY, ""]
    if not payload["fields"]:
        lines.append("No packet field mappings matched the requested filters.")
        return "\n".join(lines) + "\n"
    for field in payload["fields"]:
        lines.append(f"## {field['packet_section']} / {field['packet_field']}")
        lines.append("")
        lines.append(f"Purpose: {field['field_purpose']}")
        lines.append(f"Fill guidance: {field['fill_guidance']}")
        if field["owner_review_questions"]:
            lines.append("Owner review questions:")
            for question in field["owner_review_questions"]:
                lines.append(f"- {question}")
        if field["do_not_do"]:
            lines.append("Do not:")
            for item in field["do_not_do"]:
                lines.append(f"- {item}")
        if not field["query_results"]:
            lines.append("Retrieval queries: none. Use packet/source facts only.")
        for query_result in field["query_results"]:
            lines.append(f"Query: `{query_result['query']}`")
            if not query_result["results"]:
                lines.append("- No retrieval results.")
                continue
            for result in query_result["results"]:
                lines.append(f"- {result['canonical_term']} ({result['chunk_type']}): {result['chunk_id']}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    field_map_path = resolve(args.field_map)
    index_path = resolve(args.index)
    field_map = load_field_map(field_map_path)
    mappings = selected_mappings(field_map, args.section, args.field)

    conn = sqlite3.connect(index_path)
    conn.row_factory = sqlite3.Row
    try:
        fields = [run_mapping_queries(conn, mapping, index_path, args.top_k) for mapping in mappings]
    finally:
        conn.close()

    payload = {
        "safety_reminder": SAFETY,
        "fields": fields,
    }
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) if args.json else render_text(payload)
    if args.output:
        output_path = resolve(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
