# PHASE8-IMPL-024 UI Execution Order

## Status

Owner-approved roadmap sequencing decision.

This decision changes documentation, dependencies, and future execution order.
It does not implement UI changes, install dependencies, select a component
library, or mark any implementation task complete.

## Decision

The UI/UX work must proceed in this order:

1. Fix P0/P1 functional and integrity issues.
2. Use Impeccable for evidence-based UI review.
3. Decide between shadcn/ui, React Aria, Radix Primitives, or retaining native/custom components.
4. Standardize the design system according to that recorded decision.
5. Complete responsive and accessibility work against the standardized component foundation.

## Existing task mapping

- Functional and integrity work: `T001`, `T002`, `T003`, then `T006`.
- Impeccable evidence review: `T007A`.
- Component-library decision: `T007B`.
- Design-system and shared-component standardization: `T007C`.
- Responsive containment and validation: `T004`.
- Accessibility semantics, target sizing, and keyboard validation: `T005`.
- Remaining validation suites: `T008`.

Task IDs remain stable. The roadmap changes dependencies and presentation order
rather than renumbering existing tasks.

## Component-library boundary

The candidates to evaluate during `PHASE8-IMPL-024-T007B` are:

- shadcn/ui;
- React Aria;
- Radix Primitives;
- the existing native/custom React component approach.

No candidate is selected by this decision.

Impeccable remains an evidence-based review and design-assistance tool. It is
not a runtime UI framework and must not determine the component-library choice
without repository evidence and owner approval.

No Tailwind, shadcn/ui, React Aria, Radix, or other component dependency may be
installed merely to satisfy this roadmap update.

## Dependency changes

- `T006A` depends on `T003C`, making truthful navigation part of the functional
  repair sequence.
- `T007A` depends on `T006C`.
- `T007B` depends on `T007A`.
- `T007C` depends on `T007B`.
- `T004A` depends on `T007C`.
- `T005A` continues to depend on `T004C`.
- `T008` remains after the primary implementation workstreams.

## Preserved boundaries

- Analysis-only.
- Candidate-first.
- Evidence/provenance-backed.
- Owner-controlled.
- Model and tool output remain non-canon.
- No automatic promotion or apply-promotion.
- No automatic Memory/Canon mutation.
- No generated story prose.
