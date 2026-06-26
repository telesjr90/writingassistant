## Bottom line

NCP is useful for your app as an **interchange format for structural context**, not as an automatic canon source. The official repo describes NCP as a transport/schema layer for preserving authorial intent across tools, and its semantic grounding explicitly says it is **not** a replacement for Dramatica theory, canonical analysis, Storyform diagnosis, Subtxt, Narrova, or product-side reasoning workflows. ([GitHub][1])

So the clean integration rule is:

**Valid NCP JSON can create candidate records with provenance. It cannot directly mutate approved memory, approved storyform, approved moments, or project truth unless the owner explicitly approves each imported claim or imports a trusted app-generated export.**

## Recommended import boundary

Your app should treat NCP like this:

1. **Validate the NCP file** against the canonical schema.
2. **Store the original NCP file unchanged** as an import artifact.
3. **Create candidate records** from relevant fields.
4. **Show owner review UI** grouped by Storyform, Moments, Throughlines, Authorial Intent, Characters/Players, Settings, and Project Metadata.
5. **Only owner-approved records move into approved structural context.**

The NCP validation guide says adopters should validate NCP JSON against the canonical schema and treat validation failure as blocking. That validates shape, not truth. ([GitHub][2])

## Field mapping

| NCP field                               | Could map to your app’s…                                                 | Import status                           | Why                                                                                                                                                                                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------ | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema_version`                        | Import metadata                                                          | Safe metadata only                      | Use for compatibility/provenance, not story truth.                                                                                                                                                                                           |
| `story.id`                              | External source ID / import source key                                   | Safe metadata only                      | Should not replace your local `project_id`; keep as source provenance.                                                                                                                                                                       |
| `story.title`                           | Project title candidate                                                  | Candidate unless creating a new project | If importing into an existing project, title conflict must be reviewed.                                                                                                                                                                      |
| `story.logline`                         | Project overview / approved synopsis candidate                           | Candidate                               | It is audience-facing project context, not structural truth by itself.                                                                                                                                                                       |
| `story.genre`                           | Project metadata / genre candidate                                       | Candidate                               | NCP treats genre as optional story-level metadata; useful, but owner should confirm. ([GitHub][3])                                                                                                                                           |
| `story.created_at`                      | Import metadata / source timestamp                                       | Safe metadata only                      | Source creation date, not project chronology.                                                                                                                                                                                                |
| `story.settings[]`                      | Approved locations/settings candidates                                   | Candidate                               | NCP settings are reusable story-level place/environment entries; they can seed your locations/settings page after review. ([GitHub][3])                                                                                                      |
| `story.ideation.character[]`            | Character idea candidates / notes                                        | Candidate only                          | NCP says ideation is exploratory material before a formal Storyform exists. It should never become approved canon automatically. ([GitHub][4])                                                                                               |
| `story.ideation.theme[]`                | Theme / authorial-intent idea candidates                                 | Candidate only                          | Same: beginner/exploratory idea layer, not approved structure.                                                                                                                                                                               |
| `story.ideation.plot[]`                 | Plot-thread / moment idea candidates                                     | Candidate only                          | Can inspire candidate plot threads, but not approved timeline/moments.                                                                                                                                                                       |
| `story.ideation.genre[]`                | Tone/genre/framing candidates                                            | Candidate only                          | Useful as context, but not canon.                                                                                                                                                                                                            |
| `story.narratives[]`                    | Storyform candidates                                                     | Candidate by default                    | NCP allows `candidate`, `draft`, and `complete`, but your app should treat NCP `status` as source status, not owner approval. ([GitHub][4])                                                                                                  |
| `narratives[].status`                   | Candidate lifecycle metadata                                             | Candidate metadata only                 | `complete` in NCP means complete in the source document, not approved in your app.                                                                                                                                                           |
| `narratives[].subtext.dynamics[]`       | Approved Storyform dynamics candidates                                   | Candidate until approved                | Dynamics map well to Story Outcome, Judgment, Driver, Limit, Resolve, Growth, Approach, etc., but changing dynamics is risky and should be owner-confirmed. ([GitHub][4])                                                                    |
| `narratives[].subtext.storypoints[]`    | Approved Storyform appreciations / Throughline fields                    | Candidate until approved                | Storypoints carry appreciation, narrative function, illustration, summary, perspective links, and optional throughline labels. These are strong Storyform candidates, but not automatic truth. ([GitHub][4])                                 |
| `storypoints[].appreciation`            | Storyform slot candidate                                                 | Candidate                               | Example: `Main Character Issue`, `Story Goal`, `Objective Story Domain`. Must be owner-reviewed.                                                                                                                                             |
| `storypoints[].narrative_function`      | Dramatica element/class/type/etc. candidate                              | Candidate                               | Useful structural value, but should not be inferred or silently normalized.                                                                                                                                                                  |
| `storypoints[].illustration`            | Authorial-intent evidence / illustration candidate                       | Candidate                               | This can support why a structural slot was chosen, but it is still a claim.                                                                                                                                                                  |
| `storypoints[].summary`                 | Structural explanation candidate                                         | Candidate                               | Good review text for owner approval.                                                                                                                                                                                                         |
| `storypoints[].storytelling`            | Audience-facing expression / evidence candidate                          | Candidate only                          | NCP separates Subtext from Storytelling; your app should not let storytelling text overwrite structure. ([GitHub][5])                                                                                                                        |
| `storypoints[].throughline`             | Throughline grouping candidate                                           | Candidate                               | Useful for Objective Story, Main Character, Influence Character, Relationship Story grouping.                                                                                                                                                |
| `narratives[].subtext.storybeats[]`     | Signpost/progression/event candidates                                    | Candidate until approved                | Storybeats are structural turns, not prose beats; they can map to approved structural progression only after review. ([GitHub][5])                                                                                                           |
| `storybeats[].scope`                    | Beat granularity: signpost/progression/event                             | Candidate                               | Useful for candidate type selection.                                                                                                                                                                                                         |
| `storybeats[].sequence`                 | Structural order candidate                                               | Candidate                               | Should be reviewed, especially if your project already has a chapter/scene order.                                                                                                                                                            |
| `storybeats[].throughline`              | Throughline progression candidate                                        | Candidate                               | Strong candidate mapping, but no auto-promotion.                                                                                                                                                                                             |
| `storybeats[].appreciation`             | Derived interoperability label                                           | Candidate metadata                      | NCP says this is optional/derived from `throughline + scope + sequence`; don’t treat it as an independent approved fact. ([GitHub][4])                                                                                                       |
| `narratives[].subtext.perspectives[]`   | Throughline/perspective candidates                                       | Candidate until approved                | NCP uses perspectives as structural points of view on conflict, not camera POV or generic character opinions. ([GitHub][5])                                                                                                                  |
| `perspectives[].author_structural_pov`  | Throughline POV candidate                                                | Candidate                               | `i/you/we/they` can help map Main Character, Influence Character, Relationship Story, Objective Story, but owner should confirm.                                                                                                             |
| `narratives[].subtext.players[]`        | Character candidates + structural role candidates                        | Candidate until approved                | Players carry identity, role, summaries, motivations, and perspective links. Character identity and structural role should remain reviewable. ([GitHub][4])                                                                                  |
| `players[].role`                        | Character role / MC/IC/protagonist-style candidate                       | Candidate                               | The semantic grounding warns not to collapse Main Character into Protagonist. ([GitHub][5])                                                                                                                                                  |
| `players[].motivations[]`               | Character function / motivation candidates                               | Candidate                               | Useful for candidate character/function records, not approved truth.                                                                                                                                                                         |
| `narratives[].storytelling.overviews[]` | Project overview / authorial-intent candidates                           | Candidate only                          | Overviews include Logline, Genre, and Blended Throughlines; useful for review, but they are audience-facing presentation. ([GitHub][4])                                                                                                      |
| `story.moments[]`                       | Project structure, scenes, chapters, sequences, levels, approved moments | Candidate until approved                | NCP says Moments are story-level storytelling units that may reference Storybeats and Storypoints across narratives. They map well to your app’s scenes/chapters/moments model, but should not auto-create approved structure. ([GitHub][4]) |
| `moments[].summary`                     | Moment title/short summary candidate                                     | Candidate                               | Good candidate scene/chapter card title.                                                                                                                                                                                                     |
| `moments[].synopsis`                    | Moment synopsis candidate                                                | Candidate                               | Reviewable project-structure content.                                                                                                                                                                                                        |
| `moments[].setting` / `setting_id`      | Location/setting candidate link                                          | Candidate                               | Can link to `story.settings[]`, but owner confirms the setting identity.                                                                                                                                                                     |
| `moments[].timing`                      | Timeline candidate                                                       | Candidate                               | Useful for approved timeline after review.                                                                                                                                                                                                   |
| `moments[].imperatives`                 | Authorial-intent / scene-purpose candidate                               | Candidate                               | Very useful, but should not become canon automatically.                                                                                                                                                                                      |
| `moments[].act` / `order`               | Project structure ordering candidate                                     | Candidate                               | Can seed chapter/scene order, but must not overwrite existing local order without review.                                                                                                                                                    |
| `moments[].storybeats[]`                | Evidence links from moment to structural beats                           | Candidate link                          | These are especially valuable as provenance: “this moment claims to express these beats.”                                                                                                                                                    |
| `moments[].storypoints[]`               | Evidence links from moment to structural storypoints                     | Candidate link                          | Same: useful as review/evidence links, not automatic truth.                                                                                                                                                                                  |

## How this fits your approved-memory model

NCP’s strongest fit is as a **structured candidate importer** for your Writer Assistant Core:

```text
NCP file
  -> schema validation
  -> immutable import record
  -> candidate records with JSON-pointer provenance
  -> owner review
  -> approved structural context
```

Each imported candidate should carry at least:

```json
{
  "candidate_type": "storyform_dynamic | storypoint | storybeat | moment | setting | player | perspective | overview | ideation",
  "source_type": "ncp_import",
  "source_file_id": "...",
  "ncp_schema_version": "1.3.0",
  "ncp_json_pointer": "/story/narratives/0/subtext/storypoints/12",
  "source_value_hash": "...",
  "claim_summary": "...",
  "evidence": {
    "ncp_field": "storypoints[].summary",
    "linked_moment_ids": [],
    "linked_storybeat_ids": [],
    "linked_storypoint_ids": []
  },
  "review_state": "pending",
  "owner_decision": null
}
```

That gives you NCP interoperability without violating your boundary: **no imported NCP field becomes approved truth merely because it is valid, complete, or structurally named.**

## Practical recommendation

Implement NCP import in two levels.

**Level 1: safe metadata + candidate extraction.** Validate the file, store it, and create reviewable candidates for story metadata, settings, ideation, narratives, perspectives, players, dynamics, storypoints, storybeats, overviews, and moments.

**Level 2: approved export/import round-trip.** Later, if your own app exports NCP from already approved structural context, you can mark those exports with your own provenance metadata and allow trusted re-import into the same project. External NCP files should still go through candidate review.

This is exactly aligned with NCP’s own boundary: preserve Storyform, Storytelling, and authored notes separately; do not pretend NCP performs Dramatica diagnosis; keep uncertainty explicit rather than silently rewriting structure. ([GitHub][5])

[1]: https://github.com/narrative-first/narrative-context-protocol/blob/main/README.md "narrative-context-protocol/README.md at main · narrative-first/narrative-context-protocol · GitHub"
[2]: https://github.com/narrative-first/narrative-context-protocol/blob/main/VALIDATION.md "narrative-context-protocol/VALIDATION.md at main · narrative-first/narrative-context-protocol · GitHub"
[3]: https://raw.githubusercontent.com/narrative-first/narrative-context-protocol/main/docs/narrative-context-protocol-schema.md "raw.githubusercontent.com"
[4]: https://github.com/narrative-first/narrative-context-protocol/blob/main/SPECIFICATION.md "narrative-context-protocol/SPECIFICATION.md at main · narrative-first/narrative-context-protocol · GitHub"
[5]: https://github.com/narrative-first/narrative-context-protocol/blob/main/NCP_SEMANTIC_GROUNDING.md "narrative-context-protocol/NCP_SEMANTIC_GROUNDING.md at main · narrative-first/narrative-context-protocol · GitHub"
--------------------------------------------------------------

A safe NCP workflow for your app should treat **NCP as an interchange format, not as authority**. The official repo describes NCP as “transport-focused” for preserving authorial intent across tools, with separate **Ideation**, **Subtext**, and **Storytelling** layers; it also defines narrative lifecycle states like `candidate`, `draft`, and `complete`. That fits your app, but only if your app’s **owner-approved memory/canon remains the authority**. ([GitHub][1])

## Safe export workflow

**Allowed export sources**

Export only from owner-approved, project-owned records:

| Your app source                                                                | NCP target                                                                       |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| Approved project metadata                                                      | `story.id`, `story.title`, `story.logline`, `story.created_at`, `schema_version` |
| Approved authorial intent / storyform                                          | `story.narratives[].subtext`                                                     |
| Approved throughlines / perspectives                                           | `subtext.perspectives[]`, `storypoints[].throughline`, perspective links         |
| Approved characters                                                            | `subtext.players[]`                                                              |
| Approved structural choices                                                    | `subtext.dynamics[]`, `subtext.storypoints[]`, `subtext.storybeats[]`            |
| Approved chapters/scenes/sequences                                             | `story.moments[]`                                                                |
| Approved locations/settings                                                    | `story.settings[]` and `moments[].setting_id`                                    |
| Approved early concept notes, only when explicitly owner-approved for exchange | `story.ideation.character/theme/plot/genre[]`                                    |

This matches the NCP design: story-level Moments belong at `story.moments[]`, while Subtext holds deeper structural intent and Storytelling holds audience-facing presentation. ([GitHub][2])

**Forbidden raw-candidate export**

Do **not** export raw OMI candidates, unreviewed extraction results, model guesses, diagnostics, contradiction warnings, inferred throughlines, or “possible storyform” records as normal NCP truth. The NCP semantic guide explicitly warns that prose may imply possible structure but does not confirm it; if Storytelling appears to contradict a Storypoint, the safe behavior is to preserve the existing structural field and record a candidate note rather than overwrite the object. ([GitHub][3])

So in your app, this should be a hard rule:

> NCP export reads from approved memory/canon only. Candidate records are not exportable as NCP storyform unless individually promoted by the owner.

A possible exception is a separate **review package export**, but it should not pretend to be canonical NCP. It should be clearly named something like `candidate_review_bundle`, outside the standard NCP canon export path.

## Safe import workflow

The safest import behavior is **import-as-candidate**, never import-as-canon.

Recommended flow:

1. **Validate the file first.** Use the official schema validation path, and treat validation failure as blocking. The repo’s validation guide says to run `npm run validate:file -- /path/to/your-ncp.json`, treat `FAIL` as blocking, and re-run until `PASS`. It also recommends pinning `schema_version` and validating before release/PR workflows. ([GitHub][4])

2. **Store the original NCP file as an immutable import artifact.** Keep `source_file_hash`, `schema_version`, import timestamp, original `story.id`, original `narrative.id`, and external `status`.

3. **Decompose the NCP into candidate records.** For example:

   * `story.ideation.*` → ideation candidates.
   * `story.narratives[].subtext.perspectives[]` → throughline/perspective candidates.
   * `players[]` → character/player candidates.
   * `storypoints[]` → structural storypoint candidates.
   * `storybeats[]` → timeline/beat candidates.
   * `dynamics[]` → storyform dynamic candidates.
   * `story.moments[]` → scene/chapter/moment candidates.
   * `story.settings[]` → location/setting candidates.

4. **Mark every imported item as unapproved.** Even if the NCP file says `status: "complete"`, that is only the external file’s claim. Your app should store it as:

   * `candidate_source: "ncp_import"`
   * `external_ncp_status: "candidate" | "draft" | "complete" | omitted`
   * `owner_review_status: "pending"`
   * `promotion_status: "not_promoted"`

5. **Never overwrite approved memory automatically.** If the imported NCP conflicts with approved canon, create a conflict candidate. Do not replace the owner-approved record.

6. **Require owner review for promotion.** The owner should approve each candidate individually or approve a carefully scoped batch, with a promotion audit entry. Promotion should copy normalized data into approved memory; it should not preserve the imported file as “truth.”

This is especially important because the NCP schema says `status` is optional and may be `candidate`, `draft`, or `complete`; if omitted, consumers may treat it as complete. Your app should **not** follow that default internally. Omitted or `complete` should mean only “the imported NCP presents itself this way,” not “the owner approved it.” ([GitHub][2])

## Owner-review requirements

Owner review should be required for:

* Any imported Subtext field.
* Any imported storyform dynamic.
* Any imported throughline/perspective assignment.
* Any imported Storypoint, Storybeat, or Moment reference.
* Any imported character-to-perspective relationship.
* Any imported setting/location that merges with an existing approved location.
* Any imported ideation item that would become part of project memory.
* Any import conflict, duplicate, or external `complete` claim.

The review UI should show the **candidate**, the **NCP source path**, the **original value**, any **matched approved record**, and the **diff/conflict reason**. Promotion should produce an audit record like: “Owner approved imported NCP Storypoint X into approved storyform slot Y.”

## Risks of treating NCP files as canon

The biggest risk is letting an interchange file bypass the owner. NCP is designed to carry structured narrative context between tools, not to decide what is true in your project. The official repo emphasizes preserving the distinction between Subtext and Storytelling, and the semantic guide warns AI consumers not to infer or rewrite Storyform fields from prose alone. ([GitHub][1])

Specific risks:

| Risk                      | What could go wrong                                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| External authority leak   | A file from another tool becomes “approved truth” without the writer accepting it.                                      |
| Candidate laundering      | Your own unreviewed candidates get exported as NCP, re-imported, and mistaken for canon.                                |
| Subtext corruption        | Storytelling summaries overwrite structural storyform fields.                                                           |
| Status confusion          | `complete` or omitted `status` is treated as owner approval.                                                            |
| Semantic drift            | Custom labels or framework mappings mutate canonical Dramatica/NCP meanings.                                            |
| Deletion by omission      | Missing fields in an imported file are interpreted as “delete existing approved data.”                                  |
| Role confusion            | Main Character, Protagonist, Influence Character, and Objective Story roles get collapsed into generic character roles. |
| Multi-narrative confusion | Moments referencing multiple narratives lose `narrative_id` context.                                                    |

## Practical rule for your roadmap

Use NCP like this:

> **Export only approved owner-controlled story context. Import every NCP file as candidates with provenance. Validate structure, preserve the original artifact, never overwrite canon, and require explicit owner promotion before anything becomes approved memory.**

That gives you interoperability without breaking your app’s candidate-first safety model.

[1]: https://github.com/narrative-first/narrative-context-protocol "GitHub - narrative-first/narrative-context-protocol: A standardized, application-agnostic narrative structure schema designed for reliably transporting authorial intent across multi-agentic narrative systems. · GitHub"
[2]: https://github.com/narrative-first/narrative-context-protocol/blob/main/SPECIFICATION.md "narrative-context-protocol/SPECIFICATION.md at main · narrative-first/narrative-context-protocol · GitHub"
[3]: https://github.com/narrative-first/narrative-context-protocol/blob/main/NCP_SEMANTIC_GROUNDING.md "narrative-context-protocol/NCP_SEMANTIC_GROUNDING.md at main · narrative-first/narrative-context-protocol · GitHub"
[4]: https://github.com/narrative-first/narrative-context-protocol/blob/main/VALIDATION.md "narrative-context-protocol/VALIDATION.md at main · narrative-first/narrative-context-protocol · GitHub"
-----------------------------------------------------