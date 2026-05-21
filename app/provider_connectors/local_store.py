"""Local storage helpers for normalized market data.

This writes CSV files in data/market_cache so Community users can run audits without
requiring PostgreSQL. PostgreSQL import remains available for Pro/advanced setups.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .base import NormalizedOHLCV


def cache_path(root: str | Path, provider: str, market_type: str, symbol: str, timeframe: str) -> Path:
    base = Path(root) / 'data' / 'market_cache' / provider / market_type / symbol.upper()
    base.mkdir(parents=True, exist_ok=True)
    return base / f'{timeframe}.csv'


def append_ohlcv_csv(path: str | Path, rows: Iterable[NormalizedOHLCV]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    count = 0
    with path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['provider','market_type','symbol','timeframe','timestamp','open','high','low','close','volume','source','metadata_json'])
        if not exists:
            writer.writeheader()
        for r in rows:
            writer.writerow({
                'provider': r.provider,
                'market_type': r.market_type,
                'symbol': r.symbol,
                'timeframe': r.timeframe,
                'timestamp': r.timestamp,
                'open': r.open,
                'high': r.high,
                'low': r.low,
                'close': r.close,
                'volume': r.volume,
                'source': r.source,
                'metadata_json': json.dumps(r.metadata or {}, ensure_ascii=False, sort_keys=True),
            })
            count += 1
    return count
