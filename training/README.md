# Phase 2 Training Workspace

This workspace is for the Dramatica-informed training data described in `docs/plan.md`. It is data and schema only; it must not change runtime app behavior.

## No Prose Generation

The assistant is analysis-only. Training outputs must never generate, rewrite, continue, imitate, polish, or improve prose. Allowed outputs are structural analysis, throughline classification, writer-focused diagnostic questions, and refusal messages that redirect to those allowed forms of help.

## Task Types

- `story_check`: diagnose scene coherence against the storyform and bible, including throughline alignment, theme drift, character consistency, warnings, suggestions, and missing evidence.
- `throughline_classification`: classify the primary throughline for a scene, list secondary throughlines, cite evidence spans, and explain why the other throughlines are not primary.
- `writer_questions`: ask open-ended diagnostic questions tied to throughlines and story points. Questions must not include suggested prose.
- `out_of_scope_refusal`: refuse requests to write, rewrite, continue, imitate, or improve prose, while offering analysis, diagnostic questions, or structural classification.

## Target Dataset Mix

Use the Phase 2 mix from `docs/plan.md`:

- Story Check diagnostics: 40-45%
- Throughline classification: 25-30%
- Writer diagnostic questions: 20-25%
- Out-of-scope refusals: 5-10%

Target size is 500-1000 validated examples, with semi-synthetic examples corrected by a human before use.

## Contrast-Pair Priority

Prioritize contrast pairs because they teach the model to separate nearby Dramatica concepts instead of guessing from surface cues. High-value pairs include:

- Same scene interpreted as Overall Story vs. Main Character
- Change vs. Steadfast
- Influence Character pressure vs. Relationship Story conflict
- Missing evidence vs. confident classification

## Directory Contract

- `training/schemas/`: JSON Schema contracts for SFT records and each task output.
- `training/data/sources/`: raw or intermediate source material before validation.
- `training/data/sft/`: validated supervised fine-tuning records that conform to `training/schemas/sft_record.schema.json`.
- `training/data/eval/`: held-out evaluation examples, including contrast pairs and refusal cases.
- `training/scripts/`: future validation, conversion, and reporting scripts.
- `training/configs/`: future training and validation configs.
- `training/runs/`: local run outputs and experiment artifacts.
- `training/reports/`: dataset audits, validation summaries, and evaluation reports.

