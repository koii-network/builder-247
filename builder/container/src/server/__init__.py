from flask import Flask
from .routes import healthz, task, submission, audit
from .utils.logging import configure_logging
from .services.database import close_db


def create_app():
    app = Flask(__name__)
    configure_logging()

    # Register blueprints
    app.register_blueprint(healthz.bp)
    app.register_blueprint(task.bp)
    app.register_blueprint(submission.bp)
    app.register_blueprint(audit.bp)

    # Teardown context
    app.teardown_appcontext(close_db)

    return app
