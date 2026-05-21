-- StratProof Lab Stage 12: Idea Lab Backtest Runner schema
-- Audit-only. Audit-only; no broker execution actions.

CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.idea_lab_backtest_reports_stage12 (
    id BIGSERIAL PRIMARY KEY,
    idea_hash TEXT NOT NULL,
    dataset_fingerprint TEXT NOT NULL,
    generated_ts BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'COMPLETE_AUDIT_ONLY',
    title TEXT,
    provider TEXT,
    market_type TEXT,
    timeframe TEXT,
    timezone_name TEXT,
    session_name TEXT,
    symbols_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    overall_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    symbol_results_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    warnings_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    report_markdown TEXT,
    production_allowed INTEGER NOT NULL DEFAULT 0,
    publish_allowed INTEGER NOT NULL DEFAULT 0,
    alert_sent INTEGER NOT NULL DEFAULT 0,
    third_party_execution_allowed INTEGER NOT NULL DEFAULT 0,
    broker_execution_allowed INTEGER NOT NULL DEFAULT 0,
    real_funds_allowed INTEGER NOT NULL DEFAULT 0,
    UNIQUE(idea_hash, dataset_fingerprint)
);

CREATE INDEX IF NOT EXISTS idx_idea_backtest_stage12_hash
    ON stratproof_public.idea_lab_backtest_reports_stage12(idea_hash);
CREATE INDEX IF NOT EXISTS idx_idea_backtest_stage12_generated
    ON stratproof_public.idea_lab_backtest_reports_stage12(generated_ts DESC);
