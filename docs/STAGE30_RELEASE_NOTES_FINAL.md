# Release Notes — v0.1.0-community-preview

## StratProof Lab Community Preview

StratProof Lab is an evidence engine for trading strategies.

This first community preview focuses on a public, audit-only workflow:

- build a strategy idea with Formula Builder blocks
- import or generate market data
- run a demo audit
- generate Evidence Report cards
- inspect the Research Brain View
- review pricing and open-source boundaries
- run a one-command public demo

## Highlights

### Formula Builder

Create strategy ideas using visual blocks such as RSI, EMA filters, MACD, VWAP, ATR, relative volume, session filters, and score thresholds.

### Evidence Report Builder

Turn audit output into readable evidence cards covering verdict, honest winrate, Net R, drawdown, duplicate risk, leakage risk, truth confidence, and warnings.

### Research Brain View

A visual observability layer showing how the research system routes ideas through departments, gates, and evidence generation.

### Provider Connector Layer

Initial public architecture for market-data connectors, CSV imports, and future multi-market expansion.

### One-command demo

Run:

```bash
python scripts/run_public_demo.py
```

The demo generates synthetic market data, runs a sample audit, creates evidence output, and builds public demo assets.

## Safety model

Audit-only by design. Evidence before action. No guaranteed returns. No financial advice. No broker execution in Community.

## License

Community Edition is licensed under AGPL-3.0-or-later. Commercial licensing is available separately.
