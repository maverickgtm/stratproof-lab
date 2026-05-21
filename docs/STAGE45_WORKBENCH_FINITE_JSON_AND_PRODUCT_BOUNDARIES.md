# Stage 45 — Workbench Finite JSON + Community/Pro Boundary Polish

Stage 45 fixes a real workbench issue found during manual testing: a relaxed audit could produce an infinite profit factor when a symbol had wins and zero losses. Python can serialize that as `Infinity`, but browser JSON parsing rejects it. The workbench now sanitizes every API payload and report file so all JSON is standards-compliant.

## Fixes

- Replaces infinite profit factor with `null` / undefined sample context.
- Rejects non-finite numeric user inputs before audit evaluation.
- Forces strict JSON output with `allow_nan=False`.
- Sanitizes workbench API responses recursively before returning them to the browser.
- Keeps audit-only behavior intact.

## Product boundary note

The public Community edition is intentionally useful enough to demonstrate the product:

- visual formula builder
- local workbench
- strict audit
- relaxed discovery audit
- visual evidence reports
- Bybit/Binance basic public history downloader
- saved ideas local workflow

Paid editions should be more complete, not just artificially unlocked:

- longer historical windows
- batch audits
- advanced walk-forward
- stronger regime/session analysis
- richer report exports
- team workspaces
- more live connectors/importers
- Pro/Enterprise evidence workflows

Community is the proof-of-value. Pro/Team/Enterprise are the productivity and scale layers.
