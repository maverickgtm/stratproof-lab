#!/usr/bin/env python3
"""CSV import wizard for StratProof Lab normalized datasets.

Stage 11 inspects CSV files and maps columns for OHLCV/signals/trades. It is
read-only by default and prints the mapping suggestion.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

OHLCV_SYNONYMS = {
    'timestamp': {'timestamp','time','date','datetime','open_time','ts'},
    'open': {'open','o'},
    'high': {'high','h'},
    'low': {'low','l'},
    'close': {'close','c'},
    'volume': {'volume','vol','v'},
    'symbol': {'symbol','pair','ticker','instrument'},
}


def suggest_mapping(headers: list[str]) -> dict[str, str | None]:
    lowered = {h.lower().strip(): h for h in headers}
    mapping: dict[str, str | None] = {}
    for canonical, synonyms in OHLCV_SYNONYMS.items():
        found = None
        for s in synonyms:
            if s in lowered:
                found = lowered[s]
                break
        mapping[canonical] = found
    return mapping


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('csv_file')
    p.add_argument('--kind', choices=['ohlcv','signals','trades'], default='ohlcv')
    p.add_argument('--sample', type=int, default=5)
    args = p.parse_args()
    path = Path(args.csv_file)
    with path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = [row for _, row in zip(range(args.sample), reader)]
    print('STRATPROOF_STAGE11_CSV_IMPORT_WIZARD')
    print(f'file={path}')
    print(f'kind={args.kind}')
    print(f'headers={headers}')
    print('suggested_mapping=')
    for k,v in suggest_mapping(headers).items():
        print(f'  {k}: {v}')
    print('sample_rows=')
    for row in rows:
        print(row)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
