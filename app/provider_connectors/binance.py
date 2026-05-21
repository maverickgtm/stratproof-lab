"""Binance public market-data connectors for StratProof Lab.

Supports spot and USD-M futures klines. No API key, no order execution.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from .base import NormalizedOHLCV, ProviderRequest


class BinancePublicConnector:
    provider_name = 'binance'

    spot_base = 'https://api.binance.com'
    futures_base = 'https://fapi.binance.com'

    def fetch_ohlcv(self, request: ProviderRequest) -> list[NormalizedOHLCV]:
        market_type = request.market_type.lower()
        if market_type in {'spot', 'cash'}:
            base = self.spot_base
            path = '/api/v3/klines'
            source = 'binance_spot_klines'
        elif market_type in {'futures', 'usdm', 'usdt_perp', 'linear'}:
            base = self.futures_base
            path = '/fapi/v1/klines'
            source = 'binance_usdm_futures_klines'
        else:
            raise ValueError(f'Unsupported Binance market_type: {request.market_type}')
        params = {
            'symbol': request.symbol.upper(),
            'interval': request.timeframe,
            'limit': min(max(int(request.limit or 1000), 1), 1000),
        }
        if request.start_ts:
            params['startTime'] = int(request.start_ts) * 1000
        if request.end_ts:
            params['endTime'] = int(request.end_ts) * 1000
        url = f"{base}{path}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=20) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
        if isinstance(rows, dict) and rows.get('code'):
            raise RuntimeError(f'Binance error: {rows}')
        out: list[NormalizedOHLCV] = []
        for row in rows:
            out.append(NormalizedOHLCV(
                provider=self.provider_name,
                market_type=market_type,
                symbol=request.symbol.upper(),
                timeframe=request.timeframe,
                timestamp=int(int(row[0]) // 1000),
                open=float(row[1]), high=float(row[2]), low=float(row[3]),
                close=float(row[4]), volume=float(row[5]),
                source=source,
                metadata={'quote_volume': row[7] if len(row) > 7 else None, 'trades': row[8] if len(row) > 8 else None},
            ))
        return sorted(out, key=lambda x: x.timestamp)
