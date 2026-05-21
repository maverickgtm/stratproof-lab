# Stage 26 — Payments Roadmap

## Payment philosophy

> Card-first for trust. Crypto-ready for global traders.

StratProof Lab should support traditional checkout for trust and enterprise readiness, while also supporting crypto payments for the trading-native audience.

## Phase 1 — Early Access

Use a simple checkout provider for early sales and manual onboarding.

Recommended options:

- Lemon Squeezy
- Gumroad
- Paddle
- PayPal invoice
- Manual USDC/USDT invoice for crypto-native customers

Output after payment:

- email receipt
- license key or access code
- onboarding instructions
- support contact

## Phase 2 — Pro subscription

Add recurring billing:

- Stripe Billing or Paddle for subscriptions
- monthly and annual plans
- customer portal
- license key generation
- cancellation and renewal workflow

## Phase 3 — Crypto checkout

Add crypto checkout or invoice workflow:

- USDC / USDT preferred for stable pricing
- BTC / ETH optional
- wallet/manual invoice at first
- provider-based checkout later if available in target jurisdictions

Possible providers to evaluate:

- BitPay
- Coinbase Commerce / Coinbase Business availability
- NOWPayments
- BTCPay Server
- CoinPayments

## Phase 4 — Enterprise invoice

Enterprise should support:

- invoice by contract
- bank transfer
- card payment
- stablecoin settlement
- annual contract
- custom terms

## Important boundary

The Community repo must not contain live payment secrets, private API keys, checkout tokens, webhook secrets, or production license servers.
