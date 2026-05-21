# Stage 37 — Local Workbench UX Fix

Stage 37 fixes issues found during real Mac testing of the Local Workbench.

## Fixes

1. `Download public history` no longer fails with `ModuleNotFoundError: No module named 'app'` when scripts are executed from the workbench server.
2. `scripts/stage11_download_history.py` can now be run directly from the repository root without manual `PYTHONPATH` setup.
3. Workbench subprocess calls now inject the project root into `PYTHONPATH`.
4. `Build JSON` now writes a visible log entry so users know the formula JSON was rebuilt.
5. After `Run Audit`, the workbench now clearly displays latest report links:
   - Markdown report
   - JSON report
   - Threshold comparison
6. Audit logs now include the Markdown report path for easier discovery.

## User flow to test

```bash
python3 scripts/launch_local_workbench.py
```

Then in the browser:

1. Click `Generate offline demo cache`.
2. Click `Build JSON` and verify the log shows the JSON was built.
3. Click `Run Audit`.
4. Open the report links under `Latest Reports` on the right side.
5. Try `Download public history`. If the exchange or local network blocks public calls, it should no longer fail because of imports; any remaining error should be provider/network related.

## Safety

Still audit-only by design. This does not add broker execution, private keys, live signals, managed accounts, or financial advice.
