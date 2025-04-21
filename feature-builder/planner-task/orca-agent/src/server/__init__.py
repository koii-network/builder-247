"""Flask application initialization."""

from flask import Flask, request
from .routes import task, submission, audit, healthz
from prometheus_swarm.utils.logging import (
    configure_logging,
    log_section,
    log_key_value,
    log_value,
)
from prometheus_swarm.database import initialize_database
from colorama import Fore, Style
import uuid
import os


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Add request ID middleware
    @app.before_request
    def before_request():
        request.id = str(uuid.uuid4())
        # Store request start time for duration calculation
        request.start_time = request.environ.get("REQUEST_TIME", 0)

    @app.after_request
    def after_request(response):
        # Calculate request duration
        duration = (request.environ.get("REQUEST_TIME", 0) - request.start_time) * 1000

        # Get error message if this is an error response
        error_msg = ""
        if response.status_code >= 400:
            try:
                json_data = response.get_json()
                if isinstance(json_data, dict):
                    error_msg = json_data.get("error") or json_data.get("message", "")
            except Exception:
                # If we can't get JSON data, try to get the message from the response
                error_msg = getattr(response, "description", "")

        # Log the request with appropriate color
        color = Fore.GREEN if response.status_code < 400 else Fore.RED
        log_value(
            f"[{color}REQ{Style.RESET_ALL}] {request.method} {request.path} "
            f"{color}{response.status_code}{Style.RESET_ALL} {error_msg} {duration}ms"
        )

        return response

    # Register blueprints
    app.register_blueprint(healthz.bp)
    app.register_blueprint(task.bp)
    # app.register_blueprint(submission.bp)
    app.register_blueprint(audit.bp)
    # app.register_blueprint(submit_pr.bp)

    # Configure logging within app context
    with app.app_context():
        # Set up logging (includes both console and database logging)
        configure_logging()

        # Debug logging for database path
        print("\nDEBUG: Environment variables:")
        print(f"DATABASE_PATH={os.getenv('DATABASE_PATH')}")
        print(f"PWD={os.getenv('PWD')}")
        print(f"Current working directory: {os.getcwd()}")

        # Initialize database
        initialize_database()
        # Disable Flask's default logging
        app.logger.disabled = True

        # Log startup information
        log_section("SERVER STARTUP")
        log_key_value("Workers", 1)
        log_key_value("Host", "0.0.0.0:8080")
        log_key_value("Database", os.getenv("DATABASE_PATH", "Not configured"))

    return app
