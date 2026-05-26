# StratProof Lab v2.0.0 Community Preview

StratProof Lab v2 turns the Community Workbench into a multi-exchange evidence environment. The project still does not execute trades or promise performance; it helps users challenge a formula against traceable public candle inputs before taking risk.

## Highlights

- Five implemented public historical-data connectors: Bybit, Binance, OKX, Coinbase Exchange, and Kraken.
- The same hypothesis can be researched across multiple crypto venues through one normalized OHLCV format.
- Local candle storage now merges overlapping downloads by timestamp instead of duplicating observations.
- OKX unconfirmed candles and Kraken's documented current candle are removed from stored audit inputs.
- Coinbase and Kraken are clearly limited to public spot candles in Community.
- The Local Workbench exposes the implemented connectors and applies basic dynamic-output escaping.
- Each formula audit offers up to three CSV audit-trail downloads: operation ledger, supporting candle path and eligible TradingView Portfolio replay import.
- The Local Workbench is redesigned as an Evidence Command Center with live provenance, audit-state and verification-pack status.
- Quick Audit reduces the first-user path to one action for synthetic walkthroughs or one audit action after public history is loaded, with immediate operations-CSV access.
- Hosted demos can opt into a visible daily CSV-download allowance while local Community keeps audit exports available without that quota.
- Evidence guidance now remains consistent when an audit exceeds its initial-review sample threshold.
- CI now tests connector parsing and the duplicate-safe cache policy.

## Safety Boundary

- Audit-only and local-first.
- No exchange API keys required for these public history downloads.
- No broker permissions, signals, order placement, live execution, or managed funds.
- TradingView Portfolio imports are visualization aids for eligible closed `LONG` spot historical replays, not independent trade execution confirmation.
- Public exchange endpoint availability, regional restrictions, rate limits, instrument coverage, and historical depth still apply.

## Quick Test

```bash
python scripts/launch_local_workbench.py
```

Choose a live Community provider, download public candles or generate offline demonstration data, build an idea, and compare strict evidence with relaxed discovery.
