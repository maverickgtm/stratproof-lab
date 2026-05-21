# Stage 27 Test Report

Status: `PASS`

Executed:

```bash
python scripts/run_public_demo.py
python -m compileall app scripts tests
python tests/smoke_test_public_package.py
```

## One-command demo result

```text
PUBLIC_DEMO_STATUS=PASS
DEMO_INDEX=reports/public_demo/DEMO_INDEX.md
DEMO_SUMMARY_JSON=reports/public_demo/demo_run_summary.json
```

## Steps verified

- Public smoke test: PASS
- Synthetic multi-timeframe data generation: PASS
- Idea Lab multi-timeframe audit: PASS
- Evidence Report cards: PASS
- Indicator catalog export: PASS
- Formula Builder schema export: PASS
- Research Brain snapshot: PASS
- GitHub helper assets export: PASS
- Pricing assets export: PASS

## Safety

The demo uses synthetic local data and remains audit-only by design. It does not connect broker accounts, request payment credentials, publish signals, or place trades.
