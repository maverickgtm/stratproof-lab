from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    'README.md',
    'app/auditor_dashboard/formula_builder_ui.html',
    'app/auditor_dashboard/evidence_report_builder_ui.html',
    'app/auditor_dashboard/research_brain_view.html',
    'app/i18n/en.json',
    'app/i18n/es.json',
    'app/i18n/pt.json',
    'app/i18n/de.json',
    'scripts/stage14_export_indicator_catalog.py',
    'scripts/stage15_export_formula_builder_schema.py',
    'scripts/stage16_build_evidence_report.py',
]

MODULES = [
    'app.i18n.translations',
    'app.idea_lab.models',
    'app.idea_lab.indicator_library',
    'app.formula_builder.blocks',
    'app.formula_builder.ui_schema',
    'app.evidence_reports.builder',
    'app.provider_connectors.base',
]


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            failures.append(f'MISSING {rel}')
    sys.path.insert(0, str(ROOT))
    for mod in MODULES:
        try:
            importlib.import_module(mod)
        except Exception as exc:
            failures.append(f'IMPORT_FAIL {mod}: {exc}')
    compile_proc = subprocess.run([sys.executable, '-m', 'compileall', '-q', str(ROOT / 'app'), str(ROOT / 'scripts')], cwd=ROOT)
    if compile_proc.returncode != 0:
        failures.append('COMPILE_FAIL')
    demo_proc = subprocess.run([sys.executable, 'scripts/stage16_build_evidence_report.py', 'examples/evidence_reports/stage16_demo_audit_summary.json', '--out-dir', 'reports/stage19_smoke'], cwd=ROOT)
    if demo_proc.returncode != 0:
        failures.append('STAGE16_DEMO_FAIL')
    if failures:
        print('FAIL')
        for item in failures:
            print(item)
        return 1
    print('PASS: public package smoke test')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
