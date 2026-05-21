# Stage 48 — Demo QA Checklist

## Must pass before GitHub

- [ ] `python3 -m compileall .`
- [ ] `python3 tests/smoke_test_public_package.py`
- [ ] `python3 scripts/run_public_demo.py`
- [ ] `python3 scripts/launch_local_workbench.py`
- [ ] Workbench opens in browser
- [ ] Generate offline demo cache works
- [ ] Download public history works for Bybit
- [ ] Build JSON logs a visible message
- [ ] Run strict audit works
- [ ] Run relaxed audit works
- [ ] Run strict + relaxed works
- [ ] Visual evidence report opens
- [ ] Markdown report opens
- [ ] JSON report opens
- [ ] Threshold comparison opens
- [ ] Symbol picker works
- [ ] Indicator buttons toggle on/off
- [ ] Remove button stays inside block
- [ ] No raw Python traceback appears in UI
- [ ] No `Infinity` / `NaN` appears in JSON output
- [ ] README explains offline demo cache vs public history
- [ ] README explains workbench step order
- [ ] README explains Community vs Pro boundaries
