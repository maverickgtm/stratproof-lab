-- StratProof Lab Stage 15 — Formula Builder UI Expansion
-- Public/audit-only schema. This stores research ideas produced by a visual builder.
-- It is not an execution schema.

CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.formula_builder_drafts (
    id BIGSERIAL PRIMARY KEY,
    idea_hash TEXT UNIQUE,
    idea_name TEXT NOT NULL,
    owner_alias TEXT,
    language TEXT DEFAULT 'en',
    asset_class TEXT DEFAULT 'crypto',
    market_type TEXT DEFAULT 'imported_or_exchange_data',
    symbols TEXT[] DEFAULT ARRAY[]::TEXT[],
    primary_timeframe TEXT DEFAULT '5m',
    builder_json JSONB NOT NULL,
    research_status TEXT NOT NULL DEFAULT 'draft',
    safety_model TEXT NOT NULL DEFAULT 'audit_only_by_design',
    execution_default TEXT NOT NULL DEFAULT 'disabled',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stratproof_public.formula_builder_block_registry (
    block_type TEXT PRIMARY KEY,
    family TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    community_available BOOLEAN NOT NULL DEFAULT TRUE,
    pro_available BOOLEAN NOT NULL DEFAULT TRUE,
    enterprise_available BOOLEAN NOT NULL DEFAULT TRUE,
    default_config JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stratproof_public.formula_builder_presets (
    preset_id TEXT PRIMARY KEY,
    preset_name TEXT NOT NULL,
    description TEXT,
    asset_class TEXT NOT NULL DEFAULT 'crypto',
    market_type TEXT NOT NULL DEFAULT 'imported_or_exchange_data',
    default_timeframe TEXT NOT NULL DEFAULT '5m',
    preset_json JSONB NOT NULL,
    safety_model TEXT NOT NULL DEFAULT 'audit_only_by_design',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE stratproof_public.formula_builder_drafts IS 'Audit-only visual formula builder drafts. These are research ideas, not broker orders or execution instructions.';
COMMENT ON TABLE stratproof_public.formula_builder_block_registry IS 'Registry of visual indicator/context/risk blocks exposed to the Formula Builder UI.';
COMMENT ON TABLE stratproof_public.formula_builder_presets IS 'Reusable audit-only presets for users who want a starting point.';
