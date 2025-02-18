from flask import Blueprint
from src.server.services.database import get_db

bp = Blueprint("utility", __name__)


@bp.route("/healthz", methods=["POST"])
def health_check():
    get_db()
    return "OK"
