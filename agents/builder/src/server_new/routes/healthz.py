from flask import Blueprint, jsonify
from src.database import get_db
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("healthz", __name__)


@bp.route("/healthz")
def healthz():
    # Test database connection
    _ = get_db()
    return jsonify({"status": "ok"})
