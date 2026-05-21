from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.idea_lab.models import StrategyIdea, compute_idea_hash, canonical_json

DEFAULT_LIBRARY_DB = Path("data/stratproof_saved_ideas.sqlite3")


def connect_library(path: str | Path = DEFAULT_LIBRARY_DB) -> sqlite3.Connection:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    init_library(con)
    return con


def init_library(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS idea_lab_saved_ideas (
            idea_hash TEXT PRIMARY KEY,
            user_label TEXT,
            title TEXT NOT NULL,
            description TEXT,
            tags_json TEXT NOT NULL DEFAULT '[]',
            builder_json TEXT NOT NULL,
            canonical_json TEXT NOT NULL,
            created_ts INTEGER NOT NULL,
            updated_ts INTEGER NOT NULL,
            last_used_ts INTEGER,
            use_count INTEGER NOT NULL DEFAULT 0,
            favorite INTEGER NOT NULL DEFAULT 0,
            archived INTEGER NOT NULL DEFAULT 0,
            source TEXT NOT NULL DEFAULT 'USER_BUILDER',
            notes TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_saved_ideas_updated ON idea_lab_saved_ideas(updated_ts);
        CREATE INDEX IF NOT EXISTS idx_saved_ideas_favorite ON idea_lab_saved_ideas(favorite, archived);

        CREATE TABLE IF NOT EXISTS idea_lab_saved_idea_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_hash TEXT NOT NULL,
            version_number INTEGER NOT NULL,
            builder_json TEXT NOT NULL,
            change_note TEXT,
            created_ts INTEGER NOT NULL,
            FOREIGN KEY(idea_hash) REFERENCES idea_lab_saved_ideas(idea_hash) ON DELETE CASCADE,
            UNIQUE(idea_hash, version_number)
        );
        """
    )
    con.commit()


def save_idea(
    idea: StrategyIdea | dict[str, Any],
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    user_label: str | None = None,
    favorite: bool = False,
    notes: str | None = None,
    cache_db: str | Path = DEFAULT_LIBRARY_DB,
) -> str:
    """Save a reusable strategy idea and return its stable idea_hash.

    This is NOT a trading activation. It stores an audit recipe that can be
    selected later by the user and sent to Research University.
    """
    if isinstance(idea, StrategyIdea):
        builder_json = idea.to_builder_json()
        default_title = idea.name
    else:
        builder_json = dict(idea)
        default_title = str(builder_json.get("name") or "Untitled strategy idea")
    canonical = canonical_json(builder_json)
    idea_hash = compute_idea_hash(builder_json, dataset_fingerprint="SAVED_IDEA_V1")
    now = int(time.time())
    tags = tags or []
    title = title or default_title
    with connect_library(cache_db) as con:
        existing = con.execute("SELECT idea_hash FROM idea_lab_saved_ideas WHERE idea_hash=?", (idea_hash,)).fetchone()
        if existing:
            con.execute(
                """
                UPDATE idea_lab_saved_ideas
                SET title=?, description=?, tags_json=?, builder_json=?, canonical_json=?,
                    updated_ts=?, favorite=?, archived=0, notes=COALESCE(?, notes)
                WHERE idea_hash=?
                """,
                (title, description, json.dumps(tags, ensure_ascii=False), json.dumps(builder_json, ensure_ascii=False), canonical, now, int(favorite), notes, idea_hash),
            )
        else:
            con.execute(
                """
                INSERT INTO idea_lab_saved_ideas
                (idea_hash, user_label, title, description, tags_json, builder_json, canonical_json,
                 created_ts, updated_ts, favorite, notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (idea_hash, user_label, title, description, json.dumps(tags, ensure_ascii=False), json.dumps(builder_json, ensure_ascii=False), canonical, now, now, int(favorite), notes),
            )
            con.execute(
                """
                INSERT INTO idea_lab_saved_idea_versions
                (idea_hash, version_number, builder_json, change_note, created_ts)
                VALUES (?,?,?,?,?)
                """,
                (idea_hash, 1, json.dumps(builder_json, ensure_ascii=False), "Initial saved idea", now),
            )
        con.commit()
    return idea_hash


def list_saved_ideas(cache_db: str | Path = DEFAULT_LIBRARY_DB, include_archived: bool = False) -> list[dict[str, Any]]:
    query = "SELECT * FROM idea_lab_saved_ideas"
    params: tuple[Any, ...] = ()
    if not include_archived:
        query += " WHERE archived=0"
    query += " ORDER BY favorite DESC, updated_ts DESC"
    with connect_library(cache_db) as con:
        rows = con.execute(query, params).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            d["tags"] = json.loads(d.pop("tags_json") or "[]")
            d["builder"] = json.loads(d.pop("builder_json") or "{}")
            out.append(d)
        return out


def load_saved_idea(idea_hash: str, cache_db: str | Path = DEFAULT_LIBRARY_DB, mark_used: bool = True) -> dict[str, Any] | None:
    now = int(time.time())
    with connect_library(cache_db) as con:
        row = con.execute("SELECT * FROM idea_lab_saved_ideas WHERE idea_hash=?", (idea_hash,)).fetchone()
        if not row:
            return None
        if mark_used:
            con.execute(
                "UPDATE idea_lab_saved_ideas SET last_used_ts=?, use_count=use_count+1 WHERE idea_hash=?",
                (now, idea_hash),
            )
            con.commit()
        d = dict(row)
        d["tags"] = json.loads(d.pop("tags_json") or "[]")
        d["builder"] = json.loads(d.pop("builder_json") or "{}")
        return d


def archive_saved_idea(idea_hash: str, cache_db: str | Path = DEFAULT_LIBRARY_DB) -> bool:
    with connect_library(cache_db) as con:
        cur = con.execute("UPDATE idea_lab_saved_ideas SET archived=1, updated_ts=? WHERE idea_hash=?", (int(time.time()), idea_hash))
        con.commit()
        return cur.rowcount > 0
