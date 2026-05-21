#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.idea_lab.backtest_runner import run_idea_backtest


def main() -> int:
    p = argparse.ArgumentParser(description="Run an audit-only Idea Lab backtest from a saved Formula Builder JSON.")
    p.add_argument("idea_json", help="Path to Formula Builder / Saved Idea JSON")
    p.add_argument("--project-root", default=".")
    p.add_argument("--market-cache-root", default=None)
    p.add_argument("--horizon", type=int, default=12, help="Candles to look ahead for TP/SL replay")
    p.add_argument("--tp-pct", type=float, default=0.0035)
    p.add_argument("--sl-pct", type=float, default=0.0035)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--out-dir", default="reports/idea_lab")
    args = p.parse_args()

    idea = json.loads(Path(args.idea_json).read_text(encoding="utf-8"))
    report = run_idea_backtest(
        idea,
        project_root=args.project_root,
        market_cache_root=args.market_cache_root,
        horizon=args.horizon,
        tp_pct=args.tp_pct,
        sl_pct=args.sl_pct,
        use_cache=not args.no_cache,
    )
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / report.idea_hash
    (base.with_suffix(".json")).write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    (base.with_suffix(".md")).write_text(report.report_markdown or "", encoding="utf-8")
    print("STATUS=IDEA_BACKTEST_COMPLETE_AUDIT_ONLY")
    print(f"IDEA_HASH={report.idea_hash}")
    print(f"VERDICT={report.overall.get('verdict')}")
    print(f"KNOWN={report.overall.get('known')}")
    print(f"WINRATE_PCT={report.overall.get('winrate_pct')}")
    print(f"NET_R_SIMPLE={report.overall.get('net_r_simple')}")
    print(f"REPORT_JSON={base.with_suffix('.json')}")
    print(f"REPORT_MD={base.with_suffix('.md')}")
    if report.warnings:
        print("WARNINGS=" + ",".join(report.warnings[:10]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
