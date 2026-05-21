-- StratProof Lab Stage 9
-- Provider Connector Layer + normalized market data schema.
-- Audit/import only. No order execution tables are created here.

CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.normalized_ohlcv (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL,
    market_type TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    ts BIGINT NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC,
    quote_volume NUMERIC,
    source_payload JSONB DEFAULT '{}'::jsonb,
    data_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider, market_type, symbol, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS idx_normalized_ohlcv_lookup
ON stratproof_public.normalized_ohlcv(provider, market_type, symbol, timeframe, ts);

CREATE TABLE IF NOT EXISTS stratproof_public.normalized_signals (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    strategy_name TEXT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    ts BIGINT NOT NULL,
    entry NUMERIC,
    sl NUMERIC,
    tp1 NUMERIC,
    tp2 NUMERIC,
    tp3 NUMERIC,
    score NUMERIC,
    formula_version TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_normalized_signals_lookup
ON stratproof_public.normalized_signals(source, symbol, side, ts);

CREATE TABLE IF NOT EXISTS stratproof_public.normalized_trades (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL,
    account_alias TEXT,
    symbol TEXT NOT NULL,
    side TEXT,
    entry_ts BIGINT,
    exit_ts BIGINT,
    entry_price NUMERIC,
    exit_price NUMERIC,
    quantity NUMERIC,
    gross_pnl NUMERIC,
    fees NUMERIC,
    net_pnl NUMERIC,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stratproof_public.provider_downloads (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL,
    market_type TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT,
    start_ts BIGINT,
    end_ts BIGINT,
    rows_downloaded INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'PENDING',
    error TEXT,
    cache_key TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS stratproof_public.provider_connector_capabilities (
    provider_key TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    edition TEXT NOT NULL,
    asset_classes TEXT NOT NULL,
    capabilities TEXT NOT NULL,
    execution_default TEXT NOT NULL DEFAULT 'disabled',
    status TEXT NOT NULL DEFAULT 'PLANNED',
    notes TEXT
);
