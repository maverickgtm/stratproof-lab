#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import json
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.idea_lab.backtest_runner import load_idea, run_idea_backtest
from app.idea_lab.evidence_export import export_audit_evidence_csvs
from app.idea_lab.score_threshold_simulator import render_threshold_markdown, simulate_thresholds


def parse_thresholds(s: str) -> list[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description="Run Stage 13 multi-timeframe idea audit with BTC context and score comparison.")
    p.add_argument("idea_json")
    p.add_argument("--project-root", default=".")
    p.add_argument("--out-dir", default="reports/idea_lab_stage13")
    p.add_argument("--thresholds", default="50,55,60,65,70,75,80")
    p.add_argument("--no-cache", action="store_true")
    args = p.parse_args()

    root = Path(args.project_root)
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    idea = load_idea(args.idea_json)

    report = run_idea_backtest(idea, project_root=root, use_cache=not args.no_cache)
    base_json = out_dir / f"{report.idea_hash}_stage13_report.json"
    base_md = out_dir / f"{report.idea_hash}_stage13_report.md"
    base_json.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    base_md.write_text(report.report_markdown or "", encoding="utf-8")
    evidence_csvs = export_audit_evidence_csvs(report, idea, out_dir, project_root=root)

    rows = simulate_thresholds(idea, parse_thresholds(args.thresholds), project_root=root, use_cache=False)
    comp_json = out_dir / f"{report.idea_hash}_threshold_comparison.json"
    comp_md = out_dir / f"{report.idea_hash}_threshold_comparison.md"
    comp_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    comp_md.write_text(render_threshold_markdown(rows), encoding="utf-8")

    print(f"REPORT_JSON={base_json}")
    print(f"REPORT_MD={base_md}")
    print(f"THRESHOLD_COMPARISON_JSON={comp_json}")
    print(f"THRESHOLD_COMPARISON_MD={comp_md}")
    for evidence_export in evidence_csvs:
        print(f"EVIDENCE_CSV_{evidence_export['kind'].upper()}={evidence_export['path']}")
    print(f"VERDICT={report.overall.get('verdict')}")
    print(f"WARNINGS={len(report.warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
