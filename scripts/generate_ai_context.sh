#!/usr/bin/env bash
set -euo pipefail

cd /home/tjrpirateking/projects/WritingAssistantApplication
mkdir -p ai_context

MODE="${1:-docs}"

if [ "$MODE" = "docs" ]; then
  echo "Generating docs-focused Repomix context..."
  npx --yes repomix@latest --config repomix.workspace-docs.config.json --compress --token-count-tree --output ai_context/repomix-workspace-docs-context.xml
  echo
  echo "Generated: ai_context/repomix-workspace-docs-context.xml"
  exit 0
fi

if [ "$MODE" = "full" ]; then
  echo "Generating full workspace Repomix context..."
  npx --yes repomix@latest --config repomix.config.json --compress --token-count-tree --output ai_context/repomix-workspace-context.xml
  echo
  echo "Generated: ai_context/repomix-workspace-context.xml"
  exit 0
fi

if [ "$MODE" = "task" ]; then
  shift || true

  if [ "$#" -eq 0 ]; then
    echo "ERROR: task mode requires file paths."
    echo "Example:"
    echo "  ./scripts/generate_ai_context.sh task docs/master_plan.md docs/plan.md docs/roadmap/task_backlog.md"
    exit 1
  fi

  TASK_STAGING_DIR=".tmp-ai-context-task-pack"
  TASK_OUTPUT_PATH="$PWD/ai_context/repomix-current-task-context.xml"

  rm -rf "$TASK_STAGING_DIR"
  rm -f "$TASK_OUTPUT_PATH"
  mkdir -p "$TASK_STAGING_DIR"

  cleanup_task_staging() {
    rm -rf "$TASK_STAGING_DIR"
  }
  trap cleanup_task_staging EXIT

  echo "Generating task-specific Repomix context for:"
  for requested_path in "$@"; do
    case "$requested_path" in
      /*)
        echo "ERROR: task mode requires relative file paths: $requested_path" >&2
        exit 1
        ;;
      *..*)
        echo "ERROR: task mode rejects paths containing '..': $requested_path" >&2
        exit 1
        ;;
    esac

    if [ ! -f "$requested_path" ]; then
      echo "ERROR: task mode file does not exist: $requested_path" >&2
      exit 1
    fi

    mkdir -p "$TASK_STAGING_DIR/$(dirname "$requested_path")"
    cp "$requested_path" "$TASK_STAGING_DIR/$requested_path"
    printf '  %s\n' "$requested_path"
  done

  (
    cd "$TASK_STAGING_DIR"
    npx --yes repomix@latest . --compress --token-count-tree --output "$TASK_OUTPUT_PATH"
  )

  python3 - "$TASK_OUTPUT_PATH" "$@" <<'PY'
import re
import sys
from pathlib import Path

output_path = Path(sys.argv[1])
requested = set(sys.argv[2:])
text = output_path.read_text(encoding="utf-8", errors="ignore")

path_pattern = re.compile(
    r"\b(?:backend|frontend|tests|docs|scripts)/"
    r"[A-Za-z0-9._/\-]+\.(?:py|jsx|js|ts|tsx|md|json|yaml|yml|sh)\b"
)


def normalize_unpacked_reference(match: re.Match[str]) -> str:
    value = match.group(0)
    if value in requested:
        return value
    return value.replace("/", "&#47;")


output_path.write_text(
    path_pattern.sub(normalize_unpacked_reference, text),
    encoding="utf-8",
)
PY

  echo
  echo "Generated: ai_context/repomix-current-task-context.xml"
  exit 0
fi

echo "Unknown mode: $MODE"
echo "Valid modes:"
echo "  docs"
echo "  full"
echo "  task <file1> <file2> ..."
exit 1
