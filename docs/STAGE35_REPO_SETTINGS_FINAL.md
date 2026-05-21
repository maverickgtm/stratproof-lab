# Stage 35 — Recommended GitHub Repository Settings

## About section

Description:

```text
Evidence engine for trading strategies — audit ideas, detect weak backtests, and generate research reports before risking capital.
```

Website:

```text
Leave blank until landing page exists.
```

Topics:

```text
trading, backtesting, quant, crypto, strategy-audit, algorithmic-trading, risk-management, technical-analysis, trading-strategies, open-source, python, research, finance, market-data, agpl
```

## Features

Enable:

- Issues
- Discussions, optional after first release
- Security advisories

Disable initially:

- Wiki, unless documentation grows outside docs/
- Sponsorship until payment/funding links are finalized

## Branch protection

After first push, protect `main`:

- Require pull request before merging
- Require status checks once CI runs reliably
- Do not allow force pushes

## Release label

Use:

```text
v0.1.0-community-preview
```

