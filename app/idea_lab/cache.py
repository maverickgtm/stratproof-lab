from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

DEFAULT_CACHE_DB = Path("data/stratproof_idea_lab_cache.sqlite3")


def connect_cache(path: str | Path = DEFAULT_CACHE_DB) -> sqlite3.Connection:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    init_cache(con)
    return con


def init_cache(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS idea_lab_research_cache (
            idea_hash TEXT NOT NULL,
            dataset_fingerprint TEXT NOT NULL DEFAULT '',
            created_ts INTEGER NOT NULL,
            updated_ts INTEGER NOT NULL,
            expires_ts INTEGER,
            reuse_count INTEGER NOT NULL DEFAULT 0,
            builder_json TEXT NOT NULL,
            result_summary_json TEXT NOT NULL,
            report_path TEXT,
            PRIMARY KEY (idea_hash, dataset_fingerprint)
        );
        CREATE INDEX IF NOT EXISTS idx_idea_lab_research_cache_updated
        ON idea_lab_research_cache(updated_ts);
        """
    )
    con.commit()


def get_cached_result(idea_hash: str, dataset_fingerprint: str = '', cache_db: str | Path = DEFAULT_CACHE_DB) -> dict[str, Any] | None:
    with connect_cache(cache_db) as con:
        row = con.execute(
            "SELECT * FROM idea_lab_research_cache WHERE idea_hash=? AND dataset_fingerprint=?",
            (idea_hash, dataset_fingerprint),
        ).fetchone()
        if not row:
            return None
        con.execute(
            "UPDATE idea_lab_research_cache SET reuse_count=reuse_count+1 WHERE idea_hash=? AND dataset_fingerprint=?",
            (idea_hash, dataset_fingerprint),
        )
        con.commit()
        return dict(row)


def store_cached_result(idea_hash: str, builder_json: dict[str, Any], result_summary: dict[str, Any], dataset_fingerprint: str = '', report_path: str | None = None, cache_db: str | Path = DEFAULT_CACHE_DB, ttl_seconds: int | None = None) -> None:
    now = int(time.time())
    expires = now + ttl_seconds if ttl_seconds else None
    with connect_cache(cache_db) as con:
        con.execute(
            """
            INSERT INTO idea_lab_research_cache
            (idea_hash, dataset_fingerprint, created_ts, updated_ts, expires_ts, reuse_count, builder_json, result_summary_json, report_path)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(idea_hash, dataset_fingerprint) DO UPDATE SET
              updated_ts=excluded.updated_ts,
              expires_ts=excluded.expires_ts,
              builder_json=excluded.builder_json,
              result_summary_json=excluded.result_summary_json,
              report_path=excluded.report_path
            """,
            (idea_hash, dataset_fingerprint, now, now, expires, 0, json.dumps(builder_json, ensure_ascii=False), json.dumps(result_summary, ensure_ascii=False), report_path),
        )
        con.commit()
