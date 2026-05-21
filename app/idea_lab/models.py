from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def compute_idea_hash(builder_json: dict[str, Any], dataset_fingerprint: str = "") -> str:
    payload = {"builder": builder_json, "dataset_fingerprint": dataset_fingerprint}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass
class StrategyIdea:
    name: str
    side: str = "BOTH"
    exchange: str = "bybit"
    market_type: str = "linear"
    symbols: list[str] = field(default_factory=lambda: ["BTCUSDT"])
    timeframe: str = "5m"
    date_range: str = "30d"
    timezone: str = "UTC"
    session: str = "ALL"
    score_threshold: int = 65
    blocks: list[dict[str, Any]] = field(default_factory=list)
    exit_rules: dict[str, Any] = field(default_factory=lambda: {"mode": "tp1_sl", "tp1_r": 1.0, "sl_r": 1.0})

    def to_builder_json(self) -> dict[str, Any]:
        return asdict(self)

    def idea_hash(self, dataset_fingerprint: str = "") -> str:
        return compute_idea_hash(self.to_builder_json(), dataset_fingerprint)


def example_rsi_btc_volume_idea() -> StrategyIdea:
    return StrategyIdea(
        name="RSI oversold + BTC EMA50 + volume expansion",
        side="LONG",
        exchange="bybit",
        market_type="linear",
        symbols=["SOLUSDT", "ETHUSDT"],
        timeframe="5m",
        date_range="30d",
        timezone="America/New_York",
        session="NEW_YORK_OPEN",
        score_threshold=65,
        blocks=[
            {"indicator": "RSI", "timeframe": "5m", "operator": "<", "value": 35},
            {"indicator": "BTC_EMA", "symbol": "BTCUSDT", "timeframe": "15m", "operator": "price_above", "period": 50},
            {"indicator": "RELATIVE_VOLUME", "timeframe": "5m", "operator": ">", "multiplier": 1.5, "lookback": 20},
        ],
    )


def human_readable_summary(builder_json: dict[str, Any]) -> str:
    """Create a compact user-facing summary for a saved idea card."""
    name = builder_json.get("name") or "Strategy idea"
    side = builder_json.get("side", "BOTH")
    symbols = ",".join(builder_json.get("symbols") or [])
    score = builder_json.get("score_threshold", "")
    session = builder_json.get("session", "ALL")
    blocks = builder_json.get("blocks") or []
    block_text = "; ".join(
        f"{b.get('indicator','condition')} {b.get('timeframe','')} {b.get('operator','')} {b.get('value', b.get('period', b.get('multiplier','')))}".strip()
        for b in blocks[:4]
    )
    return f"{name}: {side} {symbols} · score>={score} · session={session} · {block_text}"
