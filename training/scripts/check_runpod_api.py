from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
REPORTS_DIR = REPO_ROOT / "training" / "reports"
API_URL = "https://api.runpod.io/graphql"
API_KEY_ENV_VAR = "RUNPOD_API_KEY"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check RunPod API connectivity without printing the API key."
    )
    parser.add_argument(
        "--list-pods",
        action="store_true",
        help="List current pod IDs/names/statuses after connectivity succeeds.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORTS_DIR / "runpod_api_check_report.md",
        help="Markdown report path.",
    )
    return parser.parse_args(argv)


def redact_key(value: str) -> str:
    if len(value) <= 8:
        return "<redacted>"
    return f"{value[:4]}...{value[-4:]}"


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_blocked_report(reason: str) -> None:
    write_report(
        REPORTS_DIR / "BLOCKED_runpod_api_not_configured.md",
        [
            "# BLOCKED: RunPod API Not Configured",
            "",
            f"- api_key_env_var: `{API_KEY_ENV_VAR}`",
            f"- status: {reason}",
            "",
            "Set `RUNPOD_API_KEY` in the shell before using RunPod API operations. "
            "Never commit or log the key value.",
        ],
    )


def run_graphql(api_key: str, query: str, timeout: float) -> dict[str, Any]:
    body = json.dumps({"query": query}).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "WritingAssistantApplication-training-check/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("RunPod response was not a JSON object.")
    return data


def pod_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    pods = data.get("data", {}).get("myself", {}).get("pods", [])
    return pods if isinstance(pods, list) else []


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    api_key = os.environ.get(API_KEY_ENV_VAR, "").strip()
    checked_at = datetime.now(timezone.utc).isoformat()

    if not api_key:
        reason = "missing"
        write_blocked_report(reason)
        print(f"RunPod API check blocked: {API_KEY_ENV_VAR} is not set.")
        print("Wrote training/reports/BLOCKED_runpod_api_not_configured.md")
        return 2

    query = "{ myself { id } }"
    if args.list_pods:
        query = "{ myself { id pods { id name machineId desiredStatus runtime { uptimeInSeconds } } } }"

    lines = [
        "# RunPod API Check Report",
        "",
        f"- checked_at_utc: {checked_at}",
        f"- api_key_env_var: `{API_KEY_ENV_VAR}`",
        f"- api_key_redacted: `{redact_key(api_key)}`",
        "- full_api_key_printed: false",
        "- endpoint: `https://api.runpod.io/graphql`",
    ]

    try:
        data = run_graphql(api_key, query, args.timeout)
    except urllib.error.HTTPError as exc:
        status = f"HTTP {exc.code}"
        lines.extend(["", f"- status: failed", f"- detail: {status}"])
        write_report(args.report, lines)
        print(f"RunPod API connectivity failed: {status}")
        print(f"Wrote {args.report}")
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        detail = f"{type(exc).__name__}: {exc}"
        lines.extend(["", "- status: failed", f"- detail: {detail}"])
        write_report(args.report, lines)
        print(f"RunPod API connectivity failed: {detail}")
        print(f"Wrote {args.report}")
        return 1

    errors = data.get("errors")
    if errors:
        lines.extend(["", "- status: failed", f"- detail: GraphQL errors returned: {errors!r}"])
        write_report(args.report, lines)
        print("RunPod API connectivity failed: GraphQL errors returned.")
        print(f"Wrote {args.report}")
        return 1

    lines.extend(["", "- status: connected"])
    if args.list_pods:
        pods = pod_rows(data)
        lines.extend(["", "## Current Pods", ""])
        if pods:
            for pod in pods:
                lines.append(
                    f"- id=`{pod.get('id')}` name=`{pod.get('name')}` "
                    f"desired_status=`{pod.get('desiredStatus')}` machine_id=`{pod.get('machineId')}`"
                )
        else:
            lines.append("- none returned")

    blocked_path = REPORTS_DIR / "BLOCKED_runpod_api_not_configured.md"
    blocked_path.unlink(missing_ok=True)
    write_report(args.report, lines)
    print("RunPod API connectivity: connected")
    print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
