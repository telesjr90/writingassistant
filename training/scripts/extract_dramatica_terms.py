from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INVENTORY_JSON = REPO_ROOT / "training" / "knowledge" / "dramatica_source_inventory.json"
DEFAULT_TARGETS_JSON = REPO_ROOT / "training" / "knowledge" / "dramatica_task_b_targets.json"
DEFAULT_SOURCE_ROOT = Path("/mnt/e/project-test-readiness")
DEFAULT_OUTPUT_RAW = REPO_ROOT / "training" / "knowledge" / "dramatica_terms_raw.jsonl"
DEFAULT_SUMMARY_REPORT = REPO_ROOT / "training" / "reports" / "dramatica_terms_raw_extraction_summary.md"
BLOCKED_MISSING_TARGETS = REPO_ROOT / "training" / "reports" / "BLOCKED_dramatica_task_b2_missing_targets.md"

JSON_LOAD_LIMIT_BYTES = 40 * 1024 * 1024
RECORD_FIELDS = [
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
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract bounded raw Dramatica term matches from canonical source files only."
    )
    parser.add_argument("--inventory-json", type=Path, default=DEFAULT_INVENTORY_JSON)
    parser.add_argument("--targets-json", type=Path, default=DEFAULT_TARGETS_JSON)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-raw", type=Path, default=DEFAULT_OUTPUT_RAW)
    parser.add_argument("--summary-report", type=Path, default=DEFAULT_SUMMARY_REPORT)
    parser.add_argument("--max-source-quote-words", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_missing_targets_report(targets_path: Path) -> None:
    write_text(
        BLOCKED_MISSING_TARGETS,
        "\n".join(
            [
                "# BLOCKED: Dramatica Task B2 Missing Targets",
                "",
                f"- expected_targets_json: `{targets_path}`",
                "- status: missing",
                "",
                "Run Task B1 before Task B2. No raw extraction files were created.",
            ]
        ),
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> tuple[Any, str | None]:
    try:
        return load_json(path), None
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"{path}: {type(exc).__name__}: {exc}"


def source_relative(path: Path, source_root: Path) -> str:
    try:
        return path.resolve().relative_to(source_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def source_name(path: str) -> str:
    return Path(path).name


def normalized_source_priority(targets: dict[str, Any], source_root: Path) -> list[dict[str, Any]]:
    priority: list[dict[str, Any]] = []
    for item in targets.get("source_priority", []):
        if not isinstance(item, dict):
            continue
        path_value = item.get("path")
        if not isinstance(path_value, str) or not path_value:
            continue
        path = Path(path_value)
        if not path.is_absolute():
            path = source_root / path
        relative = source_relative(path, source_root)
        if relative.startswith("recu33/"):
            continue
        if path.name in {"data.json", "schema.json"}:
            continue
        priority.append(
            {
                "rank": int(item.get("rank") or len(priority) + 1),
                "path": path,
                "relative": relative,
                "source_family": str(item.get("source_family") or "unknown"),
            }
        )
    return sorted(priority, key=lambda item: item["rank"])


def read_pages(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        return [], f"stat failed: {exc}"
    if size > JSON_LOAD_LIMIT_BYTES:
        return [], f"skipped large JSON over safe load limit: {size} bytes"
    try:
        data = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"{type(exc).__name__}: {exc}"

    pages: list[dict[str, Any]] = []
    if isinstance(data, dict):
        raw_pages = data.get("pages")
        if isinstance(raw_pages, list):
            for index, page in enumerate(raw_pages):
                if isinstance(page, dict):
                    content = page.get("content")
                    if isinstance(content, str):
                        pages.append(
                            {
                                "location": f"page {page.get('page_number', index + 1)}",
                                "text": content,
                            }
                        )
                elif isinstance(page, str):
                    pages.append({"location": f"page {index + 1}", "text": page})
            return pages, None
        flattened = flatten_text_nodes(data)
        for index, (json_path, text) in enumerate(flattened):
            pages.append({"location": json_path or f"object text {index + 1}", "text": text})
        return pages, None
    if isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, str):
                pages.append({"location": f"list[{index}]", "text": item})
            elif isinstance(item, dict):
                flattened = flatten_text_nodes(item, prefix=f"list[{index}]")
                for json_path, text in flattened:
                    pages.append({"location": json_path, "text": text})
        return pages, None
    return [], f"unsupported JSON top-level type: {type(data).__name__}"


def flatten_text_nodes(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    nodes: list[tuple[str, str]] = []
    if isinstance(value, str):
        if value.strip():
            nodes.append((prefix, value))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            nodes.extend(flatten_text_nodes(item, f"{prefix}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            nodes.extend(flatten_text_nodes(item, f"{prefix}.{key}"))
    return nodes


def aliases_for(family: dict[str, Any], target_term: str) -> list[str]:
    aliases = [target_term]
    raw_aliases = family.get("aliases")
    if isinstance(raw_aliases, dict):
        value = raw_aliases.get(target_term)
        if isinstance(value, list):
            aliases.extend(item for item in value if isinstance(item, str))
    return list(dict.fromkeys(aliases))


def term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


def compact_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def excerpt_around(text: str, match: re.Match[str], max_words: int) -> str:
    clean = compact_whitespace(text)
    matched = compact_whitespace(match.group(0))
    start_in_clean = clean.lower().find(matched.lower())
    if start_in_clean < 0:
        words = clean.split()
    else:
        before = clean[:start_in_clean].split()
        middle = clean[start_in_clean : start_in_clean + len(matched)].split()
        after = clean[start_in_clean + len(matched) :].split()
        remaining = max(max_words - len(middle), 0)
        left_count = remaining // 2
        right_count = remaining - left_count
        words = before[-left_count:] + middle + after[:right_count]
    return " ".join(words[:max_words])


def stable_record_id(*parts: str) -> str:
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-z0-9]+", "_", "_".join(parts[:2]).lower()).strip("_")[:60]
    return f"dram_raw_{slug}_{digest}"


def make_record(
    *,
    family_id: str,
    target_term: str,
    matched_alias: str,
    source: dict[str, Any],
    source_root: Path,
    location: str,
    raw_excerpt: str,
    extraction_status: str,
    notes: str,
    safety_flags: list[str],
) -> dict[str, Any]:
    path = source["path"]
    relative = source_relative(path, source_root)
    record = {
        "record_id": stable_record_id(family_id, target_term, matched_alias, relative, location, extraction_status),
        "target_family_id": family_id,
        "target_term": target_term,
        "matched_alias": matched_alias,
        "source_path": str(path.resolve()),
        "source_relative_path": relative,
        "source_priority_rank": int(source["rank"]),
        "source_family": str(source["source_family"]),
        "source_location": location,
        "raw_excerpt": raw_excerpt,
        "extraction_status": extraction_status,
        "notes": notes,
        "safety_flags": list(dict.fromkeys(safety_flags)),
    }
    return {field: record[field] for field in RECORD_FIELDS}


def family_flags(family: dict[str, Any], global_flags: list[str]) -> list[str]:
    flags = ["definition_only_not_scene_evidence", "requires_owner_approval"]
    raw = family.get("caution_flags")
    if isinstance(raw, list):
        flags.extend(item for item in raw if isinstance(item, str))
    for flag in (
        "do_not_use_data_json_or_schema_json_as_definition_authority",
        "ignore_recu33_archival_duplicates_unless_canonical_missing",
    ):
        if flag in global_flags:
            flags.append(flag)
    return list(dict.fromkeys(flags))


def extract_records(
    *,
    targets: dict[str, Any],
    sources: list[dict[str, Any]],
    source_pages: dict[str, list[dict[str, Any]]],
    source_root: Path,
    max_words: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    found_terms: set[tuple[str, str]] = set()
    global_flags = [item for item in targets.get("caution_flags", []) if isinstance(item, str)]

    for family in targets.get("target_families", []):
        if not isinstance(family, dict):
            continue
        family_id = str(family.get("family_id") or "")
        if not family_id:
            continue
        flags = family_flags(family, global_flags)
        terms = [item for item in family.get("target_terms", []) if isinstance(item, str)]
        for target_term in terms:
            aliases = aliases_for(family, target_term)
            for source in sources:
                pages = source_pages.get(str(source["path"]), [])
                source_had_match = False
                for alias in aliases:
                    pattern = term_pattern(alias)
                    for page in pages:
                        text = page["text"]
                        match = pattern.search(text)
                        if not match:
                            continue
                        key = (family_id, target_term, str(source["path"]))
                        if key in seen_keys:
                            source_had_match = True
                            break
                        seen_keys.add(key)
                        found_terms.add((family_id, target_term))
                        status = "found_secondary" if int(source["rank"]) >= 6 else (
                            "found_direct" if alias == target_term else "found_alias"
                        )
                        notes = "B2 raw extraction only; not normalized; not scene evidence."
                        if alias != target_term:
                            notes += f" Matched alias for target term {target_term!r}."
                        records.append(
                            make_record(
                                family_id=family_id,
                                target_term=target_term,
                                matched_alias=alias,
                                source=source,
                                source_root=source_root,
                                location=str(page["location"]),
                                raw_excerpt=excerpt_around(text, match, max_words),
                                extraction_status=status,
                                notes=notes,
                                safety_flags=flags,
                            )
                        )
                        source_had_match = True
                        break
                    if source_had_match:
                        break

    target_pairs = {
        (str(family.get("family_id")), term)
        for family in targets.get("target_families", [])
        if isinstance(family, dict)
        for term in family.get("target_terms", [])
        if isinstance(term, str)
    }
    diagnostics = {
        "found_terms": sorted(found_terms),
        "not_found_terms": sorted(target_pairs - found_terms),
    }
    return records, diagnostics


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def make_summary(
    *,
    inventory_path: Path,
    targets_path: Path,
    source_root: Path,
    sources: list[dict[str, Any]],
    skipped_sources: list[dict[str, str]],
    parse_warnings: list[str],
    rows: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    dry_run: bool,
) -> str:
    by_source = Counter(row["source_relative_path"] for row in rows)
    by_family = Counter(row["target_family_id"] for row in rows)
    by_status = Counter(row["extraction_status"] for row in rows)
    found_terms = diagnostics["found_terms"]
    not_found_terms = diagnostics["not_found_terms"]

    lines = [
        "# Dramatica Terms Raw Extraction Summary",
        "",
        "## Purpose",
        "",
        "Create traceable raw extraction candidates for targeted Dramatica packet-reference terms. This B2 output is not normalized and is not scene evidence.",
        "",
        "## Inputs Read",
        "",
        f"- inventory_json: `{inventory_path}`",
        f"- targets_json: `{targets_path}`",
        f"- source_root: `{source_root}`",
        "",
        "## Source Files Parsed",
        "",
    ]
    for source in sources:
        lines.append(f"- rank {source['rank']}: `{source['relative']}` ({source['source_family']})")
    lines.extend(["", "## Source Files Skipped And Why", ""])
    if skipped_sources:
        for item in skipped_sources:
            lines.append(f"- `{item['path']}`: {item['reason']}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Raw Records Extracted",
            "",
            f"- dry_run: {str(dry_run).lower()}",
            f"- raw_record_count: {len(rows)}",
            "",
            "## Raw Records By Source File",
            "",
        ]
    )
    for source, count in sorted(by_source.items()):
        lines.append(f"- `{source}`: {count}")
    if not by_source:
        lines.append("- none")
    lines.extend(["", "## Raw Records By Target Family", ""])
    for family, count in sorted(by_family.items()):
        lines.append(f"- `{family}`: {count}")
    if not by_family:
        lines.append("- none")
    lines.extend(["", "## Raw Records By Extraction Status", ""])
    for status, count in sorted(by_status.items()):
        lines.append(f"- `{status}`: {count}")
    if not by_status:
        lines.append("- none")
    lines.extend(["", "## Target Terms Found", ""])
    for family_id, term in found_terms:
        lines.append(f"- `{family_id}`: {term}")
    if not found_terms:
        lines.append("- none")
    lines.extend(["", "## Target Terms Not Found", ""])
    for family_id, term in not_found_terms:
        lines.append(f"- `{family_id}`: {term}")
    if not not_found_terms:
        lines.append("- none")
    lines.extend(["", "## JSON Parsing Errors Or Warnings", ""])
    if parse_warnings:
        for warning in parse_warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Raw excerpts are short bounded source quotes and are not normalized definitions.",
            "- Matches are lexical candidates only; B3 must normalize, de-duplicate, cite, and review them.",
            "- Dictionary matches are preferred by source priority, but secondary matches are retained as raw evidence candidates.",
            "- `data.json`, `schema.json`, and `recu33/...` archival duplicates were not used as definition authorities.",
            "",
            "## Confirmations",
            "",
            "- No normalization was performed.",
            "- No packet files were edited.",
            "- No SFT records were created.",
            "- No backend/frontend files were modified.",
            "- All raw records are definition/reference extraction candidates only.",
            "- No raw record may be used as scene evidence.",
            "",
            "## Next Step",
            "",
            "Run B3 normalize, report, validate, repair.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    inventory_path = resolve_repo_path(args.inventory_json)
    targets_path = resolve_repo_path(args.targets_json)
    output_raw = resolve_repo_path(args.output_raw)
    summary_report = resolve_repo_path(args.summary_report)
    source_root = args.source_root

    if not targets_path.exists():
        write_missing_targets_report(targets_path)
        print(f"Missing targets JSON: {targets_path}")
        print(f"Wrote {BLOCKED_MISSING_TARGETS}")
        return 2

    targets = load_json(targets_path)
    inventory, inventory_warning = load_optional_json(inventory_path) if inventory_path.exists() else ({}, None)
    sources = normalized_source_priority(targets, source_root)
    skipped_sources = [
        {"path": str(item.get("path")), "reason": "deprioritized source; not a definition authority"}
        for item in targets.get("deprioritized_sources", [])
        if isinstance(item, dict)
    ]

    source_pages: dict[str, list[dict[str, Any]]] = {}
    parse_warnings: list[str] = []
    if inventory_warning:
        parse_warnings.append(f"inventory warning: {inventory_warning}")
    usable_sources: list[dict[str, Any]] = []
    for source in sources:
        path = source["path"]
        if source["relative"].startswith("recu33/"):
            skipped_sources.append({"path": source["relative"], "reason": "archival duplicate ignored"})
            continue
        if path.name in {"data.json", "schema.json"}:
            skipped_sources.append({"path": source["relative"], "reason": "deprioritized source; not a definition authority"})
            continue
        pages, warning = read_pages(path)
        if warning:
            parse_warnings.append(f"{source['relative']}: {warning}")
            skipped_sources.append({"path": source["relative"], "reason": warning})
            continue
        source_pages[str(path)] = pages
        usable_sources.append(source)

    rows, diagnostics = extract_records(
        targets=targets,
        sources=usable_sources,
        source_pages=source_pages,
        source_root=source_root,
        max_words=max(1, args.max_source_quote_words),
    )

    summary = make_summary(
        inventory_path=inventory_path,
        targets_path=targets_path,
        source_root=source_root,
        sources=usable_sources,
        skipped_sources=skipped_sources,
        parse_warnings=parse_warnings,
        rows=rows,
        diagnostics=diagnostics,
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        write_jsonl(output_raw, rows)
        write_text(summary_report, summary)
        BLOCKED_MISSING_TARGETS.unlink(missing_ok=True)
    print(f"Raw records: {len(rows)}")
    print(f"Found target family/term pairs: {len(diagnostics['found_terms'])}")
    print(f"Not found target family/term pairs: {len(diagnostics['not_found_terms'])}")
    if args.dry_run:
        print("Dry run only; no files written.")
    else:
        print(f"Wrote {output_raw}")
        print(f"Wrote {summary_report}")
    _ = inventory
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
