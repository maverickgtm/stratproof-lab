
from __future__ import annotations
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
SUPPORTED = {"en", "es", "pt", "de"}

def load_translations(lang: str = "en") -> dict:
    lang = (lang or "en").lower()
    if lang not in SUPPORTED:
        lang = "en"
    return json.loads((BASE / f"{lang}.json").read_text(encoding="utf-8"))

def translate(key: str, lang: str = "en", default: str | None = None) -> str:
    return load_translations(lang).get(key, default if default is not None else key)
