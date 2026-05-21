# Stage 38 — Workbench Evidence UX + Sample Sufficiency Fix

Stage 38 improves the local Workbench after a real Mac test showed the full pipeline worked, but a strict formula could return `NEEDS_MORE_DATA` with zero known outcomes without enough explanation.

## What changed

- Added sample sufficiency diagnostics to Idea Audit reports.
- Added Markdown sections:
  - `Why this report needs more data`
  - `Next recommended tests`
- Added a Workbench `Run relaxed audit` button.
- Added `/api/relaxed_audit` for discovery-only sample-size probing.
- Increased the offline Workbench demo cache default from 420 rows to 2400 rows.
- Improved Workbench evidence guidance panel so users understand why a formula returned too few outcomes.

## Important safety boundary

Relaxed audit is only for discovery. It does not replace the user's strict formula. Final evidence must be rerun with the original strict conditions.

## Validation

- Python compile: PASS
- Smoke test: PASS
- Public demo: PASS
- Final GitHub preflight: PASS
- Blockers: 0
- Warnings: 0
