"""StratProof provider connector base classes.

Audit-first: connectors import or download historical data only. Execution is not
implemented here and should remain disabled in the public/community edition.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Protocol


@dataclass(frozen=True)
class ProviderRequest:
    provider: str
    market_type: str
    symbol: str
    timeframe: str
    start_ts: int | None = None
    end_ts: int | None = None
    limit: int = 1000
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class NormalizedOHLCV:
    provider: str
    market_type: str
    symbol: str
    timeframe: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HistoricalOHLCVConnector(Protocol):
    provider_name: str

    def fetch_ohlcv(self, request: ProviderRequest) -> list[NormalizedOHLCV]:
        """Fetch historical candles in normalized format."""
        raise NotImplementedError


def timeframe_to_ms(timeframe: str) -> int:
    table = {
        '1m': 60_000,
        '3m': 180_000,
        '5m': 300_000,
        '15m': 900_000,
        '30m': 1_800_000,
        '1h': 3_600_000,
        '4h': 14_400_000,
        '1d': 86_400_000,
    }
    if timeframe not in table:
        raise ValueError(f'Unsupported timeframe: {timeframe}')
    return table[timeframe]
