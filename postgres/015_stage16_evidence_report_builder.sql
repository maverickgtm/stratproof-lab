-- StratProof Lab Stage 16 — Evidence Report Builder UI
-- Audit/reporting schema only. No execution, broker order placement, or live alerting.

CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.evidence_report_runs (
    id BIGSERIAL PRIMARY KEY,
    run_key TEXT UNIQUE NOT NULL,
    idea_hash TEXT,
    dataset_fingerprint TEXT,
    verdict TEXT,
    closed_outcomes INTEGER,
    winrate_pct NUMERIC,
    net_r NUMERIC,
    max_drawdown_r NUMERIC,
    duplicate_rate_pct NUMERIC,
    ambiguous_same_candle INTEGER,
    report_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    report_markdown TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stratproof_public.evidence_report_cards (
    id BIGSERIAL PRIMARY KEY,
    run_key TEXT NOT NULL REFERENCES stratproof_public.evidence_report_runs(run_key) ON DELETE CASCADE,
    card_id TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT,
    metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
    warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(run_key, card_id)
);

CREATE INDEX IF NOT EXISTS idx_evidence_report_runs_idea_hash ON stratproof_public.evidence_report_runs(idea_hash);
CREATE INDEX IF NOT EXISTS idx_evidence_report_runs_created_at ON stratproof_public.evidence_report_runs(created_at DESC);
