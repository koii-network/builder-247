import sqlite3
from flask import g
import os


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            os.getenv("DATABASE_PATH", "database.db"),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        initialize_database(g.db)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialize_database(db):
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            roundNumber INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'pending',
            pr_url TEXT,
            username TEXT,
            repo_owner TEXT,
            repo_name TEXT
        )
    """
    )
    db.commit()
