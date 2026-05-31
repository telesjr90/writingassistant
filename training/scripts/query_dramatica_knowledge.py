from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = REPO_ROOT / "training" / "knowledge" / "dramatica_retrieval_index.sqlite"
SAFETY = "Retrieved Dramatica terms are definition/reference material only. They are not scene evidence and do not approve packet labels."
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "from",
    "generic",
    "in",
    "is",
    "of",
    "only",
    "or",
    "the",
    "to",
    "versus",
    "vs",
    "with",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the local Dramatica retrieval index.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--family")
    parser.add_argument("--term")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dedupe-terms", action="store_true", default=True, help="Diversify results by canonical term. Enabled by default.")
    parser.add_argument("--prefer-definition", action="store_true", default=True, help="Prefer definition chunks before other chunk types. Enabled by default.")
    parser.add_argument("--max-chunks-per-term", type=int, default=2)
    parser.add_argument("--all-chunks", action="store_true", help="Disable term deduping and return the old chunk-level behavior.")
    return parser.parse_args(argv)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def metadata(conn: sqlite3.Connection) -> dict[str, str]:
    try:
        return {key: value for key, value in conn.execute("SELECT key, value FROM metadata")}
    except sqlite3.Error:
        return {}


def row_to_result(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "chunk_id": row["chunk_id"],
        "canonical_term": row["canonical_term"],
        "chunk_type": row["chunk_type"],
        "retrieval_text": row["retrieval_text"],
        "packet_fields_supported": json.loads(row["packet_fields_supported_json"]),
        "caution_flags": json.loads(row["caution_flags_json"]),
        "owner_review_questions": json.loads(row["owner_review_questions_json"]),
        "recommended_primary_source": json.loads(row["recommended_primary_source_json"]),
    }


def packet_field_query(query: str) -> bool:
    terms = set(query_terms(query))
    return bool(terms & {"packet", "field", "fields", "guidance", "storyform_context", "evidence_spans"})


def chunk_type_priority(chunk_type: str, *, prefer_definition: bool, wants_packet_fields: bool) -> int:
    if wants_packet_fields:
        order = {
            "definition": 0 if prefer_definition else 1,
            "packet_field_guidance": 1 if prefer_definition else 0,
            "aliases": 2,
            "cautions": 3,
            "owner_review_questions": 3,
        }
    else:
        order = {
            "definition": 0 if prefer_definition else 2,
            "aliases": 1,
            "cautions": 2,
            "owner_review_questions": 2,
            "packet_field_guidance": 3,
        }
    return order.get(chunk_type, 9)


def diversify_results(results: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    limit = max(1, args.top_k)
    if args.all_chunks:
        return results[:limit]

    max_per_term = max(1, args.max_chunks_per_term)
    wants_packet_fields = packet_field_query(args.query)
    grouped: dict[str, list[dict[str, Any]]] = {}
    term_order: list[str] = []
    original_order: dict[str, int] = {}
    for order, result in enumerate(results):
        term = result["canonical_term"]
        grouped.setdefault(term, []).append(result)
        if term not in original_order:
            original_order[term] = order
            term_order.append(term)

    for chunks in grouped.values():
        chunks.sort(
            key=lambda result: (
                chunk_type_priority(
                    result["chunk_type"],
                    prefer_definition=args.prefer_definition,
                    wants_packet_fields=wants_packet_fields,
                ),
                results.index(result),
            )
        )
    term_order.sort(key=lambda term: original_order[term])

    selected: list[dict[str, Any]] = []
    for pass_index in range(max_per_term):
        for term in term_order:
            chunks = grouped[term]
            if pass_index < len(chunks):
                selected.append(chunks[pass_index])
                if len(selected) >= limit:
                    return selected
    return selected


def query_terms(query: str) -> list[str]:
    terms = []
    for raw in query.replace("/", " ").replace("-", " ").split():
        token = "".join(ch for ch in raw.lower() if ch.isalnum() or ch == "_")
        if len(token) < 3 or token in STOPWORDS:
            continue
        terms.append(token)
    return list(dict.fromkeys(terms))


def like_query(conn: sqlite3.Connection, args: argparse.Namespace, filters: list[str], filter_params: list[Any]) -> list[dict[str, Any]]:
    terms = query_terms(args.query)
    limit = candidate_limit(args)
    if not terms:
        term_where = "1=1"
        term_params: list[Any] = []
        score_sql = "1"
        score_params: list[Any] = []
    else:
        clauses = []
        score_parts = []
        term_params = []
        score_params = []
        for term in terms:
            like = f"%{term}%"
            clauses.append("(canonical_term LIKE ? OR retrieval_text LIKE ?)")
            term_params.extend([like, like])
            score_parts.append("(CASE WHEN canonical_term LIKE ? THEN 4 ELSE 0 END + CASE WHEN retrieval_text LIKE ? THEN 1 ELSE 0 END)")
            score_params.extend([like, like])
        term_where = "(" + " OR ".join(clauses) + ")"
        score_sql = " + ".join(score_parts)

    where = term_where
    params = term_params[:]
    if filters:
        where += " AND " + " AND ".join(filters)
        params.extend(filter_params)

    sql = f"""
        SELECT *, ({score_sql}) AS score
        FROM chunks
        WHERE {where}
        ORDER BY score DESC, canonical_term, chunk_type
        LIMIT ?
    """
    return [row_to_result(row) for row in conn.execute(sql, score_params + params + [limit])]


def query_index(conn: sqlite3.Connection, args: argparse.Namespace) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    meta = metadata(conn)
    params: list[Any] = []
    filters = []
    if args.family:
        filters.append("target_family_ids_json LIKE ?")
        params.append(f"%{args.family}%")
    if args.term:
        filters.append("canonical_term = ?")
        params.append(args.term)
    limit = candidate_limit(args)
    if meta.get("sqlite_fts_enabled") == "true":
        where = "chunks_fts MATCH ?"
        fts_terms = query_terms(args.query)
        fts_query = " AND ".join(fts_terms) if fts_terms else " ".join(args.query.replace('"', " ").split())
        query_params: list[Any] = [fts_query]
        if filters:
            where += " AND " + " AND ".join(f"chunks.{flt}" for flt in filters)
            query_params.extend(params)
        sql = f"""
            SELECT chunks.*
            FROM chunks_fts
            JOIN chunks ON chunks.chunk_id = chunks_fts.chunk_id
            WHERE {where}
            ORDER BY bm25(chunks_fts)
            LIMIT ?
        """
        query_params.append(limit)
        try:
            results = [row_to_result(row) for row in conn.execute(sql, query_params)]
            if results:
                return diversify_results(results, args)
        except sqlite3.Error:
            pass
    return diversify_results(like_query(conn, args, filters, params), args)


def candidate_limit(args: argparse.Namespace) -> int:
    top_k = max(1, args.top_k)
    if args.all_chunks:
        return top_k
    return max(top_k * max(4, args.max_chunks_per_term * 4), top_k + 40)


def print_text(results: list[dict[str, Any]]) -> None:
    print(SAFETY)
    print("")
    if not results:
        print("No results.")
        return
    for index, result in enumerate(results, start=1):
        print(f"{index}. {result['canonical_term']} ({result['chunk_type']})")
        print(f"   chunk_id: {result['chunk_id']}")
        print(f"   {result['retrieval_text']}")
        print("")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    index_path = resolve(args.index)
    conn = sqlite3.connect(index_path)
    conn.row_factory = sqlite3.Row
    try:
        results = query_index(conn, args)
    finally:
        conn.close()
    if args.json:
        print(json.dumps({"safety_reminder": SAFETY, "results": results}, indent=2, ensure_ascii=False))
    else:
        print_text(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
