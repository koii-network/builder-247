"""Logging configuration for the application."""

import logging
import traceback
import json
import uuid
import sys
from flask import has_request_context, request, current_app
from src.server.models.Log import save_log, init_logs_table


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


def configure_logging():
    """Configure logging for the application."""
    try:
        # Initialize the logs table
        init_logs_table()

        # Create console handler with INFO level (for all logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "\033[36m%(asctime)s.%(msecs)03d\033[0m [\033[33m%(levelname)s\033[0m] %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)

        # Create and configure the database handler for ERROR and above only
        db_handler = DatabaseLogHandler()
        db_handler.setLevel(logging.ERROR)  # Only log errors and above to the database
        db_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        db_handler.setFormatter(db_formatter)

        # Get root logger and remove any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Set overall logging level to INFO to capture all logs
        root_logger.setLevel(logging.INFO)

        # Add both handlers to root logger
        root_logger.addHandler(console_handler)
        root_logger.addHandler(db_handler)

        # Log a test message to verify configuration
        logger = logging.getLogger(__name__)
        logger.info("Logging configured: INFO+ to console, ERROR+ to database")

    except Exception as e:
        # If logging setup fails, ensure basic console logging is available
        logging.basicConfig(
            level=logging.INFO,
            format="\033[36m%(asctime)s.%(msecs)03d\033[0m [\033[33m%(levelname)s\033[0m] %(message)s",
            datefmt="%H:%M:%S",
            stream=sys.stdout,
        )
        logging.error(f"Failed to configure logging: {e}")
