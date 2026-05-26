# Changelog

All notable public changes to StratProof Lab will be documented here.

## v2.0.0-community-preview

### Added

- Live public historical OHLCV downloads for OKX, Coinbase Exchange, and Kraken alongside Bybit and Binance.
- Connector validation tests for normalized candle parsing and completed-candle safeguards.
- An evidence-integrity cache merge policy that prevents repeated downloads from duplicating candle timestamps.
- Live provider selection in the local Workbench for all five implemented Community connectors.
- A three-file audit trail export pack: detected operations, supporting candle paths, and eligible TradingView Portfolio replay rows.
- A redesigned Evidence Command Center interface that surfaces provenance, audit state and verification exports as the primary user workflow.
- A one-click Quick Audit path with immediate operations-CSV verification and an optional hosted-demo daily export allowance.
- An in-product TradingView Portfolio visual-cross-check guide and direct replay CSV action for compatible audit results.
- A compact evidence-and-recipe entry flow with expandable advanced controls for assets, data inputs, formula blocks and portable JSON.

### Fixed

- Kraken's documented current, uncommitted OHLC candle is excluded from audit inputs.
- OKX unconfirmed candles are excluded from audit inputs.
- Community provider claims now match implemented downloaders.
- Dynamic Workbench report and saved-idea fields are escaped before HTML rendering.
- Evidence guidance no longer describes samples above the initial-review threshold as undersized.
- Comprehensive-product checks validate current README language and new connector tests run in CI.
- The project notice is separated from canonical AGPL text so repository hosts can identify the license cleanly.

### Boundaries

- Public data import remains audit-only: no API keys, order placement, signals, or broker execution.
- Coinbase and Kraken Community downloads are spot-only; OKX supports public spot and USDT swap candle inputs.
- TradingView-format exports visualize eligible closed `LONG` spot replays; they do not independently validate formula logic or prove executed trades.

## v0.1.0-community-preview

Initial community preview release.

### Added

- Premium GitHub README positioning StratProof Lab as an evidence engine for trading strategies.
- One-command public demo flow: `python scripts/run_public_demo.py`.
- Formula Builder UI for assembling audit ideas from visual blocks.
- Evidence Report Builder UI with honest winrate, Net R, drawdown, duplicate risk, leakage risk, and verdict cards.
- Research Brain View / Strategy Intelligence Center for visual observability of the Research University.
- Public Provider Connector Layer with Bybit/Binance public data support, CSV import, and multi-market roadmap.
- Idea Lab Backtest Runner with research cache, dataset fingerprinting, and demo reports.
- Multi-timeframe BTC context engine and score threshold simulator.
- Indicator Block Library with RSI, EMA, MACD, VWAP, ATR, relative volume, Bollinger, session filters, and funding/open-interest placeholders.
- Multilingual UI foundation: English, Spanish, Portuguese, and German.
- Community/Pro/SaaS monetization strategy, pricing assets, and payment roadmap.
- AGPL-3.0-or-later license, dual-license policy, trademark policy, open-source boundaries, premium module boundaries, security policy, contributing guide, roadmap, and notice.

### Safety model

- Audit-only by design.
- Evidence before action.
- No broker execution in Community.
- No guaranteed returns.
- No financial advice.

### Known limits

- This is a community preview, not a production SaaS.
- Screenshots are public demo/concept assets generated for GitHub presentation.
- Enterprise connectors are roadmap items unless explicitly implemented.
