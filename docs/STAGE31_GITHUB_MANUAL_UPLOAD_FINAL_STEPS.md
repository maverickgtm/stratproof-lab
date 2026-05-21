# Stage 31 — Final Manual GitHub Upload Steps

Use this only after the Stage 31 rehearsal passes and after the final human review.

Recommended repo settings:

- Repository name: `stratproof-lab`
- Description: `Evidence engine for trading strategies — audit ideas, detect weak backtests, and generate research reports before risking capital.`
- License: `AGPL-3.0-or-later`
- Initial release: `v0.1.0-community-preview`
- Visibility: public, when ready.

Suggested final local sequence:

```bash
unzip stratproof-lab-community-stage31.zip
cd stratproof-lab-community-stage31
python scripts/stage31_local_publishing_rehearsal.py
python scripts/run_public_demo.py
```

Then initialize Git manually using the Stage 29 command pack.

Final human checks before push:

- README looks premium.
- Screenshots are acceptable.
- License is complete.
- No private OpenClaw branding is used as public brand.
- Community vs Pro boundaries are clear.
- No guaranteed return claims.
- No secrets, DB dumps, or private server artifacts.
