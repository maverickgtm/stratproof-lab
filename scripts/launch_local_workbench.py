#!/usr/bin/env python3
"""Launch the StratProof Lab local workbench.

This is a local-only HTTP server for trying real formulas end-to-end before a
GitHub release. It uses only the Python standard library and the existing
StratProof audit modules. It does not execute trades or connect to brokers.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
import webbrowser
from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.idea_lab.backtest_runner import run_idea_backtest
from app.idea_lab.score_threshold_simulator import simulate_thresholds, render_threshold_markdown
from app.idea_lab.saved_ideas import save_idea, list_saved_ideas, load_saved_idea
from app.idea_lab.indicator_library import block_catalog

PORT_DEFAULT = 8765
REPORT_DIR = PROJECT_ROOT / "reports" / "local_workbench"
IDEA_DIR = PROJECT_ROOT / "data" / "local_workbench_ideas"


def json_safe(value: Any) -> Any:
    """Return a browser-safe JSON payload with no NaN/Infinity values."""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def json_response(handler: SimpleHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(json_safe(payload), ensure_ascii=False, indent=2, default=str, allow_nan=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def read_body(handler: SimpleHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    if length > 2_000_000:
        raise ValueError("request_body_too_large")
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    try:
        return json.loads(raw or "{}")
    except Exception as exc:
        raise ValueError(f"invalid_json_body:{exc}") from exc


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except Exception:
        return str(path)



def build_relaxed_discovery_idea(idea: dict[str, Any]) -> dict[str, Any]:
    """Create a non-promotional discovery variant to diagnose sample starvation."""
    import copy
    relaxed = copy.deepcopy(idea or {})
    relaxed["name"] = str(relaxed.get("name") or "Strategy idea") + " — relaxed discovery probe"
    relaxed["session"] = "ALL"
    relaxed["score_threshold"] = min(float(relaxed.get("score_threshold") or 65), 50)
    for block in relaxed.get("blocks") or []:
        indicator = str(block.get("indicator") or "").upper()
        if indicator == "RELATIVE_VOLUME":
            block["multiplier"] = min(float(block.get("multiplier") or block.get("value") or 1.5), 1.1)
            block["operator"] = ">"
        elif indicator == "RSI":
            block["value"] = max(float(block.get("value") or 35), 45)
            block["operator"] = "<"
    relaxed["discovery_probe"] = True
    relaxed["discovery_note"] = "Relaxed sample-size probe only. Do not treat as final strategy evidence."
    return relaxed



def _esc(value: Any) -> str:
    import html
    return html.escape(str(value if value is not None else ""))


def render_visual_report_html(report: Any, idea: dict[str, Any]) -> str:
    data = asdict(report) if not isinstance(report, dict) else report
    overall = data.get("overall") or {}
    rows = data.get("symbol_results") or []
    verdict = str(overall.get("verdict") or "UNKNOWN")
    known = float(overall.get("known") or 0)
    wins = float(overall.get("wins") or 0)
    losses = float(overall.get("losses") or 0)
    wr = float(overall.get("winrate_pct") or 0)
    net = float(overall.get("net_r_simple") or 0)
    dup = float(overall.get("duplicate_rate_pct") or 0)
    diag = overall.get("sample_diagnostics") or {}
    max_abs_net = max([abs(float(r.get("net_r_simple") or 0)) for r in rows] + [1.0])
    max_known = max([float(r.get("known") or 0) for r in rows] + [1.0])

    def bar(width_pct: float, cls: str = "barFill") -> str:
        width_pct = max(0, min(100, float(width_pct or 0)))
        return f'<div class="bar"><div class="{cls}" style="width:{width_pct:.2f}%"></div></div>'

    sym_cards = []
    for r in rows:
        rnet = float(r.get("net_r_simple") or 0)
        rknown = float(r.get("known") or 0)
        sym_cards.append(f'''<div class="symCard">
          <div class="symHead"><b>{_esc(r.get('symbol'))}</b><span>{_esc(r.get('side'))}</span></div>
          <div class="small">Known {int(rknown)} · Wins {int(float(r.get('wins') or 0))} · Losses {int(float(r.get('losses') or 0))}</div>
          <div class="metricLine"><span>Winrate</span><b>{_esc(r.get('winrate_pct'))}%</b></div>{bar(float(r.get('winrate_pct') or 0))}
          <div class="metricLine"><span>Net R</span><b class="{'good' if rnet>0 else 'bad' if rnet<0 else ''}">{rnet:g}</b></div>{bar(abs(rnet)/max_abs_net*100, 'barFillBad' if rnet<0 else 'barFillGood')}
          <div class="metricLine"><span>Sample share</span><b>{(rknown/max_known*100):.0f}%</b></div>{bar(rknown/max_known*100)}
          <div class="verdict">{_esc(r.get('verdict'))}</div>
        </div>''')
    reasons = ''.join(f'<li>{_esc(x)}</li>' for x in (diag.get('reasons') or [])) or '<li>No extra diagnostics.</li>'
    recs = ''.join(f'<li>{_esc(x)}</li>' for x in (diag.get('recommended_next_tests') or [])) or '<li>No extra tests suggested.</li>'
    blocks = ''.join(f'<span class="pill">{_esc((b or {}).get("indicator"))} · {_esc((b or {}).get("operator"))}</span>' for b in (idea.get('blocks') or []))
    sym_html = ''.join(sym_cards) or '<div class="small">No symbol results.</div>'
    wr_cls = 'good' if wr >= 55 else 'bad' if wr < 45 else ''
    net_cls = 'good' if net > 0 else 'bad' if net < 0 else ''
    net_bar_cls = 'barFillBad' if net < 0 else 'barFillGood'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>StratProof Visual Evidence Report</title>
<style>
:root{{--bg:#06101d;--panel:#101c30;--line:#294866;--text:#eaf1fb;--muted:#aeb9c8;--cyan:#6ed7ff;--green:#7ef0a0;--yellow:#ffd96a;--red:#ff7b7b;--purple:#b899ff}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 20% 0,#132842,#06101d 48%,#030712);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--text)}}
header{{padding:28px 34px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:16px;align-items:center}}h1{{margin:0;font-size:30px;letter-spacing:.04em}}.sub{{color:var(--muted);margin-top:6px}}.tag{{border:1px solid var(--line);border-radius:999px;padding:10px 14px;color:var(--cyan);background:#0c1b30;font-weight:800;white-space:nowrap}}
.wrap{{padding:24px;max-width:1280px;margin:0 auto}}.grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}}.panel{{background:rgba(16,28,48,.92);border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:0 18px 40px rgba(0,0,0,.24);overflow:hidden}}.wide{{grid-column:1/-1}}.metric{{font-size:44px;font-weight:950;line-height:1;color:var(--yellow);overflow-wrap:anywhere}}.good{{color:var(--green)}}.bad{{color:var(--red)}}.muted{{color:var(--muted)}}.small{{font-size:13px;color:var(--muted);line-height:1.55}}.pill{{display:inline-block;border:1px solid var(--line);background:#0b1a30;color:var(--muted);padding:6px 10px;border-radius:999px;margin:4px;font-size:12px}}.bar{{height:12px;background:#071225;border:1px solid #203954;border-radius:999px;overflow:hidden;margin:7px 0 12px}}.barFill{{height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple))}}.barFillGood{{height:100%;background:linear-gradient(90deg,var(--green),#d6ffe2)}}.barFillBad{{height:100%;background:linear-gradient(90deg,var(--red),var(--yellow))}}.symGrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}.symCard{{background:#081426;border:1px solid var(--line);border-radius:18px;padding:15px}}.symHead{{display:flex;justify-content:space-between;gap:8px;align-items:center;font-size:18px;margin-bottom:8px}}.metricLine{{display:flex;justify-content:space-between;color:var(--muted);font-size:13px}}li{{margin:7px 0}}.verdict{{margin-top:12px;color:var(--cyan);font-weight:800;word-break:break-word}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}header{{display:block}}}}
</style></head><body>
<header><div><h1>StratProof Lab // Visual Evidence Report</h1><div class="sub">Client-ready audit view generated from the same local report JSON. Audit-only by design.</div></div><div class="tag">{_esc(verdict)}</div></header>
<div class="wrap"><div class="grid">
<section class="panel"><div class="small">Known outcomes</div><div class="metric">{known:g}</div><div class="small">Wins {wins:g} · Losses {losses:g}</div>{bar((known/30)*100)}</section>
<section class="panel"><div class="small">Honest winrate</div><div class="metric {wr_cls}">{wr:.2f}%</div><div class="small">No guaranteed returns. Evidence only.</div>{bar(wr)}</section>
<section class="panel"><div class="small">Net R simple</div><div class="metric {net_cls}">{net:g}</div><div class="small">Duplicate risk {dup:.2f}%</div>{bar(abs(net)/max(max_abs_net,1)*100, net_bar_cls)}</section>
<section class="panel wide"><h2>Configuration</h2><span class="pill">Provider: {_esc(data.get('provider'))}</span><span class="pill">Symbols: {_esc(', '.join(data.get('symbols') or []))}</span><span class="pill">Timeframe: {_esc(data.get('timeframe'))}</span><span class="pill">Session: {_esc(data.get('session'))}</span><span class="pill">Score ≥ {_esc(idea.get('score_threshold'))}</span><div style="margin-top:10px">{blocks}</div></section>
<section class="panel wide"><h2>Symbol Results</h2><div class="symGrid">{sym_html}</div></section>
<section class="panel"><h2>Why this result needs review</h2><ul>{reasons}</ul></section>
<section class="panel"><h2>Next recommended tests</h2><ul>{recs}</ul></section>
<section class="panel"><h2>Safety</h2><p class="small">This report validates evidence only. It does not send alerts, place broker orders, manage funds, or provide financial advice.</p></section>
</div></div></body></html>'''

def command(args: list[str], timeout: int = 90) -> dict[str, Any]:
    started = time.time()
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(PROJECT_ROOT) + ((os.pathsep + existing) if existing else "")
    proc = subprocess.run(
        args,
        cwd=str(PROJECT_ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    return {
        "cmd": args,
        "exit_code": proc.returncode,
        "duration_sec": round(time.time() - started, 3),
        "stdout": proc.stdout[-6000:],
        "stderr": proc.stderr[-6000:],
        "ok": proc.returncode == 0,
    }


class WorkbenchHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter logs
        print("[workbench] " + fmt % args)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if any(part in {".git", ".env"} or part.startswith(".env.") for part in Path(parsed.path).parts):
            json_response(self, {"ok": False, "error": "path_not_served"}, status=404)
            return
        if parsed.path == "/":
            self.send_response(302)
            self.send_header("Location", "/app/auditor_dashboard/local_workbench.html")
            self.end_headers()
            return
        if parsed.path == "/api/status":
            payload = {
                "product": "StratProof Lab",
                "mode": "LOCAL_WORKBENCH_AUDIT_ONLY",
                "project_root": str(PROJECT_ROOT),
                "report_dir": rel(REPORT_DIR),
                "data_cache_exists": (PROJECT_ROOT / "data" / "market_cache").exists(),
                "safety": "Audit-only by design. No broker execution.",
            }
            json_response(self, payload)
            return
        if parsed.path == "/api/indicator_catalog":
            catalog = block_catalog()
            json_response(self, {"blocks": catalog, "count": len(catalog)})
            return
        if parsed.path == "/api/saved_ideas":
            json_response(self, {"ideas": list_saved_ideas(), "count": len(list_saved_ideas())})
            return
        if parsed.path == "/api/load_idea":
            qs = parse_qs(parsed.query)
            idea_hash = (qs.get("hash") or [""])[0]
            item = load_saved_idea(idea_hash) if idea_hash else None
            json_response(self, {"idea": item, "found": bool(item)})
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/api/download_history":
                payload = read_body(self)
                provider = str(payload.get("provider") or "bybit").lower()
                market_type = str(payload.get("market_type") or "linear")
                symbols = str(payload.get("symbols") or "SOLUSDT,ETHUSDT").upper().replace(" ", "")
                timeframe = str(payload.get("timeframe") or "5m")
                days = int(payload.get("days") or 30)
                limit = int(payload.get("limit") or 1000)
                context_timeframe = str(payload.get("context_timeframe") or "15m")
                include_btc_context = bool(payload.get("include_btc_context", True))
                live_download_providers = {"bybit", "binance", "okx", "coinbase", "kraken"}
                if provider not in live_download_providers:
                    json_response(self, {
                        "ok": False,
                        "provider": provider,
                        "reason": "provider_registered_but_live_downloader_not_implemented_in_community_preview",
                        "message": "This provider is part of the connector roadmap/import matrix. Use a live Community connector, CSV/local import, or Generate offline demo cache for now.",
                        "commands": [],
                    }, 200)
                    return
                commands: list[dict[str, Any]] = []
                commands.append(command([
                    sys.executable, "scripts/stage11_download_history.py",
                    "--provider", provider,
                    "--market-type", market_type,
                    "--symbols", symbols,
                    "--timeframe", timeframe,
                    "--days", str(days),
                    "--limit", str(limit),
                    "--root", ".",
                ], timeout=120))
                # Always make sure BTC context exists when requested.
                # If BTCUSDT is already in the main symbols, the first download only
                # fetches the main timeframe. BTC_EMA can require a different
                # context timeframe such as 15m, so we still fetch BTCUSDT again
                # when context_timeframe != timeframe. This prevents confusing
                # zero-sample audits after a successful public-history download.
                symbol_set = {s.strip().upper() for s in symbols.split(",") if s.strip()}
                should_fetch_btc_context = bool(include_btc_context) and (
                    "BTCUSDT" not in symbol_set or str(context_timeframe) != str(timeframe)
                )
                if should_fetch_btc_context:
                    commands.append(command([
                        sys.executable, "scripts/stage11_download_history.py",
                        "--provider", provider,
                        "--market-type", market_type,
                        "--symbols", "BTCUSDT",
                        "--timeframe", context_timeframe,
                        "--days", str(days),
                        "--limit", str(limit),
                        "--root", ".",
                    ], timeout=120))
                json_response(self, {"ok": all(c["ok"] for c in commands), "commands": commands})
                return

            if self.path == "/api/generate_demo_cache":
                payload = read_body(self)
                symbols = str(payload.get("symbols") or "SOLUSDT,ETHUSDT").upper().replace(" ", "")
                timeframe = str(payload.get("timeframe") or "5m")
                context_timeframe = str(payload.get("context_timeframe") or "15m")
                rows = int(payload.get("rows") or 2400)
                result = command([
                    sys.executable, "scripts/stage13_generate_multitimeframe_demo_cache.py",
                    "--symbols", symbols,
                    "--timeframe", timeframe,
                    "--context-timeframe", context_timeframe,
                    "--rows", str(rows),
                ], timeout=90)
                json_response(self, result, 200 if result["ok"] else 500)
                return

            if self.path in {"/api/audit_idea", "/api/relaxed_audit"}:
                payload = read_body(self)
                idea = payload.get("idea") or payload
                if isinstance(idea, str):
                    idea = json.loads(idea)
                mode = "RELAXED_DISCOVERY_PROBE" if self.path == "/api/relaxed_audit" else "STRICT_USER_FORMULA"
                if self.path == "/api/relaxed_audit":
                    idea = build_relaxed_discovery_idea(idea)
                thresholds_raw = payload.get("thresholds") or [50, 55, 60, 65, 70, 75, 80]
                thresholds = [int(x) for x in thresholds_raw]
                REPORT_DIR.mkdir(parents=True, exist_ok=True)
                IDEA_DIR.mkdir(parents=True, exist_ok=True)
                ts = int(time.time())
                idea_path = IDEA_DIR / f"idea_{ts}_{'relaxed' if self.path == '/api/relaxed_audit' else 'strict'}.json"
                idea_path.write_text(json.dumps(idea, ensure_ascii=False, indent=2), encoding="utf-8")
                report = run_idea_backtest(idea, project_root=PROJECT_ROOT, use_cache=False)
                report_json = REPORT_DIR / f"{report.idea_hash}_report.json"
                report_md = REPORT_DIR / f"{report.idea_hash}_report.md"
                report_html = REPORT_DIR / f"{report.idea_hash}_visual_report.html"
                report_payload = json_safe(asdict(report))
                report_json.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
                report_md.write_text(report.report_markdown or "", encoding="utf-8")
                report_html.write_text(render_visual_report_html(report, idea), encoding="utf-8")
                rows = simulate_thresholds(idea, thresholds, project_root=PROJECT_ROOT, use_cache=False)
                threshold_json = REPORT_DIR / f"{report.idea_hash}_thresholds.json"
                threshold_md = REPORT_DIR / f"{report.idea_hash}_thresholds.md"
                rows_payload = json_safe(rows)
                threshold_json.write_text(json.dumps(rows_payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
                threshold_md.write_text(render_threshold_markdown(rows), encoding="utf-8")
                json_response(self, {
                    "ok": True,
                    "mode": mode,
                    "idea_path": rel(idea_path),
                    "idea": idea,
                    "report_json": rel(report_json),
                    "report_md": rel(report_md),
                    "report_html": rel(report_html),
                    "threshold_json": rel(threshold_json),
                    "threshold_md": rel(threshold_md),
                    "report_json_url": "/" + rel(report_json),
                    "report_md_url": "/" + rel(report_md),
                    "report_html_url": "/" + rel(report_html),
                    "threshold_json_url": "/" + rel(threshold_json),
                    "threshold_md_url": "/" + rel(threshold_md),
                    "report": report_payload,
                    "thresholds": rows_payload,
                })
                return

            if self.path == "/api/save_idea":
                payload = read_body(self)
                idea = payload.get("idea") or payload
                idea_hash = save_idea(idea, title=idea.get("name") if isinstance(idea, dict) else None)
                json_response(self, {"ok": True, "idea_hash": idea_hash, "ideas": list_saved_ideas()})
                return

            json_response(self, {"ok": False, "error": "unknown_endpoint", "path": self.path}, status=404)
        except Exception as exc:
            json_response(self, {"ok": False, "error": repr(exc)}, status=500)


def main() -> int:
    port = int(os.environ.get("STRATPROOF_WORKBENCH_PORT") or PORT_DEFAULT)
    server = ThreadingHTTPServer(("127.0.0.1", port), WorkbenchHandler)
    url = f"http://127.0.0.1:{port}/app/auditor_dashboard/local_workbench.html"
    print("STRATPROOF_LOCAL_WORKBENCH")
    print(f"URL={url}")
    print("MODE=AUDIT_ONLY_LOCAL_NO_BROKER_EXECUTION")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping StratProof local workbench.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
