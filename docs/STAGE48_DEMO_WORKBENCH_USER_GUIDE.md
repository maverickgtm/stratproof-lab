# Stage 48 — Community Demo Workbench User Guide

This guide explains how a new user should test StratProof Lab Community before GitHub release.

## What this Community demo is

The Community demo is a local audit workbench. It lets a user build a trading hypothesis, import or generate market data, run an audit, compare strict vs relaxed evidence, and open a visual evidence report.

It is **audit-only by design**. It does not place trades, connect to broker execution, publish signals, or manage funds.

## Offline demo cache vs public history

### Generate offline demo cache

Use this when you want a quick first test without relying on internet, exchange availability, API limits, or regional blocking.

The offline cache is **synthetic demo data** generated locally. It is useful for testing the workflow, UI, reports, and formula builder. It should not be treated as real market evidence.

Use it for:

- first-time testing
- UI review
- explaining the workflow
- checking that reports generate correctly
- testing formulas without waiting for downloads

### Download public history

Use this when you want to audit against real public exchange candles.

Community currently supports live public downloads for Bybit and Binance. Other providers are listed as roadmap/import targets unless implemented later.

Use it for:

- real market candle audits
- testing a formula on actual exchange data
- checking specific symbols and timeframes
- comparing how the same formula behaves on different market conditions

Important: Public history downloads depend on exchange availability, network access, symbols supported by the exchange, and candle limits.

## Correct workbench order

Open the workbench:

```bash
python3 scripts/launch_local_workbench.py
```

Then follow this order:

1. Choose provider.
   - Use `bybit` or `binance` for public downloads.
   - Use offline demo cache for UI-only testing.

2. Choose symbols.
   - Select common symbols from the checkbox list.
   - Add custom symbols manually only when the provider supports them.

3. Choose timeframe and BTC context timeframe.
   - Example: main timeframe `5m`, BTC context `15m`.

4. Choose days and limit.
   - For quick tests, use 5–10 days.
   - For stronger evidence, use more history when available.

5. Load data.
   - Click **Generate offline demo cache** for synthetic local data.
   - Or click **Download public history** for real public candles.

6. Build the formula.
   - Choose side: LONG or SHORT.
   - Add indicator blocks: RSI, BTC EMA, Relative Volume, EMA.
   - Configure operator, value/period, and timeframe/lookback.

7. Click **Build JSON**.
   - This creates the portable formula JSON from visual controls.
   - The JSON can be inspected or copied.

8. Click **Run strict audit**.
   - This runs the exact formula as configured.
   - It is the evidence that matters most.

9. Click **Run relaxed audit** or **Run strict + relaxed**.
   - Relaxed audit is only for sample-size discovery.
   - It helps identify whether strict filters are starving the sample.

10. Review **Evidence Guidance** and **Strict vs Relaxed Evidence Ladder**.
    - If strict has low sample but relaxed has high sample, loosen one filter at a time.
    - If both are weak, the idea likely has poor evidence.

11. Open reports.
    - Open visual evidence report.
    - Open Markdown report.
    - Open JSON report.
    - Open threshold comparison.

12. Save useful ideas.
    - Use **Save Idea** after building a formula worth revisiting.

## Area guide

### Area 1 — Data Setup

This area chooses data source, symbols, timeframe, history window, and download/cache method.

- Provider: data source.
- Symbols: pairs to audit.
- Main timeframe: candle timeframe used for the audited symbols.
- BTC context timeframe: timeframe used for BTC trend/context block.
- Days: requested history window.
- Limit: maximum candles requested per symbol.

### Area 2 — Formula Builder

This area builds the audit idea.

- Side: LONG or SHORT in Community.
- LONG + SHORT comparison is a Pro preview.
- Indicator blocks are toggles. First click adds; second click removes.
- Operators are dropdowns to avoid invalid formulas.
- Build JSON creates the portable formula.

### Area 3 — Evidence Results

This area shows the latest audit results.

- Verdict: current research verdict.
- Winrate: honest closed-outcome winrate.
- Net R: simple win/loss R proxy.
- Evidence guidance: explains why more data may be needed.
- Strict vs relaxed ladder: compares original formula vs discovery probe.
- Latest reports: opens visual/Markdown/JSON/threshold outputs.
- Symbol results: shows per-symbol outcome summaries.

## How to explain strict vs relaxed

Strict audit uses the exact formula. It answers:

> Did this exact idea have enough evidence?

Relaxed audit loosens filters to diagnose sample-size starvation. It answers:

> Is there market behavior nearby worth investigating?

Relaxed results are not promotion evidence. They are discovery evidence.

## Why LONG and SHORT can differ

LONG and SHORT are different hypotheses even with the same indicators.

LONG asks whether the conditions work for upward TP/SL logic.
SHORT asks whether the conditions work for downward TP/SL logic.

Differences can come from market regime, directional bias, volatility, session behavior, symbol trend, and the fact that TP/SL are mirrored.

In Pro, this becomes Side Comparison: LONG vs SHORT, best side by symbol, session, and regime.

## Community vs Pro expectation

Community should demonstrate the product:

- build formulas
- import/generate data
- run strict and relaxed audits
- view reports
- save ideas locally

Pro should add deeper research:

- LONG + SHORT side comparison
- batch audits
- walk-forward validation
- regime/session analytics
- more providers
- premium reports
- PDF exports
- workspaces
- strategy/version ranking

## Pre-GitHub demo checklist

Before publishing, test:

- offline cache generation
- public history download for Bybit
- public history download for Binance
- formula builder with RSI/BTC EMA/Relative Volume/EMA
- LONG audit
- SHORT audit
- strict + relaxed ladder
- visual evidence report
- Markdown report
- save idea / refresh saved ideas
- invalid or partial formula handling
- no `Infinity` or `NaN` in browser JSON
- no layout overflow on MacBook screen
