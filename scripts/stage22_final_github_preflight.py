#!/usr/bin/env python3
"""Stage 22 final GitHub preflight scanner for StratProof Lab Community.

This scanner is intentionally conservative. It looks for likely release blockers
before a public GitHub push: secrets, private infrastructure references, large
artifacts, binary/database dumps, placeholder license text, risky product claims,
and legacy internal branding.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

TEXT_EXTS = {
    ".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".html",
    ".css", ".js", ".sql", ".csv", ".example", ".gitignore", ""
}
BINARY_OR_PRIVATE_EXTS = {
    ".pem", ".key", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db", ".dump",
    ".gz", ".zip", ".tar", ".7z", ".rar", ".parquet", ".feather"
}
SECRET_PATTERNS = [
    ("private_key_block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |)?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic_api_key_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}")),
]
PRIVATE_PATTERNS = [
    ("private_ip_or_known_server", re.compile(r"(194\.60\.87\.39|43\.162\.119\.237|43\.157\.95\.145)")),
    ("absolute_private_path", re.compile(r"(/opt/clawtrade-ai-lab|/root/|/home/ubuntu|/Users/marioantillon|Documents/openclaw|id_ed25519_contabo|openclaw\.pem)")),
    ("internal_legacy_brand", re.compile(r"(?i)(OpenClaw|clawtrade|Cornix|Telegram|autotrading|real funds|live signals)")),
]
RISKY_CLAIM_PATTERNS = [
    ("positive_guaranteed_return_claim", re.compile(r"(?i)(profit guaranteed|risk[- ]?free|sure win|100% winrate|guaranteed profit|guaranteed returns are offered)")),
    ("positive_financial_advice_claim", re.compile(r"(?i)(we provide financial advice|we offer investment advice|we recommend buying|we recommend selling)")),
]

@dataclass
class Finding:
    severity: str
    category: str
    path: str
    line: int | None
    message: str
    excerpt: str = ""


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts:
            continue
        yield path


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return None
    except Exception:
        return None


def add_line_findings(findings: list[Finding], root: Path, path: Path, patterns, severity: str, category: str, allow_internal_docs: bool = False):
    text = read_text(path)
    if text is None:
        return
    rel = str(path.relative_to(root))
    if allow_internal_docs and rel.startswith("docs/STAGE"):
        return
    for i, line in enumerate(text.splitlines(), start=1):
        for name, rx in patterns:
            if rx.search(line):
                findings.append(Finding(severity, category + ":" + name, rel, i, f"Pattern matched: {name}", line[:240]))


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout[-4000:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="reports/stage22/final_preflight_report.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    findings: list[Finding] = []

    files = list(iter_files(root))
    total_size = 0
    for path in files:
        rel = str(path.relative_to(root))
        size = path.stat().st_size
        total_size += size
        if size > 5_000_000:
            findings.append(Finding("WARN", "large_file", rel, None, f"File is larger than 5 MB: {size} bytes"))
        if path.suffix.lower() in BINARY_OR_PRIVATE_EXTS:
            findings.append(Finding("BLOCKER", "private_or_archive_extension", rel, None, f"Potentially unsafe extension for public repo: {path.suffix}"))
        if is_text_file(path):
            rel_for_scan = str(path.relative_to(root))
            add_line_findings(findings, root, path, SECRET_PATTERNS, "BLOCKER", "secret")
            if not rel_for_scan.startswith("reports/stage22/") and rel_for_scan != "scripts/stage22_final_github_preflight.py":
                add_line_findings(findings, root, path, PRIVATE_PATTERNS, "WARN", "private_reference", allow_internal_docs=True)
                add_line_findings(findings, root, path, RISKY_CLAIM_PATTERNS, "BLOCKER", "risky_claim")

    # License completeness check.
    lic = root / "LICENSE"
    if not lic.exists():
        findings.append(Finding("BLOCKER", "license_missing", "LICENSE", None, "LICENSE file missing"))
    else:
        lic_text = read_text(lic) or ""
        if len(lic_text) < 15_000 or "GNU AFFERO GENERAL PUBLIC LICENSE" not in lic_text:
            findings.append(Finding("BLOCKER", "license_placeholder", "LICENSE", None, "LICENSE does not appear to contain the full canonical AGPL-3.0 text."))

    # README minimum commercial/positioning checks.
    readme = root / "README.md"
    if readme.exists():
        r = (read_text(readme) or "").lower()
        required_phrases = ["audit", "evidence", "bot", "guaranteed returns", "financial advice"]
        for phrase in required_phrases:
            if phrase not in r:
                findings.append(Finding("WARN", "readme_missing_positioning", "README.md", None, f"README may be missing phrase/concept: {phrase}"))
    else:
        findings.append(Finding("BLOCKER", "readme_missing", "README.md", None, "README.md missing"))

    compile_code, compile_out = run_cmd([sys.executable, "-m", "compileall", "-q", "app", "scripts", "tests"], root)
    if compile_code != 0:
        findings.append(Finding("BLOCKER", "python_compile_failed", "app/scripts/tests", None, "Python compileall failed", compile_out))

    smoke = root / "tests" / "smoke_test_public_package.py"
    if smoke.exists():
        smoke_code, smoke_out = run_cmd([sys.executable, str(smoke)], root)
        if smoke_code != 0:
            findings.append(Finding("BLOCKER", "smoke_test_failed", str(smoke.relative_to(root)), None, "Smoke test failed", smoke_out))
    else:
        findings.append(Finding("WARN", "smoke_test_missing", "tests/smoke_test_public_package.py", None, "Smoke test missing"))

    counts = {"BLOCKER": 0, "WARN": 0, "INFO": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    verdict = "PASS" if counts.get("BLOCKER", 0) == 0 else "BLOCKED"

    report = {
        "ok": verdict == "PASS",
        "verdict": verdict,
        "root": str(root),
        "files_scanned": len(files),
        "total_size_bytes": total_size,
        "finding_counts": counts,
        "findings": [asdict(f) for f in findings],
        "next_action": "Resolve BLOCKER findings before public GitHub release." if verdict == "BLOCKED" else "Ready for final manual review before GitHub.",
    }
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["verdict", "files_scanned", "total_size_bytes", "finding_counts", "next_action"]}, indent=2))
    return 0 if verdict == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
