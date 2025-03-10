from flask import Blueprint, jsonify, request
from src.server.services import task_service
from src.utils.logging import logger

bp = Blueprint("task", __name__)


@bp.post("/worker-task/<round_number>")
def start_worker_task(round_number):
    return start_task(round_number, "worker", request)


@bp.post("/leader-task/<round_number>")
def start_leader_task(round_number):
    return start_task(round_number, "leader", request)


def start_task(round_number, node_type, request):
    if node_type not in ["worker", "leader"]:
        return jsonify({"error": "Invalid node type"}), 400

    task_functions = {
        "worker": task_service.complete_todo,
        "leader": task_service.consolidate_prs,
    }
    logger.info(f"{node_type.capitalize()} task started for round: {round_number}")

    data = request.get_json()
    logger.info(f"Task data: {data}")
    required_fields = [
        "taskId",
        "roundNumber",
        "stakingKey",
        "stakingSignature",
        "pubKey",
        "publicSignature",
    ]
    if any(data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401

    pr_url = task_functions[node_type](
        task_id=data["taskId"],
        round_number=int(round_number),
        staking_signature=data["stakingSignature"],
        staking_key=data["stakingKey"],
        public_signature=data["publicSignature"],
        pub_key=data["pubKey"],
    )
    if not pr_url:
        return jsonify({"error": "Missing PR URL"}), 400

    message = task_service.record_pr(
        task_id=data["taskId"],
        round_number=int(round_number),
        staking_signature=data["stakingSignature"],
        staking_key=data["stakingKey"],
        public_signature=data["publicSignature"],
        pub_key=data["pubKey"],
        pr_url=pr_url,
    )

    return jsonify({"message": message})
