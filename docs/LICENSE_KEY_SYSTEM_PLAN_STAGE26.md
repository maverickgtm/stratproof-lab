# Stage 26 — License Key System Plan

## Goal

Create a simple license system for Pro features without putting commercial secrets into the Community repository.

## License states

- community
- pro_early_access
- pro_plus
- team
- enterprise
- trial
- expired

## Suggested license payload

```json
{
  "license_id": "sp_...",
  "plan": "pro_plus",
  "customer_email_hash": "...",
  "issued_at": "2026-01-01T00:00:00Z",
  "expires_at": "2027-01-01T00:00:00Z",
  "features": ["advanced_reports", "batch_audits"],
  "signature": "..."
}
```

## Recommended architecture

Community repo:

- reads local license file
- checks signed payload
- unlocks local features if valid
- works without secrets

Private commercial service:

- creates license keys
- stores customers
- handles payment webhooks
- rotates signing keys
- disables/refunds/renews licenses

## Never publish

- private signing key
- payment webhook secret
- customer database
- checkout provider secrets
- production license server credentials

## Community boundary

The Community edition should remain useful without a license. License keys should unlock convenience, scale, advanced reports, team features, premium connectors, or SaaS workflows — not basic educational value.
