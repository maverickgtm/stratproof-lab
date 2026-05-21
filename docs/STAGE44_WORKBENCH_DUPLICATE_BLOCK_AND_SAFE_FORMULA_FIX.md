# Stage 44 — Workbench Duplicate Block Toggle + Safe Formula Handling

## Purpose

Stage 44 polishes the Local Workbench before GitHub by fixing two real usability issues found during manual formula testing:

1. Clicking the same indicator button repeatedly created duplicate RSI/EMA/RVOL/BTC_EMA blocks.
2. Some partially edited or unusual formula configurations could trigger raw backend type errors during audit.

## Changes

### Indicator buttons now toggle blocks

Formula Builder buttons now behave like on/off toggles:

- Click `+ RSI` once: add RSI block.
- Click `+ RSI` again: remove RSI block.
- Same behavior for BTC EMA, Relative Volume, and EMA.

This prevents accidental duplicate blocks and makes the Community workbench easier for non-technical users.

### Safer formula parsing

The audit engine now handles missing or invalid numeric values more defensively:

- missing RSI value no longer crashes the audit
- missing EMA period defaults safely
- missing Relative Volume multiplier defaults safely
- invalid score threshold falls back safely

Invalid/missing values fail the affected condition instead of crashing the whole audit.

## Validation

- Python compile: PASS
- Public smoke test: PASS
- Final GitHub preflight: PASS
- Bad/partial formula audit: PASS without raw `NoneType` crash

## Safety

No execution, broker integration, real funds, signal publishing, or strategy promotion was added. This remains audit-only by design.
