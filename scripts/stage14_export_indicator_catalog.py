#!/usr/bin/env python3
"""Export the Stage 14 indicator block catalog to JSON."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.idea_lab.indicator_library import write_catalog_json, block_catalog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="examples/formula_blocks/stage14_indicator_catalog.json")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_catalog_json(str(out))
    print(f"WROTE={out}")
    print(f"BLOCKS={len(block_catalog())}")
    print("SAFETY_MODEL=Audit-only by design; no broker execution in Community")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
