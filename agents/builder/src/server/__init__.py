"""Flask application initialization."""

from flask import Flask
from .routes import task, submission, audit, healthz, submit_pr
from .utils.logging import configure_logging
from .services.database import close_db
from .middleware import add_error_headers


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    configure_logging()

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

    return app
