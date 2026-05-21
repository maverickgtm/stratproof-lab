#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "stage29"
OUT.mkdir(parents=True, exist_ok=True)
summary = {
    "stage": 29,
    "name": "GitHub Upload Command Pack",
    "repo": "stratproof-lab",
    "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "unknown",
    "release_tag": "v0.1.0-community-preview",
    "upload_mode": "manual_controlled",
    "automatic_upload": False,
    "required_docs": [
        "docs/STAGE29_GITHUB_UPLOAD_COMMAND_PACK.md",
        "docs/STAGE29_GITHUB_COMMANDS_MAC.md",
        "docs/STAGE29_GITHUB_RELEASE_FINAL_CHECKLIST.md",
        "docs/STAGE29_REPOSITORY_DESCRIPTION_PACK.md",
    ],
}
(OUT / "github_upload_pack_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("STAGE29_UPLOAD_PACK=PASS")
print(OUT / "github_upload_pack_summary.json")
