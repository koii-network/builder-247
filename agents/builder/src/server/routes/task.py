from flask import Blueprint, jsonify, request
from src.server.services import task_service

bp = Blueprint("task", __name__, url_prefix="/task")


@bp.route("/<roundNumber>", methods=["POST"])
def start_task(roundNumber):
    logger = task_service.logger
    logger.info(f"Task started for round: {roundNumber}")

    data = request.get_json()
    required_fields = ["fetchSignature", "addSignature", "stakingKey"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "Missing signature or staking key"}), 401

    return task_service.handle_task_creation(
        roundNumber, data["fetchSignature"], data["addSignature"], data["stakingKey"]
    )
