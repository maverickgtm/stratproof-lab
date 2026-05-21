-- StratProof Lab Stage 11 provider import audit schema
-- Audit-only. No exchange execution, no order routing.
CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.provider_import_jobs (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    provider TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbols TEXT[] NOT NULL,
    timeframe TEXT NOT NULL,
    start_ts BIGINT,
    end_ts BIGINT,
    status TEXT NOT NULL DEFAULT 'created',
    rows_downloaded BIGINT NOT NULL DEFAULT 0,
    error TEXT,
    audit_only BOOLEAN NOT NULL DEFAULT TRUE,
    execution_allowed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS stratproof_public.normalized_ohlcv_stage11 (
    provider TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    ts BIGINT NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    source TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (provider, market_type, symbol, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS idx_normalized_ohlcv_stage11_symbol_time
ON stratproof_public.normalized_ohlcv_stage11(symbol, timeframe, ts);
