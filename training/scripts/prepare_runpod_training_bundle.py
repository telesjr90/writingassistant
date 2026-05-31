from __future__ import annotations

import argparse
import fnmatch
import json
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
REPORTS_DIR = TRAINING_DIR / "reports"
DEFAULT_OUTPUT_DIR = TRAINING_DIR / "bundles"


EXCLUDE_PATTERNS = [
    ".git/**",
    ".venv*/**",
    "**/.env",
    "**/.env.*",
    "**/__pycache__/**",
    "**/.pytest_cache/**",
    "training/models/hf_cache/**",
    "training/runs/**",
    "training/bundles/**",
    "training/**/*.safetensors",
    "training/**/*.bin",
    "training/**/*.gguf",
    "training/**/*.pt",
    "training/**/*.pth",
    "training/**/*.ckpt",
    "node_modules/**",
    "frontend/node_modules/**",
]

INCLUDE_ROOTS = [
    "docs/plan.md",
    "training/configs",
    "training/data",
    "training/reports",
    "training/schemas",
    "training/scripts",
    "training/requirements-unsloth.txt",
]


@dataclass(frozen=True)
class BundlePlan:
    included: list[Path]
    excluded: list[tuple[Path, str]]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a RunPod training bundle or dry-run manifest. Excludes API keys, "
            "environment files, caches, runs, and model weights by default."
        )
    )
    parser.add_argument("--dry-run", action="store_true", help="Write reports without creating a tarball.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--include-model-weights",
        action="store_true",
        help="Include training/models/hf_cache and model weight files. Default is excluded.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORTS_DIR / "runpod_training_bundle_report.md",
    )
    return parser.parse_args(argv)


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def active_excludes(include_model_weights: bool) -> list[str]:
    if not include_model_weights:
        return EXCLUDE_PATTERNS
    return [
        pattern
        for pattern in EXCLUDE_PATTERNS
        if pattern
        not in {
            "training/models/hf_cache/**",
            "training/**/*.safetensors",
            "training/**/*.bin",
            "training/**/*.gguf",
            "training/**/*.pt",
            "training/**/*.pth",
            "training/**/*.ckpt",
        }
    ]


def excluded_by(path: Path, patterns: list[str]) -> str | None:
    relative = rel(path)
    for pattern in patterns:
        if fnmatch.fnmatch(relative, pattern):
            return pattern
    return None


def iter_include_candidates() -> list[Path]:
    candidates: list[Path] = []
    for root_name in INCLUDE_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        if root.is_file():
            candidates.append(root)
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                candidates.append(path)
    return sorted(set(candidates))


def build_plan(include_model_weights: bool) -> BundlePlan:
    patterns = active_excludes(include_model_weights)
    included: list[Path] = []
    excluded: list[tuple[Path, str]] = []
    for path in iter_include_candidates():
        pattern = excluded_by(path, patterns)
        if pattern:
            excluded.append((path, pattern))
        else:
            included.append(path)
    return BundlePlan(included=included, excluded=excluded)


def write_report(
    path: Path,
    *,
    timestamp: str,
    dry_run: bool,
    archive_path: Path,
    plan: BundlePlan,
    include_model_weights: bool,
) -> None:
    lines = [
        "# RunPod Training Bundle Report",
        "",
        f"- generated_at_utc: {timestamp}",
        f"- dry_run: {str(dry_run).lower()}",
        f"- archive_path: `{rel(archive_path)}`",
        f"- include_model_weights: {str(include_model_weights).lower()}",
        f"- included_file_count: {len(plan.included)}",
        f"- excluded_file_count: {len(plan.excluded)}",
        "",
        "## Included Paths",
        "",
    ]
    lines.extend(f"- `{rel(path)}`" for path in plan.included)
    lines.extend(["", "## Excluded Paths", ""])
    if plan.excluded:
        lines.extend(f"- `{rel(path)}` via `{pattern}`" for path, pattern in plan.excluded)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety Notes",
            "",
            "- `.env` files and `.env.*` files are excluded.",
            "- `RUNPOD_API_KEY` is not read and is not written into the bundle.",
            "- Model weights, GGUF files, cache folders, and previous runs are excluded unless `--include-model-weights` is passed.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_manifest(path: Path, *, timestamp: str, dry_run: bool, archive_path: Path, plan: BundlePlan) -> None:
    data = {
        "generated_at_utc": timestamp,
        "dry_run": dry_run,
        "archive_path": rel(archive_path),
        "included": [rel(path) for path in plan.included],
        "excluded": [{"path": rel(path), "pattern": pattern} for path, pattern in plan.excluded],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def create_archive(archive_path: Path, included: list[Path]) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as archive:
        for path in included:
            archive.add(path, arcname=rel(path))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir if args.output_dir.is_absolute() else REPO_ROOT / args.output_dir
    archive_path = output_dir / f"runpod_training_bundle_{timestamp}.tar.gz"
    manifest_path = output_dir / f"runpod_training_bundle_{timestamp}.manifest.json"
    plan = build_plan(args.include_model_weights)

    write_manifest(manifest_path, timestamp=timestamp, dry_run=args.dry_run, archive_path=archive_path, plan=plan)
    write_report(
        args.report if args.report.is_absolute() else REPO_ROOT / args.report,
        timestamp=timestamp,
        dry_run=args.dry_run,
        archive_path=archive_path,
        plan=plan,
        include_model_weights=args.include_model_weights,
    )

    if not args.dry_run:
        create_archive(archive_path, plan.included)

    print(f"Included files: {len(plan.included)}")
    print(f"Excluded files: {len(plan.excluded)}")
    print(f"Manifest: {rel(manifest_path)}")
    print(f"Report: {rel(args.report if args.report.is_absolute() else REPO_ROOT / args.report)}")
    if args.dry_run:
        print("Dry run only; no archive created.")
    else:
        print(f"Archive: {rel(archive_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
