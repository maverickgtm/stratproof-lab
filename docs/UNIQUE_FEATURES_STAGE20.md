# Stage 20 — Unique Features We Should Own

## Goal

The product must not be perceived as another bot or another generic backtester.

It should own a distinct promise:

> Strategy evidence quality.

## Features that help us stand out

### 1. Evidence Score

A single explainable score that summarizes whether a strategy result is trustworthy.

Inputs may include:

- sample size,
- duplicate risk,
- leakage risk,
- drawdown,
- Net R,
- threshold stability,
- symbol/session concentration,
- out-of-sample degradation,
- regime dependency.

### 2. Truth Engine

A subsystem that reviews whether the audit result may be misleading.

Examples:

- same candle TP/SL ambiguity,
- lookahead risk,
- future context contamination,
- duplicated/clustering signals,
- unrealistic fills,
- missing cost model.

### 3. Quality Gates

Verdict gates that can block or warn a strategy even if winrate looks attractive.

Examples:

- BLOCKED_WEAK_SAMPLE
- WATCH_DUPLICATE_RISK
- REJECT_LEAKAGE_RISK
- PROMISING_NEEDS_WALK_FORWARD
- PASS_RESEARCH_ONLY

### 4. Research University

A named workflow that makes the product feel bigger than a script:

- Data Setup Department
- Formula Builder
- Idea Lab
- Truth Engine
- RiskGuard
- Evidence Reports
- Provider Connector Layer
- Research Brain View

### 5. Research Brain View

A visual-only observability screen that makes the internal workflow understandable and attractive.

### 6. Multi-language evidence reports

Not only UI translations. The long-term differentiator is reports in the user's language.

Initial languages:

- English
- Spanish
- Portuguese
- German

### 7. Multi-market data model

Crypto first, but normalized schemas allow future expansion into forex, equities, futures, options, and custom CSV datasets.

## Product sentence

StratProof Lab is the evidence layer that other trading systems are missing.

