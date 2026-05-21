#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from app.research_brain_view.snapshot import build_snapshot, snapshot_to_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a StratProof Lab Research Brain View snapshot JSON.")
    parser.add_argument("--db", default=None, help="Optional SQLite DB path. Use a local user-provided SQLite DB path when needed")
    parser.add_argument("--out", default="research_brain_snapshot.json", help="Output JSON path")
    args = parser.parse_args()

    snapshot = build_snapshot(args.db)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(snapshot_to_json(snapshot), encoding="utf-8")
    print(f"WROTE={out}")
    print(f"MODE={snapshot.mode}")
    print(f"AUDIT_HEALTH={snapshot.audit_health_score}")
    print(f"EVIDENCE_SCORE={snapshot.evidence_score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
