#!/usr/bin/env python3
"""Export Stage 15 Formula Builder UI schema to JSON."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.formula_builder.ui_schema import build_stage15_ui_schema


def main() -> int:
    out = ROOT / "examples" / "formula_builder" / "stage15_formula_builder_ui_schema.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_stage15_ui_schema(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"STAGE15_SCHEMA_EXPORTED={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
