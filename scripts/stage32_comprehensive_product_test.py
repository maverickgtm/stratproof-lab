#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / 'reports' / 'stage32'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def run(name, cmd, timeout=90):
    t0=time.time(); env=dict(os.environ)
    env['PYTHONPATH']=str(ROOT)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    p=subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout, env=env)
    return {'name':name,'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'seconds':round(time.time()-t0,3),'cmd':' '.join(cmd),'stdout_tail':p.stdout[-2000:],'stderr_tail':p.stderr[-2000:]}

def exists(name, rels):
    missing=[r for r in rels if not (ROOT/r).exists()]
    return {'name':name,'status':'PASS' if not missing else 'FAIL','missing':[str(x) for x in missing]}

def text(name, rel, includes=(), excludes=()):
    p=ROOT/rel; data=p.read_text(errors='ignore') if p.exists() else ''
    missing=[x for x in includes if x not in data]
    forbidden=[x for x in excludes if x in data]
    return {'name':name,'status':'PASS' if p.exists() and not missing and not forbidden else 'FAIL','missing':missing,'forbidden':forbidden}

checks=[]
checks.append(exists('core_public_files', [Path('README.md'),Path('LICENSE'),Path('VERSION'),Path('CHANGELOG.md'),Path('scripts/run_public_demo.py'),Path('tests/smoke_test_public_package.py')]))
checks.append(exists('visual_product_files', [Path('app/auditor_dashboard/formula_builder_ui.html'),Path('app/auditor_dashboard/evidence_report_builder_ui.html'),Path('app/auditor_dashboard/research_brain_view.html'),Path('assets/github/screenshots/01_formula_builder_ui.png'),Path('assets/github/screenshots/02_evidence_report_cards.png'),Path('assets/github/screenshots/03_research_brain_view.png'),Path('assets/github/screenshots/04_provider_connector_layer.png')]))
checks.append(text('readme_premium_positioning', Path('README.md'), ['Most trading strategies look good','Evidence engine for trading strategies','Audit-only by design'], ['guaranteed' + ' profit','risk-' + 'free returns']))
checks.append(text('license_agpl_canonical_present', Path('LICENSE'), ['GNU AFFERO GENERAL PUBLIC LICENSE','Version 3']))
cmds=[
 ('python_compile',[sys.executable,'-m','compileall','-q','app','scripts','tests'],120),
 ('public_smoke_test',[sys.executable,'tests/smoke_test_public_package.py'],90),
 ('indicator_catalog_direct_script',[sys.executable,'scripts/stage14_export_indicator_catalog.py'],90),
 ('formula_schema_direct_script',[sys.executable,'scripts/stage15_export_formula_builder_schema.py'],90),
 ('evidence_builder_direct_script',[sys.executable,'scripts/stage16_build_evidence_report.py','examples/evidence_reports/stage16_demo_audit_summary.json','--out-dir','reports/stage32/evidence'],90),
 ('github_assets_direct_script',[sys.executable,'scripts/stage17_generate_github_assets.py'],90),
 ('visual_assets_check',[sys.executable,'scripts/stage24_verify_visual_assets.py'],90),
 ('pricing_assets_direct_script',[sys.executable,'scripts/stage26_export_pricing_assets.py'],90),
 ('demo_market_cache_generation',[sys.executable,'scripts/stage13_generate_multitimeframe_demo_cache.py','--symbols','SOLUSDT,ETHUSDT','--timeframe','5m','--context-timeframe','15m','--rows','420','--context-rows','180'],90),
 ('multitimeframe_audit_direct_script',[sys.executable,'scripts/stage13_run_multitimeframe_audit.py','examples/idea_lab/rsi_btc_volume_long_example.json','--project-root','.','--out-dir','reports/stage32/idea_lab','--thresholds','50,65,80','--no-cache'],90),
 ('research_brain_snapshot_direct_script',[sys.executable,'scripts/generate_research_brain_snapshot.py','--db','data/demo_missing.sqlite3','--out','reports/stage32/research_brain_snapshot.json'],90),
 ('stage28_release_preflight',[sys.executable,'scripts/stage28_release_preflight.py'],120),
]
for name,cmd,timeout in cmds:
    try: checks.append(run(name,cmd,timeout))
    except Exception as e: checks.append({'name':name,'status':'FAIL','error':repr(e)})
checks.append(exists('expected_test_outputs', [Path('reports/stage32/evidence/stage16_evidence_report.md'),Path('reports/stage32/idea_lab'),Path('reports/stage32/research_brain_snapshot.json'),Path('reports/stage28/release_preflight.json')]))
failures=[c for c in checks if c.get('status')!='PASS']
summary={'stage':32,'product':'StratProof Lab Community','test_name':'Comprehensive Product Test Matrix','overall_status':'PASS' if not failures else 'FAIL','total_checks':len(checks),'failures_count':len(failures),'failures':failures,'checks':checks,'note':'Stage 32 runs direct script tests and generated-output verification. It intentionally avoids publishing or external payment/GitHub actions.'}
(REPORT_DIR/'comprehensive_product_test_report.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
md=['# Stage 32 — Comprehensive Product Test Matrix','',f"Overall status: **{summary['overall_status']}**",'',f"Total checks: {len(checks)}",f"Failures: {len(failures)}",'', '## Checks']
for c in checks:
    md.append(f"- **{c['name']}**: `{c.get('status')}`")
    if c.get('status')!='PASS': md.append(f"  - Details: `{json.dumps(c, ensure_ascii=False)[:800]}`")
md += ['','## Safety boundary','No GitHub publication, no payment integration, no broker execution, and no external secrets were used in this test stage.']
(REPORT_DIR/'comprehensive_product_test_report.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'overall_status':summary['overall_status'],'total_checks':len(checks),'failures':len(failures)},indent=2))
return_code=0 if not failures else 1
raise SystemExit(return_code)
