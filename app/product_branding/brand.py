
"""Public branding layer for the community release.

Internal legacy modules may still contain Private Legacy Research System names while the public product
brand is StratProof Lab. This avoids breaking imports while removing public
Private Legacy Research System positioning from the dashboard/docs.
"""

PUBLIC_PRODUCT_NAME = "StratProof Lab"
PUBLIC_TAGLINE = "Autonomous strategy auditing before capital risk"
INTERNAL_LEGACY_NAME = "Private Legacy Research System"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "es"]

def public_brand_payload():
    return {
        "product_name": PUBLIC_PRODUCT_NAME,
        "tagline": PUBLIC_TAGLINE,
        "default_language": DEFAULT_LANGUAGE,
        "supported_languages": SUPPORTED_LANGUAGES,
        "mode": "audit_only_no_trading_by_default",
    }
