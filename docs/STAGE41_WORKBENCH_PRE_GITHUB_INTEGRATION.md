# Stage 41 — Workbench Pre-GitHub Integration Polish

This stage integrates final workbench improvements discovered during real local use before GitHub publication.

## Changes

- Added a combined **Run strict + relaxed** button.
- Added safe JSON recovery: if a user edits portable JSON incorrectly, the workbench rebuilds from visual controls instead of failing with a raw JSON parse error.
- Expanded provider dropdown to include more visible roadmap/import targets.
- Replaced visible Guatemala-specific timezone option with **Central America (UTC-6)**.
- Improved operator dropdown labels so users cannot type unsupported free-text operators.
- Improved grid/card CSS to reduce clipped operators and overflowing verdict cards.
- Evidence ladder now shows strict/relaxed known, WR, Net R, and verdict with `not run` labels instead of confusing dashes.

## Safety

Still audit-only. No broker execution, no live trading, no secrets, no real funds.
