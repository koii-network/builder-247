from flask import Blueprint, jsonify, request
from src.server_new.services import task_service

bp = Blueprint("task", __name__)


@bp.route("/task/<roundNumber>", methods=["POST"])
def start_task(roundNumber):
    logger = task_service.logger
    logger.info(f"Task started for round: {roundNumber}")

    data = request.get_json()
    logger.info(f"Task data: {data}")
    required_fields = ["taskId", "roundNumber", "stakingKey", "signature"]
    if any(data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401

    return task_service.handle_task_creation(
        task_id=data["taskId"],
        round_number=int(roundNumber),
        signature=data["signature"],
        staking_key=data["stakingKey"],
        pub_key=data["pubKey"],
    )
