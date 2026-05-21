"""Stage 16 Evidence Report Builder.

Audit-only report formatter for StratProof Lab. It turns an Idea Lab
backtest JSON into UI-ready result cards and a portable Markdown report.
No broker execution, no signal publishing, and no live trading actions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import json


@dataclass(frozen=True)
class EvidenceMetric:
    key: str
    label: str
    value: Any
    unit: str = ""
    status: str = "neutral"  # positive | warning | danger | neutral
    description: str = ""


@dataclass(frozen=True)
class EvidenceCard:
    card_id: str
    title: str
    status: str
    summary: str
    metrics: List[EvidenceMetric]
    warnings: List[str]


def _float(payload: Mapping[str, Any], *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key in payload and payload[key] is not None:
            try:
                return float(payload[key])
            except (TypeError, ValueError):
                continue
    return default


def _int(payload: Mapping[str, Any], *keys: str, default: int = 0) -> int:
    for key in keys:
        if key in payload and payload[key] is not None:
            try:
                return int(float(payload[key]))
            except (TypeError, ValueError):
                continue
    return default


def _status_for_rate(value: float, good: float, warn: float, inverse: bool = False) -> str:
    if inverse:
        if value <= good:
            return "positive"
        if value <= warn:
            return "warning"
        return "danger"
    if value >= good:
        return "positive"
    if value >= warn:
        return "warning"
    return "danger"


def build_result_cards(report: Mapping[str, Any]) -> List[EvidenceCard]:
    """Create consistent cards from a backtest/evidence JSON payload."""
    verdict = str(report.get("verdict", "UNKNOWN"))
    warnings = [str(w) for w in report.get("warnings", []) if w]
    winrate = _float(report, "winrate", "winrate_pct")
    net_r = _float(report, "net_r", "simple_net_r", "net_r_simple")
    max_dd = _float(report, "max_drawdown", "max_drawdown_r", "drawdown")
    duplicate_rate = _float(report, "duplicate_rate", "duplicate_rate_pct")
    leakage_risk = _float(report, "leakage_risk", "leakage_risk_pct")
    trades = _int(report, "trades", "signals", "total_signals", "sample_size")
    evidence_score = _float(report, "evidence_score", "research_confidence", default=0.0)
    truth_confidence = _float(report, "truth_confidence", default=0.0)

    cards: List[EvidenceCard] = []
    cards.append(EvidenceCard(
        card_id="verdict",
        title="Verdict",
        status="positive" if verdict in {"PROMISING", "PASS", "APPROVED_FOR_RESEARCH"} else ("warning" if "MORE" in verdict or "WATCH" in verdict else "danger"),
        summary=f"Research verdict: {verdict}. Audit-only result; evidence must be reviewed before any action.",
        metrics=[
            EvidenceMetric("verdict", "Verdict", verdict, status="neutral"),
            EvidenceMetric("sample_size", "Sample Size", trades, status="positive" if trades >= 100 else "warning"),
            EvidenceMetric("evidence_score", "Evidence Score", round(evidence_score, 2), "%", _status_for_rate(evidence_score, 70, 45)),
        ],
        warnings=warnings[:3],
    ))

    cards.append(EvidenceCard(
        card_id="performance",
        title="Performance Evidence",
        status=_status_for_rate(winrate, 55, 48),
        summary="Honest performance snapshot using available closed outcomes and conservative audit assumptions.",
        metrics=[
            EvidenceMetric("winrate", "Honest Winrate", round(winrate, 2), "%", _status_for_rate(winrate, 55, 48)),
            EvidenceMetric("net_r", "Net R", round(net_r, 2), "R", "positive" if net_r > 0 else ("warning" if net_r == 0 else "danger")),
            EvidenceMetric("max_drawdown", "Max Drawdown", round(max_dd, 2), "R", "positive" if max_dd >= -3 else ("warning" if max_dd >= -8 else "danger")),
        ],
        warnings=[],
    ))

    cards.append(EvidenceCard(
        card_id="quality_gate",
        title="Quality Gate",
        status="danger" if leakage_risk > 10 or duplicate_rate > 35 else ("warning" if leakage_risk > 3 or duplicate_rate > 15 else "positive"),
        summary="Checks whether the result may be distorted by duplicate clusters, leakage, or small samples.",
        metrics=[
            EvidenceMetric("duplicate_rate", "Duplicate Risk", round(duplicate_rate, 2), "%", _status_for_rate(duplicate_rate, 10, 25, inverse=True)),
            EvidenceMetric("leakage_risk", "Leakage Risk", round(leakage_risk, 2), "%", _status_for_rate(leakage_risk, 1, 8, inverse=True)),
            EvidenceMetric("truth_confidence", "Truth Confidence", round(truth_confidence, 2), "%", _status_for_rate(truth_confidence, 75, 50)),
        ],
        warnings=[w for w in warnings if "duplicate" in w.lower() or "leak" in w.lower() or "sample" in w.lower()][:5],
    ))

    threshold_rows = report.get("score_thresholds") or report.get("threshold_comparison") or []
    if isinstance(threshold_rows, list) and threshold_rows:
        best = max(threshold_rows, key=lambda row: _float(row, "net_r", "simple_net_r", default=-9999))
        cards.append(EvidenceCard(
            card_id="thresholds",
            title="Score Threshold Comparison",
            status="neutral",
            summary="Compares candidate score thresholds so the user can see whether stricter filters improve evidence.",
            metrics=[
                EvidenceMetric("best_threshold", "Best Threshold", best.get("threshold", best.get("score_threshold", "n/a"))),
                EvidenceMetric("best_winrate", "Best WR", round(_float(best, "winrate", "winrate_pct"), 2), "%"),
                EvidenceMetric("best_net_r", "Best Net R", round(_float(best, "net_r", "simple_net_r"), 2), "R"),
            ],
            warnings=[],
        ))

    return cards


def cards_to_dict(cards: Iterable[EvidenceCard]) -> List[Dict[str, Any]]:
    return [asdict(card) for card in cards]


def build_markdown_report(report: Mapping[str, Any], cards: Optional[List[EvidenceCard]] = None) -> str:
    cards = cards or build_result_cards(report)
    title = report.get("idea_name") or report.get("strategy_name") or "StratProof Evidence Report"
    idea_hash = report.get("idea_hash", "unknown")
    dataset = report.get("dataset_fingerprint", "unknown")
    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# {title}",
        "",
        "**Audit-only by design.** This report validates evidence; it does not place trades or provide financial advice.",
        "",
        f"- Generated UTC: `{generated}`",
        f"- Idea hash: `{idea_hash}`",
        f"- Dataset fingerprint: `{dataset}`",
        "",
        "## Result Cards",
        "",
    ]
    for card in cards:
        lines.extend([f"### {card.title}", "", card.summary, ""])
        for metric in card.metrics:
            suffix = f" {metric.unit}" if metric.unit else ""
            lines.append(f"- **{metric.label}:** {metric.value}{suffix} ({metric.status})")
        if card.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in card.warnings:
                lines.append(f"- {warning}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_evidence_outputs(input_path: str | Path, output_dir: str | Path) -> Dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = load_json(input_path)
    cards = build_result_cards(report)
    payload = {
        "schema": "stratproof.evidence_report.stage16",
        "source_report": str(input_path),
        "cards": cards_to_dict(cards),
        "raw_summary": report,
    }
    json_path = output_dir / "stage16_evidence_cards.json"
    md_path = output_dir / "stage16_evidence_report.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(build_markdown_report(report, cards), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
