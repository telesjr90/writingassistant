---
name: review-and-commit-docs
description: Use this skill when the user asks for commands to manually review and commit a documentation package. Do not commit automatically.
effort: medium
---

# Review and Commit Docs Skill

Do not commit automatically.

When the user asks for commit commands, provide commands only.

Use this structure:

```bash
cd /home/tjrpirateking/projects/WritingAssistantApplication

pwd
git status --short --branch
git log -5 --oneline
git diff --stat
git diff --name-only
git diff --check
```

Safety checks:

```bash
echo "Runtime file changes:"
git diff --name-only | grep -E '^(backend|frontend/src|frontend/package.json|frontend/package-lock.json|package.json|package-lock.json)' || true

echo "Test changes:"
git diff --name-only | grep -E '^tests/' || true

echo "Dataset/JSONL changes:"
git diff --name-only | grep -E 'training/data/dataset_manifest.json|training/data/|\.jsonl$|training/data/.+\.jsonl' || true

echo "Runtime project/memory/OMI files:"
git status --short | grep -E '^.. projects/|^.. .*/memory/|^.. .*/omi/' || true

echo "Ignored report status:"
git status --short --ignored training/reports/<report_name>.md || true
```

Then provide an explicit `git add` command listing only expected docs.

Then:

```bash
git status --short
git diff --cached --stat
git diff --cached --check
git commit -m "<message>"
git status --short --branch
git log -1 --oneline
```

Do not stage ignored local reports unless explicitly requested.
