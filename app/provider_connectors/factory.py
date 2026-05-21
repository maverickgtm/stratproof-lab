"""Connector factory for StratProof Lab Stage 11."""
from __future__ import annotations

from .binance import BinancePublicConnector
from .bybit import BybitPublicConnector


def get_connector(provider: str):
    key = provider.lower().strip()
    if key == 'bybit':
        return BybitPublicConnector()
    if key == 'binance':
        return BinancePublicConnector()
    raise ValueError(f'Provider not implemented in Community connector layer yet: {provider}')
