#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import random
import time
from pathlib import Path


def write_symbol(root: Path, provider: str, market_type: str, symbol: str, timeframe: str, rows: int, seed: int) -> Path:
    random.seed(seed + sum(ord(c) for c in symbol))
    path = root / "data" / "market_cache" / provider / market_type / symbol / f"{timeframe}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    now = int(time.time())
    step = 300 if timeframe == "5m" else 60
    start = now - rows * step
    price = 100.0 + (sum(ord(c) for c in symbol) % 50)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["provider","market_type","symbol","timeframe","timestamp","open","high","low","close","volume","source","metadata_json"])
        writer.writeheader()
        for i in range(rows):
            drift = math.sin(i / 37.0) * 0.001 + random.uniform(-0.003, 0.003)
            # create occasional oversold/rebound zones for demo strategy
            if i % 180 in range(45, 58):
                drift -= 0.006
            if i % 180 in range(58, 78):
                drift += 0.004
            o = price
            c = max(0.0001, price * (1 + drift))
            hi = max(o, c) * (1 + random.uniform(0.0005, 0.0035))
            lo = min(o, c) * (1 - random.uniform(0.0005, 0.0035))
            vol = 1000 + random.random() * 500
            if i % 180 in range(50, 65):
                vol *= 2.2
            writer.writerow({
                "provider": provider, "market_type": market_type, "symbol": symbol, "timeframe": timeframe,
                "timestamp": start + i * step, "open": round(o, 8), "high": round(hi, 8), "low": round(lo, 8), "close": round(c, 8),
                "volume": round(vol, 4), "source": "stage12_demo_synthetic", "metadata_json": "{}",
            })
            price = c
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Generate synthetic OHLCV cache for Stage 12 demo only.")
    p.add_argument("--root", default=".")
    p.add_argument("--provider", default="bybit")
    p.add_argument("--market-type", default="linear")
    p.add_argument("--symbols", default="SOLUSDT,ETHUSDT")
    p.add_argument("--timeframe", default="5m")
    p.add_argument("--rows", type=int, default=1200)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    root = Path(args.root)
    for sym in [s.strip().upper() for s in args.symbols.split(",") if s.strip()]:
        print(write_symbol(root, args.provider, args.market_type, sym, args.timeframe, args.rows, args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
