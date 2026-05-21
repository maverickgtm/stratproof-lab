"""Formula Builder block registry for Stage 14."""
from __future__ import annotations

from app.idea_lab.indicator_library import block_catalog


def get_formula_builder_blocks():
    """Return UI-ready block metadata grouped by family."""
    grouped = {}
    for block in block_catalog():
        grouped.setdefault(block["family"], []).append(block)
    return grouped


if __name__ == "__main__":
    import json
    print(json.dumps(get_formula_builder_blocks(), indent=2, ensure_ascii=False))
