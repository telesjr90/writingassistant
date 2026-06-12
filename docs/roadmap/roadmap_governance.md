# Roadmap Governance

## Control Layer

Roadmap execution is controlled by:

1. `docs/roadmap/roadmap_index.yaml`
2. `docs/roadmap/implementation_status.md`
3. `docs/roadmap/validation/latest_roadmap_validation.md`

GitHub Issues and GitHub Projects are not authoritative until a future sync task explicitly makes them part of the source hierarchy.

## ID Governance

- Parent implementation IDs are immutable after publication.
- Parent implementation IDs must match `PHASE[0-9]+-IMPL-[0-9]{3}`.
- Child micro-task IDs must match `PHASE[0-9]+-IMPL-[0-9]{3}-T[0-9]{3}`.
- Do not reuse a parent runtime ID for validation work.
- Do not renumber parent IDs to correct drift.
- Add child micro-tasks instead of changing a parent task identity.

## Boundary Tags

| Tag | Meaning |
| --- | --- |
| `owner_authored_prose_storage` | Stores or edits owner-authored prose without generating, rewriting, or improving prose. |
| `no_generated_prose` | Must not create story prose, summaries, continuations, rewrites, polish, or stylistic imitation. |
| `no_scene_rewrite` | Must not alter existing scene body text during metadata, routing, listing, or compatibility work. |
| `candidate_only` | Output remains a candidate or planning artifact and is not canon or project truth. |
| `no_memory_canon_mutation` | Must not create, edit, promote, or repair approved memory/canon records. |
| `no_model_calls` | Must not call Ollama, live models, extraction models, Story Check, or model-backed analysis. |
| `metadata_only` | Work is limited to metadata, indexes, registry records, or compatibility surfaces. |
| `validation` | Work validates behavior or documents manual checks. It does not add runtime feature scope. |
| `read_only` | Work may inspect or display existing state but must not mutate runtime project data. |
| `deferred` | Work is explicitly later and not part of the current micro-task. |
| `empty_states_only` | UI or docs may represent absent future data without creating or mutating that data. |
| `local_first` | Work operates on local project files and local app state, with no remote dependency by default. |
| `no_auto_promotion` | Candidates, model output, notes, or planning records must not become approved truth automatically. |
| `manual_smoke` | Human/browser validation belongs in checklist or validation tasks, not runtime implementation IDs. |
| `no_runtime_feature_scope` | Validation/documentation work must not add application features. |
| `owner_supplied_material` | Material is provided by the owner and must retain source/provenance/license distinction. |
| `read_only_overview` | Overview surfaces cheap metadata/status only and must not generate summaries or mutate project state. |

## Drift Handling

If a task ID has been reused incorrectly, treat that as numbering drift. Preserve the canonical task identity in `roadmap_index.yaml`, move the mistaken scope to the correct parent or child task, and record the correction in `implementation_status.md` or the relevant task record.

