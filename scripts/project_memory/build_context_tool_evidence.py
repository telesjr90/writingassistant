#!/usr/bin/env python3
"""CLI for read-only existing context-tool evidence import."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.project_memory.context_tool_evidence import build_context_evidence_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Build existing context-tool evidence package.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = build_context_evidence_package(
            repo_root=args.repo_root,
            output_root=args.output_root,
            task_id=args.task_id,
            run_id=args.run_id,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "result": "BLOCKED"}, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Context-tool evidence package: {result['output_directory']}")
        print(f"Result: {result['result']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
