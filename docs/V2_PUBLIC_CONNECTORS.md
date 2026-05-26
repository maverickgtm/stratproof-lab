# v2 Public Connector Evidence Policy

StratProof Lab Community imports historical public candles for research audits. It does not authenticate trading accounts, place orders, publish signals, or manage funds.

## Implemented Community connectors

| Provider | Public endpoint family | Community markets | Completed-candle control |
|---|---|---|---|
| Bybit | V5 market kline | Spot, linear and inverse where supported by the venue | Normalized candle input |
| Binance | Spot and USD-M kline | Spot and USD-M futures | Normalized candle input |
| OKX | V5 market history-candles | Spot and USDT swap | Rows with `confirm != 1` are excluded |
| Coinbase Exchange | Public product candles | Spot only | Public historical buckets |
| Kraken | REST public OHLC | Spot only | Documented current final candle is excluded |

## Evidence integrity

Real candle downloads are stored in a local normalized CSV cache. Version 2 changes storage from append-only writes to a timestamp-keyed merge. Downloading overlapping history again updates the existing timestamp instead of adding a duplicate observation to later audits.

This is important because a duplicate candle can inflate sample size and overstate confidence without adding new market evidence.

## Provider limits

Public feeds are subject to venue availability, regional access, endpoint rate limits, supported instruments, and historical depth. A connector being implemented does not promise that every symbol or history range is available from that provider.

## Source documentation

- OKX REST market data API: <https://www.okx.com/docs-v5/en/#rest-api-market-data-get-candlesticks-history>
- Coinbase Exchange REST candles API: <https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles>
- Kraken REST OHLC API: <https://docs.kraken.com/api/docs/rest-api/get-ohlc-data/>
