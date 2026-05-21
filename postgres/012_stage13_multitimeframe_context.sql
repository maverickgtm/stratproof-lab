-- StratProof Lab Stage 13: multi-timeframe context and score-threshold audit tables.
-- Audit-only schema. Audit-only; no broker execution actions.
CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.context_snapshots_stage13 (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    provider TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    context_kind TEXT NOT NULL,
    period INTEGER,
    timestamp_utc TIMESTAMPTZ,
    value_numeric DOUBLE PRECISION,
    verdict TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS stratproof_public.idea_lab_threshold_comparisons_stage13 (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    idea_hash TEXT NOT NULL,
    dataset_fingerprint TEXT,
    score_threshold INTEGER NOT NULL,
    known INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    winrate_pct DOUBLE PRECISION NOT NULL DEFAULT 0,
    net_r_simple DOUBLE PRECISION NOT NULL DEFAULT 0,
    duplicate_rate_pct DOUBLE PRECISION NOT NULL DEFAULT 0,
    verdict TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_stage13_context_lookup
ON stratproof_public.context_snapshots_stage13(provider, market_type, symbol, timeframe, context_kind, timestamp_utc);

CREATE INDEX IF NOT EXISTS idx_stage13_threshold_idea
ON stratproof_public.idea_lab_threshold_comparisons_stage13(idea_hash, score_threshold);
