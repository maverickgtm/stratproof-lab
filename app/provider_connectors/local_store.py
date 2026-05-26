"""Local storage helpers for normalized market data.

This writes CSV files in data/market_cache so Community users can run audits without
requiring PostgreSQL. Database import is a possible future contribution.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .base import NormalizedOHLCV


def cache_path(root: str | Path, provider: str, market_type: str, symbol: str, timeframe: str) -> Path:
    base = Path(root) / 'data' / 'market_cache' / provider / market_type / symbol.upper()
    base.mkdir(parents=True, exist_ok=True)
    return base / f'{timeframe}.csv'


@dataclass(frozen=True)
class CacheMergeStats:
    fetched: int
    inserted: int
    updated: int
    total_rows: int


FIELDS = ['provider', 'market_type', 'symbol', 'timeframe', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'source', 'metadata_json']


def _as_csv_row(row: NormalizedOHLCV) -> dict[str, object]:
    return {
        'provider': row.provider,
        'market_type': row.market_type,
        'symbol': row.symbol,
        'timeframe': row.timeframe,
        'timestamp': row.timestamp,
        'open': row.open,
        'high': row.high,
        'low': row.low,
        'close': row.close,
        'volume': row.volume,
        'source': row.source,
        'metadata_json': json.dumps(row.metadata or {}, ensure_ascii=False, sort_keys=True),
    }


def merge_ohlcv_csv(path: str | Path, rows: Iterable[NormalizedOHLCV]) -> CacheMergeStats:
    """Atomically upsert candles by timestamp so repeated downloads cannot duplicate evidence."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[int, dict[str, object]] = {}
    if path.exists():
        with path.open(newline='', encoding='utf-8') as input_file:
            for row in csv.DictReader(input_file):
                existing[int(row['timestamp'])] = row
    incoming = [_as_csv_row(row) for row in rows]
    inserted = 0
    updated = 0
    for row in incoming:
        timestamp = int(row['timestamp'])
        if timestamp not in existing:
            inserted += 1
        elif {key: str(existing[timestamp].get(key, '')) for key in FIELDS} != {key: str(row.get(key, '')) for key in FIELDS}:
            updated += 1
        existing[timestamp] = row
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDS)
        writer.writeheader()
        for timestamp in sorted(existing):
            writer.writerow(existing[timestamp])
    temporary.replace(path)
    return CacheMergeStats(fetched=len(incoming), inserted=inserted, updated=updated, total_rows=len(existing))


def append_ohlcv_csv(path: str | Path, rows: Iterable[NormalizedOHLCV]) -> int:
    """Backward-compatible wrapper: stores merged candles and returns fetched row count."""
    return merge_ohlcv_csv(path, rows).fetched
