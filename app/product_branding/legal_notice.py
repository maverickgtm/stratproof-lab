"""Public legal notice helpers for StratProof Lab.

These helpers keep the UI language consistent. They are not legal advice.
"""

COMMUNITY_LICENSE = "AGPL-3.0-or-later"
PUBLIC_PRODUCT_NAME = "StratProof Lab"

LEGAL_NOTICE = (
    "StratProof Lab Community Edition is licensed under AGPL-3.0-or-later. "
    "It is an audit and research platform, not a broker, exchange, investment "
    "adviser, managed-account service, signal seller, or guaranteed-return system."
)

AUDIT_ONLY_NOTICE = (
    "Audit-only by design. Evidence before action. No broker execution in the "
    "Community Edition. No guaranteed returns. No financial advice."
)


def get_public_legal_notice() -> dict:
    return {
        "product": PUBLIC_PRODUCT_NAME,
        "community_license": COMMUNITY_LICENSE,
        "legal_notice": LEGAL_NOTICE,
        "audit_only_notice": AUDIT_ONLY_NOTICE,
    }
