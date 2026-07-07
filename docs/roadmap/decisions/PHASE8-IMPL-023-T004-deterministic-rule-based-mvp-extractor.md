# PHASE8-IMPL-023-T004 Deterministic Rule-Based MVP Extractor

- Result: PASS for backend deterministic marker extraction.
- Scope: backend only; no frontend API helper, OMI UI, browser harness, model-assisted extraction, NLP dependency, or story prose generation was added.
- Implementation: `project_manager.extract_omi_candidates_from_raw_idea` now detects explicit owner-authored raw idea markers for `Character:`, `Location:`, `Organization:`, `Object:`, `Timeline event:`, `Relationship:`, `Plot thread:`, `Story fact:`, `Open question:`, and `Storyform context:`.
- Candidate output: supported markers produce evidence-backed extracted candidates with `candidate_type`, `label` and entity `name` where applicable, owner-authored `extracted_claim`, source excerpt, source locator, line number, character offsets, deterministic provenance, pending owner decision, candidate-review status, and support-strength metadata labeled as support only.
- Empty/unsupported behavior: empty raw idea returns `empty`; non-empty raw idea with no supported evidence markers returns `fail_closed` with explanation and no candidates.
- Persistence behavior: when `persist_candidates=true` and a source OMI idea is present, evidence-backed extracted candidates are persisted through the existing OMI candidate queue as candidate-first records with pending owner decision and `promotion_status.eligible=false`; persisted records are not canon and not approved.
- Safety boundaries: no Memory/Canon mutation, no promotion records, no apply-promotion, no model/Ollama/Story Check/BookNLP/spaCy/NCP/Subtxt/dramatica-flow/external-service calls, no training artifacts, and no generated story prose.
- Backend expected-red turned green: `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_expected_red.py -q` -> `4 passed in 0.24s`.
- Contract validation: `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_contract.py -q` -> `5 passed in 0.27s`.
- Existing OMI regressions: `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_routes.py -q` -> `20 passed in 0.34s`; `.venv-unsloth-clean/bin/python -m pytest tests/test_project_manager.py -q -k omi` -> `18 passed, 51 deselected in 0.22s`; `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_boundaries.py -q` -> `21 passed in 0.36s`; `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_manual_workflow_source.py -q` -> `7 passed in 0.05s`.
- Frontend/source expected-red remains deferred: `.venv-unsloth-clean/bin/python -m pytest tests/test_omi_extraction_ui_source_expected_red.py -q` -> `5 failed, 1 passed in 0.06s`, limited to missing T006 frontend API/UI/detail/empty-state surfaces.
- Roadmap validation: `python3 scripts/check_enrichment.py` -> PASS; `python3 scripts/validate_roadmap.py` -> PASS; `python3 -m json.tool docs/roadmap/enrichment/PHASE8-IMPL-023.enrichment.json >/dev/null` -> PASS.
- Next child task: `PHASE8-IMPL-023-T005 - Candidate persistence with evidence/provenance/source spans`.
