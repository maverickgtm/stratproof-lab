# Stage 26 — Crypto Payment Policy

## Supported concept

StratProof Lab can support crypto payments without turning the product into a custody system.

The recommended initial approach is:

- manual invoice
- fixed stablecoin amount
- supported networks clearly stated
- no custody of customer funds inside StratProof Lab
- no wallet private keys in the software repository

## Preferred assets

Recommended first assets:

- USDC
- USDT

Optional later:

- BTC
- ETH

## Why stablecoins first

Stablecoins reduce pricing confusion. A $290 annual subscription should not become unclear because of BTC/ETH volatility during checkout.

## Risk controls

- Always specify exact network, for example Ethereum, Polygon, Arbitrum, Tron, or Base.
- Warn users not to send on unsupported networks.
- Do not store private keys in the app.
- Do not build wallet custody into the Community edition.
- Manual crypto orders should be verified before license activation.
- Keep invoices and accounting records.

## Public wording

> Crypto payments may be supported for eligible customers through manual invoice or approved checkout partners. Availability depends on region, compliance requirements, and provider support.

## Not included

- no investment pooling
- no custody service
- no exchange service
- no managed accounts
- no financial advice
