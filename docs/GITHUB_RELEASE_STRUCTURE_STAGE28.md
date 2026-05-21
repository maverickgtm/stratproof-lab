# Stage 28 — GitHub Release Structure v0.1.0

Stage 28 prepares StratProof Lab for a controlled public GitHub release. It does not add trading features. It adds release structure, version metadata, GitHub community templates, CI smoke test workflow, changelog, and release notes.

## Release target

- Repository: `stratproof-lab`
- Version: `0.1.0-community-preview`
- License: `AGPL-3.0-or-later`
- Public name: `StratProof Lab`
- Short name: `StratProof`
- Release type: Community Preview

## Release message

StratProof Lab is an evidence engine for trading strategies. It helps users inspect whether a strategy deserves trust before risking capital.

## Added in this stage

- `VERSION`
- `CHANGELOG.md`
- `RELEASE_NOTES_v0.1.0.md`
- `.github/ISSUE_TEMPLATE/*`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/ci.yml`
- `app/product_branding/version.py`
- `docs/STAGE28_GITHUB_RELEASE_CHECKLIST.md`
- `docs/STAGE28_REPOSITORY_SETUP_PLAN.md`
- `docs/STAGE28_TEST_REPORT.md`

## Release philosophy

Public users should understand the product quickly:

1. Build a strategy idea.
2. Import or generate market data.
3. Run an audit.
4. Inspect evidence quality.
5. Generate a report.

StratProof Lab remains audit-only by design.
