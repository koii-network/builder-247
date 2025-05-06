import os
import sqlite3
from typing import List, Dict, Any, Optional

def perform_database_migration(db_path: str, target_version: int = 1) -> bool:
    """
    Perform database migration to the specified target version.
    
    Args:
        db_path (str): Path to the SQLite database file
        target_version (int, optional): Target migration version. Defaults to 1.
    
    Returns:
        bool: True if migration was successful, False otherwise
    """
    # Validate path
    try:
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except (PermissionError, OSError):
                print(f"Cannot create directory for {db_path}")
                return False
    except Exception:
        print(f"Invalid path: {db_path}")
        return False
    
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Check current schema version
        current_version = _get_current_version(cursor)
        
        # Perform migrations in order
        migrations = {
            1: _migrate_to_version_1
        }
        
        # Apply migrations incrementally
        for version in range(current_version + 1, target_version + 1):
            if version in migrations:
                migrations[version](cursor)
                _update_schema_version(cursor, version)
        
        connection.commit()
        return True
    
    except sqlite3.Error as e:
        print(f"Database migration error: {e}")
        return False
    finally:
        if connection:
            connection.close()

def _get_current_version(cursor: sqlite3.Cursor) -> int:
    """
    Get the current database schema version.
    
    Args:
        cursor (sqlite3.Cursor): Database cursor
    
    Returns:
        int: Current schema version
    """
    try:
        cursor.execute("SELECT version FROM schema_version")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.OperationalError:
        # If schema_version table doesn't exist, create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        """)
        cursor.execute("INSERT INTO schema_version (version) VALUES (0)")
        return 0

def _update_schema_version(cursor: sqlite3.Cursor, version: int) -> None:
    """
    Update the schema version in the database.
    
    Args:
        cursor (sqlite3.Cursor): Database cursor
        version (int): New schema version
    """
    cursor.execute("UPDATE schema_version SET version = ?", (version,))

def _migrate_to_version_1(cursor: sqlite3.Cursor) -> None:
    """
    Initial migration: Create core tables if they don't exist
    
    Args:
        cursor (sqlite3.Cursor): Database cursor
    """
    # Example migration: Create conversation history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            model_name TEXT,
            prompt TEXT,
            response TEXT,
            tokens_used INTEGER,
            status TEXT
        )
    """)