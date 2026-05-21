#!/usr/bin/env python3
"""Download public OHLCV history for StratProof Lab.

Audit-only: no API keys, no order execution. Downloads public kline/OHLCV data
and stores it under data/market_cache.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.provider_connectors.base import ProviderRequest, timeframe_to_ms
from app.provider_connectors.factory import get_connector
from app.provider_connectors.local_store import append_ohlcv_csv, cache_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--provider', required=True, choices=['bybit','binance'])
    p.add_argument('--market-type', default='linear')
    p.add_argument('--symbols', required=True, help='Comma separated, e.g. BTCUSDT,ETHUSDT')
    p.add_argument('--timeframe', default='5m')
    p.add_argument('--days', type=int, default=30)
    p.add_argument('--limit', type=int, default=1000)
    p.add_argument('--root', default='.')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    now = int(time.time())
    start = now - args.days * 86400
    connector = get_connector(args.provider)
    print('STRATPROOF_STAGE11_HISTORY_DOWNLOAD')
    print(f'provider={args.provider} market_type={args.market_type} timeframe={args.timeframe} days={args.days}')
    for symbol in [s.strip().upper() for s in args.symbols.split(',') if s.strip()]:
        req = ProviderRequest(provider=args.provider, market_type=args.market_type, symbol=symbol, timeframe=args.timeframe, start_ts=start, end_ts=now, limit=args.limit)
        out_path = cache_path(args.root, args.provider, args.market_type, symbol, args.timeframe)
        print(f'FETCH symbol={symbol} path={out_path}')
        if args.dry_run:
            continue
        rows = connector.fetch_ohlcv(req)
        written = append_ohlcv_csv(out_path, rows)
        print(f'OK symbol={symbol} rows={written}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
