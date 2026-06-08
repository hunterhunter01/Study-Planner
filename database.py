"""
Study Planner — Database Layer
================================
Handles SQLite initialisation, table creation, and mock data seeding.
Uses Python's built-in sqlite3 module so no extra packages are needed.

Schema
------
  users      — registered accounts
  tasks      — individual study tasks per user
  schedules  — auto-generated study slots (managed by the scheduler)
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "study_planner.db")


# ──────────────────────────────────────────────
# CONNECTION FACTORY
# Returns a connection with Row factory enabled
# so rows behave like dicts: row["column_name"]
# ──────────────────────────────────────────────
def get_db_connection():
    """Open and return a SQLite connection with dict-style row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Allows row["column"] syntax
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce FK constraints
    return conn


# ──────────────────────────────────────────────
# TABLE CREATION
# ──────────────────────────────────────────────
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    DEFAULT (datetime('now'))
);
"""

CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    task_name   TEXT    NOT NULL,
    task_type   TEXT    NOT NULL DEFAULT 'Other',   -- Assignment|Quiz|Exam|Other
    deadline    TEXT    NOT NULL,                   -- stored as ISO string
    priority    TEXT    NOT NULL DEFAULT 'Medium',  -- High|Medium|Low
    status      TEXT    NOT NULL DEFAULT 'Pending', -- Pending|In Progress|Completed
    created_at  TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

CREATE_SCHEDULES_TABLE = """
CREATE TABLE IF NOT EXISTS schedules (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    task_id          INTEGER NOT NULL UNIQUE,       -- one slot per task
    scheduled_start  TEXT    NOT NULL,
    scheduled_end    TEXT    NOT NULL,
    created_at       TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    FOREIGN KEY (task_id)  REFERENCES tasks(id)  ON DELETE CASCADE
);
"""


# ──────────────────────────────────────────────
# MOCK DATA
# Seeded only when the DB is first created.
# Demo user: admin / password123
# ──────────────────────────────────────────────
def _seed_mock_data(cursor):
    """Insert a demo user and sample tasks for immediate testing."""

    demo_password_hash = hashlib.sha256(b"password123").hexdigest()

    # Demo user
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        ("admin", "admin@studyplanner.dev", demo_password_hash),
    )

    # Retrieve the demo user's id
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    row = cursor.fetchone()
    if row is None:
        return
    uid = row[0]

    # Sample tasks — mix of priorities and types
    from datetime import datetime, timedelta
    now = datetime.now()

    sample_tasks = [
        # (task_name, task_type, deadline_offset_hours, priority, status)
        ("Calculus Problem Set",      "Assignment", -2,   "High",   "Pending"),     # overdue
        ("History Essay Draft",       "Assignment",  20,  "Medium", "Pending"),     # due soon
        ("Python Quiz",               "Quiz",        48,  "High",   "Pending"),
        ("Physics Lab Report",        "Assignment",  72,  "Medium", "Pending"),
        ("Database Mid-term Exam",    "Exam",        96,  "High",   "Pending"),
        ("English Literature Review", "Assignment",  120, "Low",    "Pending"),
        ("Statistics Homework",       "Assignment",  168, "Low",    "Completed"),   # already done
    ]

    for name, ttype, offset_h, priority, status in sample_tasks:
        deadline = (now + timedelta(hours=offset_h)).strftime("%Y-%m-%dT%H:%M")
        cursor.execute(
            "INSERT OR IGNORE INTO tasks "
            "(user_id, task_name, task_type, deadline, priority, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (uid, name, ttype, deadline, priority, status),
        )


# ──────────────────────────────────────────────
# PUBLIC INIT FUNCTION
# Called once from app.py on startup.
# ──────────────────────────────────────────────
def init_db():
    """
    Create all tables if they don't exist, then seed mock data.
    Safe to call on every startup — uses IF NOT EXISTS / INSERT OR IGNORE.
    """
    conn   = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(CREATE_USERS_TABLE)
    cursor.execute(CREATE_TASKS_TABLE)
    cursor.execute(CREATE_SCHEDULES_TABLE)

    _seed_mock_data(cursor)

    conn.commit()
    conn.close()
    print("[DB] Database initialised:", DB_PATH)


# ──────────────────────────────────────────────
# CLI helper: run `python database.py` to reset
# ──────────────────────────────────────────────
if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[DB] Existing database removed.")
    init_db()
    print("[DB] Fresh database created with mock data.")
    print("[DB] Demo login → username: admin  |  password: password123")
