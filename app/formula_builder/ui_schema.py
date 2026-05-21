"""Stage 15 Formula Builder UI schema.

This module converts the indicator block catalog into a UI-ready schema for the
visual formula builder. It is intentionally audit-only: it builds strategy idea
JSON, not broker orders or execution instructions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from app.formula_builder.blocks import get_formula_builder_blocks


@dataclass(frozen=True)
class FormulaBuilderPreset:
    preset_id: str
    name: str
    description: str
    asset_class: str
    market_type: str
    timeframe: str
    default_blocks: List[Dict[str, Any]]
    safety_scope: str = "audit_only_by_design"


DEFAULT_PRESETS: List[FormulaBuilderPreset] = [
    FormulaBuilderPreset(
        preset_id="crypto_pullback_with_btc_context",
        name="Crypto pullback with BTC context",
        description="RSI pullback + BTC trend + relative volume + session filter.",
        asset_class="crypto",
        market_type="perpetual_futures",
        timeframe="5m",
        default_blocks=[
            {"type": "rsi", "symbol_scope": "target", "timeframe": "5m", "operator": "<", "value": 35},
            {"type": "ema_trend", "symbol": "BTCUSDT", "timeframe": "15m", "operator": "close_above_ema", "period": 50},
            {"type": "relative_volume", "timeframe": "5m", "operator": ">", "value": 1.5},
            {"type": "session_filter", "timezone": "America/New_York", "session": "new_york_open"},
            {"type": "score_threshold", "thresholds": [50, 55, 60, 65, 70, 75, 80]},
        ],
    ),
    FormulaBuilderPreset(
        preset_id="trend_continuation_audit",
        name="Trend continuation audit",
        description="EMA/VWAP alignment + ATR risk + score threshold comparison.",
        asset_class="multi_asset",
        market_type="imported_or_exchange_data",
        timeframe="15m",
        default_blocks=[
            {"type": "ema_trend", "timeframe": "15m", "operator": "close_above_ema", "period": 50},
            {"type": "vwap", "timeframe": "15m", "operator": "close_above_vwap"},
            {"type": "atr", "timeframe": "15m", "risk_mode": "avoid_extreme_volatility"},
            {"type": "score_threshold", "thresholds": [55, 60, 65, 70, 75]},
        ],
    ),
]


def build_stage15_ui_schema() -> Dict[str, Any]:
    return {
        "stage": "15",
        "product": "StratProof Lab",
        "view": "Formula Builder UI Expansion",
        "safety_model": {
            "public_label": "Audit-only by design",
            "default_execution": "disabled",
            "description": "The builder creates research ideas and evidence reports, not live broker orders.",
        },
        "supported_languages": ["en", "es", "pt", "de"],
        "block_groups": get_formula_builder_blocks(),
        "presets": [asdict(p) for p in DEFAULT_PRESETS],
        "output_contract": {
            "builder_json": "Portable formula idea definition produced by the visual builder.",
            "idea_hash": "Stable hash used by Research Cache.",
            "research_status": "draft | queued_for_audit | audited | archived",
            "next_step": "Send to Research University / run backtest / generate evidence report.",
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_stage15_ui_schema(), indent=2, ensure_ascii=False))
