# NCP schema/interface recovery for PHASE8-IMPL-025-T010F

This directory contains the repo-local real NCP schema/interface artifacts available for T010F read-only validation binding.

Recovered required files:

- schema/ncp-schema.json
- schema/ncp-schema.yaml
- package.json

Validator script surfaces were searched but unavailable in the local source copy:

- scripts/validate-schema.js
- scripts/validate-file.js

T010F remains forbidden from executing Node, npm, subprocess validators, network calls, or dependency installation. These artifacts are for read-only schema/interface identity and hash binding only.
