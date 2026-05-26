from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.provider_connectors.base import NormalizedOHLCV, ProviderRequest
from app.provider_connectors.factory import get_connector
from app.provider_connectors.local_store import cache_path, merge_ohlcv_csv
from app.idea_lab.backtest_runner import run_idea_backtest
from app.idea_lab.evidence_export import export_audit_evidence_csvs, TRADINGVIEW_HEADERS
from scripts import launch_local_workbench as workbench


class FakeResponse:
    def __init__(self, payload: object):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class ConnectorTests(unittest.TestCase):
    def request(self, provider: str, market_type: str = "spot") -> ProviderRequest:
        return ProviderRequest(
            provider=provider,
            market_type=market_type,
            symbol="BTCUSDT",
            timeframe="5m",
            start_ts=1_700_000_000,
            end_ts=1_700_001_000,
            limit=20,
        )

    def test_factory_exposes_all_community_live_connectors(self) -> None:
        for provider in ("bybit", "binance", "okx", "coinbase", "kraken"):
            self.assertEqual(get_connector(provider).provider_name, provider)

    @patch("app.provider_connectors.okx.urllib.request.urlopen")
    def test_okx_parses_confirmed_candles_and_omits_live_candle(self, open_url) -> None:
        open_url.return_value = FakeResponse({
            "code": "0",
            "data": [
                ["1700000300000", "2", "3", "1", "2.5", "12", "3", "4", "0"],
                ["1700000000000", "1", "2", "0.5", "1.5", "10", "2", "3", "1"],
            ],
        })
        rows = get_connector("okx").fetch_ohlcv(self.request("okx", "linear"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].source, "okx_public_history_candles")
        self.assertEqual(rows[0].market_type, "linear")
        self.assertEqual(rows[0].metadata["instrument"], "BTC-USDT-SWAP")

    @patch("app.provider_connectors.coinbase.urllib.request.urlopen")
    def test_coinbase_parses_public_exchange_spot_candles(self, open_url) -> None:
        open_url.return_value = FakeResponse([
            [1700000300, 2, 4, 3, 3.5, 12],
            [1700000000, 1, 3, 2, 2.5, 10],
        ])
        rows = get_connector("coinbase").fetch_ohlcv(self.request("coinbase"))
        self.assertEqual([row.timestamp for row in rows], [1700000000, 1700000300])
        self.assertEqual(rows[0].open, 2.0)
        self.assertEqual(rows[0].metadata["product_id"], "BTC-USDT")

    @patch("app.provider_connectors.kraken.urllib.request.urlopen")
    def test_kraken_discards_the_documented_uncommitted_last_candle(self, open_url) -> None:
        open_url.return_value = FakeResponse({
            "error": [],
            "result": {
                "XXBTZUSDT": [
                    [1700000000, "1", "3", "0.5", "2", "1.8", "10", 4],
                    [1700000300, "2", "4", "1", "3", "2.5", "12", 5],
                ],
                "last": 1700000300,
            },
        })
        rows = get_connector("kraken").fetch_ohlcv(self.request("kraken"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].timestamp, 1700000000)
        self.assertEqual(rows[0].metadata["pair"], "XBTUSDT")
        self.assertTrue(rows[0].metadata["completed_only"])


class LocalStoreTests(unittest.TestCase):
    def candle(self, timestamp: int, close: float, source: str = "test") -> NormalizedOHLCV:
        return NormalizedOHLCV(
            provider="okx", market_type="spot", symbol="BTCUSDT", timeframe="5m",
            timestamp=timestamp, open=1.0, high=3.0, low=0.5, close=close,
            volume=10.0, source=source, metadata={"confirmed": True},
        )

    def test_repeated_download_does_not_duplicate_candles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "5m.csv"
            first = merge_ohlcv_csv(path, [self.candle(100, 2.0), self.candle(200, 2.5)])
            second = merge_ohlcv_csv(path, [self.candle(100, 2.0), self.candle(200, 2.75)])
            self.assertEqual((first.inserted, first.total_rows), (2, 2))
            self.assertEqual((second.inserted, second.updated, second.total_rows), (0, 1, 2))
            with path.open(newline="", encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
            self.assertEqual(len(rows), 2)
            self.assertEqual(float(rows[1]["close"]), 2.75)

    def test_audit_runner_consumes_v2_provider_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = cache_path(directory, "okx", "spot", "BTCUSDT", "5m")
            candles = [self.candle(1_700_000_000 + index * 300, 100.0 + index / 10) for index in range(90)]
            merge_ohlcv_csv(path, candles)
            report = run_idea_backtest(
                {
                    "name": "Provider v2 integration",
                    "exchange": "okx",
                    "market_type": "spot",
                    "symbols": ["BTCUSDT"],
                    "timeframe": "5m",
                    "timezone": "UTC",
                    "session": "ALL",
                    "side": "LONG",
                    "score_threshold": 0,
                    "blocks": [{"indicator": "RSI", "period": 14, "operator": "<", "value": 101}],
                },
                project_root=directory,
                market_cache_root=directory,
                use_cache=False,
            )
            self.assertEqual(report.provider, "okx")
            self.assertNotEqual(report.symbol_results[0]["verdict"], "NO_DATA")
            self.assertGreater(report.overall["signals_total"], 0)
            self.assertEqual(len(report.detected_operations), report.overall["signals_total"])

    def test_audit_exports_three_traceable_csv_files_and_tradingview_spot_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = cache_path(directory, "okx", "spot", "BTCUSDT", "5m")
            candles = [self.candle(1_700_000_000 + index * 300, 100.0 + index / 10) for index in range(130)]
            merge_ohlcv_csv(path, candles)
            idea = {
                "name": "Evidence export",
                "exchange": "okx", "market_type": "spot", "symbols": ["BTCUSDT"],
                "timeframe": "5m", "timezone": "UTC", "session": "ALL", "side": "LONG",
                "score_threshold": 0,
                "blocks": [{"indicator": "RSI", "period": 14, "operator": "<", "value": 101}],
            }
            report = run_idea_backtest(idea, project_root=directory, market_cache_root=directory, use_cache=False)
            exports = export_audit_evidence_csvs(report, idea, Path(directory) / "reports", project_root=directory)
            self.assertEqual(len(exports), 3)
            self.assertGreater(exports[0]["rows"], 0)
            self.assertGreater(exports[1]["rows"], exports[0]["rows"])
            self.assertGreater(exports[2]["rows"], 0)
            self.assertEqual(report.overall["sample_diagnostics"]["sample_status"], "ENOUGH_FOR_INITIAL_REVIEW")
            self.assertNotIn("below the preferred", " ".join(report.overall["sample_diagnostics"]["reasons"]))
            with exports[0]["path"].open(newline="", encoding="utf-8") as input_file:
                operations = list(csv.DictReader(input_file))
            self.assertEqual(operations[0]["detection_type"], "HISTORICAL_REPLAY_DETECTION")
            self.assertEqual(operations[0]["source"], "test")
            self.assertEqual(operations[0]["market_evidence_class"], "STORED_HISTORICAL_MARKET_DATA")
            self.assertIn("not an executed account trade", operations[0]["evidence_disclaimer"])
            with exports[1]["path"].open(newline="", encoding="utf-8") as input_file:
                candle_evidence = list(csv.DictReader(input_file))
            self.assertEqual(candle_evidence[0]["source"], "test")
            self.assertEqual(candle_evidence[0]["role"], "ENTRY")
            with exports[2]["path"].open(newline="", encoding="utf-8") as input_file:
                tradingview_reader = csv.DictReader(input_file)
                tradingview_rows = list(tradingview_reader)
                self.assertEqual(tradingview_reader.fieldnames, TRADINGVIEW_HEADERS)
            self.assertEqual({row["Side"] for row in tradingview_rows}, {"buy", "sell"})
            self.assertRegex(tradingview_rows[0]["Closing Time"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_tradingview_export_is_empty_for_short_or_derivative_replays(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = cache_path(directory, "okx", "linear", "BTCUSDT", "5m")
            merge_ohlcv_csv(path, [self.candle(1_700_000_000 + index * 300, 100.0) for index in range(90)])
            idea = {
                "exchange": "okx", "market_type": "linear", "symbols": ["BTCUSDT"],
                "timeframe": "5m", "session": "ALL", "side": "SHORT", "score_threshold": 0,
                "blocks": [{"indicator": "RSI", "period": 14, "operator": "<", "value": 101}],
            }
            report = run_idea_backtest(idea, project_root=directory, market_cache_root=directory, use_cache=False)
            exports = export_audit_evidence_csvs(report, idea, Path(directory) / "reports", project_root=directory)
            self.assertEqual(exports[2]["rows"], 0)

    def test_audit_export_labels_synthetic_demo_as_non_market_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = cache_path(directory, "bybit", "spot", "BTCUSDT", "5m")
            merge_ohlcv_csv(
                path,
                [self.candle(1_700_000_000 + index * 300, 100.0, "stage13_demo_synthetic") for index in range(90)],
            )
            idea = {
                "exchange": "bybit", "market_type": "spot", "symbols": ["BTCUSDT"],
                "timeframe": "5m", "session": "ALL", "side": "LONG", "score_threshold": 0,
                "blocks": [{"indicator": "RSI", "period": 14, "operator": "<", "value": 101}],
            }
            report = run_idea_backtest(idea, project_root=directory, market_cache_root=directory, use_cache=False)
            exports = export_audit_evidence_csvs(report, idea, Path(directory) / "reports", project_root=directory)
            with exports[0]["path"].open(newline="", encoding="utf-8") as input_file:
                operation = next(csv.DictReader(input_file))
            self.assertEqual(operation["market_evidence_class"], "SYNTHETIC_DEMO")
            self.assertIn("not real market evidence", operation["evidence_disclaimer"])

    def test_high_rsi_period_fails_closed_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = cache_path(directory, "okx", "spot", "BTCUSDT", "5m")
            merge_ohlcv_csv(path, [self.candle(1_700_000_000 + index * 300, 100.0) for index in range(90)])
            report = run_idea_backtest(
                {
                    "exchange": "okx", "market_type": "spot", "symbols": ["BTCUSDT"],
                    "timeframe": "5m", "session": "ALL", "side": "LONG", "score_threshold": 0,
                    "blocks": [{"indicator": "RSI", "period": 200, "operator": "<", "value": 35}],
                },
                project_root=directory,
                market_cache_root=directory,
                use_cache=False,
            )
            self.assertEqual(report.overall["signals_total"], 0)

    def test_hosted_demo_csv_quota_allows_three_downloads_before_upgrade_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            usage_file = Path(directory) / "csv_usage.json"
            with patch.object(workbench, "HOSTED_DEMO_DAILY_CSV_LIMIT", 3), patch.object(
                workbench, "EXPORT_USAGE_FILE", usage_file
            ):
                initial = workbench.export_policy()
                first = workbench.export_policy(consume=True)
                second = workbench.export_policy(consume=True)
                third = workbench.export_policy(consume=True)
                fourth = workbench.export_policy(consume=True)
            self.assertEqual(initial["downloads_remaining_today"], 3)
            self.assertTrue(first["request_allowed"])
            self.assertTrue(second["request_allowed"])
            self.assertTrue(third["request_allowed"])
            self.assertEqual(third["downloads_remaining_today"], 0)
            self.assertFalse(fourth["request_allowed"])

    def test_local_community_csv_download_policy_remains_unlimited(self) -> None:
        with patch.object(workbench, "HOSTED_DEMO_DAILY_CSV_LIMIT", 0):
            policy = workbench.export_policy(consume=True)
        self.assertEqual(policy["mode"], "COMMUNITY_LOCAL_UNLIMITED")
        self.assertTrue(policy["can_download"])
        self.assertIsNone(policy["daily_limit"])


if __name__ == "__main__":
    unittest.main()
