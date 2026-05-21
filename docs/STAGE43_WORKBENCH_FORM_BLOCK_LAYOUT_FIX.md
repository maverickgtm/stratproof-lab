# Stage 43 — Workbench Formula Block Layout Fix

This stage polishes the Local Workbench formula block editor after real Mac visual testing.

## Fixes

- Replaces the generic `Lookback/TF` free text field with a clearer contextual control.
- RSI, EMA, and BTC EMA blocks now use a timeframe dropdown.
- Relative Volume blocks now use a numeric lookback-bars input.
- Formula block grid columns were compacted to prevent right-side clipping on laptop screens.
- Block labels now truncate safely instead of overflowing.
- Inputs inside block rows use smaller padding/font sizing for better fit.

## Product impact

Users can build formulas visually without guessing whether a field expects a timeframe or a numeric lookback. This keeps Community usable and reduces invalid formulas before GitHub launch.
