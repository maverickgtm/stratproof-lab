#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORT_DIR=ROOT/'reports'/'stage31'; REPORT_DIR.mkdir(parents=True, exist_ok=True)

def run(name, cmd):
    env=dict(os.environ); env['PYTHONPATH']=str(ROOT)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    start=time.time(); log=REPORT_DIR/f'{name}.log'
    with log.open('w',encoding='utf-8') as f:
        f.write('$ '+' '.join(cmd)+'\n\n'); f.flush()
        rc=subprocess.call(cmd,cwd=str(ROOT),env=env,stdout=f,stderr=subprocess.STDOUT)
    return {'name':name,'cmd':cmd,'returncode':rc,'status':'PASS' if rc==0 else 'FAIL','seconds':round(time.time()-start,3),'log':str(log.relative_to(ROOT))}

def main():
    py=sys.executable
    steps=[
        ('python_compile',[py,'-m','compileall','-q','app','scripts','tests']),
        ('public_smoke_test',[py,'tests/smoke_test_public_package.py']),
        ('one_command_public_demo',[py,'scripts/run_public_demo.py']),
        ('release_preflight',[py,'scripts/stage28_release_preflight.py']),
        ('github_preflight',[py,'scripts/stage22_final_github_preflight.py']),
    ]
    res={'stage':'31','name':'Final Local Publishing Rehearsal','status':'PASS','publish_actions_performed':False,'network_required':False,'steps':[]}
    for name,cmd in steps:
        step=run(name,cmd); res['steps'].append(step)
        if step['status']!='PASS': res['status']='FAIL'; break
    (REPORT_DIR/'local_publishing_rehearsal_report.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
    lines=['# Stage 31 Local Publishing Rehearsal Report','',f"Status: **{res['status']}**",'', '## Steps','']
    for s in res['steps']: lines.append(f"- {s['status']}: `{s['name']}` ({s['seconds']}s)")
    lines+=['','No GitHub publish action was performed.']
    (REPORT_DIR/'local_publishing_rehearsal_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('STAGE31_REHEARSAL_STATUS='+res['status'])
    print('REPORT_JSON='+str(REPORT_DIR/'local_publishing_rehearsal_report.json'))
    return 0 if res['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
