from flask import Blueprint
from src.server.services.database import get_db
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("healthz", __name__)


@bp.route("/healthz", methods=["POST"])
def health_check():
    logger.info("Health check")
    get_db()
    return "OK"
