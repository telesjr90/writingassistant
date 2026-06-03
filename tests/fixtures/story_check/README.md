# Story Check App Evaluation Fixtures

These files are app-level evaluation fixtures for parser, normalizer, guardrail, malformed-output, refusal, insufficient-evidence, and future harness behavior.

They are not training data, SFT records, model artifacts, or durable project truth. Do not copy them into `training/data`, do not add them to `dataset_manifest.json`, and do not promote them as owner-approved Dramatica/NCP truth.

The App-13 offline baseline harness consumes these fixtures through `training/scripts/run_story_check_baseline_eval.py`. Harness reports are app evaluation reports only.

Fixtures must not contain generated story prose. Unsafe-output examples use short blocked markers only so the output guard can be tested without storing replacement scenes, rewritten paragraphs, continuations, imitation text, or polished prose.

Positive Dramatica/NCP truth still requires owner-approved evidence. These fixtures mostly exercise unresolved and insufficient-evidence behavior.

| Fixture | Purpose |
| --- | --- |
| `valid_rich_story_check.json` | Rich schema-compatible Story Check object. |
| `minimal_story_check.json` | Minimal UI-compatible Story Check object. |
| `malformed_story_check.txt` | Malformed model output fallback case. |
| `refusal_response.json` | Standard no-prose refusal shape. |
| `insufficient_evidence_story_check.json` | Rich unresolved IC/RS/CIPS/dynamics case. |
| `unsafe_output_story_check.json` | Short unsafe model-authored strings for output guard sanitization. |
