"""Public monetization metadata for StratProof Lab.

This module is documentation-friendly and intentionally contains no payment
provider secrets, webhook secrets, wallet private keys, or license signing keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Plan:
    plan_id: str
    name: str
    monthly_usd: Optional[int]
    yearly_standard_usd: Optional[int]
    yearly_founding_usd: Optional[int]
    target: str
    summary: str


PAYMENT_PRINCIPLE = "Card-first for trust. Crypto-ready for global traders."

ANNUAL_DISCOUNT_STANDARD_PCT = 15
FOUNDING_MEMBER_ANNUAL_DISCOUNT_PCT = 40
FOUNDING_MEMBER_SLOTS = 100

PLANS = [
    Plan("community", "Community", 0, 0, 0, "Open-source users", "AGPL community edition."),
    Plan("pro_early_access", "Pro Early Access", 29, 295, 209, "Serious individual traders", "Early Pro evidence workflows."),
    Plan("pro_plus", "Pro Plus", 79, 805, 569, "Power users", "Batch audits and multi-market workflows."),
    Plan("team", "Team", 199, 2030, 1433, "Communities and teams", "Shared workspace and branded reports."),
    Plan("enterprise", "Enterprise / SaaS", 999, None, None, "Firms and institutions", "Private deployment and custom integrations."),
]


def public_pricing_summary() -> dict:
    return {
        "payment_principle": PAYMENT_PRINCIPLE,
        "annual_discount_standard_pct": ANNUAL_DISCOUNT_STANDARD_PCT,
        "founding_member_annual_discount_pct": FOUNDING_MEMBER_ANNUAL_DISCOUNT_PCT,
        "founding_member_slots": FOUNDING_MEMBER_SLOTS,
        "plans": [plan.__dict__ for plan in PLANS],
        "not_sold": [
            "signals",
            "guaranteed returns",
            "managed trading",
            "financial advice",
        ],
    }
