"""Database logging handler and utilities."""

import logging
import traceback
import json
import uuid
import sys
from flask import has_request_context, request, current_app
from src.server.models.Log import save_log, init_logs_table
from src.utils.logging import logger

# Track if database logging has been configured
_db_logging_configured = False


class DatabaseLogHandler(logging.Handler):
    """Custom logging handler that saves logs to the database."""

    def emit(self, record):
        """Save the log record to the database."""
        # Only attempt database logging if we're in application context
        if not current_app:
            return

        # Only log ERROR and above
        if record.levelno < logging.ERROR:
            return

        try:
            # Get exception info if present
            exc_info = None
            stack_trace = None
            if record.exc_info:
                exc_info = str(record.exc_info[1])
                stack_trace = "".join(traceback.format_exception(*record.exc_info))

            # Get request ID if in request context
            request_id = None
            additional_data = {}
            if has_request_context():
                request_id = getattr(request, "id", str(uuid.uuid4()))
                additional_data.update(
                    {
                        "method": request.method,
                        "path": request.path,
                        "remote_addr": request.remote_addr,
                    }
                )

            # Add any custom attributes from the record
            if hasattr(record, "additional_data"):
                additional_data.update(record.additional_data)

            save_log(
                level=record.levelname,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                path=record.pathname,
                line_no=record.lineno,
                exception=exc_info,
                stack_trace=stack_trace,
                request_id=request_id,
                additional_data=(
                    json.dumps(additional_data) if additional_data else None
                ),
            )
        except Exception as e:
            # Fallback to standard error output if database logging fails
            print(f"Failed to log to database: {e}", file=sys.stderr)


def setup_db_logging() -> None:
    """Set up database logging for the application."""
    global _db_logging_configured
    if _db_logging_configured:
        return

    try:
        # Initialize the logs table
        init_logs_table()

        # Remove any existing database handlers
        for handler in logger.handlers[:]:
            if isinstance(handler, DatabaseLogHandler):
                logger.removeHandler(handler)

        # Create and configure the database handler for ERROR and above only
        db_handler = DatabaseLogHandler()
        db_handler.setLevel(logging.ERROR)
        db_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        db_handler.setFormatter(db_formatter)
        logger.addHandler(db_handler)

        logger.info("Database logging enabled: ERROR+ to database")
        _db_logging_configured = True
    except Exception as e:
        print(f"Failed to set up database logging: {e}", file=sys.stderr)
