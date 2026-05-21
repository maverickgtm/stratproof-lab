"""Stage 13 score-threshold simulator.

Runs the same saved idea through several score thresholds and returns a compact
comparison table. Audit-only: no live signal activation.
"""
from __future__ import annotations

import copy
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.idea_lab.backtest_runner import run_idea_backtest


def simulate_thresholds(
    idea: dict[str, Any],
    thresholds: list[int] | None = None,
    project_root: str | Path = ".",
    use_cache: bool = False,
) -> list[dict[str, Any]]:
    thresholds = thresholds or [50, 55, 60, 65, 70, 75, 80]
    rows: list[dict[str, Any]] = []
    for th in thresholds:
        candidate = copy.deepcopy(idea)
        candidate["score_threshold"] = th
        report = run_idea_backtest(candidate, project_root=project_root, use_cache=use_cache)
        rows.append({
            "score_threshold": th,
            "known": report.overall.get("known"),
            "wins": report.overall.get("wins"),
            "losses": report.overall.get("losses"),
            "winrate_pct": report.overall.get("winrate_pct"),
            "net_r_simple": report.overall.get("net_r_simple"),
            "duplicate_rate_pct": report.overall.get("duplicate_rate_pct"),
            "verdict": report.overall.get("verdict"),
            "idea_hash": report.idea_hash,
        })
    return rows


def render_threshold_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# StratProof Lab Score Threshold Comparison",
        "",
        "| Score >= | Known | Wins | Losses | WR % | Net R | Duplicate % | Verdict |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['score_threshold']} | {r['known']} | {r['wins']} | {r['losses']} | {r['winrate_pct']} | {r['net_r_simple']} | {r['duplicate_rate_pct']} | {r['verdict']} |"
        )
    lines.append("")
    lines.append("Safety: comparison is audit-only and validates evidence and does not execute broker actions.")
    return "\n".join(lines) + "\n"
