"""OKX public historical-candle connector for StratProof Lab.

Uses public market history only. No API key and no order execution.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from .base import NormalizedOHLCV, ProviderRequest


class OKXPublicConnector:
    provider_name = "okx"
    base_url = "https://www.okx.com"

    interval_map = {
        "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1H", "4h": "4H", "1d": "1Dutc",
    }

    @staticmethod
    def _instrument(symbol: str, market_type: str) -> tuple[str, str]:
        normalized = symbol.upper().replace("-", "")
        if normalized.endswith("USDT"):
            base = normalized[:-4]
            quote = "USDT"
        else:
            raise ValueError("OKX Community download currently expects USDT symbols, e.g. BTCUSDT")
        market = market_type.lower()
        if market in {"spot", "cash"}:
            return f"{base}-{quote}", "spot"
        if market in {"linear", "usdt_perp", "swap", "usdm", "futures"}:
            return f"{base}-{quote}-SWAP", "linear"
        raise ValueError(f"Unsupported OKX market_type: {market_type}")

    def fetch_ohlcv(self, request: ProviderRequest) -> list[NormalizedOHLCV]:
        interval = self.interval_map.get(request.timeframe)
        if not interval:
            raise ValueError(f"Unsupported OKX timeframe: {request.timeframe}")
        instrument, market_type = self._instrument(request.symbol, request.market_type)
        params: dict[str, Any] = {
            "instId": instrument,
            "bar": interval,
            "limit": min(max(int(request.limit or 100), 1), 300),
        }
        if request.end_ts:
            params["after"] = int(request.end_ts) * 1000
        if request.start_ts:
            params["before"] = int(request.start_ts) * 1000
        url = f"{self.base_url}/api/v5/market/history-candles?{urllib.parse.urlencode(params)}"
        request_obj = urllib.request.Request(url, headers={"User-Agent": "StratProof-Lab/2.0"})
        with urllib.request.urlopen(request_obj, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if str(payload.get("code")) != "0":
            raise RuntimeError(f"OKX error: {payload.get('msg')} payload={payload}")
        out: list[NormalizedOHLCV] = []
        for row in payload.get("data", []) or []:
            # The final confirm flag is 1 only for completed candles.
            if len(row) > 8 and str(row[8]) != "1":
                continue
            out.append(NormalizedOHLCV(
                provider=self.provider_name,
                market_type=market_type,
                symbol=request.symbol.upper(),
                timeframe=request.timeframe,
                timestamp=int(int(row[0]) // 1000),
                open=float(row[1]), high=float(row[2]), low=float(row[3]),
                close=float(row[4]), volume=float(row[5]),
                source="okx_public_history_candles",
                metadata={
                    "instrument": instrument,
                    "volume_currency": row[6] if len(row) > 6 else None,
                    "volume_quote": row[7] if len(row) > 7 else None,
                    "confirmed": True,
                },
            ))
        return sorted(out, key=lambda x: x.timestamp)
