"""Export audit evidence that lets users inspect replay detections outside the UI."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.idea_lab.backtest_runner import IdeaAuditReport, market_cache_path, read_ohlcv_csv


TRADINGVIEW_HEADERS = ["Symbol", "Side", "Qty", "Fill Price", "Commission", "Closing Time"]
TRADINGVIEW_PREFIXES = {
    "binance": "BINANCE",
    "bybit": "BYBIT",
    "coinbase": "COINBASE",
    "kraken": "KRAKEN",
    "okx": "OKX",
}


def utc_iso(timestamp: int | None) -> str:
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def tradingview_symbol(provider: str, symbol: str) -> str:
    prefix = TRADINGVIEW_PREFIXES.get(provider.lower())
    return f"{prefix}:{symbol.upper()}" if prefix else symbol.upper()


def tradingview_time(timestamp: int) -> str:
    return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def evidence_origin(source: str) -> tuple[str, str]:
    if "synthetic" in source.lower() or "demo" in source.lower():
        return (
            "SYNTHETIC_DEMO",
            "Simulated detection on synthetic demo candles; not real market evidence or an executed account trade.",
        )
    return (
        "STORED_HISTORICAL_MARKET_DATA",
        "Simulated detection on stored historical candles; not an executed account trade. Verify source provenance.",
    )


def export_audit_evidence_csvs(
    report: IdeaAuditReport,
    idea: dict[str, Any],
    out_dir: str | Path,
    project_root: str | Path = ".",
    horizon: int | None = None,
) -> list[dict[str, Any]]:
    """Produce at most three auditable CSV artifacts for one formula audit.

    The audit identifies hypothetical replay entries against stored candles.
    These outputs deliberately do not call those entries executed trades.
    """
    output_dir = Path(out_dir)
    cache_root = Path(project_root)
    horizon_candles = int(horizon or report.overall.get("replay_horizon_candles") or 12)
    operations = report.detected_operations or []
    keyed_operations: list[tuple[str, dict[str, Any]]] = [
        (f"{report.idea_hash[:12]}-{index:05d}", operation)
        for index, operation in enumerate(operations, start=1)
    ]
    symbol_candles: dict[str, list[Any]] = {}

    def candles_for(symbol: str) -> list[Any]:
        if symbol not in symbol_candles:
            source_path = market_cache_path(cache_root, report.provider, report.market_type, symbol, report.timeframe)
            symbol_candles[symbol] = read_ohlcv_csv(source_path) if source_path.exists() else []
        return symbol_candles[symbol]

    operation_fields = [
        "operation_id", "idea_hash", "dataset_fingerprint", "detection_type",
        "provider", "market_type", "symbol", "timeframe", "source",
        "market_evidence_class", "side",
        "entry_time_utc", "entry_timestamp", "entry_price", "tp1_price",
        "sl_price", "outcome", "exit_time_utc", "exit_timestamp",
        "score_proxy", "conditions_passed", "conditions_total",
        "condition_trace", "evidence_disclaimer",
    ]
    operation_rows: list[dict[str, Any]] = []
    for operation_id, operation in keyed_operations:
        symbol = str(operation.get("symbol") or "").upper()
        entry_candle = next(
            (candle for candle in candles_for(symbol) if candle.timestamp == operation.get("timestamp")),
            None,
        )
        source = entry_candle.source if entry_candle else ""
        evidence_class, disclaimer = evidence_origin(source)
        operation_rows.append({
            "operation_id": operation_id,
            "idea_hash": report.idea_hash,
            "dataset_fingerprint": report.dataset_fingerprint,
            "detection_type": "HISTORICAL_REPLAY_DETECTION",
            "provider": report.provider,
            "market_type": report.market_type,
            "symbol": symbol,
            "timeframe": report.timeframe,
            "source": source,
            "market_evidence_class": evidence_class,
            "side": operation.get("side", ""),
            "entry_time_utc": utc_iso(operation.get("timestamp")),
            "entry_timestamp": operation.get("timestamp", ""),
            "entry_price": operation.get("entry", ""),
            "tp1_price": operation.get("tp1", ""),
            "sl_price": operation.get("sl", ""),
            "outcome": operation.get("result", ""),
            "exit_time_utc": utc_iso(operation.get("exit_timestamp")),
            "exit_timestamp": operation.get("exit_timestamp") or "",
            "score_proxy": operation.get("score_proxy", ""),
            "conditions_passed": operation.get("conditions_passed", ""),
            "conditions_total": operation.get("conditions_total", ""),
            "condition_trace": operation.get("notes", ""),
            "evidence_disclaimer": disclaimer,
        })
    operations_path = output_dir / f"{report.idea_hash}_operations_evidence.csv"
    operations_count = _write_csv(operations_path, operation_fields, operation_rows)

    candle_fields = [
        "operation_id", "provider", "market_type", "symbol", "timeframe",
        "candle_time_utc", "candle_timestamp", "open", "high", "low",
        "close", "volume", "source", "role",
    ]
    candle_rows: list[dict[str, Any]] = []
    for operation_id, operation in keyed_operations:
        symbol = str(operation.get("symbol") or "").upper()
        candles = candles_for(symbol)
        start_index = next((i for i, candle in enumerate(candles) if candle.timestamp == operation.get("timestamp")), None)
        if start_index is None:
            continue
        exit_timestamp = operation.get("exit_timestamp")
        if exit_timestamp is not None:
            end_index = next((i for i in range(start_index, len(candles)) if candles[i].timestamp == exit_timestamp), start_index)
        else:
            end_index = min(len(candles) - 1, start_index + horizon_candles)
        for index in range(start_index, end_index + 1):
            candle = candles[index]
            is_entry = index == start_index
            is_exit = exit_timestamp is not None and candle.timestamp == exit_timestamp
            role = "ENTRY_EXIT" if is_entry and is_exit else "ENTRY" if is_entry else "EXIT" if is_exit else "PATH"
            candle_rows.append({
                "operation_id": operation_id,
                "provider": candle.provider or report.provider,
                "market_type": candle.market_type or report.market_type,
                "symbol": symbol,
                "timeframe": candle.timeframe or report.timeframe,
                "candle_time_utc": utc_iso(candle.timestamp),
                "candle_timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "source": candle.source,
                "role": role,
            })
    candles_path = output_dir / f"{report.idea_hash}_candle_path_evidence.csv"
    candles_count = _write_csv(candles_path, candle_fields, candle_rows)

    tv_rows: list[dict[str, Any]] = []
    if report.market_type.lower() == "spot":
        for operation_id, operation in keyed_operations:
            if operation.get("side") != "LONG" or operation.get("result") not in {"TP1_PROTECTED", "SL_DIRECT"}:
                continue
            exit_timestamp = operation.get("exit_timestamp")
            if exit_timestamp is None:
                continue
            symbol = str(operation.get("symbol") or "").upper()
            tv_rows.append({
                "Symbol": tradingview_symbol(report.provider, symbol),
                "Side": "buy",
                "Qty": 1,
                "Fill Price": operation.get("entry"),
                "Commission": 0,
                "Closing Time": tradingview_time(operation.get("timestamp")),
            })
            tv_rows.append({
                "Symbol": tradingview_symbol(report.provider, symbol),
                "Side": "sell",
                "Qty": 1,
                "Fill Price": operation.get("tp1") if operation.get("result") == "TP1_PROTECTED" else operation.get("sl"),
                "Commission": 0,
                "Closing Time": tradingview_time(exit_timestamp),
            })
    tradingview_path = output_dir / f"{report.idea_hash}_tradingview_portfolio_replay.csv"
    tradingview_count = _write_csv(tradingview_path, TRADINGVIEW_HEADERS, tv_rows)

    return [
        {
            "kind": "operations_evidence",
            "label": "Detected operations ledger (CSV)",
            "description": "Every formula detection and replay outcome, with condition trace.",
            "path": operations_path,
            "rows": operations_count,
        },
        {
            "kind": "candle_path_evidence",
            "label": "Source candle path evidence (CSV)",
            "description": "OHLCV candles used from each entry through its replay outcome or horizon.",
            "path": candles_path,
            "rows": candles_count,
        },
        {
            "kind": "tradingview_portfolio_replay",
            "label": "TradingView Portfolio replay import (CSV)",
            "description": (
                "Closed LONG spot replay rows for TradingView visualization; "
                "it does not independently validate formula logic."
            ),
            "path": tradingview_path,
            "rows": tradingview_count,
        },
    ]
