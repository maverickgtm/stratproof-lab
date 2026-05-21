# Stage 49 — Community Demo QA + BTC Context Download Fix

This stage records the final Community demo QA findings from local Mac testing and fixes a confusing data setup edge case.

## Fix

When users selected `BTCUSDT` inside the main symbol list and also used the `BTC_EMA` block with a BTC context timeframe such as `15m`, the workbench only downloaded `BTCUSDT` for the main timeframe. This could make an audit return `known=0` even after public history download succeeded.

The workbench now always downloads `BTCUSDT` for the BTC context timeframe when needed, even if `BTCUSDT` is already included in the main symbol list.

## Why this matters

A user may reasonably ask why a formula returns no evidence after data was downloaded. The answer can be either:

- the formula is too strict,
- the selected side is not favored by the market regime,
- the session/timeframe has too few matching candles,
- or the BTC context file was missing.

Stage 49 removes the BTC-context missing-file edge case from normal usage.

## Community demo QA checklist

Before GitHub release, test:

1. Generate offline demo cache.
2. Download Bybit public history.
3. Download Binance public history.
4. Include BTCUSDT in the main symbols with BTC context timeframe different from main timeframe.
5. Run strict audit.
6. Run relaxed audit.
7. Run strict + relaxed evidence ladder.
8. Open visual evidence report.
9. Open Markdown report.
10. Open JSON report.
11. Open threshold comparison.
12. Toggle blocks on and off.
13. Test LONG and SHORT separately.
14. Confirm LONG + SHORT comparison remains Pro preview in Community.

## Expected behavior

Community can run one side at a time and one formula at a time. It can show whether a formula is promising, not ready, or needs more data. It should not guarantee returns, send signals, connect to brokers, or execute orders.
