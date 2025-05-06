"""
Route registration for the server application.
"""

from .task import register_task_routes
from .submission import register_submission_routes
from .audit import register_audit_routes
from .healthz import healthz_route
from .evidence_uniqueness import register_evidence_uniqueness_routes

def register_routes(app, *args, **kwargs):
    """
    Register all routes for the application.

    Args:
        app: Flask application instance
    """
    # Register individual route groups
    healthz_route(app)
    register_task_routes(app, *args, **kwargs)
    register_submission_routes(app, *args, **kwargs)
    register_audit_routes(app, *args, **kwargs)
    register_evidence_uniqueness_routes(app, *args, **kwargs)