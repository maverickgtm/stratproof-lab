#!/usr/bin/env python3
"""Build Stage 16 evidence cards + Markdown from an audit JSON file."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.evidence_reports import write_evidence_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build StratProof Stage 16 evidence report outputs.")
    parser.add_argument("input_json", help="Idea Lab / backtest JSON summary")
    parser.add_argument("--out-dir", default="reports/evidence_reports", help="Output directory")
    args = parser.parse_args()
    outputs = write_evidence_outputs(args.input_json, args.out_dir)
    print("STAGE16_EVIDENCE_REPORT_BUILDER_DONE=1")
    for key, value in outputs.items():
        print(f"{key.upper()}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
