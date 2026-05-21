# Stage 27 — One-Command Public Demo Flow

Stage 27 adds a single local demo command for the Community Edition:

```bash
python scripts/run_public_demo.py
```

The demo is designed for GitHub users who want to understand StratProof Lab quickly without connecting broker accounts, API keys, or private data.

## What it does

1. Runs the public smoke test.
2. Generates synthetic multi-timeframe market data.
3. Runs an Idea Lab audit from a Formula Builder JSON.
4. Builds Evidence Report cards.
5. Exports indicator catalog, Formula Builder schema, Research Brain snapshot, GitHub assets, and pricing assets.
6. Writes a demo index at:

```text
reports/public_demo/DEMO_INDEX.md
```

## Safety model

The demo is audit-only by design.

It uses synthetic local data and does not place broker orders, connect customer accounts, publish signals, or provide financial advice.

## Main user story

```text
Clone repo
  ↓
Install requirements
  ↓
python scripts/run_public_demo.py
  ↓
Open reports/public_demo/DEMO_INDEX.md
  ↓
Open dashboard HTML screens in browser
```

## Why this matters

Before GitHub launch, StratProof Lab needs to be easy to try. A strong README is not enough. The project should give a new user a fast success path and show the whole product story:

```text
Formula idea → market data → audit runner → evidence report → visual research system
```
