"""Database model for logging."""

from datetime import datetime
from src.database import get_db


def init_logs_table():
    """Initialize the logs table if it doesn't exist."""
    # Not needed - handled by SQLModel
    pass


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
        from src.database import Log

        log = Log(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            module=module,
            function=function,
            path=path,
            line_no=line_no,
            exception=exception,
            stack_trace=stack_trace,
            request_id=request_id,
            additional_data=additional_data,
        )
        db.add(log)
        db.commit()
        return True
    except Exception as e:
        print(f"Failed to save log to database: {e}")  # Fallback logging
        return False
