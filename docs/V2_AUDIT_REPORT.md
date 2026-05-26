# v2 Audit Report and Product Direction

## Audit Scope

This review covered the public README, release checks, Community Workbench, provider connector factory, local candle storage, audit-runner ingestion path, browser-facing dynamic rendering, GitHub CI, and the public product boundary.

## Corrected Findings

| Finding | Risk | v2 correction |
|---|---|---|
| OKX, Coinbase and Kraken were shown as Community-capable but could not download in the Workbench | Product promise did not match runtime behavior | Added three public historical-candle connectors, factory wiring and live Workbench options |
| Re-downloading overlapping history appended duplicate timestamps | Inflated samples can make audit evidence look stronger than it is | Replaced append-only storage with timestamp-keyed atomic merge |
| Live/incomplete provider candles could enter audits | Results can change after a candle closes | Reject OKX unconfirmed rows and Kraken's documented current final candle |
| A high RSI period could reference an uninitialized target during replay | A valid user formula could crash an audit | Fail closed when RSI cannot yet be calculated; regression test added |
| Dynamic report content used HTML rendering without escaping | Imported/local report content could render injected markup | Escape dynamic values in Workbench and Evidence Report Builder |
| Local Workbench could serve sensitive repository paths | Local exposure of Git metadata or environment files | Reject `.git` and `.env` paths and cap JSON request bodies |
| Release tests and generated launch metadata were pinned to v0.1 language | A healthy v2 build failed or published obsolete claims | Updated release preflight, launch generation, docs and CI |
| GitHub could classify the customized license file as `Other` | Weaker public trust and license visibility | Moved project notice to `NOTICE`; retained canonical AGPL text in `LICENSE` |

## v2 Implemented Capability

Community v2 provides an audit-only path from five public crypto candle feeds into the existing formula audit runner:

| Provider | Implemented public history path | Community market coverage |
|---|---|---|
| Bybit | Public kline feed | Spot and supported derivatives |
| Binance | Public spot / USD-M klines | Spot and USD-M |
| OKX | Public historical candles | Spot and USDT swap |
| Coinbase Exchange | Public candles | Spot |
| Kraken | Public OHLC | Spot |

No connector places orders or requires exchange trading credentials.

## Competitive Position

Large open-source competitors are already strong where StratProof should not pretend to win immediately:

- Freqtrade provides bot execution, backtesting, optimization, a web UI and broad exchange workflows.
- Jesse positions itself as a crypto trading framework for backtesting, optimization and live trading.
- Backtesting.py offers a compact general backtesting API, statistics and interactive visualization.

StratProof's defensible Community direction is different: an evidence-quality layer that tests whether the same hypothesis survives data-source variation, duplicate controls, chronological rules and honest report boundaries before anyone considers execution.

## Recommended Next Delivery

The highest-value next feature is a **Cross-Exchange Evidence Comparison** report:

1. Run one saved formula against two or more implemented venue caches.
2. Display sample count, winrate, Net R, drawdown and data warnings side by side.
3. Flag results that are strong on only one venue as venue-dependent evidence.
4. Export a reproducible comparison report with source, timeframe and dataset fingerprints.

That feature turns the new v2 connector work into a unique user action rather than simply a larger provider list.

## Evidence Boundary

StratProof Lab is a research and audit tool. Outputs are not financial advice, trade signals, guaranteed performance, or broker execution.
