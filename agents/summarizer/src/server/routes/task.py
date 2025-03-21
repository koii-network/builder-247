from flask import Blueprint, jsonify, request
from src.server.services import task_service

bp = Blueprint("task", __name__)


@bp.post("/task/<round_number>")
def start_task(round_number):
    logger = task_service.logger
    logger.info(f"Task started for round: {round_number}")

    data = request.get_json()
    logger.info(f"Task data: {data}")
    required_fields = [
        "taskId",
        "roundNumber",
        "stakingKey",
        "stakingSignature",
        "pubKey",
        "publicSignature",
        "repoOwner",
    ]
    if any(data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401

    result = task_service.handle_task_creation(
        task_id=data["taskId"],
        round_number=int(round_number),
        signature=data["signature"],
        staking_key=data["stakingKey"],
        pub_key=data["pubKey"],
    )

    return jsonify({"message": result})
