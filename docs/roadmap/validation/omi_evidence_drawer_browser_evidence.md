# OMI Evidence Drawer Browser Evidence

- Result: **PASS**
- Exit code: `0`
- Started: `2026-07-04T05:04:29.068Z`
- Finished: `2026-07-04T05:04:32.372Z`
- App base URL: `http://localhost:5173`
- Project ID: `example`
- API mode: `live-backend`
- Evidence directory: `docs/roadmap/validation/omi-evidence-drawer-browser-evidence`
- Workflow log: `docs/roadmap/validation/omi-evidence-drawer-browser-evidence/workflow-log.json`

## Screenshots

- Desktop: `docs/roadmap/validation/omi-evidence-drawer-browser-evidence/screenshots/01-desktop-omi-evidence-drawer.png`
- Mobile: `docs/roadmap/validation/omi-evidence-drawer-browser-evidence/screenshots/02-mobile-omi-evidence-drawer.png`

## Assertions

- PASS: desktop: Evidence Drawer is visible
- PASS: desktop: drawer title includes evidence scope
- PASS: desktop: required drawer copy visible: Source type
- PASS: desktop: required drawer copy visible: Source location
- PASS: desktop: required drawer copy visible: Quote exactness
- PASS: desktop: required drawer copy visible: Confidence/support
- PASS: desktop: required drawer copy visible: Original wording/excerpt
- PASS: desktop: required drawer copy visible: Evidence summary
- PASS: desktop: required drawer copy visible: Supports claim
- PASS: desktop: required drawer copy visible: Limitations / ambiguity
- PASS: desktop: required drawer copy visible: Provenance chain
- PASS: desktop: required drawer copy visible: Related IDs
- PASS: desktop: required drawer copy visible: Timestamps
- PASS: desktop: required drawer copy visible: Source hash
- PASS: desktop: required drawer copy visible: Snapshot hash
- PASS: desktop: required drawer copy visible: Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
- PASS: desktop: required drawer copy visible: Viewing evidence does not copy source text into Memory/Canon.
- PASS: desktop: required drawer copy visible: Confidence indicates support strength, not truth.
- PASS: desktop: required drawer copy visible: Navigation / copy
- PASS: desktop: required drawer copy visible: Review marking
- PASS: desktop: required drawer copy visible: Owner note
- PASS: desktop: required drawer copy visible: Close
- PASS: desktop: Open source record disabled fail-closed
- PASS: desktop: source open disabled reason associated
- PASS: desktop: Evidence Drawer has no apply to Memory/Canon action
- PASS: desktop: no generated prose controls visible in drawer
- PASS: desktop: drawer moves focus to labelled top close button
- PASS: desktop: focus trap wraps backward inside drawer
- PASS: desktop: closing drawer returns focus to opener
- PASS: opening evidence drawer does not create candidates
- PASS: opening evidence drawer does not mutate approved Memory/Canon snapshot
- PASS: opening evidence drawer performs no mutating API requests
- PASS: mobile: Evidence Drawer is visible
- PASS: mobile: drawer title includes evidence scope
- PASS: mobile: required drawer copy visible: Source type
- PASS: mobile: required drawer copy visible: Source location
- PASS: mobile: required drawer copy visible: Quote exactness
- PASS: mobile: required drawer copy visible: Confidence/support
- PASS: mobile: required drawer copy visible: Original wording/excerpt
- PASS: mobile: required drawer copy visible: Evidence summary
- PASS: mobile: required drawer copy visible: Supports claim
- PASS: mobile: required drawer copy visible: Limitations / ambiguity
- PASS: mobile: required drawer copy visible: Provenance chain
- PASS: mobile: required drawer copy visible: Related IDs
- PASS: mobile: required drawer copy visible: Timestamps
- PASS: mobile: required drawer copy visible: Source hash
- PASS: mobile: required drawer copy visible: Snapshot hash
- PASS: mobile: required drawer copy visible: Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
- PASS: mobile: required drawer copy visible: Viewing evidence does not copy source text into Memory/Canon.
- PASS: mobile: required drawer copy visible: Confidence indicates support strength, not truth.
- PASS: mobile: required drawer copy visible: Navigation / copy
- PASS: mobile: required drawer copy visible: Review marking
- PASS: mobile: required drawer copy visible: Owner note
- PASS: mobile: required drawer copy visible: Close
- PASS: mobile: Open source record disabled fail-closed
- PASS: mobile: source open disabled reason associated
- PASS: mobile: Evidence Drawer has no apply to Memory/Canon action
- PASS: mobile: no generated prose controls visible in drawer
- PASS: mobile: Evidence Drawer is full-screen sheet width
- PASS: mobile: top close visible
- PASS: mobile: bottom close visible

## Read-Only Snapshot Check

- Candidate count before: `2`
- Candidate count after: `2`
- Approved Memory/Canon total before: `0`
- Approved Memory/Canon total after: `0`

## Safety Confirmations

- Evidence-only browser navigation and GET snapshots only.
- If the backend or candidate evidence data is unavailable, Playwright serves a read-only candidate evidence API fixture and blocks mutating API requests.
- No backend code changed by this script.
- No candidates were created by this script.
- Memory/Canon snapshot, bible JSON, and storyform JSON were compared before/after.
- No model/Ollama calls were made.
- Apply-promotion was not run or enabled from the Evidence Drawer.
- No generated prose controls were added by this script.
