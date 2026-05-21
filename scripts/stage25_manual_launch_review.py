#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks=[]

def add(name,status,detail=''):
    checks.append({'name':name,'status':status,'detail':detail})

readme=(ROOT/'README.md').read_text(errors='ignore')
for phrase in ['StratProof Lab','Most trading strategies look good','evidence engine','audit-only by design','AGPL-3.0-or-later']:
    add(f'readme_contains_{phrase[:20].replace(" ","_")}', 'PASS' if phrase.lower() in readme.lower() else 'FAIL', phrase)
for img in ['assets/github/screenshots/01_formula_builder_ui.png','assets/github/screenshots/02_evidence_report_cards.png','assets/github/screenshots/03_research_brain_view.png','assets/github/screenshots/04_provider_connector_layer.png']:
    add(f'visual_asset_{Path(img).name}', 'PASS' if (ROOT/img).exists() else 'FAIL', img)
license_text=(ROOT/'LICENSE').read_text(errors='ignore') if (ROOT/'LICENSE').exists() else ''
add('license_full_agpl_present', 'PASS' if 'GNU AFFERO GENERAL PUBLIC LICENSE' in license_text and 'Version 3' in license_text else 'FAIL')
try:
    res=subprocess.run([sys.executable,'tests/smoke_test_public_package.py'],cwd=ROOT,capture_output=True,text=True,timeout=60)
    add('public_smoke_test','PASS' if res.returncode==0 else 'FAIL',(res.stdout+res.stderr)[-1000:])
except Exception as e:
    add('public_smoke_test','FAIL',repr(e))
try:
    res=subprocess.run([sys.executable,'-m','compileall','-q','app','scripts','tests'],cwd=ROOT,capture_output=True,text=True,timeout=120)
    add('python_compile','PASS' if res.returncode==0 else 'FAIL',(res.stdout+res.stderr)[-1000:])
except Exception as e:
    add('python_compile','FAIL',repr(e))
status='PASS' if all(c['status']=='PASS' for c in checks) else 'NEEDS_REVIEW'
out={'stage':25,'status':status,'verdict':'READY_FOR_DEMO_REVIEW' if status=='PASS' else 'FIX_BEFORE_DEMO','checks':checks}
outdir=ROOT/'reports/stage25'; outdir.mkdir(parents=True,exist_ok=True)
(outdir/'manual_launch_review.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
sys.exit(0 if status=='PASS' else 1)
