from flask import Blueprint

bp = Blueprint("utility", __name__)


@bp.route("/healthz", methods=["POST"])
def health_check():
    return "OK"
