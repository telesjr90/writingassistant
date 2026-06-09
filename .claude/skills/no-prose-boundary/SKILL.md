---
name: no-prose-boundary
description: Use this skill whenever reviewing prompts, specs, routes, UI plans, OMI flows, memory/canon flows, extraction flows, or editor behavior for no-prose and candidate/canon safety.
effort: high
---

# No-Prose Boundary Skill

The project is analysis-only.

The AI must never:

* write story prose
* rewrite story prose
* continue story prose
* imitate style
* polish prose
* improve prose
* expand scenes
* generate dialogue
* generate chapters
* generate passages

Allowed:

* analyze owner-authored text
* ask diagnostic questions
* classify structure as candidate-only
* extract candidates with evidence/provenance
* store/edit owner-authored prose
* display owner-approved memory/canon after explicit promotion exists

Candidate/canon rules:

* Raw ideas are not canon.
* Candidates are not canon.
* Approved candidates are not applied memory/canon until explicit future apply-promotion runs.
* Promotion records are audit-only.
* Notes/materials are not canon or training data by default.
* Model output is never durable truth by default.
* Extraction output routes to OMI candidates only.
* No silent mutation of bible, storyform, scenes, notes, materials, project.json, OMI, memory/canon, or training data.

Review checklist:

1. Are any AI writing/rewrite/continue/polish/improve controls introduced?
2. Are owner-authored saves incorrectly treated as AI requests?
3. Are candidates visually or structurally blended into canon?
4. Are promotion records described as canon?
5. Is evidence/provenance required where needed?
6. Are model/Ollama calls hidden in workflows that should be deterministic/local?
7. Are training-data writes blocked by default?
8. Are future-only features clearly labeled?
9. Are warning/repair flows non-destructive?
10. Are Dramatica-specific features deferred unless explicitly requested?
