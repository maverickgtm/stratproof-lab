#!/usr/bin/env python3
"""One-command public demo for StratProof Lab Community Edition.

This script is intentionally local and audit-only. It generates synthetic demo
market data, runs a sample Idea Lab audit, builds an evidence report, exports
supporting product assets, and writes a simple demo index.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "reports" / "public_demo"


def run_step(name: str, args: list[str]) -> dict:
    print(f"\n=== {name} ===")
    print("$ " + " ".join(args))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, env=env)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr)
    status = "PASS" if proc.returncode == 0 else "FAIL"
    print(f"{name}: {status}")
    return {
        "name": name,
        "command": args,
        "returncode": proc.returncode,
        "status": status,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def parse_key_values(stdout: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in stdout.splitlines():
        if "=" in line and line.split("=", 1)[0].isupper():
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip()
    return values


def write_demo_summary(results: list[dict]) -> None:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    summary = {
        "product": "StratProof Lab Community Edition",
        "demo": "One-command public demo",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "audit_only_by_design": True,
        "steps": results,
    }
    (REPORT_ROOT / "demo_run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    stage13 = next((r for r in results if r["name"] == "Run multi-timeframe idea audit"), None)
    evidence = next((r for r in results if r["name"] == "Build evidence report cards"), None)
    stage13_kv = parse_key_values(stage13.get("stdout", "") if stage13 else "")
    evidence_kv = parse_key_values(evidence.get("stdout", "") if evidence else "")

    lines = [
        "# StratProof Lab Public Demo",
        "",
        "**Audit-only by design.** This demo uses synthetic market data and does not place trades.",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        "",
        "## What this demo does",
        "",
        "1. Generates synthetic multi-timeframe crypto market data.",
        "2. Runs a Formula Builder idea through the Idea Lab audit runner.",
        "3. Builds evidence report cards.",
        "4. Exports Formula Builder, indicator and GitHub support assets.",
        "5. Leaves browser-ready dashboard screens available under `app/auditor_dashboard/`.",
        "",
        "## Main outputs",
        "",
    ]
    for label, key in [
        ("Idea audit JSON", "REPORT_JSON"),
        ("Idea audit Markdown", "REPORT_MD"),
        ("Threshold comparison JSON", "THRESHOLD_COMPARISON_JSON"),
        ("Threshold comparison Markdown", "THRESHOLD_COMPARISON_MD"),
    ]:
        if key in stage13_kv:
            lines.append(f"- {label}: `{stage13_kv[key]}`")
    for label, key in [("Evidence cards JSON", "CARDS_JSON"), ("Evidence report Markdown", "REPORT_MD")]:
        if key in evidence_kv:
            lines.append(f"- {label}: `{evidence_kv[key]}`")
    lines += [
        "",
        "## Dashboard screens",
        "",
        "Open these files in a browser:",
        "",
        "- `app/auditor_dashboard/formula_builder_ui.html`",
        "- `app/auditor_dashboard/evidence_report_builder_ui.html`",
        "- `app/auditor_dashboard/research_brain_view.html`",
        "- `app/auditor_dashboard/setup_idea_lab_dashboard.html`",
        "",
        "## Step status",
        "",
    ]
    for result in results:
        icon = "✅" if result["status"] == "PASS" else "❌"
        lines.append(f"- {icon} {result['name']}: `{result['status']}`")
    lines.append("")
    (REPORT_ROOT / "DEMO_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    os.environ.setdefault("PYTHONUTF8", "1")
    if REPORT_ROOT.exists():
        shutil.rmtree(REPORT_ROOT)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    py = sys.executable
    results: list[dict] = []
    commands: list[tuple[str, list[str]]] = [
        ("Run public smoke test", [py, "tests/smoke_test_public_package.py"]),
        ("Generate multi-timeframe demo market cache", [py, "scripts/stage13_generate_multitimeframe_demo_cache.py", "--symbols", "SOLUSDT,ETHUSDT", "--timeframe", "5m", "--context-timeframe", "15m", "--rows", "420", "--context-rows", "180"]),
        ("Run multi-timeframe idea audit", [py, "scripts/stage13_run_multitimeframe_audit.py", "examples/idea_lab/rsi_btc_volume_long_example.json", "--project-root", ".", "--out-dir", "reports/public_demo/idea_lab", "--thresholds", "50,65,80", "--no-cache"]),
        ("Build evidence report cards", [py, "scripts/stage16_build_evidence_report.py", "examples/evidence_reports/stage16_demo_audit_summary.json", "--out-dir", "reports/public_demo/evidence_reports"]),
        ("Export indicator catalog", [py, "scripts/stage14_export_indicator_catalog.py"]),
        ("Export Formula Builder schema", [py, "scripts/stage15_export_formula_builder_schema.py"]),
        ("Generate Research Brain snapshot", [py, "scripts/generate_research_brain_snapshot.py", "--db", "data/demo_missing.sqlite3", "--out", "reports/public_demo/research_brain_snapshot.json"]),
        ("Generate GitHub assets", [py, "scripts/stage17_generate_github_assets.py"]),
    ]

    for name, cmd in commands:
        result = run_step(name, cmd)
        results.append(result)
        if result["returncode"] != 0:
            write_demo_summary(results)
            print("\nPUBLIC_DEMO_STATUS=FAIL")
            print(f"FAILED_STEP={name}")
            print(f"DEMO_INDEX={REPORT_ROOT / 'DEMO_INDEX.md'}")
            return result["returncode"] or 1

    write_demo_summary(results)
    print("\nPUBLIC_DEMO_STATUS=PASS")
    print(f"DEMO_INDEX={REPORT_ROOT / 'DEMO_INDEX.md'}")
    print(f"DEMO_SUMMARY_JSON={REPORT_ROOT / 'demo_run_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
