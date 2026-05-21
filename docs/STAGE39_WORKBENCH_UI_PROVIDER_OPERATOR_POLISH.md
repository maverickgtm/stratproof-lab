# Stage 39 — Workbench UI Provider / Timezone / Operator Polish

This stage responds to the first full local workbench UX review.

## Fixed

- Timezone list now uses **Central America (UTC-6)** instead of exposing a country-specific Guatemala label.
- Provider selector now lists a broader connector map:
  - Bybit
  - Binance
  - OKX
  - Coinbase
  - Kraken
  - KuCoin
  - Bitfinex
  - Bitstamp
  - Deribit
  - Hyperliquid
  - CSV / local import
- The workbench clearly explains that only Bybit and Binance have live public OHLCV download in this Community preview; the other providers are connector roadmap/import targets.
- Operator controls are now dropdowns instead of free-text inputs, so users cannot type unsupported operators.
- Evidence result cards now wrap long verdicts like `NEEDS_MORE_DATA` without overflowing outside the card.
- The workbench server returns a clear provider-roadmap message instead of a traceback if a provider does not have a live downloader yet.

## Safety

This remains audit-only. The provider list is for market-data import and future connector planning only. No broker execution, account permissions, or live order placement are enabled.
