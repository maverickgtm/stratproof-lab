# Stage 46 — Workbench Remove Button Layout Fix

This stage polishes the Local Workbench formula block layout before GitHub release.

## Fix

The formula block remove control no longer uses the full word `Remove`, which could overflow in narrow layouts. It is now a compact `×` button with accessible `aria-label` and tooltip text.

## Why

The Community workbench should feel clean on laptop screens. The compact remove button prevents clipped text and keeps the block editor aligned.

## Safety

- No broker execution.
- No live trading.
- No payment integration.
- UI polish only.
