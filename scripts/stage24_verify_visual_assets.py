#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'assets/github/screenshots/01_formula_builder_ui.png',
    'assets/github/screenshots/02_evidence_report_cards.png',
    'assets/github/screenshots/03_research_brain_view.png',
    'assets/github/screenshots/04_provider_connector_layer.png',
    'assets/github/social_preview/stratproof_lab_social_preview.png',
    'assets/github/screenshot_captions_final.md',
    'assets/brand/brand_decision_stage24.md',
]

errors=[]
for rel in REQUIRED:
    path = ROOT / rel
    if not path.exists():
        errors.append(f'MISSING {rel}')
        continue
    if path.suffix.lower() == '.png':
        with Image.open(path) as img:
            w,h = img.size
            if w < 1000 or h < 500:
                errors.append(f'TOO_SMALL {rel} {w}x{h}')

if errors:
    print('FAIL')
    for e in errors: print(e)
    raise SystemExit(1)
print('PASS: visual assets verified')
