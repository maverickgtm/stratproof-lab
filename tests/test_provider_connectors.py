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
    def candle(self, timestamp: int, close: float) -> NormalizedOHLCV:
        return NormalizedOHLCV(
            provider="okx", market_type="spot", symbol="BTCUSDT", timeframe="5m",
            timestamp=timestamp, open=1.0, high=3.0, low=0.5, close=close,
            volume=10.0, source="test", metadata={"confirmed": True},
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


if __name__ == "__main__":
    unittest.main()
