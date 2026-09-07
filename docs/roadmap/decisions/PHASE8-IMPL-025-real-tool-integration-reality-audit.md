# PHASE8-IMPL-025 Real Tool Integration Reality Audit

Date: 2026-09-07

## Result

`PASS_AUDIT_READY_FOR_SUPERVISOR_REVIEW` for the documentation-only reality
audit and roadmap reconciliation.

No accepted evidence proves successful real external-tool execution through
the complete PHASE8-IMPL-025 T002/T003 layered path. Historical real execution
remains valid foundation evidence for spaCy, BookNLP after compatibility
repair, Ollama/qwen3:8b, Story Check through the actual analysis-engine/Ollama
path, and owner-selected NCP import. Those runs predate the T002/T003 layered
control plane and do not satisfy current-layer completion.

## Completion rule

External integrations use:

```text
CONTRACT -> REAL APPLICATION ADAPTER -> REAL TOOL EXECUTION
```

NCP-style gateways substitute real supported-interface/schema
interoperability and round-trip execution for the third stage. Mocks and
fixtures remain necessary regression evidence but are insufficient completion
evidence. Accepted implementation milestones remain valid even when an
overall integration stays open.

## Evidence matrix

| Tool identity | Role / kind | Contract implemented? | Contract evidence | Production adapter implemented? | Adapter evidence | Concrete real external edge | Historical real execution | Current layered path reaches real edge? | Real execution through current layered path proven? | Mock / fixture evidence | Provenance / version / provider / model evidence | Current-machine availability from existing evidence | Completion under owner gate | Exact missing stage | Exact next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `spacy` | External local NLP runtime; source-evidence producer | Yes | OMI local-NLP envelope and T003 source-evidence operation contract | Yes | `_build_spacy_live_runner`; resolver flag branch | `spacy.load(model)` then `nlp(raw_text)` | Yes; PHASE8-IMPL-023-T014D | Conditionally yes through T003's default OMI runner and live flags | No accepted post-T003 real run | Yes | Historical installed runtime/model evidence; T003 may otherwise record unknown version fields | Not re-probed; existing availability evidence is historical | `HISTORICAL_REAL_EXECUTION_CURRENT_LAYERED_REAL_EXECUTION_UNPROVEN` | Current source/hash-to-manifest/artifact/ledger real run | Perform one bounded real T003-layered spaCy run and verify required downstream handoffs |
| `booknlp` | External local NLP runtime; raw/source-evidence producer | Yes, including T004 raw-artifact handoff | `booknlp_adapter_contract.py`, T004 parser/mapping contracts, T003 operation | Yes | Expanded `_build_booknlp_live_runner` and T004 handoff consumed by T003 | `BookNLP("en", params).process(...)` | Yes; T017C reached runtime and T017C1 repaired rerun produced real findings | Conditionally yes through T003 and the T004 raw-artifact handoff | No real run proven after expanded T004/T003 integration | Yes; expanded T004 suites use mocked/generated runtime output | Historical BookNLP 1.0.8/runtime/model evidence | Not re-probed; existing availability evidence is historical | `HISTORICAL_REAL_EXECUTION_CURRENT_LAYERED_REAL_EXECUTION_UNPROVEN` | T004G real expanded output plus layered artifact/ledger/fusion/candidate validation | Run real expanded BookNLP through T002 source identity, T003 artifacts/ledger, T004 mappings, fusion, and candidates; keep T004 implementation commit accepted |
| `ollama_model` / `qwen3:8b` | External model runtime; exact-source structured extractor and future evidence consumer | Yes | OMI structured extraction contract and T003 operation | Yes | `_build_ollama_model_live_runner`; resolver flag branch | HTTP POST to Ollama `/api/chat` | Yes; T015D/T015F | Conditionally yes through T003's default OMI runner and live flags | No accepted post-T003 real run | Yes | Historical Ollama/qwen3:8b service/model evidence | Current service not re-probed; existing availability evidence is historical | `HISTORICAL_REAL_EXECUTION_CURRENT_LAYERED_REAL_EXECUTION_UNPROVEN` | T007 current exact-source/hash/manifest/ledger execution | T007E must run qwen3:8b through the current layered path and retain native/model provenance |
| `story_check` | External/model-backed grounded diagnostic consumer | Yes | Story Check envelope, grounding contract, and T003 operation | Yes | `_build_story_check_live_runner` | `analysis_engine.run_story_check` -> `requests.post` to Ollama `/api/chat` | Yes; T016D and later grounding evidence | Conditionally yes when T003/OMI receives valid project and scene context plus live flags | No accepted post-T003 real run | Yes | Historical analysis-engine/Ollama provider/model evidence | Current service not re-probed; existing availability evidence is historical | `HISTORICAL_REAL_EXECUTION_CURRENT_LAYERED_REAL_EXECUTION_UNPROVEN` | T007 current exact source/context and layered execution | T007E must prove real Story Check through source hash, manifest, artifacts, ledger, grounding, and quarantine semantics |
| `subtxt` | Official external runtime; normalized-evidence consumer | Yes | T005 runtime inventory/request/result/provenance contracts | Yes, application side only | T006 `run_official_subtxt_adapter` and persistence helpers at commit `23d4825...` | None in production; external invocation is an injected `runner(...)` seam | None | No; T003 supplies no normalized-evidence dependency and does not call the T006 adapter | No | Yes; deterministic mocked runner, persistence, and grouped-review tests | Runtime/provider/model unknown | T006G `NOT_EXECUTED_RUNTIME_UNAVAILABLE`; T006K found zero verified available surfaces | `CONTRACT_AND_ADAPTER_NO_REAL_EXECUTION` + `RUNTIME_UNAVAILABLE` | Verified production runner, T003 connection, and real execution | Keep T006 active/open; establish a supported official surface, implement the concrete runner in a later authorized task, connect T003, and perform bounded real execution |
| `subtxt_informed_rubric` | App-owned public diagnostic rubric adapter | Yes | T019C request/result contract | Yes | Built-in `_build_subtxt_informed_rubric_runner` | App-owned evaluator only; no external edge | Accepted owner-source in-process T019F run | Reachable as an app-owned T003 contributor | Not applicable as external proof | Yes | Explicit app-owned identity; no external provider/model/runtime | Available as committed app-owned code; external availability not applicable | `APP_OWNED_INTERNAL_IMPLEMENTATION` | None for its app-owned scope | Preserve labeling and never count it as official Subtxt execution |
| `app_owned_subtxt_informed_rubric` | Internal evaluator identity behind the public rubric adapter | Yes | T019C/T019D | Not a separate external adapter; wrapped by `subtxt_informed_rubric` | T019D evaluator | Pure in-memory evaluator | Exercised through accepted app-owned validation | Indirectly through the public adapter | Not applicable as external proof | Yes | Internal provenance only | Available as committed app-owned code; external availability not applicable | `APP_OWNED_INTERNAL_IMPLEMENTATION` | None for its internal scope | Keep distinct from both `subtxt` and the public adapter identity |
| `dramatica_flow_informed_rubric` | App-owned diagnostic rubric adapter | Yes | T020C contract | Yes | Built-in `_build_dramatica_flow_informed_rubric_runner` and T020D evaluator | App-owned evaluator only; no external edge | Accepted owner-source in-process T020F run | Reachable as an app-owned T003 contributor | Not applicable as external proof | Yes | Explicit app-owned identity; no external runtime/model | Available as committed app-owned code; external availability not applicable | `APP_OWNED_INTERNAL_IMPLEMENTATION` | None for its app-owned scope | Never use it as evidence of external dramatica-flow execution |
| `dramatica_flow` | External/reference integration; normalized-evidence consumer | Fixture handoff only; no authorized live-runtime contract | T009 fixture contract and T020A/T020B reference evidence | No live production adapter | Resolver supports fixtures only; preflight hard-false live availability | None | None | No; T003 withholds normalized evidence and authorized runtime | No | Yes, fixture-only | Installed/reference signals exist; T020B keeps runtime owner-blocked/reference-only | Unavailable by current authority; not re-probed or executed | `AUTHORITATIVE_CONFLICT_REQUIRES_OWNER_DECISION` and `EXTERNAL_RUNTIME_BLOCKED_BY_CURRENT_AUTHORITY` | Owner reconciliation of MVP scope and runtime authority | `OWNER_DECISION_REQUIRED_BEFORE_EXTERNAL_DRAMATICA_FLOW_IMPLEMENTATION`; do not implement or execute before that decision |
| `ncp` | External artifact/schema gateway | Partial import contract; full T010 gateway absent | T009 handoff and T018 import validation; T010 planned contract | Legacy import adapter yes; full gateway no | `_build_ncp_live_runner`; T003 declares gateway role but supplies no imported artifact | Owner-selected JSON read; optional bounded supported validator subprocess | Yes; T018C/T018C1 rerun import and supported file validation | No supported successful layered gateway path; T003 raw-source request lacks imported-artifact input and rejects producing output | No | Yes | Historical NCP schema 1.2.0/import provenance | Current source/validator not re-probed; availability evidence is historical | `HISTORICAL_REAL_EXECUTION_CURRENT_LAYERED_REAL_EXECUTION_UNPROVEN`; `REAL_INTEROPERABILITY_PROVEN` absent | Full current-layer import/export/validation/round trip | T010 must implement immutable import, explicit mapping, provenance, import, export, validation, and real supported-schema round trip |
| `deterministic_fallback` | Internal fallback/safety baseline | Yes | OMI fallback contract | Yes, internal wrapper | `_deterministic_fallback_findings` -> project-manager marker extractor | None external | Internal deterministic execution only | Yes when explicitly allowed | Not external proof | Yes | App-owned deterministic version identity | Available as committed internal code; external availability not applicable | `INTERNAL_FALLBACK_NOT_EXTERNAL_TOOL` | No external stage applies | Retain fallback labeling; never count it toward external integration completion |

No other current runtime/tool identity was found in the inspected
`project_manager`, `analysis_run_control`, OMI orchestrator, preflight, or
adapter registries. Evidence ledger, manifests, fusion, persistence, review,
and guardrails are application pipeline components, not external tools.

## Trace conclusions

For spaCy, BookNLP, Ollama, and Story Check, T003 constructs the exact source
snapshot/hash and calls `analyze_omi_raw_idea_with_tools`, whose resolver can
still reach the concrete historical live runners behind explicit flags. T003
then builds the run manifest, immutable artifact bundle, and evidence ledger.
The chain stops at proof: no accepted bounded real execution after T002/T003
was found. T003 itself does not persist candidates or complete grouped review.

For NCP, Subtxt, and external dramatica-flow, T003 declares imported-artifact
or normalized-evidence dependencies but `_enforce_t001_control_plane_inputs`
records those inputs as unprovided and removes producing results. The legacy
NCP runner can be conditionally invoked from environment configuration before
that enforcement, but that is not a supported successful T003 gateway chain.
Official Subtxt is separate: its T006 adapter exists in
`analysis_runtime_integration.py`, but T003 does not invoke it and production
code supplies no concrete external runner. External dramatica-flow has neither
an authorized live contract nor a live resolution branch.

The app-owned rubrics run in process and normalize candidate-first diagnostic
support. Their chains contain no external runtime edge. Deterministic fallback
is likewise internal.

## Roadmap reconciliation

- T003 remains complete/PASS for its accepted application control-plane and
  persistence milestone.
- T004 implementation commit `ca2f99f...` remains accepted; overall T004
  real-tool completion is open pending real expanded BookNLP layered proof.
- T005 remains complete/PASS.
- T006 implementation commit `23d4825...` and mocked validation remain
  accepted; overall T006 is active/open pending a real official runtime runner
  and current-layer execution. T006 is the immediate execution frontier.
- T007 and T008 remain planned/not begun.
- T007E, T008, T010, and T012 carry the strengthened real-execution gates from
  the 2026-09-07 owner decision.
- External dramatica-flow requires an owner decision before any implementation
  or execution and does not block reconciliation of other integrations.

## Audit boundary

This audit changed documentation only. It did not implement adapters, execute
application code or tests, call any external runtime/model/service/schema
validator, begin T007, mutate candidates or Memory/Canon, or stage/commit/push.
