"""Stage 14 indicator block library for StratProof Lab.

The library is intentionally deterministic and dependency-light. Blocks are
used by the Formula Builder and Idea Lab runner to describe audit conditions in
an exchange-agnostic way. The module calculates indicators only from local
market data and never performs brokerage/execution actions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Any
import math


@dataclass(frozen=True)
class IndicatorBlock:
    key: str
    label: str
    family: str
    description: str
    parameters: dict[str, Any]
    output_type: str
    audit_notes: str


def sma(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = []
    if period <= 0:
        raise ValueError("period must be positive")
    for i in range(len(values)):
        if i + 1 < period:
            out.append(None)
        else:
            out.append(sum(values[i + 1 - period:i + 1]) / period)
    return out


def ema(values: list[float], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[float | None] = []
    k = 2 / (period + 1)
    seed: float | None = None
    for i, v in enumerate(values):
        if i + 1 < period:
            out.append(None)
            continue
        if seed is None:
            seed = sum(values[i + 1 - period:i + 1]) / period
        else:
            seed = v * k + seed * (1 - k)
        out.append(seed)
    return out


def rsi(values: list[float], period: int = 14) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[float | None] = [None] * len(values)
    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, len(values)):
        delta = values[i] - values[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
        if i < period:
            continue
        if i == period:
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
        else:
            prev = out[i - 1]
            # recompute rolling averages to keep the function simple and deterministic
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            out[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i] = 100 - (100 / (1 + rs))
    return out


def atr(high: list[float], low: list[float], close: list[float], period: int = 14) -> list[float | None]:
    trs: list[float] = []
    for i in range(len(close)):
        if i == 0:
            trs.append(high[i] - low[i])
        else:
            trs.append(max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])))
    return sma(trs, period)


def vwap(high: list[float], low: list[float], close: list[float], volume: list[float]) -> list[float | None]:
    out: list[float | None] = []
    cum_pv = 0.0
    cum_v = 0.0
    for h, l, c, v in zip(high, low, close, volume):
        typical = (h + l + c) / 3
        cum_pv += typical * v
        cum_v += v
        out.append(cum_pv / cum_v if cum_v else None)
    return out


def macd(close: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict[str, list[float | None]]:
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    line: list[float | None] = []
    line_for_signal: list[float] = []
    for f, s in zip(fast_ema, slow_ema):
        if f is None or s is None:
            line.append(None)
            line_for_signal.append(0.0)
        else:
            val = f - s
            line.append(val)
            line_for_signal.append(val)
    sig = ema(line_for_signal, signal)
    hist: list[float | None] = []
    for m, s in zip(line, sig):
        hist.append(None if m is None or s is None else m - s)
    return {"macd": line, "signal": sig, "histogram": hist}


def relative_volume(volume: list[float], period: int = 20) -> list[float | None]:
    avg = sma(volume, period)
    out: list[float | None] = []
    for v, a in zip(volume, avg):
        out.append(None if not a else v / a)
    return out


DEFAULT_BLOCKS: list[IndicatorBlock] = [
    IndicatorBlock("rsi_threshold", "RSI Threshold", "momentum", "RSI below/above a threshold.", {"period": 14, "operator": "<", "threshold": 35}, "boolean", "Useful for oversold/overbought hypotheses; must be checked per symbol and regime."),
    IndicatorBlock("ema_trend", "EMA Trend Filter", "trend", "Price or context market above/below EMA.", {"period": 50, "timeframe": "15m", "operator": ">"}, "boolean", "Good for BTC context or local symbol trend alignment."),
    IndicatorBlock("macd_cross", "MACD Cross", "momentum", "MACD line crossing signal line.", {"fast": 12, "slow": 26, "signal": 9, "direction": "bullish"}, "event", "Event-based block; requires chronological replay to avoid look-ahead."),
    IndicatorBlock("vwap_position", "VWAP Position", "structure", "Close above/below session VWAP.", {"operator": ">"}, "boolean", "Useful for intraday structure; session reset rules should be explicit."),
    IndicatorBlock("atr_risk", "ATR Risk Filter", "risk", "ATR percent below/above risk threshold.", {"period": 14, "max_atr_pct": 2.5}, "boolean", "Prevents testing formulas only during unusable volatility."),
    IndicatorBlock("relative_volume", "Relative Volume", "liquidity", "Current volume compared with rolling average.", {"period": 20, "operator": ">", "threshold": 1.5}, "boolean", "Useful as liquidity/attention confirmation; weak on illiquid assets."),
    IndicatorBlock("bollinger_position", "Bollinger Band Position", "volatility", "Close relative to Bollinger bands.", {"period": 20, "stddev": 2, "position": "lower_band"}, "boolean", "Research-only block for mean reversion/volatility hypotheses."),
    IndicatorBlock("session_filter", "Session Filter", "time", "Restrict replay to selected sessions/timezone.", {"timezone": "America/New_York", "session": "new_york_open"}, "boolean", "Important for comparing Asia/London/NY behavior."),
    IndicatorBlock("score_threshold", "Score Threshold Simulator", "quality", "Compare formula performance across score thresholds.", {"thresholds": [50,55,60,65,70,75,80]}, "comparison", "Simulator only; does not activate signals."),
    IndicatorBlock("funding_oi_placeholder", "Funding/OI Context Placeholder", "derivatives", "Optional derivatives context from user-provided APIs.", {"provider": "coinglass_or_coinalyze", "mode": "optional"}, "context", "Future research input; not computed in current audits."),
]


def block_catalog() -> list[dict[str, Any]]:
    return [asdict(b) for b in DEFAULT_BLOCKS]


def write_catalog_json(path: str) -> None:
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(block_catalog(), f, indent=2, ensure_ascii=False)
