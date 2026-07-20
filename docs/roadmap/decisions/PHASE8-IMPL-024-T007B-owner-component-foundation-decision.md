# PHASE8-IMPL-024 T007B Owner Component-Foundation Decision

## Decision

`PHASE8-IMPL-024-T007B` is complete/PASS as a research-and-owner-decision
task. The owner selects Radix Primitives as the application's accessibility and
complex-interaction foundation under the controlling conditions in this
record.

The `PHASE8-IMPL-024-T007` parent remains active and in progress. T007C becomes
the next planned, dependency-satisfied, eligible frontier and has not begun.
This record does not install or implement Radix.

## Authority and evidence

This decision is based on:

- the accepted T007A closeout and its four verified P2 defects:
  1. Candidate Detail table actions can begin offscreen in a horizontally
     scrolled desktop viewport.
  2. At `320 x 568`, the document expands beyond the viewport and clips the
     Story Check selector.
  3. Inputs and selects are approximately 19-21 pixels high and checkboxes are
     approximately 13 pixels; this is a target-size finding, not a complete
     WCAG determination.
  4. OMI pages contain duplicate `h1` elements and heading-level skips.
- committed `PRODUCT.md` product context;
- committed `.impeccable/live/config.json` initialization;
- T007B read-only repository inspection and current primary-source research;
- the owner's explicit Radix Primitives selection; and
- repository starting HEAD `cd59c236ed5fcbdc4a4eba5995c7d5805c0497c7`.

The read-only T007B research packet was advisory conversation output rather
than a repository artifact.

## Selected foundation

Radix Primitives is selected for layer-2 accessibility and interaction
primitives beneath application-owned shared components and product-specific
composites. Radix is not the application's complete design system and does not
define the product's visual language, information architecture, or safety
semantics.

## Adoption policy

- Adoption is limited to complex widgets and interaction behavior.
- Native HTML remains preferred for ordinary buttons, fields, forms, labels,
  headings, disclosures, and semantic tables wherever native behavior is
  sufficient.
- Adoption must proceed incrementally, wrapper by wrapper.
- T007C must begin with the smallest necessary individual Radix package.
- The Radix umbrella package is not authorized for the first gate.
- No wholesale DOM or component-API conversion is authorized.
- Selective continued use of native controls is expected throughout later
  implementation.
- Tailwind and shadcn/ui are not authorized.
- T007B installs no dependency and pins no package or version. Current version
  and peer compatibility must be verified at the T007C starting gate.

## Application-owned boundaries

The application retains ownership of:

- the application shell and task-priority header;
- the project selector/create/refresh group;
- primary navigation and the location indicator;
- the safety/boundary banner;
- the candidate status and owner-attention strip;
- evidence/provenance summaries and disclosures;
- the owner review gate;
- promotion readiness and blockers;
- the final owner checkpoint;
- loading, empty, unavailable, degraded, error, retry, and recovery states;
- responsive table containment;
- Approved Memory/Canon category presentation;
- Analysis Sidebar sections;
- field and validation wrappers; and
- accessible drawer/dialog composition.

The application also owns every distinction among analysis, candidate, queue
presence, confidence, evidence strength, provenance, owner approval, approved
Memory, Canon, review-only promotion, executable apply-promotion, and blocked
or unavailable behavior. A Radix primitive must not collapse, rename, or define
any of these product meanings.

## T007C first gate

The first T007C implementation gate is a bounded `OMIEvidenceDrawer` proof of
concept. After separate implementation authorization, that first task must:

- verify the current smallest appropriate individual Radix package and version;
- install only that authorized package;
- change only the bounded drawer family and its focused tests or harness;
- preserve accessible dialog naming, initial focus, Tab and Shift+Tab
  containment, Escape dismissal, trigger-focus restoration, responsive/mobile
  containment, evidence and provenance visibility, review-only behavior, the
  absence of an apply action in the evidence drawer, existing safety text, and
  existing test contracts and locators;
- make no Story Check, model, extraction, promotion, apply-promotion, or
  Memory/Canon call; and
- stop if the change spreads beyond the separately authorized surface.

This record neither authorizes nor implements that proof of concept.

## Failure and fallback

Broader Radix adoption stops if the bounded drawer gate fails. React Aria
Components is the first reassessment option, particularly if later
requirements materially prioritize broad collection, table, form, selection,
or internationalization behavior over DOM continuity. Retained native/custom
behavior is the second reassessment option.

Failure does not authorize shadcn/ui or Tailwind.

## Design-system boundary

`DESIGN.md` remains deferred to T007C. Design tokens and product semantics
remain application-owned; Radix supplies no accepted product semantics or
visual language. T007C owns the application token system, shared components,
information architecture, and standardization.

## Explicit exclusions

T007B did not:

- install Radix;
- install Tailwind, shadcn/ui, or React Aria Components;
- edit package files;
- modify application code or CSS;
- create `DESIGN.md`;
- run a proof of concept;
- repair or reclassify T007A findings;
- begin T007C; or
- perform model, Story Check, extraction, promotion, apply-promotion, or
  Memory/Canon work.

## Status and dependencies

- T007A: complete/PASS.
- T007B: complete/PASS.
- T007 parent: active/in progress.
- T007C: planned, dependency-satisfied, eligible, next frontier, and not begun.
- T004: remains after T007C.
- T005: remains after T004.
- T008: remains later.
- Broad owner acceptance and MVP readiness remain blocked.
