from __future__ import annotations

PROVIDERS = [
    {"key":"bybit","name":"Bybit","asset_classes":["crypto"],"capabilities":["historical_ohlcv","funding_future","open_interest_future"],"edition":"Community","execution_default":"disabled"},
    {"key":"binance","name":"Binance","asset_classes":["crypto"],"capabilities":["historical_ohlcv","spot","usdm_futures"],"edition":"Community","execution_default":"disabled"},
    {"key":"okx","name":"OKX","asset_classes":["crypto"],"capabilities":["historical_ohlcv"],"edition":"Community","execution_default":"disabled"},
    {"key":"coinbase","name":"Coinbase","asset_classes":["crypto"],"capabilities":["historical_ohlcv"],"edition":"Community","execution_default":"disabled"},
    {"key":"kraken","name":"Kraken","asset_classes":["crypto"],"capabilities":["historical_ohlcv"],"edition":"Community","execution_default":"disabled"},
    {"key":"bitstamp","name":"Bitstamp","asset_classes":["crypto"],"capabilities":["historical_ohlcv_future"],"edition":"Community Roadmap","execution_default":"disabled"},
    {"key":"bitfinex","name":"Bitfinex","asset_classes":["crypto"],"capabilities":["historical_ohlcv_future"],"edition":"Community Roadmap","execution_default":"disabled"},
    {"key":"deribit","name":"Deribit","asset_classes":["crypto_derivatives"],"capabilities":["historical_ohlcv_future","options_data_future"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"kucoin","name":"KuCoin","asset_classes":["crypto"],"capabilities":["historical_ohlcv_future"],"edition":"Community Roadmap","execution_default":"disabled"},
    {"key":"htx","name":"HTX","asset_classes":["crypto"],"capabilities":["historical_ohlcv_future"],"edition":"Community Roadmap","execution_default":"disabled"},
    {"key":"hyperliquid","name":"Hyperliquid","asset_classes":["crypto_derivatives"],"capabilities":["historical_ohlcv_future","trades_import_future"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"csv","name":"CSV Import","asset_classes":["crypto","forex","stocks","futures","multi_asset"],"capabilities":["ohlcv_import","signals_import","trades_import"],"edition":"Community","execution_default":"not_applicable"},
    {"key":"ccxt","name":"CCXT Generic","asset_classes":["crypto"],"capabilities":["historical_ohlcv_many_exchanges"],"edition":"Community","execution_default":"disabled"},
    {"key":"interactive_brokers","name":"Interactive Brokers","asset_classes":["stocks","forex","futures","options"],"capabilities":["historical_ohlcv","account_export_import"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"polygon_io","name":"Polygon.io","asset_classes":["stocks","crypto","forex","options"],"capabilities":["historical_ohlcv","ticks_future"],"edition":"Contribution Roadmap","execution_default":"not_applicable"},
    {"key":"alpaca","name":"Alpaca Markets","asset_classes":["stocks","crypto"],"capabilities":["historical_ohlcv","account_export_import"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"mt4_mt5","name":"MT4 / MT5 Import","asset_classes":["forex","cfds","indices","commodities"],"capabilities":["history_import","trade_export_import"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"oanda_fxcm","name":"Oanda / FXCM Import","asset_classes":["forex","cfds"],"capabilities":["historical_ohlcv_future","account_export_import_future"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"fix_fast","name":"FIX/FAST Data Import","asset_classes":["multi_asset"],"capabilities":["institutional_data_pipeline_future"],"edition":"Contribution Roadmap","execution_default":"disabled"},
    {"key":"cqg_rithmic_tt","name":"CQG / Rithmic / Trading Technologies","asset_classes":["futures"],"capabilities":["institutional_data_import_future"],"edition":"Contribution Roadmap","execution_default":"disabled"},
]


def list_providers(include_future: bool = True):
    if include_future:
        return PROVIDERS
    return [p for p in PROVIDERS if p.get("edition") == "Community"]


def get_provider(key: str):
    for p in PROVIDERS:
        if p["key"] == key:
            return p
    raise KeyError(f"provider_not_registered: {key}")


def capability_matrix():
    return [
        {
            "provider": p["name"],
            "key": p["key"],
            "asset_classes": ",".join(p["asset_classes"]),
            "capabilities": ",".join(p["capabilities"]),
            "edition": p.get("edition", "Community"),
            "execution_default": p.get("execution_default", "disabled"),
        }
        for p in PROVIDERS
    ]
