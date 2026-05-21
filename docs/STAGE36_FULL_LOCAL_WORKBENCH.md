# Stage 36 — Full Local Workbench

Stage 36 adds a local browser workbench so StratProof Lab can be tested as a real product before GitHub publication.

## Launch

```bash
python3 scripts/launch_local_workbench.py
```

Then open:

```text
http://127.0.0.1:8765/app/auditor_dashboard/local_workbench.html
```

## What it tests

- public data setup using Bybit/Binance public OHLCV endpoints
- offline synthetic market cache generation
- visual formula creation
- portable formula JSON
- Idea Lab audit runner
- score threshold comparison
- Evidence report output paths
- saved ideas library
- local-only workflow from input to report

## Safety model

The workbench is local and audit-only. It does not place broker orders, send trading alerts, manage accounts, request withdrawal permissions, or promise returns.

## Recommended pre-GitHub use

1. Launch the local workbench.
2. Download public market history for a small symbol set.
3. Build a formula.
4. Run the audit.
5. Save the idea.
6. Open the generated Markdown and JSON reports.
7. Confirm the UI is clear enough for a new user.
