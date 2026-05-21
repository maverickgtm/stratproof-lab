#!/usr/bin/env python3
"""Generate lightweight GitHub landing helper assets for StratProof Lab Stage 17."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "github"
OUT.mkdir(parents=True, exist_ok=True)

files = {
    "screenshot_order.md": """# Recommended Screenshot Order\n\n1. Formula Builder UI\n2. Evidence Report Builder UI\n3. Research Brain View\n4. Data Setup / Provider Connector Layer\n5. Saved Ideas Library\n""",
    "tagline.txt": "Audit trading strategies before risking money.\n",
    "short_description.txt": "StratProof Lab is an audit-first crypto strategy research platform designed to grow into a multi-market evidence framework.\n",
}

for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8")

print(f"Generated GitHub helper assets in {OUT}")
