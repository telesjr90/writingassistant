from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_ROOT = Path("/mnt/e/project-test-readiness")
DEFAULT_OUTPUT_JSON = REPO_ROOT / "training" / "knowledge" / "dramatica_source_inventory.json"
DEFAULT_OUTPUT_MD = REPO_ROOT / "training" / "knowledge" / "dramatica_source_inventory.md"
REPORT_PATH = REPO_ROOT / "training" / "reports" / "dramatica_source_inventory_report.md"
BLOCKED_PATH = REPO_ROOT / "training" / "reports" / "BLOCKED_dramatica_source_inventory_missing_path.md"

EXCLUDED_DIRS = {
    ".git",
    ".agents",
    ".codex",
    ".codex-pr-reopened-closeout",
    ".codex-temp",
    ".cursor",
    ".local-archive",
    ".playwright-cli",
    ".playwright-mcp",
    ".recovery",
    ".vscode",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
    "test-results",
    "__mocks__",
    "__tests__",
    "__tests__backup",
    "components",
    "constants",
    "containers",
    "contexts",
    "cypress",
    "e2e",
    "electron",
    "errors",
    "examples",
    "features",
    "hooks",
    "logging",
    "monitoring",
    "nlp_backend",
    "pages",
    "public",
    "routes",
    "schemas",
    "scripts",
    "src",
    "store",
    "test",
    "test-data",
    "tests",
    "tests_backup",
    "tools",
    "types",
    "utils",
    "workers",
}

TEXT_EXTENSIONS = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

EXPECTED_SOURCES = [
    "Dramatica-Dictionary-2000.json",
    "dramatica-theory-book.json",
    "dramatica-appendix.json",
    "dramatica-structure-chart.json",
    "original-dramatica-tables.json",
    "dramatica-comic-book-2004.json",
    "never-trust-a-hero-3rd-edition.json",
    "data.json",
    "schema.json",
    "12-targeted-dramatica-definition-catalog.md",
]

TASK_B_ORDER = [
    "Dramatica-Dictionary-2000.json",
    "dramatica-theory-book.json",
    "dramatica-appendix.json",
    "dramatica-structure-chart.json",
    "original-dramatica-tables.json",
    "dramatica-comic-book-2004.json",
    "never-trust-a-hero-3rd-edition.json",
    "data.json",
    "schema.json",
]

JSON_LOAD_LIMIT_BYTES = 12 * 1024 * 1024
LARGE_FILE_THRESHOLD_BYTES = 25 * 1024 * 1024
LINE_COUNT_LIMIT_BYTES = 2 * 1024 * 1024


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory Dramatica knowledge sources for later safe packet-reference retrieval."
    )
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--max-sample-chars", type=int, default=4000)
    parser.add_argument("--max-files", type=int)
    return parser.parse_args(argv)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_output(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_missing_path_report(source_root: Path) -> None:
    write_text(
        BLOCKED_PATH,
        "\n".join(
            [
                "# BLOCKED: Dramatica Source Inventory Missing Path",
                "",
                f"- requested_source_root: `{source_root}`",
                "- status: missing or not a directory",
                "",
                "Inventory was not created. Confirm the Windows path `E:\\project-test-readiness` "
                "is mounted at `/mnt/e/project-test-readiness` before rerunning.",
            ]
        ),
    )


def is_binary_sample(path: Path, sample_size: int = 4096) -> bool:
    try:
        data = path.open("rb").read(sample_size)
    except OSError:
        return True
    return b"\0" in data


def read_text_sample(path: Path, max_chars: int) -> tuple[str, str | None]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(max_chars), None
    except OSError as exc:
        return "", str(exc)


def count_lines(path: Path, size_bytes: int) -> int | None:
    if size_bytes > LINE_COUNT_LIMIT_BYTES:
        return None
    try:
        with path.open("rb") as handle:
            return sum(chunk.count(b"\n") for chunk in iter(lambda: handle.read(1024 * 1024), b""))
    except OSError:
        return None


def headings_from_sample(sample: str, limit: int = 12) -> list[str]:
    headings: list[str] = []
    for line in sample.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped[:160])
            if len(headings) >= limit:
                break
    return headings


def inspect_json(path: Path, size_bytes: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "json_valid": None,
        "json_top_level_type": None,
        "json_top_level_keys": [],
        "json_list_item_count": None,
        "json_error": None,
        "json_skipped_reason": None,
    }
    if size_bytes > JSON_LOAD_LIMIT_BYTES:
        result["json_skipped_reason"] = f"larger than safe JSON load limit ({JSON_LOAD_LIMIT_BYTES} bytes)"
        return result
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["json_valid"] = False
        result["json_error"] = f"{type(exc).__name__}: {exc}"
        return result
    result["json_valid"] = True
    if isinstance(value, dict):
        result["json_top_level_type"] = "object"
        result["json_top_level_keys"] = list(value.keys())[:50]
    elif isinstance(value, list):
        result["json_top_level_type"] = "list"
        result["json_list_item_count"] = len(value)
    else:
        result["json_top_level_type"] = type(value).__name__
    return result


def classify_family(path: Path, relative: str, sample: str) -> str:
    name = path.name
    rel_lower = relative.lower()
    sample_lower = sample.lower()
    if name == "Dramatica-Dictionary-2000.json":
        return "primary_dictionary"
    if name in {"dramatica-theory-book.json", "dramatica-comic-book-2004.json"}:
        return "theory_book"
    if name in {"dramatica-appendix.json", "dramatica-structure-chart.json"}:
        return "structural_corroboration"
    if name == "original-dramatica-tables.json":
        return "original_table_or_chart"
    if name == "never-trust-a-hero-3rd-edition.json":
        return "secondary_explanation"
    if name in {"data.json", "schema.json"} and "dramatica_json" in rel_lower:
        return "simplified_schema_or_vocabulary"
    if name == "12-targeted-dramatica-definition-catalog.md":
        return "analysis_review_doc"
    if "dramatica_json" in rel_lower:
        return "unknown"
    if any(token in rel_lower for token in ("component", "src/", "backend", "frontend", "utils", "hooks", "routes", "workers")):
        return "implementation_evidence"
    if any(token in rel_lower for token in ("analysis", "audit", "review", "report", "plan", "docs/")):
        return "analysis_review_doc"
    if any(token in sample_lower for token in ("dramatica", "throughline", "storyform", "relationship story")):
        return "secondary_explanation"
    if any(token in rel_lower for token in ("harry", "chapter", "prologue")):
        return "irrelevant_or_unsafe"
    return "unknown"


def classify_role(path: Path, relative: str, sample: str) -> str:
    text = f"{path.name} {relative} {sample[:2000]}".lower()
    if "schema" in path.name.lower():
        return "schema"
    role_keywords = [
        ("relationship_story", ("relationship story", "relationship_story")),
        ("four_throughlines", ("throughline", "overall story", "main character", "influence character")),
        ("domains_classes", ("domain", "class", "situation", "activity", "manipulation", "fixed attitude")),
        ("concerns_types", ("concern", "type")),
        ("issues_variations", ("issue", "variation")),
        ("problems_elements", ("problem", "solution", "element")),
        ("dynamics", ("resolve", "outcome", "judgment", "driver", "limit")),
        ("character_roles", ("protagonist", "antagonist", "guardian", "contagonist", "sidekick", "skeptic")),
        ("definitions", ("dictionary", "definition", "term")),
        ("implementation_map", ("component", "function", "class", "typescript", "react")),
    ]
    for role, keywords in role_keywords:
        if any(keyword in text for keyword in keywords):
            return role
    if classify_family(path, relative, sample) == "implementation_evidence":
        return "app_code"
    return "unknown"


def priority_for_family(family: str, name: str) -> str:
    if family == "primary_dictionary":
        return "primary"
    if family in {"theory_book", "secondary_explanation"}:
        return "secondary"
    if family in {"structural_corroboration", "original_table_or_chart"}:
        return "corroborating"
    if family == "implementation_evidence":
        return "implementation_evidence"
    if family == "simplified_schema_or_vocabulary" or name == "schema.json":
        return "schema_only"
    if family == "analysis_review_doc":
        return "ambient_vocabulary"
    return "unknown"


def reliability_for(family: str, priority: str) -> str:
    if priority == "primary":
        return "high_for_definitions_not_scene_truth"
    if priority in {"secondary", "corroborating"}:
        return "medium_for_reference_corroboration"
    if priority == "schema_only":
        return "low_for_theory_definitions_ambient_vocabulary_only"
    if priority == "implementation_evidence":
        return "implementation_only_not_theory_authority"
    return "unknown"


def should_extract_later(family: str, role: str, sample: str) -> bool:
    if family in {"irrelevant_or_unsafe", "implementation_evidence"}:
        return False
    relevant_roles = {
        "definitions",
        "four_throughlines",
        "domains_classes",
        "concerns_types",
        "issues_variations",
        "problems_elements",
        "dynamics",
        "character_roles",
        "relationship_story",
    }
    if role in relevant_roles:
        return True
    sample_lower = sample.lower()
    return any(
        term in sample_lower
        for term in (
            "throughline",
            "domain",
            "class",
            "concern",
            "issue",
            "variation",
            "problem",
            "element",
            "resolve",
            "relationship story",
            "appreciation",
            "story point",
        )
    )


def reason_for(
    family: str,
    role: str,
    priority: str,
    safe_for_packet_reference: bool,
    should_extract: bool,
    relative: str,
) -> str:
    if family == "implementation_evidence":
        return "Implementation file may show app behavior but is not theory authority."
    if family == "irrelevant_or_unsafe":
        return "Appears to be story text, tests, generated output, or otherwise unsafe for packet reference."
    if safe_for_packet_reference and should_extract:
        return f"Relevant Dramatica {role} reference material; priority={priority}."
    if safe_for_packet_reference:
        return "Potentially useful as broad reference or ambient vocabulary; extraction not prioritized."
    return f"No strong Dramatica reference signal found in {relative}."


def walk_files(source_root: Path, max_files: int | None) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    skipped_dirs: list[str] = []
    for root, dirs, filenames in os.walk(source_root):
        original_dirs = list(dirs)
        dirs[:] = [dirname for dirname in dirs if dirname not in EXCLUDED_DIRS]
        for dirname in sorted(set(original_dirs) - set(dirs)):
            skipped_dirs.append(str(Path(root) / dirname))
        for filename in sorted(filenames):
            files.append(Path(root) / filename)
            if max_files is not None and len(files) >= max_files:
                return files, skipped_dirs
    return files, skipped_dirs


def inspect_file(path: Path, source_root: Path, max_sample_chars: int) -> dict[str, Any]:
    stat = path.stat()
    relative = relative_to_root(path, source_root)
    extension = path.suffix.lower()
    binary = is_binary_sample(path)
    text_readable = not binary and (extension in TEXT_EXTENSIONS or stat.st_size < 1024 * 1024)
    sample = ""
    read_error = None
    if text_readable:
        sample, read_error = read_text_sample(path, max_sample_chars)
    family = classify_family(path, relative, sample)
    role = classify_role(path, relative, sample)
    priority = priority_for_family(family, path.name)
    safe_for_packet_reference = family in {
        "primary_dictionary",
        "theory_book",
        "structural_corroboration",
        "original_table_or_chart",
        "secondary_explanation",
        "simplified_schema_or_vocabulary",
        "analysis_review_doc",
    }
    may_be_used_as_scene_evidence = False
    extract = should_extract_later(family, role, sample)
    index = extract and safe_for_packet_reference
    record: dict[str, Any] = {
        "absolute_path": str(path.resolve()),
        "path_relative_to_source_root": relative,
        "extension": extension or "(none)",
        "size_bytes": stat.st_size,
        "modified_time_iso": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        "line_count": count_lines(path, stat.st_size) if text_readable else None,
        "detected_text_or_binary": "binary" if binary else "text",
        "likely_source_family": family,
        "likely_dramatica_role": role,
        "source_priority": priority,
        "reliability_guess": reliability_for(family, priority),
        "safe_for_packet_reference": safe_for_packet_reference,
        "may_be_used_as_scene_evidence": may_be_used_as_scene_evidence,
        "should_extract_later": extract,
        "should_index_later": index,
        "reason": reason_for(family, role, priority, safe_for_packet_reference, extract, relative),
        "notes": [],
    }
    if read_error:
        record["notes"].append(f"text sample read error: {read_error}")
    if stat.st_size > LARGE_FILE_THRESHOLD_BYTES:
        record["notes"].append("large_file_chunked_handling_recommended")
    if text_readable and stat.st_size > LINE_COUNT_LIMIT_BYTES:
        record["notes"].append("line_count_skipped_large_file")
    if extension == ".json" and not binary:
        record.update(inspect_json(path, stat.st_size))
    if extension in {".md", ".txt"} and sample:
        record["sample_headings"] = headings_from_sample(sample)
    if path.name in EXPECTED_SOURCES:
        record["notes"].append("known_expected_source")
    return record


def known_sources(files: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    for record in files:
        name = Path(record["path_relative_to_source_root"]).name
        if name in EXPECTED_SOURCES and name not in by_name:
            by_name[name] = record
    result: dict[str, dict[str, Any]] = {}
    for name in EXPECTED_SOURCES:
        record = by_name.get(name)
        result[name] = {
            "found": record is not None,
            "path": record["absolute_path"] if record else None,
            "recommended_role": (
                record["likely_source_family"]
                if record
                else (
                    "analysis_review_doc"
                    if name.endswith(".md")
                    else "expected_dramatica_reference"
                )
            ),
        }
    return result


def summarize(files: list[dict[str, Any]]) -> dict[str, Any]:
    family_counts = Counter(record["likely_source_family"] for record in files)
    priority_counts = Counter(record["source_priority"] for record in files)
    extension_counts = Counter(record["extension"] for record in files)
    candidate_count = sum(1 for record in files if record["safe_for_packet_reference"])
    return {
        "total_files_scanned": len(files),
        "total_candidate_dramatica_files": candidate_count,
        "total_should_extract_later": sum(1 for record in files if record["should_extract_later"]),
        "total_should_index_later": sum(1 for record in files if record["should_index_later"]),
        "source_family_counts": dict(sorted(family_counts.items())),
        "priority_counts": dict(sorted(priority_counts.items())),
        "extension_counts": dict(sorted(extension_counts.items())),
    }


def markdown_inventory(inventory: dict[str, Any]) -> str:
    files = inventory["files"]
    known = inventory["known_sources"]
    found = [name for name, data in known.items() if data["found"]]
    missing = [name for name, data in known.items() if not data["found"]]
    safe = [record for record in files if record["safe_for_packet_reference"]]
    unsafe = [record for record in files if not record["safe_for_packet_reference"]]
    implementation = [record for record in files if record["likely_source_family"] == "implementation_evidence"]
    large = [record for record in files if "large_file_chunked_handling_recommended" in record.get("notes", [])]
    extraction = [
        record for name in TASK_B_ORDER for record in files if Path(record["path_relative_to_source_root"]).name == name
    ]
    lines = [
        "# Dramatica Source Inventory",
        "",
        "## Purpose",
        "",
        "Inventory available Dramatica knowledge sources for later targeted definition extraction. "
        "These files are definition/reference material only and are not scene evidence.",
        "",
        "## Source Root Inspected",
        "",
        f"- `{inventory['source_root']}`",
        f"- generated_at: `{inventory['generated_at']}`",
        "",
        "## High-Value Files Found",
        "",
    ]
    lines.extend(f"- `{name}`: `{known[name]['path']}`" for name in found)
    if not found:
        lines.append("- none")
    lines.extend(["", "## Missing Expected Files", ""])
    lines.extend(f"- `{name}`" for name in missing) if missing else lines.append("- none")
    lines.extend(["", "## Source Family Summary", ""])
    for family, count in inventory["summary"]["source_family_counts"].items():
        lines.append(f"- `{family}`: {count}")
    lines.extend(["", "## Recommended Extraction Order", ""])
    if extraction:
        for record in extraction:
            lines.append(f"- `{record['path_relative_to_source_root']}` ({record['likely_source_family']}, {record['likely_dramatica_role']})")
    else:
        lines.append("- none")
    lines.extend(["", "## Files Safe For Packet Reference", ""])
    for record in safe[:200]:
        lines.append(f"- `{record['path_relative_to_source_root']}`: {record['likely_source_family']} / {record['likely_dramatica_role']}")
    if len(safe) > 200:
        lines.append(f"- ... {len(safe) - 200} additional safe reference files omitted from markdown listing")
    if not safe:
        lines.append("- none")
    lines.extend(["", "## Files Not Safe For Packet Use", ""])
    for record in unsafe[:200]:
        lines.append(f"- `{record['path_relative_to_source_root']}`: {record['reason']}")
    if len(unsafe) > 200:
        lines.append(f"- ... {len(unsafe) - 200} additional unsafe/unknown files omitted from markdown listing")
    if not unsafe:
        lines.append("- none")
    lines.extend(["", "## Implementation Evidence Only", ""])
    for record in implementation[:200]:
        lines.append(f"- `{record['path_relative_to_source_root']}`")
    if len(implementation) > 200:
        lines.append(f"- ... {len(implementation) - 200} additional implementation files omitted")
    if not implementation:
        lines.append("- none")
    lines.extend(["", "## Large Files Needing Chunked Handling Later", ""])
    lines.extend(f"- `{record['path_relative_to_source_root']}` ({record['size_bytes']} bytes)" for record in large) if large else lines.append("- none")
    lines.extend(
        [
            "",
            "## Warnings And Caveats",
            "",
            "- Dramatica reference files may define terms but must not be treated as proof of a specific scene's storyform.",
            "- Source definitions are not evidence spans for owner micro-storyform packets.",
            "- Packet labels still require owner approval.",
            "- This inventory does not prove that the app implements any Dramatica feature.",
            "- No packet files, SFT files, backend files, frontend files, or example project files were edited by this inventory.",
            "",
            "## Next Recommended Task",
            "",
            "Task B: targeted term extraction from the prioritized Dramatica sources, starting with the dictionary and theory book.",
        ]
    )
    return "\n".join(lines)


def report_markdown(inventory: dict[str, Any], skipped_dirs: list[str], source_root: Path) -> str:
    known = inventory["known_sources"]
    found = [name for name, data in known.items() if data["found"]]
    missing = [name for name, data in known.items() if not data["found"]]
    json_dir = source_root / "dramatica_JSON"
    lines = [
        "# Dramatica Source Inventory Report",
        "",
        "## Scan Summary",
        "",
        f"- source_root: `{source_root}`",
        f"- dramatica_JSON_exists: {str(json_dir.is_dir()).lower()}",
        f"- total_files_scanned: {inventory['summary']['total_files_scanned']}",
        f"- candidate_reference_files: {inventory['summary']['total_candidate_dramatica_files']}",
        f"- should_extract_later: {inventory['summary']['total_should_extract_later']}",
        f"- should_index_later: {inventory['summary']['total_should_index_later']}",
        "",
        "## What Was Not Scanned",
        "",
        "The scanner skipped configured noisy folders by directory name.",
    ]
    if skipped_dirs:
        for path in skipped_dirs[:200]:
            lines.append(f"- `{path}`")
        if len(skipped_dirs) > 200:
            lines.append(f"- ... {len(skipped_dirs) - 200} additional skipped directories")
    else:
        lines.append("- none")
    lines.extend(["", "## Expected Dramatica JSON Files", ""])
    for name in EXPECTED_SOURCES:
        status = "found" if known[name]["found"] else "missing"
        lines.append(f"- `{name}`: {status}")
    lines.extend(["", "## Recommended Source Priority For Task B", ""])
    for index, name in enumerate(TASK_B_ORDER, start=1):
        if name in {"data.json", "schema.json"}:
            suffix = " (ambient vocabulary only, not proof)"
        else:
            suffix = ""
        status = "found" if known[name]["found"] else "missing"
        lines.append(f"{index}. `{name}` - {status}{suffix}")
    lines.extend(
        [
            "",
            "## Safety Warnings",
            "",
            "- Reference definitions must not be used as scene evidence.",
            "- This inventory must not approve owner packet labels automatically.",
            "- Dramatica knowledge files can support definitions and review, not story truth for a specific scene.",
            "",
            "## Change Boundary Confirmations",
            "",
            "- No packet files were edited.",
            "- No SFT records were created.",
            "- No backend files were modified.",
            "- No frontend files were modified.",
            "- No example project files were modified.",
            "",
            "## High-Value Sources Found",
            "",
        ]
    )
    lines.extend(f"- `{name}`" for name in found) if found else lines.append("- none")
    lines.extend(["", "## Missing Expected Sources", ""])
    lines.extend(f"- `{name}`" for name in missing) if missing else lines.append("- none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = args.source_root.resolve()
    output_json = resolve_output(args.output_json)
    output_md = resolve_output(args.output_md)
    if not source_root.is_dir():
        write_missing_path_report(source_root)
        print(f"Source root missing: {source_root}")
        print(f"Wrote {BLOCKED_PATH}")
        return 2

    files, skipped_dirs = walk_files(source_root, args.max_files)
    records = [inspect_file(path, source_root, args.max_sample_chars) for path in files if path.is_file()]
    inventory = {
        "source_root": str(source_root),
        "generated_at": utc_now(),
        "summary": summarize(records),
        "known_sources": known_sources(records),
        "files": records,
    }
    write_json(output_json, inventory)
    write_text(output_md, markdown_inventory(inventory))
    write_text(REPORT_PATH, report_markdown(inventory, skipped_dirs, source_root))
    BLOCKED_PATH.unlink(missing_ok=True)
    print(f"Scanned files: {inventory['summary']['total_files_scanned']}")
    print(f"Candidate reference files: {inventory['summary']['total_candidate_dramatica_files']}")
    print(f"Should extract later: {inventory['summary']['total_should_extract_later']}")
    print(f"Wrote {output_json}")
    print(f"Wrote {output_md}")
    print(f"Wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
