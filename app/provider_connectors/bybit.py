"""Bybit public market-data connector for StratProof Lab.

Uses public kline data only. No API key, no order execution.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from .base import NormalizedOHLCV, ProviderRequest


class BybitPublicConnector:
    provider_name = 'bybit'
    base_url = 'https://api.bybit.com'

    interval_map = {
        '1m': '1', '3m': '3', '5m': '5', '15m': '15', '30m': '30',
        '1h': '60', '4h': '240', '1d': 'D',
    }

    category_map = {
        'linear': 'linear',
        'usdt_perp': 'linear',
        'inverse': 'inverse',
        'spot': 'spot',
    }

    def fetch_ohlcv(self, request: ProviderRequest) -> list[NormalizedOHLCV]:
        category = self.category_map.get(request.market_type, request.market_type)
        interval = self.interval_map.get(request.timeframe)
        if not interval:
            raise ValueError(f'Unsupported Bybit timeframe: {request.timeframe}')
        params: dict[str, Any] = {
            'category': category,
            'symbol': request.symbol.upper(),
            'interval': interval,
            'limit': min(max(int(request.limit or 1000), 1), 1000),
        }
        if request.start_ts:
            params['start'] = int(request.start_ts) * 1000
        if request.end_ts:
            params['end'] = int(request.end_ts) * 1000
        url = f"{self.base_url}/v5/market/kline?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=20) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        if str(payload.get('retCode')) != '0':
            raise RuntimeError(f"Bybit error: {payload.get('retMsg')} payload={payload}")
        rows = payload.get('result', {}).get('list', []) or []
        out: list[NormalizedOHLCV] = []
        for row in rows:
            # Bybit returns [startTime, open, high, low, close, volume, turnover]
            out.append(NormalizedOHLCV(
                provider=self.provider_name,
                market_type=category,
                symbol=request.symbol.upper(),
                timeframe=request.timeframe,
                timestamp=int(int(row[0]) // 1000),
                open=float(row[1]), high=float(row[2]), low=float(row[3]),
                close=float(row[4]), volume=float(row[5]),
                source='bybit_public_kline',
                metadata={'turnover': row[6] if len(row) > 6 else None},
            ))
        return sorted(out, key=lambda x: x.timestamp)
