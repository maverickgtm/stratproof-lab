"""Public version metadata for StratProof Lab."""

PUBLIC_PRODUCT_NAME = "StratProof Lab"
VERSION = "0.1.0-community-preview"
RELEASE_CHANNEL = "community-preview"
LICENSE = "AGPL-3.0-or-later"

def version_banner() -> str:
    return f"{PUBLIC_PRODUCT_NAME} {VERSION} ({RELEASE_CHANNEL})"
