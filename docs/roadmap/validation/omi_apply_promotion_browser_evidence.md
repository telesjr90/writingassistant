# OMI Apply-Promotion Browser Evidence

- Result: **PASS**
- Exit code: `0`
- Started: `2026-07-04T05:30:52.955Z`
- Finished: `2026-07-04T05:30:58.130Z`
- App base URL: `http://localhost:5173`
- Project ID: `example`
- API mode: `live-backend`
- Evidence directory: `docs/roadmap/validation/omi-apply-promotion-browser-evidence`
- Workflow log: `docs/roadmap/validation/omi-apply-promotion-browser-evidence/workflow-log.json`

## Screenshots

- Desktop: `docs/roadmap/validation/omi-apply-promotion-browser-evidence/screenshots/01-desktop-omi-apply-promotion-confirmation.png`
- Mobile: `docs/roadmap/validation/omi-apply-promotion-browser-evidence/screenshots/02-mobile-omi-apply-promotion-confirmation.png`

## Assertions

- PASS: desktop: Apply-Promotion Confirmation is reachable
- PASS: desktop: required confirmation copy visible: Candidate Snapshot
- PASS: desktop: required confirmation copy visible: Destination
- PASS: desktop: required confirmation copy visible: Target Path
- PASS: desktop: required confirmation copy visible: Evidence / Provenance Summary
- PASS: desktop: required confirmation copy visible: Source Location Summary
- PASS: desktop: required confirmation copy visible: Duplicate / Link / Dependency Summary
- PASS: desktop: required confirmation copy visible: Approved Memory/Canon Before-State
- PASS: desktop: required confirmation copy visible: Audit Preview
- PASS: desktop: required confirmation copy visible: Owner Final Confirmation
- PASS: desktop: required confirmation copy visible: Cancel / Return
- PASS: desktop: required confirmation copy visible: This is the only screen that may lead to Memory/Canon mutation.
- PASS: desktop: required confirmation copy visible: Candidate approval, queue presence, confidence, and promotion audit records are not enough.
- PASS: desktop: required confirmation copy visible: Ready means the handoff packet is complete. Memory/Canon has not changed.
- PASS: desktop: required confirmation copy visible: Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
- PASS: desktop: required confirmation copy visible: This remains a candidate until apply-promotion is separately confirmed and completed.
- PASS: desktop: required confirmation copy visible: Memory/Canon Unchanged
- PASS: desktop: blockers appear before confirmation control
- PASS: desktop: final action disabled when blocker visible
- PASS: desktop: disabled final action reason associated
- PASS: desktop: described reason exists omi-apply-promotion-visible-blocker-reasons
- PASS: desktop: described reason exists omi-apply-promotion-final-action-disabled-reason
- PASS: desktop: owner final confirmation visible
- PASS: desktop: cancel return visible
- PASS: desktop: cancel return keyboard reachable
- PASS: desktop: final action remains disabled after checkbox while blockers visible
- PASS: desktop: no apply-promotion request is made in blocked state
- PASS: desktop: no generated prose controls visible
- PASS: opening confirmation does not create candidates
- PASS: opening confirmation does not mutate approved Memory/Canon snapshot
- PASS: blocked confirmation performs no mutating API requests
- PASS: Dashboard does not expose enabled apply-promotion
- PASS: Candidate Detail does not expose enabled apply-promotion
- PASS: Evidence Drawer does not expose enabled apply-promotion
- PASS: mobile: Apply-Promotion Confirmation is reachable
- PASS: mobile: required confirmation copy visible: Candidate Snapshot
- PASS: mobile: required confirmation copy visible: Destination
- PASS: mobile: required confirmation copy visible: Target Path
- PASS: mobile: required confirmation copy visible: Evidence / Provenance Summary
- PASS: mobile: required confirmation copy visible: Source Location Summary
- PASS: mobile: required confirmation copy visible: Duplicate / Link / Dependency Summary
- PASS: mobile: required confirmation copy visible: Approved Memory/Canon Before-State
- PASS: mobile: required confirmation copy visible: Audit Preview
- PASS: mobile: required confirmation copy visible: Owner Final Confirmation
- PASS: mobile: required confirmation copy visible: Cancel / Return
- PASS: mobile: required confirmation copy visible: This is the only screen that may lead to Memory/Canon mutation.
- PASS: mobile: required confirmation copy visible: Candidate approval, queue presence, confidence, and promotion audit records are not enough.
- PASS: mobile: required confirmation copy visible: Ready means the handoff packet is complete. Memory/Canon has not changed.
- PASS: mobile: required confirmation copy visible: Evidence supports review. It is not canon truth until owner approval and apply-promotion are complete.
- PASS: mobile: required confirmation copy visible: This remains a candidate until apply-promotion is separately confirmed and completed.
- PASS: mobile: required confirmation copy visible: Memory/Canon Unchanged
- PASS: mobile: blockers appear before confirmation control
- PASS: mobile: final action disabled when blocker visible
- PASS: mobile: disabled final action reason associated
- PASS: mobile: described reason exists omi-apply-promotion-visible-blocker-reasons
- PASS: mobile: described reason exists omi-apply-promotion-final-action-disabled-reason
- PASS: mobile: owner final confirmation visible
- PASS: mobile: cancel return visible
- PASS: mobile: cancel return keyboard reachable
- PASS: mobile: final action remains disabled after checkbox while blockers visible
- PASS: mobile: no apply-promotion request is made in blocked state
- PASS: mobile: no generated prose controls visible

## Read-Only Snapshot Check

- Candidate count before: `2`
- Candidate count after: `2`
- Approved Memory/Canon total before: `0`
- Approved Memory/Canon total after: `0`

## Safety Confirmations

- Evidence-only browser navigation and GET snapshots only.
- If backend or handoff packet data is unavailable, Playwright serves a read-only OMI apply-promotion fixture and blocks mutating API requests.
- No backend code changed by this script.
- No candidates were created by this script.
- Memory/Canon snapshot, bible JSON, and storyform JSON were compared before/after.
- No model/Ollama calls were made.
- Apply-promotion was not run during browser smoke.
- No generated prose controls were added by this script.
