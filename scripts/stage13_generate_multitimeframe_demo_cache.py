#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import csv
import math
import random
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def step_for_timeframe(tf: str) -> int:
    return {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}.get(tf, 300)


def write_symbol(root: Path, provider: str, market_type: str, symbol: str, timeframe: str, rows: int, seed: int, btc: bool = False) -> Path:
    random.seed(seed + sum(ord(c) for c in symbol) + step_for_timeframe(timeframe))
    path = root / "data" / "market_cache" / provider / market_type / symbol / f"{timeframe}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    step = step_for_timeframe(timeframe)
    start = int(time.time()) - rows * step
    price = 80000.0 if symbol == "BTCUSDT" else 80.0 + (sum(ord(c) for c in symbol) % 60)
    with path.open("w", newline="", encoding="utf-8") as f:
        fields = ["provider","market_type","symbol","timeframe","timestamp","open","high","low","close","volume","source","metadata_json"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i in range(rows):
            if btc:
                # Slight upward trend so BTC > EMA50 frequently after warmup.
                drift = 0.00035 + math.sin(i / 23.0) * 0.0008 + random.uniform(-0.0012, 0.0012)
                vol = 5000 + random.random() * 2000
            else:
                drift = math.sin(i / 37.0) * 0.001 + random.uniform(-0.003, 0.003)
                if i % 180 in range(45, 58):
                    drift -= 0.006
                if i % 180 in range(58, 78):
                    drift += 0.004
                vol = 1000 + random.random() * 500
                if i % 180 in range(50, 65):
                    vol *= 2.2
            o = price
            c = max(0.0001, price * (1 + drift))
            hi = max(o, c) * (1 + random.uniform(0.0005, 0.0035))
            lo = min(o, c) * (1 - random.uniform(0.0005, 0.0035))
            writer.writerow({
                "provider": provider, "market_type": market_type, "symbol": symbol, "timeframe": timeframe,
                "timestamp": start + i * step, "open": round(o, 8), "high": round(hi, 8), "low": round(lo, 8), "close": round(c, 8),
                "volume": round(vol, 4), "source": "stage13_demo_synthetic", "metadata_json": "{}",
            })
            price = c
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Generate Stage 13 multi-timeframe demo cache: symbols 5m + BTCUSDT 15m context.")
    p.add_argument("--root", default=".")
    p.add_argument("--provider", default="bybit")
    p.add_argument("--market-type", default="linear")
    p.add_argument("--symbols", default="SOLUSDT,ETHUSDT")
    p.add_argument("--timeframe", default="5m")
    p.add_argument("--context-timeframe", default="15m")
    p.add_argument("--rows", type=int, default=2400)
    p.add_argument("--context-rows", type=int, default=900)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    root = Path(args.root)
    for sym in [s.strip().upper() for s in args.symbols.split(",") if s.strip()]:
        print(write_symbol(root, args.provider, args.market_type, sym, args.timeframe, args.rows, args.seed))
    print(write_symbol(root, args.provider, args.market_type, "BTCUSDT", args.context_timeframe, args.context_rows, args.seed, btc=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
