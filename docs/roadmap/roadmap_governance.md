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
| `tool_evaluation_only` | Work evaluates external tools/references for future extraction strategy only; no tool execution or adapter implementation. |
| `no_tool_execution` | Must not install, clone, run, or demo external tools. |
| `no_source_retrieval_in_t001` | Parent publication micro-task records source policy only; official source retrieval is deferred to a later authorized child. |
| `no_rewrite` | Must not rewrite, revise, polish, or improve owner-authored story prose. |
| `no_continuation` | Must not continue, extend, or bridge owner-authored story prose. |
| `docs_only` | Work is limited to roadmap docs, status files, enrichment JSON, and validation records. |
| `evidence_first` | Source maps, source locators, evidence records, and provenance come before any extraction runtime. |
| `booknlp_ready` | BookNLP-like raw artifacts, manifest policy, and adapter normalization boundaries are decided before real BookNLP install or execution. |
| `mocked_fixtures_only` | BookNLP-like outputs are mocked fixture dictionaries only; no real BookNLP run or file output parsing. |
| `source_inventory_before_implementation` | A read-only official source inventory child must run before any adapter implementation. |
| `pure_validation` | Work is pure shape validation only; no filesystem I/O, no tool/package import, no model call. |
| `pure_normalization` | Work is pure mocked normalization only; no persistence writes, no candidate JSON writes, no memory/canon mutation. |
| `no_package_changes` | Must not change `package.json`, `requirements.txt`, or other dependency files. |
| `no_routes` | Must not add backend routes or API endpoints. |
| `no_frontend` | Must not add frontend UI components, pages, or client behavior. |
| `no_runtime_extraction` | Must not implement runtime extraction, extraction orchestrator, or raw output storage writes. |
| `docs_only_t001` | The T001 publication child is docs/status/planning only; it must not implement runtime code or tests. |
| `read_only_external_sources_only` | `.external_sources/` clones are inspected read-only; no clone, fetch, pull, install, run, import, vendor, or execute external repository code. |
| `raw_artifacts_non_canon` | Raw extraction artifacts (run folders, raw TSV/JSON/HTML outputs) are never approved truth, canon, project truth, memory/canon records, or OMI candidate records. |
| `raw_artifacts_non_candidate` | Raw extraction artifacts and parsed fixture output are raw support data only; they do not enter the OMI candidate pipeline and never become candidate records by default. |
| `fixture_parser_only` | BookNLP-like parsing is limited to mocked in-memory TSV/JSON fixture text; no real BookNLP output files are parsed from disk. |
| `storage_contract_first` | Project-local raw extraction artifact storage layout, run-folder naming, and path/manifest contracts are decided and tested before any extractor runtime exists. |
| `tests_first` | Future helpers are specified by expected-red contract tests before implementation. |
| `pure_path_helpers` | Helpers compute and validate safe storage paths and manifests only; they do not write, read, or list raw artifact files unless separately authorized. |
| `orchestration_contract` | Extraction sequencing, inputs, outputs, failure behavior, and handoff boundaries are decided by contract before runtime orchestration exists. |
| `review_safe_pipeline` | Extraction output must remain review-safe and owner-gated before any candidate persistence or approved truth handoff. |
| `in_memory_only` | Authorized helper behavior is limited to in-memory data structures and must not depend on project runtime files. |
| `standard_library_only` | Authorized implementation, if any, must use Python standard-library behavior only and must not add package dependencies. |
| `no_filesystem_io` | Authorized helper behavior must not read, write, list, or mutate filesystem content. |
| `owner_review_required` | Parser, adapter, orchestration, or candidate output requires explicit owner review before it can become approved truth. |
| `persistence_gate_planning` | The boundary for turning in-memory candidate drafts into persisted candidate records is decided and tested before any persistence helper exists. |
| `review_queue_planning` | The candidate review queue entry shape, lifecycle, and owner-action boundaries are decided before any review queue, route, or UI exists; the queue is a review surface, not an approval/canon queue. |
| `candidate_draft_support` | In-memory candidate drafts from the orchestrator are review support only and are not candidate records, canon, memory, owner decisions, or promotion. |
| `no_automatic_persistence` | Orchestrator or extraction output must not be automatically persisted as candidate records without an explicit owner-gated persistence boundary. |
| `queue_storage_planning` | Whether and how review queue entries are stored, listed, loaded, and prepared for future owner review is decided and tested before any queue storage helper, route, or UI exists; stored queue state is review workflow support only, never approval or canon truth. |
| `owner_action_workflow_planning` | Owner review action workflow states and commands are defined as planning terms only; owner actions are not apply-promotion, owner action storage is not memory/canon mutation, and review UI/API remains deferred. |

## Drift Handling

If a task ID has been reused incorrectly, treat that as numbering drift. Preserve the canonical task identity in `roadmap_index.yaml`, move the mistaken scope to the correct parent or child task, and record the correction in `implementation_status.md` or the relevant task record.
