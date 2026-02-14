from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS holdings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT NOT NULL,
            name        TEXT NOT NULL,
            symbol      TEXT NOT NULL,
            quantity    REAL NOT NULL,
            buy_price   REAL NOT NULL,
            buy_date    TEXT,
            currency    TEXT NOT NULL,
            broker      TEXT,
            notes       TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_holdings_category ON holdings(category);

        CREATE TABLE IF NOT EXISTS price_cache (
            symbol          TEXT PRIMARY KEY,
            current_price   REAL,
            all_time_high   REAL,
            all_time_low    REAL,
            trend           TEXT,
            currency        TEXT,
            fetched_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS forex_cache (
            pair        TEXT PRIMARY KEY,
            rate        REAL NOT NULL,
            fetched_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ai_usage_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL DEFAULT (datetime('now')),
            provider        TEXT NOT NULL,
            model           TEXT NOT NULL,
            input_tokens    INTEGER NOT NULL DEFAULT 0,
            output_tokens   INTEGER NOT NULL DEFAULT 0,
            cost_usd        REAL NOT NULL DEFAULT 0.0,
            feature         TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


# --------------- Holdings CRUD ---------------

def add_holding(data: dict) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO holdings (category, name, symbol, quantity, buy_price,
           buy_date, currency, broker, notes)
           VALUES (:category, :name, :symbol, :quantity, :buy_price,
           :buy_date, :currency, :broker, :notes)""",
        data,
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def update_holding(holding_id: int, data: dict) -> None:
    conn = get_connection()
    data["id"] = holding_id
    data["updated_at"] = datetime.utcnow().isoformat()
    conn.execute(
        """UPDATE holdings SET name=:name, symbol=:symbol, quantity=:quantity,
           buy_price=:buy_price, buy_date=:buy_date, currency=:currency,
           broker=:broker, notes=:notes, updated_at=:updated_at
           WHERE id=:id""",
        data,
    )
    conn.commit()
    conn.close()


def delete_holding(holding_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM holdings WHERE id=?", (holding_id,))
    conn.commit()
    conn.close()


def get_holdings(category: str | None = None) -> list[dict]:
    conn = get_connection()
    if category:
        rows = conn.execute(
            "SELECT * FROM holdings WHERE category=? ORDER BY name", (category,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM holdings ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_holding_by_id(holding_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM holdings WHERE id=?", (holding_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# --------------- Price Cache ---------------

def upsert_price_cache(symbol: str, data: dict) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO price_cache
           (symbol, current_price, all_time_high, all_time_low, trend, currency, fetched_at)
           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
        (symbol, data.get("current_price"), data.get("all_time_high"),
         data.get("all_time_low"), data.get("trend"), data.get("currency")),
    )
    conn.commit()
    conn.close()


def get_cached_price(symbol: str, ttl_minutes: int = 15) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM price_cache WHERE symbol=?", (symbol,)).fetchone()
    conn.close()
    if not row:
        return None
    fetched_at = datetime.fromisoformat(row["fetched_at"])
    if datetime.utcnow() - fetched_at > timedelta(minutes=ttl_minutes):
        return None
    return dict(row)


# --------------- Forex Cache ---------------

def upsert_forex_cache(pair: str, rate: float) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO forex_cache (pair, rate, fetched_at)
           VALUES (?, ?, datetime('now'))""",
        (pair, rate),
    )
    conn.commit()
    conn.close()


def get_cached_forex(pair: str, ttl_minutes: int = 60) -> float | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM forex_cache WHERE pair=?", (pair,)).fetchone()
    conn.close()
    if not row:
        return None
    fetched_at = datetime.fromisoformat(row["fetched_at"])
    if datetime.utcnow() - fetched_at > timedelta(minutes=ttl_minutes):
        return None
    return row["rate"]


# --------------- AI Usage Log ---------------

def log_ai_usage(provider: str, model: str, input_tokens: int,
                 output_tokens: int, cost_usd: float, feature: str) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT INTO ai_usage_log (provider, model, input_tokens, output_tokens, cost_usd, feature)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (provider, model, input_tokens, output_tokens, cost_usd, feature),
    )
    conn.commit()
    conn.close()


def get_monthly_ai_cost() -> float:
    conn = get_connection()
    now = datetime.utcnow()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    row = conn.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) as total FROM ai_usage_log WHERE timestamp >= ?",
        (first_of_month.isoformat(),),
    ).fetchone()
    conn.close()
    return row["total"]
