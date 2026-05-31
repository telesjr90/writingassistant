from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
TRAINING_DIR = REPO_ROOT / "training"
EXTERNAL_DIR = TRAINING_DIR / "data" / "external"
METADATA_DIR = EXTERNAL_DIR / "metadata"
SAMPLES_DIR = EXTERNAL_DIR / "samples"
DEFAULT_CONFIG = TRAINING_DIR / "configs" / "external_dataset_sources.yaml"

MAX_METADATA_BYTES = 500_000
MAX_ARTICLE_BYTES = 160_000
MAX_SAMPLE_RECORDS_HARD_LIMIT = 150
USER_AGENT = "WritingAssistantExternalDatasetRetriever/1.0"

LICENSE_PATTERNS = [
    (re.compile(r"\bMIT\b", re.IGNORECASE), "MIT"),
    (re.compile(r"\bApache(?: License)?,?\s*(?:Version\s*)?2(?:\.0)?\b", re.IGNORECASE), "Apache-2.0"),
    (re.compile(r"\bBSD[- ]?3[- ]?Clause\b", re.IGNORECASE), "BSD-3-Clause"),
    (re.compile(r"\bCC\s*BY[- ]SA\s*4\.0\b|Attribution[- ]ShareAlike\s*4\.0", re.IGNORECASE), "CC BY-SA 4.0"),
    (re.compile(r"\bCC\s*BY\s*4\.0\b|Attribution\s*4\.0\s*International", re.IGNORECASE), "CC BY 4.0"),
    (re.compile(r"\bCC0\s*1\.0\b|Creative Commons Zero", re.IGNORECASE), "CC0 1.0"),
]

LICENSE_ALIASES = {
    "mit": "MIT",
    "apache-2.0": "Apache-2.0",
    "apache 2.0": "Apache-2.0",
    "bsd-3-clause": "BSD-3-Clause",
    "bsd 3 clause": "BSD-3-Clause",
    "cc-by-4.0": "CC BY 4.0",
    "cc by 4.0": "CC BY 4.0",
    "cc-by-sa-4.0": "CC BY-SA 4.0",
    "cc by-sa 4.0": "CC BY-SA 4.0",
    "cc0-1.0": "CC0 1.0",
    "cc0 1.0": "CC0 1.0",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrieve safe metadata and small samples for Phase 2 external dataset candidates."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to training/configs/external_dataset_sources.yaml.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Retrieve metadata manifests only; do not write samples.",
    )
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="Retrieve safe small samples only; still writes a manifest recording the sample attempt.",
    )
    parser.add_argument("--dataset-id", help="Limit retrieval to one dataset id from the config.")
    parser.add_argument("--all", action="store_true", help="Process all configured datasets.")
    parser.add_argument(
        "--max-sample-records",
        type=int,
        default=25,
        help="Maximum sample records to write. Hard-capped at 150.",
    )
    parser.add_argument(
        "--allow-large-download",
        action="store_true",
        help="Allow explicitly configured large downloads. This script still skips unclear-provenance fiction by default.",
    )
    return parser.parse_args(argv)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_workspace_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def ensure_dirs() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def load_config(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("datasets"), list):
        raise ValueError(f"{path} must contain a top-level datasets list")
    entries = data["datasets"]
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ValueError("Each dataset entry must be a mapping with an id")
    return entries


def select_entries(entries: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.metadata_only and args.sample_only:
        raise ValueError("--metadata-only and --sample-only cannot be used together")
    if not args.all and not args.dataset_id:
        raise ValueError("Use --all or --dataset-id DATASET_ID")
    if args.all:
        if args.dataset_id:
            return [entry for entry in entries if entry["id"] == args.dataset_id]
        return entries
    selected = [entry for entry in entries if entry["id"] == args.dataset_id]
    if not selected:
        raise ValueError(f"Unknown dataset id: {args.dataset_id}")
    return selected


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def find_licenses(text: str) -> list[str]:
    found: list[str] = []
    for pattern, label in LICENSE_PATTERNS:
        if pattern.search(text) and label not in found:
            found.append(label)
    return found


def normalize_license_value(value: Any) -> str | None:
    if isinstance(value, list):
        for item in value:
            normalized = normalize_license_value(item)
            if normalized:
                return normalized
        return None
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    return LICENSE_ALIASES.get(value.lower(), value)


def fetch_limited_text(url: str, max_bytes: int) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=25) as response:
            raw = response.read(max_bytes + 1)
            content_type = response.headers.get("content-type", "")
            status = getattr(response, "status", 200)
    except HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code, "error": str(exc)}
    except (OSError, URLError) as exc:
        return {"url": url, "ok": False, "status": None, "error": str(exc)}

    truncated = len(raw) > max_bytes
    raw = raw[:max_bytes]
    text = raw.decode("utf-8", errors="replace")
    return {
        "url": url,
        "ok": True,
        "status": status,
        "content_type": content_type,
        "bytes_read": len(raw),
        "truncated": truncated,
        "text": text,
        "sha256": sha256_text(text),
    }


def html_title(text: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()


def html_meta_description(text: str) -> str | None:
    match = re.search(
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)["\']',
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()


def extract_links(text: str, limit: int = 30) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r'href=["\']([^"\']+)["\']', text, flags=re.IGNORECASE):
        link = html.unescape(match.group(1))
        if link.startswith(("http://", "https://")) and link not in links:
            links.append(link)
        if len(links) >= limit:
            break
    return links


def summarize_fetched_document(url: str, fetched: dict[str, Any], preserve_excerpt: bool) -> dict[str, Any]:
    summary = {
        "url": url,
        "ok": fetched.get("ok", False),
        "status": fetched.get("status"),
        "error": fetched.get("error"),
    }
    if not fetched.get("ok"):
        return summary

    text = str(fetched.get("text", ""))
    content_type = str(fetched.get("content_type", ""))
    summary.update(
        {
            "content_type": content_type,
            "bytes_read": fetched.get("bytes_read"),
            "truncated": fetched.get("truncated"),
            "sha256": fetched.get("sha256"),
            "license_candidates": find_licenses(text),
        }
    )
    if "html" in content_type or "<html" in text[:500].lower():
        summary.update(
            {
                "title": html_title(text),
                "description": html_meta_description(text),
                "links_discovered": extract_links(text),
            }
        )
    elif preserve_excerpt:
        summary["text_excerpt"] = text[:8_000]
    else:
        summary["text_excerpt"] = text[:1_000]
    return summary


def metadata_urls_for(entry: dict[str, Any]) -> list[str]:
    configured = entry.get("metadata_urls")
    if isinstance(configured, list) and configured:
        return [str(url) for url in configured]
    urls = [str(entry["primary_url"])]
    urls.extend(str(url) for url in entry.get("secondary_urls", []))
    return urls


def retrieve_hf_metadata(entry: dict[str, Any], manifest: dict[str, Any]) -> None:
    repo_id = entry.get("hf_repo_id")
    if not repo_id:
        parsed = urlparse(str(entry.get("primary_url", "")))
        path = parsed.path.strip("/")
        if path.startswith("datasets/"):
            repo_id = path.removeprefix("datasets/")
    if not repo_id:
        manifest["warnings"].append("No Hugging Face repo id configured.")
        return

    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError as exc:
        manifest["errors"].append(f"huggingface_hub unavailable: {exc}")
        return

    try:
        info = HfApi().dataset_info(str(repo_id))
        siblings = [s.rfilename for s in (info.siblings or [])]
        card_data = getattr(info, "card_data", None)
        card_data_dict = card_data.to_dict() if hasattr(card_data, "to_dict") else card_data
        tags = list(getattr(info, "tags", None) or [])
        manifest["huggingface"] = {
            "repo_id": repo_id,
            "sha": getattr(info, "sha", None),
            "tags": tags,
            "card_data": card_data_dict if isinstance(card_data_dict, dict) else None,
            "siblings_count": len(siblings),
            "sample_siblings": siblings[:30],
        }
        manifest["urls_accessed"].append(f"hf://datasets/{repo_id}")
        license_from_card = None
        if isinstance(card_data_dict, dict):
            license_from_card = card_data_dict.get("license")
        if not license_from_card:
            for tag in tags:
                if str(tag).startswith("license:"):
                    license_from_card = str(tag).split(":", 1)[1]
                    break
        normalized_license = normalize_license_value(license_from_card)
        if normalized_license:
            manifest["license_sources"].append(
                {"source": f"hf://datasets/{repo_id}", "license": normalized_license}
            )
    except Exception as exc:  # pragma: no cover - network/library variability
        manifest["errors"].append(f"HF dataset_info failed for {repo_id}: {exc}")

    try:
        readme_path = hf_hub_download(repo_id=str(repo_id), repo_type="dataset", filename="README.md")
        readme = Path(readme_path).read_text(encoding="utf-8", errors="replace")
        manifest["retrieved_metadata"].append(
            {
                "url": f"hf://datasets/{repo_id}/README.md",
                "ok": True,
                "sha256": sha256_text(readme),
                "bytes_read": len(readme.encode("utf-8", errors="replace")),
                "license_candidates": find_licenses(readme),
                "text_excerpt": readme[:8_000],
            }
        )
        manifest["urls_accessed"].append(f"hf://datasets/{repo_id}/README.md")
    except Exception as exc:  # pragma: no cover - network/library variability
        manifest["warnings"].append(f"HF README retrieval failed for {repo_id}: {exc}")


def retrieve_http_metadata(entry: dict[str, Any], manifest: dict[str, Any]) -> None:
    for url in metadata_urls_for(entry):
        max_bytes = MAX_ARTICLE_BYTES if "articles/" in url or "doi.org" in url else MAX_METADATA_BYTES
        fetched = fetch_limited_text(url, max_bytes=max_bytes)
        manifest["urls_accessed"].append(url)
        preserve_excerpt = "raw.githubusercontent.com" in url or url.endswith((".md", ".txt", ".csv"))
        manifest["retrieved_metadata"].append(summarize_fetched_document(url, fetched, preserve_excerpt))


def choose_license(manifest: dict[str, Any], expected_license: str) -> str | None:
    candidates: list[str] = []
    for source in manifest.get("license_sources", []):
        license_value = normalize_license_value(source.get("license"))
        if license_value and license_value not in candidates:
            candidates.append(license_value)
    for item in manifest.get("retrieved_metadata", []):
        for license_value in item.get("license_candidates", []) or []:
            if license_value not in candidates:
                candidates.append(license_value)
    if candidates:
        return candidates[0]
    if "not found" in expected_license.lower() or "pending" in expected_license.lower():
        return None
    return expected_license


def should_skip_sample(entry: dict[str, Any], allow_large_download: bool) -> str | None:
    if not entry.get("safe_sample", False):
        return f"sample_policy={entry.get('sample_policy', 'unspecified')} is not marked safe"
    if entry.get("recommended_status") in {"reject", "reject_pending_license_review"}:
        return f"recommended_status={entry.get('recommended_status')} blocks sampling"
    if entry.get("requires_large_download") and not allow_large_download:
        return "large download requires --allow-large-download"
    return None


def row_id(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    row_id_value = value.get("ID") or value.get("id")
    return str(row_id_value) if isinstance(row_id_value, str) and row_id_value else None


def stream_hf_jsonl_head(entry: dict[str, Any], sample_path: Path, max_records: int) -> dict[str, Any]:
    try:
        from huggingface_hub import HfFileSystem
    except ImportError as exc:
        return {"ok": False, "error": f"huggingface_hub unavailable: {exc}"}

    repo_id = str(entry["hf_repo_id"])
    source_path = str(entry["sample_source_path"])
    hf_path = f"datasets/{repo_id}/{source_path}"
    records_written = 0
    seen_ids: set[str] = set()
    sample_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fs = HfFileSystem()
        with fs.open(hf_path, "r", encoding="utf-8") as source, sample_path.open(
            "w", encoding="utf-8"
        ) as target:
            for line in source:
                if not line.strip():
                    continue
                value = json.loads(line)
                current_id = row_id(value)
                if current_id and current_id in seen_ids:
                    continue
                if current_id:
                    seen_ids.add(current_id)
                target.write(json.dumps(value, ensure_ascii=False, sort_keys=False))
                target.write("\n")
                records_written += 1
                if records_written >= max_records:
                    break
    except Exception as exc:  # pragma: no cover - network/library variability
        return {"ok": False, "error": str(exc), "source": f"hf://{hf_path}"}

    return {
        "ok": True,
        "source": f"hf://{hf_path}",
        "local_path": relative_path(sample_path),
        "records_written": records_written,
    }


def sample_output_path(entry: dict[str, Any], max_records: int) -> Path:
    configured_path = resolve_workspace_path(
        entry.get("local_sample_path"),
        SAMPLES_DIR / f"{entry['id']}_sample.jsonl",
    )
    if max_records <= 25:
        return configured_path
    return configured_path.with_name(f"{configured_path.stem}_{max_records}{configured_path.suffix}")


def write_sample(entry: dict[str, Any], args: argparse.Namespace, manifest: dict[str, Any]) -> None:
    max_records = max(0, min(args.max_sample_records, MAX_SAMPLE_RECORDS_HARD_LIMIT))
    sample_path = sample_output_path(entry, max_records)
    skip_reason = should_skip_sample(entry, args.allow_large_download)
    manifest["sample"] = {
        "attempted": skip_reason is None,
        "local_path": relative_path(sample_path),
        "max_records": max_records,
        "records_written": 0,
        "skipped": skip_reason is not None,
        "skip_reason": skip_reason,
    }
    if skip_reason:
        return
    if max_records <= 0:
        manifest["sample"].update({"skipped": True, "skip_reason": "max sample records was 0"})
        return

    policy = entry.get("sample_policy")
    if policy == "huggingface_jsonl_head":
        result = stream_hf_jsonl_head(entry, sample_path, max_records)
    else:
        result = {"ok": False, "error": f"No sampler implemented for sample_policy={policy!r}"}

    if result.get("ok"):
        manifest["sample"].update(
            {
                "skipped": False,
                "source": result.get("source"),
                "records_written": result.get("records_written", 0),
            }
        )
        if result.get("source"):
            manifest["urls_accessed"].append(str(result["source"]))
    else:
        manifest["sample"].update({"skipped": True, "skip_reason": result.get("error")})
        manifest["errors"].append(f"Sample retrieval failed: {result.get('error')}")


def read_existing_manifest(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def new_manifest(entry: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    metadata_path = resolve_workspace_path(
        entry.get("local_metadata_path"),
        METADATA_DIR / f"{entry['id']}_manifest.json",
    )
    sample_path = resolve_workspace_path(
        entry.get("local_sample_path"),
        SAMPLES_DIR / f"{entry['id']}_sample.jsonl",
    )
    return {
        "dataset_id": entry["id"],
        "name": entry["name"],
        "retrieved_at_utc": utc_now(),
        "retriever": relative_path(Path(__file__).resolve()),
        "source_url": entry["primary_url"],
        "secondary_urls": entry.get("secondary_urls", []),
        "source_type": entry.get("source_type"),
        "expected_license": entry.get("expected_license"),
        "license_found": None,
        "license_sources": [],
        "expected_size": entry.get("expected_size"),
        "recommended_status": entry.get("recommended_status"),
        "intended_mapping": entry.get("intended_mapping", []),
        "cautions": entry.get("cautions", []),
        "retrieval_method": entry.get("retrieval_method"),
        "local_metadata_path": relative_path(metadata_path),
        "local_sample_path": relative_path(sample_path),
        "metadata_retrieval_skipped": args.sample_only,
        "sample_retrieval_skipped": args.metadata_only,
        "full_download_skipped": True,
        "full_download_skip_reason": (
            "Full corpus downloads are out of scope for this metadata/sample retriever."
            if args.allow_large_download
            else "Full corpus downloads require --allow-large-download and explicit per-dataset implementation."
        ),
        "urls_accessed": [],
        "retrieved_metadata": [],
        "warnings": [],
        "errors": [],
    }


def retrieve_entry(entry: dict[str, Any], args: argparse.Namespace) -> Path:
    metadata_path = resolve_workspace_path(
        entry.get("local_metadata_path"),
        METADATA_DIR / f"{entry['id']}_manifest.json",
    )
    existing_manifest = read_existing_manifest(metadata_path) if args.sample_only else None
    manifest = existing_manifest if existing_manifest is not None else new_manifest(entry, args)
    manifest["retrieved_at_utc"] = utc_now()
    manifest.setdefault("retrieval_history", []).append(
        {
            "retrieved_at_utc": manifest["retrieved_at_utc"],
            "mode": "sample-only"
            if args.sample_only
            else "metadata-only"
            if args.metadata_only
            else "metadata-and-sample",
        }
    )
    if args.sample_only:
        manifest["sample_retrieval_skipped"] = False
        manifest["metadata_retrieval_skipped"] = existing_manifest is None

    if not args.sample_only:
        manifest["retrieved_metadata"] = []
        manifest["license_sources"] = []
        manifest["urls_accessed"] = []
        if "huggingface" in str(entry.get("source_type", "")) or entry.get("hf_repo_id"):
            retrieve_hf_metadata(entry, manifest)
        retrieve_http_metadata(entry, manifest)
        manifest["license_found"] = choose_license(manifest, str(entry.get("expected_license", "")))

    if not args.metadata_only:
        write_sample(entry, args, manifest)
        if manifest["license_found"] is None:
            manifest["license_found"] = choose_license(manifest, str(entry.get("expected_license", "")))

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return metadata_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        entries = select_entries(load_config(args.config), args)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"retrieve_external_datasets.py: error: {exc}", file=sys.stderr)
        return 2

    ensure_dirs()
    written: list[Path] = []
    for entry in entries:
        path = retrieve_entry(entry, args)
        written.append(path)
        print(f"Wrote {relative_path(path)}")

    print(f"Processed {len(written)} dataset source(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
