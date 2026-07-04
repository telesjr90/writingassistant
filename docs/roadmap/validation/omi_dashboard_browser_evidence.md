# OMI Dashboard Browser Evidence

- Result: **PASS**
- Exit code: `0`
- Started: `2026-07-04T05:44:00.855Z`
- Finished: `2026-07-04T05:44:04.466Z`
- App base URL: `http://localhost:5173`
- Project ID: `example`
- API mode: `live-backend`
- Evidence directory: `docs/roadmap/validation/omi-dashboard-browser-evidence`
- Workflow log: `docs/roadmap/validation/omi-dashboard-browser-evidence/workflow-log.json`

## Screenshots

- Desktop: `docs/roadmap/validation/omi-dashboard-browser-evidence/screenshots/01-desktop-omi-dashboard.png`
- Mobile: `docs/roadmap/validation/omi-dashboard-browser-evidence/screenshots/02-mobile-omi-dashboard.png`

## Assertions

- PASS: desktop: OMI Dashboard is reachable
- PASS: desktop: active project label visible
- PASS: desktop: OMI boundary banner visible
- PASS: desktop: candidate/canon status strip visible
- PASS: desktop: dense workflow rows visible
- PASS: desktop: Approved Memory/Canon snapshot visible
- PASS: desktop: Apply to Memory/Canon disabled
- PASS: desktop: disabled apply reason visible
- PASS: desktop: apply reason associated with disabled control
- PASS: desktop: apply reason text matches expected boundary
- PASS: desktop: approved Memory/Canon snapshot is visually separate from OMI counts
- PASS: desktop: no generated prose controls visible
- PASS: opening dashboard does not create candidates
- PASS: opening dashboard does not mutate approved Memory/Canon snapshot
- PASS: opening dashboard performs no mutating API requests
- PASS: mobile: OMI Dashboard is reachable
- PASS: mobile: active project label visible
- PASS: mobile: OMI boundary banner visible
- PASS: mobile: candidate/canon status strip visible
- PASS: mobile: dense workflow rows visible
- PASS: mobile: Approved Memory/Canon snapshot visible
- PASS: mobile: Apply to Memory/Canon disabled
- PASS: mobile: disabled apply reason visible
- PASS: mobile: apply reason associated with disabled control
- PASS: mobile: apply reason text matches expected boundary
- PASS: mobile: approved Memory/Canon snapshot is visually separate from OMI counts
- PASS: mobile: no generated prose controls visible
- PASS: mobile: stacked workflow row layout visible

## Read-Only Snapshot Check

- Candidate count before: `2`
- Candidate count after: `2`
- Approved Memory/Canon total before: `0`
- Approved Memory/Canon total after: `0`

## Safety Confirmations

- Evidence-only browser navigation and GET snapshots only.
- If the backend is unavailable, Playwright serves a read-only zero-state API fixture and blocks mutating API requests.
- No backend code changed by this script.
- No candidates were created by this script.
- Memory/Canon snapshot, bible JSON, and storyform JSON were compared before/after.
- No model/Ollama calls were made.
- Apply-promotion was not run and the dashboard apply control remained disabled.
- No generated prose controls were added by this script.
