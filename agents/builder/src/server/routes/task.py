from flask import Blueprint, jsonify, request
from src.server.services import task_service

bp = Blueprint("task", __name__)


@bp.post("/worker-task/<roundNumber>")
def start_worker_task(roundNumber):
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


@bp.post("/submit-pr/<roundNumber>")
def submit_pr_route(roundNumber):
    data = request.get_json()
    signature = data.get("signature")
    staking_key = data.get("stakingKey")
    pub_key = data.get("pubKey")
    pr_url = data.get("prUrl")

    if not pr_url:
        return jsonify({"error": "Missing PR URL"}), 400

    message = task_service.submit_pr(
        signature, staking_key, pub_key, pr_url, roundNumber
    )

    return jsonify({"message": message})


@bp.post("/leader-task/<roundNumber>")
def start_leader_task(roundNumber):
    logger = task_service.logger
    logger.info(f"Task started for round: {roundNumber}")
