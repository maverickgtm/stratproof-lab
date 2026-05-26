"""Coinbase Exchange public candle connector for StratProof Lab.

Uses the public Exchange market-data endpoint. No API key and no execution.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from .base import NormalizedOHLCV, ProviderRequest


class CoinbasePublicConnector:
    provider_name = "coinbase"
    base_url = "https://api.exchange.coinbase.com"

    granularity_map = {
        "1m": 60, "5m": 300, "15m": 900, "1h": 3600, "1d": 86400,
    }

    @staticmethod
    def _product(symbol: str) -> str:
        normalized = symbol.upper().replace("-", "")
        for quote in ("USDT", "USD", "USDC", "EUR", "GBP"):
            if normalized.endswith(quote):
                return f"{normalized[:-len(quote)]}-{quote}"
        raise ValueError("Coinbase Community download expects a quoted pair, e.g. BTCUSD or BTCUSDT")

    def fetch_ohlcv(self, request: ProviderRequest) -> list[NormalizedOHLCV]:
        if request.market_type.lower() not in {"spot", "cash"}:
            raise ValueError("Coinbase public candle download supports spot market data only")
        granularity = self.granularity_map.get(request.timeframe)
        if not granularity:
            raise ValueError(f"Unsupported Coinbase timeframe: {request.timeframe}")
        product = self._product(request.symbol)
        params: dict[str, Any] = {"granularity": granularity}
        if request.start_ts:
            params["start"] = int(request.start_ts)
        if request.end_ts:
            params["end"] = int(request.end_ts)
        url = f"{self.base_url}/products/{urllib.parse.quote(product)}/candles?{urllib.parse.urlencode(params)}"
        request_obj = urllib.request.Request(url, headers={"User-Agent": "StratProof-Lab/2.0"})
        with urllib.request.urlopen(request_obj, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        if isinstance(rows, dict):
            raise RuntimeError(f"Coinbase error: {rows}")
        out: list[NormalizedOHLCV] = []
        for row in rows[:min(max(int(request.limit or 300), 1), 300)]:
            # Coinbase returns [time, low, high, open, close, volume].
            out.append(NormalizedOHLCV(
                provider=self.provider_name,
                market_type="spot",
                symbol=request.symbol.upper(),
                timeframe=request.timeframe,
                timestamp=int(row[0]),
                open=float(row[3]), high=float(row[2]), low=float(row[1]),
                close=float(row[4]), volume=float(row[5]),
                source="coinbase_exchange_public_candles",
                metadata={"product_id": product},
            ))
        return sorted(out, key=lambda x: x.timestamp)
