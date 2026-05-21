"""Public safety wording for StratProof Lab.

This replaces legacy bot-specific phrasing with product-friendly language.
"""
from __future__ import annotations

PUBLIC_SAFETY_MODEL = {
    "headline": "Audit-only by design",
    "summary": "StratProof Lab imports market data, tests strategy ideas, validates evidence, and generates reports. It does not execute trades by default.",
    "principles": [
        "Evidence before action",
        "No broker order placement in Community",
        "No withdrawal permissions",
        "No managed accounts",
        "No guaranteed returns",
        "No financial advice",
        "Execution and live alerting are outside the default auditor scope",
    ],
    "legacy_internal_note": "Public documentation should use audit-first wording instead of legacy bot-oriented wording.",
}


def get_public_safety_model() -> dict:
    return PUBLIC_SAFETY_MODEL.copy()
