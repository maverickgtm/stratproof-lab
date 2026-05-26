"""Connector factory for StratProof Lab Stage 11."""
from __future__ import annotations

from .binance import BinancePublicConnector
from .bybit import BybitPublicConnector
from .coinbase import CoinbasePublicConnector
from .kraken import KrakenPublicConnector
from .okx import OKXPublicConnector


def get_connector(provider: str):
    key = provider.lower().strip()
    if key == 'bybit':
        return BybitPublicConnector()
    if key == 'binance':
        return BinancePublicConnector()
    if key == 'okx':
        return OKXPublicConnector()
    if key == 'coinbase':
        return CoinbasePublicConnector()
    if key == 'kraken':
        return KrakenPublicConnector()
    raise ValueError(f'Provider not implemented in Community connector layer yet: {provider}')
