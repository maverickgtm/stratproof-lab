# Stage 48 — Community Demo Workbench User Guide

This guide explains how a new user should test StratProof Lab Community before GitHub release.

## What this Community demo is

The Community demo is a local **Evidence Command Center**. It lets a user build a trading hypothesis, import or generate market data, run an audit, compare strict vs relaxed evidence, open a visual report, and download the operations and candle paths behind the result.

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

Community v2 supports live public downloads for Bybit, Binance, OKX, Coinbase Exchange, and Kraken. Coinbase and Kraken downloads are spot-only. OKX supports spot and USDT swap candles. Other providers remain roadmap/import targets unless explicitly implemented later.

Downloaded candle history is merged by timestamp, so rerunning the same range does not inflate a backtest sample with duplicates. OKX unconfirmed candles and Kraken's current uncommitted candle are excluded before audit input is stored.

Use it for:

- real market candle audits
- testing a formula on actual exchange data
- checking specific symbols and timeframes
- comparing how the same formula behaves on different market conditions

Important: Public history downloads depend on exchange availability, network access, symbols supported by the exchange, and candle limits.

## Correct Evidence Command Center order

Open the workbench:

```bash
python3 scripts/launch_local_workbench.py
```

### Fast path for a first-time user

1. Click **Try demo + audit**.
   - This creates clearly labeled synthetic data, builds the default visual formula and runs a strict audit in one action.
   - It is a workflow demonstration, not real market evidence.

2. Review the result and click **Download operations CSV**.
   - This is the shortest path from an idea to inspectable replay detections.
   - If **Download TradingView replay CSV** appears, it can be imported into TradingView Portfolio for a visual cross-check of eligible replay entries and exits.

3. When ready for real evidence, choose a live provider, click **Download public history**, adjust the formula and click **Audit current formula + prepare CSV**.
   - JSON is built automatically from the visual controls.

### Detailed research path

Follow this order when deliberately modifying every input:

1. Choose provider.
   - Use `bybit`, `binance`, `okx`, `coinbase`, or `kraken` for public downloads.
   - Choose `spot` for Coinbase or Kraken.
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

7. Optionally click **Build JSON**.
   - This creates the portable formula JSON from visual controls.
   - The JSON can be inspected or copied.
   - Quick Audit builds it automatically, so most users can skip this step.

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

12. Download the audit trail.
    - Download the detected operations ledger CSV.
    - Download the linked source candle-path CSV.
    - For eligible closed `LONG` spot replays, download the TradingView Portfolio replay CSV for chart visualization.
    - These exports document historical replay detections, not executed account trades.

### Checking a Replay in TradingView

TradingView Portfolio supports transaction import from a CSV file. When StratProof offers a non-empty **TradingView replay CSV**:

1. Download it from the Audit Trail panel.
2. Open a TradingView Portfolio and go to its **Transactions** tab.
3. Use the import action and upload the CSV.
4. Prefer merging transactions unless replacing an existing portfolio is intentional.
5. Compare displayed buy/sell events to StratProof's operations ledger and source candle-path CSV.

TradingView is a visual cross-check, not a formula auditor. It does not recalculate indicators, score thresholds or condition traces, and an imported replay is not proof of a real executed trade. TradingView documents a 25 MB upload maximum and imports only supported instruments.

Official instructions:

- [TradingView transaction file import](https://www.tradingview.com/support/solutions/43000756014-how-to-add-transactions-via-file-import/)
- [TradingView Portfolio CSV formatting](https://www.tradingview.com/support/solutions/43000756010-how-to-create-a-portfolio-via-transaction-import/)

13. Save useful ideas.
    - Use **Save Idea** after building a formula worth revisiting.

## Area guide

### Command status rail

The top status rail makes the evidence workflow explicit:

- Input provenance tells the user whether public history has been loaded or the workflow is using synthetic demo inputs.
- Audit engine shows whether the strict or discovery audit is running and how many outcomes closed.
- Verification pack reports when the maximum-three CSV audit trail is ready.

### CSV access and hosted demo boundary

The local open-source Community workbench keeps audit-trail CSV downloads available without a daily quota. This is important because verification should remain useful to GitHub users.

For a separately hosted public demo, the server can disclose and enforce a free daily CSV allowance:

```bash
STRATPROOF_HOSTED_DEMO_DAILY_CSV_LIMIT=3 python3 scripts/launch_local_workbench.py
```

In that mode the dashboard displays how many free CSV downloads remain for the UTC day and offers a Pro preview when the allowance is exhausted. This repository does not include checkout, accounts or paid entitlement activation.

### Area 1 — Data Setup

This area chooses data source, symbols, timeframe, history window, and download/cache method.

- Provider: data source.
- Live Community providers: Bybit, Binance, OKX, Coinbase Exchange, and Kraken.
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
- Audit Trail Downloads: exports no more than three CSV files for operation-level and candle-level verification.
- Quick Audit: automatically builds the current visual formula, runs the strict audit and exposes the primary operations CSV download.
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
- public history download for each live connector supported in the test region
- repeated history download without duplicate timestamps
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
