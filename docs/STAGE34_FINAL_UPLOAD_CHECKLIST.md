# Stage 34 — Final Upload Checklist

Before pushing to GitHub:

```bash
python3 -m compileall .
python3 tests/smoke_test_public_package.py
python3 scripts/run_public_demo.py
python3 scripts/stage28_release_preflight.py
python3 scripts/stage22_final_github_preflight.py
bash scripts/stage34_clean_before_git_upload.sh
```

Then check:

- `README.md`
- `LICENSE`
- `app/auditor_dashboard/index.html`
- `assets/github/screenshots/`
- `reports/public_demo/DEMO_INDEX.md`
- `docs/STAGE29_GITHUB_COMMANDS_MAC.md`

Do not commit:

- `__pycache__/`
- `*.pyc`
- `.env`
- local virtualenvs
- private keys
- DB dumps
