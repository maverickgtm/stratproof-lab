"""Stage 12 Idea Lab backtest runner.

This module turns a visual Formula Builder idea into a local, audit-only
chronological replay over normalized OHLCV CSV files. It is intentionally
conservative and does not execute trades, send alerts, or publish signals.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from app.idea_lab.models import canonical_json, compute_idea_hash


DEFAULT_MARKET_CACHE = Path("data/market_cache")
DEFAULT_RESEARCH_CACHE = Path("data/research_cache")


@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str = ""
    timeframe: str = ""
    provider: str = ""
    market_type: str = ""
    source: str = ""
    metadata_json: str = ""


@dataclass
class SignalReplay:
    symbol: str
    side: str
    timestamp: int
    entry: float
    tp1: float
    sl: float
    result: str
    exit_timestamp: int | None
    score_proxy: float
    conditions_passed: int
    conditions_total: int
    notes: str = ""


@dataclass
class SymbolAuditResult:
    symbol: str
    side: str
    known: int
    wins: int
    losses: int
    ambiguous: int
    no_touch: int
    winrate_pct: float
    net_r_simple: float
    max_drawdown_r: float
    profit_factor: float | None
    duplicate_rate_pct: float
    verdict: str


@dataclass
class IdeaAuditReport:
    idea_hash: str
    dataset_fingerprint: str
    generated_ts: int
    status: str
    title: str
    provider: str
    market_type: str
    timeframe: str
    timezone: str
    session: str
    symbols: list[str]
    overall: dict[str, Any]
    symbol_results: list[dict[str, Any]]
    warnings: list[str]
    report_markdown: str | None = None
    detected_operations: list[dict[str, Any]] = field(default_factory=list)


def load_idea(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def market_cache_path(root: str | Path, provider: str, market_type: str, symbol: str, timeframe: str) -> Path:
    return Path(root) / "data" / "market_cache" / provider / market_type / symbol.upper() / f"{timeframe}.csv"


def read_ohlcv_csv(path: str | Path) -> list[Candle]:
    path = Path(path)
    rows: list[Candle] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ts = r.get("timestamp") or r.get("time") or r.get("open_time") or r.get("ts")
            if ts is None or ts == "":
                continue
            try:
                ts_i = int(float(ts))
                # accept milliseconds and convert to seconds
                if ts_i > 10_000_000_000:
                    ts_i //= 1000
                rows.append(
                    Candle(
                        timestamp=ts_i,
                        open=float(r.get("open") or r.get("Open") or 0),
                        high=float(r.get("high") or r.get("High") or 0),
                        low=float(r.get("low") or r.get("Low") or 0),
                        close=float(r.get("close") or r.get("Close") or 0),
                        volume=float(r.get("volume") or r.get("Volume") or 0),
                        symbol=str(r.get("symbol") or r.get("Symbol") or path.parent.name).upper(),
                        timeframe=str(r.get("timeframe") or path.stem),
                        provider=str(r.get("provider") or (path.parents[2].name if len(path.parents) > 2 else "local")),
                        market_type=str(r.get("market_type") or "unknown"),
                        source=str(r.get("source") or ""),
                        metadata_json=str(r.get("metadata_json") or ""),
                    )
                )
            except Exception:
                continue
    rows.sort(key=lambda c: c.timestamp)
    return rows


def ema(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if period <= 0 or len(values) < period:
        return out
    k = 2 / (period + 1)
    seed = mean(values[:period])
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def rsi(values: list[float], period: int = 14) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return out
    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, period + 1):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    out[period] = 100.0 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
    for i in range(period + 1, len(values)):
        diff = values[i] - values[i - 1]
        gain = max(diff, 0)
        loss = abs(min(diff, 0))
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        out[i] = 100.0 if avg_loss == 0 else 100 - (100 / (1 + avg_gain / avg_loss))
    return out


def rolling_mean(values: list[float], lookback: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if lookback <= 0:
        return out
    for i in range(lookback - 1, len(values)):
        out[i] = mean(values[i - lookback + 1 : i + 1])
    return out


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        out = float(value)
        if not math.isfinite(out):
            return default
        return out
    except Exception:
        return default


def safe_int(value: Any, default: int) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def build_indicator_cache(candles: list[Candle], idea: dict[str, Any]) -> dict[str, Any]:
    """Precompute indicator arrays used by Formula Builder blocks.

    This keeps Idea Lab backtests fast enough for interactive audits.
    """
    closes = [c.close for c in candles]
    vols = [c.volume for c in candles]
    rsi_periods: set[int] = set()
    ema_periods: set[int] = set()
    vol_lookbacks: set[int] = set()
    for block in idea.get("blocks") or []:
        indicator = str(block.get("indicator", "")).upper()
        if indicator == "RSI":
            rsi_periods.add(safe_int(block.get("period"), 14))
        elif indicator == "EMA":
            ema_periods.add(safe_int(block.get("period"), 50))
        elif indicator == "RELATIVE_VOLUME":
            vol_lookbacks.add(safe_int(block.get("lookback"), 20))
    return {
        "rsi": {p: rsi(closes, p) for p in rsi_periods},
        "ema": {p: ema(closes, p) for p in ema_periods},
        "rolling_volume": {lb: rolling_mean(vols, lb) for lb in vol_lookbacks},
    }


def in_session(ts: int, session: str, tz_name: str) -> bool:
    if not session or session.upper() in {"ALL", "ANY"}:
        return True
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(ZoneInfo(tz_name or "UTC"))
    except Exception:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    minute = dt.hour * 60 + dt.minute
    s = session.upper()
    ranges = {
        "NEW_YORK_OPEN": (9 * 60 + 30, 11 * 60 + 30),
        "US_AFTERNOON": (13 * 60, 16 * 60),
        "LONDON_OPEN": (8 * 60, 10 * 60 + 30),
        "ASIA": (0, 6 * 60),
    }
    lo, hi = ranges.get(s, (0, 24 * 60))
    return lo <= minute <= hi


def evaluate_operator(left: float, operator: str, right: float) -> bool:
    op = str(operator or "").strip().lower()
    if op in {"<", "lt", "below"}:
        return left < right
    if op in {"<=", "lte"}:
        return left <= right
    if op in {">", "gt", "above"}:
        return left > right
    if op in {">=", "gte"}:
        return left >= right
    if op in {"=", "==", "eq"}:
        return math.isclose(left, right)
    return False


def evaluate_blocks(
    candles: list[Candle],
    idx: int,
    idea: dict[str, Any],
    btc_context: dict[str, Any] | None = None,
    indicator_cache: dict[str, Any] | None = None,
) -> tuple[int, int, list[str]]:
    blocks = idea.get("blocks") or []
    closes = [c.close for c in candles]
    vols = [c.volume for c in candles]
    passed = 0
    notes: list[str] = []
    for block in blocks:
        indicator = str(block.get("indicator", "")).upper()
        ok = False
        if indicator == "RSI":
            period = safe_int(block.get("period"), 14)
            values = (indicator_cache or {}).get("rsi", {}).get(period) if indicator_cache else rsi(closes, period)
            v = values[idx] if values else None
            target = None
            if v is not None:
                target = safe_float(block.get("value"), None)
            if target is None:
                notes.append(f"RSI{period}:missing_value:FAIL")
            else:
                ok = evaluate_operator(v, str(block.get("operator")), target)
                notes.append(f"RSI{period}={v:.2f}:{'PASS' if ok else 'FAIL'}")
        elif indicator == "RELATIVE_VOLUME":
            lookback = safe_int(block.get("lookback"), 20)
            avg_values = (indicator_cache or {}).get("rolling_volume", {}).get(lookback) if indicator_cache else rolling_mean(vols, lookback)
            avg = avg_values[idx] if avg_values else None
            mult = safe_float(block.get("multiplier"), safe_float(block.get("value"), 1.0)) or 1.0
            if avg and avg > 0:
                ratio = vols[idx] / avg
                ok = evaluate_operator(ratio, str(block.get("operator", ">")), mult)
                notes.append(f"RVOL={ratio:.2f}x:{'PASS' if ok else 'FAIL'}")
        elif indicator in {"BTC_EMA", "EMA"}:
            period = safe_int(block.get("period"), 50)
            # BTC context is optional in Community mode. If unavailable, fail closed.
            if indicator == "BTC_EMA" and btc_context:
                btc_ok = bool(btc_context.get("price_above_ema", {}).get(str(period), False))
                ok = btc_ok if str(block.get("operator", "price_above")).lower() in {"price_above", "above"} else not btc_ok
                notes.append(f"BTC_EMA{period}:{'PASS' if ok else 'FAIL'}")
            elif indicator == "EMA":
                values = (indicator_cache or {}).get("ema", {}).get(period) if indicator_cache else ema(closes, period)
                v = values[idx] if values else None
                if v is not None:
                    op = str(block.get("operator", "price_above")).lower()
                    ok = candles[idx].close > v if op in {"price_above", "above"} else candles[idx].close < v
                    notes.append(f"EMA{period}={v:.6g}:{'PASS' if ok else 'FAIL'}")
        else:
            notes.append(f"UNSUPPORTED:{indicator}:FAIL")
        if ok:
            passed += 1
    return passed, len(blocks), notes


def replay_exit(candles: list[Candle], idx: int, side: str, entry: float, tp1: float, sl: float, horizon: int) -> tuple[str, int | None, str]:
    side = side.upper()
    for j in range(idx + 1, min(len(candles), idx + 1 + horizon)):
        c = candles[j]
        if side == "LONG":
            tp_hit = c.high >= tp1
            sl_hit = c.low <= sl
        else:
            tp_hit = c.low <= tp1
            sl_hit = c.high >= sl
        if tp_hit and sl_hit:
            return "AMBIGUOUS_SAME_CANDLE", c.timestamp, "tp_and_sl_same_candle_conservative_ambiguous"
        if tp_hit:
            return "TP1_PROTECTED", c.timestamp, "tp1_first"
        if sl_hit:
            return "SL_DIRECT", c.timestamp, "sl_first"
    return "NO_TOUCH", None, "horizon_expired"


def max_drawdown_r(sequence: list[int]) -> float:
    equity = 0
    peak = 0
    max_dd = 0
    for x in sequence:
        equity += x
        peak = max(peak, equity)
        max_dd = min(max_dd, equity - peak)
    return float(max_dd)


def duplicate_rate(signals: list[SignalReplay]) -> float:
    if not signals:
        return 0.0
    seen: set[tuple[str, str, int]] = set()
    dup = 0
    for s in signals:
        bucket = int(s.timestamp // 300)  # 5 minute bucket
        key = (s.symbol, s.side, bucket)
        if key in seen:
            dup += 1
        seen.add(key)
    return round(100.0 * dup / len(signals), 2)


def dataset_fingerprint(paths: Iterable[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: str(x)):
        if p.exists():
            st = p.stat()
            h.update(str(p).encode())
            h.update(str(st.st_size).encode())
            h.update(str(int(st.st_mtime)).encode())
    return h.hexdigest()


def run_idea_backtest(
    idea: dict[str, Any],
    project_root: str | Path = ".",
    market_cache_root: str | Path | None = None,
    horizon: int = 12,
    tp_pct: float = 0.0035,
    sl_pct: float = 0.0035,
    use_cache: bool = True,
) -> IdeaAuditReport:
    root = Path(project_root)
    provider = str(idea.get("exchange") or idea.get("provider") or "bybit").lower()
    market_type = str(idea.get("market_type") or "linear")
    timeframe = str(idea.get("timeframe") or "5m")
    tz = str(idea.get("timezone") or "UTC")
    session = str(idea.get("session") or "ALL")
    side = str(idea.get("side") or "LONG").upper()
    symbols = [str(s).upper() for s in (idea.get("symbols") or [])]
    score_threshold = safe_float(idea.get("score_threshold"), 0.0) or 0.0
    cache_root = Path(market_cache_root) if market_cache_root else root

    paths = [market_cache_path(cache_root, provider, market_type, symbol, timeframe) for symbol in symbols]
    fp = dataset_fingerprint(paths)
    idea_hash = compute_idea_hash(idea, fp)
    research_cache_dir = root / DEFAULT_RESEARCH_CACHE
    research_cache_dir.mkdir(parents=True, exist_ok=True)
    cached_path = research_cache_dir / f"{idea_hash}.json"
    if use_cache and cached_path.exists():
        data = json.loads(cached_path.read_text(encoding="utf-8"))
        if "detected_operations" in data:
            return IdeaAuditReport(**data)

    warnings: list[str] = []
    symbol_results: list[dict[str, Any]] = []
    all_signals: list[SignalReplay] = []

    # Stage 13: optional multi-timeframe BTC context, fail-closed when required but missing.
    btc_lookup = None
    try:
        from app.idea_lab.context_engine import load_btc_context_lookup
        btc_lookup, btc_warnings = load_btc_context_lookup(cache_root, provider, market_type, idea)
        warnings.extend(btc_warnings)
    except Exception as exc:
        warnings.append(f"btc_context_load_error:{repr(exc)[:180]}")

    for symbol, path in zip(symbols, paths):
        if not path.exists():
            warnings.append(f"missing_market_cache:{symbol}:{path}")
            symbol_results.append(asdict(SymbolAuditResult(symbol, side, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, None, 0.0, "NO_DATA")))
            continue
        candles = read_ohlcv_csv(path)
        if len(candles) < 60:
            warnings.append(f"insufficient_candles:{symbol}:{len(candles)}")
            symbol_results.append(asdict(SymbolAuditResult(symbol, side, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, None, 0.0, "INSUFFICIENT_DATA")))
            continue
        indicator_cache = build_indicator_cache(candles, idea)
        signals: list[SignalReplay] = []
        for i in range(60, len(candles) - horizon):
            if not in_session(candles[i].timestamp, session, tz):
                continue
            btc_context = btc_lookup.at_or_before(candles[i].timestamp) if btc_lookup else None
            passed, total, notes = evaluate_blocks(candles, i, idea, btc_context=btc_context, indicator_cache=indicator_cache)
            if total == 0:
                continue
            score_proxy = round(100.0 * passed / total, 2)
            if passed != total or score_proxy < score_threshold:
                continue
            entry = candles[i].close
            if side == "SHORT":
                tp1 = entry * (1 - tp_pct)
                sl = entry * (1 + sl_pct)
            else:
                tp1 = entry * (1 + tp_pct)
                sl = entry * (1 - sl_pct)
            result, exit_ts, exit_note = replay_exit(candles, i, side, entry, tp1, sl, horizon)
            signals.append(SignalReplay(symbol, side, candles[i].timestamp, entry, tp1, sl, result, exit_ts, score_proxy, passed, total, ";".join(notes + [exit_note])))
        wins = sum(1 for s in signals if s.result == "TP1_PROTECTED")
        losses = sum(1 for s in signals if s.result == "SL_DIRECT")
        ambiguous = sum(1 for s in signals if s.result == "AMBIGUOUS_SAME_CANDLE")
        no_touch = sum(1 for s in signals if s.result == "NO_TOUCH")
        known = wins + losses
        seq = [1 if s.result == "TP1_PROTECTED" else -1 for s in signals if s.result in {"TP1_PROTECTED", "SL_DIRECT"}]
        wr = round(100.0 * wins / known, 2) if known else 0.0
        net = float(wins - losses)
        # Keep JSON strict and browser-safe. Infinite profit factor is mathematically
        # possible when losses=0, but JSON Infinity is invalid in browsers. We use
        # None to mean "undefined / no losses in sample" and avoid corrupting
        # the workbench response.
        pf = round(wins / losses, 4) if losses else None
        verdict = "PROMISING_RESEARCH_ONLY" if known >= 20 and wr >= 55 and net > 0 else "NEEDS_MORE_DATA" if known < 20 else "NOT_READY_RESEARCH_ONLY"
        sym_result = SymbolAuditResult(symbol, side, known, wins, losses, ambiguous, no_touch, wr, net, max_drawdown_r(seq), pf, duplicate_rate(signals), verdict)
        symbol_results.append(asdict(sym_result))
        all_signals.extend(signals)

    total_known = sum(r["known"] for r in symbol_results)
    total_wins = sum(r["wins"] for r in symbol_results)
    total_losses = sum(r["losses"] for r in symbol_results)
    total_wr = round(100.0 * total_wins / total_known, 2) if total_known else 0.0
    total_net = float(total_wins - total_losses)
    overall_verdict = "PROMISING_RESEARCH_ONLY" if total_known >= 30 and total_wr >= 55 and total_net > 0 else "NEEDS_MORE_DATA" if total_known < 30 else "NOT_READY_RESEARCH_ONLY"
    overall = {
        "known": total_known,
        "wins": total_wins,
        "losses": total_losses,
        "winrate_pct": total_wr,
        "net_r_simple": total_net,
        "signals_total": len(all_signals),
        "ambiguous": sum(1 for s in all_signals if s.result == "AMBIGUOUS_SAME_CANDLE"),
        "no_touch": sum(1 for s in all_signals if s.result == "NO_TOUCH"),
        "duplicate_rate_pct": duplicate_rate(all_signals),
        "verdict": overall_verdict,
        "replay_horizon_candles": horizon,
    }
    # Stage 38: attach evidence/sufficiency guidance for UX and reports.
    # It is intentionally user-facing and audit-only.
    report = IdeaAuditReport(
        idea_hash=idea_hash,
        dataset_fingerprint=fp,
        generated_ts=int(time.time()),
        status="COMPLETE_AUDIT_ONLY",
        title=str(idea.get("name") or "Strategy idea audit"),
        provider=provider,
        market_type=market_type,
        timeframe=timeframe,
        timezone=tz,
        session=session,
        symbols=symbols,
        overall=overall,
        symbol_results=symbol_results,
        warnings=warnings,
        report_markdown=None,
        detected_operations=[asdict(signal) for signal in all_signals],
    )
    report.overall["sample_diagnostics"] = build_sample_sufficiency_guidance(report, idea)
    report.report_markdown = render_markdown_report(report, idea)
    cached_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return report



def build_sample_sufficiency_guidance(report: IdeaAuditReport, idea: dict[str, Any]) -> dict[str, Any]:
    """Return user-facing diagnostics when an audit has too little evidence.

    This is not a trading recommendation. It explains why evidence is thin and
    suggests safer follow-up tests that can increase sample size for research.
    """
    known = int(report.overall.get("known") or 0)
    signals_total = int(report.overall.get("signals_total") or 0)
    no_touch = int(report.overall.get("no_touch") or 0)
    session = str(report.session or "ALL")
    score = idea.get("score_threshold")
    blocks = idea.get("blocks") or []
    reasons: list[str] = []
    recommendations: list[str] = []

    if known == 0 and signals_total == 0:
        reasons.append("No candles matched every active formula block inside the selected session/window.")
    elif known == 0 and signals_total > 0:
        reasons.append("The formula produced candidate entries, but none resolved to TP1 or SL inside the replay horizon.")
    elif known < 20:
        reasons.append(f"Only {known} closed outcomes were available; StratProof prefers at least 20 per symbol-side review and 30+ overall for stronger evidence.")
    if session.upper() not in {"ALL", "ANY", ""}:
        recommendations.append("Run the same formula with Session = ALL to learn whether the session filter is starving the sample.")
    try:
        if (safe_float(score, 0.0) or 0.0) >= 65:
            recommendations.append("Compare lower score thresholds such as 50/55/60 before deciding that the idea has no evidence.")
    except Exception:
        pass
    if any(str(b.get("indicator", "")).upper() == "RELATIVE_VOLUME" and (safe_float(b.get("multiplier"), safe_float(b.get("value"), 0.0)) or 0.0) >= 1.5 for b in blocks):
        recommendations.append("Try Relative Volume 1.1x–1.3x as a sample-size probe, then tighten again if evidence improves.")
    if any(str(b.get("indicator", "")).upper() == "RSI" and (safe_float(b.get("value"), 0.0) or 0.0) <= 35 for b in blocks):
        recommendations.append("Try RSI < 40 or RSI < 45 as a discovery probe; keep the strict RSI version as the final validation candidate.")
    if len(report.symbols) <= 2:
        recommendations.append("Add more symbols or extend history to 60–90 days for a broader evidence check.")
    recommendations.append("Use relaxed audit only for discovery; final promotion should rerun the original strict formula.")
    return {
        "known": known,
        "signals_total": signals_total,
        "no_touch": no_touch,
        "minimum_preferred_known": 30,
        "sample_status": "INSUFFICIENT_SAMPLE" if known < 30 else "ENOUGH_FOR_INITIAL_REVIEW",
        "reasons": reasons or ["Evidence sample is below the preferred review threshold."],
        "recommended_next_tests": recommendations,
    }

def render_markdown_report(report: IdeaAuditReport, idea: dict[str, Any]) -> str:
    lines = [
        f"# StratProof Lab Idea Audit Report",
        "",
        f"**Idea:** {report.title}",
        f"**Status:** {report.status}",
        f"**Verdict:** {report.overall.get('verdict')}",
        f"**Generated UTC:** {datetime.fromtimestamp(report.generated_ts, tz=timezone.utc).isoformat()}",
        "",
        "## Configuration",
        f"- Provider: `{report.provider}`",
        f"- Market type: `{report.market_type}`",
        f"- Symbols: `{', '.join(report.symbols)}`",
        f"- Timeframe: `{report.timeframe}`",
        f"- Timezone: `{report.timezone}`",
        f"- Session: `{report.session}`",
        f"- Side: `{idea.get('side', 'BOTH')}`",
        f"- Score threshold: `{idea.get('score_threshold')}`",
        "",
        "## Overall Results",
        f"- Known outcomes: **{report.overall.get('known')}**",
        f"- Wins: **{report.overall.get('wins')}**",
        f"- Losses: **{report.overall.get('losses')}**",
        f"- Winrate: **{report.overall.get('winrate_pct')}%**",
        f"- Net R simple: **{report.overall.get('net_r_simple')}**",
        f"- Duplicate rate: **{report.overall.get('duplicate_rate_pct')}%**",
        "",
        "## Symbol Results",
        "| Symbol | Side | Known | Wins | Losses | WR % | Net R | Max DD | Verdict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in report.symbol_results:
        lines.append(f"| {r['symbol']} | {r['side']} | {r['known']} | {r['wins']} | {r['losses']} | {r['winrate_pct']} | {r['net_r_simple']} | {r['max_drawdown_r']} | {r['verdict']} |")
    diag = report.overall.get("sample_diagnostics") or build_sample_sufficiency_guidance(report, idea)
    if int(report.overall.get("known") or 0) < int(diag.get("minimum_preferred_known") or 30):
        lines += ["", "## Why this report needs more data"]
        for reason in diag.get("reasons") or []:
            lines.append(f"- {reason}")
        lines += ["", "## Next recommended tests"]
        for rec in diag.get("recommended_next_tests") or []:
            lines.append(f"- {rec}")
    lines += ["", "## Warnings"]
    if report.warnings:
        lines += [f"- `{w}`" for w in report.warnings]
    else:
        lines.append("- None")
    lines += ["", "## Safety", "This report is audit-only. It validates evidence and does not execute broker actions."]
    return "\n".join(lines) + "\n"
