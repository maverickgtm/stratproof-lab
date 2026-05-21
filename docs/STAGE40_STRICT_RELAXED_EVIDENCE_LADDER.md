# Stage 40 — Strict vs Relaxed Evidence Ladder

This stage integrates the local workbench feedback from real Mac testing before GitHub publication.

## Why

A strict strategy can return `NEEDS_MORE_DATA` with zero or very few known outcomes, while a relaxed discovery probe may find hundreds of cases. That difference is useful evidence: it tells the user that the original formula may be too restrictive, not necessarily impossible.

## What changed

- Added a **Strict vs Relaxed Evidence Ladder** panel to the Local Workbench.
- The workbench now remembers the last strict audit and the last relaxed audit.
- It compares strict known outcomes vs relaxed known outcomes.
- It explains whether the formula is likely starving the sample, needs more history/symbols, or has enough data for comparison.

## Safety

Relaxed audits remain discovery-only. Final evidence must be produced with the original strict formula.
