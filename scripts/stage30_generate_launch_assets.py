#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports' / 'stage30'
OUT.mkdir(parents=True, exist_ok=True)

payload = {
    'stage': 30,
    'name': 'GitHub Landing Final Polish + Release Notes Final',
    'status': 'PASS',
    'repo_name': 'stratproof-lab',
    'version': (ROOT / 'VERSION').read_text().strip() if (ROOT / 'VERSION').exists() else '0.1.0-community-preview',
    'short_description': (ROOT / 'assets/github/repo_about_stage30.txt').read_text().strip(),
    'topics': [line.strip() for line in (ROOT / 'assets/github/repo_topics_stage30.txt').read_text().splitlines() if line.strip()],
    'release_title': 'StratProof Lab v0.1.0 Community Preview',
    'hero': 'Most trading strategies look good — until they are audited.',
    'category': 'Evidence engine for trading strategies',
    'safety_model': 'Audit-only by design. Evidence before action. No broker execution in Community.',
}
(OUT / 'launch_assets_summary.json').write_text(json.dumps(payload, indent=2) + '\n')
print('STAGE30_LAUNCH_ASSETS=PASS')
print(OUT / 'launch_assets_summary.json')
