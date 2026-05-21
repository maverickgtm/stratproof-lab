# Stage 51 Final Community Demo QA Checklist

Use this checklist before publishing the Community repo.

## Data setup

- [x] Offline demo cache works.
- [x] Bybit download works.
- [x] Binance download works.
- [x] BTC context timeframe is downloaded separately.
- [x] Custom symbols can be typed manually.
- [x] Roadmap providers do not throw raw errors.

## Formula Builder

- [x] LONG works.
- [x] SHORT works.
- [x] Pro-only LONG + SHORT option is visible but locked.
- [x] RSI block toggles on/off.
- [x] BTC EMA block toggles on/off.
- [x] Relative Volume block toggles on/off.
- [x] EMA block toggles on/off.
- [x] Operators are dropdowns, not free-text.
- [x] Numeric fields are sanitized.
- [x] JSON rebuild is safe.

## Evidence

- [x] Strict audit works.
- [x] Relaxed audit works.
- [x] Strict + relaxed ladder works.
- [x] Visual report opens.
- [x] Markdown report opens.
- [x] JSON report opens.
- [x] Threshold comparison opens.
- [x] Needs-more-data cases are explained.
- [x] Promising research-only cases are not promoted as trading signals.

## Pro Preview

- [x] Pro Preview section is visible.
- [x] Pro buttons do not execute paid features.
- [x] Pro preview explains what the paid edition unlocks.
- [x] Community remains usable after preview.

## GitHub

- [x] README explains Community usage flow.
- [x] License is present.
- [x] No secrets.
- [x] No database dumps.
- [x] No private keys.
- [x] Audit-only positioning remains clear.
