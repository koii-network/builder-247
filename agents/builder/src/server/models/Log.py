"""Database model for logging."""

from datetime import datetime
import sqlite3
from src.server.services.database import get_db


def init_logs_table():
    """Initialize the logs table if it doesn't exist."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            module TEXT,
            function TEXT,
            path TEXT,
            line_no INTEGER,
            exception TEXT,
            stack_trace TEXT,
            request_id TEXT,
            additional_data TEXT
        )
        """
    )
    db.commit()


def save_log(
    level: str,
    message: str,
    module: str = None,
    function: str = None,
    path: str = None,
    line_no: int = None,
    exception: str = None,
    stack_trace: str = None,
    request_id: str = None,
    additional_data: str = None,
) -> bool:
    """
    Save a log entry to the database.

    Args:
        level: Log level (ERROR, WARNING, INFO, etc)
        message: Log message
        module: Module name where log was generated
        function: Function name where log was generated
        path: File path where log was generated
        line_no: Line number where log was generated
        exception: Exception type if any
        stack_trace: Stack trace if any
        request_id: Request ID if available
        additional_data: Any additional JSON-serializable data

    Returns:
        bool: True if log was saved successfully
    """
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO logs (
                timestamp, level, message, module, function, path,
                line_no, exception, stack_trace, request_id, additional_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                level,
                message,
                module,
                function,
                path,
                line_no,
                exception,
                stack_trace,
                request_id,
                additional_data,
            ),
        )
        db.commit()
        return True
    except sqlite3.Error as e:
        print(f"Failed to save log to database: {e}")  # Fallback logging
        return False
