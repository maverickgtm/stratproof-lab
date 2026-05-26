"""Kraken public OHLC connector for StratProof Lab.

The Kraken REST response includes a live, uncommitted final candle. This
connector omits it so audit inputs contain completed candles only.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from .base import NormalizedOHLCV, ProviderRequest


class KrakenPublicConnector:
    provider_name = "kraken"
    base_url = "https://api.kraken.com"

    interval_map = {
        "1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440,
    }

    @staticmethod
    def _pair(symbol: str) -> str:
        normalized = symbol.upper().replace("-", "")
        if normalized.startswith("BTC"):
            normalized = "XBT" + normalized[3:]
        return normalized

    def fetch_ohlcv(self, request: ProviderRequest) -> list[NormalizedOHLCV]:
        if request.market_type.lower() not in {"spot", "cash"}:
            raise ValueError("Kraken public OHLC download supports spot market data only")
        interval = self.interval_map.get(request.timeframe)
        if not interval:
            raise ValueError(f"Unsupported Kraken timeframe: {request.timeframe}")
        pair = self._pair(request.symbol)
        params: dict[str, Any] = {"pair": pair, "interval": interval}
        if request.start_ts:
            params["since"] = int(request.start_ts)
        url = f"{self.base_url}/0/public/OHLC?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if payload.get("error"):
            raise RuntimeError(f"Kraken error: {payload.get('error')}")
        result = payload.get("result") or {}
        row_key = next((key for key in result if key != "last"), None)
        rows = list(result.get(row_key, []) if row_key else [])
        if rows:
            rows = rows[:-1]
        out: list[NormalizedOHLCV] = []
        for row in rows:
            timestamp = int(row[0])
            if request.end_ts and timestamp > request.end_ts:
                continue
            out.append(NormalizedOHLCV(
                provider=self.provider_name,
                market_type="spot",
                symbol=request.symbol.upper(),
                timeframe=request.timeframe,
                timestamp=timestamp,
                open=float(row[1]), high=float(row[2]), low=float(row[3]),
                close=float(row[4]), volume=float(row[6]),
                source="kraken_public_ohlc",
                metadata={"pair": pair, "vwap": row[5], "trades": row[7], "completed_only": True},
            ))
        return sorted(out, key=lambda x: x.timestamp)
