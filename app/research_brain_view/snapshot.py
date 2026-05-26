from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

DEFAULT_DB = None

@dataclass
class DepartmentStatus:
    key: str
    label: str
    status: str
    confidence: float
    summary: str
    rows_seen: int = 0

@dataclass
class BrainSnapshot:
    generated_ts: int
    product: str
    mode: str
    audit_health_score: float
    evidence_score: float
    truth_confidence: float
    duplicate_risk: str
    leakage_risk: str
    departments: list[DepartmentStatus]
    activity_feed: list[str]
    metrics: dict[str, Any]


def _table_count(con: sqlite3.Connection, table: str) -> int:
    try:
        row = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        if not row or row[0] == 0:
            return 0
        return int(con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] or 0)
    except Exception:
        return 0


def _latest_count(con: sqlite3.Connection, table: str, ts_col: str = "ts", window_seconds: int = 86400) -> int:
    try:
        exists = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()[0]
        if not exists:
            return 0
        now = int(time.time())
        return int(con.execute(f'SELECT COUNT(*) FROM "{table}" WHERE {ts_col} >= ?', (now - window_seconds,)).fetchone()[0] or 0)
    except Exception:
        return 0


def build_snapshot(db_path: str | Path | None = None) -> BrainSnapshot:
    path = Path(db_path) if db_path else DEFAULT_DB
    departments: list[DepartmentStatus]
    metrics: dict[str, Any] = {}
    feed: list[str] = []

    if path.exists():
        con = sqlite3.connect(path)
        try:
            candidates = _table_count(con, "candidate_signals")
            outcomes = _table_count(con, "signal_outcomes_tp1")
            ideas = _table_count(con, "idea_lab_submissions")
            agent_actions = _table_count(con, "agent_actions")
            chief = _table_count(con, "chief_orchestrator_decisions")
            truth_v3 = _table_count(con, "enterprise_chronological_truth_engine_v3_runs")
            net_r = _table_count(con, "enterprise_net_r_drawdown_metrics_v1_runs")
            formula_runs = _table_count(con, "enterprise_adaptive_scenario_router_v1_runs") + _table_count(con, "real_formula_evolution_hybrid_redesign_replay_v1_1_runs")
            quality_rows = _table_count(con, "quality_ledger")
            recent_candidates = _latest_count(con, "candidate_signals")
            metrics = {
                "candidate_signals": candidates,
                "outcomes": outcomes,
                "ideas_submitted": ideas,
                "agent_actions": agent_actions,
                "chief_decisions": chief,
                "quality_rows": quality_rows,
                "recent_candidates_24h": recent_candidates,
                "truth_engine_runs": truth_v3,
                "net_r_runs": net_r,
                "formula_runs": formula_runs,
            }
            departments = [
                DepartmentStatus("setup", "Setup Department", "READY", 0.92, "Audit configuration and language/timezone preferences ready.", 0),
                DepartmentStatus("data", "Data Setup Department", "SYNC", 0.88, "Provider layer and market-history cache prepared.", candidates),
                DepartmentStatus("idea_lab", "Research University Idea Lab", "WATCH", 0.84, "User hypotheses can be converted into audit jobs.", ideas),
                DepartmentStatus("truth", "Truth Engine", "ACTIVE", 0.98 if truth_v3 else 0.62, "Chronological TP/SL truth verification layer.", truth_v3),
                DepartmentStatus("risk", "RiskGuard / Net R", "ACTIVE", 0.86 if net_r else 0.58, "Drawdown, expectancy, and risk veto reviews.", net_r),
                DepartmentStatus("formula", "Formula Registry", "ACTIVE", 0.81 if formula_runs else 0.55, "Formula versions compete in audit-only mode.", formula_runs),
                DepartmentStatus("quality", "Quality Gate", "ACTIVE", 0.9 if quality_rows else 0.6, "Duplicate, clustering, and low-quality contexts monitored.", quality_rows),
                DepartmentStatus("evidence", "Evidence Reports", "READY", 0.79, "Reports can summarize findings for human review.", 0),
                DepartmentStatus("api", "API Contribution Center", "LOCKED", 0.75, "Research-only API references; no execution permissions.", 0),
            ]
            feed = [
                f"Candidate ledger indexed: {candidates:,} rows.",
                f"Outcome ledger indexed: {outcomes:,} rows.",
                f"Chief decisions observed: {chief:,} rows.",
                f"Quality ledger observed: {quality_rows:,} rows.",
                "Execution disabled by default; audit-only observability mode.",
            ]
        finally:
            con.close()
    else:
        metrics = {
            "candidate_signals": 0,
            "outcomes": 0,
            "ideas_submitted": 0,
            "agent_actions": 0,
            "chief_decisions": 0,
            "quality_rows": 0,
            "recent_candidates_24h": 0,
            "truth_engine_runs": 0,
            "net_r_runs": 0,
            "formula_runs": 0,
        }
        departments = [
            DepartmentStatus("setup", "Setup Department", "DEMO", 0.8, "Demo mode: configure audits without live data."),
            DepartmentStatus("data", "Data Setup Department", "DEMO", 0.74, "Connect one of five public exchange feeds or CSV to build a dataset."),
            DepartmentStatus("idea_lab", "Research University Idea Lab", "DEMO", 0.7, "Submit ideas to generate hypotheses."),
            DepartmentStatus("truth", "Truth Engine", "WAIT", 0.5, "Waiting for OHLCV and signals."),
            DepartmentStatus("risk", "RiskGuard / Net R", "WAIT", 0.5, "Waiting for audit results."),
            DepartmentStatus("formula", "Formula Registry", "READY", 0.68, "Formula versions can be compared."),
            DepartmentStatus("quality", "Quality Gate", "READY", 0.66, "Anticlustering and duplicate checks available."),
            DepartmentStatus("evidence", "Evidence Reports", "READY", 0.64, "Evidence packages can be generated."),
            DepartmentStatus("api", "API Contribution Center", "LOCKED", 0.7, "Research-only API references."),
        ]
        feed = [
            "Demo mode active. Visual observability only; no execution actions.",
            "Connect market data to activate the Research Brain.",
            "Submit a strategy idea to route it through the University.",
        ]

    # Visual-only scores: derived from observability readiness, not trading promises.
    active_departments = sum(1 for d in departments if d.status in {"ACTIVE", "READY", "SYNC", "WATCH"})
    audit_health = round(100.0 * active_departments / max(len(departments), 1), 1)
    evidence_score = round(sum(d.confidence for d in departments) / max(len(departments), 1) * 100, 1)
    truth_confidence = next((round(d.confidence * 100, 1) for d in departments if d.key == "truth"), 0.0)

    return BrainSnapshot(
        generated_ts=int(time.time()),
        product="StratProof Lab",
        mode="VISUAL_OBSERVABILITY_ONLY",
        audit_health_score=audit_health,
        evidence_score=evidence_score,
        truth_confidence=truth_confidence,
        duplicate_risk="WATCH" if metrics.get("quality_rows", 0) else "UNKNOWN",
        leakage_risk="CONTROLLED_RESEARCH_ONLY",
        departments=departments,
        activity_feed=feed,
        metrics=metrics,
    )


def snapshot_to_json(snapshot: BrainSnapshot) -> str:
    return json.dumps(asdict(snapshot), ensure_ascii=False, indent=2)
