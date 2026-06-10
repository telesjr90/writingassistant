#!/usr/bin/env bash
set -euo pipefail

cd /home/tjrpirateking/projects/WritingAssistantApplication

echo "Git state:"
git status --short --branch --untracked-files=all || true

echo
echo "Large tracked files:"
git ls-files | xargs -r du -h 2>/dev/null | sort -h | tail -30 || true

echo
echo "AI context files:"
ls -lh ai_context 2>/dev/null || true

echo
echo "Ignored/generated Prismo files:"
ls -la .prismo 2>/dev/null || true
ls -lh .claudeignore.prismo-suggested .cursorignore.prismo-suggested prismo-optimized-CLAUDE.template.md 2>/dev/null || true

echo
echo "Graphify outputs:"
ls -lh graphify-out 2>/dev/null || true
ls -lh graph.html GRAPH_REPORT.md graph.json 2>/dev/null || true

echo
echo "Repomix docs token tree:"
npx --yes repomix@latest --config repomix.workspace-docs.config.json --token-count-tree --dry-run || true

echo
echo "CCE status:"
cce status || true

echo
echo "Graphify status:"
if command -v graphify >/dev/null 2>&1; then
  graphify --help >/dev/null 2>&1 && echo "Graphify installed." || true
else
  echo "Graphify not found."
fi

echo
echo "LeanCTX status:"
if command -v lean-ctx >/dev/null 2>&1; then
  lean-ctx doctor || true
  lean-ctx gain || true
else
  echo "LeanCTX not found."
fi
