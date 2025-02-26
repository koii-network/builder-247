"""Flask application initialization."""

from flask import Flask, request
from .routes import task, submission, audit, healthz, submit_pr
from src.utils.logging import configure_logging, log_section, log_key_value
from src.database import close_db, initialize_database
from .middleware import add_error_headers
import uuid
import multiprocessing
import os


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Add request ID middleware
    @app.before_request
    def before_request():
        request.id = str(uuid.uuid4())

    # Register blueprints with middleware
    app.register_blueprint(healthz.bp)
    app.register_blueprint(task.bp)
    app.register_blueprint(submission.bp)
    app.register_blueprint(audit.bp)
    app.register_blueprint(submit_pr.bp)

    # Teardown context
    app.teardown_appcontext(close_db)

    # Apply middleware to all routes
    for endpoint in app.view_functions:
        app.view_functions[endpoint] = add_error_headers(app.view_functions[endpoint])

    # Configure logging within app context
    with app.app_context():
        # Set up logging (includes both console and database logging)
        configure_logging()
        # Initialize database
        initialize_database()
        # Disable Flask's default logging
        app.logger.disabled = True

        # Only log startup info in the main worker (worker 0)
        if os.environ.get("GUNICORN_WORKER_ID", "0") == "0":
            # Log startup information
            log_section("SERVER STARTUP")
            log_key_value("Workers", multiprocessing.cpu_count())
            log_key_value("Host", "0.0.0.0:8080")
            log_key_value("Database", os.getenv("DATABASE_PATH", "Not configured"))

    return app
