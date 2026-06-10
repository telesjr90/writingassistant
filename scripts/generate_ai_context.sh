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

  echo "Generating task-specific Repomix context for:"
  printf '  %s\n' "$@"

  printf '%s\n' "$@" | npx --yes repomix@latest --stdin --compress --token-count-tree --output ai_context/repomix-current-task-context.xml

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
