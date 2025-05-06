"""Shared database configuration."""

import os
from pathlib import Path
from sqlalchemy import create_engine

def get_sqlite_db_url(test_path: str = None) -> str:
    """
    Generate a SQLite database URL.

    Args:
        test_path (str, optional): Path for test database. Defaults to None.

    Returns:
        str: SQLite database URL
    """
    if test_path:
        return f"sqlite:///{test_path}"
    
    db_path = os.getenv("DATABASE_PATH", "sqlite:///database.db")
    # If the path doesn't start with sqlite://, assume it's a file path and convert it
    if not db_path.startswith("sqlite:")]:
        path = Path(db_path).resolve()
        # Ensure the parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        # Convert to SQLite URL format with absolute path
        db_path = f"sqlite:///{path}"

    return db_path

# Create engine with default database path
engine = create_engine(get_sqlite_db_url())