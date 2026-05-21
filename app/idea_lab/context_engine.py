"""Stage 13 multi-timeframe context engine.

Audit-only helpers for aligning strategy candles with higher-timeframe context,
starting with BTC EMA regime checks. This module never sends orders, alerts, or
signals; it only enriches backtest/audit decisions.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.idea_lab.backtest_runner import Candle, ema, read_ohlcv_csv


@dataclass
class BTCContextPoint:
    timestamp: int
    close: float
    ema_values: dict[int, float | None]
    price_above_ema: dict[int, bool]


def detect_required_btc_ema_periods(idea: dict[str, Any]) -> list[int]:
    periods: set[int] = set()
    for block in idea.get("blocks") or []:
        if str(block.get("indicator", "")).upper() == "BTC_EMA":
            periods.add(int(block.get("period") or 50))
    return sorted(periods)


def context_cache_path(root: str | Path, provider: str, market_type: str, symbol: str, timeframe: str) -> Path:
    return Path(root) / "data" / "market_cache" / provider / market_type / symbol.upper() / f"{timeframe}.csv"


def build_btc_context_series(candles: list[Candle], periods: list[int]) -> list[BTCContextPoint]:
    if not candles or not periods:
        return []
    closes = [c.close for c in candles]
    ema_by_period = {p: ema(closes, p) for p in periods}
    series: list[BTCContextPoint] = []
    for i, c in enumerate(candles):
        ev: dict[int, float | None] = {p: ema_by_period[p][i] for p in periods}
        above: dict[int, bool] = {}
        for p, v in ev.items():
            above[p] = bool(v is not None and c.close > v)
        series.append(BTCContextPoint(timestamp=c.timestamp, close=c.close, ema_values=ev, price_above_ema=above))
    return series


class BTCContextLookup:
    def __init__(self, series: list[BTCContextPoint]) -> None:
        self.series = sorted(series, key=lambda x: x.timestamp)
        self.timestamps = [x.timestamp for x in self.series]

    def at_or_before(self, ts: int) -> dict[str, Any] | None:
        if not self.series:
            return None
        idx = bisect.bisect_right(self.timestamps, ts) - 1
        if idx < 0:
            return None
        point = self.series[idx]
        return {
            "timestamp": point.timestamp,
            "close": point.close,
            "ema_values": {str(k): v for k, v in point.ema_values.items()},
            "price_above_ema": {str(k): v for k, v in point.price_above_ema.items()},
        }


def load_btc_context_lookup(
    project_root: str | Path,
    provider: str,
    market_type: str,
    idea: dict[str, Any],
) -> tuple[BTCContextLookup | None, list[str]]:
    """Load optional BTC context for BTC_EMA blocks.

    Returns a lookup plus warnings. Missing context fails closed in the backtest
    runner because unaudited BTC regime assumptions should not create wins.
    """
    periods = detect_required_btc_ema_periods(idea)
    if not periods:
        return None, []
    # Use timeframe from the first BTC_EMA block, defaulting to 15m.
    tf = "15m"
    for block in idea.get("blocks") or []:
        if str(block.get("indicator", "")).upper() == "BTC_EMA":
            tf = str(block.get("timeframe") or "15m")
            break
    path = context_cache_path(project_root, provider, market_type, "BTCUSDT", tf)
    if not path.exists():
        return None, [f"missing_btc_context:BTCUSDT:{tf}:{path}"]
    candles = read_ohlcv_csv(path)
    if len(candles) < max(periods) + 5:
        return None, [f"insufficient_btc_context:BTCUSDT:{tf}:{len(candles)}"]
    return BTCContextLookup(build_btc_context_series(candles, periods)), []
