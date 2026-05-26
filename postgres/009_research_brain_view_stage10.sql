-- StratProof Lab Stage 10: Research Brain View observability schema.
-- Visual/observability only. Visual/observability only; no broker execution actions.
CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.research_brain_snapshots (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    mode TEXT NOT NULL DEFAULT 'VISUAL_OBSERVABILITY_ONLY',
    workflow_readiness_percent NUMERIC,
    active_departments INTEGER,
    observed_outcomes INTEGER,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    departments JSONB NOT NULL DEFAULT '[]'::jsonb,
    activity_feed JSONB NOT NULL DEFAULT '[]'::jsonb,
    production_allowed INTEGER NOT NULL DEFAULT 0,
    publish_allowed INTEGER NOT NULL DEFAULT 0,
    alert_sent INTEGER NOT NULL DEFAULT 0,
    third_party_execution_allowed INTEGER NOT NULL DEFAULT 0,
    broker_execution_allowed INTEGER NOT NULL DEFAULT 0,
    real_funds_allowed INTEGER NOT NULL DEFAULT 0,
    affects_signal INTEGER NOT NULL DEFAULT 0
);

CREATE OR REPLACE VIEW stratproof_public.v_research_brain_latest AS
SELECT *
FROM stratproof_public.research_brain_snapshots
ORDER BY created_at DESC
LIMIT 1;
