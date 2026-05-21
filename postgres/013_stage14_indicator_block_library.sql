-- Stage 14 Indicator Block Library + Public Safety Model
-- Schema-only. No trading execution.

CREATE SCHEMA IF NOT EXISTS stratproof_public;

CREATE TABLE IF NOT EXISTS stratproof_public.indicator_block_catalog (
    block_key TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    family TEXT NOT NULL,
    description TEXT NOT NULL,
    default_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_type TEXT NOT NULL,
    audit_notes TEXT,
    community_available BOOLEAN NOT NULL DEFAULT TRUE,
    pro_available BOOLEAN NOT NULL DEFAULT TRUE,
    enterprise_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stratproof_public.formula_builder_templates (
    template_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    blocks JSONB NOT NULL,
    asset_class TEXT NOT NULL DEFAULT 'crypto',
    safety_model TEXT NOT NULL DEFAULT 'audit_only_by_design',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stratproof_public.public_safety_model_versions (
    version_key TEXT PRIMARY KEY,
    headline TEXT NOT NULL,
    summary TEXT NOT NULL,
    principles JSONB NOT NULL,
    replaces_legacy_bot_wording BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
