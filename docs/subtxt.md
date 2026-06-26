I searched the official `narrative-first/subtxt-docs` repo. The useful move is **not** “classify the manuscript into Dramatica labels.” It is: turn Subtxt/Dramatica concepts into **evidence-gated semantic rubric rules** that produce candidate observations, confidence limits, and diagnostic questions.

The repo’s own framing supports that: the Subtxt Guide is a documentation source for core concepts like Storyforms and thematic exploration, but the docs repeatedly frame these concepts around author intent, review, and conflict reasoning rather than blind automatic labels. ([GitHub][1])

## Concepts that are safe as semantic rubric rules

| Concept                         | Safe rubric rule for your app                                                                                                                    | What the app should output                                                                                | What it must not do                                                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Source of conflict**          | A candidate must explain **why** the observed thing creates conflict, not merely name a topic, object, trait, scene, or event.                   | “This passage may indicate a source of conflict because X causes Y pressure for Z.”                       | Do not auto-label “Mind,” “Physics,” “Psychology,” “Universe,” or Subtxt’s newer domain names from keywords alone.             |
| **Removal test**                | Ask: “If this were removed, would the problem still exist?” If yes, the candidate is weak.                                                       | `evidence_status: insufficient_evidence` or `needs_owner_review`.                                         | Do not promote the candidate as canon just because the passage is thematically interesting.                                    |
| **Subject matter vs conflict**  | Treat subject matter as **surface material** unless the text shows an underlying tension or mechanism of conflict.                               | “War/heartbreak/caste system appears as subject matter; the conflict mechanism is not yet clear.”         | Do not turn “this story is about war” into “the conflict is war.”                                                              |
| **Author-level interpretation** | Storyform and structural meaning belong to the author’s argument, not to what characters consciously know.                                       | Candidate records should include `author_intent_question` and `owner_review_required: true`.              | Do not infer that a character’s stated goal equals the Story Goal or that a character’s opinion equals the author’s structure. |
| **Throughlines / perspectives** | Use OS, MC, IC, RS as **perspective lenses**: all characters/objective system, personal “I,” challenging “You,” relationship “We.”               | “This evidence is consistent with an MC-perspective candidate because it focuses on personal experience.” | Do not auto-assign a throughline; do not assume MC = protagonist or IC = antagonist.                                           |
| **Storypoints**                 | Domain, Concern, Issue, Problem are **rubric dimensions** for examining how conflict is framed, located, thematically focused, and sustained.    | Candidate: `possible_storypoint: Concern/Issue/etc`, plus why-problem evidence.                           | Do not output “confirmed OS Concern = Obtaining” without owner approval.                                                       |
| **Insufficient evidence**       | This should be your app’s safety state whenever the text lacks a clear conflict mechanism, viewpoint, owner intent, or sufficient evidence span. | “Insufficient evidence: the text shows topic/setting/action but not why it is structurally problematic.”  | Do not guess a Dramatica classification to fill the gap.                                                                       |
| **Diagnostic questions**        | Convert Subtxt’s “why is this a problem?” and removal-test logic into questions.                                                                 | A short set of owner-facing questions.                                                                    | Do not generate prose, outlines, rewrites, or “fixed” story content.                                                           |

The strongest source is the `Key Concepts` doc: it states that **subject matter is not conflict**, that conflict lies beneath the surface, and that the writer should identify the specific source of conflict rather than equating it with a topic. It also gives the “If I remove this, would there still be a problem?” test and says every Storypoint/Storybeat should be treated as a source of conflict, not just storytelling material. ([GitHub][2])

## How each focus area should map into your app

### 1. Source of conflict → “conflict mechanism required”

Your rubric should require a candidate to answer:

> What exactly creates pressure, inequity, contradiction, self-sabotage, escalation, blockage, or opposition here?

The docs explicitly say it is not enough to illustrate a domain as a surface trait, like Scrooge “having a bad attitude”; the illustration must show how that attitude creates conflict for him and around him. ([GitHub][2])

**Candidate field recommendation:**

```json
{
  "candidate_type": "source_of_conflict",
  "claim": "...",
  "conflict_mechanism": "...",
  "evidence_spans": ["..."],
  "removal_test": "...",
  "why_problem": "...",
  "status": "candidate_only"
}
```

### 2. Subject matter vs conflict → “topic is not enough”

Your app should flag topic-only analysis as weak. A passage about divorce, war, murder, class, grief, romance, or caste systems is not enough. The app must identify the underlying dynamic: control vs freedom, self-protection, exposure, pursuit, avoidance, obligation, denial, etc. The Subtxt docs make this distinction directly: heartbreak and caste systems may contain potential conflict, but they are not conflict by themselves. ([GitHub][2])

**Rubric rule:**

```text
If the model only identifies a topic, genre, event, relationship, object, or setting,
return insufficient_evidence and ask what makes it problematic.
```

### 3. Author-level interpretation → “owner intent is required”

The docs say Subtxt/Dramatica is “a tool for Authors, not for characters,” and that a Story Goal is about the author’s goal for the story, even if a protagonist is not consciously aware of it. ([GitHub][2])

That maps perfectly to your candidate-first architecture: the AI can suggest an interpretation, but **the owner must approve whether that interpretation matches the intended story argument**.

**Rubric rule:**

```text
Any structural interpretation must be framed as author-facing:
“Is this what you want the story to argue?”
Never treat character awareness as proof of structure.
```

### 4. Throughlines → “perspective lens, not classifier”

The `Perspectives` doc defines the four throughlines as distinct vantage points: Objective Story is the whole-system view of conflict, Main Character is the personal subjective view, Influence Character challenges the MC’s worldview, and Relationship Story tracks the evolving relationship dynamic. It also warns that MC is not inherently the protagonist. ([GitHub][3])

For your app, this means throughline detection should be **candidate tagging**, not automatic classification.

Good output:

```text
This passage may belong to an MC-perspective candidate because the evidence centers on the character’s personal burden and subjective experience.
```

Bad output:

```text
This is definitely the MC Throughline.
```

### 5. Storypoints → “semantic dimensions of conflict”

The `Storypoints` doc says Storypoints are organized by Throughline and help authors articulate conflict from different perspectives. It defines Domain, Concern, Issue, and Problem as layers for identifying the source of conflict and why the imbalance persists. ([GitHub][4])

So in your app, Storypoints can become rubric dimensions:

```text
Domain candidate: What kind of conflict is this?
Concern candidate: Where/how does it manifest?
Issue candidate: What thematic quality is in focus?
Problem candidate: What tension sustains the inequity?
```

But each one needs evidence and review. The app should never say “confirmed Storypoint.” It should say “possible Storypoint candidate.”

### 6. Insufficient evidence → “first-class safe outcome”

I did not find “insufficient evidence” as a named Subtxt concept in the repo. But it is the right safety status for your app because the docs repeatedly require deeper justification: “why is this a problem?”, the removal test, and author review/adjustment. ([GitHub][2])

Use `insufficient_evidence` when:

```text
- The passage shows subject matter but not conflict.
- The model cannot identify who experiences the conflict.
- The model cannot explain why the thing is problematic.
- The throughline perspective is ambiguous.
- The claim depends on author intent not present in the text.
- The evidence is only a scene summary, not structural pressure.
```

### 7. Diagnostic questions → “preferred output when unsure”

Subtxt’s “Why is this a problem?” and removal-test logic should become your app’s default diagnostic mode. The docs explicitly recommend asking why a Storypoint or Storybeat is a problem, and the Extract Four Throughlines task says generated throughlines should be reviewed and adjusted to align with the author’s vision. ([GitHub][2])

Good diagnostic questions for your app:

```text
1. What problem would disappear if this trait/action/situation were removed?
2. Is this a topic you want to explore, or the actual source of conflict?
3. Who experiences this conflict: everyone, the personal viewpoint character, the challenging influence, or the relationship?
4. Why is this problematic rather than merely descriptive?
5. What evidence in the manuscript makes this interpretation stronger than the alternatives?
6. Is this interpretation part of your intended story argument?
```

## Practical recommendation

Use Subtxt/Dramatica concepts as **semantic rubric rules that generate candidate records**, not as classifiers.

Your MVP should implement the rules like this:

```text
Input prose/notes
→ detect possible structural evidence
→ require conflict mechanism
→ require “why is this a problem?”
→ apply removal test
→ identify possible perspective lens
→ mark confidence and insufficiency
→ ask diagnostic questions
→ owner approves, rejects, or revises
→ only owner-approved items become app truth
```

The core boundary is simple: **Subtxt concepts can guide analysis, but your app must not let the model decide canon.** The model can surface “this may be a source of conflict,” “this may fit an MC perspective,” or “this lacks sufficient evidence.” The owner decides what the story means.

[1]: https://raw.githubusercontent.com/narrative-first/subtxt-docs/main/README.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/narrative-first/subtxt-docs/main/content/1.getting-started/5.key-concepts.md "raw.githubusercontent.com"
[3]: https://raw.githubusercontent.com/narrative-first/subtxt-docs/main/content/2.narrative-aspects/1.perspectives.md "raw.githubusercontent.com"
[4]: https://raw.githubusercontent.com/narrative-first/subtxt-docs/main/content/2.narrative-aspects/5.storypoints.md "raw.githubusercontent.com"
-------------------------------------------------------

Based on the official Subtxt docs, your app should treat Dramatica/Subtxt-inspired output as **evidence-backed structural hypotheses**, not automatic truth.

## Rules before making any Dramatica/Subtxt-inspired claim

| Area                        | App rule                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claim status**            | Every claim starts as a **candidate**, never canon. It can only become approved structure after owner review. Subtxt itself frames storyform building as tied to the author’s creative intent, and generated throughlines are meant to be reviewed and adjusted to align with the author’s vision. ([Subtxt with Muse - Documentation][1]) ([Subtxt with Muse - Documentation][2]) |
| **Evidence threshold**      | A claim must cite concrete story evidence: source text, user-approved notes, approved storyform fields, or explicit author intent. A genre, trope, vibe, or logline is not enough by itself.                                                                                                                                                                                       |
| **Conflict test**           | Before labeling a Domain, Concern, Issue, Problem, Throughline, or Storypoint, the app must show **why this is a source of conflict**, not merely what the subject matter is. Subtxt says authors should ask “Why is this a problem?” and warns against treating Storypoints as surface storytelling labels. ([Subtxt with Muse - Documentation][3])                               |
| **Removal test**            | The app should ask: **If this element were removed, would the same problem still exist?** If yes, the proposed source of conflict is probably too shallow or wrong. Subtxt explicitly presents this as a way to test whether the source of conflict has been identified. ([Subtxt with Muse - Documentation][3])                                                                   |
| **Perspective specificity** | Claims must state the perspective they apply to: Objective Story, Main Character, Influence Character, Relationship Story, or a sub-perspective. Subtxt defines these as distinct vantage points on conflict, not interchangeable labels. ([Subtxt with Muse - Documentation][4])                                                                                                  |
| **Storypoint specificity**  | For Storypoints, the app should require evidence for the layer being claimed: Domain, Concern, Issue, or Problem. Subtxt describes these as four layers for identifying a source of conflict, moving from general nature to manifestation, thematic focus, and sustaining tension. ([Subtxt with Muse - Documentation][5])                                                         |
| **No overview-as-canon**    | Overviews, blended summaries, loglines, and generated summaries should not automatically drive the rest of the system. Subtxt says Overviews are private understanding aids, and structural changes must be made in the underlying components if they should affect the app. ([Subtxt with Muse - Documentation][2])                                                               |

## Required evidence fields for your candidate records

Each Dramatica/Subtxt-inspired candidate should require:

```json
{
  "claim_type": "throughline | storypoint | source_of_conflict | diagnostic",
  "claim": "The proposed structural interpretation",
  "status": "candidate | insufficient_evidence | approved | rejected",
  "scope": {
    "throughline": "OS | MC | IC | RS | unknown",
    "storypoint_layer": "Domain | Concern | Issue | Problem | other | unknown"
  },
  "evidence": [
    {
      "source_type": "story_text | user_note | approved_context | author_intent",
      "quote_or_summary": "Concrete supporting evidence",
      "location": "chapter/scene/note/path",
      "why_it_supports_the_claim": "How this shows conflict, not just subject matter"
    }
  ],
  "conflict_test": {
    "why_is_this_a_problem": "...",
    "removal_test_result": "passes | fails | unknown"
  },
  "confidence": "low | medium | high",
  "missing_evidence": [],
  "diagnostic_questions": [],
  "provenance": {
    "generated_by": "analysis_engine",
    "created_at": "...",
    "model_or_rule_version": "..."
  }
}
```

## Insufficient-evidence behavior

When the app cannot show the source of conflict, it should **not guess**. It should return something like:

```json
{
  "status": "insufficient_evidence",
  "claim_attempted": "MC Domain appears to be Mind",
  "reason": "The available text shows attitude/subject matter, but not enough evidence that this attitude creates or sustains personal conflict.",
  "missing_evidence": [
    "A scene where the character's fixed attitude causes personal trouble",
    "Evidence that removing this attitude would remove the personal conflict"
  ],
  "diagnostic_questions": [
    "Why is this attitude a problem for the character personally?",
    "If the character stopped holding this attitude, would the same personal conflict remain?",
    "Is this conflict experienced privately by the Main Character, or by everyone in the Objective Story?"
  ]
}
```

That matches the Subtxt logic: a label like “bad attitude,” “obtaining the murderer’s identity,” or “caste system” is not enough; the author must show why that thing creates inequity/conflict. ([Subtxt with Muse - Documentation][3])

## Diagnostic-question behavior

Your app should ask questions that help the writer clarify structure without writing prose for them. Good defaults:

1. **Why is this a problem?**
2. **Who experiences this conflict: everyone, the Main Character personally, the Influence Character’s pressure, or the relationship?**
3. **If this proposed source of conflict disappeared, would the story problem still remain?**
4. **Is this evidence showing subject matter, or showing the underlying tension beneath the subject matter?**
5. **Which author-approved component should this update: Throughline, Domain, Concern, Issue, Problem, or just a private overview note?**

Subtxt’s own docs support this direction: Perspectives organize conflict by viewpoint, Storypoints identify conflict through structured layers, and generated throughlines should be reviewed and adjusted by the author rather than accepted blindly. ([Subtxt with Muse - Documentation][4]) ([Subtxt with Muse - Documentation][5]) ([Subtxt with Muse - Documentation][2])

## Guardrails against overclaiming storyform truth

Your app should never say:

> “This story’s Main Character Domain is definitely Mind.”

It should say:

> “Candidate: MC Domain may be Mind. Evidence: [x]. Conflict test: [y]. Missing evidence: [z]. Owner review required.”

Strong guardrails:

* **No automatic classification as canon.**
* **No claim without evidence.**
* **No Storyform truth from a logline alone.**
* **No treating generated throughlines as final.**
* **No treating subject matter as conflict.**
* **No promotion without owner approval.**
* **No prose generation, continuation, or rewriting as part of diagnostics.**
* **Always preserve alternatives when evidence supports multiple interpretations.**

The practical rule is: **Subtxt concepts can guide the rubric, but your app should behave like a careful analyst, not an oracle.**

[1]: https://guide.subtxt.app/advanced-concepts/storyform-builder/ "Storyform Builder - Subtxt with Muse - Documentation"
[2]: https://guide.subtxt.app/narrative-tasks/extracting-four-throughlines/ "Extracting Four Throughlines - Subtxt with Muse - Documentation"
[3]: https://guide.subtxt.app/getting-started/key-concepts/ "Key Concepts - Subtxt with Muse - Documentation"
[4]: https://guide.subtxt.app/narrative-aspects/perspectives/ "Perspectives - Subtxt with Muse - Documentation"
[5]: https://guide.subtxt.app/narrative-aspects/storypoints/ "Storypoints - Subtxt with Muse - Documentation"
------------------------------------------------

