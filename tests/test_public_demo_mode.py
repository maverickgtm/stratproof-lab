from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HostedPublicDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = tempfile.TemporaryDirectory()
        previous = {
            "STRATPROOF_PUBLIC_DEMO": os.environ.get("STRATPROOF_PUBLIC_DEMO"),
            "STRATPROOF_PUBLIC_RUNTIME_ROOT": os.environ.get("STRATPROOF_PUBLIC_RUNTIME_ROOT"),
        }
        os.environ["STRATPROOF_PUBLIC_DEMO"] = "1"
        os.environ["STRATPROOF_PUBLIC_RUNTIME_ROOT"] = cls.runtime.name
        spec = importlib.util.spec_from_file_location(
            "stratproof_public_demo_test_server",
            ROOT / "scripts" / "launch_local_workbench.py",
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("could_not_load_public_demo_server")
        cls.workbench = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.workbench)
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), cls.workbench.WorkbenchHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.runtime.cleanup()

    def request_json(self, path: str, payload: dict | None = None) -> tuple[int, dict]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            headers={"Content-Type": "application/json"} if body else {},
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_public_mode_hides_repository_and_shared_features(self) -> None:
        status, payload = self.request_json("/api/status")
        self.assertEqual(status, 200)
        self.assertTrue(payload["public_demo"])
        self.assertIsNone(payload["project_root"])

        with self.assertRaises(urllib.error.HTTPError) as static_error:
            urllib.request.urlopen(self.base_url + "/README.md", timeout=5)
        self.assertEqual(static_error.exception.code, 404)

        status, _ = self.request_json("/api/save_idea", {"idea": {"name": "private"}})
        self.assertEqual(status, 403)
        status, _ = self.request_json("/api/download_history", {"provider": "bybit"})
        self.assertEqual(status, 403)

    def test_public_mode_runs_labeled_synthetic_audit_and_exports_csv(self) -> None:
        status, generated = self.request_json(
            "/api/generate_demo_cache",
            {
                "provider": "bybit",
                "market_type": "spot",
                "symbols": "SOLUSDT",
                "timeframe": "5m",
                "context_timeframe": "15m",
                "rows": 300,
            },
        )
        self.assertEqual(status, 200)
        self.assertTrue(generated["ok"])

        status, audit = self.request_json(
            "/api/audit_idea",
            {
                "idea": {
                    "name": "Hosted evidence test",
                    "side": "LONG",
                    "exchange": "bybit",
                    "market_type": "spot",
                    "symbols": ["SOLUSDT"],
                    "timeframe": "5m",
                    "timezone": "UTC",
                    "session": "ALL",
                    "score_threshold": 0,
                    "blocks": [],
                    "exit_rules": {"mode": "tp1_sl", "tp1_r": 1, "sl_r": 1},
                },
                "thresholds": [0],
            },
        )
        self.assertEqual(status, 200)
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["export_policy"]["mode"], "COMMUNITY_UNRESTRICTED")
        self.assertTrue(audit["report_html_url"].startswith("/api/report_artifact?file="))
        self.assertGreater(len(audit["evidence_csvs"]), 0)

        with urllib.request.urlopen(self.base_url + audit["evidence_csvs"][0]["url"], timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("text/csv", response.headers["Content-Type"])


if __name__ == "__main__":
    unittest.main()
