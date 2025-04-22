"""Centralized logging configuration and utilities."""

import logging
import sys
import traceback
from typing import Any
from pathlib import Path
from functools import wraps
import ast
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init(strip=False)  # Force color output even when not in a terminal

# Create our logger
logger = logging.getLogger("builder")
logger.setLevel(logging.INFO)
# Prevent propagation to avoid duplicate logs
logger.propagate = False

# Track if logging has been configured
_logging_configured = False


class SectionFormatter(logging.Formatter):
    """Custom formatter that only shows timestamp and level for section headers and errors."""

    def format(self, record):
        # Check if this is a section header (starts with newline + ===)
        is_section = (
            record.msg.startswith("\n=== ") if isinstance(record.msg, str) else False
        )

        # Check if this is an error message
        is_error = record.levelno >= logging.ERROR

        if is_section:
            # Full timestamp format for sections and errors
            if is_error:
                # Red timestamp and level for errors
                fmt = f"{Fore.RED}%(asctime)s{Style.RESET_ALL}"
                fmt += f" [{Fore.RED}ERROR{Style.RESET_ALL}] %(message)s"
                self._style._fmt = fmt
            else:
                # Cyan timestamp and yellow level for sections
                fmt = f"\n{Fore.CYAN}%(asctime)s{Style.RESET_ALL}"
                fmt += f" [{Fore.YELLOW}INFO{Style.RESET_ALL}] %(message)s"
                self._style._fmt = fmt
            self.datefmt = "%Y-%m-%d %H:%M:%S"
        else:
            # No timestamp or level for other logs
            self._style._fmt = "%(message)s"

        # Format the message first
        formatted_msg = super().format(record)

        # If this is a section header, color the header text but keep equals signs black
        if is_section:
            # Split the header into parts (handle the newline)
            parts = formatted_msg.split("===")
            if len(parts) == 3:  # Should be ["\n", " HEADER ", ""]
                # Color the middle part (the header text) while keeping === black
                color = (
                    Fore.RED if is_error else Fore.MAGENTA
                )  # Red for errors, purple for info
                formatted_msg = (
                    parts[0] + "===" + color + parts[1] + Style.RESET_ALL + "==="
                )

        return formatted_msg


def configure_logging():
    """Configure logging for the application."""
    global _logging_configured
    if _logging_configured:
        return

    try:
        # Remove any existing handlers to prevent duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Create console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = SectionFormatter()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logger.info("Logging configured: INFO+ to console")
        _logging_configured = True

    except Exception as e:
        # If logging setup fails, ensure basic console logging is available
        print(f"Failed to configure logging: {e}", file=sys.stderr)


def format_value(value: Any) -> str:
    """Format a value for logging, handling multiline strings."""
    if isinstance(value, str) and "\n" in value:
        # Indent multiline strings
        return "\n    " + value.replace("\n", "\n    ")
    return str(value)


def log_section(name: str) -> None:
    """Log a section header with consistent formatting."""
    if not _logging_configured:
        configure_logging()
    logger.info(f"\n=== {name.upper()} ===")


def log_key_value(key: str, value: Any) -> None:
    """Log a key-value pair with consistent formatting."""
    if not _logging_configured:
        configure_logging()
    logger.info(f"{key}: {format_value(value)}")


def log_value(value: str) -> None:
    """Log a value with consistent formatting."""
    if not _logging_configured:
        configure_logging()
    logger.info(format_value(value))


def log_dict(data: dict, prefix: str = "") -> None:
    """Log a dictionary with consistent formatting."""
    for key, value in data.items():
        if isinstance(value, dict):
            log_dict(value, f"{prefix}{key}.")
        else:
            log_key_value(f"{prefix}{key}", value)


def log_tool_call(tool_name: str, inputs: dict) -> None:
    """Log a tool call with consistent formatting."""
    if not _logging_configured:
        configure_logging()
    log_section(f"EXECUTING TOOL: {tool_name}")
    if inputs:
        logger.info("INPUTS:")
        log_dict(inputs)


def log_tool_result(result: Any) -> None:
    """Log a tool result with consistent formatting."""
    if not _logging_configured:
        configure_logging()
    logger.info("RESULT:")
    if isinstance(result, dict):
        # Handle success/failure responses
        if "success" in result:
            if result["success"]:
                logger.info("✓ Success")
                # For successful operations, show the main result or message
                if "message" in result:
                    logger.info(format_value(result["message"]))
                # Show other relevant fields (excluding success flag and error)
                for key, value in result.items():
                    if key not in ["success", "error", "message"]:
                        log_key_value(key, value)
            else:
                logger.info("✗ Failed")
                if "error" in result:
                    logger.info(format_value(result["error"]))
        else:
            # For other responses, just show key-value pairs
            log_dict(result)
    else:
        logger.info(format_value(result))


def log_error(
    error: Exception, context: str = "", include_traceback: bool = True
) -> None:
    """Log an error with consistent formatting and optional stack trace."""
    if not _logging_configured:
        configure_logging()
    logger.error(f"\n=== {context.upper() if context else 'ERROR'} ===")
    logger.info(f"Error: {str(error)}")
    if include_traceback and error.__traceback__:
        logger.info("Stack trace:")
        for line in traceback.format_tb(error.__traceback__):
            logger.info(line.rstrip())


def log_execution_time(func):
    """Decorator to log function execution time."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _logging_configured:
            configure_logging()
        import time

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds")
            raise

    return wrapper


def add_file_logging(log_file: str) -> None:
    """Add file logging with rotation."""
    if not _logging_configured:
        configure_logging()
    try:
        from logging.handlers import RotatingFileHandler

        # Create log directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        logger.info(f"File logging enabled: {log_file}")
    except Exception as e:
        logger.error(f"Failed to set up file logging: {e}")


def log_tool_response(response_str: str, tool_use_id: str = None) -> None:
    """Log a tool response with consistent formatting.

    Args:
        response_str: The tool response string
        tool_use_id: Optional tool use ID
    """
    if not _logging_configured:
        configure_logging()
    if tool_use_id:
        logger.info(f"TOOL USE ID: {tool_use_id}")
    logger.info("RESPONSE:")
    try:
        # Try to parse as Python dict string
        response = ast.literal_eval(response_str)
        if isinstance(response, dict):
            # Handle success/failure responses
            if "success" in response:
                if response["success"]:
                    logger.info("✓ Success")
                    # For successful operations, show the main result or message
                    if "message" in response:
                        logger.info(format_value(response["message"]))
                    # Show other relevant fields (excluding success flag and error)
                    for key, value in response.items():
                        if key not in ["success", "error", "message"]:
                            log_key_value(key, value)
                else:
                    logger.info("✗ Failed")
                    if "error" in response:
                        logger.info(format_value(response["error"]))
            else:
                # For other responses, just show key-value pairs
                log_dict(response)
        else:
            logger.info(format_value(response_str))
    except (ValueError, SyntaxError):
        # If not a valid Python literal, log as formatted string
        logger.info(format_value(response_str))
