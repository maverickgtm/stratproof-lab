# Stage 29 — Final GitHub Release Checklist

## Must pass before pushing

- [ ] Only the Community Stage 29 package is being uploaded.
- [ ] No Full Preserve zip is inside the repo.
- [ ] No `.env` file with secrets is inside the repo.
- [ ] No PEM/private key is inside the repo.
- [ ] No SQLite/PostgreSQL dump is inside the repo.
- [ ] No server IPs, private paths, or operational secrets are present.
- [ ] `LICENSE` contains AGPL-3.0-or-later text.
- [ ] `README.md` renders well locally.
- [ ] Screenshots exist under `assets/github/screenshots/`.
- [ ] `python scripts/run_public_demo.py` passes.
- [ ] `python scripts/stage28_release_preflight.py` passes.
- [ ] Version is `0.1.0-community-preview`.

## After pushing

- [ ] GitHub README displays correctly.
- [ ] Screenshots render correctly.
- [ ] License appears in GitHub sidebar.
- [ ] CI workflow runs.
- [ ] Release tag exists.
- [ ] Release notes are published.
- [ ] No unexpected files are visible on GitHub.
