#!/usr/bin/env python3
"""Stage 28 release preflight for StratProof Lab public repo."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "stage28" / "release_preflight.json"

REQUIRED = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "VERSION",
    "CHANGELOG.md",
    "RELEASE_NOTES_v2.0.0.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/ISSUE_TEMPLATE/strategy_audit_question.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/ci.yml",
    "scripts/run_public_demo.py",
    "tests/smoke_test_public_package.py",
    "tests/test_provider_connectors.py",
    "docs/V2_PUBLIC_CONNECTORS.md",
    "docs/V2_AUDIT_REPORT.md",
    "docs/V2_AUDIT_EVIDENCE_EXPORTS.md",
    "assets/github/screenshots/01_formula_builder_ui.png",
    "assets/github/screenshots/02_evidence_report_cards.png",
    "assets/github/screenshots/03_research_brain_view.png",
    "assets/github/screenshots/04_provider_connector_layer.png",
]


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout[-5000:]


def main() -> int:
    checks = []
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    checks.append({"name": "required_release_files", "status": "PASS" if not missing else "FAIL", "missing": missing})

    version = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else ""
    checks.append({"name": "version", "status": "PASS" if version == "2.0.0-community-preview" else "FAIL", "version": version})

    code, out = run([sys.executable, "-m", "compileall", "app", "scripts", "tests"])
    checks.append({"name": "python_compile", "status": "PASS" if code == 0 else "FAIL", "output_tail": out})

    code, out = run([sys.executable, "tests/smoke_test_public_package.py"])
    checks.append({"name": "public_smoke_test", "status": "PASS" if code == 0 else "FAIL", "output_tail": out})

    code, out = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
    checks.append({"name": "provider_connector_tests", "status": "PASS" if code == 0 else "FAIL", "output_tail": out})

    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"stage": 28, "overall_status": overall, "checks": checks}, indent=2), encoding="utf-8")
    print(f"STAGE28_RELEASE_PREFLIGHT={overall}")
    print(f"REPORT={REPORT}")
    return 0 if overall == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
