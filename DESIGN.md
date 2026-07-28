---
name: Writing Assistant Application
description: A calm, rigorous, trustworthy interface for evidence-backed, owner-controlled story analysis.
colors:
  application-canvas: "#f5f7fb"
  primary-surface: "#ffffff"
  subtle-surface: "#fbfcff"
  muted-surface: "#f7f9fc"
  selected-surface: "#eef4ff"
  normal-text: "#172033"
  strong-text: "#101828"
  secondary-text: "#46546c"
  muted-text: "#637089"
  normal-border: "#dfe5ef"
  boundary-border: "#9fb3d4"
  primary-action-accent: "#234a84"
  focus-accent: "#7aa2e8"
  success-text: "#3b6948"
  success-surface: "#f3fbf5"
  success-border: "#8ec79c"
  warning-text: "#9a6500"
  warning-surface: "#fff9eb"
  warning-border: "#d7b46a"
  danger-text: "#a93636"
  danger-surface: "#fff7f7"
  danger-border: "#e2a3a3"
typography:
  h1:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.2
  h2:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
  body-copy:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  compact-metadata:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.45
  label-eyebrow:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0"
  monospace-data:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  control: "6px"
  surface: "8px"
  pill: "999px"
spacing:
  hairline: "4px"
  tight: "6px"
  compact: "8px"
  control-gap: "10px"
  inset: "12px"
  comfortable: "14px"
  standard: "16px"
  section: "20px"
  large: "24px"
  canvas: "32px"
components:
  primary-action:
    backgroundColor: "{colors.primary-action-accent}"
    textColor: "{colors.primary-surface}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "32px"
  secondary-action:
    backgroundColor: "{colors.primary-surface}"
    textColor: "{colors.primary-action-accent}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "32px"
  form-input:
    backgroundColor: "{colors.subtle-surface}"
    textColor: "{colors.normal-text}"
    rounded: "{rounded.surface}"
    padding: "0 10px"
    height: "36px"
  surface-panel:
    backgroundColor: "{colors.primary-surface}"
    textColor: "{colors.normal-text}"
    rounded: "{rounded.surface}"
    padding: "20px"
  boundary-notice:
    backgroundColor: "{colors.subtle-surface}"
    textColor: "{colors.secondary-text}"
    rounded: "{rounded.surface}"
    padding: "10px 12px"
  status-badge:
    backgroundColor: "{colors.selected-surface}"
    textColor: "{colors.primary-action-accent}"
    rounded: "{rounded.pill}"
    padding: "2px 8px"
    height: "24px"
  loading-state:
    backgroundColor: "{colors.muted-surface}"
    textColor: "{colors.secondary-text}"
    rounded: "{rounded.surface}"
    padding: "10px 12px"
  empty-state:
    backgroundColor: "{colors.subtle-surface}"
    textColor: "{colors.secondary-text}"
    rounded: "{rounded.surface}"
    padding: "14px"
  error-state:
    backgroundColor: "{colors.danger-surface}"
    textColor: "{colors.danger-text}"
    rounded: "{rounded.surface}"
    padding: "12px 14px"
  metadata-list:
    textColor: "{colors.secondary-text}"
  native-disclosure:
    backgroundColor: "{colors.primary-surface}"
    textColor: "{colors.secondary-text}"
    rounded: "{rounded.surface}"
    padding: "12px 14px"
  radix-evidence-dialog:
    backgroundColor: "{colors.primary-surface}"
    textColor: "{colors.normal-text}"
    width: "520px"
---

# Design System: Writing Assistant Application

## 1. Overview

**Creative North Star: "The Evidence Workbench"**

The interface is calm, rigorous, and trustworthy: a restrained product workspace where writers can inspect owner-authored material, analysis, evidence, provenance, and review state without mistaking any automated output for truth. Visual hierarchy must make the next honest task clear while keeping consequential transitions explicit and owner-controlled.

**The Truthful Affordance Rule.** A control must communicate its real availability. Blocked, unavailable, degraded, review-only, and not-yet-implemented states remain visibly distinct and never masquerade as working actions.

**The Evidence-First Rule.** Evidence and provenance precede confidence. Confidence communicates support strength, never truth, approval, approved Memory, or Canon status.

**The Progressive Disclosure Rule.** Show the primary review task first; preserve complete safety, boundary, evidence, and provenance detail in task-focused disclosures and secondary surfaces rather than repeating undifferentiated metadata everywhere.

**Key Characteristics:**

- Restrained product-UI register with cool neutral surfaces and one established blue action accent.
- Application-owned visual language and product semantics.
- Flat-by-default surfaces with borders and tonal layering; elevation is limited to established major panels and modal composition.
- Native HTML is the default for buttons, fields, forms, labels, headings, disclosures, and semantic tables.
- Radix is limited to complex interaction behavior and does not define product meaning or visual identity.
- The current CSS uses one `900px` breakpoint. This records existing behavior; it does not claim responsive completion. T004 owns responsive containment and repair.
- Current accessibility intent includes semantic structure, keyboard operation, visible focus, non-color-only states, and screen-reader clarity. No WCAG conformance claim is made. T005 owns heading, target-size, focus, and keyboard completion.

## 2. Colors

The palette is a restrained cool-neutral system. The frontmatter is the normative source for every color value; the roles below explain application intent.

### Core surfaces and text

- **Application Canvas:** the workspace behind navigation, editor, and analysis surfaces.
- **Primary Surface:** major panels, controls, and the portalled evidence dialog.
- **Subtle Surface:** metadata, review boundaries, and quiet inset content.
- **Muted Surface:** low-emphasis status and structural rows.
- **Selected Surface:** current selection and neutral informational badges.
- **Normal, Strong, Secondary, and Muted Text:** a deliberate hierarchy from working copy through headings and compact metadata.
- **Normal Border and Boundary Border:** normal structure uses the quiet border; evidence, provenance, and review-only boundaries use the emphasized boundary border.

### Actions and focus

- **Primary Action Accent:** reserved for enabled primary actions and strong navigation emphasis.
- **Focus Accent:** preserves the existing focus border and ring treatment without implying selection or approval.

### Semantic states

- **Success:** reserved for completed or satisfied states; it does not mean Canon unless the product label explicitly says so.
- **Warning:** communicates owner attention, unsaved state, blockers, or review caution.
- **Danger:** communicates failure or invalid state, not merely absence.

**The State Meaning Rule.** Color supplements explicit labels and reasons. It must never collapse candidate, queue presence, confidence, owner approval, approved Memory, Canon, or apply-promotion state.

## 3. Typography

The existing Inter/system UI family is the sole interface family. No new font, fluid type scale, or heading repair is introduced by this foundation.

- **H1 role:** current 24px page-level heading with strong text color and 1.2 line height.
- **H2 role:** current 22px section heading with strong text color and 1.2 line height.
- **Body/copy role:** current compact product copy, commonly 14px with 1.5 line height.
- **Compact metadata role:** current 11–12px labels and values used for provenance, status, and IDs.
- **Label/eyebrow role:** current 12px, weight-700 label treatment with zero added letter spacing; uppercase is reserved for the existing eyebrow vocabulary.
- **Monospace data role:** the existing system monospace stack for stored JSON, hashes, locators, and other machine-shaped data.

**The Semantic Hierarchy Rule.** Typography must reinforce source, evidence, state, and owner-action hierarchy. T005—not this gate—owns correction of duplicate headings, heading-level skips, target sizing, and complete focus/keyboard policy.

## 4. Elevation

Surfaces are flat by default. Borders and tonal changes carry most hierarchy. The existing major editor panel uses the established panel shadow, and the Radix-backed evidence dialog uses its existing directional drawer shadow; neither treatment authorizes a new elevation scale.

**The Flat-by-Default Rule.** Do not add decorative card shadows. Elevation is structural and scarce, never a substitute for information hierarchy.

**The Boundary-before-Shadow Rule.** Evidence, provenance, owner-review, warning, and danger meaning is expressed through explicit labels, borders, and surfaces—not through elevation alone.

## 5. Components

This section documents current component families and intent. It does not claim that shared JSX wrappers already exist.

### Current shared CSS vocabulary

- **Primary action:** enabled consequential action using the established accent, light text, control radius, and current sizing.
- **Secondary action:** neutral surface, accent text, and current outlined control treatment.
- **Form/input wrapper:** subtle or primary surface, existing border, current control/surface radius, and established focus ring.
- **Surface or panel:** primary surface with normal border and surface radius; the major editor panel retains its current limited shadow.
- **Boundary/review-only notice:** subtle surface with emphasized boundary border and explicit explanatory copy.
- **Status badge:** compact pill for labeled state; variants preserve informational, warning, and danger distinctions.
- **Loading, empty, and error states:** distinct shared treatments with truthful text and no fabricated recovery capability.
- **Metadata list:** compact definition-list vocabulary for evidence, provenance, stored values, IDs, and timestamps.
- **Native disclosure:** native `details`/`summary` behavior remains preferred where it is sufficient.

### Planned application-owned JSX abstractions

Later accepted T007C slices may extract application-owned wrappers from proven repeated patterns. This gate creates no shared JSX component and does not claim those abstractions exist.

### Radix interaction primitives

Radix is used incrementally only for complex interaction behavior. The installed runtime primitive is `@radix-ui/react-dialog`; it supplies the evidence dialog’s portal, modal focus containment, Escape behavior, and close autofocus behavior.

### Product-specific composites

The application-owned `OMIEvidenceDrawer` remains the evidence-dialog composite and retains evidence, provenance, review-only, disabled-reason, owner-authority, candidate, and Memory/Canon semantics. Radix supplies no product meaning.

**The Native-First Rule.** Use native HTML whenever it provides sufficient semantics and behavior. A runtime primitive must earn adoption through a bounded interaction requirement.

## 6. Do's and Don'ts

### Do

- **Do** keep the application analysis-only and candidate-first; model and tool output remains non-canon.
- **Do** preserve truthful affordances over apparent capability.
- **Do** keep owner authority explicit at every consequential transition.
- **Do** place evidence and provenance before confidence and label confidence as support strength rather than truth.
- **Do** use task-focused progressive disclosure while preserving complete safety and provenance detail.
- **Do** preserve distinctions among owner-authored material, analysis output, candidates, queue presence, confidence, evidence, provenance, owner approval, approved Memory, Canon, review-only promotion, executable apply-promotion, and blocked or unavailable behavior.
- **Do** keep analysis output candidate-first and non-canon; require explicit owner review for any later authorized transition.
- **Do** keep native HTML as the default and use Radix only for bounded complex interaction behavior.
- **Do** retain truthful loading, empty, unavailable, degraded, error, retry, and recovery states without inventing successful behavior.

### Don't

- **Don't** make the product resemble a generic AI chat or co-writer that writes, rewrites, continues, imitates, polishes, expands, outlines, drafts, revises, or improves story prose.
- **Don't** create an opaque automated system that presents confidence, candidates, queue entries, or model output as truth or silently promotes them.
- **Don't** turn the interface into a dense generic SaaS administration dashboard made from repetitive cards, banners, and metadata with no clear primary task.
- **Don't** use decorative or playful presentation that obscures evidence, provenance, risk, candidate status, or owner checkpoints.
- **Don't** make unavailable, blocked, review-only, or not-yet-implemented behavior appear actionable.
- **Don't** automatically promote, automatically apply promotion, or automatically mutate approved Memory or Canon.
- **Don't** add generated story-prose controls or examples.
- **Don't** let Radix, another primitive, or a CSS framework define application visual language, information architecture, or product semantics.
- **Don't** claim responsive completion before T004 or accessibility completion before T005.

## 7. Minimum Operable-Target Policy

This policy classifies pointer-operable targets under review relative to two
target-size thresholds. It is a documented, testable guide, not a
product-wide WCAG conformance claim.

### Classification Distinctions

1. **Confirmed failure of the 24 CSS-pixel minimum** — A control whose
   interactive target area is demonstrably smaller than 24-by-24 CSS pixels,
   no spacing exception is available, and no other applicable WCAG exception
   is active. This requires repair.

2. **Allowed WCAG exception** — A control that is smaller than 24-by-24 CSS
   pixels but qualifies for an explicit WCAG 2.2 SC 2.5.8 exception. The
   exact exception name and the evidence supporting it must be recorded.

3. **Meets the WCAG minimum but below the preferred 44 CSS pixels** — A
   control whose interactive target area is at least 24-by-24 CSS pixels
   (meets SC 2.5.8 Level AA) but falls below the preferred 44-by-44
   CSS-pixel objective (SC 2.5.5 Level AAA). Repair is desirable but not a
   Level AA failure.

4. **Already meets the preferred 44 CSS pixels** — A control whose
   interactive target area is at least 44-by-44 CSS pixels, satisfying both
   SC 2.5.8 and the application's preferred objective.

5. **Insufficient evidence pending rendered geometry** — Source CSS alone
   cannot establish the actual computed target area or determine whether a
   spacing exception applies. Classification is deferred until rendered
   browser geometry evidence is available.

### Governing Criteria

- **WCAG 2.2 SC 2.5.8 (Level AA):** Target Size (Minimum) requires that
  pointer-target interactive areas are at least 24-by-24 CSS pixels. This
  applies to clickable/tappable interactive controls in the rendered page.

- **WCAG 2.2 SC 2.5.5 (Level AAA):** Target Size (Enhanced) requires that
  pointer-target interactive areas are at least 44-by-44 CSS pixels.

- This application **adopts 44-by-44 CSS pixels as a preferred product
  objective**, especially for frequent, consequential, sequential, mobile,
  or coarse-pointer actions.

- **A control below 44 CSS pixels is not automatically a WCAG Level AA
  failure.** The 44-pixel threshold belongs to SC 2.5.5 (Level AAA), not the
  Level AA minimum.

### WCAG 2.5.8 Exceptions

A control smaller than 24 CSS pixels may still satisfy SC 2.5.8 if one of the
following exceptions applies:

1. **Spacing** — For an undersized target, a 24-CSS-pixel-diameter circle
   centered on the target's bounding box must not intersect another target
   or the corresponding circle for another undersized target. The visible
   glyph, icon, or checkbox alone is insufficient to evaluate this
   exception; rendered target geometry is required.

2. **Equivalent** — An equivalent control that meets the minimum exists
   elsewhere on the same page.

3. **Inline** — The target is part of a sentence or block of text and
   its size is constrained by the line height of non-target text.

4. **User-agent control** — The target size is determined by the user agent
   and has not been modified by the author.

5. **Essential** — A particular presentation of the target is essential to
   the information being conveyed.

### Evidence Requirements

- **Interactive target area matters, not merely the visible icon, label, or
  checkbox glyph.** A small glyph inside a larger clickable region may meet
  the minimum target through its full interactive area.

- **CSS source declarations (width, height, padding, line-height) are not
  browser-computed geometry.** Source CSS may be used to identify controls
  likely to require further review, but alone it cannot establish the final
  rendered target size or confirm that a spacing exception applies.

- **No product-wide WCAG conformance claim is asserted.** Each classification
  is a bounded assessment of a specific control under the distinctions defined
  here. Accessibility completion (T005) and full WCAG conformance evaluation
  are separate from this policy.
