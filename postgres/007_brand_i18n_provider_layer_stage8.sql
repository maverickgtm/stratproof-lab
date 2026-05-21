-- StratProof Lab Stage 8: public branding, i18n preferences, provider connector registry
CREATE SCHEMA IF NOT EXISTS stratproof_public;
CREATE TABLE IF NOT EXISTS stratproof_public.user_preferences (
  id BIGSERIAL PRIMARY KEY,
  user_ref TEXT DEFAULT 'local_user',
  language TEXT DEFAULT 'en',
  timezone TEXT DEFAULT 'UTC',
  default_exchange TEXT,
  default_market_type TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS stratproof_public.provider_registry (
  provider_key TEXT PRIMARY KEY,
  provider_name TEXT NOT NULL,
  asset_classes TEXT NOT NULL,
  capabilities TEXT NOT NULL,
  edition TEXT NOT NULL DEFAULT 'Community',
  execution_default TEXT NOT NULL DEFAULT 'disabled',
  status TEXT NOT NULL DEFAULT 'planned_or_available',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS stratproof_public.product_feature_matrix (
  feature_key TEXT PRIMARY KEY,
  feature_name TEXT NOT NULL,
  community_included BOOLEAN DEFAULT false,
  pro_included BOOLEAN DEFAULT true,
  saas_included BOOLEAN DEFAULT true,
  notes TEXT
);
