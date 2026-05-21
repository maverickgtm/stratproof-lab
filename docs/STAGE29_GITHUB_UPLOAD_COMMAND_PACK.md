# Stage 29 — GitHub Upload Command Pack

Stage 29 prepares the exact manual commands for publishing StratProof Lab Community as a controlled GitHub repository.

This stage does **not** upload anything automatically. It gives the maintainer a safe, copy/paste launch path.

## Recommended repository

- Repository name: `stratproof-lab`
- Visibility: Public
- License: AGPL-3.0-or-later
- Initial release: `v0.1.0-community-preview`
- Short description: `Evidence engine for trading strategies`

## Launch sequence

1. Review the package locally.
2. Create an empty GitHub repo named `stratproof-lab`.
3. Initialize git locally.
4. Commit the Community package.
5. Push `main`.
6. Create tag `v0.1.0-community-preview`.
7. Publish release notes from `RELEASE_NOTES_v0.1.0.md`.
8. Verify README, screenshots, license and demo commands on GitHub.

## Safety principle

Upload only the clean Community Edition package. Do not upload Full Preserve packages, private server backups, database dumps, private keys, env files, or internal OpenClaw artifacts.
