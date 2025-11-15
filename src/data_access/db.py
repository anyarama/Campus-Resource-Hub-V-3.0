"""SQLite helpers and schema management."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student','staff','admin')),
    department TEXT,
    email_verified INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    availability_notes TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS resource_images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resource_id) REFERENCES resources(resource_id)
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL,
    start_datetime TEXT NOT NULL,
    end_datetime TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    notes TEXT,
    owner_notes TEXT,
    decision_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY(requester_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS message_threads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER,
    owner_id INTEGER NOT NULL,
    participant_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY(owner_id) REFERENCES users(user_id),
    FOREIGN KEY(participant_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(thread_id) REFERENCES message_threads(thread_id),
    FOREIGN KEY(sender_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY(reviewer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
"""


def get_connection(close_only: bool = False) -> Optional[sqlite3.Connection]:
    if close_only:
        return getattr(g, '_database', None)

    conn = getattr(g, '_database', None)
    if conn is None:
        database_path = current_app.config['DATABASE_PATH']
        conn = g._database = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
    return conn


def init_database(force: bool = False) -> None:
    database_path = current_app.config['DATABASE_PATH']
    if force and database_path != ':memory:':
        db_file = Path(database_path)
        if db_file.exists():
            db_file.unlink()

    conn = sqlite3.connect(database_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

    from src.data_access.sample_data import ensure_seed_data
    ensure_seed_data()
