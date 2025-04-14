"""Shared database configuration."""

import os
from pathlib import Path
from sqlalchemy import create_engine

# Create engine
db_path = os.getenv("DATABASE_PATH", "sqlite:///database.db")
# If the path doesn't start with sqlite://, assume it's a file path and convert it
if not db_path.startswith("sqlite:"):
    path = Path(db_path).resolve()
    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    # Convert to SQLite URL format with absolute path
    db_path = f"sqlite:///{path}"

engine = create_engine(db_path)
