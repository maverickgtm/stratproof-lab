#!/usr/bin/env python3
"""Export public pricing assets for StratProof Lab Stage 26."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.product_branding.monetization import public_pricing_summary


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "reports" / "stage26" / "pricing_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(public_pricing_summary(), indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
