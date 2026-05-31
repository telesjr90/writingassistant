# Owner Micro-Storyform Packet Schema Notes

These notes describe how an approved packet can later be converted into review-candidate SFT records. This template does not create SFT records by itself.

## Required SFT Inputs

Every SFT record derived from a packet must provide:

- `task`
- `storyform_context`
- `bible_summary`
- `scene_text`
- `user_request`
- `gold_output`
- provenance metadata

`scene_text` must come from the packet source text only. Codex must not write or improve it.

## Storyform Context

The SFT schema requires all four throughline context objects:

- `overall_story`
- `main_character`
- `influence_character`
- `relationship_story`

Each throughline context requires:

- `domain`
- `concern`
- `issue`
- `problem`
- `solution`

If a field is unresolved, it must stay marked as unresolved and must not be used as a positive training label. A record may train only the labels that are explicitly owner-approved and supported by evidence spans.

## Throughline Classification Output

For `throughline_classification`, `gold_output` must include:

- `primary_throughline`: one of `overall_story`, `main_character`, `influence_character`, `relationship_story`, `mixed`, or `insufficient_evidence`.
- `secondary_throughlines`: zero or more concrete throughlines only.
- `confidence`: number from 0 to 1.
- `evidence_spans`: objects with `text`, `supports`, and `reason`.
- `why_not`: explanations for all four concrete throughlines.

Positive labels require owner-approved storyform context and matching evidence spans. External source labels or model guesses are not sufficient.

## Story Check Output

For `story_check`, `gold_output` must keep suggestions diagnostic. It must not write, rewrite, continue, imitate, or improve prose.

`throughline_alignment` must include all four throughlines. Each alignment requires:

- `present`
- `evidence`
- `concerns`

When evidence is missing, use `insufficient_evidence` behavior rather than inventing storyform truth.

## Recommended Metadata

Derived review-candidate records should preserve:

- `packet_id`
- `source_type`
- `source_url`
- `source_license`
- `source_provenance_status`
- `owner_approval_reference`
- `approved_throughlines`
- `evidence_review_status`
- `transformation_notes`
- `no_prose_generated: true`
- `training_eligibility: draft_needs_human_review`
- `human_review_required: true`

Promotion to `eligible_for_training` requires a separate review pass.

## Promotion Gates

Promote only after:

- Schema validation passes.
- Source/provenance review passes.
- Owner approval is recorded.
- Evidence spans are confirmed against the source scene text.
- No prose-generation leakage is present.
- No unresolved placeholder remains for the trained label.
- No unapproved Dramatica/NCP storyform truth is introduced.

## Disallowed Transformations

Do not create:

- Positive throughline labels from Moral Stories or other external datasets without owner-approved storyform context.
- Generated scene text.
- Prose-generation outputs.
- Style-imitation outputs.
- Confident Story Check against a fabricated storyform.
- Records that treat unresolved fields as final Dramatica truth.
