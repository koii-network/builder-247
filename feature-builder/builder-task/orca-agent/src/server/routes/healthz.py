from flask import Blueprint, jsonify
from src.database import get_db

bp = Blueprint("healthz", __name__)


@bp.post("/healthz")
def healthz():
    # Test database connection
    _ = get_db()
    return jsonify({"status": "ok"})
